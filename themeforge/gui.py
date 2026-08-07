"""GTK 4 / libadwaita graphical front-end for ThemeForge."""
from __future__ import annotations

import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk

from themeforge import apply as apply_mod
from themeforge import bundle as bundle_mod
from themeforge.installer import InstallError, build_forge


class ForgeWindow(Adw.ApplicationWindow):
    def __init__(self, app: Adw.Application, forge, bundle: dict) -> None:
        super().__init__(application=app, title="ThemeForge",
                         default_width=920, default_height=680)
        self.forge = forge
        self.bundle = bundle
        self._busy = False  # guards against concurrent install/apply actions
        self._kind_listboxes: dict[str, Gtk.ListBox] = {}
        self._kind_search: dict[str, Gtk.SearchEntry] = {}
        self._search_text: dict[str, str] = {}

        self.toast = Adw.ToastOverlay()
        self.set_content(self.toast)

        self.stack = Adw.ViewStack()
        self.stack.add_titled(self._looks_page(), "looks", "Looks")
        self.stack.add_titled(self._families_page("gtk", "Themes"), "themes", "Themes")
        self.stack.add_titled(self._families_page("icons", "Icons"), "icons", "Icons")
        self.stack.add_titled(self._families_page("wallpaper", "Wallpapers"),
                              "wallpapers", "Wallpapers")

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        reset_btn = Gtk.Button(label="Reset to defaults")
        reset_btn.add_css_class("flat")
        reset_btn.connect("clicked", self._on_reset)
        header.pack_end(reset_btn)
        header.set_title_widget(Adw.ViewSwitcher(stack=self.stack))
        toolbar.add_top_bar(header)
        toolbar.set_content(self.stack)
        self.toast.set_child(toolbar)

    # ------------------------------------------------------------- pages

    def _looks_page(self) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label(
            label="Curated Looks — one click applies a coordinated theme set "
                  "(GTK + icons + light/dark mode + wallpaper).",
            xalign=0, margin_top=12, margin_bottom=4, margin_start=12, margin_end=12,
        )
        label.add_css_class("dim-label")
        label.set_wrap(True)
        box.append(label)
        listbox = Gtk.ListBox()
        listbox.add_css_class("boxed-list")
        for lk in bundle_mod.looks(self.bundle):
            subtitle = lk.get("description", "")
            if lk.get("wallpaper"):
                subtitle += "  ·  wallpaper included"
            row = Adw.ActionRow(title=lk["name"], subtitle=subtitle)
            apply_btn = Gtk.Button(label="Apply")
            apply_btn.add_css_class("suggested-action")
            apply_btn.connect("clicked", self._on_apply, lk["id"], True)
            row.add_suffix(apply_btn)
            listbox.append(row)
        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.set_child(listbox)
        box.append(scroller)
        return box

    def _families_page(self, kind: str, title: str) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        search = Gtk.SearchEntry(placeholder_text=f"Search {title.lower()}…")
        search.set_margin_top(10)
        search.set_margin_bottom(6)
        search.set_margin_start(12)
        search.set_margin_end(12)
        box.append(search)
        listbox = Gtk.ListBox()
        listbox.add_css_class("boxed-list")
        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.set_child(listbox)
        box.append(scroller)
        self._kind_listboxes[kind] = listbox
        self._kind_search[kind] = search
        search.connect("search-changed", self._on_search_changed, kind)
        self._populate_families(kind)
        return box

    def _populate_families(self, kind: str) -> None:
        listbox = self._kind_listboxes[kind]
        while (row := listbox.get_first_child()) is not None:
            listbox.remove(row)
        text = self._search_text.get(kind, "").lower()
        for fam in bundle_mod.families(self.bundle):
            if fam["kind"] != kind:
                continue
            haystack = f"{fam['id']} {fam['name']}".lower()
            if text and text not in haystack:
                continue
            installed = bool(self.forge.installed(fam["id"]))
            row = Adw.ActionRow(
                title=fam["name"],
                subtitle=f"{fam.get('license', '?')} · {fam.get('homepage', fam['id'])}",
            )
            if installed:
                row.add_suffix(self._reinstall_btn(fam))
                row.add_suffix(self._uninstall_btn(fam))
            else:
                row.add_suffix(self._apply_btn(fam))
            listbox.append(row)

    def _apply_btn(self, fam: dict) -> Gtk.Button:
        btn = Gtk.Button(label="Install & Apply")
        btn.add_css_class("suggested-action")
        btn.connect("clicked", self._on_apply, fam["id"], False)
        return btn

    def _reinstall_btn(self, fam: dict) -> Gtk.Button:
        btn = Gtk.Button(label="Reinstall")
        btn.connect("clicked", self._on_apply, fam["id"], False)
        return btn

    def _uninstall_btn(self, fam: dict) -> Gtk.Button:
        btn = Gtk.Button(label="Uninstall")
        btn.add_css_class("destructive-action")
        btn.connect("clicked", self._on_uninstall, fam["id"])
        return btn

    def _on_search_changed(self, entry: Gtk.SearchEntry, kind: str) -> None:
        self._search_text[kind] = entry.get_text()
        self._populate_families(kind)

    # ------------------------------------------------------------ actions

    def _on_apply(self, _btn, target_id: str, is_look: bool) -> None:
        if self._busy:
            self._show_toast("Already busy installing — please wait.")
            return
        self._busy = True

        def worker() -> None:
            try:
                if is_look:
                    look = bundle_mod.look(self.bundle, target_id)
                    res = apply_mod.apply_look(look, self.forge, self.bundle)
                else:
                    fam = bundle_mod.family(self.bundle, target_id)
                    res = apply_mod.apply_family(fam, self.forge, self.bundle)
                if res.changed:
                    msg = "; ".join(res.changed)
                elif res.skipped:
                    msg = "Skipped: " + "; ".join(res.skipped)
                else:
                    msg = "Nothing to do."
                if res.logout_needed:
                    msg += " — log out/in to see Shell changes"
            except (InstallError, KeyError, RuntimeError) as exc:
                msg = f"Failed: {exc}"
            GLib.idle_add(self._done, msg)
        threading.Thread(target=worker, daemon=True).start()

    def _on_uninstall(self, _btn, fam_id: str) -> None:
        try:
            name = bundle_mod.family(self.bundle, fam_id)["name"]
        except KeyError:
            name = fam_id  # installed but no longer in the current bundle
        dialog = Adw.AlertDialog(
            heading=f"Uninstall {name}?",
            body="Its theme/icon/wallpaper files will be deleted from your "
                 "user directories. Your settings are not changed.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("uninstall", "Uninstall")
        dialog.set_response_appearance("uninstall", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.connect("response", self._on_uninstall_response, fam_id)
        dialog.present(self)

    def _on_uninstall_response(self, dialog: Adw.AlertDialog, response: str,
                               fam_id: str) -> None:
        if response != "uninstall":
            return
        if self._busy:
            self._show_toast("Already busy — please wait.")
            return
        self._busy = True

        def worker() -> None:
            try:
                removed = self.forge.remove_family(fam_id)
                msg = f"Uninstalled {fam_id}." if removed else f"{fam_id}: nothing to remove."
            except OSError as exc:
                msg = f"Failed to uninstall {fam_id}: {exc}"
            GLib.idle_add(self._done, msg)
        threading.Thread(target=worker, daemon=True).start()

    def _done(self, msg: str) -> None:
        self._busy = False
        for kind in self._kind_listboxes:
            self._populate_families(kind)
        self._show_toast(msg)

    def _on_reset(self, _btn) -> None:
        dialog = Adw.AlertDialog(
            heading="Reset to defaults?",
            body="Restore your distro's stock appearance (Yaru/Adwaita). "
                 "Installed themes stay in place unless you uninstall them.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("reset", "Reset")
        dialog.set_response_appearance("reset", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.connect("response", self._on_reset_response)
        dialog.present(self)

    def _on_reset_response(self, dialog: Adw.AlertDialog, response: str) -> None:
        if response != "reset":
            return
        from themeforge import distro as distro_mod

        def worker() -> None:
            res = apply_mod.reset(self.forge, self.bundle, distro_mod.detect())
            msg = "; ".join(res.changed) if res.changed else "Already at defaults."
            GLib.idle_add(self._done, msg)
        threading.Thread(target=worker, daemon=True).start()

    def _show_toast(self, msg: str) -> None:
        self.toast.add_toast(Adw.Toast.new(msg))


class ThemeForgeApp(Adw.Application):
    def __init__(self, forge=None, bundle: dict | None = None) -> None:
        super().__init__(application_id="io.themeforge.ThemeForge")
        self.forge = forge
        self.bundle = bundle
        self._win = None

    def do_activate(self) -> None:
        if self._win is None:
            self._win = ForgeWindow(self, self.forge, self.bundle)
        self._win.present()


def run_gui(forge=None, bundle_path=None) -> int:
    bundle = bundle_mod.load_bundle(bundle_path)
    app = ThemeForgeApp(forge=forge or build_forge(), bundle=bundle)
    return app.run(None)

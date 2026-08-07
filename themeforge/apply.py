"""Apply theme settings via gsettings and manage GNOME shell extension state."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field

from themeforge import bundle as bundle_mod
from themeforge.installer import InstallError

INTERFACE = "org.gnome.desktop.interface"
USER_THEME = "org.gnome.shell.extensions.user-theme"
BACKGROUND = "org.gnome.desktop.background"

USER_THEME_EXTENSION_ID = "user-theme@gnome-shell-extensions.gcampax.github.com"


@dataclass
class ApplyResult:
    changed: list = field(default_factory=list)
    skipped: list = field(default_factory=list)
    logout_needed: bool = False


# -------------------------------------------------------------- gsettings

def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def gsettings_get(schema: str, key: str) -> str:
    proc = _run(["gsettings", "get", schema, key])
    return proc.stdout.strip().strip("'") if proc.returncode == 0 else ""


def gsettings_set(schema: str, key: str, value: str) -> bool:
    return _run(["gsettings", "set", schema, key, value]).returncode == 0


def _set(schema: str, key: str, value: str, dry_run: bool) -> bool:
    if dry_run:
        return True
    return gsettings_set(schema, key, value)


# ------------------------------------------------------------ extensions

def user_themes_extension_state() -> tuple[bool, str]:
    """Returns (usable, state) where state is one of enabled|installed|missing|unknown."""
    try:
        all_out = _run(["gnome-extensions", "list"]).stdout
        enabled_out = _run(["gnome-extensions", "list", "--enabled"]).stdout
    except OSError:
        return False, "unknown"
    installed = any("user-theme" in line for line in all_out.splitlines())
    enabled = any("user-theme" in line for line in enabled_out.splitlines())
    if enabled:
        return True, "enabled"
    if installed:
        return False, "installed"
    return False, "missing"


def _shell_theme_ok(result: ApplyResult) -> bool:
    usable, state = user_themes_extension_state()
    if state != "enabled":
        result.skipped.append(f"shell theme (User Themes extension: {state})")
        return False
    return True


# ------------------------------------------------------------------ apply

def _installed_name(forge, fam: dict, kind: str, dry_run: bool = False) -> str | None:
    """Return the installed dir name for a family kind, installing it if needed.

    In dry-run mode nothing is installed — callers report the family as
    'would be installed' instead.
    """
    info = forge.installed(fam["id"])
    if info:
        names = info.get(kind) or []
        return names[0] if names else None
    if dry_run:
        return None
    info = forge.install_family(fam)
    names = info.get(kind) or []
    return names[0] if names else None


def _set_theme(result: ApplyResult, schema: str, key: str, value: str | None,
               dry_run: bool, label: str, display: str | None = None) -> bool:
    """Apply a theme key, reporting the outcome; returns True if applied."""
    name = display or key
    if value:
        if _set(schema, key, value, dry_run):
            result.changed.append(f"{name} → {value}")
            return True
        result.skipped.append(f"{name} → {value}")
    elif dry_run:
        result.changed.append(f"{label}: would install first")
    else:
        result.skipped.append(label)
    return False


def _set_wallpaper(result: ApplyResult, forge, name: str, dry_run: bool) -> None:
    """Point GNOME's background at an installed wallpaper file."""
    target = forge.backgrounds_dir / name
    if not target.exists() and not dry_run:
        result.skipped.append(f"wallpaper {name}: file missing after install")
        return
    uri = target.as_uri()
    for key in ("picture-uri", "picture-uri-dark"):
        if _set(BACKGROUND, key, uri, dry_run):
            result.changed.append(f"{key} → {name}")
        else:
            result.skipped.append(f"{key} (unsupported on this GNOME)")


def apply_family(fam: dict, forge, bundle: dict, *, dry_run: bool = False) -> ApplyResult:
    """Install one family and apply its theme setting (defaults for its kind)."""
    result = ApplyResult()
    kind = fam["kind"]
    if kind == "gtk":
        _set_theme(result, INTERFACE, "gtk-theme",
                   _installed_name(forge, fam, "themes", dry_run), dry_run, fam["id"])
    elif kind == "icons":
        _set_theme(result, INTERFACE, "icon-theme",
                   _installed_name(forge, fam, "icons", dry_run), dry_run, fam["id"])
    elif kind == "shell":
        name = _installed_name(forge, fam, "shell", dry_run)
        if name and _shell_theme_ok(result):
            if _set_theme(result, USER_THEME, "name", name, dry_run, fam["id"],
                          display="shell theme"):
                result.logout_needed = True
        elif not name and dry_run:
            result.changed.append(f"{fam['id']}: would install first")
    elif kind == "wallpaper":
        name = _installed_name(forge, fam, "wallpapers", dry_run)
        if name:
            _set_wallpaper(result, forge, name, dry_run)
        elif dry_run:
            result.changed.append(f"{fam['id']}: would install first")
    return result


def apply_look(look: dict, forge, bundle: dict, *, dry_run: bool = False) -> ApplyResult:
    """Apply a curated Look: GTK + Shell + icons + color scheme (+ optional accent)."""
    result = ApplyResult()

    def resolve(fam_id: str, kind: str) -> str | None:
        if not fam_id:  # looks may leave shell_theme unset (null)
            return None
        try:
            fam = bundle_mod.family(bundle, fam_id)
        except KeyError:
            result.skipped.append(f"{fam_id}: not in bundle")
            return None
        name = _installed_name(forge, fam, kind, dry_run)
        if not name and not dry_run:
            result.skipped.append(f"{fam_id}: nothing of kind '{kind}' installed")
        return name

    gtk = resolve(look.get("gtk_theme"), "themes")
    _set_theme(result, INTERFACE, "gtk-theme", gtk, dry_run, "gtk-theme")

    shell = resolve(look.get("shell_theme"), "shell")
    if shell and _shell_theme_ok(result):
        if _set_theme(result, USER_THEME, "name", shell, dry_run, "shell theme",
                      display="shell theme"):
            result.logout_needed = True
    elif shell is None and dry_run and look.get("shell_theme"):
        result.changed.append("shell theme: would install first")

    icon = resolve(look.get("icon_theme"), "icons")
    _set_theme(result, INTERFACE, "icon-theme", icon, dry_run, "icon-theme")

    color_scheme = look.get("color_scheme")
    if color_scheme and _set(INTERFACE, "color-scheme", color_scheme, dry_run):
        result.changed.append(f"color-scheme → {color_scheme}")
    elif color_scheme:
        result.skipped.append(f"color-scheme → {color_scheme}")

    accent = look.get("accent")
    if accent:
        # org.gnome.desktop.interface accent-color exists on GNOME 47+
        # (and Ubuntu's GNOME 46). Harmless if unsupported.
        if _set(INTERFACE, "accent-color", accent, dry_run):
            result.changed.append(f"accent-color → {accent}")
        else:
            result.skipped.append("accent-color (unsupported on this GNOME)")

    wallpaper_id = look.get("wallpaper")
    if wallpaper_id:
        try:
            wp_fam = bundle_mod.family(bundle, wallpaper_id)
        except KeyError:
            result.skipped.append(f"{wallpaper_id}: not in bundle")
        else:
            try:
                name = _installed_name(forge, wp_fam, "wallpapers", dry_run)
            except InstallError as exc:
                # wallpapers are best-effort — never fail the whole Look
                result.skipped.append(f"wallpaper: {exc}")
                name = None
            if name:
                _set_wallpaper(result, forge, name, dry_run)
            elif dry_run:
                result.changed.append("wallpaper: would install first")
    return result


# ------------------------------------------------------------------ reset

def reset(forge, bundle: dict, distro, *, purge: bool = False, dry_run: bool = False) -> ApplyResult:
    """Restore distro defaults (Yaru on Ubuntu, Adwaita elsewhere)."""
    result = ApplyResult()
    for schema, key, value in (
        (INTERFACE, "gtk-theme", distro.reset_theme()),
        (INTERFACE, "icon-theme", distro.reset_icon_theme()),
        (INTERFACE, "color-scheme", "default"),
        (USER_THEME, "name", ""),
    ):
        if _set(schema, key, value, dry_run):
            result.changed.append(f"{key} → {value or 'default'}")
        else:
            result.skipped.append(f"{key} → {value or 'default'}")
    if purge:
        for fam in bundle_mod.families(bundle):
            for removed in forge.remove_family(fam["id"]):
                result.changed.append(f"removed {removed}")
    return result

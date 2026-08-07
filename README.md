# ThemeForge

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Ubuntu%20%7C%20Fedora%20%7C%20Arch-lightgrey.svg)
![GUI](https://img.shields.io/badge/GTK-4%20%2F%20libadwaita-green.svg)
[![Buy on itch.io](https://img.shields.io/badge/buy_on-itch.io-fa5c5c.svg)](https://YOUR-NAME.itch.io/themeforge)
[![Support on Ko-fi](https://img.shields.io/badge/support-Ko--fi-ff5e5b.svg)](https://ko-fi.com/YOUR-HANDLE)

A **Theme Studio-style one-click desktop theming app for GNOME** — built for
**Ubuntu, Fedora and Arch**. Browse curated *Looks* (a coordinated GTK theme +
GNOME Shell theme + icon pack + light/dark mode + wallpaper), install them with
one click, and reset to your distro's defaults whenever you like.

No root. No package manager. No system-directory writes. Everything installs
into your **user directories** (`~/.local/share/themes`, `~/.icons`,
`~/.local/share/backgrounds`), the same safe, reversible approach as the
closed-source app that inspired this one — except ThemeForge is open source and
ships an original catalog of *open-source* themes (see [Licenses](#licenses)).

> Inspired by Theme Studio (Linux Tex). ThemeForge is an independent, original
> implementation and is **not** affiliated with or endorsed by Linux Tex.

## Requirements

- **Python 3.12+** (CLI). The GUI additionally needs GTK 4 + libadwaita
  bindings: `python3-gobject` on Ubuntu/Fedora/Arch, or `pip install PyGObject`.
- **GNOME desktop**; the **User Themes** extension for GNOME Shell themes
  - Ubuntu: `gnome-shell-extensions` · Fedora: `gnome-shell-extension-user-theme` · Arch: AUR
- An internet connection — themes, icons and wallpapers are fetched from their
  upstream sources on demand and cached in `~/.cache/themeforge`.

## Install

From source (or `pip install .` in this directory):

```bash
pip install .              # CLI + GUI entry points (themeforge, themeforge-gui)
python3 -m themeforge --help
```

Or run without installing:

```bash
python3 -m themeforge status
python3 -m themeforge gui
```

## Quick start

```bash
themeforge status                     # distro + current settings + install state
themeforge list                       # bundled looks & families
themeforge apply catppuccin-mocha     # one-click look: themes + icons + wallpaper
themeforge apply --dry-run dracula    # preview without changing anything
themeforge install whitesur           # download + install a single family
themeforge uninstall whitesur         # remove a family's files
themeforge reset                      # back to Yaru (Ubuntu) / Adwaita defaults
themeforge reset --purge              # ...and delete everything ThemeForge installed
themeforge gui                        # graphical front-end
```

## The v1.1 bundle (19 families, 6 Looks)

**GTK themes** — Catppuccin Mocha · Catppuccin Latte · Dracula · Orchis ·
WhiteSur · Colloid · Fluent · Graphite

**Icon packs** — Papirus · Tela · Colloid Icons · Fluent Icons

**Wallpapers** — one per Look, matching its palette (Catppuccin Mocha, Catppuccin
Latte, Dracula, Orchis, Colloid, WhiteSur), plus a standalone Rosé Pine
wallpaper — all installable from the Wallpapers tab.

**Looks** (one-click curated sets) — Catppuccin Mocha · Catppuccin Latte ·
Dracula · Orchis Light · Colloid Dark · WhiteSur

## How it works

1. **`asset` strategy** — downloads a ready-made release asset (Catppuccin,
   Dracula, Rosé Pine) and copies the theme/icon directories it contains.
2. **`script` strategy** — downloads the source tarball of a release and runs
   the upstream `install.sh` with explicit user-level destinations
   (`-d ~/.local/share/themes -i ~/.icons`).
3. **`url` strategy (wallpapers)** — downloads a single wallpaper image into
   `~/.local/share/backgrounds`.
4. **Apply** — sets the `gsettings` keys GNOME reads:
   `org.gnome.desktop.interface {gtk-theme, icon-theme, color-scheme}`,
   `org.gnome.shell.extensions.user-theme name` for Shell themes, and
   `org.gnome.desktop.background {picture-uri, picture-uri-dark}` for
   wallpapers. Wallpaper download failures are non-fatal — the rest of the
   Look still applies.

A record of everything installed lives in `~/.cache/themeforge/installed.json`,
which powers per-theme **uninstall** (`themeforge uninstall <family>`), the
GUI's Uninstall buttons, and the reset action.

## Distro support

| Distro | Detection | Reset defaults | User Themes extension package |
|---|---|---|---|
| Ubuntu (+ derivatives) | `ID=ubuntu` / `ID_LIKE=ubuntu` | Yaru / Yaru | `gnome-shell-extensions` |
| Fedora (+ derivatives e.g. Nobara) | `ID=fedora` / `ID_LIKE=fedora` | Adwaita / Adwaita | `gnome-shell-extension-user-theme` |
| Arch (+ derivatives e.g. EndeavourOS) | `ID=arch` / `ID_LIKE=arch` | Adwaita / Adwaita | `gnome-shell-extension-user-theme` (AUR) |

## Roadmap

- [x] Ubuntu / Fedora / Arch engine + GUI + CLI, 19-family bundle
- [x] Wallpapers per Look (`picture-uri` / `picture-uri-dark`)
- [x] Per-family uninstall (CLI + GUI)
- [ ] Native packaging: `.deb`, `.rpm`, AUR `PKGBUILD`
- [ ] `select` globs per Look so light/dark Looks pick matching variants
      deterministically instead of the first alphabetical dir
- [ ] Live theme previews (screenshots per theme); terminal (TUI) interface
- [ ] More families: Tokyo Night, Everforest, Gruvbox, Dracula Shell…
- [ ] Flatpak packaging (needs sandbox escapes — tricky for themers)

## Security notes

- Only the **exact upstream repos/URLs listed in `themeforge/data/bundle.json`**
  are ever downloaded and executed — never arbitrary URLs. Keep it that way
  when adding families.
- Archives are extracted with zip-slip/path-traversal guards, and release
  asset filenames are sanitised before use as local paths.
- The `script` strategy runs upstream `install.sh` with **your** user rights,
  pointed only at your user directories (`-d`/`-i`). It never gets root. For
  release-grade hardening (pinned tags + SHA-256 checksums) see the roadmap.

## Tests

```bash
python3 -m unittest discover -s tests            # hermetic unit tests
THEMEFORGE_NET_TESTS=1 python3 -m unittest discover -s tests  # + live release checks
```

## Licenses

The bundled themes, icon packs and wallpapers are the work of their respective
authors and remain under their original licenses (MIT / GPL). Each family in
`themeforge/data/bundle.json` carries `license` and `homepage` fields so
attribution stays intact. ThemeForge itself is MIT.

## Support ThemeForge

ThemeForge is free and open source. If it saves you time or makes your desktop
yours, consider supporting development — every contribution goes straight back
into the catalog:

- **itch.io** — pay-what-you-want download of the latest release:
  https://YOUR-NAME.itch.io/themeforge
- **Ko-fi** — buy me a coffee: https://ko-fi.com/YOUR-HANDLE
- **GitHub Sponsors** — recurring support: (link once sponsors are enabled)

> Replace the `YOUR-NAME` / `YOUR-HANDLE` placeholders above with your real
> storefront links when the pages are live.

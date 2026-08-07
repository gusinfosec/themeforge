# RESUME.md — project handoff

> Read this first when resuming work on this project. Written 2026-08-06, updated 2026-08-06 (session 2).

## What this is

**ThemeForge** — an original, open-source equivalent of **Theme Studio** (a
$19 closed-source GNOME theming app by YouTube channel "Linux Tex", demoed at
https://www.youtube.com/watch?v=_qREvPL36LQ). One-click desktop theming for
**Ubuntu, Fedora, and Arch** (GNOME desktop): curated "Looks" (GTK theme +
GNOME Shell theme + icon pack + light/dark mode + **wallpaper**), installed
user-locally (no root, no package manager), reversible via "reset to defaults".

## User decisions locked in (from Q&A)

- **Stack:** Python + GTK4/libadwaita (PyGObject) — chosen as "best & fast"
- **Interfaces:** shared engine powers both a GUI and a CLI
- **Packaging:** native packages per distro (.deb / .rpm / AUR PKGBUILD) — Flatpak later
- **Bundle:** 10–15 families originally; we now ship **19 families + 6 Looks**
- **Monetization plan (session 2):** open-source on GitHub + paid download on
  **itch.io** (primary) with **Ko-fi tips** and **GitHub Sponsors** as support
  channels — see "Selling strategy" below.

## Project location & structure

```
/home/gus/coding/themeforge/
├── pyproject.toml           # pip packaging (builds a clean wheel; entry points)
├── LICENSE                  # MIT (app) + note that themes stay under upstream licenses
├── README.md                # full docs, bundle table, roadmap, selling notes
├── themeforge.desktop       # GUI launcher (Exec=themeforge-gui)
├── requirements.txt         # PyGObject (only runtime dep)
├── themeforge/
│   ├── cli.py               # argparse CLI: status/list/install/apply/uninstall/reset/gui
│   ├── gui.py               # GTK4/libadwaita GUI: Looks/Themes/Icons/Wallpapers + search + uninstall
│   ├── installer.py         # core engine: GitHub fetch, zip/tar extract (zip-slip-safe),
│   │                       #   asset + script + url/wallpaper strategies, manifest,
│   │                       #   uninstall, backgrounds dir, locks
│   ├── apply.py             # gsettings apply/reset (incl. picture-uri wallpapers), dry-run
│   ├── bundle.py            # bundle.json loader/validator (kinds: gtk/shell/icons/cursor/wallpaper)
│   ├── distro.py            # /etc/os-release detection (ubuntu/fedora/arch) + defaults
│   └── data/bundle.json     # 19 families + 6 Looks (all sources live-verified)
└── tests/test_engine.py     # 29 hermetic unit tests + 2 live network tests
```

## Status: DONE & VALIDATED (session 2)

- **29 unit tests pass**, 2 live network tests pass
  (`THEMEFORGE_NET_TESTS=1 python3 -m unittest discover -s tests`) — every
  GitHub asset pattern matches a real release; Catppuccin installs end-to-end.
- **All 7 wallpaper URLs live-verified** (HTTP 200, sizes 0.2–17 MB).
- Wheel builds cleanly: `python3 -m pip wheel . --no-deps` (bundle.json + LICENSE
  packaged, `themeforge` + `themeforge-gui` entry points).
- **GUI smoke-tested on the real display** — builds, all tabs populate,
  search + wallpapers tab + uninstall buttons work.
- CLI verified with temp dirs; `python -m themeforge` exit codes fixed
  (`__main__.py` now `sys.exit(main())`).

### New in session 2
- **Wallpapers per Look** — new `kind: "wallpaper"` + `source.type: "url"`
  strategy; installed to `~/.local/share/backgrounds`; applied via
  `org.gnome.desktop.background picture-uri` (+ `picture-uri-dark`). Failures
  are non-fatal to a Look.
- **`themeforge uninstall <family>`** + GUI Uninstall buttons (manifest-driven).
- **GUI polish** — Wallpapers tab, per-page search, rows refresh after actions.
- **Catalog growth** — WhiteSur look + 7 wallpaper families (Catppuccin
  Mocha/Latte, Dracula, Rosé Pine, Orchis, Colloid, WhiteSur). **Rosé Pine's
  GTK family/look was dropped after live verification**: its release assets
  (`gtk4.tar.gz`) are CSS-only with no `index.theme`/`gtk-4.0` dirs, so it
  doesn't fit the theme-dir engine — its wallpaper is kept (standalone).
- **Packaging** — pyproject.toml, LICENSE (MIT), .desktop file.
- **Fedora validated** — `is_fedora` + `ID_LIKE=fedora` (Nobara etc.) covered
  by tests; extension package + Adwaita defaults already correct in distro.py.

## Selling strategy (decided session 2 — details in chat)

- **Primary storefront: itch.io** — 10% default platform share (0%–100% optional),
  ~2.9% + $0.30 processing, native Linux audience, direct file downloads, no DRM.
- **Support/tips: Ko-fi** (0% on tips, 5% on shop for free tier) and
  **GitHub Sponsors** (0% fee on personal accounts) alongside the free repo.
- **Payhip as the key/paid-Download alternative** if license keys or EU VAT
  automation (automatic MoR) become important (5% free / 2% at $29/mo).
- Next: git init + first commit, GitHub repo, .deb/.rpm/AUR packaging.

## Quickstart (for the GNOME test session)

```bash
cd /home/gus/coding/themeforge
python3 -m themeforge status                     # distro + current settings
python3 -m themeforge list                       # looks & families (19)
python3 -m themeforge apply --dry-run catppuccin-mocha   # preview
python3 -m themeforge apply catppuccin-mocha     # real apply (themes + icons + wallpaper)
python3 -m themeforge gui                        # graphical app
python3 -m themeforge reset                      # back to Yaru (Ubuntu) / Adwaita
```

Testing on a real desktop: apply a Look, then **log out and back in** — GNOME
Shell themes only appear after re-login (the engine flags this).

## Important caveats

- **This dev machine is EndeavourOS + Hyprland, not GNOME.** Installing themes
  works (files land in `~/.local/share/themes`, `~/.icons`), but they won't
  visually apply without a GNOME session. Testing on GNOME requires a real
  GNOME install (VM/other machine) or logging into a GNOME session.
- **GNOME Shell themes need the User Themes extension** (Ubuntu:
  `gnome-shell-extensions`; Fedora: `gnome-shell-extension-user-theme`; Arch:
  AUR). Engine checks and reports this.
- **Licensing:** the bundled themes/icons/wallpapers are MIT/GPL open-source —
  downloaded from upstream at install time, never redistributed. ThemeForge
  itself is MIT. Do not copy Theme Studio's app name/branding.
- **Security model:** only the exact repos/URLs in bundle.json are ever
  downloaded/executed. Never add arbitrary URLs. install.sh runs with user
  rights only.
- **Wallpaper sources:** catppuccin's official `wallpapers` repo 404s (gone);
  community mirrors are pinned instead (orangci, iQuickDev). Keep URLs verified
  if the catalog grows. `THEMEFORGE_HOME` is overridden by `XDG_DATA_HOME` /
  `XDG_CACHE_HOME` if those are set.

## Roadmap / natural next steps

1. ✅ DONE — repo created and pushed: **http://100.108.60.110:3000/gus/themeforge** (public, `main`)
   (`git init`, first commit `255491b`, pushed over SSH from this machine)
2. Set up itch.io page (upload wheel/tarball + screenshots), Ko-fi page, GitHub Sponsors
3. Native packaging: Fedora (.rpm spec) and Arch (AUR PKGBUILD); Ubuntu .deb later
4. More families (Tokyo Night, Everforest, Gruvbox, Dracula Shell) — verify sources first
5. `select` globs per Look so light/dark Looks pick matching variants deterministically
6. Live theme previews (screenshots); TUI (rich/textual); Flatpak packaging
7. Release-grade hardening: pinned tags + SHA-256 checksums

## Pricing & storefront (session 3, decided by user)

- **Price: $12.00 USD flat** on every paid channel (itch.io / Payhip / Ko-fi
  shop) — recorded in SELLING.md.
- **itch.io page: new project under the existing cyberlabgames account**
  (`cyberlab.itch.io/themeforge`) — not a separate account, not the games page.
- **Screenshots generated** (real captures, OCR-verified) in `screenshots/`:
  looks, themes, icons, wallpapers (GUI) + cli. GUI renders dark on this box.
- Release artifacts live in `dist/` (gitignored): tarball + wheel.

## Repo & git (session 3)

- Repo **`gus/themeforge`** created via Gitea API (default branch `main`, topics:
  gnome/gtk/libadwaita/linux/theming/wallpapers). **Private** — flipped to
  private on 2026-08-07 per user; go public when polished.
- First commit `255491b` pushed; `origin` set, `main` tracks `origin/main`.
- Release **v0.1.0** published (release id 26) with `themeforge-0.1.0.tar.gz`
  + `themeforge-0.1.0-py3-none-any.whl` attached; tag `v0.1.0` pushed.
- This machine pushes to Gitea over **SSH** (`ssh://100.108.60.110:2222`) — a
  global URL rewrite handles it; no credentials stored in `.git/config`.

## Files changed this session (session 2, all under /home/gus/coding/themeforge/)

- `themeforge/installer.py`, `themeforge/bundle.py`, `themeforge/apply.py`,
  `themeforge/cli.py`, `themeforge/gui.py`, `themeforge/__main__.py`,
  `themeforge/data/bundle.json`
- `tests/test_engine.py` (+7 tests, Fedora ID_LIKE coverage, wallpaper guards)
- NEW: `pyproject.toml`, `LICENSE`, `themeforge.desktop`; rewritten `README.md`;
  this file updated.

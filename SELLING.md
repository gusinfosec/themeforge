# SELLING.md — storefront copy & release checklist

> Copy-paste source for the ThemeForge storefront pages. Update this file with
> each release so the listings stay in sync. Replace every `YOUR-…` placeholder
> with the real account/page values once they exist.

## Where ThemeForge is sold / supported

| Channel | Purpose | Fee | URL (placeholder) |
|---|---|---|---|
| GitHub / Gitea repo | free source, releases | — | your Gitea instance |
| itch.io | paid pay-what-you-want download | 10% platform (default) + ~2.9%+$0.30 processing | `https://YOUR-NAME.itch.io/themeforge` |
| Ko-fi | one-off tips | 0% on tips | `https://ko-fi.com/YOUR-HANDLE` |
| GitHub Sponsors | recurring support | 0% on personal accounts | (enable when repo is live) |
| Payhip (later) | paid download + license keys, EU VAT handled | 5% free / 2% Plus | — |

---

## itch.io listing

- **Page URL:** `https://YOUR-NAME.itch.io/themeforge`
- **Classification:** Tools → Desktop → Customization
- **Pricing:** Pay-what-you-want — **$3 minimum, $5 suggested**
  (below ~$2 the $0.30 + 2.9% processor fee eats the margin; itch recommends ≥ $2)
- **Visibility:** public

### Short tagline

```
One-click GNOME theming for Ubuntu, Fedora & Arch
```

### Long description

```
ThemeForge is a one-click theming studio for GNOME — the open-source way.
Pick a curated Look (a coordinated GTK theme, icon pack, light/dark mode and
matching wallpaper), install it with a single click, and reset to your
distro's defaults whenever you like.

No root. No system writes. No risk. Everything installs into your user
directories (~/.local/share/themes, ~/.icons, ~/.local/share/backgrounds)
and is fully reversible.

Included: 6 curated Looks (Catppuccin Mocha & Latte, Dracula, Orchis Light,
Colloid Dark, WhiteSur) · 8 GTK themes · 4 icon packs · 7 matching wallpapers

Works on Ubuntu (+ derivatives), Fedora (+ derivatives), Arch (+ derivatives)
— GNOME desktop. A graphical app and a terminal CLI.

What's inside
- Graphical app (GTK4/libadwaita) with a Wallpapers tab and search
- CLI: status, list, apply, install, uninstall, reset
- Themes fetched from their official upstream projects and cached locally
- Dry-run previews — see exactly what will change before it does
- Per-theme uninstall and one-click "reset to defaults" (Yaru/Adwaita)

Requirements: Python 3.12+, a GNOME session, and the User Themes extension
for Shell themes (the app detects and explains this).

ThemeForge is MIT licensed and its entire catalog is open source —
supporting the itch.io download funds development, it doesn't unlock
walled content.
```

### Tags

```
gnome, theme, linux, desktop, gtk, libadwaita, icons, wallpaper, customization
```

### Screenshots (5–8, 16:9)

1. GUI — Looks tab (curated Looks with Apply buttons)
2. GUI — Wallpapers tab with search
3. Desktop "before / after" shot (stock → Catppuccin Mocha Look)
4. CLI — `themeforge apply --dry-run dracula` output
5. CLI — `themeforge status` output
6. GUI — Uninstall confirmation dialog
7. (optional) Wallpaper showcase — the 7 wallpapers side by side

Cover image: the app window over a themed desktop.

### Upload file

Source tarball named `themeforge-<version>.tar.gz`, built from the repo:

```bash
git archive -o themeforge-0.1.0.tar.gz HEAD
```

In the file's description on itch, add:

```
Install:
  pip install .          # from the extracted source, or
  python3 -m themeforge --help
Run:
  themeforge gui         # graphical app
  themeforge apply catppuccin-mocha
```

---

## Ko-fi page

- **Page name:** ThemeForge
- **Tagline:** Support open-source GNOME theming
- **Text:**

```
ThemeForge is a free, open-source one-click theming app for GNOME
(Ubuntu, Fedora, Arch). If it made your desktop feel like home, a coffee
keeps the catalog growing — new Looks, wallpapers and distro packages.
```

---

## GitHub Sponsors (once enabled)

- **Tier 1 — "Coffee"** · $2/mo: supporter badge in the README thanks list.
- **Tier 2 — "Patron"** · $5/mo: early access to new Looks before release.
- **Tier 3 — "Backer"** · $10/mo: request a look/theme from the roadmap queue.

---

## Release checklist (every version)

1. `git tag v<version>` + push tag.
2. Build wheel (`python3 -m pip wheel . --no-deps`) and source tarball
   (`git archive -o themeforge-<version>.tar.gz HEAD`).
3. Attach both to the Gitea/GitHub release.
4. Update the itch.io upload with the new tarball; bump the description's
   version/date if shown.
5. Bump `__version__` in `themeforge/__init__.py` **before** tagging.
6. Refresh the README bundle table if the catalog changed.

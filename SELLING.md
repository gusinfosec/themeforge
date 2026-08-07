# SELLING.md — storefront copy & release checklist

> Copy-paste source for the ThemeForge storefront pages. Update this file with
> each release so the listings stay in sync. Replace every `YOUR-…` placeholder
> with the real account/page values once they exist.

## Where ThemeForge is sold / supported

| Channel | Purpose | Fee | URL |
|---|---|---|---|
| Gitea repo | free source, releases | — | http://100.108.60.110:3000/gus/themeforge |
| itch.io | paid download | 10% platform (default) + ~2.9%+$0.30 processing | `https://cyberlab.itch.io/themeforge` |
| Ko-fi | paid download (shop) | ~5% + processing | `https://ko-fi.com/s/680f36c441` |
| GitHub Sponsors | recurring support | 0% on personal accounts | https://github.com/gusinfosec/themeforge (enable once repo is public) |
| Payhip | paid download, EU VAT handled (Cyberlab store) | 5% free / 2% Plus | `https://payhip.com/b/n82Sq` (store: `https://payhip.com/cyberlabgames`) |

## Pricing (unified — one price everywhere)

**$12.00 USD — fixed, on every paid channel** (itch.io, Payhip, Ko-fi shop).
No pay-what-you-want variants, no regional pricing — the same number everywhere
so buyers never see a cheaper version and wonder why.

Net per sale at $12 (approx):
- itch.io: $12 − 10% ($1.20) − ~2.9%+$0.30 ($0.65) ≈ **$10.15**
- Payhip free plan: $12 − 5% ($0.60) − processing ≈ **$10.90**
- Ko-fi shop: $12 − 5% ($0.60) − processing ≈ **$10.90**

---

## itch.io listing

- **Page URL:** `https://cyberlab.itch.io/themeforge` (new project page under the
  existing cyberlabgames account — separate from your games, same payout)
- **Classification:** Tools → Desktop → Customization
- **Pricing:** **$12.00 USD fixed** (unified across all platforms)
- **Visibility:** public (flip to public when the repo goes public)

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

### Screenshots

Already generated (repo: `screenshots/`, real captures, verified by OCR):

| File | Shows |
|---|---|
| `screenshots/themeforge-looks.png` | GUI — Looks tab (all 6 Looks + Apply buttons) |
| `screenshots/themeforge-themes.png` | GUI — Themes tab with search |
| `screenshots/themeforge-icons.png` | GUI — Icons tab |
| `screenshots/themeforge-wallpapers.png` | GUI — Wallpapers tab |
| `screenshots/themeforge-cli.png` | CLI — `themeforge list` + `apply --dry-run` in a terminal |

All are 919×945 window captures (dark theme). itch's editor can crop a 16:9
cover from them. Optional extras for later: a desktop before/after shot and the
Uninstall dialog.

Cover image: `themeforge-looks.png` cropped to 16:9, or a fresh full-desktop
shot once the Look is applied on a real GNOME session.

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

## Ko-fi shop item

- **Shop URL:** `https://ko-fi.com/s/680f36c441` (product: ThemeForge — GNOME One-Click Theming)
- **Price:** **$12.00 USD fixed** (pay-what-you-want off — matches itch.io)
- **Type:** Digital item (attachment: `themeforge-0.1.0.tar.gz`)
- **Cover image:** `cover.png` (reused from the itch.io page)
- **Tagline:** Support open-source GNOME theming
- **Text:**

```
ThemeForge is a free, open-source one-click theming app for GNOME
(Ubuntu, Fedora, Arch). If it made your desktop feel like home, a coffee
keeps the catalog growing — new Looks, wallpapers and distro packages.
```

---

## Payhip shop item (Cyberlab store)

- **Store:** `https://payhip.com/cyberlabgames` (display name **Cyberlab**, dark
  Tusk theme, About Me section)
- **ThemeForge product URL:** `https://payhip.com/b/n82Sq`
- **Price:** **$12.00 USD fixed** (matches itch.io + Ko-fi)
- **Type:** Digital product (file: `themeforge-0.1.0.tar.gz`)
- **Cover image:** `release/themeforge-cover.png`
- **Description:** same long description as itch (plain text, no markdown)

### Full Cyberlab catalog on Payhip (Phase 1)

The store also mirrors the itch catalog (all prices matched to itch):

| Product | Price |
|---|---|
| ThemeForge | $12.00 |
| SECTOR-9 — Co-op Combat Simulation | $9.99 |
| HUSH | $7.99 |
| DESCENT | $7.99 |
| COMPLETE COLLECTION | $44.99 |
| HORROR COLLECTION | $19.99 |
| STRATEGY COLLECTION | $12.99 |
| CLASSICS COLLECTION | $8.99 |
| Dungeon Gen Toolkit | $9.99 |
| Tower Defense Toolkit | $9.99 |
| Horror Atmosphere Toolkit | $9.99 |
| Cyberlab Systems Collection | $24.99 |

**Rule:** keep every product price identical across itch.io, Ko-fi and Payhip.
Phase 2 (pending Payhip game sales): mirror the long-tail games (Solitaire,
Breaker, 3D Checkers, etc.).

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

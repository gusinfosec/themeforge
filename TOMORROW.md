# TOMORROW.md — ThemeForge launch day plan (step-by-step)

> Everything needed in one place. Contact email for press: **folivares@cyberglobal.ai**
> (same address for Payhip tomorrow so all follow-ups land in one inbox).

---

## ✅ Already done (don't redo)

| Channel | URL | Status |
|---|---|---|
| Gitea repo | `http://100.108.60.110:3000/gus/themeforge` | v0.1.0 release, tarball + wheel |
| itch.io | `https://cyberlab.itch.io/themeforge` | **LIVE** — $12.00 fixed |
| Ko-fi | `https://ko-fi.com/s/680f36c441` | **LIVE** — $12.00 fixed |
| Storefront docs | `SELLING.md`, `README.md` | URLs filled in |

**Unified price everywhere: $12.00 USD fixed** (no pay-what-you-want).

---

## ☕ Step 1 — Payhip (morning, ~30 min)

1. Create account at **https://payhip.com** using `folivares@cyberglobal.ai`.
2. **Create a product:**
   - Name: `ThemeForge — GNOME One-Click Theming`
   - Price: **$12.00 USD fixed**
   - Type: digital download
   - Upload file: `release/themeforge-0.1.0.tar.gz` (28 KB)
   - Cover image: `release/themeforge-cover.png` (630×500)
3. **Description** — paste from SELLING.md "itch.io listing → Long description"
   (plain text is fine; strip the code fences).
4. Save **as draft** → preview → publish.
5. Update `SELLING.md`:
   - table row: `| Payhip | paid download + license keys | 5% free / 2% Plus | <your-payhip-url> |`
   - pricing section note: add Payhip net ≈ $10.90
6. Tell Buffy the URL so the README + SELLING.md get updated.

> Payhip tip: enable the "sell to EU" VAT handling — it's built in and was the
> reason Payhip was chosen over alternatives.

---

## 📰 Step 2 — Linux press (afternoon, ~20 min)

Use email **folivares@cyberglobal.ai** and credit name **Cyberlab Games**.

### 2a. OMG! Ubuntu — tip form
- URL: **https://www.omgubuntu.co.uk/tip**
- Link field: `https://cyberlab.itch.io/themeforge`
- Message (paste):

```
ThemeForge — one-click GNOME theming for Ubuntu (open source, $12)

ThemeForge is a free, open-source theming studio for GNOME: pick a curated
"Look" — a coordinated GTK theme, icon pack, light/dark mode and matching
wallpaper — and install it with one click, no root and no system writes.
Everything lands in the user directory (~/.local/share/themes, ~/.icons,
~/.local/share/backgrounds) and is fully reversible with a "reset to
defaults" button.

It ships 6 Looks (Catppuccin Mocha & Latte, Dracula, Orchis Light, Colloid
Dark, WhiteSur), 8 GTK themes, 4 icon packs and 7 wallpapers, with a
GTK4/libadwaita GUI plus a terminal CLI (themeforge apply catppuccin-mocha).
Works on Ubuntu + derivatives, Fedora and Arch.

Downloads are $12 on itch.io (open source — MIT — so the fee funds
development, not access): https://cyberlab.itch.io/themeforge

Happy to provide screenshots of it working on Ubuntu.
```

### 2b. It's FOSS — contact form
- URL: **https://itsfoss.com/contact-us/**
- Subject: `Open-source GNOME theming app: ThemeForge`
- Message (paste):

```
Hi It's FOSS team,

I'd love to see ThemeForge covered: an open-source (MIT) one-click theming
studio for GNOME. Pick a curated Look — coordinated GTK theme + icon pack +
light/dark mode + wallpaper — and apply it with a single click. No root, no
system writes, fully reversible.

Highlights:
- 6 Looks (Catppuccin Mocha & Latte, Dracula, Orchis Light, Colloid Dark,
  WhiteSur), 8 GTK themes, 4 icon packs, 7 wallpapers
- GTK4/libadwaita GUI and a terminal CLI
- Ubuntu, Fedora & Arch support, detects User Themes extension requirements
- Screenshots and demo: https://cyberlab.itch.io/themeforge
  (downloads $12, source free)

Happy to provide screenshots or answer any questions. Thanks for
considering it!

— Cyberlab Games
```

### 2c. Backups (if 2a/2b get no reply in ~1 week)
- **DebugPoint** — contact form at debugpoint.com (submit a tip)
- **Linux Uprising** — linuxuprising.com contact form

---

## 🖥️ Step 3 — Site review fixes (Cyber Global product family, ~30 min)

Review done — actions to take:

| Site | Action |
|---|---|
| outreachsafe.com | Pick www vs non-www (currently 301-redirects) + add `<link rel="canonical">` (missing) |
| compliance.cyberglobal.ai | Rewrite meta description (currently 2 words: "Codify Compliance. Simplify Audits.") → ~150 chars with keywords |
| mergemind.dev | Add meta description (currently none) |
| cyberglobal.ai | Add meta description + move "5 products" links higher on the page |
| All 5 product pages | Add Open Graph tags (og:title, og:description, og:image) — helps sharing on X/LinkedIn/Mastodon, and press |
| Propaudit | Fix risk-scale wording — "12/100 — Critical" reads wrong (low number, "Critical" label) |
| InboxSafe | Confirm the "Add to Chrome" CTA has a real Chrome Web Store listing behind it |
| All | Cross-link the 5 products to each other (they're a suite) |

---

## 🌐 Step 4 — Social & directories (quick wins, ~15 min)

> ✅ **LinkedIn posts: DONE** (already posted). Remaining: Mastodon + X.

- **Mastodon** (fosstodon.org) — post (copy below) + screenshot, tags `#linux #gnome #themeforge`
- **X/Twitter** — post (copy below) + screenshot, tag `#Linux #GNOME #DesktopCustomization`
- **Hacker News "Show HN"** — title: "Show HN: ThemeForge – one-click GNOME theming (CLI + GUI)" + link to itch page
- **Awesome-gnome GitHub list** — open a PR adding the repo link to the themes section

### Post copy (Mastodon / X — trim to fit each platform)

```
I built ThemeForge — a one-click theming studio for GNOME 🎨

Pick a curated Look (GTK theme + icon pack + light/dark mode + wallpaper),
apply it with a single click. No root, no system writes, fully reversible.

• 6 Looks: Catppuccin Mocha & Latte, Dracula, Orchis, Colloid, WhiteSur
• 8 GTK themes · 4 icon packs · 7 wallpapers
• GTK4/libadwaita GUI + terminal CLI
• Ubuntu, Fedora & Arch — MIT licensed, open source

$12 download (funds development, not access):
https://cyberlab.itch.io/themeforge

#linux #gnome #themeforge #desktopcustomization
```

---

## 🧾 Quick reference

| Thing | Value |
|---|---|
| itch.io | https://cyberlab.itch.io/themeforge |
| Ko-fi | https://ko-fi.com/s/680f36c441 |
| Tarball | `release/themeforge-0.1.0.tar.gz` (28 KB) |
| Cover | `release/themeforge-cover.png` (630×500) |
| Press email | folivares@cyberglobal.ai |
| Price everywhere | **$12.00 USD** |

> After Payhip goes live, ask Buffy to run a final **4-way price alignment check**
> (itch / Ko-fi / Payhip / Gitea) and update SELLING.md + README.

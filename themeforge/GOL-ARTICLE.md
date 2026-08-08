# ThemeForge — one-click GNOME theming, no root required

*Draft article for GamingOnLinux (`/submit-article/`). Paste as-is into Title + Body.*

---

**Title:** ThemeForge: one-click GNOME theming, no root, no system writes

**Body:**

Theming GNOME has always meant one of two things: hand-editing config files, or
trusting a random script that writes into system directories. ThemeForge takes a
third path — it's an open-source, one-click theming app that runs entirely in
your user space.

Pick a curated **Look** — a coordinated GTK theme, icon pack and wallpaper that
have been matched to work together — preview it, and apply it with one click.
No root, no package manager, no writes outside your own `~/.local`, `~/.icons`
and `~/.cache`. Everything is reversible: one command resets you back to your
distro's defaults.

**What's inside**

- 19 families in the first bundle: GTK themes (Catppuccin, Dracula, Orchis,
  WhiteSur, Colloid, Fluent, Graphite), icon packs (Papirus, Tela, Colloid,
  Fluent) and matching wallpapers, arranged into 6 curated Looks
- A GTK 4 / libadwaita GUI **and** a full CLI (`themeforge apply catppuccin`,
  `--dry-run` previews, per-family uninstall, `reset`)
- Works on GNOME 45+ across Ubuntu, Fedora and Arch (including derivatives)
- Clean security story: only exact upstream URLs from the pinned bundle manifest
  are ever fetched, archives are zip-slip guarded, and the one script-based
  installer runs with your user rights into your user directories only

**Where to get it**

- Source + releases: MIT-licensed
- Prebuilt download: **$12** on itch.io, Ko-fi and Payhip (same price everywhere)
- Screenshots and docs in the README

It's my first open-source release — feedback on the catalog and the design is
very welcome.

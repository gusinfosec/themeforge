# CLIPBOARD-NOTES.md — kitty + tmux Wayland clipboard fix

> Fixed 2026-08-08. Symptom: text copied in the terminal (kitty + tmux) never
> reached the browser / other apps — "I see it copied in the terminal but
> nothing works outside."

## Root causes found

1. **Wedged cliphist watcher** — `wl-paste --watch cliphist store` had been
   running for 2 days (since Aug 6) plus a zombie `wl-paste` process. A stale
   clipboard manager silently ate copies. → killed both, restarted fresh.
2. **Copies only wrote CLIPBOARD, not PRIMARY** — middle-click paste (PRIMARY
   selection) got nothing; only Ctrl+V (CLIPBOARD) worked. Classic Linux gotcha.
3. **kitty wasn't accepting tmux's OSC 52 writes** — needed explicit
   `clipboard_control write-clipboard write-primary`.
4. **tmux had no `set-clipboard on`** — tmux didn't push selections to the
   terminal's clipboard via OSC 52.

## Files changed

| File | Change |
|---|---|
| `~/.local/bin/copy-clip` | **NEW helper** — copies stdin to BOTH `wl-copy` (CLIPBOARD) and `wl-copy --primary` (PRIMARY) |
| `~/.tmux.conf` | `set -g set-clipboard on`; `y`/`Y`/`Enter`/mouse-drag copy via `copy-clip` |
| `~/.config/kitty/kitty.conf` | `clipboard_control write-clipboard write-primary`; `copy_on_select clipboard+primary`; `ctrl+shift+c/v/s` bindings |
| `~/.config/hypr/conf/autostart.lua` | (unchanged) already runs `wl-paste --watch cliphist store` |

Backups: `~/.tmux.conf.bak.1786224269`, `~/.config/kitty/kitty.conf.bak.1786224269`.

## How to copy/paste now

- **Copy:** select text (mouse-drag, or `C-b [` + `v` + `y`) → lands in system clipboard
- **Paste:** `Ctrl+V` anywhere, or **middle-click** anywhere — both work
- **History:** `mod+V` opens cliphist to grab any previous copy

## If it breaks again

```bash
# 1. Restart the clipboard watcher
pkill -f 'wl-paste --watch' ; nohup wl-paste --watch cliphist store >/dev/null 2>&1 &

# 2. Verify the copy-clip helper exists
ls ~/.local/bin/copy-clip

# 3. Reload tmux config
tmux source-file ~/.tmux.conf

# 4. Reload kitty config (Ctrl+Shift+F5) and test:
#    select text -> y -> wl-paste   (should show the text)
#    select text -> y -> wl-paste --primary   (should show the text too)
```

## Key fact

Firefox is Wayland-native on this system (`MOZ_ENABLE_WAYLAND=1`), so it reads
the Wayland clipboard directly. No X↔Wayland bridge (wl-clipboard-x11) is needed
for Firefox, but `xclip` is installed for any XWayland apps.

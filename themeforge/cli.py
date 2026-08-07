"""Command-line interface for ThemeForge."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from themeforge import __version__
from themeforge import apply as apply_mod
from themeforge import bundle as bundle_mod
from themeforge import distro as distro_mod
from themeforge.installer import InstallError, build_forge


def _forge(args):
    return build_forge(args.themes_dir, args.icons_dir, args.cache_dir,
                       getattr(args, "backgrounds_dir", None))


def _print_result(result) -> None:
    for c in result.changed:
        print(f"  ✓ {c}")
    for s in result.skipped:
        print(f"  – {s} (skipped)")
    if result.logout_needed:
        print("  ℹ log out and back in to see GNOME Shell theme changes.")


def cmd_status(args) -> int:
    forge = _forge(args)
    d = distro_mod.detect()
    _, ext_state = apply_mod.user_themes_extension_state()
    print(f"Distro:      {d.pretty_name or d.id}  (id={d.id}, id_like={d.id_like or '-'})")
    print(f"Defaults:    GTK '{d.reset_theme()}' / icons '{d.reset_icon_theme()}'")
    print(f"User Themes: {ext_state}")
    print(f"Themes dir:  {forge.themes_dir}")
    print(f"Icons dir:   {forge.icons_dir}")
    print(f"Cache dir:   {forge.cache_dir}")
    print(f"Wallpapers:  {forge.backgrounds_dir}")
    print("Settings:")
    for key in ("gtk-theme", "icon-theme", "color-scheme"):
        print(f"  {key}: {apply_mod.gsettings_get(apply_mod.INTERFACE, key) or '(unset)'}")
    installed = forge.installed_ids()
    print(f"Installed families ({len(installed)}): {', '.join(installed) or 'none'}")
    return 0


def cmd_list(args) -> int:
    bundle = bundle_mod.load_bundle(args.bundle)
    forge = _forge(args)
    print("Looks:")
    for lk in bundle_mod.looks(bundle):
        print(f"  {lk['id']:<20} {lk.get('name')}")
    print(f"\nFamilies ({len(bundle_mod.families(bundle))}):")
    for fam in bundle_mod.families(bundle):
        mark = "installed" if forge.installed(fam["id"]) else ""
        print(f"  {fam['id']:<20} {fam['kind']:<5} {fam['strategy']:<7} {fam['name']}  {mark}")
    return 0


def cmd_install(args) -> int:
    bundle = bundle_mod.load_bundle(args.bundle)
    forge = _forge(args)
    try:
        fam = bundle_mod.family(bundle, args.family)
    except KeyError:
        print(f"unknown family '{args.family}' — see 'themeforge list'", file=sys.stderr)
        return 1
    try:
        info = forge.install_family(fam, force=args.force)
    except InstallError as exc:
        print(f"install failed: {exc}", file=sys.stderr)
        return 1
    print(f"Installed {fam['id']} (version {info.get('version')}):")
    for kind in ("themes", "shell", "icons"):
        for name in info.get(kind, []):
            print(f"  {kind}: {name}")
    return 0


def cmd_apply(args) -> int:
    bundle = bundle_mod.load_bundle(args.bundle)
    forge = _forge(args)
    try:
        look = bundle_mod.look(bundle, args.target)
        result = apply_mod.apply_look(look, forge, bundle, dry_run=args.dry_run)
    except KeyError:
        try:
            fam = bundle_mod.family(bundle, args.target)
        except KeyError:
            print(f"unknown look or family '{args.target}' — see 'themeforge list'",
                  file=sys.stderr)
            return 1
        result = apply_mod.apply_family(fam, forge, bundle, dry_run=args.dry_run)
    except InstallError as exc:
        print(f"apply failed: {exc}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("DRY RUN — nothing was changed. Planned changes:")
    _print_result(result)
    return 0


def cmd_reset(args) -> int:
    bundle = bundle_mod.load_bundle(args.bundle)
    forge = _forge(args)
    result = apply_mod.reset(forge, bundle, distro_mod.detect(),
                             purge=args.purge, dry_run=args.dry_run)
    if args.dry_run:
        print("DRY RUN — nothing was changed. Planned changes:")
    _print_result(result)
    return 0


def cmd_uninstall(args) -> int:
    bundle = bundle_mod.load_bundle(args.bundle)
    forge = _forge(args)
    try:
        fam = bundle_mod.family(bundle, args.family)
    except KeyError:
        print(f"unknown family '{args.family}' — see 'themeforge list'", file=sys.stderr)
        return 1
    removed = forge.remove_family(fam["id"])
    if not removed:
        print(f"'{fam['id']}' is not installed — nothing to remove")
        return 1
    for path in removed:
        print(f"  ✗ removed {path}")
    print("Run 'themeforge reset' to restore default settings.")
    return 0


def cmd_gui(args) -> int:
    from themeforge.gui import run_gui
    return run_gui(_forge(args), args.bundle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="themeforge",
        description="One-click GNOME theming for Ubuntu, Fedora and Arch.",
    )
    parser.add_argument("--version", action="version", version=f"themeforge {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser, *, dry_run: bool = False) -> None:
        p.add_argument("--bundle", type=Path, help="path to an alternative bundle.json")
        p.add_argument("--themes-dir", type=Path, help="theme install dir (default: ~/.local/share/themes)")
        p.add_argument("--icons-dir", type=Path, help="icon install dir (default: ~/.local/share/icons)")
        p.add_argument("--cache-dir", type=Path, help="download cache dir (default: ~/.cache/themeforge)")
        p.add_argument("--backgrounds-dir", type=Path,
                       help="wallpaper install dir (default: ~/.local/share/backgrounds)")
        if dry_run:
            p.add_argument("--dry-run", action="store_true", help="show what would change, change nothing")

    p = sub.add_parser("status", help="distro, current settings, install state"); common(p)
    p = sub.add_parser("list", help="list bundled looks and families"); common(p)
    p = sub.add_parser("install", help="download + install one family")
    common(p)
    p.add_argument("family")
    p.add_argument("--force", action="store_true", help="re-download and reinstall even if present")
    p = sub.add_parser("apply", help="apply a curated look (or a single family)")
    common(p, dry_run=True)
    p.add_argument("target")
    p = sub.add_parser("uninstall", help="remove one installed family (themes/icons/wallpapers)")
    common(p)
    p.add_argument("family")
    p = sub.add_parser("reset", help="restore distro defaults (Yaru/Adwaita)")
    common(p, dry_run=True)
    p.add_argument("--purge", action="store_true",
                   help="also delete every theme/icon dir ThemeForge installed")
    p = sub.add_parser("gui", help="launch the graphical front-end"); common(p)

    args = parser.parse_args(argv)
    return {"status": cmd_status, "list": cmd_list, "install": cmd_install,
            "apply": cmd_apply, "uninstall": cmd_uninstall,
            "reset": cmd_reset, "gui": cmd_gui}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

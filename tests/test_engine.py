"""Unit tests for the ThemeForge engine. Hermetic by default.

Network-backed tests run only when THEMEFORGE_NET_TESTS=1.
"""
from __future__ import annotations

import fnmatch
import io
import os
import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from themeforge import apply as apply_mod
from themeforge import bundle as bundle_mod
from themeforge import distro as distro_mod
from themeforge.installer import (
    Forge,
    InstallError,
    discover_themes,
    extract_archive,
    install_dirs,
    latest_release,
)

NET = bool(os.environ.get("THEMEFORGE_NET_TESTS"))


def make_index_theme(d: Path, name: str, kind: str) -> None:
    d.mkdir(parents=True, exist_ok=True)
    if kind == "icons":
        content = f"[Icon Theme]\nName={name}\n"
    else:
        content = f"[Desktop Entry]\nName={name}\nType=X-GNOME-Metatheme\n"
        if kind == "shell":
            (d / "gnome-shell").mkdir(parents=True, exist_ok=True)
        else:
            (d / "gtk-3.0").mkdir(parents=True, exist_ok=True)
    (d / "index.theme").write_text(content, encoding="utf-8")


def make_zip(path: Path, members: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)


def make_tar_gz(path: Path, members: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, "w:gz") as tf:
        for name, content in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            info.mode = 0o755 if name.endswith("install.sh") else 0o644
            tf.addfile(info, io.BytesIO(content.encode()))


class BundleTests(unittest.TestCase):
    def test_bundle_loads_and_is_valid(self):
        data = bundle_mod.load_bundle()
        self.assertGreaterEqual(len(bundle_mod.families(data)), 12)
        self.assertGreaterEqual(len(bundle_mod.looks(data)), 4)
        bundle_mod.validate_bundle(data)  # raises on problems

    def test_every_family_has_required_strategy_fields(self):
        data = bundle_mod.load_bundle()
        for fam in bundle_mod.families(data):
            if fam["strategy"] == "asset" and fam["source"].get("type") != "url":
                self.assertTrue(fam["asset_pattern"], fam["id"])
            elif fam["strategy"] == "script":
                self.assertTrue(fam["script_args"], fam["id"])
            self.assertIn(fam["kind"], ("gtk", "shell", "icons", "cursor", "wallpaper"))

    def test_unknown_look_or_family_raises(self):
        data = bundle_mod.load_bundle()
        with self.assertRaises(KeyError):
            bundle_mod.family(data, "does-not-exist")
        with self.assertRaises(KeyError):
            bundle_mod.look(data, "does-not-exist")


class DistroTests(unittest.TestCase):
    def _release(self, text: str) -> distro_mod.Distro:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "os-release"
            path.write_text(text)
            return distro_mod.parse_os_release(path)

    def test_ubuntu(self):
        d = self._release('ID=ubuntu\nVERSION_ID="24.04"\nPRETTY_NAME="Ubuntu 24.04"\n')
        self.assertTrue(d.is_ubuntu)
        self.assertEqual(d.reset_theme(), "Yaru")
        self.assertEqual(d.reset_icon_theme(), "Yaru")
        self.assertEqual(d.user_themes_extension_package(), "gnome-shell-extensions")

    def test_fedora(self):
        d = self._release("ID=fedora\nVERSION_ID=41\nPRETTY_NAME=\"Fedora Linux 41\"\n")
        self.assertTrue(d.is_fedora)
        self.assertEqual(d.reset_theme(), "Adwaita")
        self.assertEqual(d.reset_icon_theme(), "Adwaita")
        self.assertEqual(d.user_themes_extension_package(), "gnome-shell-extension-user-theme")

    def test_fedora_via_id_like(self):
        # distros that are *like* Fedora (e.g. Nobara) should be treated as Fedora
        d = self._release('ID=nobara\nID_LIKE="fedora"\nPRETTY_NAME="Nobara"\n')
        self.assertTrue(d.is_fedora)
        self.assertEqual(d.user_themes_extension_package(), "gnome-shell-extension-user-theme")

    def test_arch(self):
        d = self._release("ID=arch\nPRETTY_NAME=\"Arch Linux\"\n")
        self.assertTrue(d.is_arch)
        self.assertEqual(d.reset_theme(), "Adwaita")

    def test_missing_file(self):
        d = distro_mod.parse_os_release(Path("/nonexistent/os-release"))
        self.assertEqual(d.id, "unknown")


class DiscoveryTests(unittest.TestCase):
    def test_classifies_gtk_shell_and_icons(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_index_theme(root / "gtk-dir", "GTK", "gtk")
            make_index_theme(root / "icons-dir", "Icons", "icons")
            make_index_theme(root / "shell-dir", "Shell", "shell")
            make_index_theme(root / "both-dir", "Both", "gtk")
            (root / "both-dir" / "gnome-shell").mkdir(exist_ok=True)

            found = discover_themes(root)
            self.assertEqual({p.name for p in found["gtk"]}, {"gtk-dir", "both-dir"})
            self.assertEqual({p.name for p in found["shell"]}, {"shell-dir", "both-dir"})
            self.assertEqual({p.name for p in found["icons"]}, {"icons-dir"})

    def test_install_dirs_copies_and_sorts(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            make_index_theme(src / "Zeta", "Z", "gtk")
            make_index_theme(src / "Alpha", "A", "gtk")
            base = Path(tmp) / "themes"
            names = install_dirs([src / "Zeta", src / "Alpha"], base)
            self.assertEqual(names, ["Alpha", "Zeta"])  # sorted for determinism
            self.assertTrue((base / "Alpha" / "index.theme").exists())

    def test_extract_zip_and_tar(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            zip_path = tmp / "a.zip"
            tar_path = tmp / "b.tar.gz"
            make_zip(zip_path, {"x/theme/index.theme": "[Desktop Entry]\n"})
            make_tar_gz(tar_path, {"x/script/install.sh": "#!/bin/sh\nexit 0\n"})
            extract_archive(zip_path, tmp / "out-zip")
            extract_archive(tar_path, tmp / "out-tar")
            self.assertTrue((tmp / "out-zip" / "x" / "theme" / "index.theme").exists())
            self.assertTrue((tmp / "out-tar" / "x" / "script" / "install.sh").exists())


class WallpaperTests(unittest.TestCase):
    @staticmethod
    def _url_family(fam_id="wallpaper-x") -> dict:
        return {
            "id": fam_id, "name": "X Wallpaper", "kind": "wallpaper",
            "author": "t", "license": "MIT",
            "source": {"type": "url", "url": "https://example.invalid/wall.png",
                        "filename": "wall.png"},
            "strategy": "asset",
        }

    def test_wallpaper_installs_and_uninstalls(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            forge = Forge(base / "themes", base / "icons", base / "cache")
            with mock.patch("themeforge.installer._download",
                            side_effect=fake_download):
                info = forge.install_family(self._url_family())
            self.assertEqual(info["wallpapers"], ["wall.png"])
            self.assertTrue((forge.backgrounds_dir / "wall.png").exists())
            removed = forge.remove_family("wallpaper-x")
            self.assertEqual(removed, [str(forge.backgrounds_dir / "wall.png")])
            self.assertFalse((forge.backgrounds_dir / "wall.png").exists())

    def test_backgrounds_dir_defaults_next_to_themes(self):
        forge = Forge(Path("/t/themes"), Path("/t/icons"), Path("/t/cache"))
        self.assertEqual(forge.backgrounds_dir, Path("/t/backgrounds"))

    def test_apply_look_wallpaper_dry_run_plans_uri(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            forge = Forge(base / "themes", base / "icons", base / "cache")
            forge.record("wallpaper-x", version="1", themes=[], shell=[], icons=[],
                         wallpapers=["wall.png"])
            forge.backgrounds_dir.mkdir(parents=True, exist_ok=True)
            (forge.backgrounds_dir / "wall.png").write_bytes(b"PNG")
            bundle = {"families": [self._url_family()], "looks": []}
            look = {"id": "lk", "name": "L", "gtk_theme": None,
                    "icon_theme": None, "wallpaper": "wallpaper-x"}
            res = apply_mod.apply_look(look, forge, bundle, dry_run=True)
            self.assertTrue(any("picture-uri → wall.png" in c for c in res.changed))

    def test_wallpaper_rejects_non_image_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            forge = Forge(base / "themes", base / "icons", base / "cache")
            def html_download(url: str, dest: Path) -> Path:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(b"<html>404 not found</html>")
                return dest

            with mock.patch("themeforge.installer._download", side_effect=html_download):
                with self.assertRaises(InstallError):
                    forge.install_family(self._url_family())
            self.assertFalse((forge.backgrounds_dir / "wall.png").exists())

    def test_bundle_rejects_url_source_on_non_wallpaper(self):
        bad = self._url_family("bad-gtk")
        bad["kind"] = "gtk"
        with self.assertRaises(bundle_mod.BundleError):
            bundle_mod.validate_bundle({"families": [bad], "looks": []})

    def test_bundle_rejects_unknown_source_type(self):
        fam = bundle_mod.families(bundle_mod.load_bundle())[0].copy()
        fam["source"] = {"type": "ftp", "url": "x"}
        with self.assertRaises(bundle_mod.BundleError):
            bundle_mod.validate_bundle({"families": [fam], "looks": []})

    def test_apply_look_wallpaper_missing_from_bundle_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            forge = Forge(base / "themes", base / "icons", base / "cache")
            bundle = {"families": [], "looks": []}
            look = {"id": "lk", "name": "L", "gtk_theme": None,
                    "icon_theme": None, "wallpaper": "does-not-exist"}
            res = apply_mod.apply_look(look, forge, bundle, dry_run=True)
            self.assertTrue(any("does-not-exist" in s for s in res.skipped))


class ForgeTests(unittest.TestCase):
    def _forge(self, tmp: str) -> Forge:
        base = Path(tmp)
        return Forge(base / "themes", base / "icons", base / "cache")

    def _fake_asset_family(self, family_id="fake-gtk", kind="gtk") -> dict:
        return {
            "id": family_id, "name": "Fake", "kind": kind,
            "author": "t", "license": "MIT",
            "source": {"type": "github", "owner": "fake", "repo": "fake-repo"},
            "strategy": "asset",
            "asset_pattern": "fake-*.zip",
        }

    def test_asset_strategy_installs_and_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            forge = self._forge(tmp)
            base = Path(tmp)
            fixture = base / "fixture" / "fake-asset.zip"
            make_zip(fixture, {
                "fake-asset/themes/Fake-Dark/index.theme": "[Desktop Entry]\nName=Fake-Dark\n",
                "fake-asset/themes/Fake-Dark/gtk-3.0/.keep": "",
                "fake-asset/icons/Fake-Icons/index.theme": "[Icon Theme]\nName=Fake-Icons\n",
            })

            release = {"tag_name": "v1", "assets": [
                {"name": "fake-asset.zip", "browser_download_url": "https://example.invalid/fake-asset.zip"}
            ]}
            with mock.patch("themeforge.installer.latest_release", return_value=release), \
                 mock.patch("themeforge.installer._download",
                            side_effect=lambda url, dest: shutil_copy(fixture, dest)):
                info = forge.install_family(self._fake_asset_family())
            self.assertEqual(info["themes"], ["Fake-Dark"])
            self.assertEqual(info["icons"], ["Fake-Icons"])
            self.assertTrue((forge.themes_dir / "Fake-Dark" / "gtk-3.0").is_dir())
            self.assertTrue((forge.icons_dir / "Fake-Icons" / "index.theme").exists())
            # manifest round-trips
            forge2 = Forge(forge.themes_dir, forge.icons_dir, forge.cache_dir)
            self.assertEqual(forge2.installed("fake-gtk")["version"], "v1")

    def test_script_strategy_runs_install_sh(self):
        with tempfile.TemporaryDirectory() as tmp:
            forge = self._forge(tmp)
            base = Path(tmp)
            fixture = base / "fixture" / "src.tar.gz"
            script = (
                "#!/bin/sh\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  case \"$1\" in -d) shift; dest=\"$1\";; -i) shift; icons=\"$1\";; esac\n"
                "  shift\n"
                "done\n"
                "mkdir -p \"$dest/Fake-GTK-Dark/gtk-3.0\"\n"
                "echo '[Desktop Entry]' > \"$dest/Fake-GTK-Dark/index.theme\"\n"
                "echo 'Name=Fake-GTK-Dark' >> \"$dest/Fake-GTK-Dark/index.theme\"\n"
                "mkdir -p \"$icons/Fake-Icons\"\n"
                "echo '[Icon Theme]' > \"$icons/Fake-Icons/index.theme\"\n"
            )
            make_tar_gz(fixture, {"fake-src/install.sh": script})
            family = {
                "id": "fake-script", "name": "Fake Script", "kind": "gtk",
                "author": "t", "license": "MIT",
                "source": {"type": "github", "owner": "fake", "repo": "fake-repo"},
                "strategy": "script",
                "script_args": ["-d", "{themes_dir}", "-i", "{icons_dir}"],
            }
            release = {"tag_name": "v2"}
            with mock.patch("themeforge.installer.latest_release", return_value=release), \
                 mock.patch("themeforge.installer._download",
                            side_effect=lambda url, dest: shutil_copy(fixture, dest)):
                info = forge.install_family(family)
            self.assertEqual(info["themes"], ["Fake-GTK-Dark"])
            self.assertEqual(info["icons"], ["Fake-Icons"])
            self.assertTrue((forge.themes_dir / "Fake-GTK-Dark" / "index.theme").exists())

    def test_install_failure_raises_and_removal_cleans_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            forge = self._forge(tmp)
            base = Path(tmp)
            fixture = base / "fixture" / "src.tar.gz"
            make_tar_gz(fixture, {"fake-src/install.sh": "#!/bin/sh\nexit 3\n"})
            family = {
                "id": "bad-script", "name": "Bad", "kind": "gtk",
                "author": "t", "license": "MIT",
                "source": {"type": "github", "owner": "fake", "repo": "fake-repo"},
                "strategy": "script", "script_args": [],
            }
            release = {"tag_name": "v1"}
            with mock.patch("themeforge.installer.latest_release", return_value=release), \
                 mock.patch("themeforge.installer._download",
                            side_effect=lambda url, dest: shutil_copy(fixture, dest)):
                with self.assertRaises(InstallError):
                    forge.install_family(family)
            # removal of a recorded family deletes its dirs
            forge.record("gone", version="1", themes=["Gone-Dark"], shell=[], icons=["Gone-Icons"])
            (forge.themes_dir / "Gone-Dark" / "gtk-3.0").mkdir(parents=True)
            (forge.icons_dir / "Gone-Icons").mkdir(parents=True)
            removed = forge.remove_family("gone")
            self.assertEqual(len(removed), 2)
            self.assertFalse((forge.themes_dir / "Gone-Dark").exists())


def shutil_copy(src: Path, dest: Path) -> Path:
    import shutil
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return dest


def fake_download(url: str, dest: Path) -> Path:
    """Mock _download: write placeholder PNG bytes, creating dirs like the real one."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)
    return dest


class ApplyTests(unittest.TestCase):
    def _setup(self, tmp: str):
        base = Path(tmp)
        forge = Forge(base / "themes", base / "icons", base / "cache")
        forge.record("fake-gtk", version="1", themes=["Fake-GTK-Dark"], shell=[], icons=[])
        forge.record("fake-shell", version="1", themes=[], shell=["Fake-Shell"], icons=[])
        forge.record("fake-icons", version="1", themes=[], shell=[], icons=["Fake-Icons"])
        bundle = {
            "families": [
                self._fam("fake-gtk", "gtk", "asset"),
                self._fam("fake-shell", "shell", "asset"),
                self._fam("fake-icons", "icons", "asset"),
            ],
            "looks": [],
        }
        return forge, bundle

    @staticmethod
    def _fam(fam_id: str, kind: str, strategy: str) -> dict:
        return {
            "id": fam_id, "name": fam_id, "kind": kind, "author": "t",
            "license": "MIT", "source": {"type": "github", "owner": "o", "repo": "r"},
            "strategy": strategy,
            "asset_pattern": "*.zip" if strategy == "asset" else None,
            "script_args": [] if strategy == "script" else None,
        }

    def test_apply_look_dry_run_plans_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            forge, bundle = self._setup(tmp)
            look = {"id": "lk", "name": "L", "gtk_theme": "fake-gtk",
                    "icon_theme": "fake-icons", "color_scheme": "prefer-dark"}
            res = apply_mod.apply_look(look, forge, bundle, dry_run=True)
            self.assertIn("gtk-theme → Fake-GTK-Dark", res.changed)
            self.assertIn("icon-theme → Fake-Icons", res.changed)
            self.assertIn("color-scheme → prefer-dark", res.changed)
            self.assertFalse(res.logout_needed)

    def test_apply_shell_requires_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            forge, bundle = self._setup(tmp)
            look = {"id": "lk", "name": "L", "gtk_theme": "fake-gtk",
                    "shell_theme": "fake-shell", "icon_theme": "fake-icons"}
            with mock.patch("themeforge.apply._run",
                            side_effect=lambda cmd: subprocess.CompletedProcess(
                                cmd, 0, stdout="", stderr="")):
                res = apply_mod.apply_look(look, forge, bundle, dry_run=True)
            self.assertTrue(any("shell theme" in s for s in res.skipped))

    def test_apply_shell_with_extension_enabled_sets_logout_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            forge, bundle = self._setup(tmp)
            look = {"id": "lk", "name": "L", "shell_theme": "fake-shell"}
            ext_id = apply_mod.USER_THEME_EXTENSION_ID

            def fake_run(cmd):
                if cmd == ["gnome-extensions", "list"]:
                    return subprocess.CompletedProcess(cmd, 0, stdout=f"{ext_id}\n", stderr="")
                if cmd == ["gnome-extensions", "list", "--enabled"]:
                    return subprocess.CompletedProcess(cmd, 0, stdout=f"{ext_id}\n", stderr="")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with mock.patch("themeforge.apply._run", side_effect=fake_run):
                res = apply_mod.apply_look(look, forge, bundle, dry_run=True)
            self.assertTrue(any("shell theme → Fake-Shell" in c for c in res.changed))
            self.assertTrue(res.logout_needed)

    def test_apply_accent_unsupported_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            forge, bundle = self._setup(tmp)
            look = {"id": "lk", "name": "L", "gtk_theme": "fake-gtk",
                    "icon_theme": "fake-icons", "accent": "blue"}

            def fake_run(cmd):
                if cmd[:2] == ["gsettings", "set"] and cmd[-1] == "blue":
                    return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="err")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with mock.patch("themeforge.apply._run", side_effect=fake_run):
                res = apply_mod.apply_look(look, forge, bundle, dry_run=False)
            self.assertTrue(any("accent-color" in s for s in res.skipped))
            self.assertIn("gtk-theme → Fake-GTK-Dark", res.changed)

    def test_dry_run_never_installs(self):
        with tempfile.TemporaryDirectory() as tmp:
            forge, bundle = self._setup(tmp)
            # uninstalled family: install_family would hit the network
            bundle["families"].append(self._fam("never-installed", "gtk", "asset"))
            look = {"id": "lk", "name": "L", "gtk_theme": "never-installed",
                    "icon_theme": "fake-icons"}
            with mock.patch.object(forge, "install_family", side_effect=AssertionError("dry-run must not install")):
                res = apply_mod.apply_look(look, forge, bundle, dry_run=True)
            self.assertTrue(any("would install first" in c for c in res.changed))
            self.assertTrue(any("icon-theme → Fake-Icons" in c for c in res.changed))

    def test_reset_uses_distro_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            forge, bundle = self._setup(tmp)
            res = apply_mod.reset(forge, bundle, distro_mod.Distro(id="ubuntu"), dry_run=True)
            self.assertIn("gtk-theme → Yaru", res.changed)
            res = apply_mod.reset(forge, bundle, distro_mod.Distro(id="arch"), dry_run=True)
            self.assertIn("gtk-theme → Adwaita", res.changed)

    def test_extension_state_detection(self):
        ext_id = apply_mod.USER_THEME_EXTENSION_ID

        def fake_run(cmd):
            stdout = f"{ext_id}\n" if cmd == ["gnome-extensions", "list"] else ""
            return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr="")

        with mock.patch("themeforge.apply._run", side_effect=fake_run):
            usable, state = apply_mod.user_themes_extension_state()
        self.assertFalse(usable)  # installed but not enabled is not usable
        self.assertEqual(state, "installed")


@unittest.skipUnless(NET, "network tests: set THEMEFORGE_NET_TESTS=1")
class LiveTests(unittest.TestCase):
    def test_live_asset_patterns_match_releases(self):
        data = bundle_mod.load_bundle()
        for fam in bundle_mod.families(data):
            if fam["strategy"] != "asset" or fam["source"].get("type") != "github":
                continue
            src = fam["source"]
            with self.subTest(fam=fam["id"]):
                rel = latest_release(src["owner"], src["repo"])
                names = [a.get("name", "") for a in rel.get("assets", [])]
                self.assertTrue(
                    any(fnmatch.fnmatch(n, fam["asset_pattern"]) for n in names),
                    f"{fam['id']}: no asset matching {fam['asset_pattern']} in {names}",
                )

    def test_live_full_install_of_catppuccin(self):
        import tempfile
        from themeforge import bundle as bundle_mod
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            forge = Forge(base / "themes", base / "icons", base / "cache")
            fam = bundle_mod.family(bundle_mod.load_bundle(), "catppuccin-mocha")
            info = forge.install_family(fam, force=True)
            self.assertTrue(info["themes"], "expected installed GTK theme dirs")
            self.assertTrue((forge.themes_dir / info["themes"][0]).is_dir())


if __name__ == "__main__":
    unittest.main()

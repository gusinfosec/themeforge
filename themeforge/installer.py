"""Download, extract and install theme/icon families into user directories.

Two install strategies are supported (declared per family in bundle.json):

* ``asset``  — download a ready-made release asset (zip / tar) from GitHub
               and copy the theme/icon directories it contains.
* ``script`` — download the source tarball of a release and run the project's
               ``install.sh`` with explicit user-level destination dirs. Some
               scripts expect a destination via an environment variable (e.g.
               Papirus' ``DESTDIR``) — declare those per family with
               ``script_env`` in the bundle.

Nothing ever touches system directories or requires root.
"""
from __future__ import annotations

import fnmatch
import json
import os
import shutil
import subprocess
import tarfile
import threading
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

GITHUB_API = "https://api.github.com"
GITHUB_CODELOAD = "https://codeload.github.com"
USER_AGENT = "themeforge/0.1"

MANIFEST_NAME = "installed.json"


class InstallError(RuntimeError):
    """Raised when a family cannot be fetched or installed."""


# ------------------------------------------------------------------- paths

def default_dirs() -> tuple[Path, Path, Path, Path]:
    """(themes_dir, icons_dir, cache_dir, backgrounds_dir), honouring env overrides."""
    home = Path(os.environ.get("THEMEFORGE_HOME", Path.home()))
    xdg_data = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    xdg_cache = Path(os.environ.get("XDG_CACHE_HOME", home / ".cache"))
    return (
        xdg_data / "themes",
        xdg_data / "icons",
        xdg_cache / "themeforge",
        xdg_data / "backgrounds",
    )


def build_forge(themes_dir: Path | None = None, icons_dir: Path | None = None,
                cache_dir: Path | None = None,
                backgrounds_dir: Path | None = None) -> "Forge":
    themes, icons, cache, backgrounds = default_dirs()
    return Forge(
        themes_dir=themes_dir or themes,
        icons_dir=icons_dir or icons,
        cache_dir=cache_dir or cache,
        backgrounds_dir=backgrounds_dir or backgrounds,
    )


# -------------------------------------------------------------------- HTTP

def _http_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise InstallError(f"HTTP {exc.code} from {url}") from exc
    except urllib.error.URLError as exc:
        raise InstallError(f"network error fetching {url}: {exc.reason}") from exc


def _download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as fh:
            shutil.copyfileobj(resp, fh)
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise InstallError(f"failed to download {url}: {exc}") from exc
    return dest


def latest_release(owner: str, repo: str) -> dict:
    return _http_json(f"{GITHUB_API}/repos/{owner}/{repo}/releases/latest")


def _source_tarball_url(owner: str, repo: str, tag: str | None) -> str:
    ref = f"refs/tags/{tag}" if tag else "refs/heads/main"
    return f"{GITHUB_CODELOAD}/{owner}/{repo}/tar.gz/{ref}"


# ---------------------------------------------------------------- archives

def extract_archive(path: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if path.name.endswith(".zip"):
        with zipfile.ZipFile(path) as zf:
            _safe_extract_zip(zf, dest)
    else:
        with tarfile.open(path, "r:*") as tf:
            tf.extractall(dest, filter="data")


def _safe_extract_zip(zf: zipfile.ZipFile, dest: Path) -> None:
    """Extract a zip guarding against zip-slip (``../`` path traversal)."""
    dest = dest.resolve()
    for member in zf.infolist():
        target = (dest / member.filename).resolve()
        if not target.is_relative_to(dest):
            raise InstallError(f"unsafe path in archive member: {member.filename}")
    zf.extractall(dest)


def _single_top_dir(root: Path) -> Path:
    children = [p for p in root.iterdir() if p.is_dir()]
    return children[0] if len(children) == 1 else root


def _looks_like_image(path: Path) -> bool:
    """Cheap magic-byte sniff so a failed/HTML download never becomes a wallpaper."""
    try:
        with path.open("rb") as fh:
            head = fh.read(12)
    except OSError:
        return False
    return head.startswith(b"\x89PNG") or head.startswith(b"\xff\xd8") or head.startswith(b"GIF87a") \
        or head.startswith(b"GIF89a")


def _dir_names(base: Path) -> set[str]:
    return {p.name for p in base.iterdir() if p.is_dir()} if base.exists() else set()


# --------------------------------------------------------------- discovery

def discover_themes(root: Path) -> dict[str, list[Path]]:
    """Find dirs containing an ``index.theme`` and classify them.

    Icons: ``index.theme`` contains ``[Icon Theme]``. Shell themes contain a
    ``gnome-shell/`` subdir. GTK themes contain ``gtk-3.0``/``gtk-4.0`` (or an
    ``X-GNOME-Metatheme`` entry). A dir can be both GTK and Shell (common).
    """
    found: dict[str, list[Path]] = {"gtk": [], "shell": [], "icons": [], "cursor": []}
    for index in root.rglob("index.theme"):
        d = index.parent
        try:
            text = index.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "[Icon Theme]" in text:
            found["icons"].append(d)
            continue
        is_gtk = (d / "gtk-3.0").is_dir() or (d / "gtk-4.0").is_dir()
        is_shell = (d / "gnome-shell").is_dir()
        if is_gtk or (not is_shell and "[Desktop Entry]" in text and "X-GNOME-Metatheme" in text):
            found["gtk"].append(d)
        if is_shell:
            found["shell"].append(d)
    return found


def _remove_target(target: Path) -> None:
    """Delete a previously-installed dir/file, tolerating symlinks."""
    if target.is_symlink():
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()


def install_dirs(dirs: list[Path], base: Path) -> list[str]:
    """Copy theme dirs into ``base``; returns the installed directory names."""
    base.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    for src in sorted(dirs, key=lambda p: p.name):
        name = src.name
        target = base / name
        _remove_target(target)
        shutil.copytree(src, target)
        installed.append(name)
    return installed


def _find_install_script(root: Path) -> Path:
    for candidate in (root / "install.sh", _single_top_dir(root) / "install.sh"):
        if candidate.exists():
            return candidate
    raise InstallError("no install.sh found in source tarball")


def _family_cache_dir(cache_dir: Path, family_id: str) -> Path:
    return cache_dir / family_id.replace("/", "_")


# -------------------------------------------------------------------- forge

@dataclass
class Forge:
    """Installs/manages theme families inside user-level directories."""

    themes_dir: Path
    icons_dir: Path
    cache_dir: Path
    backgrounds_dir: Path | None = None
    _manifest: dict = field(default_factory=dict, init=False)
    _lock: "threading.RLock" = field(default_factory=threading.RLock, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.backgrounds_dir is None:
            self.backgrounds_dir = self.themes_dir.parent / "backgrounds"
        self.manifest_path = self.cache_dir / MANIFEST_NAME
        if self.manifest_path.exists():
            try:
                self._manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self._manifest = {}

    # -- manifest -------------------------------------------------------

    def _save_manifest(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(self._manifest, indent=2), encoding="utf-8")

    def installed(self, family_id: str) -> dict | None:
        return self._manifest.get(family_id)

    def installed_ids(self) -> list[str]:
        return list(self._manifest.keys())

    def record(self, family_id: str, *, version: str, name: str = "",
               themes: list[str], shell: list[str], icons: list[str],
               wallpapers: list[str] | None = None) -> dict:
        with self._lock:
            self._manifest[family_id] = {
                "name": name or family_id,
                "version": version,
                "themes": themes,
                "shell": shell,
                "icons": icons,
                "wallpapers": wallpapers or [],
            }
            self._save_manifest()
            return self._manifest[family_id]

    # -- install --------------------------------------------------------

    def install_family(self, fam: dict, *, force: bool = False) -> dict:
        """Install (or report already-installed) a family from the bundle."""
        with self._lock:
            family_id = fam["id"]
            if not force and self.installed(family_id):
                return self.installed(family_id)
            if fam["kind"] == "wallpaper":
                result = self._install_wallpaper(fam)
            elif fam["strategy"] == "asset":
                result = self._install_from_asset(fam)
            else:
                result = self._install_from_script(fam)
            return self.record(
                family_id,
                version=result.get("version", "unknown"),
                name=fam["name"],
                themes=result.get("themes", []),
                shell=result.get("shell", []),
                icons=result.get("icons", []),
                wallpapers=result.get("wallpapers", []),
            )

    def _install_wallpaper(self, fam: dict) -> dict:
        """Download a single wallpaper image into the user backgrounds dir."""
        src = fam["source"]
        url = src.get("url")
        if not url:
            raise InstallError(f"wallpaper family {fam['id']} needs source.url")
        filename = Path(src.get("filename") or Path(url).name).name
        workdir = _family_cache_dir(self.cache_dir, fam["id"])
        cached = workdir / filename
        if not cached.exists():
            _download(url, cached)
        if not _looks_like_image(cached):
            raise InstallError(f"downloaded wallpaper for {fam['id']} is not a PNG/JPEG")
        self.backgrounds_dir.mkdir(parents=True, exist_ok=True)
        target = self.backgrounds_dir / filename
        _remove_target(target)
        shutil.copy2(cached, target)
        return {"version": "latest", "wallpapers": [filename]}

    def _install_from_asset(self, fam: dict) -> dict:
        src = fam["source"]
        rel = latest_release(src["owner"], src["repo"])
        tag = rel.get("tag_name", "unknown")
        matches = [a for a in rel.get("assets", [])
                   if fnmatch.fnmatch(a.get("name", ""), fam["asset_pattern"])]
        if not matches:
            raise InstallError(
                f"no asset matching '{fam['asset_pattern']}' in "
                f"{src['owner']}/{src['repo']} release {tag}"
            )
        asset = matches[0]
        asset_name = Path(asset["name"]).name  # never trust upstream names for paths
        workdir = _family_cache_dir(self.cache_dir, fam["id"])
        archive = workdir / asset_name
        if not archive.exists():
            _download(asset["browser_download_url"], archive)
        extracted = workdir / "extracted"
        extract_archive(archive, extracted)
        found = discover_themes(_single_top_dir(extracted))
        return {
            "version": tag,
            "themes": install_dirs(found["gtk"], self.themes_dir),
            "shell": install_dirs(found["shell"], self.themes_dir),
            "icons": install_dirs(found["icons"], self.icons_dir),
        }

    def _install_from_script(self, fam: dict) -> dict:
        src = fam["source"]
        tag = None
        try:
            tag = latest_release(src["owner"], src["repo"]).get("tag_name")
        except InstallError:
            pass  # no published release — fall back to the default-branch tarball
        workdir = _family_cache_dir(self.cache_dir, fam["id"])
        tarball = workdir / "src.tar.gz"
        if not tarball.exists():
            _download(_source_tarball_url(src["owner"], src["repo"], tag), tarball)
        src_dir = workdir / "src"
        extract_archive(tarball, src_dir)
        script = _find_install_script(src_dir)
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        before = (_dir_names(self.themes_dir), _dir_names(self.icons_dir))
        args = [arg.format(themes_dir=self.themes_dir, icons_dir=self.icons_dir)
                for arg in fam.get("script_args", [])]
        home = str(Path(os.environ.get("THEMEFORGE_HOME", Path.home())))
        env = {**os.environ, "HOME": home}
        for key, value in (fam.get("script_env") or {}).items():
            env[key] = value.format(themes_dir=self.themes_dir,
                                    icons_dir=self.icons_dir)
        proc = subprocess.run(
            [str(script), *args],
            cwd=script.parent,
            capture_output=True,
            text=True,
            timeout=600,
            env=env,
        )
        if proc.returncode != 0:
            tail = (proc.stdout + proc.stderr)[-2000:]
            raise InstallError(f"install.sh failed for {fam['id']}:\n{tail}")
        themes_after, icons_after = _dir_names(self.themes_dir), _dir_names(self.icons_dir)
        new_themes = sorted(themes_after - before[0])
        new_icons = sorted(icons_after - before[1])
        if not new_themes and not new_icons:
            # force-reinstall: dirs already exist, so fall back to name matching
            needle = fam["id"].lower().replace("-", " ")
            new_themes = sorted(n for n in themes_after if needle in n.lower())
            new_icons = sorted(n for n in icons_after if needle in n.lower())
        return {
            "version": tag or "main",
            "themes": new_themes,
            "shell": [],
            "icons": new_icons,
        }

    # -- uninstall ------------------------------------------------------

    def remove_family(self, family_id: str) -> list[str]:
        """Delete the dirs a family installed; returns removed paths."""
        with self._lock:
            info = self._manifest.pop(family_id, None)
            removed: list[str] = []
            if info:
                for kind in ("themes", "shell"):
                    for name in info.get(kind, []):
                        target = self.themes_dir / name
                        if target.is_dir() or target.is_symlink():
                            _remove_target(target)
                            removed.append(str(target))
                for name in info.get("icons", []):
                    target = self.icons_dir / name
                    if target.is_dir() or target.is_symlink():
                        _remove_target(target)
                        removed.append(str(target))
                for name in info.get("wallpapers", []):
                    target = self.backgrounds_dir / name
                    if target.is_file() or target.is_symlink():
                        _remove_target(target)
                        removed.append(str(target))
                self._save_manifest()
            return removed

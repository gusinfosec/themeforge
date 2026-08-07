"""Loading and validation of the bundled theme/icon catalog (data/bundle.json)."""
from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

BUNDLE_PATH = resources.files("themeforge") / "data" / "bundle.json"

REQUIRED_FAMILY_FIELDS = ("id", "name", "kind", "strategy", "author", "license", "source")
REQUIRED_LOOK_FIELDS = ("id", "name", "gtk_theme", "icon_theme")


class BundleError(RuntimeError):
    pass


def load_bundle(path: Path | None = None) -> dict:
    if path is None:
        path = Path(str(BUNDLE_PATH))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BundleError(f"Failed to read bundle {path}: {exc}") from exc
    validate_bundle(data)
    return data


def validate_bundle(data: dict) -> None:
    families = data.get("families")
    if not isinstance(families, list) or not families:
        raise BundleError("bundle must contain a non-empty 'families' list")
    ids = [f.get("id") for f in families]
    if len(ids) != len(set(ids)):
        raise BundleError("family ids must be unique")
    for fam in families:
        missing = [k for k in REQUIRED_FAMILY_FIELDS if k not in fam]
        if missing:
            raise BundleError(f"family {fam.get('id', '?')} missing fields: {missing}")
        if fam["kind"] not in ("gtk", "shell", "icons", "cursor", "wallpaper"):
            raise BundleError(f"family {fam['id']} has invalid kind {fam['kind']}")
        if fam["strategy"] not in ("asset", "script"):
            raise BundleError(f"family {fam['id']} has invalid strategy {fam['strategy']}")
        if fam["strategy"] == "asset" and fam.get("source", {}).get("type") != "url" \
                and not fam.get("asset_pattern"):
            raise BundleError(f"asset family {fam['id']} needs asset_pattern (or source.type 'url')")
        if fam["strategy"] == "script" and not (fam.get("script_args") or fam.get("script_env")):
            raise BundleError(f"script family {fam['id']} needs script_args or script_env")
        env = fam.get("script_env")
        if env is not None and not isinstance(env, dict):
            raise BundleError(f"family {fam['id']} has invalid script_env (must be an object)")
        src = fam.get("source", {})
        if src.get("type") not in ("github", "url"):
            raise BundleError(f"family {fam['id']} has unsupported source.type {src.get('type')!r}")
        if src.get("type") == "github" and not (src.get("owner") and src.get("repo")):
            raise BundleError(f"family {fam['id']} needs source.owner/repo")
        if src.get("type") == "url":
            if not src.get("url"):
                raise BundleError(f"family {fam['id']} needs source.url")
            if fam["kind"] != "wallpaper":
                raise BundleError(f"url-source family {fam['id']} must be kind 'wallpaper'")
    for look in looks(data):
        missing = [k for k in REQUIRED_LOOK_FIELDS if k not in look]
        if missing:
            raise BundleError(f"look {look.get('id', '?')} missing fields: {missing}")


def families(data: dict) -> list[dict]:
    return data["families"]


def looks(data: dict) -> list[dict]:
    return data.get("looks", [])


def family(data: dict, fam_id: str) -> dict:
    for fam in families(data):
        if fam["id"] == fam_id:
            return fam
    raise KeyError(f"unknown family: {fam_id}")


def look(data: dict, look_id: str) -> dict:
    for lk in looks(data):
        if lk["id"] == look_id:
            return lk
    raise KeyError(f"unknown look: {look_id}")

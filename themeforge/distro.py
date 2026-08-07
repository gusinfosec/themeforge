"""Distro detection (Ubuntu / Fedora / Arch) and distro-specific defaults."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

OS_RELEASE = Path("/etc/os-release")


@dataclass(frozen=True)
class Distro:
    id: str
    id_like: str = ""
    version_id: str = ""
    pretty_name: str = ""

    @property
    def is_ubuntu(self) -> bool:
        return self.id == "ubuntu" or "ubuntu" in self.id_like

    @property
    def is_fedora(self) -> bool:
        return self.id == "fedora" or "fedora" in self.id_like

    @property
    def is_arch(self) -> bool:
        return self.id == "arch" or "arch" in self.id_like

    def reset_theme(self) -> str:
        """Default GTK theme name used by the 'reset to defaults' action."""
        return "Yaru" if self.is_ubuntu else "Adwaita"

    def reset_icon_theme(self) -> str:
        return "Yaru" if self.is_ubuntu else "Adwaita"

    def user_themes_extension_package(self) -> str:
        """Package that provides the GNOME User Themes extension."""
        if self.is_ubuntu:
            return "gnome-shell-extensions"
        if self.is_fedora:
            return "gnome-shell-extension-user-theme"
        return "gnome-shell-extension-user-theme (AUR)"


def parse_os_release(path: Path = OS_RELEASE) -> Distro:
    fields: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return Distro(id="unknown")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        fields[key.strip()] = value.strip().strip('"')
    return Distro(
        id=fields.get("ID", "unknown"),
        id_like=fields.get("ID_LIKE", ""),
        version_id=fields.get("VERSION_ID", ""),
        pretty_name=fields.get("PRETTY_NAME", ""),
    )


def detect() -> Distro:
    return parse_os_release()

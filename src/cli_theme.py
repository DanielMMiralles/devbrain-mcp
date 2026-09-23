"""
DevBrain CLI Theme & Configuration Manager (v1.0)
Temas visuales inspirados en Gentle-Shell, Gentle-PI y Cyberpunk con soporte de 'Modo Papa'.
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class ThemeColors:
    name: str
    primary: str
    secondary: str
    accent: str
    success: str
    warning: str
    danger: str
    text: str
    dim: str
    background: str

THEMES: dict[str, ThemeColors] = {
    "gentleman": ThemeColors(
        name="Gentleman-Dark",
        primary="magenta",
        secondary="cyan",
        accent="yellow",
        success="green",
        warning="bright_yellow",
        danger="bright_red",
        text="white",
        dim="bright_black",
        background="#0f172a"
    ),
    "cyberpunk": ThemeColors(
        name="Cyberpunk",
        primary="yellow",
        secondary="bright_cyan",
        accent="bright_magenta",
        success="bright_green",
        warning="yellow",
        danger="red",
        text="bright_white",
        dim="bright_black",
        background="#050505"
    ),
    "obsidian": ThemeColors(
        name="Obsidian-Dark",
        primary="bright_magenta",
        secondary="bright_blue",
        accent="cyan",
        success="green",
        warning="yellow",
        danger="red",
        text="white",
        dim="bright_black",
        background="#18181b"
    ),
    "monokai": ThemeColors(
        name="Monokai",
        primary="green",
        secondary="cyan",
        accent="bright_yellow",
        success="bright_green",
        warning="yellow",
        danger="red",
        text="bright_white",
        dim="bright_black",
        background="#272822"
    ),
    "papa": ThemeColors(
        name="Modo Papa (Minimal)",
        primary="white",
        secondary="bright_white",
        accent="white",
        success="white",
        warning="white",
        danger="white",
        text="white",
        dim="bright_black",
        background="default"
    )
}

def resolve_config_path() -> Path:
    base = Path(os.path.expanduser("~")) / ".devbrain"
    try:
        base.mkdir(parents=True, exist_ok=True)
        return base / "config.json"
    except Exception:
        fallback = Path("./.devbrain_cache").resolve()
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback / "config.json"

class ConfigManager:
    """Gestiona la persistencia de configuración del CLI de DevBrain."""

    DEFAULT_CONFIG = {
        "theme": "gentleman",
        "papa_mode": False,
        "refresh_rate_sec": 0.5,
        "show_thought_trace": True,
        "show_synaptic_cortex": True,
        "default_model": "gemini-3.8-flash"
    }

    def __init__(self, config_file: Path | None = None):
        self.config_file = config_file or resolve_config_path()
        self.config = self.load()

    def load(self) -> dict:
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text(encoding="utf-8"))
                merged = dict(self.DEFAULT_CONFIG)
                merged.update(data)
                return merged
            except Exception:
                pass
        return dict(self.DEFAULT_CONFIG)

    def save(self) -> None:
        try:
            self.config_file.write_text(json.dumps(self.config, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_theme(self) -> ThemeColors:
        if self.config.get("papa_mode", False):
            return THEMES["papa"]
        t_key = self.config.get("theme", "gentleman").lower()
        return THEMES.get(t_key, THEMES["gentleman"])

    def set_theme(self, theme_name: str) -> bool:
        t_key = theme_name.lower().replace("-dark", "").replace("modo-", "")
        if t_key in THEMES:
            self.config["theme"] = t_key
            self.save()
            return True
        return False

    def toggle_papa_mode(self) -> bool:
        current = self.config.get("papa_mode", False)
        self.config["papa_mode"] = not current
        self.save()
        return self.config["papa_mode"]

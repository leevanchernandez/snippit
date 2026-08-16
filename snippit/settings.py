"""Settings and configuration management for Snippit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    """Application user settings."""
    # Global hotkey string in pynput format (default: Win+Alt+S)
    hotkey: str = "<cmd>+<alt>+s"
    # Auto-dismiss timeout for post-capture toolbar in seconds (0 = disabled)
    toolbar_timeout_seconds: float = 6.0
    # Default save directory (None means standard Pictures / Screenshots folder or Desktop)
    save_directory: Optional[str] = None
    # Dark theme or system theme
    theme: str = "dark"
    # AI model to use for background removal (default: isnet-general-use)
    ai_model: str = "isnet-general-use"

    @classmethod
    def get_config_path(cls) -> Path:
        """Returns the platform-specific configuration file path."""
        config_dir = Path.home() / ".config" / "snippit"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "settings.json"

    @classmethod
    def load(cls) -> Settings:
        """Load settings from disk, falling back to defaults if not found or corrupted."""
        path = cls.get_config_path()
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        """Save settings to disk."""
        path = self.get_config_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
        except Exception:
            pass

"""Unit tests for Settings model and persistence."""

from pathlib import Path
from snippit.settings import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.hotkey == "<cmd>+<alt>+s"
    assert settings.toolbar_timeout_seconds == 6.0
    assert settings.theme == "dark"
    assert settings.ai_model == "isnet-general-use"


def test_settings_save_and_load(tmp_path, monkeypatch):
    custom_config_dir = tmp_path / "snippit"
    monkeypatch.setattr(Settings, "get_config_path", classmethod(lambda cls: custom_config_dir / "settings.json"))

    s1 = Settings(hotkey="<ctrl>+<shift>+x", toolbar_timeout_seconds=10.0)
    s1.save()

    assert (custom_config_dir / "settings.json").exists()

    s2 = Settings.load()
    assert s2.hotkey == "<ctrl>+<shift>+x"
    assert s2.toolbar_timeout_seconds == 10.0

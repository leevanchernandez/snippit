"""Integration tests for SnippitApp lifecycle and background removal flow."""

from unittest.mock import MagicMock, patch
import pytest
from PIL import Image
from PySide6.QtCore import QRect

from snippit.app import SnippitApp
from snippit.settings import Settings


def test_snippit_app_init_and_quit(qapp):
    settings = Settings(hotkey="<ctrl>+<alt>+z", toolbar_timeout_seconds=0)
    with patch("snippit.core.hotkey.HotkeyListener.start"), \
         patch("snippit.core.hotkey.HotkeyListener.stop"):
        app = SnippitApp(settings=settings)
        assert app is not None
        assert app.settings.hotkey == "<ctrl>+<alt>+z"
        app.quit()


def test_snippit_app_region_captured_and_remove_bg(qapp):
    settings = Settings(toolbar_timeout_seconds=0)
    with patch("snippit.core.hotkey.HotkeyListener.start"), \
         patch("snippit.core.hotkey.HotkeyListener.stop"):
        app = SnippitApp(settings=settings)

    img = Image.new("RGB", (100, 80), color=(255, 0, 0))
    rect = QRect(50, 50, 100, 80)
    mock_transparent = Image.new("RGBA", (100, 80), color=(255, 0, 0, 0))

    with patch("snippit.app.copy_image_to_clipboard") as mock_clipboard, \
         patch("snippit.processing.background_removal.is_model_downloaded", return_value=True), \
         patch("snippit.processing.background_removal.get_session", return_value=MagicMock()), \
         patch("snippit.processing.background_removal.remove_background", return_value=mock_transparent):

        # Simulate overlay region captured
        app._on_region_captured(img, rect)

        assert app._toolbar is not None
        assert mock_clipboard.call_count == 1  # Raw copy

        # Trigger Remove BG
        app._on_remove_bg_requested()
        assert app._bg_worker is not None
        app._bg_worker.wait(3000)
        qapp.processEvents()

        # Transparent copy should have been called
        assert mock_clipboard.call_count == 2
        assert app._toolbar.image == mock_transparent

    app.quit()

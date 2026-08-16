"""Unit tests for UI components (Theme, Toolbar, Overlay, Tray, Icons)."""

import pytest
from PIL import Image
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtWidgets import QApplication

from snippit.core.capture import CapturedScreen, ScreenGeometry
from snippit.resources.icons import create_action_icon_pixmap, create_app_icon, get_action_icon, get_icon
from snippit.ui.overlay import SelectionOverlay
from snippit.ui.theme import TOKENS, get_color, get_font, get_toolbar_stylesheet, get_tray_menu_stylesheet
from snippit.ui.toolbar import FloatingToolbar
from snippit.ui.tray import SystemTray


def test_theme_tokens_and_colors():
    assert "accent" in TOKENS
    assert "surface" in TOKENS
    assert "success" in TOKENS

    accent_color = get_color("accent")
    assert isinstance(accent_color, QColor)
    assert accent_color.isValid()

    font = get_font(size_pt=10)
    assert font is not None

    toolbar_qss = get_toolbar_stylesheet()
    assert "rgba(" in toolbar_qss
    assert "qlineargradient" not in toolbar_qss.lower()

    tray_qss = get_tray_menu_stylesheet()
    assert "QMenu" in tray_qss


def test_icons_generation(qapp):
    for state in ["idle", "capturing", "processing"]:
        pixmap = create_app_icon(size=64, state=state)
        assert not pixmap.isNull()
        assert pixmap.width() == 64
        assert pixmap.height() == 64

        icon = get_icon(state=state)
        assert not icon.isNull()

    for action_name in ["capture", "settings", "quit", "save", "remove_bg", "check", "close", "warning"]:
        action_pix = create_action_icon_pixmap(action_name, size=16)
        assert not action_pix.isNull()
        action_icon = get_action_icon(action_name)
        assert not action_icon.isNull()


def test_floating_toolbar_lifecycle(qapp):
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    anchor = QRect(100, 100, 200, 200)

    toolbar = FloatingToolbar(image=img, anchor_rect=anchor, timeout_seconds=0)
    assert toolbar is not None
    assert "Copied" in toolbar._status_label.text()

    # Test signals
    remove_bg_called = []
    toolbar.remove_bg_requested.connect(lambda: remove_bg_called.append(True))
    toolbar._on_remove_bg_clicked()
    assert len(remove_bg_called) == 1

    toolbar.close()


def test_system_tray_creation(qapp):
    tray = SystemTray(hotkey_display="Win+Alt+S")
    assert tray._tray_icon is not None
    assert tray._menu is not None
    actions = tray._menu.actions()
    assert len(actions) >= 3
    # Check that emojis are removed from actions
    for act in actions:
        if act.text():
            assert not any(emoji in act.text() for emoji in ["📸", "⚙️", "❌", "💾", "⚠️"])


def test_selection_overlay_selection(qapp):
    img = Image.new("RGB", (500, 400), color=(50, 50, 50))
    geom = ScreenGeometry(left=0, top=0, width=500, height=400)
    captured = CapturedScreen(image=img, geometry=geom)

    overlay = SelectionOverlay(captured)
    assert overlay.width() == 500
    assert overlay.height() == 400

    results = []
    overlay.captured.connect(lambda im, rect: results.append((im, rect)))

    # Simulate selection rect
    overlay._selection_rect = QRect(10, 10, 80, 80)
    overlay._finish_selection()

    assert len(results) == 1
    cropped_im, global_rect = results[0]
    assert cropped_im.size == (80, 80)
    assert global_rect == QRect(10, 10, 80, 80)

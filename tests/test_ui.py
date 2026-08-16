"""Unit tests for UI components (Toolbar, Overlay, Tray, Icons)."""

import pytest
from PIL import Image
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from snippit.core.capture import CapturedScreen, ScreenGeometry
from snippit.resources.icons import create_app_icon, get_icon
from snippit.ui.overlay import SelectionOverlay
from snippit.ui.toolbar import FloatingToolbar
from snippit.ui.tray import SystemTray



def test_icons_generation(qapp):
    for state in ["idle", "capturing", "processing"]:
        pixmap = create_app_icon(size=64, state=state)
        assert not pixmap.isNull()
        assert pixmap.width() == 64
        assert pixmap.height() == 64

        icon = get_icon(state=state)
        assert not icon.isNull()


def test_floating_toolbar_lifecycle(qapp):
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    anchor = QRect(100, 100, 200, 200)

    toolbar = FloatingToolbar(image=img, anchor_rect=anchor, timeout_seconds=0)
    assert toolbar is not None
    assert toolbar._status_label.text() == "✓ Copied"

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
    assert len(tray._menu.actions()) >= 3


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

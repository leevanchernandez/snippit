"""Floating post-capture action toolbar."""

from __future__ import annotations

import logging
from typing import Optional
from PIL import Image
from PySide6.QtCore import QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QGuiApplication, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from snippit.core.clipboard import copy_image_to_clipboard
from snippit.resources.icons import get_action_icon
from snippit.ui.theme import get_color, get_toolbar_stylesheet

logger = logging.getLogger(__name__)


class FloatingToolbar(QWidget):
    """
    Floating action toolbar that appears consistently at the top of the screen.
    Follows a native, restrained Windows utility aesthetic.
    """
    remove_bg_requested = Signal()
    save_requested = Signal()
    dismissed = Signal()

    def __init__(
        self,
        image: Image.Image,
        anchor_rect: QRect,
        timeout_seconds: float = 6.0,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._image = image
        self._anchor_rect = anchor_rect
        self._timeout_seconds = timeout_seconds

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._init_ui()
        self._init_timer()
        self._position_at_top()

        # Keyboard shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Outer container frame
        self._frame = QFrame(self)
        self._frame.setObjectName("toolbarFrame")
        self._frame.setStyleSheet(get_toolbar_stylesheet())

        # Drop shadow effect (restrained, professional depth)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 140))
        shadow.setOffset(0, 3)
        self._frame.setGraphicsEffect(shadow)

        frame_layout = QHBoxLayout(self._frame)
        frame_layout.setContentsMargins(10, 6, 10, 6)
        frame_layout.setSpacing(8)

        # Copied status badge (Checkmark glyph + Copied)
        self._status_label = QLabel("\uE73E Copied", self._frame)
        self._status_label.setObjectName("statusLabel")
        frame_layout.addWidget(self._status_label)

        # Primary Action: Remove BG (Solid Accent, No Gradient)
        self._btn_remove_bg = QPushButton("Remove BG", self._frame)
        self._btn_remove_bg.setObjectName("btnRemoveBg")
        self._btn_remove_bg.setIcon(get_action_icon("remove_bg", color=get_color("text_on_accent")))
        self._btn_remove_bg.setIconSize(QSize(14, 14))
        self._btn_remove_bg.setToolTip("Remove background using offline AI (Phase 2)")
        self._btn_remove_bg.clicked.connect(self._on_remove_bg_clicked)
        frame_layout.addWidget(self._btn_remove_bg)

        # Secondary Action: Save (Clean Neutral Control)
        self._btn_save = QPushButton("Save", self._frame)
        self._btn_save.setObjectName("btnSave")
        self._btn_save.setIcon(get_action_icon("save", color=get_color("text_primary")))
        self._btn_save.setIconSize(QSize(14, 14))
        self._btn_save.setToolTip("Save snippet to file (Ctrl+S)")
        self._btn_save.clicked.connect(self._on_save_clicked)
        frame_layout.addWidget(self._btn_save)

        # Ghost / Dismiss Action: Close
        self._btn_close = QPushButton("✕", self._frame)
        self._btn_close.setObjectName("btnClose")
        self._btn_close.setToolTip("Dismiss (Esc)")
        self._btn_close.clicked.connect(self.close)
        frame_layout.addWidget(self._btn_close)

        main_layout.addWidget(self._frame)

    def _init_timer(self):
        if self._timeout_seconds > 0:
            self._timer = QTimer(self)
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self.close)
            self._timer.start(int(self._timeout_seconds * 1000))
        else:
            self._timer = None

    def enterEvent(self, event):
        """Pause auto-dismiss timer on mouse hover."""
        if self._timer and self._timer.isActive():
            self._timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Resume auto-dismiss timer when mouse leaves."""
        if self._timer:
            self._timer.start(int(self._timeout_seconds * 1000))
        super().leaveEvent(event)

    def _position_at_top(self):
        """Positions the toolbar consistently at the top-center of the screen (Windows Snipping Tool style)."""
        self.adjustSize()
        tb_w = self.sizeHint().width()

        app = QGuiApplication.instance()
        screen = None
        if app and hasattr(app, "screenAt"):
            screen = app.screenAt(self._anchor_rect.center())

        if not screen:
            screen = self.screen() or (app.primaryScreen() if app else None)

        if screen:
            screen_geo = screen.geometry()
        else:
            screen_geo = QRect(0, 0, 1920, 1080)

        # Center horizontally at the top of the monitor
        x = screen_geo.left() + (screen_geo.width() - tb_w) // 2
        y = screen_geo.top() + 16

        self.move(x, y)

    def _on_remove_bg_clicked(self):
        self.remove_bg_requested.emit()

    def _on_save_clicked(self):
        self.save_requested.emit()
        self._prompt_save_file()

    def _prompt_save_file(self):
        """Opens native file dialog to save snippet."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Snippet",
            "snippet.png",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;All Files (*)",
        )
        if file_path:
            try:
                self._image.save(file_path)
                self.show_status("\uE73E Saved", duration_ms=2000)
            except Exception as e:
                logger.error(f"Failed to save image to {file_path}: {e}")
                self.show_status("\uE7BA Save failed", duration_ms=3000)

    def show_status(self, text: str, duration_ms: int = 2000):
        """Updates status text badge temporarily."""
        self._status_label.setText(text)
        if duration_ms > 0 and self._timer:
            self._timer.start(duration_ms)

    def closeEvent(self, event):
        self.dismissed.emit()
        super().closeEvent(event)

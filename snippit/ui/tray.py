"""System tray icon and context menu."""

from __future__ import annotations

import logging
from typing import Optional
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from snippit.resources.icons import get_action_icon, get_icon
from snippit.ui.theme import get_color, get_tray_menu_stylesheet

logger = logging.getLogger(__name__)


class SystemTray(QObject):
    """
    Manages the system tray icon, context menu, and desktop notifications.
    Follows a native, restrained Windows utility aesthetic.
    """
    capture_requested = Signal()
    settings_requested = Signal()
    quit_requested = Signal()

    def __init__(self, hotkey_display: str = "Win+Alt+S", parent: Optional[QObject] = None):
        super().__init__(parent)
        self._hotkey_display = hotkey_display
        self._tray_icon = QSystemTrayIcon(parent=parent)
        self._tray_icon.setIcon(get_icon("idle"))
        self._tray_icon.setToolTip(f"Snippit — Screen Snipping ({self._hotkey_display})")

        self._init_menu()
        self._tray_icon.activated.connect(self._on_tray_activated)

    def _init_menu(self):
        self._menu = QMenu()
        self._menu.setStyleSheet(get_tray_menu_stylesheet())

        # Capture action with vector icon
        capture_text = f"Capture Screen\t{self._hotkey_display}"
        self._act_capture = QAction(get_action_icon("capture", color=get_color("text_primary")), capture_text, self._menu)
        self._act_capture.triggered.connect(self.capture_requested.emit)
        self._menu.addAction(self._act_capture)

        self._menu.addSeparator()

        # Settings action with vector icon
        self._act_settings = QAction(get_action_icon("settings", color=get_color("text_primary")), "Settings...", self._menu)
        self._act_settings.triggered.connect(self.settings_requested.emit)
        self._menu.addAction(self._act_settings)

        self._menu.addSeparator()

        # Quit action with vector icon
        self._act_quit = QAction(get_action_icon("quit", color=get_color("text_primary")), "Quit Snippit", self._menu)
        self._act_quit.triggered.connect(self.quit_requested.emit)
        self._menu.addAction(self._act_quit)

        self._tray_icon.setContextMenu(self._menu)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.capture_requested.emit()

    def show(self):
        """Displays the tray icon."""
        self._tray_icon.show()

    def hide(self):
        """Hides the tray icon."""
        self._tray_icon.hide()

    def set_icon_state(self, state: str = "idle"):
        """Updates the tray icon visual state ('idle', 'capturing', 'processing')."""
        self._tray_icon.setIcon(get_icon(state))

    def show_message(self, title: str, message: str, msecs: int = 3000):
        """Shows a system tray balloon notification."""
        self._tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, msecs)

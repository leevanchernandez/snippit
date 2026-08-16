"""Main application controller for Snippit."""

from __future__ import annotations

import logging
import sys
from typing import Optional
from PIL import Image
from PySide6.QtCore import QObject, QRect, Qt
from PySide6.QtWidgets import QApplication

from snippit.core.capture import capture_virtual_screen
from snippit.core.clipboard import copy_image_to_clipboard
from snippit.core.hotkey import HotkeyListener
from snippit.processing.background_removal import BackgroundRemovalWorker
from snippit.resources.icons import get_icon
from snippit.settings import Settings
from snippit.ui.overlay import SelectionOverlay
from snippit.ui.toolbar import FloatingToolbar
from snippit.ui.tray import SystemTray

logger = logging.getLogger(__name__)


class SnippitApp(QObject):
    """
    Main application coordinator wiring together hotkey events, screen capture,
    selection overlay, clipboard copy, post-capture toolbar, and AI processing.
    """

    def __init__(self, settings: Optional[Settings] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.settings = settings or Settings.load()

        self._overlay: Optional[SelectionOverlay] = None
        self._toolbar: Optional[FloatingToolbar] = None
        self._bg_worker: Optional[BackgroundRemovalWorker] = None
        self._is_capturing = False

        # Initialize System Tray
        self._tray = SystemTray(hotkey_display=self._format_hotkey_display(self.settings.hotkey), parent=self)
        self._tray.capture_requested.connect(self.trigger_capture)
        self._tray.quit_requested.connect(self.quit)

        # Initialize Global Hotkey Listener
        self._hotkey_listener = HotkeyListener(hotkey_str=self.settings.hotkey, parent=self)
        self._hotkey_listener.activated.connect(self.trigger_capture)

    def _format_hotkey_display(self, hotkey_str: str) -> str:
        """Converts pynput syntax like '<cmd>+<alt>+s' to user-friendly 'Win+Alt+S'."""
        display = hotkey_str.replace("<cmd>", "Win").replace("<alt>", "Alt").replace("<ctrl>", "Ctrl").replace("<shift>", "Shift")
        return "+".join([part.capitalize() if len(part) > 1 else part.upper() for part in display.split("+")])

    def start(self):
        """Starts the application components and tray."""
        self._tray.show()
        self._hotkey_listener.start()
        logger.info("Snippit application running in system tray")

    def trigger_capture(self):
        """Freezes screen and presents the selection overlay."""
        if self._is_capturing or (self._overlay is not None and self._overlay.isVisible()):
            logger.debug("Capture already in progress, ignoring trigger")
            return

        self._is_capturing = True
        self._tray.set_icon_state("capturing")

        # Close any existing toolbar safely
        if self._toolbar is not None:
            try:
                self._toolbar.close()
            except Exception:
                pass
            self._toolbar = None

        try:
            # 1. Grab frozen virtual desktop snapshot
            captured_screen = capture_virtual_screen()

            # 2. Display fullscreen overlay
            self._overlay = SelectionOverlay(captured_screen)
            self._overlay.captured.connect(self._on_region_captured)
            self._overlay.cancelled.connect(self._on_capture_cancelled)
            self._overlay.show()
            self._overlay.raise_()
            self._overlay.activateWindow()

        except Exception as e:
            logger.error(f"Error during screen capture freeze: {e}", exc_info=True)
            self._is_capturing = False
            self._tray.set_icon_state("idle")

    def _on_region_captured(self, cropped_image: Image.Image, global_rect: QRect):
        """Handles successful selection from overlay."""
        self._is_capturing = False
        self._tray.set_icon_state("idle")
        self._overlay = None

        try:
            # Immediate clipboard copy (standard Snipping Tool flow)
            copy_image_to_clipboard(cropped_image)
            logger.info("Raw snippet copied to clipboard")

            # Show floating post-capture toolbar
            self._toolbar = FloatingToolbar(
                image=cropped_image,
                anchor_rect=global_rect,
                timeout_seconds=self.settings.toolbar_timeout_seconds,
            )
            self._toolbar.remove_bg_requested.connect(self._on_remove_bg_requested)
            self._toolbar.dismissed.connect(self._on_toolbar_dismissed)
            self._toolbar.show()
            self._toolbar.raise_()
            self._toolbar.activateWindow()

        except Exception as e:
            logger.error(f"Error processing captured region: {e}", exc_info=True)

    def _on_remove_bg_requested(self):
        """Triggers offline AI background removal in a background thread."""
        if self._bg_worker is not None and self._bg_worker.isRunning():
            logger.debug("Background removal worker already running")
            return

        if self._toolbar is None:
            return

        image_to_process = self._toolbar.image
        self._tray.set_icon_state("processing")
        self._toolbar.set_loading(True, "Initializing AI...")

        self._bg_worker = BackgroundRemovalWorker(
            image=image_to_process,
            model_name=self.settings.ai_model,
            parent=self,
        )
        self._bg_worker.status_changed.connect(self._on_bg_status_changed)
        self._bg_worker.finished.connect(self._on_bg_removed)
        self._bg_worker.error.connect(self._on_bg_remove_error)
        self._bg_worker.start()

    def _on_bg_status_changed(self, status_text: str):
        """Updates toolbar loading status during inference."""
        if self._toolbar is not None:
            self._toolbar.set_loading(True, status_text)

    def _on_bg_removed(self, transparent_image: Image.Image):
        """Handles successful background removal."""
        self._tray.set_icon_state("idle")
        self._bg_worker = None

        try:
            # Copy transparent PNG to clipboard
            copy_image_to_clipboard(transparent_image)
            logger.info("Background removed and transparent PNG copied to clipboard")

            # Update floating toolbar
            if self._toolbar is not None:
                self._toolbar.set_processed_image(transparent_image)

        except Exception as e:
            logger.error(f"Error handling background removed image: {e}", exc_info=True)
            if self._toolbar is not None:
                self._toolbar.set_error("Clipboard copy failed")

    def _on_bg_remove_error(self, error_msg: str):
        """Handles background removal failure."""
        self._tray.set_icon_state("idle")
        self._bg_worker = None
        logger.error(f"Background removal failed: {error_msg}")

        if self._toolbar is not None:
            self._toolbar.set_error("Background removal failed")

    def _on_toolbar_dismissed(self):
        """Reset toolbar reference when dismissed."""
        self._toolbar = None

    def _on_capture_cancelled(self):
        """Handles capture dismissal by user."""
        self._is_capturing = False
        self._tray.set_icon_state("idle")
        self._overlay = None
        logger.debug("Screen capture cancelled")

    def quit(self):
        """Gracefully shuts down Snippit."""
        logger.info("Shutting down Snippit...")
        self._hotkey_listener.stop()

        if self._bg_worker is not None and self._bg_worker.isRunning():
            self._bg_worker.cancel()
            self._bg_worker.wait(1000)
            self._bg_worker = None

        if self._overlay is not None:
            try:
                self._overlay.close()
            except Exception:
                pass
            self._overlay = None

        if self._toolbar is not None:
            try:
                self._toolbar.close()
            except Exception:
                pass
            self._toolbar = None

        self._tray.hide()

        app = QApplication.instance()
        if app:
            app.quit()

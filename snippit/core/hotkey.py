"""Global hotkey listener using pynput with Qt signal dispatching."""

from __future__ import annotations

import logging
from typing import Optional
from pynput import keyboard
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class HotkeyListener(QObject):
    """
    Listens for global system hotkeys in a background thread and emits
    Qt signals on the main thread.
    """
    activated = Signal()

    def __init__(self, hotkey_str: str = "<cmd>+<alt>+s", parent: Optional[QObject] = None):
        super().__init__(parent)
        self._hotkey_str = hotkey_str
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._is_running = False

    @property
    def hotkey_str(self) -> str:
        return self._hotkey_str

    @hotkey_str.setter
    def hotkey_str(self, value: str):
        was_running = self._is_running
        if was_running:
            self.stop()
        self._hotkey_str = value
        if was_running:
            self.start()

    def _on_hotkey_triggered(self):
        """Callback invoked by pynput on hotkey detection thread."""
        logger.debug(f"Hotkey '{self._hotkey_str}' triggered")
        # Emitting a Qt signal from another thread is thread-safe; Qt queues it to the receiver thread.
        self.activated.emit()

    def start(self) -> bool:
        """Starts the global hotkey listener thread."""
        if self._is_running:
            return True

        try:
            hotkeys_map = {
                self._hotkey_str: self._on_hotkey_triggered
            }
            self._listener = keyboard.GlobalHotKeys(hotkeys_map)
            self._listener.daemon = True
            self._listener.start()
            self._is_running = True
            logger.info(f"Hotkey listener started for: {self._hotkey_str}")
            return True
        except Exception as e:
            logger.error(f"Failed to start hotkey listener for '{self._hotkey_str}': {e}")
            self._listener = None
            self._is_running = False
            return False

    def stop(self):
        """Stops the global hotkey listener thread."""
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception as e:
                logger.warning(f"Error stopping hotkey listener: {e}")
            finally:
                self._listener = None
                self._is_running = False
                logger.info("Hotkey listener stopped")

    @property
    def is_running(self) -> bool:
        return self._is_running

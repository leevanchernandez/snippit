"""Unit tests for HotkeyListener bridge."""

import pytest
from PySide6.QtCore import QCoreApplication
from snippit.core.hotkey import HotkeyListener



def test_hotkey_listener_initialization(qapp):
    listener = HotkeyListener(hotkey_str="<cmd>+<alt>+s")
    assert listener.hotkey_str == "<cmd>+<alt>+s"
    assert listener.is_running is False


def test_hotkey_listener_signal_emission(qapp):
    listener = HotkeyListener(hotkey_str="<cmd>+<alt>+s")
    triggered = []

    listener.activated.connect(lambda: triggered.append(True))
    listener._on_hotkey_triggered()

    assert len(triggered) == 1
    assert triggered[0] is True

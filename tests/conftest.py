"""Shared pytest fixtures for Snippit test suite."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Provides a single QApplication instance for all UI and Qt-dependent tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

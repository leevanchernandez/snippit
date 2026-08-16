"""Entrypoint bootstrap for Snippit application."""

from __future__ import annotations

import logging
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from snippit.app import SnippitApp
from snippit.resources.icons import get_icon
from snippit.ui.theme import get_font


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    setup_logging()

    # Enable High-DPI scaling attributes if necessary
    app = QApplication(sys.argv)
    app.setApplicationName("Snippit")
    app.setOrganizationName("Snippit")
    app.setApplicationDisplayName("Snippit")
    app.setWindowIcon(get_icon("idle"))

    # Set standardized Windows typography
    app.setFont(get_font(size_pt=9))

    # Critical for tray applications: don't exit when overlay or toolbar closes
    app.setQuitOnLastWindowClosed(False)

    snippit_app = SnippitApp()
    snippit_app.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

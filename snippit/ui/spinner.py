"""Restrained, native vector-drawn animated spinner widget."""

from __future__ import annotations

from typing import Optional
from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from snippit.ui.theme import get_color


class SpinnerWidget(QWidget):
    """
    Smooth circular loading indicator matching the native design aesthetic.
    Renders an anti-aliased rotating arc using QPainter.
    """

    def __init__(
        self,
        size: int = 14,
        color: Optional[QColor] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._size = size
        self._color = color or get_color("accent")
        self._angle = 0.0
        self._is_active = False

        self.setFixedSize(QSize(size, size))
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # 60 FPS animation timer
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._on_tick)

    def set_color(self, color: QColor) -> None:
        """Sets the spinner arc color."""
        self._color = color
        self.update()

    def start(self) -> None:
        """Starts the spinner animation and makes widget visible."""
        if not self._is_active:
            self._is_active = True
            self.show()
            self._timer.start()

    def stop(self) -> None:
        """Stops the spinner animation and hides widget."""
        if self._is_active:
            self._is_active = False
            self._timer.stop()
            self.hide()

    def _on_tick(self) -> None:
        # Rotate 360 degrees in ~800ms
        self._angle = (self._angle + 7.2) % 360.0
        self.update()

    def paintEvent(self, event) -> None:
        if not self._is_active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        stroke_width = max(1.6, w * 0.14)
        margin = stroke_width / 2.0 + 1.0

        rect = QRectF(margin, margin, w - 2 * margin, h - 2 * margin)

        # Background track (faint subtle circle)
        track_color = QColor(self._color)
        track_color.setAlpha(40)
        track_pen = QPen(track_color, stroke_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)

        # Foreground spinning arc (~100 degree sweep)
        arc_pen = QPen(self._color, stroke_width)
        arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(arc_pen)

        # QPainter.drawArc takes startAngle and spanAngle in 1/16ths of a degree
        start_angle_16ths = int((-self._angle) * 16)
        span_angle_16ths = int(100 * 16)
        painter.drawArc(rect, start_angle_16ths, span_angle_16ths)

        painter.end()

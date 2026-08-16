"""Programmatic icon generators for Snippit."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)


def create_app_icon(size: int = 128, state: str = "idle") -> QPixmap:
    """
    Programmatically renders a modern, crisp app/tray icon for Snippit.
    
    States:
        - "idle": Cyan/Blue gradient snipping frame with scissors / crosshair
        - "capturing": Amber/Orange gradient active capture state
        - "processing": Purple/Indigo gradient AI processing state
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    # Base colors per state
    if state == "capturing":
        c1 = QColor(255, 140, 0)
        c2 = QColor(255, 69, 0)
    elif state == "processing":
        c1 = QColor(138, 43, 226)
        c2 = QColor(75, 0, 130)
    else:  # idle
        c1 = QColor(0, 150, 255)
        c2 = QColor(0, 100, 220)

    # Background rounded container
    margin = size * 0.08
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    radius = size * 0.22

    gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
    gradient.setColorAt(0.0, c1)
    gradient.setColorAt(1.0, c2)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawRoundedRect(rect, radius, radius)

    # Foreground snipping crop frame icon
    pen = QPen(QColor(255, 255, 255, 240))
    pen.setWidthF(max(2.0, size * 0.07))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    # Inward crop corners
    pad = size * 0.26
    c_len = size * 0.16
    l = pad
    t = pad
    r = size - pad
    b = size - pad

    # Top-Left corner
    p_tl = QPainterPath()
    p_tl.moveTo(l, t + c_len)
    p_tl.lineTo(l, t)
    p_tl.lineTo(l + c_len, t)
    painter.drawPath(p_tl)

    # Top-Right corner
    p_tr = QPainterPath()
    p_tr.moveTo(r - c_len, t)
    p_tr.lineTo(r, t)
    p_tr.lineTo(r, t + c_len)
    painter.drawPath(p_tr)

    # Bottom-Left corner
    p_bl = QPainterPath()
    p_bl.moveTo(l, b - c_len)
    p_bl.lineTo(l, b)
    p_bl.lineTo(l + c_len, b)
    painter.drawPath(p_bl)

    # Bottom-Right corner
    p_br = QPainterPath()
    p_br.moveTo(r - c_len, b)
    p_br.lineTo(r, b)
    p_br.lineTo(r, b - c_len)
    painter.drawPath(p_br)

    # Center dot / crosshair
    dot_pen = QPen(QColor(255, 255, 255, 220))
    dot_pen.setWidthF(max(2.0, size * 0.06))
    dot_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(dot_pen)
    center = QPointF(size / 2.0, size / 2.0)
    painter.drawPoint(center)

    painter.end()
    return pixmap


def get_icon(state: str = "idle") -> QIcon:
    """Returns a multi-resolution QIcon for the given state."""
    icon = QIcon()
    for s in [16, 24, 32, 48, 64, 128, 256]:
        icon.addPixmap(create_app_icon(s, state=state))
    return icon

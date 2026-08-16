"""Programmatic icon generators for Snippit."""

from __future__ import annotations

from typing import Optional
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)

from snippit.ui.theme import get_color


def create_app_icon(size: int = 128, state: str = "idle") -> QPixmap:
    """
    Programmatically renders a clean, crisp, solid-color app/tray icon for Snippit.
    No multi-color gradients — razor-sharp at 16x16 up to 256x256.

    States:
        - "idle": Solid accent cerulean blue (#0096FF)
        - "capturing": Solid warm amber (#FF9F0A)
        - "processing": Solid indigo (#6366F1)
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    # Base solid color per state
    if state == "capturing":
        bg_color = get_color("warning")
    elif state == "processing":
        bg_color = QColor(99, 102, 241)
    else:  # idle
        bg_color = get_color("accent")

    # Background squircle container
    margin = size * 0.08
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    radius = size * 0.22

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(bg_color))
    painter.drawRoundedRect(rect, radius, radius)

    # Foreground snipping crop frame icon
    pen = QPen(QColor(255, 255, 255, 250))
    pen.setWidthF(max(1.8, size * 0.075))
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
    dot_pen = QPen(QColor(255, 255, 255, 240))
    dot_pen.setWidthF(max(1.8, size * 0.065))
    dot_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(dot_pen)
    center = QPointF(size / 2.0, size / 2.0)
    painter.drawPoint(center)

    painter.end()
    return pixmap


def get_icon(state: str = "idle") -> QIcon:
    """Returns a multi-resolution QIcon for the given application state."""
    icon = QIcon()
    for s in [16, 24, 32, 48, 64, 128, 256]:
        icon.addPixmap(create_app_icon(s, state=state))
    return icon


def create_action_icon_pixmap(name: str, color: Optional[QColor] = None, size: int = 16) -> QPixmap:
    """
    Renders a crisp, monochrome vector action icon at the specified pixel size.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    icon_color = color or get_color("text_primary")
    scale = size / 16.0

    pen = QPen(icon_color)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    if name == "capture":
        # Camera / Snipping Frame
        pen.setWidthF(max(1.2, 1.4 * scale))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Camera body
        painter.drawRoundedRect(QRectF(2.0 * scale, 4.5 * scale, 12.0 * scale, 9.0 * scale), 1.5 * scale, 1.5 * scale)
        # Top bump
        painter.drawRoundedRect(QRectF(5.5 * scale, 2.5 * scale, 5.0 * scale, 2.0 * scale), 0.5 * scale, 0.5 * scale)
        # Center lens
        painter.drawEllipse(QPointF(8.0 * scale, 9.0 * scale), 2.4 * scale, 2.4 * scale)

    elif name == "settings":
        # Minimalist 6-tooth gear
        pen.setWidthF(max(1.2, 1.3 * scale))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Central circle
        painter.drawEllipse(QPointF(8.0 * scale, 8.0 * scale), 3.0 * scale, 3.0 * scale)
        # Center hole
        painter.drawEllipse(QPointF(8.0 * scale, 8.0 * scale), 1.2 * scale, 1.2 * scale)
        # 6 teeth ticks
        teeth = [
            (8.0, 2.0, 8.0, 4.5),
            (8.0, 11.5, 8.0, 14.0),
            (2.8, 5.0, 5.0, 6.2),
            (11.0, 9.8, 13.2, 11.0),
            (2.8, 11.0, 5.0, 9.8),
            (11.0, 6.2, 13.2, 5.0),
        ]
        for x1, y1, x2, y2 in teeth:
            painter.drawLine(QPointF(x1 * scale, y1 * scale), QPointF(x2 * scale, y2 * scale))

    elif name == "quit":
        # Power button symbol
        pen.setWidthF(max(1.2, 1.5 * scale))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Arc (top open)
        arc_rect = QRectF(3.0 * scale, 3.5 * scale, 10.0 * scale, 10.0 * scale)
        painter.drawArc(arc_rect, 45 * 16, 270 * 16)
        # Top vertical bar
        painter.drawLine(QPointF(8.0 * scale, 2.0 * scale), QPointF(8.0 * scale, 7.5 * scale))

    elif name == "save":
        # Clean Floppy / Save File icon
        pen.setWidthF(max(1.2, 1.3 * scale))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Body path with cut corner
        body = QPainterPath()
        body.moveTo(3.0 * scale, 2.5 * scale)
        body.lineTo(10.5 * scale, 2.5 * scale)
        body.lineTo(13.0 * scale, 5.0 * scale)
        body.lineTo(13.0 * scale, 13.5 * scale)
        body.lineTo(3.0 * scale, 13.5 * scale)
        body.closeSubpath()
        painter.drawPath(body)
        # Shutter box
        painter.drawRect(QRectF(5.5 * scale, 2.5 * scale, 5.0 * scale, 3.5 * scale))
        # Label area
        painter.drawRect(QRectF(5.0 * scale, 8.5 * scale, 6.0 * scale, 5.0 * scale))

    elif name == "remove_bg":
        # AI Magic Sparkles
        pen.setWidthF(max(1.1, 1.2 * scale))
        painter.setPen(pen)
        painter.setBrush(QBrush(icon_color))
        # Main sparkle
        sp1 = QPainterPath()
        cx1, cy1 = 7.0 * scale, 7.0 * scale
        sp1.moveTo(cx1, cy1 - 5.0 * scale)
        sp1.quadTo(cx1, cy1, cx1 + 5.0 * scale, cy1)
        sp1.quadTo(cx1, cy1, cx1, cy1 + 5.0 * scale)
        sp1.quadTo(cx1, cy1, cx1 - 5.0 * scale, cy1)
        sp1.quadTo(cx1, cy1, cx1, cy1 - 5.0 * scale)
        painter.drawPath(sp1)
        # Small companion sparkle
        sp2 = QPainterPath()
        cx2, cy2 = 12.5 * scale, 12.5 * scale
        sp2.moveTo(cx2, cy2 - 2.5 * scale)
        sp2.quadTo(cx2, cy2, cx2 + 2.5 * scale, cy2)
        sp2.quadTo(cx2, cy2, cx2, cy2 + 2.5 * scale)
        sp2.quadTo(cx2, cy2, cx2 - 2.5 * scale, cy2)
        sp2.quadTo(cx2, cy2, cx2, cy2 - 2.5 * scale)
        painter.drawPath(sp2)

    elif name == "check":
        # Crisp checkmark
        pen.setWidthF(max(1.3, 1.6 * scale))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        p = QPainterPath()
        p.moveTo(3.2 * scale, 8.0 * scale)
        p.lineTo(6.5 * scale, 11.5 * scale)
        p.lineTo(13.0 * scale, 4.5 * scale)
        painter.drawPath(p)

    elif name == "close":
        # Dismiss cross
        pen.setWidthF(max(1.2, 1.4 * scale))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(QPointF(4.0 * scale, 4.0 * scale), QPointF(12.0 * scale, 12.0 * scale))
        painter.drawLine(QPointF(12.0 * scale, 4.0 * scale), QPointF(4.0 * scale, 12.0 * scale))

    elif name == "warning":
        # Warning triangle
        pen.setWidthF(max(1.2, 1.3 * scale))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        tri = QPainterPath()
        tri.moveTo(8.0 * scale, 2.5 * scale)
        tri.lineTo(13.5 * scale, 13.0 * scale)
        tri.lineTo(2.5 * scale, 13.0 * scale)
        tri.closeSubpath()
        painter.drawPath(tri)
        # Exclamation
        painter.drawLine(QPointF(8.0 * scale, 6.0 * scale), QPointF(8.0 * scale, 9.5 * scale))
        painter.drawPoint(QPointF(8.0 * scale, 11.5 * scale))

    painter.end()
    return pixmap


def get_action_icon(name: str, color: Optional[QColor] = None) -> QIcon:
    """Returns a multi-resolution QIcon for a named UI action."""
    icon = QIcon()
    for s in [16, 20, 24, 32, 48]:
        icon.addPixmap(create_action_icon_pixmap(name, color=color, size=s))
    return icon

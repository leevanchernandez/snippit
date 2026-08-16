"""Fullscreen translucent overlay for frozen screen capture and region selection."""

from __future__ import annotations

import logging
from typing import Optional
from PIL import Image
from PySide6.QtCore import QPoint, QRect, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import QWidget

from snippit.core.capture import CapturedScreen, crop_region
from snippit.core.clipboard import pil_to_qimage
from snippit.ui.theme import get_color, get_font

logger = logging.getLogger(__name__)


class SelectionOverlay(QWidget):
    """
    Spans the entire multi-monitor virtual screen with a frozen screenshot,
    allowing the user to drag a rubber-band rectangle to select a capture area.
    """
    # Emitted when a region is successfully captured: (cropped_pil_image, global_qrect)
    captured = Signal(object, object)
    # Emitted when selection is cancelled (Esc / Right-click)
    cancelled = Signal()

    def __init__(self, captured_screen: CapturedScreen, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._captured_screen = captured_screen
        self._geom = captured_screen.geometry

        # Convert background PIL Image to QPixmap for rendering
        qimg = pil_to_qimage(captured_screen.image)
        self._bg_pixmap = QPixmap.fromImage(qimg)

        # State tracking
        self._is_selecting = False
        self._start_pos = QPoint()
        self._current_pos = QPoint()
        self._selection_rect = QRect()

        # Window flags and attributes for frameless multi-monitor overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)

        # Position to cover the virtual desktop
        self.setGeometry(
            self._geom.left,
            self._geom.top,
            self._geom.width,
            self._geom.height,
        )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_selecting = True
            self._start_pos = event.position().toPoint()
            self._current_pos = self._start_pos
            self._selection_rect = QRect(self._start_pos, self._start_pos)
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancel()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_selecting:
            self._current_pos = event.position().toPoint()
            self._selection_rect = QRect(self._start_pos, self._current_pos).normalized()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self._is_selecting:
            self._is_selecting = False
            self._current_pos = event.position().toPoint()
            self._selection_rect = QRect(self._start_pos, self._current_pos).normalized()

            # Ignore accidental micro-clicks (< 5px)
            if self._selection_rect.width() >= 5 and self._selection_rect.height() >= 5:
                self._finish_selection()
            else:
                self._selection_rect = QRect()
                self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Q):
            self.cancel()
        else:
            super().keyPressEvent(event)

    def cancel(self):
        """Cancels capture and closes the overlay."""
        self.hide()
        self.cancelled.emit()
        self.deleteLater()

    def _finish_selection(self):
        """Crops the selected region and emits the captured signal."""
        # Convert local coordinates to global virtual screen coordinates
        crop_x = self._geom.left + self._selection_rect.x()
        crop_y = self._geom.top + self._selection_rect.y()
        crop_w = self._selection_rect.width()
        crop_h = self._selection_rect.height()

        cropped_image = crop_region(
            image=self._captured_screen.image,
            screen_geometry=self._geom,
            crop_x=crop_x,
            crop_y=crop_y,
            crop_w=crop_w,
            crop_h=crop_h,
        )

        global_rect = QRect(crop_x, crop_y, crop_w, crop_h)
        self.hide()
        self.captured.emit(cropped_image, global_rect)
        self.deleteLater()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 1. Draw frozen desktop background scaled to widget rect (preserves 1:1 physical alignment)
        if not self._bg_pixmap.isNull():
            painter.drawPixmap(self.rect(), self._bg_pixmap)

        # 2. Draw mask over everything outside the selection
        mask_color = get_color("surface_overlay_dim")
        if self._selection_rect.isValid() and not self._selection_rect.isEmpty():
            # Cutout path using OddEvenFill
            path = QPainterPath()
            path.setFillRule(Qt.FillRule.OddEvenFill)
            path.addRect(QRectF(self.rect()))
            path.addRect(QRectF(self._selection_rect))
            painter.fillPath(path, mask_color)

            # 3. Draw border around selection rectangle (Crisp accent blue)
            border_pen = QPen(get_color("accent"))
            border_pen.setWidth(2)
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._selection_rect)

            # 4. Draw dimension badge (showing physical pixels)
            w = self._selection_rect.width()
            h = self._selection_rect.height()
            phys_w = int(round(w * self._geom.scale_x))
            phys_h = int(round(h * self._geom.scale_y))
            dim_text = f"{phys_w} × {phys_h} px"

            font = get_font(size_pt=9, weight=QFont.Weight.DemiBold)
            painter.setFont(font)
            fm = painter.fontMetrics()
            text_w = fm.horizontalAdvance(dim_text) + 16
            text_h = fm.height() + 8

            # Position badge below selection, or above if close to bottom
            badge_x = self._selection_rect.x() + (self._selection_rect.width() - text_w) // 2
            badge_x = max(8, min(self.width() - text_w - 8, badge_x))

            if self._selection_rect.bottom() + text_h + 12 < self.height():
                badge_y = self._selection_rect.bottom() + 8
            elif self._selection_rect.top() - text_h - 8 > 0:
                badge_y = self._selection_rect.top() - text_h - 8
            else:
                badge_y = self._selection_rect.y() + 8

            badge_rect = QRectF(badge_x, badge_y, text_w, text_h)

            # Badge background and subtle border
            badge_bg = get_color("surface_solid")
            badge_border = get_color("surface_border")
            painter.setPen(QPen(badge_border, 1))
            painter.setBrush(QBrush(badge_bg))
            painter.drawRoundedRect(badge_rect, 4, 4)

            # Badge text
            painter.setPen(get_color("text_primary"))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, dim_text)
        else:
            # Entire screen is dimmed when no selection is in progress
            painter.fillRect(self.rect(), mask_color)

        painter.end()

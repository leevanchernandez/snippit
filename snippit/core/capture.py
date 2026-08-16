"""Screen capture engine leveraging mss for high-performance multi-monitor capture."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import mss
from PIL import Image
from PySide6.QtGui import QGuiApplication


@dataclass(frozen=True)
class ScreenGeometry:
    """Represents virtual screen geometry with logical dimensions and physical pixel mapping."""
    left: int
    top: int
    width: int
    height: int
    phys_width: Optional[int] = None
    phys_height: Optional[int] = None

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return (self.left, self.top, self.width, self.height)

    @property
    def scale_x(self) -> float:
        if self.phys_width and self.width > 0:
            return self.phys_width / self.width
        return 1.0

    @property
    def scale_y(self) -> float:
        if self.phys_height and self.height > 0:
            return self.phys_height / self.height
        return 1.0


@dataclass
class CapturedScreen:
    """Container for the frozen screenshot and its screen geometry."""
    image: Image.Image
    geometry: ScreenGeometry


def get_virtual_screen_geometry() -> ScreenGeometry:
    """
    Returns the logical geometry of the combined virtual screen across all monitors.
    """
    app = QGuiApplication.instance()
    if app:
        primary = app.primaryScreen()
        if primary:
            virt_rect = primary.virtualGeometry()
            return ScreenGeometry(
                left=virt_rect.left(),
                top=virt_rect.top(),
                width=virt_rect.width(),
                height=virt_rect.height(),
            )

    # Fallback to mss monitor coordinates
    with mss.mss() as sct:
        mon = sct.monitors[0]
        return ScreenGeometry(
            left=mon["left"],
            top=mon["top"],
            width=mon["width"],
            height=mon["height"],
        )


def capture_virtual_screen() -> CapturedScreen:
    """
    Captures the entire virtual screen across all connected monitors.
    
    Returns a CapturedScreen object containing the PIL Image (RGB) and its ScreenGeometry.
    """
    logical_geom = get_virtual_screen_geometry()

    with mss.mss() as sct:
        mon = sct.monitors[0]
        sct_img = sct.grab(mon)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        geom = ScreenGeometry(
            left=logical_geom.left,
            top=logical_geom.top,
            width=logical_geom.width,
            height=logical_geom.height,
            phys_width=img.width,
            phys_height=img.height,
        )
        return CapturedScreen(image=img, geometry=geom)


def crop_region(
    image: Image.Image,
    screen_geometry: ScreenGeometry,
    crop_x: int,
    crop_y: int,
    crop_w: int,
    crop_h: int,
) -> Image.Image:
    """
    Crops a rectangular region from the captured virtual screen image.
    Handles HiDPI display scaling between logical coordinates and physical image pixels.
    """
    # Normalize if width/height are negative (dragged upwards/leftwards)
    if crop_w < 0:
        crop_x += crop_w
        crop_w = abs(crop_w)
    if crop_h < 0:
        crop_y += crop_h
        crop_h = abs(crop_h)

    # Calculate scale factor between physical image pixels and logical coordinates
    scale_x = screen_geometry.scale_x
    scale_y = screen_geometry.scale_y

    # Convert logical coordinates to relative physical pixel coordinates
    rel_x = (crop_x - screen_geometry.left) * scale_x
    rel_y = (crop_y - screen_geometry.top) * scale_y
    phys_w = crop_w * scale_x
    phys_h = crop_h * scale_y

    # Clamp coordinates to image dimensions
    img_w, img_h = image.size
    x0 = max(0, min(img_w, int(round(rel_x))))
    y0 = max(0, min(img_h, int(round(rel_y))))
    x1 = max(0, min(img_w, int(round(rel_x + phys_w))))
    y1 = max(0, min(img_h, int(round(rel_y + phys_h))))

    # Ensure valid bounding box
    if x1 <= x0 or y1 <= y0:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))

    return image.crop((x0, y0, x1, y1))

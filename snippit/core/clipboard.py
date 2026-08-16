"""Alpha-aware dual-format clipboard manager for cross-application compatibility."""

from __future__ import annotations

import io
from typing import Union
from PIL import Image
from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QMimeData
from PySide6.QtGui import QGuiApplication, QImage


def pil_to_qimage(image: Image.Image) -> QImage:
    """
    Converts a PIL Image to a PySide6 QImage with appropriate format handling.
    """
    if image.mode == "RGBA":
        # Convert RGBA to raw bytes and create QImage with Format_RGBA8888
        data = image.tobytes("raw", "RGBA")
        qimage = QImage(data, image.width, image.height, image.width * 4, QImage.Format.Format_RGBA8888)
        # Deep copy to ensure memory safety after the PIL buffer is garbage collected
        return qimage.copy()
    elif image.mode == "RGB":
        data = image.tobytes("raw", "RGB")
        qimage = QImage(data, image.width, image.height, image.width * 3, QImage.Format.Format_RGB888)
        return qimage.copy()
    else:
        # Fallback convert to RGBA
        converted = image.convert("RGBA")
        data = converted.tobytes("raw", "RGBA")
        qimage = QImage(data, converted.width, converted.height, converted.width * 4, QImage.Format.Format_RGBA8888)
        return qimage.copy()


def qimage_to_pil(qimage: QImage) -> Image.Image:
    """
    Converts a PySide6 QImage to a PIL Image (RGBA or RGB).
    """
    # Save QImage as PNG bytes in memory and open via PIL for robustness across platforms/formats
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    qimage.save(buffer, "PNG")
    bytes_data = buffer.data().data()
    return Image.open(io.BytesIO(bytes_data))


def image_to_png_bytes(image: Union[Image.Image, QImage]) -> bytes:
    """
    Encodes a PIL Image or QImage as PNG bytes.
    """
    if isinstance(image, QImage):
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        return bytes(buffer.data().data())
    elif isinstance(image, Image.Image):
        out = io.BytesIO()
        image.save(out, format="PNG")
        return out.getvalue()
    else:
        raise TypeError(f"Expected PIL.Image or QImage, got {type(image)}")


def copy_image_to_clipboard(image: Union[Image.Image, QImage]) -> bool:
    """
    Copies an image to the system clipboard using a dual-format strategy:
    1. Bitmap format via QMimeData.setImageData(qimage) for native bitmap apps (e.g. Paint).
    2. Raw 'image/png' bytes for alpha-channel aware apps (e.g. Discord, Slack, Photoshop, browsers).
    
    Returns True if successfully set.
    """
    clipboard = QGuiApplication.clipboard()
    if clipboard is None:
        return False

    if isinstance(image, Image.Image):
        qimage = pil_to_qimage(image)
        png_bytes = image_to_png_bytes(image)
    elif isinstance(image, QImage):
        qimage = image
        png_bytes = image_to_png_bytes(image)
    else:
        raise TypeError(f"Expected PIL.Image or QImage, got {type(image)}")

    mime_data = QMimeData()
    # Format 1: Standard QImage bitmap
    mime_data.setImageData(qimage)
    # Format 2: PNG data with preserved alpha channel
    mime_data.setData("image/png", QByteArray(png_bytes))

    clipboard.setMimeData(mime_data)
    return True

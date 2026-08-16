"""Unit tests for clipboard conversion and formatting."""

import pytest
from PIL import Image
from PySide6.QtGui import QGuiApplication, QImage
from snippit.core.clipboard import (
    image_to_png_bytes,
    pil_to_qimage,
    qimage_to_pil,
)



def test_pil_to_qimage_rgba(qapp):
    pil_img = Image.new("RGBA", (64, 32), color=(255, 0, 0, 128))
    qimg = pil_to_qimage(pil_img)

    assert qimg.width() == 64
    assert qimg.height() == 32
    assert qimg.hasAlphaChannel() is True


def test_pil_to_qimage_rgb(qapp):
    pil_img = Image.new("RGB", (50, 50), color=(0, 255, 0))
    qimg = pil_to_qimage(pil_img)

    assert qimg.width() == 50
    assert qimg.height() == 50


def test_qimage_pil_roundtrip(qapp):
    pil_img = Image.new("RGBA", (30, 30), color=(10, 20, 30, 200))
    qimg = pil_to_qimage(pil_img)
    recovered_pil = qimage_to_pil(qimg)

    assert recovered_pil.size == (30, 30)
    # Check pixel value match
    orig_px = pil_img.getpixel((15, 15))
    rec_px = recovered_pil.getpixel((15, 15))
    assert orig_px == rec_px


def test_image_to_png_bytes(qapp):
    pil_img = Image.new("RGBA", (16, 16), color=(255, 255, 0, 255))
    png_bytes = image_to_png_bytes(pil_img)

    # Standard PNG magic signature: \x89PNG\r\n\x1a\n
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")

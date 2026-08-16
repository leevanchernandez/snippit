"""Unit tests for screen capture geometry and cropping logic."""

import pytest
from PIL import Image
from snippit.core.capture import ScreenGeometry, crop_region


def test_screen_geometry_bounds():
    geom = ScreenGeometry(left=-1920, top=0, width=3840, height=1080)
    assert geom.left == -1920
    assert geom.top == 0
    assert geom.width == 3840
    assert geom.height == 1080
    assert geom.right == 1920
    assert geom.bottom == 1080
    assert geom.bounds == (-1920, 0, 3840, 1080)


def test_crop_region_standard():
    # Create a 200x200 test image with known red pixel at (50, 50)
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img.putpixel((50, 50), (255, 0, 0))

    geom = ScreenGeometry(left=0, top=0, width=200, height=200)
    cropped = crop_region(img, geom, crop_x=40, crop_y=40, crop_w=20, crop_h=20)

    assert cropped.size == (20, 20)
    # The pixel at (50, 50) global should now be at (10, 10) in the cropped image
    assert cropped.getpixel((10, 10)) == (255, 0, 0)


def test_crop_region_with_virtual_offset():
    # Simulate secondary monitor located at left = -1000, top = -500
    img = Image.new("RGB", (2000, 1000), color=(0, 128, 255))
    geom = ScreenGeometry(left=-1000, top=-500, width=2000, height=1000)

    # Crop a 100x100 box at global coords (-900, -400) -> relative coords in image (100, 100)
    cropped = crop_region(img, geom, crop_x=-900, crop_y=-400, crop_w=100, crop_h=100)
    assert cropped.size == (100, 100)


def test_crop_region_inverted_drag():
    # When user drags from bottom-right to top-left, crop_w and crop_h are negative
    img = Image.new("RGB", (200, 200), color=(100, 100, 100))
    geom = ScreenGeometry(left=0, top=0, width=200, height=200)

    cropped = crop_region(img, geom, crop_x=100, crop_y=100, crop_w=-50, crop_h=-30)
    # Should normalize to x=50, y=70, w=50, h=30
    assert cropped.size == (50, 30)


def test_crop_region_out_of_bounds_clamping():
    img = Image.new("RGB", (100, 100), color=(50, 50, 50))
    geom = ScreenGeometry(left=0, top=0, width=100, height=100)

    # Crop extending beyond image boundaries
    cropped = crop_region(img, geom, crop_x=80, crop_y=80, crop_w=50, crop_h=50)
    assert cropped.size == (20, 20)


def test_crop_region_hidpi_scaling():
    # Logical screen: 1536x960, Physical screen image: 1920x1200 (1.25x scaling)
    img = Image.new("RGB", (1920, 1200), color=(100, 100, 100))
    geom = ScreenGeometry(
        left=0,
        top=0,
        width=1536,
        height=960,
        phys_width=1920,
        phys_height=1200,
    )
    assert geom.scale_x == 1.25
    assert geom.scale_y == 1.25

    # Crop logical region of 100x100 -> should result in 125x125 physical pixels
    cropped = crop_region(img, geom, crop_x=100, crop_y=100, crop_w=100, crop_h=100)
    assert cropped.size == (125, 125)


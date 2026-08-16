"""Centralized design token system and QSS stylesheets for Snippit."""

from __future__ import annotations

from typing import Any, Dict
from PySide6.QtGui import QColor, QFont

# ----------------------------------------------------------------------
# 1. DESIGN TOKENS
# ----------------------------------------------------------------------

# Standardized color tokens (Hex & RGBA with float alpha 0.0 - 1.0)
TOKENS: Dict[str, str] = {
    # Surfaces
    "surface": "rgba(30, 32, 38, 0.95)",
    "surface_solid": "#1E2026",
    "surface_border": "rgba(255, 255, 255, 0.10)",
    "surface_overlay_dim": "rgba(0, 0, 0, 0.43)",

    # Typography / Text
    "text_primary": "#E8E8E8",
    "text_secondary": "#9B9B9B",
    "text_muted": "#707070",
    "text_on_accent": "#FFFFFF",

    # Primary Accent (Electric Cerulean Blue - Native & Restrained)
    "accent": "#0096FF",
    "accent_hover": "#0082E0",
    "accent_pressed": "#006FBF",
    "accent_subtle": "rgba(0, 150, 255, 0.15)",

    # Semantic Status Colors
    "success": "#34C759",
    "success_hover": "#2DB84F",
    "warning": "#FF9F0A",
    "danger": "#FF3B30",
    "danger_hover": "#E0342B",
    "danger_pressed": "#C42A22",

    # Secondary Controls / Buttons
    "control_bg": "rgba(255, 255, 255, 0.07)",
    "control_bg_hover": "rgba(255, 255, 255, 0.13)",
    "control_bg_pressed": "rgba(255, 255, 255, 0.04)",
    "control_border": "rgba(255, 255, 255, 0.10)",
    "control_border_hover": "rgba(255, 255, 255, 0.20)",

    # Dimensions & Radii
    "radius_sm": "4px",
    "radius_md": "6px",
    "radius_lg": "8px",

    # Spacing
    "space_xs": "4px",
    "space_sm": "6px",
    "space_md": "8px",
    "space_lg": "12px",
    "space_xl": "16px",

    # Typography Families & Sizes
    "font_family": '"Segoe UI Variable", "Segoe UI"',
    "font_size_sm": "11px",
    "font_size_md": "12px",
    "font_size_lg": "13px",
    "font_size_xl": "14px",
}

# Pre-computed QColor map for QPainter, QBrush, QPen, and QWidget rendering
_COLOR_MAP: Dict[str, QColor] = {
    "surface": QColor(30, 32, 38, 242),
    "surface_solid": QColor(30, 32, 38, 255),
    "surface_border": QColor(255, 255, 255, 25),
    "surface_overlay_dim": QColor(0, 0, 0, 110),
    "text_primary": QColor(232, 232, 232, 255),
    "text_secondary": QColor(155, 155, 155, 255),
    "text_muted": QColor(112, 112, 112, 255),
    "text_on_accent": QColor(255, 255, 255, 255),
    "accent": QColor(0, 150, 255, 255),
    "accent_hover": QColor(0, 130, 224, 255),
    "accent_pressed": QColor(0, 111, 191, 255),
    "accent_subtle": QColor(0, 150, 255, 38),
    "success": QColor(52, 199, 89, 255),
    "success_hover": QColor(45, 184, 79, 255),
    "warning": QColor(255, 159, 10, 255),
    "danger": QColor(255, 59, 48, 255),
    "danger_hover": QColor(224, 52, 43, 255),
    "danger_pressed": QColor(196, 42, 34, 255),
    "control_bg": QColor(255, 255, 255, 18),
    "control_bg_hover": QColor(255, 255, 255, 33),
    "control_bg_pressed": QColor(255, 255, 255, 10),
    "control_border": QColor(255, 255, 255, 25),
    "control_border_hover": QColor(255, 255, 255, 51),
}


def get_color(token_name: str) -> QColor:
    """
    Returns a QColor instance for the given design token name.
    Falls back to parsing the token string or white if unrecognized.
    """
    if token_name in _COLOR_MAP:
        return QColor(_COLOR_MAP[token_name])

    val = TOKENS.get(token_name, token_name)
    color = QColor(val)
    if color.isValid():
        return color
    return QColor(255, 255, 255, 255)


def get_font(size_pt: int = 9, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    """Returns a standardized QFont preferring Segoe UI Variable with Segoe UI fallback."""
    font = QFont("Segoe UI Variable", size_pt, weight)
    if not font.exactMatch():
        font = QFont("Segoe UI", size_pt, weight)
    return font


# ----------------------------------------------------------------------
# 2. QSS STYLESHEET GENERATORS
# ----------------------------------------------------------------------

def get_toolbar_stylesheet() -> str:
    """Returns the complete QSS stylesheet for the floating action toolbar."""
    return f"""
    QFrame#toolbarFrame {{
        background-color: {TOKENS["surface"]};
        border: 1px solid {TOKENS["surface_border"]};
        border-radius: {TOKENS["radius_lg"]};
    }}

    QLabel#statusLabel {{
        color: {TOKENS["success"]};
        font-family: {TOKENS["font_family"]};
        font-size: {TOKENS["font_size_md"]};
        font-weight: 600;
        padding-left: 6px;
        padding-right: 4px;
    }}

    /* Standard secondary action buttons */
    QPushButton {{
        background-color: {TOKENS["control_bg"]};
        color: {TOKENS["text_primary"]};
        border: 1px solid {TOKENS["control_border"]};
        border-radius: {TOKENS["radius_md"]};
        font-family: {TOKENS["font_family"]};
        font-size: {TOKENS["font_size_md"]};
        font-weight: 500;
        padding: 5px 12px;
        min-height: 18px;
    }}

    QPushButton:hover {{
        background-color: {TOKENS["control_bg_hover"]};
        border-color: {TOKENS["control_border_hover"]};
        color: {TOKENS["text_on_accent"]};
    }}

    QPushButton:pressed {{
        background-color: {TOKENS["control_bg_pressed"]};
    }}

    /* Primary action button (Remove BG - Solid Accent, No Gradient) */
    QPushButton#btnRemoveBg {{
        background-color: {TOKENS["accent"]};
        border: 1px solid {TOKENS["accent"]};
        color: {TOKENS["text_on_accent"]};
        font-weight: 600;
    }}

    QPushButton#btnRemoveBg:hover {{
        background-color: {TOKENS["accent_hover"]};
        border-color: {TOKENS["accent_hover"]};
        color: {TOKENS["text_on_accent"]};
    }}

    QPushButton#btnRemoveBg:pressed {{
        background-color: {TOKENS["accent_pressed"]};
        border-color: {TOKENS["accent_pressed"]};
    }}

    /* Ghost dismiss button (Close) */
    QPushButton#btnClose {{
        background-color: transparent;
        border: none;
        color: {TOKENS["text_secondary"]};
        padding: 4px 8px;
        font-family: {TOKENS["font_family"]};
        font-size: {TOKENS["font_size_xl"]};
        font-weight: 400;
        border-radius: {TOKENS["radius_md"]};
    }}

    QPushButton#btnClose:hover {{
        background-color: {TOKENS["danger"]};
        color: {TOKENS["text_on_accent"]};
    }}

    QPushButton#btnClose:pressed {{
        background-color: {TOKENS["danger_pressed"]};
        color: {TOKENS["text_on_accent"]};
    }}
    """


def get_tray_menu_stylesheet() -> str:
    """Returns the complete QSS stylesheet for the system tray context menu."""
    return f"""
    QMenu {{
        background-color: {TOKENS["surface"]};
        color: {TOKENS["text_primary"]};
        border: 1px solid {TOKENS["surface_border"]};
        border-radius: {TOKENS["radius_lg"]};
        padding: 6px;
        font-family: {TOKENS["font_family"]};
        font-size: {TOKENS["font_size_md"]};
    }}

    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: {TOKENS["radius_sm"]};
        color: {TOKENS["text_primary"]};
    }}

    QMenu::item:selected {{
        background-color: {TOKENS["accent"]};
        color: {TOKENS["text_on_accent"]};
    }}

    QMenu::item:disabled {{
        color: {TOKENS["text_muted"]};
    }}

    QMenu::separator {{
        height: 1px;
        background-color: {TOKENS["surface_border"]};
        margin: 4px 6px;
    }}

    QMenu::icon {{
        padding-left: 6px;
    }}
    """

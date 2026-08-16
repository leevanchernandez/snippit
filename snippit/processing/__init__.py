"""Processing package for pluggable processors (AI background removal, OCR, etc.)."""

from snippit.processing.background_removal import (
    DEFAULT_MODEL,
    SUPPORTED_MODELS,
    BackgroundRemovalWorker,
    clear_session_cache,
    get_session,
    is_model_downloaded,
    remove_background,
)

__all__ = [
    "DEFAULT_MODEL",
    "SUPPORTED_MODELS",
    "BackgroundRemovalWorker",
    "clear_session_cache",
    "get_session",
    "is_model_downloaded",
    "remove_background",
]

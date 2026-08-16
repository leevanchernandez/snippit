"""AI Background Removal processor and asynchronous worker using rembg and ONNX Runtime."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional
from PIL import Image
from PySide6.QtCore import QObject, QThread, Signal

logger = logging.getLogger(__name__)

# Supported model identifiers
SUPPORTED_MODELS = [
    "isnet-general-use",
    "silueta",
    "birefnet-general-lite",
    "u2net",
]

DEFAULT_MODEL = "isnet-general-use"

# Global session cache to avoid expensive ONNX model re-initialization
_SESSION_CACHE: Dict[str, object] = {}


def get_model_cache_dir() -> Path:
    """Returns the local directory where ONNX model weights are stored."""
    try:
        from rembg.sessions.base import BaseSession
        return Path(BaseSession.u2net_home())
    except Exception:
        return Path.home() / ".u2net"


def is_model_downloaded(model_name: str = DEFAULT_MODEL) -> bool:
    """Checks if the specified model weights file already exists on disk."""
    cache_dir = get_model_cache_dir()
    # rembg typically saves models as <model_name>.onnx in ~/.u2net/
    model_file = cache_dir / f"{model_name}.onnx"
    return model_file.is_file() and model_file.stat().st_size > 0


def get_session(model_name: str = DEFAULT_MODEL) -> object:
    """
    Retrieves or instantiates an ONNX Runtime inference session for the given model.
    Sessions are cached in memory for zero-overhead subsequent inferences.
    """
    global _SESSION_CACHE
    if model_name in _SESSION_CACHE:
        return _SESSION_CACHE[model_name]

    import rembg

    logger.info(f"Initializing rembg session for model '{model_name}'...")
    session = rembg.new_session(model_name=model_name)
    _SESSION_CACHE[model_name] = session
    return session


def clear_session_cache() -> None:
    """Clears cached inference sessions to free memory."""
    global _SESSION_CACHE
    _SESSION_CACHE.clear()


def remove_background(
    image: Image.Image,
    session: Optional[object] = None,
    model_name: str = DEFAULT_MODEL,
    **kwargs,
) -> Image.Image:
    """
    Performs background removal on a PIL Image and returns an RGBA image with transparency.

    Args:
        image: Source PIL Image (RGB or RGBA).
        session: Optional pre-loaded rembg session. If None, uses cached session.
        model_name: Model name to use if session is not provided.
        **kwargs: Extra parameters passed to rembg.remove (e.g., alpha_matting, post_process_mask).

    Returns:
        Transparent PIL Image (RGBA).
    """
    if image is None:
        raise ValueError("Cannot remove background from None image")

    if session is None:
        session = get_session(model_name=model_name)

    import rembg

    # Ensure input image is PIL Image
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected PIL.Image.Image, got {type(image)}")

    # Perform background removal
    output = rembg.remove(image, session=session, **kwargs)

    # Ensure output is converted to RGBA
    if isinstance(output, Image.Image):
        if output.mode != "RGBA":
            output = output.convert("RGBA")
        return output
    elif isinstance(output, bytes):
        import io
        return Image.open(io.BytesIO(output)).convert("RGBA")
    else:
        raise RuntimeError(f"Unexpected output type from rembg: {type(output)}")


class BackgroundRemovalWorker(QThread):
    """
    Asynchronous worker thread executing AI background removal off the main Qt UI thread.
    """
    started_processing = Signal()
    status_changed = Signal(str)
    finished = Signal(object)  # Emits PIL.Image.Image
    error = Signal(str)

    def __init__(
        self,
        image: Image.Image,
        model_name: str = DEFAULT_MODEL,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.image = image
        self.model_name = model_name
        self._is_cancelled = False

    def cancel(self):
        """Requests cancellation of worker."""
        self._is_cancelled = True

    def run(self):
        """Worker thread entry point."""
        try:
            self.started_processing.emit()

            if self._is_cancelled:
                return

            # Check if model is downloaded
            if not is_model_downloaded(self.model_name):
                logger.info(f"Model '{self.model_name}' not found locally. Downloading...")
                self.status_changed.emit("Downloading AI model (~176 MB)...")
            else:
                self.status_changed.emit("Removing background...")

            if self._is_cancelled:
                return

            # Load or retrieve session (handles download internally if needed)
            session = get_session(self.model_name)

            if self._is_cancelled:
                return

            self.status_changed.emit("Removing background...")

            # Run inference
            result_image = remove_background(
                self.image,
                session=session,
                model_name=self.model_name,
            )

            if self._is_cancelled:
                return

            logger.info("Background removal completed successfully")
            self.finished.emit(result_image)

        except Exception as e:
            logger.error(f"Error during background removal: {e}", exc_info=True)
            self.error.emit(str(e))

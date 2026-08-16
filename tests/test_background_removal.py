"""Unit tests for AI background removal processor, session caching, and QThread worker."""

from unittest.mock import MagicMock, patch
import pytest
from PIL import Image
from PySide6.QtCore import QCoreApplication

from snippit.processing.background_removal import (
    DEFAULT_MODEL,
    BackgroundRemovalWorker,
    clear_session_cache,
    get_model_cache_dir,
    get_session,
    is_model_downloaded,
    remove_background,
)


def test_model_cache_dir():
    cache_dir = get_model_cache_dir()
    assert cache_dir is not None
    assert str(cache_dir).endswith(".u2net")


def test_is_model_downloaded_nonexistent():
    # A dummy non-existent model name should return False
    assert not is_model_downloaded("non_existent_dummy_model_12345")


def test_session_caching():
    clear_session_cache()

    mock_session = MagicMock()
    with patch("rembg.new_session", return_value=mock_session) as mock_new_session:
        s1 = get_session("test-model")
        s2 = get_session("test-model")

        assert s1 is mock_session
        assert s2 is mock_session
        # Should only call new_session once due to cache
        assert mock_new_session.call_count == 1

    clear_session_cache()


def test_remove_background_with_mock():
    img = Image.new("RGB", (50, 50), color=(255, 0, 0))
    expected_output = Image.new("RGBA", (50, 50), color=(255, 0, 0, 0))

    mock_session = MagicMock()
    with patch("rembg.remove", return_value=expected_output) as mock_rembg_remove:
        result = remove_background(img, session=mock_session)
        assert result is not None
        assert result.mode == "RGBA"
        assert result.size == (50, 50)
        mock_rembg_remove.assert_called_once_with(img, session=mock_session)


def test_remove_background_invalid_input():
    with pytest.raises(ValueError):
        remove_background(None)

    with pytest.raises(TypeError):
        remove_background("not an image")


def test_worker_lifecycle_success(qapp):
    img = Image.new("RGB", (30, 30), color=(0, 255, 0))
    expected_output = Image.new("RGBA", (30, 30), color=(0, 255, 0, 128))

    worker = BackgroundRemovalWorker(image=img, model_name="test-model")

    started_events = []
    status_events = []
    finished_events = []
    error_events = []

    worker.started_processing.connect(lambda: started_events.append(True))
    worker.status_changed.connect(lambda msg: status_events.append(msg))
    worker.finished.connect(lambda res: finished_events.append(res))
    worker.error.connect(lambda err: error_events.append(err))

    mock_session = MagicMock()
    with patch("snippit.processing.background_removal.get_session", return_value=mock_session), \
         patch("snippit.processing.background_removal.remove_background", return_value=expected_output):
        worker.start()
        worker.wait(3000)
        qapp.processEvents()

    assert len(started_events) == 1
    assert len(status_events) >= 1
    assert len(finished_events) == 1
    assert len(error_events) == 0
    assert finished_events[0].size == (30, 30)


def test_worker_lifecycle_error(qapp):
    img = Image.new("RGB", (30, 30), color=(0, 0, 255))
    worker = BackgroundRemovalWorker(image=img, model_name="error-model")

    started_events = []
    error_events = []
    finished_events = []

    worker.started_processing.connect(lambda: started_events.append(True))
    worker.finished.connect(lambda res: finished_events.append(res))
    worker.error.connect(lambda err: error_events.append(err))

    with patch("snippit.processing.background_removal.get_session", side_effect=RuntimeError("Download failed")):
        worker.start()
        worker.wait(3000)
        qapp.processEvents()

    assert len(started_events) == 1
    assert len(finished_events) == 0
    assert len(error_events) == 1
    assert "Download failed" in error_events[0]


def test_worker_cancel(qapp):
    img = Image.new("RGB", (20, 20), color=(100, 100, 100))
    worker = BackgroundRemovalWorker(image=img)
    worker.cancel()

    finished_events = []
    worker.finished.connect(lambda res: finished_events.append(res))

    worker.start()
    worker.wait(1000)
    qapp.processEvents()

    assert len(finished_events) == 0

"""Unit tests for pure helpers in clipper.py."""

import pytest

from clipper import ProcessingError, compute_crop_box, sanitize_timecodes


def test_sanitize_timecodes_clamps_boundaries() -> None:
    start, end = sanitize_timecodes(-5.0, 120.0, duration=100.0)
    assert start == 0.0
    assert end == 100.0


def test_sanitize_timecodes_rejects_invalid_windows() -> None:
    with pytest.raises(ProcessingError):
        sanitize_timecodes(10.0, 10.1, duration=10.0)


def test_compute_crop_box_center_crop_landscape_to_vertical() -> None:
    crop_box = compute_crop_box(1920, 1080, 1080, 1920)
    assert crop_box.width == 608
    assert crop_box.height == 1080
    assert crop_box.x1 == 656
    assert crop_box.y1 == 0


def test_compute_crop_box_returns_full_frame_when_already_matching() -> None:
    crop_box = compute_crop_box(1080, 1920, 1080, 1920)
    assert crop_box.x1 == 0
    assert crop_box.y1 == 0
    assert crop_box.width == 1080
    assert crop_box.height == 1920

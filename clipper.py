"""Core video processing utilities for the Video Clipper app."""
from __future__ import annotations

import contextlib
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import yt_dlp
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop as vfx_crop


class ClipperError(Exception):
    """Base error for the clipper module."""


class DownloadError(ClipperError):
    """Raised when a YouTube download fails."""


class ProcessingError(ClipperError):
    """Raised when video processing fails."""


@dataclass
class DownloadResult:
    """Metadata returned after a successful download."""

    path: Path
    title: str
    duration: Optional[float]
    thumbnail: Optional[str]


@dataclass
class CropBox:
    """Axis-aligned crop rectangle."""

    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1


ProgressCallback = Callable[[float, Dict[str, Any]], None]


def download_video(
    url: str,
    output_dir: str | Path,
    progress_callback: Optional[ProgressCallback] = None,
) -> DownloadResult:
    """Download a YouTube video as MP4 using yt-dlp.

    Parameters
    ----------
    url:
        Public YouTube URL.
    output_dir:
        Directory where the resulting file should be stored.
    progress_callback:
        Optional callable receiving (progress, yt_dlp_dict) where progress is 0-1.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    def _hook(status: Dict[str, Any]) -> None:
        if not progress_callback:
            return
        if status.get("status") == "downloading":
            total = status.get("total_bytes") or status.get("total_bytes_estimate") or 0
            downloaded = status.get("downloaded_bytes", 0)
            progress = downloaded / total if total else 0.0
            progress_callback(max(0.0, min(progress, 1.0)), status)
        elif status.get("status") == "finished":
            progress_callback(1.0, status)

    ydl_opts = {
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "progress_hooks": [_hook] if progress_callback else [],
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as exc:  # pragma: no cover - passthrough for yt-dlp errors
        raise DownloadError(str(exc)) from exc

    filepath = Path(info.get("_filename") or ydl.prepare_filename(info))
    if filepath.suffix != ".mp4" and info.get("ext"):
        filepath = filepath.with_suffix(f".{info['ext']}")

    return DownloadResult(
        path=filepath,
        title=info.get("title", filepath.stem),
        duration=info.get("duration"),
        thumbnail=info.get("thumbnail"),
    )


def get_video_metadata(path: str | Path) -> Dict[str, Any]:
    """Return inexpensive metadata (duration, size) for a local video file."""

    path = Path(path)
    if not path.exists():
        raise ProcessingError(f"Video not found at {path}")

    try:
        with VideoFileClip(str(path)) as clip:
            return {
                "duration": float(clip.duration or 0.0),
                "fps": float(clip.fps) if clip.fps else None,
                "width": int(clip.w),
                "height": int(clip.h),
                "filesize": path.stat().st_size,
            }
    except OSError as exc:  # pragma: no cover - moviepy raises OSError for decoding issues
        raise ProcessingError(f"Unable to read video metadata: {exc}") from exc


def sanitize_timecodes(start: float, end: float, duration: float, min_length: float = 0.5) -> Tuple[float, float]:
    """Clamp and validate requested start/end timestamps."""

    if duration <= 0:
        raise ProcessingError("Video duration is zero.")

    start = max(0.0, float(start))
    end = min(float(end), float(duration))

    if end - start < min_length:
        raise ProcessingError("Clip selection is too short. Increase the end time.")

    if start >= duration:
        raise ProcessingError("Start time falls outside the video.")

    if end <= start:
        raise ProcessingError("End time must be greater than start time.")

    return round(start, 3), round(end, 3)


def compute_crop_box(width: int, height: int, target_width: int, target_height: int) -> CropBox:
    """Calculate centered crop box preserving as much content as possible."""

    if width <= 0 or height <= 0 or target_width <= 0 or target_height <= 0:
        raise ProcessingError("Invalid dimensions for crop computation.")

    src_ratio = width / height
    dest_ratio = target_width / target_height

    if math.isclose(src_ratio, dest_ratio, rel_tol=1e-03):
        return CropBox(0, 0, width, height)

    if src_ratio > dest_ratio:
        new_width = int(round(height * dest_ratio))
        offset_x = (width - new_width) // 2
        return CropBox(offset_x, 0, offset_x + new_width, height)

    new_height = int(round(width / dest_ratio))
    offset_y = (height - new_height) // 2
    return CropBox(0, offset_y, width, offset_y + new_height)


def _apply_vertical_transform(clip: VideoFileClip, resolution: Tuple[int, int]) -> VideoFileClip:
    """Crop and resize the clip to the target vertical resolution."""

    target_width, target_height = resolution
    crop_box = compute_crop_box(clip.w, clip.h, target_width, target_height)

    if crop_box.width != clip.w or crop_box.height != clip.h:
        clip = clip.fx(
            vfx_crop,
            x1=crop_box.x1,
            y1=crop_box.y1,
            x2=crop_box.x2,
            y2=crop_box.y2,
        )

    return clip.resize(newsize=resolution)


def export_vertical_clip(
    source: str | Path,
    start: float,
    end: float,
    output_dir: str | Path,
    resolution: Tuple[int, int] = (1080, 1920),
    preset: str = "medium",
    audio_bitrate: str = "128k",
) -> Path:
    """Trim, crop, and export a vertical clip suitable for shorts."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = get_video_metadata(source)
    trimmed_start, trimmed_end = sanitize_timecodes(start, end, metadata["duration"])

    with VideoFileClip(str(source)) as clip:
        subclip = clip.subclip(trimmed_start, trimmed_end)
        processed = _apply_vertical_transform(subclip, resolution)

        fps = processed.fps or clip.fps or 30
        filename = f"short_{Path(source).stem}_{int(trimmed_start)}_{int(trimmed_end)}.mp4"
        output_path = output_dir / filename

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a")
        temp_audio.close()

        try:
            processed.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                audio_bitrate=audio_bitrate,
                fps=fps,
                preset=preset,
                threads=min(4, os.cpu_count() or 1),
                temp_audiofile=temp_audio.name,
                remove_temp=True,
                verbose=False,
                logger=None,
            )
        except Exception as exc:  # pragma: no cover - moviepy internal errors bubble up
            raise ProcessingError(f"Unable to export clip: {exc}") from exc
        finally:
            with contextlib.suppress(Exception):
                processed.close()
            with contextlib.suppress(Exception):
                subclip.close()
            with contextlib.suppress(FileNotFoundError):
                Path(temp_audio.name).unlink()

    return output_path


__all__ = [
    "ClipperError",
    "DownloadError",
    "ProcessingError",
    "DownloadResult",
    "CropBox",
    "download_video",
    "get_video_metadata",
    "sanitize_timecodes",
    "compute_crop_box",
    "export_vertical_clip",
]

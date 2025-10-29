"""Streamlit front-end for the Video Clipper application."""
from __future__ import annotations

import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Optional, Tuple

import streamlit as st

from clipper import (
    DownloadError,
    ProcessingError,
    download_video,
    export_vertical_clip,
    get_video_metadata,
)

APP_ROOT = Path(__file__).parent
OUTPUT_DIR = APP_ROOT / "outputs"
UPLOAD_DIR = APP_ROOT / "uploads"
CACHE_DIR = APP_ROOT / "cache"
MEDIA_DIR = APP_ROOT / "media"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _format_bytes(num: int) -> str:
    step = 1024.0
    for unit in ["B", "KB", "MB", "GB"]:
        if num < step:
            return f"{num:.1f} {unit}"
        num /= step
    return f"{num:.1f} TB"


def _format_duration(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def _rerun() -> None:
    try:
        st.rerun()
    except AttributeError:  # pragma: no cover - fallback for older Streamlit
        st.experimental_rerun()


def _inject_theme_css() -> None:
    st.markdown(
        """
        <style>
            body.theme-light {
                background-color: #FFFFFF;
                color: #111111;
            }
            body.theme-dark {
                background-color: #050505;
                color: #FFFFFF;
            }
            .stApp {
                max-width: 1100px;
                margin: 0 auto;
                padding-bottom: 3rem;
            }
            .vc-frame {
                background: linear-gradient(135deg, rgba(0,0,0,0.04), rgba(0,0,0,0.02));
                padding: 24px;
                border-radius: 24px;
                box-shadow: 10px 10px 20px rgba(0,0,0,0.15), -10px -10px 20px rgba(255,255,255,0.6);
            }
            body.theme-dark .vc-frame {
                background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
                box-shadow: 10px 10px 22px rgba(0,0,0,0.45), -10px -10px 22px rgba(255,255,255,0.08);
            }
            .vc-inline-field > div {
                display: flex;
                gap: 12px;
                align-items: center;
            }
            .vc-badge {
                background-color: #F5F5F5;
                color: #111111;
                border-radius: 999px;
                padding: 4px 12px;
                font-size: 0.8rem;
                font-weight: 500;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }
            body.theme-dark .vc-badge {
                background-color: #111111;
                color: #FFFFFF;
            }
            .vc-section-title {
                font-size: 1.4rem;
                font-weight: 600;
                margin-bottom: 8px;
            }
            .stButton>button {
                border-radius: 16px;
                border: 1px solid #E0E0E0;
                background: #F5F5F5;
                color: #111111;
                padding: 0.6rem 1.2rem;
                font-weight: 600;
                transition: transform 120ms ease-in-out;
            }
            .stButton>button:hover {
                transform: translateY(-2px);
            }
            body.theme-dark .stButton>button {
                border: 1px solid #2A2A2A;
                background: #111111;
                color: #FFFFFF;
            }
            .stDownloadButton>button {
                background: #111111;
                color: #FFFFFF;
            }
            body.theme-dark .stDownloadButton>button {
                background: #FFFFFF;
                color: #111111;
            }
            .stSlider > div:nth-child(2) > div {
                background: #E0E0E0;
                border-radius: 999px;
                height: 6px;
            }
            body.theme-dark .stSlider > div:nth-child(2) > div {
                background: #2A2A2A;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def _neuromorphic_card():
    st.markdown("<div class='vc-frame'>", unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _get_demo_options() -> Dict[str, Path]:
    options: Dict[str, Path] = {}
    for file in MEDIA_DIR.glob("*.mp4"):
        options[file.stem.replace("_", " ").title()] = file
    return options


def _set_theme(mode: str) -> None:
    st.markdown(
        f"""
        <script>
        const body = window.parent.document.body;
        body.classList.remove('theme-light', 'theme-dark');
        body.classList.add('theme-{mode}');
        </script>
        """,
        unsafe_allow_html=True,
    )


def _persist_upload(upload) -> Optional[Path]:
    if upload is None:
        return None
    suffix = Path(upload.name).suffix or ".mp4"
    destination = UPLOAD_DIR / f"upload_{uuid.uuid4().hex[:8]}{suffix}"
    with open(destination, "wb") as target:
        target.write(upload.getbuffer())
    return destination


def _reset_generated_clip() -> None:
    st.session_state.pop("generated_clip", None)


def _update_source(path: Path, label: str) -> None:
    metadata = get_video_metadata(path)
    st.session_state["source_path"] = str(path)
    st.session_state["source_title"] = label
    st.session_state["source_metadata"] = metadata
    duration = float(metadata.get("duration", 0.0) or 0.0)
    if duration <= 0.0:
        st.session_state["clip_range"] = (0.0, 0.5)
    else:
        default_end = min(duration, 30.0)
        if duration >= 0.7 and default_end < 0.7:
            default_end = min(duration, 0.7)
        if duration >= 0.5 and default_end < 0.5:
            default_end = 0.5
        st.session_state["clip_range"] = (0.0, min(duration, default_end))
    _reset_generated_clip()


st.set_page_config(page_title="Video Clipper", layout="wide", page_icon="🎬")
_inject_theme_css()

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"
_set_theme(st.session_state["theme_mode"])

with st.sidebar:
    st.markdown("**Display**")
    theme_selected = st.toggle("Dark mode", value=st.session_state["theme_mode"] == "dark")
    st.session_state["theme_mode"] = "dark" if theme_selected else "light"
    _set_theme(st.session_state["theme_mode"])

    st.markdown("---")
    st.markdown("**Video Source**")
    demo_options = _get_demo_options()
    if demo_options:
        demo_choice = st.selectbox("Demo video", ["None"] + list(demo_options.keys()), index=0)
        if demo_choice != "None":
            _update_source(demo_options[demo_choice], demo_choice)

    current_source = st.session_state.get("source_path")
    if current_source:
        metadata = st.session_state.get("source_metadata", {})
        st.markdown(f"**Loaded:** {st.session_state.get('source_title', Path(current_source).name)}")
        if metadata:
            duration_text = _format_duration(metadata.get("duration", 0.0)) if metadata.get("duration") else "–"
            resolution_text = f"{metadata.get('width', '–')}×{metadata.get('height', '–')}"
            size_text = _format_bytes(int(metadata.get("filesize", 0))) if metadata.get("filesize") else "–"
            st.caption(f"Duration {duration_text} • \n{resolution_text} • {size_text}")
        if st.button("Clear source", use_container_width=True):
            st.session_state.pop("source_path", None)
            st.session_state.pop("source_metadata", None)
            st.session_state.pop("source_title", None)
            _reset_generated_clip()
            _rerun()

st.title("Video Clipper")
st.caption("Turn long-form videos into ready-to-share Shorts in minutes.")

upload_col, url_col = st.columns(2)
with upload_col:
    st.markdown("<div class='vc-section-title'>Upload video</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=("mp4", "mov", "mkv", "avi"), label_visibility="collapsed")
    if uploaded:
        path = _persist_upload(uploaded)
        if path:
            _update_source(path, "Local upload")
            st.success("Upload saved. Preview ready below.")

with url_col:
    st.markdown("<div class='vc-section-title'>YouTube URL</div>", unsafe_allow_html=True)
    yt_url = st.text_input("Paste a YouTube link", placeholder="https://www.youtube.com/watch?v=...")
    if st.button("Download", use_container_width=True, disabled=not yt_url.strip()):
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        def progress_hook(progress: float, details: Dict[str, object]) -> None:
            progress_placeholder.progress(progress)
            if details.get("status") == "finished":
                status_placeholder.success("Download complete.")
            elif details.get("status") == "downloading":
                downloaded = details.get("downloaded_bytes", 0)
                total = details.get("total_bytes") or details.get("total_bytes_estimate") or 1
                percent = progress * 100
                status_placeholder.info(f"Downloading… {percent:0.1f}% ({_format_bytes(int(downloaded))})")

        try:
            result = download_video(yt_url.strip(), CACHE_DIR, progress_hook)
        except DownloadError as exc:
            progress_placeholder.empty()
            status_placeholder.error(f"Download failed: {exc}")
        else:
            progress_placeholder.empty()
            if result.path.exists():
                destination = CACHE_DIR / result.path.name
                if result.path.resolve() != destination.resolve():
                    shutil.move(str(result.path), destination)
                _update_source(destination, result.title)
                status_placeholder.success("Video ready for clipping.")
            else:
                status_placeholder.error("The downloaded file was not found.")

st.markdown("---")

source_path = st.session_state.get("source_path")
if not source_path:
    st.info("Upload a video or provide a YouTube URL to start.")
    st.stop()

metadata = st.session_state.get("source_metadata") or get_video_metadata(source_path)
st.session_state["source_metadata"] = metadata

preview_col, controls_col = st.columns([3, 2])

with preview_col:
    with _neuromorphic_card():
        st.markdown("<div class='vc-section-title'>Preview</div>", unsafe_allow_html=True)
        st.video(source_path)
        st.caption("Original aspect ratio. Export will adapt to 9:16 vertical format.")

with controls_col:
    with _neuromorphic_card():
        st.markdown("<div class='vc-section-title'>Clip settings</div>", unsafe_allow_html=True)
        duration = metadata.get("duration", 0.0) or 0.0
        if duration <= 0.1:
            st.error("Could not read video duration. Try another file.")
            st.stop()

        default_end = min(duration, 30.0)
        if "clip_range" not in st.session_state or st.session_state["clip_range"][1] > duration:
            st.session_state["clip_range"] = (0.0, default_end)

        clip_range: Tuple[float, float] = st.slider(
            "Select clip range",
            min_value=0.0,
            max_value=float(duration),
            value=st.session_state["clip_range"],
            step=0.1,
            format="%.1f s",
        )
        st.session_state["clip_range"] = clip_range

        quality = st.select_slider(
            "Export preset",
            options=["fast", "medium", "slow"],
            value=st.session_state.get("quality", "medium"),
        )
        st.session_state["quality"] = quality

        if st.button("Generate vertical short", use_container_width=True):
            with st.spinner("Processing clip…"):
                try:
                    clip_path = export_vertical_clip(
                        source_path,
                        clip_range[0],
                        clip_range[1],
                        OUTPUT_DIR,
                        preset=quality,
                    )
                except ProcessingError as exc:
                    st.error(f"Processing failed: {exc}")
                else:
                    st.session_state["generated_clip"] = str(clip_path)
                    st.success("Export complete. Preview below.")

generated_clip = st.session_state.get("generated_clip")
if generated_clip:
    st.markdown("---")
    with _neuromorphic_card():
        st.markdown("<div class='vc-section-title'>Exported short</div>", unsafe_allow_html=True)
        st.video(generated_clip)
        clip_path = Path(generated_clip)
        with open(clip_path, "rb") as file:
            st.download_button(
                label="Download MP4",
                data=file.read(),
                file_name=clip_path.name,
                mime="video/mp4",
            )
        st.caption(f"Saved to {clip_path.relative_to(APP_ROOT)}")

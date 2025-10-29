# Project Context

## Overview
- **Product**: Video Clipper — a Streamlit-based toolkit that downloads a YouTube video, trims it into short-form clips, and reformats for YouTube Shorts delivery.
- **Primary Users**: Creators who want a quick way to turn long-form videos into vertical shorts.
- **Core Modules**:
  - `app.py`: Streamlit UI layer for URL input, trimming controls, preview, and export.
  - `clipper.py` (to be created): Backend transformations (download via `yt-dlp`, trimming, aspect-ratio adjustments, overlays, subtitles).
  - `auth.py` (existing): Placeholder for optional auth/back-end integrations.
  - `media/`: Demo assets for offline workflows.

## Feature Expectations
1. Download videos from YouTube using `yt-dlp` with configurable options.
2. Provide trimming controls (start/end timestamps) and resizing to vertical 9:16.
3. Offer presets for overlays, captions, and export quality.
4. Allow preview of resulting short and export to `outputs/` with quick download.
5. Run through Streamlit front end with responsive feedback while heavy processing happens server-side.

## UI & Theme
- Adopt the **white-black neuromorphic** theme detailed in `theme.md`.
- Default (light) mode: white backgrounds with soft black/graphite accents; components use subtle inset embossing, no glow effects.
- Dark mode: invert to black backgrounds and white/elevated surfaces while preserving neumorphic depth cues.
- Streamlit components should be styled (via `theme.base` config and custom CSS) to respect this design language.

## Implementation Plan
1. **Environment**: Provide `requirements.txt` matching Streamlit, yt-dlp, moviepy, OpenCV, Pillow, NumPy. Consider Dockerfile for reproducibility.
2. **Backend Logic (`clipper.py`)**:
   - Wrap `yt-dlp` for download with progress callbacks.
   - Use MoviePy/OpenCV to trim, crop, resize, and optionally overlay captions.
   - Provide reusable helper functions for future automation/tests.
3. **Frontend (`app.py`)**:
   - Single-page Streamlit app.
   - URL input, fallback to local demo video, controls for start/end durations, style presets, and export.
   - Integrate theme, show previews, and display export status.
4. **Media Handling**: Ensure sample content lives in `media/`. Export results to `outputs/` with naming convention.
5. **Testing/Validation**: Unit tests around clip segmentation and aspect ratio conversions. Spot-check front end manually via Streamlit.
6. **Documentation**: Keep README updated, add usage notes for Docker and local dev. Reference `theme.md` for styling decisions.

## Guidelines for AI Code Editors
- Keep heavy processing off the UI thread; use background tasks or caching where Streamlit allows.
- Follow `theme.md` styling rules; do not introduce glow or gradient-heavy effects.
- Maintain separation between UI (Streamlit) and processing logic (`clipper.py` or utilities).
- When adding new assets, keep filenames descriptive and update documentation.
- Prefer modular, testable functions; avoid hard-coded paths outside `media/` and `outputs/`.
- Update tests or add new ones when altering trim/resize logic.

## Outstanding TODOs
- Scaffold `clipper.py` with core download/trim pipeline.
- Add Streamlit theme configuration and CSS injection per `theme.md`.
- Create Dockerfile aligning with README instructions.
- Seed unit tests for core video utilities.
- Add license and contribution guidelines once project stabilizes.

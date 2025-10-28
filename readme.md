# Video Clipper — YouTube downloader → engaging Shorts

A minimal toolkit to download YouTube videos, auto-clip and reformat them into engaging YouTube Shorts. Designed for quick demos and iterative development (Docker + Streamlit UI).

## Features
- Download YouTube videos (configurable back-end: yt-dlp)
- Trim and reformat to vertical shorts (crop, resize, subtitle overlay)
- Simple Streamlit UI for quick clip creation and preview
- Docker-ready for reproducible environments
- Repo seeded with a demo video and images in `media/`

## Repo layout (suggested)
- app.py                — Streamlit frontend
- clipper.py            — core clip/transform logic
- requirements.txt
- Dockerfile
- images/
    - demo.mp4
    - thumbnail.jpg
    - overlays/
- README.md

## Quick start (local)
1. Clone the repo.
2. Create a virtual environment and install:
     pip install -r requirements.txt
3. Run the Streamlit UI:
     streamlit run app.py
4. In the UI: paste a YouTube URL, choose start/end, select style, generate and preview the short.

## Quick start (Docker)
Build:
docker build -t video-clipper .
Run (dev):
docker run --rm -p 8501:8501 -v "$(pwd)/images:/app/images" video-clipper

Then open http://localhost:8501

## Streamlit UI (notes)
- Minimal single-page app for URL input, trimming controls, and style presets.
- Provide upload/fallback to the `images/demo.mp4` for offline demos.
- Expose an export button that saves result to `outputs/` and shows a download link.

## requirements.txt (example)
```text
streamlit==1.24.1
yt-dlp==2024.06.01
moviepy==1.0.3
opencv-python-headless==4.8.0.76
numpy==1.26.2
Pillow==10.1.0
```

Adjust versions to your environment.

## Development tips
- Keep heavy processing in worker functions (clipper.py) so the UI stays responsive.
- Add automated tests for trimming logic and aspect-ratio conversions.
- Version the Docker image and tag releases for reproducibility.

## Demo content
- Place a short sample video at `images/demo.mp4` and thumbnails in `images/` to allow a standalone demo without network access.

## Contributing
- Open issues for feature requests/bugs.
- Use branches and semantic tags for releases.

## License
Choose an appropriate license (e.g., MIT) and add a LICENSE file.

That's it — scaffold the files above, add your Streamlit UI and clipper logic, and use Docker for a reproducible demo environment.
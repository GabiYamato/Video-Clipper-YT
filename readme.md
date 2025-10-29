# Video Clipper — YouTube downloader → engaging Shorts

Video Clipper is a Streamlit-based toolkit that downloads long-form YouTube content (or local files) and turns the most relevant moments into 9:16-ready shorts. The UI stays focused on a single workflow while the heavy lifting happens inside `clipper.py`.

## Features
- Download YouTube videos with `yt-dlp` and track progress inside the app
- Trim any portion of the source video and convert it to a vertical 9:16 frame
- Neuromorphic-themed Streamlit UI with light/dark toggle matching `theme.md`
- Automatic output naming and download links for the rendered short clips
- Unit tests covering trim-window clamping and crop math for regressions

## Repo layout
- `app.py` — Streamlit front end
- `clipper.py` — video download, trimming, and vertical formatting helpers
- `.streamlit/config.toml` — base theme definition
- `requirements.txt` — runtime and dev dependencies
- `media/` — optional demo assets (empty by default)
- `outputs/` — generated shorts (created at runtime)
- `uploads/` — persisted local uploads (gitignored)
- `cache/` — temporary downloads from YouTube (gitignored)
- `tests/` — pytest suite for helper logic

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

1. Upload a video or paste a YouTube URL.
2. Adjust the start and end markers (defaults to the first 30 seconds).
3. Pick an export preset and generate the vertical short.
4. Preview the result in the app or download the MP4 from the link provided.

## Tests
Run the helper tests (no video assets required):
```bash
pytest
```

## Next steps
- Add overlay presets (captions, brand frames) using MoviePy overlays.
- Extend `clipper.py` with batching and automation hooks for multiple shorts.
- Provide Dockerfile and deployment notes once the pipeline stabilises.

## Contributing
- Open issues for enhancements or bugs.
- Keep processing utilities in `clipper.py` and UI logic in `app.py` for clarity.
- Follow the white-black neuromorphic rules in `theme.md` when styling UI additions.

## License
Choose an appropriate license (e.g., MIT) and add a `LICENSE` file when ready.
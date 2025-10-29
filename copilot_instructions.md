# Copilot Working Notes

## Primary Goals
- Build a Streamlit-based workflow that downloads, trims, and reformats YouTube videos into vertical shorts.
- Keep UI code in `app.py` lean; move processing logic to helper modules (future `clipper.py`, utilities).
- Respect the white-black neuromorphism theme documented in `theme.md` with strict no-glow policy.

## Implementation Guidelines
- Follow the roadmap in `context.md`; update it if plans shift meaningfully.
- When adding UI, reference `theme.md` for color, typography, and elevation tokens; ensure both light/dark variants exist.
- Favor pure Python/Streamlit solutions first; only add dependencies when justified and update documentation.
- Use descriptive logging for long-running jobs (download, rendering) so Streamlit status updates stay informative.
- Extend or add tests when touching video trimming, aspect ratio, or export logic.

## Non-Goals / Cautions
- Do not introduce glow, neon, or saturated gradient effects.
- Avoid blocking operations on the Streamlit main thread; use async helpers or placeholders with progress updates.
- Keep demo assets lightweight and in `media/`; do not store large binaries in repo.
- Maintain high contrast and keyboard accessibility; never remove visible focus outlines.

See `context.md` for project overview and `theme.md` for design tokens before making UI or UX changes.

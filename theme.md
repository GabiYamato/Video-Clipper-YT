# Video Clipper Theme Spec

## Design Principles
- **White-Black Neuromorphism**: Surfaces simulate soft physical depth using light and shadow with high-contrast monochrome palette.
- **No Glow Effects**: Avoid drop shadows with blur halos, neon glows, or gradient glimmers. Depth relies on crisp highlights/shadows.
- **Minimalist**: Focus on legibility and clarity. Refrain from ornamental gradients or colorful accents unless communicating status (success/error).
- **Responsive & Accessible**: Components adapt to wide and narrow breakpoints; ensure text contrast meets WCAG AA.

## Color Palette
### Light Mode (default)
- **Base Background**: `#FFFFFF`
- **Elevated Surfaces**: `#F5F5F5`
- **Text Primary**: `#111111`
- **Text Secondary**: `#444444`
- **Divider/Borders**: `#E0E0E0`
- **Accent (status only)**: Success `#1DB954`, Warning `#FFB020`, Error `#E53935`

### Dark Mode
- **Base Background**: `#050505`
- **Elevated Surfaces**: `#111111`
- **Text Primary**: `#FFFFFF`
- **Text Secondary**: `#D0D0D0`
- **Divider/Borders**: `#2A2A2A`
- **Accent (status only)**: Success `#3DDC97`, Warning `#FFC857`, Error `#FF6F59`

## Neuromorphic Treatments
- **Elevation Style**: Use paired box-shadows with equal radius and opposite offsets to simulate extrusion/inset. Example (light mode):
  - `box-shadow: 6px 6px 12px rgba(0, 0, 0, 0.12), -6px -6px 12px rgba(255, 255, 255, 0.6);`
- **Inset Controls**: For inputs/sliders, invert the shadow direction with subtle inner shadow.
- **Dark Mode Adjustment**: Swap shadow colors for white/black pairings; reduce opacity to maintain subtlety.

## Typography
- **Primary Font**: `"Inter", "Segoe UI", sans-serif`
- **Weights**: 400 regular, 500 medium for labels, 600 for section titles.
- **Sizing**:
  - Headline: 24px
  - Section Label: 18px
  - Body: 16px
  - Caption/Hint: 14px
- **Letter Spacing**: Slight positive tracking (`0.01em`) on uppercase labels to reinforce modern aesthetic.

## Components
- **Buttons**: Rounded corners (12px radius). Raised buttons use elevation shadows; active state shifts to inset style. Disabled buttons reduce contrast by 40%.
- **Inputs**: Inset neuromorphic edges, consistent padding (`12px 16px`). Focus state uses thin solid border (`1px`) with accent color; no glow.
- **Cards/Panels**: Large padding (`24px`), soft elevation. In dark mode, lighten inner portion with subtle gradient from `#111111` to `#0C0C0C` (2-3% change only).
- **Sliders/Timeline**: Track with inset groove; thumb uses floating circular knob with dual shadow pair.
- **Modals/Popovers**: Centered, high elevation shadows, blur-free edges, optional border (`1px` semi-transparent) for separation.

## Layout & Spacing
- **Grid**: 8px baseline grid. Section spacing 32px. Align primary content in max-width 960px central column.
- **Navigation/Header**: Sticky top bar with subtle bottom border; support theme toggle.
- **Timeline Preview**: Use card with embedded video preview; maintain 9:16 frame with neutral placeholder background when empty.

## Streamlit Implementation Tips
- Configure `.streamlit/config.toml` with `theme.base="light"`, set primaries to palette above; use custom CSS via `st.markdown("<style>...</style>", unsafe_allow_html=True)`.
- Override default Streamlit box-shadows to match neuromorphic spec.
- Provide `.theme-dark` class toggled with session state to apply dark palette (mirror values above).
- Ensure widgets respect keyboard navigation and focus outlines (use `outline: 2px solid accent` on focus).

## Iconography & Media
- Use monochrome SVG icons with stroke width 1.5px, no fill gradients.
- For status indicators, use accent colors sparingly (small dots or thin bars).
- Thumbnail overlays should desaturate video stills behind UI controls to maintain contrast.

## Accessibility & Testing
- Verify contrast ratios: Light mode text on base >= 12.8:1 for primary, 7:1 for secondary. Dark mode similar checks.
- Provide high-contrast focus rings; do not rely solely on color for interactive states.
- Test both modes for aliasing on shadows; adjust blur radius between 8-12px as needed to avoid harsh edges.
- Ensure theme toggles persist using Streamlit session state.

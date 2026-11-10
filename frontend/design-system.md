# DocugraphAI Retro-Futurism Design System

## 1. Brand Palette (60 / 30 / 10 Rule)
All colors are defined exclusively as CSS custom properties in `src/index.css` under `:root` and mapped in `tailwind.config.ts`. Hardcoded hex values in components are strictly prohibited.

| Role | Token | CSS Variable | Value | Usage |
|---|---|---|---|---|
| **Primary (60%)** | `primary` | `--color-primary` | `#8DB9F0` | Powder Blue — washes, structural highlights, dark-mode mono accents |
| **Secondary (30%)** | `secondary` | `--color-secondary` | `#E9E8F8` | Soft Lavender — primary canvas, card surfaces, logo plate on dark |
| **Accent (10%)** | `accent` | `--color-accent` | `#F5B69E` | Warm Sunset — CTAs, active route indicators, terminal tags |
| **Primary Ink** | `ink` | `--color-ink` | `#101828` | Charcoal Blue — primary typography, borders, dark footer surface |
| **Secondary Ink** | `ink-secondary` | `--color-ink-secondary` | `#2C3E50` | Secondary body copy and muted structural labels |
| **Light Ink** | `ink-light` | `--color-ink-light` | `#E9E8F8` | Lavender white — headings and copy on `--color-ink` surfaces |

### Contrast Guardrails
- Never render white text directly on `--color-primary` (`#8DB9F0`) or `--color-accent` (`#F5B69E`). Always pair those surfaces with `--color-ink` (`#101828`).
- On `--color-ink` (`#101828`) surfaces, use `--color-ink-light` (`#E9E8F8`), `--color-primary` (`#8DB9F0`), or `--color-accent` (`#F5B69E`).

## 2. Typography & Modular Scale (1.25 Ratio)
- **Headings (`--font-heading`)**: `'Space Grotesk', sans-serif` — tight tracking (`-0.02em` to `-0.04em`).
- **Body (`--font-body`)**: `'Inter', sans-serif` — tracking `0`.
- **Technical / Monospace (`--font-mono`)**: `'JetBrains Mono', monospace` — tracking `0.02em`.
- **Scale**:
  - `H1`: `3.5rem` desktop / `2.5rem` mobile
  - `H2`: `2.5rem` desktop / `2.0rem` mobile
  - `H3`: `1.75rem` desktop / `1.5rem` mobile
  - `Body`: `1rem`
  - `Small`: `0.875rem`
  - `Terminal`: `0.75rem`

## 3. Geometry, Spacing & Layout
- **Grid**: 12-column CSS Grid (`.grid-12`), `24px` column gutter, `16px` card gap.
- **Max Widths**: `1200px` (`max-w-landing`) for marketing/legal pages; `960px` (`max-w-auth`) for `/login`.
- **Section Padding**: `80px` vertical desktop (`py-section-desktop`), `48px` mobile (`py-section-mobile`).
- **Card Padding**: `32px` (`p-card`).
- **Border Radii**:
  - Primary containers: `0px` (`--radius-sharp` / `rounded-sharp`)
  - Cards: `8px` (`--radius-card` / `rounded-card`)
  - Buttons & tags: `4px` (`--radius-button` / `rounded-button`)
  - Never use `9999px` pill shapes or drop shadows on cards.

## 4. Atmospheric Surfaces & Retro-Futuristic Accents
- **Directional Washes**: `.wash-atmospheric-135`, `.wash-atmospheric-225`, `.wash-atmospheric-180` — slow `8s–9s` ambient shifts; horizontal `90deg` gradients are forbidden.
- **Analog Grain**: `.grain-surface::after` applies a fixed `2.5%` opacity SVG fractal-noise overlay across the viewport.
- **Glassmorphism**: `.glass-panel` (`backdrop-filter: blur(12px)`, `rgba(233, 232, 248, 0.6)`, `1px solid rgba(141, 185, 240, 0.3)`), reserved strictly for sticky navigation and floating cards.
- **Scan Lines**: `.scanlines-dark` and `.scanlines-light` render `1px` horizontal lines every `24px` at `0.03` opacity.
- **Motion Safety**: All keyframe animations and transitions are disabled under `@media (prefers-reduced-motion: reduce)`.

## 5. Frozen Shared Components
- **`<Nav />`**: Sticky header with transparent-to-glass scroll transition, official Goodlad Twinstars SVG logo (`36px` desktop, `30px` mobile), links (`/#product`, `/#enterprise`, `/pricing`, `Docs` coming-soon), and `Request org access` CTA (`/login#request-access`). Frozen after Prompt 1.
- **`<Footer />`**: Dark ink (`--color-ink`) surface with scanlines, `28px` logo inside a `--color-secondary` plate (`8px` padding, `4px` radius), monospace engine descriptor, 5 route links with `aria-current="page"`, copyright notice, and `1px` Peach bottom border at `0.3` opacity. Frozen after Prompt 1.
- **`<Button />`**: `primary` (Peach fill, Ink text, `4px` radius, hover glow) and `secondary` (transparent fill, `1px` Ink border, Ink text, `4px` radius).
- **`<TerminalLabel />`**: Monospace `0.75rem` tag in `--color-accent` on `--color-ink` pill container with square status indicator.
- **`<Divider />`**: Architectural rule with center geometric diamond-crosshair SVG node.
# Design System — AgriSight

## Product Context
- **What this is:** Conflict-aware food security monitoring platform. Fuses satellite NDVI, ACLED conflict events, UNHCR displacement flows, and CHIRPS rainfall into district-level IPC risk reports.
- **Who it's for:** Food security analysts at INGOs (IRC, NRC, Mercy Corps) and UN country offices (WFP, FAO), producing monthly IPC early-warning reports for eastern DRC conflict zones.
- **Space/industry:** Humanitarian tech, satellite remote sensing, food security monitoring.
- **Project type:** Data-dense web app — map views, analytics dashboards, alert feeds, report generation. No consumer audiences.
- **Reference:** HungerMap LIVE (WFP), FEWS NET, IPC-CH Dashboard — all use white backgrounds, UN blue, generic sans. AgriSight deliberately does not.

## Aesthetic Direction
- **Direction:** Industrial/Utilitarian — precision instrument
- **Decoration level:** Minimal (typography and spatial rhythm do all the work)
- **Mood:** A weather station or aircraft navigation display — every pixel earns its place, data is the content, chrome recedes. Authoritative without being heavy. Built for analysts who work at 2am under deadline.
- **Dark-first rationale:** Satellite imagery and choropleth maps read better on dark backgrounds. Maps glow rather than floating in a white void. Analysts working in field contexts with poor lighting benefit from low-emission screens. Every competitor defaults to white — this is the deliberate departure.

## Typography

- **Display/Headers:** [Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans) (weight 700–800) — humanist sans with strong character, not overused in the NGO/humanitarian space. Used for section titles, district names in reports, page headers.
- **Body/UI Labels:** [DM Sans](https://fonts.google.com/specimen/DM+Sans) (weight 400–600) — clean, slightly geometric, readable. Used for all prose, form labels, nav items, descriptions.
- **Data/Metrics:** [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) (weight 400–500, tabular-nums) — all numeric data. NDVI values, conflict event counts, IPC scores, timestamps, coordinates. Renders as an instrument reading, not a typed label.
- **Code:** JetBrains Mono
- **Loading:** Google Fonts CDN
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  ```

**Type scale:**

| Level | Font | Size | Weight | Use |
|-------|------|------|--------|-----|
| Display | Plus Jakarta Sans | 36px | 800 | Report title, landing hero |
| H1 | Plus Jakarta Sans | 24px | 700 | Page headers |
| H2 | Plus Jakarta Sans | 18px | 700 | Section headers |
| H3 | Plus Jakarta Sans | 14px | 600 | Card titles, table headers (text) |
| Body | DM Sans | 14px | 400 | Prose, descriptions |
| Label | DM Sans | 12px | 500 | Form labels, nav |
| Caption | DM Sans | 11px | 400 | Metadata, timestamps |
| Data-lg | JetBrains Mono | 26–32px | 500 | Stat card values |
| Data-md | JetBrains Mono | 14px | 400 | Table data cells |
| Data-sm | JetBrains Mono | 11–12px | 400 | Badges, small metrics |

**Font blacklist:** Never use Inter, Roboto, Arial, Helvetica, Open Sans, Lato, Montserrat, or Poppins as primary fonts. If a dependency forces one of these, override with the stack above.

## Color

- **Approach:** Restrained — two accents (green/amber), one danger (red), rest is neutral surface.
- **Background:** `#0d1117` — deep blue-gray, not pure black. The page base.
- **Surface:** `#161b22` — cards, panels, sidebars.
- **Surface elevated:** `#1c2128` — hover states, active items.
- **Border:** `#30363d` — dividers, card outlines.
- **Border muted:** `#21262d` — subtle separators in tables.
- **Text primary:** `#e6edf3` — all readable text on dark backgrounds.
- **Text muted:** `#7d8590` — labels, metadata, timestamps, placeholders.
- **Accent green (primary):** `#238636` — vegetation health, primary actions, NDVI positive signal. Light variant: `#3fb950`. Subtle bg: `#162a1d`.
- **Accent amber (conflict/warning):** `#d29922` — conflict density, warnings, data staleness, missing data. Light variant: `#e3b341`. Subtle bg: `#2d2000`.
- **Alert red:** `#f85149` — errors, critical alerts, high-severity events. Subtle bg: `#2d1117`.
- **Dark mode:** Default. Light mode is available via CSS custom properties but not the primary experience.

**Light mode overrides** (CSS `[data-theme="light"]`):
```css
--bg: #f6f8fa; --surface: #ffffff; --surface-2: #f0f2f5;
--border: #d0d7de; --text: #1f2328; --muted: #636c76;
--green: #1a7f37; --green-light: #1f883d; --green-subtle: #dafbe1;
--amber: #9a6700; --amber-subtle: #fef8c3;
--red: #d1242f; --red-subtle: #ffebe9;
```

### IPC Phase Colors — Semantic, Non-Negotiable

Analysts are trained globally on these colors. Do not change them. Do not use these colors for any other purpose.

| Phase | Label | Background | Text/Border | Usage |
|-------|-------|------------|-------------|-------|
| Phase 1 | Minimal | `#162a1d` | `#7bc47f` / `#2d5a1b` | Adequate food security |
| Phase 2 | Stressed | `#2d2000` | `#d4ab35` / `#8a6500` | Stressed but manageable |
| Phase 3 | Crisis | `#2d1500` | `#ef6c00` / `#8b3a0a` | Crisis — humanitarian response needed |
| Phase 4 | Emergency | `#2d1117` | `#ef5350` / `#8b0000` | Emergency — urgent action required |
| Phase 5 | Catastrophe | `#1a0030` | `#ce93d8` / `#4a0072` | Catastrophe / Famine |

**Critical:** Never use `#8b5cf6` (Tailwind violet-500) for conflict data. It collides with Phase 5 semantics. Use amber (`#d29922`) for conflict event density instead.

## Spacing
- **Base unit:** 8px
- **Density:** Comfortable — analysts need to read a lot at once, but not cramped.
- **Scale:**

| Token | Value | Use |
|-------|-------|-----|
| 2xs | 2px | Fine details, icon gaps |
| xs | 4px | Tight element gaps |
| sm | 8px | Base unit — default gap |
| md | 16px | Section padding, card padding |
| lg | 24px | Between major sections |
| xl | 32px | Page-level spacing |
| 2xl | 48px | Large section breaks |
| 3xl | 64px | Hero sections |

## Layout
- **Approach:** Hybrid — grid-disciplined for the app dashboard and map, editorial treatment only for the Landing page.
- **App shell:** Fixed sidebar nav (56px) + main content area. Topbar optional per view.
- **Dashboard grid:** 4-column stat card row → map + sidebar → data tables below.
- **Max content width:** 1200px (dashboard), unconstrained for full-screen map.
- **Border radius:** Low — 4px for inputs, cards, badges. 6–8px for larger containers. 9999px only for pill badges. Instruments don't have round corners.

## Motion
- **Approach:** Minimal-functional — only transitions that aid comprehension.
- **Easing:** enter → `ease-out` | exit → `ease-in` | move → `ease-in-out`
- **Duration:** micro (50–100ms) — icon states | short (150–200ms) — panel opens, badge changes | medium (250–350ms) — map layer transitions | avoid anything longer in the main UI.
- **No decorative animation.** No scroll-driven reveals, no loading skeletons with shimmer gradients, no entrance choreography on the dashboard.

## CSS Custom Properties

Paste into `frontend/src/index.css` after `@import "tailwindcss"`:

```css
:root {
  /* Surfaces */
  --bg:            #0d1117;
  --surface:       #161b22;
  --surface-2:     #1c2128;
  --border:        #30363d;
  --border-muted:  #21262d;

  /* Text */
  --text:          #e6edf3;
  --muted:         #7d8590;

  /* Accents */
  --green:         #238636;
  --green-light:   #3fb950;
  --green-subtle:  #162a1d;
  --amber:         #d29922;
  --amber-light:   #e3b341;
  --amber-subtle:  #2d2000;
  --red:           #f85149;
  --red-subtle:    #2d1117;
  --blue:          #388bfd;

  /* IPC phases */
  --ipc-1-bg:      #162a1d; --ipc-1-fg: #7bc47f;
  --ipc-2-bg:      #2d2000; --ipc-2-fg: #d4ab35;
  --ipc-3-bg:      #2d1500; --ipc-3-fg: #ef6c00;
  --ipc-4-bg:      #2d1117; --ipc-4-fg: #ef5350;
  --ipc-5-bg:      #1a0030; --ipc-5-fg: #ce93d8;

  /* Typography */
  --font-display:  'Plus Jakarta Sans', system-ui, sans-serif;
  --font-body:     'DM Sans', system-ui, sans-serif;
  --font-mono:     'JetBrains Mono', 'Courier New', monospace;
}
```

## Anti-patterns — Never Do These

- Purple (`#8b5cf6`, `#7c3aed`) for conflict data — it collides with Phase 5 IPC
- `#8884d8` (Recharts default purple) for any chart — replace with green/amber/blue
- 3-column feature grids with icons in colored circles
- Gradient buttons as the primary CTA
- Decorative blobs, gradient backgrounds, or radial glows
- Centered layouts for data-dense pages (charts and tables need left-anchored reading)
- Any font from the blacklist as primary

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Industrial/Utilitarian dark-first aesthetic | Every competitor (HungerMap, FEWS NET, IPC dashboard) uses white + UN blue. Dark backgrounds make satellite imagery and choropleth maps read better. Analysts work at night. |
| 2026-04-18 | Plus Jakarta Sans + DM Sans + JetBrains Mono | Tri-font stack: display authority (Jakarta Sans), readable UI (DM Sans), instrument-grade data (JetBrains Mono tabular-nums). Avoids the overused Inter/Roboto defaults. |
| 2026-04-18 | Amber (#d29922) for conflict density, not purple | Purple collides with IPC Phase 5 semantics. Amber reads as "warning/caution" and doesn't conflict with any IPC phase color. Removes current `#8b5cf6` from the codebase. |
| 2026-04-18 | IPC phase colors preserved exactly | These are a global semantic system. Analysts are trained on them. Changing them reduces utility, regardless of aesthetic preference. |
| 2026-04-18 | 4px border radius | Instruments don't have round corners. Low radius pairs with the industrial/precision aesthetic. |

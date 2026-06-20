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

- **Display/Headers:** [Fraunces](https://fonts.google.com/specimen/Fraunces) (weight 300–700, roman + italic) — a serif with editorial weight, deliberately not another humanist sans. Carries the wordmark, report titles, stat-card values, and the large decorative section numerals. Italic weight used for pull-quotes (`.thesis-text`).
- **Body/UI Labels:** [DM Sans](https://fonts.google.com/specimen/DM+Sans) (weight 300–500) — clean, slightly geometric, readable. Used for all prose, nav items, alert titles, descriptions.
- **Data/Metrics:** [Geist Mono](https://vercel.com/font) (weight 300–500, tabular-nums), falling back to JetBrains Mono — all numeric data, labels, and badges. NDVI values, conflict event counts, IPC scores, timestamps, coordinates. Renders as an instrument reading, not a typed label.
- **Code:** Geist Mono, falling back to JetBrains Mono
- **Loading:** Google Fonts CDN
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,300;1,9..144,400&family=DM+Sans:wght@300;400;500&family=Geist+Mono:wght@300;400;500&display=swap" rel="stylesheet">
  ```

**Type scale** (extracted from the live design preview, `agrisight-design-preview.html`):

| Level | Font | Size | Weight | Use |
|-------|------|------|--------|-----|
| Display-lg | Fraunces | 64px | 700 | Decorative section numerals (`.depart-n`, 18% opacity) |
| Display | Fraunces | 48px | 600 | Type-spec display sample |
| Wordmark | Fraunces | 42px | 300 | App wordmark |
| Card value | Fraunces | 36px | 600 | Stat card values, tabular-nums |
| Pull-quote | Fraunces | 20px | 400 italic | Editorial thesis/quote blocks |
| H1 | Fraunces | 18px | 600 | Section/departure card titles |
| Display-sm | Fraunces | 24px | 400 italic | Type-spec secondary sample |
| Brand (in-app) | Fraunces | 16px | 600 | App topbar brand mark |
| Body | DM Sans | 14px | 400 | Prose, descriptions |
| Alert title | DM Sans | 13px | 500 | Alert feed item titles |
| Region/label | DM Sans | 11–12px | 400 | Sidebar nav, district names |
| Data-lg | Geist Mono | 16px | 500 | Stat-panel values, tabular-nums |
| Data-md | Geist Mono | 12px | 400 | Table/mono-grid data cells |
| Label/caption | Geist Mono | 9–11px | 400 | Section labels, badges, timestamps, uppercase, letter-spaced |

**Font blacklist:** Never use Inter, Roboto, Arial, Helvetica, Open Sans, Lato, Montserrat, or Poppins as primary fonts. If a dependency forces one of these, override with the stack above.

## Color

- **Approach:** Restrained, desaturated "warm dark" — earthy accent (green), warning rust (amber/orange), danger (red), a dedicated catastrophe plum, rest is neutral surface. Deliberately avoids the cool blue-gray "enterprise SaaS" look of the original GitHub-dark palette below — every competitor (HungerMap, FEWS NET) reads either sterile-corporate or alarm-red; this palette reads as a calm, authoritative instrument instead.
- **Background:** `#0D0F0E` — near-black, warm not blue-black. The page base.
- **Surface:** `#161A17` — cards, panels, sidebars.
- **Surface elevated:** `#1E2520` — hover states, active items.
- **Border/grid:** `#2A2E2B` — dividers, card outlines, table separators.
- **Text primary:** `#E8E4DA` — warm off-white, all readable text on dark backgrounds.
- **Text muted:** `#8A8C7F` — labels, metadata, timestamps.
- **Text faint:** `#505550` — least-prominent captions, scale markers.
- **Accent green (primary):** `#4A7C59` — vegetation health, primary actions, NDVI positive signal, IPC Phase 2 badge. Subtle bg: `#2C4D38`.
- **Warn (rust/amber):** `#C97B38` — conflict density, warnings, data staleness, IPC Phase 3 badge. Subtle bg: `#6B3E15`.
- **Critical (red):** `#B84436` — errors, IPC Phase 4 badge tone family. Subtle bg: `#5C1F18`.
- **Catastrophe (plum):** `#9B6B95` — IPC Phase 5 only. Subtle bg: `#3D2438`. Added 2026-06-20 — see Decisions Log; exists specifically so Phase 5 cannot collide with Phase 4's red.
- **OK (secondary green):** `#5A8A6A` — positive deltas, resolved states. Subtle bg: `#243D2C`.
- **Dark mode:** Default and primary experience. Light mode available via `[data-theme="light"]`.

**Light mode overrides** (CSS `[data-theme="light"]`):
```css
[data-theme="light"]{
  --bg:#F2EDE3;--surface:#EAE3D5;--surface-high:#E0D8C8;--grid:#C2B9AB;
  --text:#1C1F1D;--muted:#6B6860;--faint:#A09890;
  --accent:#2C5E3A;--accent-dim:#C8DDCC;
  --warn:#8F4E12;--warn-dim:#F5DFC3;
  --crit:#7A2219;--crit-dim:#F0C8C4;
  --catastrophe:#6B3D63;--catastrophe-dim:#E8D5E3;
  --ok:#2C5E3A;--ok-dim:#C8E0CC;
}
```

### IPC Phase Colors — Semantic, Non-Negotiable

Analysts are trained globally on these colors. Do not change them for aesthetic reasons. Do not use these hues for any other purpose. **Phase 4 and Phase 5 must always be visually distinguishable at a glance** — confusing Emergency with Catastrophe under fast scanning has real humanitarian-response consequences. (2026-06-20 incident: a preview iteration put both in the same red family — see Decisions Log.)

| Phase | Label | Token | Background | Text | Usage |
|-------|-------|-------|------------|------|-------|
| Phase 1 | Minimal | *(undefined — see note)* | — | — | Adequate food security. Not yet implemented in any mockup; pick a token visually distinct from Phase 2's green before shipping it (e.g. a paler/more neutral tint), not a reuse of `--ok`. |
| Phase 2 | Stressed | `--ok` / `--ok-dim` | `#243D2C` | `#5A8A6A` | Stressed but manageable |
| Phase 3 | Crisis | `--warn` / `--warn-dim` | `#6B3E15` | `#C97B38` | Crisis — humanitarian response needed |
| Phase 4 | Emergency | custom | `#6B2E10` | `#E07A38` | Emergency — urgent action required |
| Phase 5 | Catastrophe | `--catastrophe` / `--catastrophe-dim` | `#3D2438` | `#9B6B95` | Catastrophe / Famine |

**Critical:** Never use `#8b5cf6` (Tailwind violet-500) or any color from the Phase 4 red/orange family for conflict-event-density data outside the IPC badges — it collides with phase semantics. Use the dedicated `--catastrophe` plum for Phase 5; never reuse it elsewhere.

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
- **Border radius:** Low — `--r-sm: 3px` for inputs/buttons/badges, `--r-md: 5px` for thesis/chart/alert blocks, `--r-lg: 8px` for cards and the dashboard shell. 9999px only for pill badges. Instruments don't have round corners.

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
  --bg:            #0D0F0E;
  --surface:       #161A17;
  --surface-high:  #1E2520;
  --grid:          #2A2E2B;

  /* Text */
  --text:          #E8E4DA;
  --muted:         #8A8C7F;
  --faint:         #505550;

  /* Accents */
  --accent:        #4A7C59;
  --accent-dim:    #2C4D38;
  --warn:          #C97B38;
  --warn-dim:      #6B3E15;
  --crit:          #B84436;
  --crit-dim:      #5C1F18;
  --ok:            #5A8A6A;
  --ok-dim:        #243D2C;
  --catastrophe:   #9B6B95;
  --catastrophe-dim: #3D2438;

  /* Radius */
  --r-sm: 3px; --r-md: 5px; --r-lg: 8px;

  /* Typography */
  --f-display:  'Fraunces', Georgia, serif;
  --f-body:     'DM Sans', system-ui, sans-serif;
  --f-mono:     'Geist Mono', 'JetBrains Mono', monospace;
}

[data-theme="light"]{
  --bg:#F2EDE3;--surface:#EAE3D5;--surface-high:#E0D8C8;--grid:#C2B9AB;
  --text:#1C1F1D;--muted:#6B6860;--faint:#A09890;
  --accent:#2C5E3A;--accent-dim:#C8DDCC;
  --warn:#8F4E12;--warn-dim:#F5DFC3;
  --crit:#7A2219;--crit-dim:#F0C8C4;
  --catastrophe:#6B3D63;--catastrophe-dim:#E8D5E3;
  --ok:#2C5E3A;--ok-dim:#C8E0CC;
}
```

## Anti-patterns — Never Do These

- Bright/saturated purple (`#8b5cf6`, `#7c3aed`) anywhere — `--catastrophe` (`#9B6B95`) is the only purple in the system and it is reserved exclusively for IPC Phase 5. Do not use it, or any other purple, for conflict density or anything else.
- `#8884d8` (Recharts default purple) for any chart — replace with green/warn/crit tokens
- Reusing Phase 4's red/orange family for anything other than Phase 4 — keep Phase 4 and Phase 5 on visibly distinct hues (see incident below)
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
| 2026-06-20 | Pivot to Fraunces + warm-dark earthy palette, superseding Plus Jakarta Sans + GitHub-dark | `/design-review` of the new preview found the GitHub-dark look read as generic enterprise SaaS rather than a distinct instrument. New direction: serif display (editorial authority) + desaturated warm-dark surfaces (`#0D0F0E`/`#161A17`) instead of cool blue-gray (`#0d1117`/`#161b22`). User approved syncing this doc to the preview rather than reverting the preview. Border radius refined from flat 4px to a graduated 3/5/8px scale (`--r-sm`/`--r-md`/`--r-lg`) within the same low-radius philosophy. |
| 2026-06-20 | Added dedicated `--catastrophe` plum (`#9B6B95`) token for IPC Phase 5 | The new preview's first cut mapped Phase 5 onto the same red family as Phase 4 (`--crit`), making Emergency and Catastrophe visually indistinguishable under fast scanning — a direct violation of the non-negotiable IPC rule above. Fixed in `agrisight-design-preview.html` (FINDING-001) and documented here so the real app never reintroduces the collision. |

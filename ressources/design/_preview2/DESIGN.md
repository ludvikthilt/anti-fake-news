---
name: Ethical Fact-Checking System
colors:
  surface: '#FFFFFF'
  surface-dim: '#cfdbeb'
  surface-bright: '#f7f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#edf4ff'
  surface-container: '#e3efff'
  surface-container-high: '#dde9f9'
  surface-container-highest: '#d7e4f3'
  on-surface: '#111d28'
  on-surface-variant: '#40484f'
  inverse-surface: '#26323d'
  inverse-on-surface: '#e8f2ff'
  outline: '#707880'
  outline-variant: '#c0c7d0'
  surface-tint: '#006496'
  primary: '#00517b'
  on-primary: '#ffffff'
  primary-container: '#0b6a9e'
  on-primary-container: '#cbe5ff'
  inverse-primary: '#91cdff'
  secondary: '#00658b'
  on-secondary: '#ffffff'
  secondary-container: '#4dc4ff'
  on-secondary-container: '#004f6d'
  tertiary: '#634800'
  on-tertiary: '#ffffff'
  tertiary-container: '#815f00'
  on-tertiary-container: '#ffdea0'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cce5ff'
  primary-fixed-dim: '#91cdff'
  on-primary-fixed: '#001e31'
  on-primary-fixed-variant: '#004b72'
  secondary-fixed: '#c4e7ff'
  secondary-fixed-dim: '#7dd0ff'
  on-secondary-fixed: '#001e2d'
  on-secondary-fixed-variant: '#004c6a'
  tertiary-fixed: '#ffdea0'
  tertiary-fixed-dim: '#fbbc0e'
  on-tertiary-fixed: '#261a00'
  on-tertiary-fixed-variant: '#5c4300'
  background: '#f7f9ff'
  on-background: '#111d28'
  surface-variant: '#d7e4f3'
  brand-900: '#0E2A3B'
  ink-muted: '#4A5A68'
  line: '#D5DEE5'
  canvas: '#F5F9FC'
  action-green: '#1E8E5A'
  status-ok-bg: '#E3F4EA'
  status-ok-fg: '#0B5D38'
  status-ok-bd: '#1E8E5A'
  status-warn-bg: '#FFF1D6'
  status-warn-fg: '#7A4B00'
  status-warn-bd: '#B26B00'
  status-bad-bg: '#FDE8E6'
  status-bad-fg: '#9B1C14'
  status-bad-bd: '#C0392B'
  status-unk-bg: '#ECEAFB'
  status-unk-fg: '#4B3F9E'
  status-unk-bd: '#6657C4'
typography:
  headline-xl:
    fontFamily: Outfit
    fontSize: 2.5rem
    fontWeight: '700'
    lineHeight: '1.2'
  headline-xl-mobile:
    fontFamily: Outfit
    fontSize: 1.875rem
    fontWeight: '700'
    lineHeight: '1.25'
  headline-lg:
    fontFamily: Outfit
    fontSize: 2rem
    fontWeight: '600'
    lineHeight: '1.25'
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 1.5rem
    fontWeight: '600'
    lineHeight: '1.3'
  headline-md:
    fontFamily: Outfit
    fontSize: 1.5rem
    fontWeight: '600'
    lineHeight: '1.3'
  headline-sm:
    fontFamily: Outfit
    fontSize: 1.25rem
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '600'
    lineHeight: '1.2'
  label-sm:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '600'
    lineHeight: '1.2'
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: '1.4'
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system powers an educational, public-interest media verification platform. Its mission is epistemic responsibility: assisting human verification without passing automated verdicts or claiming omniscience. 

The aesthetic is **Institutional Modernism with Analytical Rigor**: calm, accessible, transparent, and strictly devoid of gamification or alarmism. The experience establishes an environment of investigative discernment rather than judicial verdict. The interface must never declare binary "TRUE" or "FALSE" outcomes, nor present 0–100% truth meters. Every screen reinforces pedagogical humility anchored by the mandatory principle: *"Ce site aide à vérifier : il ne prouve pas qu'une information est vraie."*

Visual accents balance crisp technical layouts with human-centric legibility: slate inks, deep atmospheric blues, distinct chromatic status badges, and the signature yellow punctuation anchor.

## Colors

The palette is engineered for maximum readability, trust, and strict compliance with WCAG AAA accessibility.

- **Primary (`#0B6A9E`, `--brand-700`)**: The workhorse interactive color. Reserved for interactive text links, primary buttons, and critical active triggers.
- **Secondary (`#1CA7E0`, `--brand-500`)**: A vibrant cyan dedicated to structural edge borders, accent lines, illustrations, and background tiles. **Strict Constraint:** Never use `--brand-500` for text or thin iconography over a white or light background.
- **Tertiary (`#F5B700`, `--dot-yellow`)**: The signature punctuation mark in the logo and contextual notice beacons.
- **Neutral Core**:
  - Canvas (`#F5F9FC`): Low-glare foundational backdrop.
  - Surface (`#FFFFFF`): Clean card and inspection panel fill.
  - Ink (`#14202B`): Primary body text, delivering deep contrast.
  - Ink-Muted (`#4A5A68`): Secondary metadata, captions, and structural labels.
  - Line (`#D5DEE5`): Clean, low-contrast 1px separation boundaries.
  - Brand-900 (`#0E2A3B`): Anchoring dark surfaces such as the footer and high-density technical query consoles.

### Semantic Status Matrix
Four nuanced analytical categories govern claim evaluation:
1. **Corroborée (`ok`)**: Background `#E3F4EA`, Foreground `#0B5D38`, Border `#1E8E5A`.
2. **Non corroborée (`warn`)**: Background `#FFF1D6`, Foreground `#7A4B00`, Border `#B26B00`.
3. **Contredite (`bad`)**: Background `#FDE8E6`, Foreground `#9B1C14`, Border `#C0392B`.
4. **Indéterminée (`unk`)**: Background `#ECEAFB`, Foreground `#4B3F9E`, Border `#6657C4`.

## Typography

The typographic hierarchy separates structural guidance from long-form documentary reading and forensic data:

- **Display & Headings (Outfit)**: Used for geometric precision and clarity, providing an approachable yet structured voice. Heading hierarchy spans `headline-xl` down to `headline-sm`.
- **Interface & Reading Body (Inter)**: Delivers clear rendering of dense investigative text, analytical caveats, and methodology disclaimers across desktop and mobile screens.
- **Forensic & Data Elements (JetBrains Mono)**: Applied to analysis identifiers (e.g., `#AN-2024-8849`), verified external URLs, cryptographic signatures, timestamp strings, and HTTP inspection parameters.

Typography should be set with generous line heights (1.5–1.6 on body text) to minimize eye fatigue during sustained reading.

## Layout & Spacing

The layout is built on a responsive 12-column grid system bounded at a maximum readable width of 1200px.

- **Desktop (≥ 1024px)**: 12 columns with 1.5rem gutters and 2rem outer margins. Verification sidebars, source citations, and timeline steps occupy a 4-column column track beside an 8-column analytical core.
- **Tablet (768px – 1023px)**: 8 columns with 1.25rem gutters and 1.5rem outer canvas margins. Sidebars reflow below the central body.
- **Mobile (< 768px)**: 4 columns with 1rem gutters and 1rem canvas margin. Multi-column forms and split comparison containers collapse into stacked vertical flows.

A strict 4px/8px rhythm (`space-xs` through `space-xl`) governs component density. Data rows leverage `space-xs` and `space-sm`, whereas critical disclaimers and report cards employ `space-lg` to create a focused, deliberate pace.

## Elevation & Depth

To sustain credibility and avoid superficial decoration, the system uses **structural planar boundaries and minimal ambient tinting** instead of heavy drop shadows:

- **Base Ground**: The main window runs on `--canvas` (`#F5F9FC`).
- **Elevated Surfaces**: Analysis cards, verification forms, and dialogs sit on `--surface` (`#FFFFFF`) with a 1px solid stroke in `--line` (`#D5DEE5`).
- **Inspection Emphasis**: Critical active cards (such as the primary analyzed claim) gain an extra-subtle tinted shadow: `0 4px 16px -2px rgba(14, 42, 59, 0.06)`.
- **Brand Accent Liseré**: High-level investigative cards feature a crisp 3px accent stroke along their top border (`--brand-500`), reinforcing visual structure without adding noise.

## Shapes

The design uses a **Soft (Level 1)** shape system. Elements have a standard 0.25rem (4px) corner radius, with 0.5rem (8px) for containers and 0.75rem (12px) for modals and hero blocks.

This restrained geometry preserves institutional authority and avoids toy-like or purely decorative interfaces. The only exception is the classification badges and pastilles, which use full capsule pill radii (`9999px`) to maintain clear status hierarchy at small scales.

## Components

### 1. Buttons
- **Primary CTA**: Background `--brand-700` (`#0B6A9E`), text `#FFFFFF`, border-radius 4px (`rounded-sm`), vertical padding 0.625rem, horizontal padding 1.25rem. Hover state shifts to dark blue (`#0A5883`). Never use `--brand-500` as a button background with white text.
- **Secondary**: Transparent background, 1px solid `--line` (`#D5DEE5`), text `--ink` (`#14202B`). Hover state shifts to `--canvas` (`#F5F9FC`) and border `--brand-700`.
- **Tertiary/Ghost**: No border, text `--brand-700`.

### 2. Status Badges & Chips
Display classification without moral judgment or binary true/false badges:
- **Corroborée (`ok`)**: Background `#E3F4EA`, Text `#0B5D38`, Border 1px `#1E8E5A`, Icon `check-circle-2`.
- **Non corroborée (`warn`)**: Background `#FFF1D6`, Text `#7A4B00`, Border 1px `#B26B00`, Icon `minus-circle`.
- **Contredite (`bad`)**: Background `#FDE8E6`, Text `#9B1C14`, Border 1px `#C0392B`, Icon `x-circle`.
- **Indéterminée (`unk`)**: Background `#ECEAFB`, Text `#4B3F9E`, Border 1px `#6657C4`, Icon `help-circle`.

### 3. Date Origin Pastilles (`DateOrigin`)
Categorical badges specifying the provenance of temporal claims:
- Variants: `Déclarée`, `Observée`, `Métadonnée`, `Indexation`.
- Styling: Pill-shaped (`rounded-full`), monospace or small label font (`label-sm`), background `#F5F9FC`, border 1px solid `#D5DEE5`, text `--ink-muted`.

### 4. Input Fields & Search Bars
- Background `#FFFFFF`, 1px border `#D5DEE5`, padding 0.75rem 1rem, text `#14202B`. Focus state reveals a 2px outline in `--brand-700` (`#0B6A9E`) with 0 offset. Analysis IDs and raw URL query fields strictly use `JetBrains Mono`.

### 5. Mandatory Disclaimer Banner
- Positioned in the global header or preceding every verification dossier:
- Surface `#F5F9FC`, left accent line 4px solid `--dot-yellow` (`#F5B700`), text `--ink` (`#14202B`), font `body-sm`.
- Content: *« Ce site aide à vérifier : il ne prouve pas qu'une information est vraie. »*

### 6. Verification Dossier Cards
- White surface, 1px outline in `--line`, subtle 3px top geometric decorative border in `--brand-500` (`#1CA7E0`).
- Divided internally by 1px `--line` rules separating context, claim, observed chronological pastille, and external corroboration links.
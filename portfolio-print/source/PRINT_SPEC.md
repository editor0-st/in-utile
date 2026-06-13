# PRINT_SPEC — 無用 In·Utile Portfolio

Everything below is transcribed from `print-portfolio.css` and the inline styles in
`Portfolio Draft.html`. Sizes are **real pt** (type) and **mm** (layout), as designed.

---

## 1. Document setup
- **Page size:** A4 portrait — **210 × 297 mm**
- **Facing pages:** ON. A *spread* = two A4 pages = A3 (420 × 297 mm).
- **Bleed:** **3 mm** all sides (not in the HTML; add for print). Full-bleed images
  and full-page dark/crimson fills must extend into the bleed.
- **Margins (mirrored / inside-outside):**
  - Top **18 mm**, Bottom **20 mm**
  - **Inside (spine) 20 mm**, **Outside 15 mm**
  - (verso = left page: outside/left 15, inside/right 20. recto = right page: inside/left 20, outside/right 15.)
- **Columns:** **6 columns**, **gutter 5 mm**, within the margin box.
- **Folio (page number):** IBM Plex Mono 8 pt, Ghost, baseline **12 mm** from bottom,
  aligned to the outside margin (verso left 15 mm / recto right 15 mm). On dark/crimson
  pages folio = Ivory 50–62%.

### Graph-paper background (brand signature — prints faintly)
- A **5 mm × 5 mm** square grid covering the whole page, very faint.
- Line tint by surface:
  - On **Paper**: grid line ≈ Charcoal **5.5%** (hairline ~0.1 pt).
  - On **Ink (dark)**: grid line ≈ Ivory **5%**.
  - On **Crimson**: grid line ≈ Ivory **8%**.
- Build as a **master-page** item: a full-bleed rectangle with a 5 mm grid (pattern
  fill, or many hairline guides converted to printing rules on their own layer), or
  place a one-page 5 mm-grid PDF at low opacity. Keep it on a back layer.

---

## 2. Swatches (CMYK) — create these first
CMYK values are from the CSS comments (PSO Uncoated v3 intent). Hex shown for reference.

| Swatch | Hex | CMYK | Use |
|---|---|---|---|
| **Paper** | #FAF8F2 | C1 M2 Y6 K0 | page canvas |
| **Ivory** | #F6F3EC | C2 M3 Y8 K0 | text on ink/crimson; subtle bg |
| **Charcoal** | #3D3936 | C0 M6 Y12 K85 | primary text |
| **Charcoal Soft** | #5E574F | C0 M8 Y16 K66 | secondary text |
| **Ghost** | #6E665B | C0 M7 Y18 K57 | meta / labels / captions |
| **Crimson (PRIME)** | #8A2D2B | C25 M90 Y82 K22 | prime accent — 5–10% area cap |
| **Crimson Bright** | #E84A3D | C0 M75 Y78 K0 | accent on dark (dividers, dark cover) |
| **Gold** | #A98742 | C20 M30 Y70 K15 | large numerals / year only |
| **Ink** | #1E1B19 | C50 M45 Y45 K100 | dark page canvas |
| **Grid Line** | #ECE6DA | C2 M3 Y9 K0 | graph-paper line (use at low tint) |

- **Rule / hairline** = Charcoal at **20% tint** (`--rule`). Soft rule = Charcoal 12%.
- **Ivory rule** (on dark) = Ivory at **22% tint**.

---

## 3. Paragraph & character styles
Map one named style per row. `tr` = tracking (letter-spacing). Leading is the second
number where given (e.g. 40/46 = 40 pt size / 46 pt leading). Justified = full justify
+ hyphenation; everything else is left/ragged unless noted.

### Display / titles
| Style | Font | Size / Leading | Tracking | Color | Notes |
|---|---|---|---|---|---|
| `Cover/Name` | Spectral 500 | 13 pt | +0.02em | Charcoal Soft | cover author line |
| `Cover/Title` | Spectral 500 | 40 / 46 pt | −0.01em | Charcoal (Ivory on dark) | "Arguing with…" |
| `Cover/Title-em` (char) | Cormorant Garamond 600 **italic** | inherits | — | Crimson (Crimson Bright on dark) | "my own" |
| `Title-Display` | Spectral 500 | 32 / 42 pt | −0.01em | Charcoal | project titles |
| `Heading` | Spectral 500 | 22 / 28 pt | 0 | Charcoal | section/article headings |
| `Lead` | Cormorant Garamond 500 **italic** | 14 / 21 pt | 0 | Charcoal Soft | project standfirst |

### Wordmark lockup (cover)
| Style | Font | Size | Tracking | Color |
|---|---|---|---|---|
| `Lockup/CJK` | Noto Serif HK 700 | 72 pt | +0.04em | Ivory (on dark) / Charcoal | 無用 — keep on one line |
| `Lockup/Latin` | Bodoni Moda 600 | 22 pt | +0.03em | Ivory 82% / Charcoal | "in utile" (lowercase) |

### Body / editorial
| Style | Font | Size / Leading | Tracking | Color | Notes |
|---|---|---|---|---|---|
| `Body` | Pretendard 360 (Light/Reg) | 9.5 / 14 pt | 0 | Charcoal | **justified**, hyphenate |
| `Body/DropCap` | + first char Spectral 500 | ~46 pt over **3 lines** | — | Crimson | drop-cap variant |
| `Caption` | Pretendard 400 | 8 / 12 pt | 0 | Ghost | `b` run = 600 Charcoal Soft |
| `Epigraph` | Cormorant Garamond 500 italic | 15 / 23 pt | 0 | Charcoal Soft (Ivory 74% on dark) | cover verso |
| `Colophon` | IBM Plex Mono 400 | 7 / 12 pt | +0.04em | Ghost | |

### Meta / labels (IBM Plex Mono, UPPERCASE)
| Style | Font | Size | Tracking | Color |
|---|---|---|---|---|
| `Meta` | IBM Plex Mono 400 | 7 pt / 14 leading | +0.08em | Ghost |
| `Eyebrow` | IBM Plex Mono 400 | 7 pt | +0.14em | Ghost |
| `Standfirst` (cover) | IBM Plex Mono 400 | 7 pt / 13 | +0.12em | Ghost |
| `Folio` | IBM Plex Mono 400 | 8 pt | +0.06em | Ghost |

### Numerals (Bodoni Moda)
| Style | Font | Size | Color | Notes |
|---|---|---|---|---|
| `MarkNum` | Bodoni Moda 600 | 84 pt | Gold (project №) / Charcoal | line-height .9, tr −0.02em |
| `Cover/Year` | Bodoni Moda 600 | 64 pt | Gold | "26" |

### Table of Contents
| Style | Font | Size | Color |
|---|---|---|---|
| `TOC/Num` | Bodoni Moda 600 | 22 pt | Gold |
| `TOC/Title` | Spectral 500 | 13 pt | Charcoal |
| `TOC/Stand` | Pretendard 360 | 8.5 pt | Charcoal Soft |
| `TOC/Meta` | IBM Plex Mono 400 | 7 pt | Ghost (caps, right-aligned) |
| `TOC/CJK` | Noto Serif HK 700 | 30 pt | Charcoal (目次) |
- TOC row: 3-col table **18 mm | flex | auto**, 6 mm gutter, **0.6 pt** top rule (Rule swatch).

### Section divider (dark pages)
| Style | Font | Size | Color |
|---|---|---|---|
| `Div/Num` (Roman I·II·III) | Bodoni Moda 600 | 30 pt | Crimson Bright |
| `Div/Title` | Spectral 500 | 30 / 36 pt | Ivory |
| `Div/CJK` (행·行 etc.) | Noto Serif HK 500 | 18 pt | Ivory |
| `Div/Index` | IBM Plex Mono 400 | 7 pt | Ivory 55% (caps) |
| `Div/Watermark` | Noto Serif HK 700 | **150 mm** | Ivory **9%** | one giant hanja, centered |
- Divider accent rule (`.dmark`): **2 pt**, **50 mm** wide, Crimson Bright.

### Two-voice critique (批) — the signature system
| Style | Font | Size / Leading | Color | Notes |
|---|---|---|---|---|
| `Crit/Label` | IBM Plex Mono 400 | 7 pt | Crimson | caps, +0.12em; leading 批 in Noto Serif HK 700 12 pt |
| `Crit/Body` | Cormorant Garamond 500 **italic** | 10.5 / 15 pt | Charcoal | the critique voice |
| `Pull` | Cormorant Garamond 600 **italic** | 19 / 25 pt | Crimson | pull-quote; leading 批 same color |
- Critique block has a **1.4 pt Crimson vertical rule** on its left edge, 5 mm from text
  (anchored line or left paragraph border). This bar is the visual signature of 批.

### Metadata blocks
| Style | Font | Size | Color |
|---|---|---|---|
| `Meta/Key` | IBM Plex Mono 400 | 7 pt | Ghost (caps, +0.1em) |
| `Meta/Val` | Pretendard 400 | 8.5 pt | Charcoal |
- `metablock` grid: **22 mm key | flex value**, 5 pt row gap, 4 mm col gap.
- `cv-row`: **26 mm year | flex entry**, 0.6 pt top rule; entry `b` = Pretendard 600 9.5 pt, span = 360 8.5 pt.

---

## 4. Object (frame) styles
- **Image frame:** picture/graphic frame, fill **Ivory**, optional **0.6 pt** Rule-swatch
  stroke. (In the web version these show a 大형 hanja sign + graph + caption; in print
  they're simply empty picture frames ready for the user's image. If you want the
  placeholder look retained for an unfilled frame, drop a centered Noto Serif HK 700
  ~60 pt hanja at Crimson 16% + a Meta caption beneath.)
- **Full-bleed image / fill:** frame spans page edge **into the 3 mm bleed**; on the
  recto it may cross the spine (the cover & some project openers are full-bleed).
- **Image treatment:** apply a subtle **saturation 90% / contrast 95%** adjustment to
  placed photos (brand imagery rule).
- **Rule / hairline objects:** `--rule-crim` = **1.4 pt** Crimson line, **46 mm** wide
  (used under titles). Hairline section rules = **0.6 pt** Rule swatch.

---

## 5. Page-background classes → which surface
- Paper (default): all body/editorial pages.
- **Ink (dark):** Cover spread (both pages), section dividers (recto of 行 / 論 / 思).
- **Crimson:** Theory statement page (recto of Spread 12) — the single full prime-color surface.
See `CONTENT_MAP.md` for the exact per-spread assignment.

# 無用 In·Utile — Taeyoung Ro Portfolio · Affinity-compatible print build

Turns the HTML/CSS design handoff in `source/` into **Affinity-compatible
publication files**. Two deliverables (README's Route A + Route B):

| File (`dist/`) | What it is | Open in Affinity via |
|---|---|---|
| `portfolio_A4_pages_bleed.pdf` | **Press PDF** — 26 single A4 pages, **3 mm bleed** all sides, brand fonts embedded. The file you send to print / impose / perfect-bind. | File ▸ Open (highest visual fidelity; text comes in as frames) |
| `portfolio_A3_spreads.pdf` | **Proof PDF** — 13 A3 facing spreads, no bleed. Quick visual review / import. | File ▸ Open |
| `Taeyoung_Ro_Portfolio.idml` | **Editable master** — A4 facing pages, 3 mm bleed, mirrored margins, 6-col/5 mm grid, all CMYK swatches, all named paragraph/character/object styles, 26 pages with the copy poured into styled frames + empty picture frames. | File ▸ Open / Import (keeps live text + named styles) |

## Regenerate

```bash
cd portfolio-print
bash fonts/download-fonts.sh          # one-time: pull brand fonts locally (~50 MB)
npm install && npx playwright install chromium   # or reuse an existing Chromium
node make-pdf.js                      # → the two PDFs
python3 build-idml.py                 # → the IDML
```

`make-pdf.js` re-flows the screen gallery into print sheets (flattening each
`.page` to A4+bleed, lifting each `.spread` to A3), embeds the local fonts as
`@font-face`, and drives Chromium's PDF box with `@page` + `preferCSSPageSize`.
If the Playwright browser download is blocked, set `CHROME_PATH` to any
Chromium/Chrome binary — the script auto-detects one under
`PLAYWRIGHT_BROWSERS_PATH` too.

## Fonts (open-source; downloaded by `fonts/download-fonts.sh`)

Spectral · Bodoni Moda · Cormorant Garamond · Pretendard · IBM Plex Mono ·
Noto Serif HK · Noto Serif KR. All CJK glyphs used (無用行論思書信目次批序歷頭號 +
hangul) were verified present in Noto Serif HK/KR — no tofu. Install the same
families in your OS before editing the IDML so Affinity links them by name.

## What transfers vs. needs hand-finishing in Affinity

**Transfers (IDML):** page size, bleed, mirrored margins, 6-col grid, every
CMYK swatch, every named paragraph/character/object style with real pt sizes,
live text per page, empty picture frames, dark/crimson surface fills.

**Hand-finish (the design has effects DTP must place by hand):**
- **Multi-column / sidebar layouts** (two-voice critique 批, TOC register, meta
  grids) — the IDML pours each page's copy into one styled frame; split into the
  column positions from `source/CONTENT_MAP.md`.
- **Drop caps** — apply the `Body` style then set a 3-line drop cap (Crimson).
- **批 critique left bar** — 1.4 pt Crimson rule on the critique frame's left edge.
- **5 mm graph-paper background** — recreate as a master-page grid (the brand
  signature; see `source/PRINT_SPEC.md §1`). The PDFs already carry it.
- **CJK font split** — Noto Serif HK on hanja, Noto Serif KR on hangul.
- **Place images** into the picture frames (saturation 90% / contrast 95%).
- **Full-bleed crossings** — extend hero frames into the 3 mm bleed / spine.

## Notes
- A4 page order follows the source document order (cover verso *ii* precedes
  recto *i*, as the spread is drawn). Reorder during imposition if needed.
- `source/` is the unmodified design handoff and the source of truth.

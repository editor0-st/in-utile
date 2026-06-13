# Handoff — 無用 In·Utile · Taeyoung Ro Architecture Portfolio → Affinity Publisher / InDesign

This bundle hands off a **print layout** (not a web app) so you can produce an
**editable layout file** in **Affinity Publisher** (or InDesign).

The design source of truth is the HTML/CSS in this folder. It is built at **real
print dimensions** (A4 pages, A3 spreads, sizes in mm/pt), so almost everything
needed for a faithful print document — page geometry, margins, a 6-column grid,
CMYK swatches, and exact type sizes — is already encoded. `PRINT_SPEC.md` extracts
all of it. `CONTENT_MAP.md` lists the 13 spreads in order with page numbers.

---

## ⚠️ Read this first — what format to target

**Affinity Publisher's native `.afpub` is a closed binary format. It cannot be
generated programmatically.** Pick one of two routes to get an *editable* file:

### Route A — Print PDF → open in Affinity Publisher  *(fastest, highest visual fidelity)*
1. Render the HTML to a print-ready, **press-quality PDF** (real fonts embedded,
   A4 pages or A3 spreads, 3 mm bleed). Use headless Chromium:
   - `Portfolio Draft.html` is a screen *gallery* of spreads. For PDF you want
     **one A4 page per page** (or one A3 per spread). Print CSS already hides the
     topbar/plate and removes gaps, but Chromium's print box must be set to the
     page size — drive it with Playwright/Puppeteer `page.pdf({ width:'210mm',
     height:'297mm', printBackground:true, preferCSSPageSize:true })` after
     injecting `@page { size:210mm 297mm; margin:0 }`, **or** split each
     `.spread` into two `.page` prints. (See "Generating the PDF" below.)
2. In Affinity Publisher: **File ▸ Open** the PDF → it converts pages to editable
   text frames + vector/curves. Re-link the brand fonts when prompted.
   - Pros: looks exactly like the design instantly; great for proofing.
   - Cons: text comes in as line-by-line frames, **no named paragraph styles**,
     justified copy may need re-flowing. Good for light edits, less so for heavy
     re-typesetting.

### Route B — Build an IDML  *(the "proper" editable layout — recommended if it will be edited seriously)*
**IDML** (InDesign Markup Language) is an **open, ZIP-of-XML** interchange format.
**Affinity Publisher 2 imports IDML**, and InDesign opens it natively. Generated
IDML keeps **named paragraph/character styles, swatches, the column grid, master
pages, and live text frames** — exactly what you want for a portfolio you'll keep
revising. This is more work to generate but is the real answer to "InDesign-format
file for Affinity."

`PRINT_SPEC.md` is written so you can build the IDML directly: it lists the
document setup, every swatch with **CMYK** values, and every paragraph/character/
object style with **exact pt sizes** mapped from the CSS class it came from.

**Best practice: do both.** Generate the PDF now for an instant editable/proofing
copy, and build the IDML for the maintainable master.

---

## Recommended build approach for the IDML (Route B)

You are generating an `.idml` package. Two viable tactics:

1. **`simple-idml` (Python)** — start from a minimal blank IDML template at the
   right page size, then inject Stories (text), Spreads (geometry/frames), Styles
   and Graphic resources. Good when you want library help with the ZIP/XML plumbing.
   `pip install SimpleIDML`

2. **Hand-assemble the IDML package** — an `.idml` is a ZIP containing
   `mimetype`, `designmap.xml`, `Resources/{Graphic,Fonts,Styles,Preferences}.xml`,
   `Spreads/Spread_*.xml`, `Stories/Story_*.xml`, `META-INF/`. Build the XML from
   `PRINT_SPEC.md` + `CONTENT_MAP.md`. More control, more verbose.

Whichever you choose:
- Set the document to **A4 portrait, facing pages**, **3 mm bleed**, margins and a
  **6-column / 5 mm gutter** grid exactly as `PRINT_SPEC.md` specifies (the
  verso/recto margins mirror).
- Create the **swatches** first (CMYK), then the **paragraph & character styles**,
  then lay frames per spread and pour the **Stories** (copy is in the HTML, by
  `data-screen-label`).
- Image placeholders → empty **graphic (picture) frames** at the sizes given, so
  the user just drops images in.

### What transfers cleanly vs. needs hand-finishing
| Transfers cleanly | Needs manual finishing in Publisher |
|---|---|
| Page size, margins, columns, bleed | The faint **5 mm graph-paper background** — recreate as a master-page rectangle filled with a grid pattern, OR place a 1-page grid PDF on a non-printing-ish low-opacity layer (see PRINT_SPEC) |
| Swatches (CMYK) | **Drop caps** — set as a Paragraph style "Drop Cap" (1 char, 3 lines) |
| Named paragraph/character styles, pt sizes | **CJK font fallback** — browsers swap per glyph; DTP apps don't. Apply **Noto Serif HK** to hanja (無用行論思書…) and **Noto Serif KR** to hangul (행·론·사·노태영) explicitly, or use the World-Ready/CJK composer |
| Text frames + story copy | **Justified body** may need hyphenation/H&J tuning |
| Picture frames for images | Full-bleed dark/crimson fills — extend frames to the bleed box |

---

## Fonts (install before opening; all Google Fonts / open source)
| Role | Family | Weights used |
|---|---|---|
| Display & headings (EN) | **Spectral** | 400, 500, 600 + italic 500 |
| Numerals / wordmark | **Bodoni Moda** | 500, 600, 700 + italic 500 (optical size) |
| Quotes / critique (italic) | **Cormorant Garamond** | 500, 600 + italic 500/600 |
| Body & UI (KR + EN) | **Pretendard** | Light/Regular (~300–400; CSS uses 360) |
| Meta / folio | **IBM Plex Mono** | 400, 500 |
| Hanja marks (無用行論思) | **Noto Serif HK** | 500, 700 |
| Hangul readings (행·론·사·노태영) | **Noto Serif KR** | 500, 700 |

> Use the **static** Pretendard weights for DTP (not "Pretendard Variable").

---

## Generating the PDF (Route A) — concrete recipe
```bash
# from this folder, with Node + Playwright installed
npx playwright install chromium
node make-pdf.js   # write this small script:
```
```js
// make-pdf.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + __dirname + '/Portfolio Draft.html', { waitUntil:'networkidle' });
  // Print one A3 landscape per spread (matches the on-screen spread):
  await p.addStyleTag({ content: '@page{ size:420mm 297mm; margin:0 } .topbar,.plate{display:none!important} .gallery{gap:0!important;padding:0!important} .scaler{transform:none!important;height:auto!important}' });
  await p.pdf({ path:'portfolio_A3_spreads.pdf', width:'420mm', height:'297mm', printBackground:true, preferCSSPageSize:true });
  await b.close();
})();
```
- For **single A4 pages** (better for binding/imposition), iterate each `.page`
  element instead and print at `210mm × 297mm`.
- `printBackground:true` keeps the graph grid, dark/crimson fills, and image fills.
- Embed fonts (Chromium does automatically when installed/online).

---

## Files in this bundle
- `Portfolio Draft.html` — the layout (13 spreads). Open in a browser to see the target.
- `print-portfolio.css` — all tokens, type styles, components (the spec's source).
- `image-slot.js` — drives the image placeholders (web only; in DTP these become picture frames).
- `Brand Reference.html` — the 無用 In·Utile brand & design system reference.
- `PRINT_SPEC.md` — document setup, CMYK swatches, paragraph/character/object styles.
- `CONTENT_MAP.md` — the 13 spreads in order with page numbers, purpose, and frame layout.

---

## Prompt to paste into Claude Code
> I have a print portfolio designed in HTML at real A4/A3 dimensions (see this
> folder). I want an **editable Affinity Publisher** file. Affinity's native format
> can't be generated, so build me an **IDML** that Affinity Publisher 2 can import.
> Follow `PRINT_SPEC.md` for the document setup (A4 portrait, facing pages, 3 mm
> bleed, 6-column / 5 mm-gutter mirrored margins), create all CMYK swatches and the
> named paragraph/character styles exactly as specified, then lay out the 13 spreads
> from `CONTENT_MAP.md` — pouring the copy from `Portfolio Draft.html` (find each
> spread by its `data-screen-label`) and adding empty picture frames at the given
> sizes for images. Use `simple-idml` from a blank A4 template. Apply Noto Serif HK
> to hanja and Noto Serif KR to hangul explicitly. Also write `make-pdf.js`
> (Playwright) to export an A3-spread press PDF as a proofing/quick-import copy.
> Tell me which elements I'll need to finish by hand in Publisher.

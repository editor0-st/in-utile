/**
 * make-pdf.js — Press PDF exporter for the 無用 In·Utile portfolio.
 *
 * The source "Portfolio Draft.html" is a *screen* gallery: it scales each A3
 * spread to fit the viewport with a sticky topbar and caption plates. For
 * print we throw all of that away and re-flow the real-mm geometry into print
 * sheets, then drive headless Chromium's PDF box with @page + preferCSSPageSize.
 *
 * Two outputs:
 *   dist/portfolio_A4_pages_bleed.pdf  — 26 single A4 pages, 3 mm bleed all
 *                                        sides (the press/binding file).
 *   dist/portfolio_A3_spreads.pdf      — 13 A3 facing spreads, no bleed
 *                                        (visual proofing / quick Affinity import).
 *
 * Both open in Affinity Publisher via File ▸ Open. Backgrounds (graph grid,
 * dark/crimson fills, image-frame placeholders) print because printBackground
 * is on; fonts embed because Chromium fetches the Google Fonts / Pretendard
 * CDNs at load and subsets them into the PDF.
 *
 *   npm i -D playwright   &&   npx playwright install chromium
 *   node make-pdf.js
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

// The sandbox blocks Playwright's browser CDN, but a Chromium build is usually
// already present under PLAYWRIGHT_BROWSERS_PATH. Point launch() straight at it
// via executablePath so the playwright/browser version mismatch is irrelevant.
function findChrome() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) {
    return process.env.CHROME_PATH;
  }
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  try {
    for (const d of fs.readdirSync(root)) {
      if (!d.startsWith('chromium-')) continue;
      const p = path.join(root, d, 'chrome-linux', 'chrome');
      if (fs.existsSync(p)) return p;
    }
  } catch (_) {}
  return undefined; // fall back to playwright's bundled resolution
}

const SRC = 'file://' + path.join(__dirname, 'source', 'Portfolio Draft.html');
const OUT_A4 = path.join(__dirname, 'dist', 'portfolio_A4_pages_bleed.pdf');
const OUT_A3 = path.join(__dirname, 'dist', 'portfolio_A3_spreads.pdf');

// 3 mm bleed: trim A4 210×297 → media 216×303. Margins/folio measured from the
// trim edge, so every interior offset shifts +3 mm once the page grows to bleed.
// --- Local brand fonts -----------------------------------------------------
// Chromium in this sandbox can't reliably reach the Google Fonts / jsdelivr
// CDNs, so we embed the real typefaces from fonts/ (run fonts/download-fonts.sh
// once). @font-face is injected with absolute file:// URLs and the remote
// <link>s are stripped so the local faces are the only ones that resolve.
function fontUrl(file) {
  return 'file://' + path.join(__dirname, 'fonts', file);
}
function face(family, file, { weight = '400', style = 'normal' } = {}) {
  const fmt = file.endsWith('.otf') ? 'opentype' : 'truetype';
  return `@font-face{font-family:"${family}";font-style:${style};font-weight:${weight};` +
    `font-display:swap;src:url("${fontUrl(file)}") format("${fmt}");}`;
}
const FONT_FACE_CSS = [
  // Spectral — display & headings
  face('Spectral', 'Spectral-Regular.ttf', { weight: '400' }),
  face('Spectral', 'Spectral-Medium.ttf', { weight: '500' }),
  face('Spectral', 'Spectral-SemiBold.ttf', { weight: '600' }),
  face('Spectral', 'Spectral-Italic.ttf', { weight: '400', style: 'italic' }),
  face('Spectral', 'Spectral-MediumItalic.ttf', { weight: '500', style: 'italic' }),
  // Bodoni Moda — numerals / wordmark (variable: weight range + auto optical size)
  face('Bodoni Moda', 'BodoniModa.ttf', { weight: '100 900' }),
  face('Bodoni Moda', 'BodoniModa-Italic.ttf', { weight: '100 900', style: 'italic' }),
  // Cormorant Garamond — critique / quotes (variable)
  face('Cormorant Garamond', 'CormorantGaramond.ttf', { weight: '100 900' }),
  face('Cormorant Garamond', 'CormorantGaramond-Italic.ttf', { weight: '100 900', style: 'italic' }),
  // IBM Plex Mono — meta / folio
  face('IBM Plex Mono', 'IBMPlexMono-Regular.ttf', { weight: '400' }),
  face('IBM Plex Mono', 'IBMPlexMono-Medium.ttf', { weight: '500' }),
  // Pretendard — body / UI (declared under both family names the CSS references)
  face('Pretendard', 'Pretendard-Light.otf', { weight: '300' }),
  face('Pretendard', 'Pretendard-Regular.otf', { weight: '400' }),
  face('Pretendard Variable', 'Pretendard-Light.otf', { weight: '300' }),
  face('Pretendard Variable', 'Pretendard-Regular.otf', { weight: '400' }),
  // Noto Serif HK / KR — hanja + hangul (variable)
  face('Noto Serif HK', 'NotoSerifHK.ttf', { weight: '100 900' }),
  face('Noto Serif KR', 'NotoSerifKR.ttf', { weight: '100 900' }),
].join('\n');

// Drop the remote font stylesheets so only the embedded faces resolve.
function stripRemoteFonts() {
  document.querySelectorAll('link[rel="stylesheet"]').forEach((l) => {
    if (/googleapis|gstatic|jsdelivr/.test(l.href)) l.remove();
  });
}

// Shared print fixes for both page geometries.
// 1) The spread-05 key drawing is authored as `.frame{flex:1}` so it "fills the
//    column", but inside the content-sized grid row it collapses to 0 (a latent
//    bug in the source draft — the cover's flex:1 survives only because it holds
//    text). Pin it to a definite height so the picture frame is real. Scoped to
//    .frame so the cover's flex:1 lockup column is untouched.
// 2) Give every empty image-slot a 0.6 pt rule edge so unfilled picture frames
//    read clearly in the proof (matches PRINT_SPEC §4 "optional 0.6 pt stroke").
const FRAME_FIX = `
  .frame[style*="flex:1"] { flex: none !important; height: 240mm; }
  image-slot { box-shadow: inset 0 0 0 0.6pt var(--rule); }
`;

const A4_BLEED_CSS = `
  @page { size: 216mm 303mm; margin: 0; }
  html, body { margin: 0; padding: 0; background: #fff; }
  /* each .page becomes its own bleed sheet */
  .page {
    width: 216mm; height: 303mm; display: block; overflow: hidden;
    box-shadow: none !important; flex: none !important;
    break-after: page; page-break-after: always;
  }
  .page:last-child { break-after: auto; page-break-after: auto; }
  /* shift the live type area + folio in by the 3 mm bleed so trim margins hold */
  .live { top: 21mm; bottom: 23mm; }
  .verso .live { left: 18mm; right: 23mm; }
  .recto .live { left: 23mm; right: 18mm; }
  .folio { bottom: 15mm; }
  .verso .folio { left: 18mm; }
  .recto .folio { right: 18mm; }
  .cover .brand-cjk, .page > .brand-cjk { top: 21mm; right: 18mm; }
  /* .bleed is inset:0 of the now-216×303 page → fills to all four bleed edges */
  /* hide the web-only "or browse files" line inside empty image placeholders */
  image-slot::part(sub) { display: none; }
`;

const A3_CSS = `
  @page { size: 420mm 297mm; margin: 0; }
  html, body { margin: 0; padding: 0; background: #fff; }
  .scaler { transform: none !important; height: auto !important; }
  .spread {
    display: flex; margin: 0 !important; box-shadow: none !important;
    break-after: page; page-break-after: always;
  }
  .spread:last-child { break-after: auto; page-break-after: auto; }
  .spread::after { display: none; }   /* drop the on-screen spine shadow */
  image-slot::part(sub) { display: none; }
`;

// Flatten every .page (verso, recto, …) up to <body> root, in document order,
// and drop the gallery chrome. Pages keep their verso/recto/dark/crimson
// classes, so all selectors still resolve.
function flattenToPages() {
  document.querySelectorAll('.topbar, .plate').forEach((e) => e.remove());
  const pages = Array.from(document.querySelectorAll('.spread .page'));
  pages.forEach((p) => document.body.appendChild(p));
  Array.from(document.body.children).forEach((c) => {
    if (!pages.includes(c)) c.remove();
  });
}

// Lift every .spread to <body> root for A3 facing-page output.
function flattenToSpreads() {
  document.querySelectorAll('.topbar, .plate').forEach((e) => e.remove());
  const spreads = Array.from(document.querySelectorAll('.spread'));
  spreads.forEach((s) => document.body.appendChild(s));
  Array.from(document.body.children).forEach((c) => {
    if (!spreads.includes(c)) c.remove();
  });
}

async function settle(page) {
  await page.waitForLoadState('networkidle').catch(() => {});
  // Make sure web fonts are actually downloaded before measuring/printing.
  await page.evaluate(() => (document.fonts ? document.fonts.ready : null));
  await page.waitForTimeout(400);
}

async function render({ browser, restructure, css, out, width, height, label }) {
  const page = await browser.newPage();
  await page.goto(SRC, { waitUntil: 'load' });
  await page.evaluate(stripRemoteFonts);
  await page.addStyleTag({ content: FONT_FACE_CSS });
  await settle(page);
  await page.evaluate(restructure);
  await page.addStyleTag({ content: css + FRAME_FIX });
  await settle(page);
  await page.emulateMedia({ media: 'print' });
  await page.pdf({
    path: out,
    width,
    height,
    printBackground: true,
    preferCSSPageSize: true,
  });
  await page.close();
  console.log(`✓ ${label} → ${path.relative(process.cwd(), out)}`);
}

(async () => {
  const executablePath = findChrome();
  if (executablePath) console.log(`• chromium: ${executablePath}`);
  const browser = await chromium.launch({ executablePath });
  try {
    await render({
      browser,
      restructure: flattenToPages,
      css: A4_BLEED_CSS,
      out: OUT_A4,
      width: '216mm',
      height: '303mm',
      label: 'A4 single pages · 3 mm bleed (press)',
    });
    await render({
      browser,
      restructure: flattenToSpreads,
      css: A3_CSS,
      out: OUT_A3,
      width: '420mm',
      height: '297mm',
      label: 'A3 facing spreads · no bleed (proof)',
    });
  } finally {
    await browser.close();
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});

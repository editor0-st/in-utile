#!/usr/bin/env bash
# Download the brand fonts locally so the PDF embeds the real typefaces instead
# of system fallbacks. All sources are open-source mirrors reachable from this
# environment's network allowlist (raw.githubusercontent.com).
set -euo pipefail
cd "$(dirname "$0")"

GF="https://raw.githubusercontent.com/google/fonts/main/ofl"
PRE="https://raw.githubusercontent.com/orioncactus/pretendard/main/packages/pretendard/dist/public/static"

dl(){ # url  outfile
  echo "  ↓ $2"
  curl -fsSL --retry 3 --max-time 120 -o "$2" "$1"
}

echo "Spectral (display/headings)…"
dl "$GF/spectral/Spectral-Regular.ttf"      Spectral-Regular.ttf
dl "$GF/spectral/Spectral-Medium.ttf"       Spectral-Medium.ttf
dl "$GF/spectral/Spectral-SemiBold.ttf"     Spectral-SemiBold.ttf
dl "$GF/spectral/Spectral-Italic.ttf"       Spectral-Italic.ttf
dl "$GF/spectral/Spectral-MediumItalic.ttf" Spectral-MediumItalic.ttf

echo "Bodoni Moda (numerals/wordmark, variable)…"
dl "$GF/bodonimoda/BodoniModa%5Bopsz%2Cwght%5D.ttf"        BodoniModa.ttf
dl "$GF/bodonimoda/BodoniModa-Italic%5Bopsz%2Cwght%5D.ttf" BodoniModa-Italic.ttf

echo "Cormorant Garamond (critique/quote, variable)…"
dl "$GF/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"        CormorantGaramond.ttf
dl "$GF/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf" CormorantGaramond-Italic.ttf

echo "IBM Plex Mono (meta/folio)…"
dl "$GF/ibmplexmono/IBMPlexMono-Regular.ttf" IBMPlexMono-Regular.ttf
dl "$GF/ibmplexmono/IBMPlexMono-Medium.ttf"  IBMPlexMono-Medium.ttf

echo "Pretendard (body/UI, KR+EN)…"
dl "$PRE/Pretendard-Light.otf"   Pretendard-Light.otf
dl "$PRE/Pretendard-Regular.otf" Pretendard-Regular.otf

echo "Noto Serif HK / KR (hanja + hangul, variable)…"
dl "$GF/notoserifhk/NotoSerifHK%5Bwght%5D.ttf" NotoSerifHK.ttf
dl "$GF/notoserifkr/NotoSerifKR%5Bwght%5D.ttf" NotoSerifKR.ttf

echo "Done. $(ls -1 *.ttf *.otf 2>/dev/null | wc -l) font files."

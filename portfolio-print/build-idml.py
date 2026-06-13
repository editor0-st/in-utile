#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build-idml.py — generate an editable IDML master for the 無用 In·Utile portfolio.

IDML (InDesign Markup Language) is an open ZIP-of-XML interchange format that
Affinity Publisher 2 imports and InDesign opens natively. Unlike the PDF (which
comes in as line-by-line frames), this keeps the document structure the spec
asks for:

  • A4 portrait, facing pages, 3 mm bleed, mirrored margins (T18/B20/inside20/
    outside15), 6 columns / 5 mm gutter.
  • Every CMYK swatch from PRINT_SPEC §2.
  • Every named paragraph & character style from §3, and object styles from §4,
    with the real font / pt size / leading / tracking / colour.
  • All 13 spreads (26 pages): each page's copy poured into styled text frames,
    dark/crimson surfaces filled, and empty picture frames at the inventory
    sizes ready for the user to drop drawings into.

Output: dist/Taeyoung_Ro_Portfolio.idml

This is a hand-assembled package (no InDesign required). It targets a
conservative DOMVersion so Affinity Publisher 2 imports it. Fine frame
positioning / multi-column splits are the documented hand-finish step.
"""
import os, zipfile, html
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist", "Taeyoung_Ro_Portfolio.idml")
DOM = "16.0"  # InDesign CC 2021 — well within Affinity Publisher 2 import range

MM = 2.834645669291339  # pt per mm
def mm(v): return round(v * MM, 4)

PAGE_W, PAGE_H = mm(210), mm(297)
BLEED = mm(3)
M_TOP, M_BOT, M_IN, M_OUT = mm(18), mm(20), mm(20), mm(15)
COLS, GUT = 6, mm(5)

# ── Swatches (CMYK, PSO Uncoated v3 intent) — PRINT_SPEC §2 ──────────────────
# name -> (C, M, Y, K)
SWATCHES = {
    "Paper":         (1, 2, 6, 0),
    "Ivory":         (2, 3, 8, 0),
    "Charcoal":      (0, 6, 12, 85),
    "Charcoal Soft": (0, 8, 16, 66),
    "Ghost":         (0, 7, 18, 57),
    "Crimson":       (25, 90, 82, 22),
    "Crimson Bright":(0, 75, 78, 0),
    "Gold":          (20, 30, 70, 15),
    "Ink":           (50, 45, 45, 100),
    "Grid Line":     (2, 3, 9, 0),
}
def cid(name): return "Color/u" + name.replace(" ", "")

# ── Fonts ───────────────────────────────────────────────────────────────────
FONTS = [
    ("Spectral", ["Regular", "Medium", "SemiBold", "Italic", "Medium Italic"]),
    ("Bodoni Moda", ["Medium", "SemiBold", "Bold", "Medium Italic"]),
    ("Cormorant Garamond", ["Medium", "SemiBold", "Medium Italic", "SemiBold Italic"]),
    ("Pretendard", ["Light", "Regular", "SemiBold"]),
    ("IBM Plex Mono", ["Regular", "Medium"]),
    ("Noto Serif HK", ["Medium", "Bold"]),
    ("Noto Serif KR", ["Medium", "Bold"]),
]

# ── Paragraph styles — PRINT_SPEC §3 ─────────────────────────────────────────
# name: dict(font, style, size, leading, track(em), color, just, case)
J_LEFT, J_FULL, J_CENTER, J_RIGHT = "LeftAlign", "FullyJustified", "CenterAlign", "RightAlign"
PSTYLES = [
    # Display / titles
    ("Cover_Name",   dict(font="Spectral", style="Medium", size=13, lead=18, track=0.02, color="Charcoal Soft")),
    ("Cover_Title",  dict(font="Spectral", style="Medium", size=40, lead=46, track=-0.01, color="Charcoal")),
    ("Title-Display",dict(font="Spectral", style="Medium", size=32, lead=42, track=-0.01, color="Charcoal")),
    ("Heading",      dict(font="Spectral", style="Medium", size=22, lead=28, track=0, color="Charcoal")),
    ("Lead",         dict(font="Cormorant Garamond", style="Medium Italic", size=14, lead=21, track=0, color="Charcoal Soft")),
    # Wordmark
    ("Lockup_CJK",   dict(font="Noto Serif HK", style="Bold", size=72, lead=72, track=0.04, color="Ivory")),
    ("Lockup_Latin", dict(font="Bodoni Moda", style="SemiBold", size=22, lead=24, track=0.03, color="Ivory")),
    # Body / editorial
    ("Body",         dict(font="Pretendard", style="Light", size=9.5, lead=14, track=0, color="Charcoal", just=J_FULL)),
    ("Caption",      dict(font="Pretendard", style="Regular", size=8, lead=12, track=0, color="Ghost")),
    ("Epigraph",     dict(font="Cormorant Garamond", style="Medium Italic", size=15, lead=23, track=0, color="Charcoal Soft")),
    ("Colophon",     dict(font="IBM Plex Mono", style="Regular", size=7, lead=12, track=0.04, color="Ghost", case="upper")),
    # Meta / labels
    ("Meta",         dict(font="IBM Plex Mono", style="Regular", size=7, lead=14, track=0.08, color="Ghost", case="upper")),
    ("Eyebrow",      dict(font="IBM Plex Mono", style="Regular", size=7, lead=14, track=0.14, color="Ghost", case="upper")),
    ("Standfirst",   dict(font="IBM Plex Mono", style="Regular", size=7, lead=13, track=0.12, color="Ghost", case="upper")),
    ("Folio",        dict(font="IBM Plex Mono", style="Regular", size=8, lead=10, track=0.06, color="Ghost")),
    # Numerals
    ("MarkNum",      dict(font="Bodoni Moda", style="SemiBold", size=84, lead=76, track=-0.02, color="Gold")),
    ("Cover_Year",   dict(font="Bodoni Moda", style="SemiBold", size=64, lead=58, track=-0.02, color="Gold")),
    # TOC
    ("TOC_Num",      dict(font="Bodoni Moda", style="SemiBold", size=22, lead=24, track=0, color="Gold")),
    ("TOC_Title",    dict(font="Spectral", style="Medium", size=13, lead=16, track=0, color="Charcoal")),
    ("TOC_Stand",    dict(font="Pretendard", style="Light", size=8.5, lead=12, track=0, color="Charcoal Soft")),
    ("TOC_Meta",     dict(font="IBM Plex Mono", style="Regular", size=7, lead=12, track=0.08, color="Ghost", case="upper", just=J_RIGHT)),
    ("TOC_CJK",      dict(font="Noto Serif HK", style="Bold", size=30, lead=34, track=0, color="Charcoal")),
    # Divider (dark)
    ("Div_Num",      dict(font="Bodoni Moda", style="SemiBold", size=30, lead=34, track=0, color="Crimson Bright")),
    ("Div_Title",    dict(font="Spectral", style="Medium", size=30, lead=36, track=0, color="Ivory")),
    ("Div_CJK",      dict(font="Noto Serif HK", style="Medium", size=18, lead=22, track=0, color="Ivory")),
    ("Div_Index",    dict(font="IBM Plex Mono", style="Regular", size=7, lead=14, track=0.12, color="Ivory", case="upper")),
    # Two-voice critique
    ("Crit_Label",   dict(font="IBM Plex Mono", style="Regular", size=7, lead=12, track=0.12, color="Crimson", case="upper")),
    ("Crit_Body",    dict(font="Cormorant Garamond", style="Medium Italic", size=10.5, lead=15, track=0, color="Charcoal")),
    ("Pull",         dict(font="Cormorant Garamond", style="SemiBold Italic", size=19, lead=25, track=0, color="Crimson")),
    # Metadata
    ("Meta_Key",     dict(font="IBM Plex Mono", style="Regular", size=7, lead=12, track=0.1, color="Ghost", case="upper")),
    ("Meta_Val",     dict(font="Pretendard", style="Regular", size=8.5, lead=12, track=0, color="Charcoal")),
]
PSTYLE_NAMES = {n for n, _ in PSTYLES}

# Character styles — PRINT_SPEC §3
CSTYLES = [
    ("Cover_Title-em", dict(font="Cormorant Garamond", style="SemiBold Italic", color="Crimson")),
    ("Emph-Ivory",     dict(color="Ivory")),
    ("Caption-Bold",   dict(font="Pretendard", style="SemiBold", color="Charcoal Soft")),
    ("Hanja-Mark",     dict(font="Noto Serif HK", style="Bold", color="Crimson")),
]

def pstyle_id(n): return "ParagraphStyle/" + n
def cstyle_id(n): return "CharacterStyle/" + n

JUST_MAP = {J_LEFT: "LeftAlign", J_FULL: "FullyJustified", J_CENTER: "CenterAlign", J_RIGHT: "RightAlign"}


# ════════════════════════════════════════════════════════════════════════════
#  XML part builders
# ════════════════════════════════════════════════════════════════════════════
def xml_header():
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

def graphic_xml():
    out = [xml_header(),
           f'<idPkg:Graphic xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="{DOM}">']
    # required standard swatches
    out.append('<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" StyleParent="$ID/[Root Color Group]"/>')
    out.append('<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" Name="Paper" ColorEditable="false" ColorRemovable="false" Visible="true" StyleParent="$ID/[Root Color Group]"/>')
    out.append('<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchColorGroupReference="$ID/[Root Color Group]"/>')
    for name, (c, m, y, k) in SWATCHES.items():
        out.append(f'<Color Self="{cid(name)}" Model="Process" Space="CMYK" '
                   f'ColorValue="{c} {m} {y} {k}" Name="{escape(name)}" ColorEditable="true" '
                   f'ColorRemovable="true" Visible="true" StyleParent="$ID/[Root Color Group]"/>')
    # tint swatches used as rules
    out.append('<Ink Self="Ink/$ID/Process Cyan" Name="$ID/Process Cyan" ConvertToProcess="false" Angle="75" Frequency="70" NeutralDensity="0.61" PrintInk="true" PrintInkIndex="0" TrapOrder="1"/>')
    out.append('</idPkg:Graphic>')
    return "".join(out)

def fonts_xml():
    out = [xml_header(),
           f'<idPkg:Fonts xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="{DOM}">']
    out.append('<FontFamily Self="di1" Name="Generic">')
    for fam, styles in FONTS:
        out.append(f'<FontFamily Self="ff{abs(hash(fam))%100000}" Name="{escape(fam)}">')
        for st in styles:
            sid = f'font_{fam}_{st}'.replace(" ", "")
            out.append(f'<Font Self="{escape(sid)}" FontFamily="{escape(fam)}" Name="{escape(fam+" "+st)}" '
                       f'PostScriptName="{escape(fam.replace(" ","")+"-"+st.replace(" ",""))}" '
                       f'Status="Installed" FontStyleName="{escape(st)}" FontType="OpenTypeCFF"/>')
        out.append('</FontFamily>')
    out.append('</FontFamily>')
    out.append('</idPkg:Fonts>')
    return "".join(out)

def _props(font=None, lead=None):
    p = ["<Properties>"]
    if lead is not None:
        p.append(f'<Leading type="unit">{lead}</Leading>')
    if font is not None:
        p.append(f'<AppliedFont type="string">{escape(font)}</AppliedFont>')
    p.append("</Properties>")
    return "".join(p)

def _common_attrs(d):
    a = []
    if "size" in d: a.append(f'PointSize="{d["size"]}"')
    if d.get("style"): a.append(f'FontStyle="{escape(d["style"])}"')
    if "track" in d and d["track"]: a.append(f'Tracking="{int(round(d["track"]*1000))}"')
    if d.get("color"): a.append(f'FillColor="{cid(d["color"])}"')
    if d.get("just"): a.append(f'Justification="{d["just"]}"')
    if d.get("case") == "upper": a.append('Capitalization="AllCaps"')
    return " ".join(a)

def styles_xml():
    out = [xml_header(),
           f'<idPkg:Styles xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="{DOM}">']
    # Root style groups + required [No ...] styles
    out.append('<RootCharacterStyleGroup Self="cstyleroot">')
    out.append('<CharacterStyle Self="CharacterStyle/$ID/[No character style]" Name="$ID/[No character style]"/>')
    for n, d in CSTYLES:
        out.append(f'<CharacterStyle Self="{cstyle_id(n)}" Name="{escape(n)}" {_common_attrs(d)}>'
                   f'{_props(d.get("font"))}</CharacterStyle>')
    out.append('</RootCharacterStyleGroup>')

    out.append('<RootParagraphStyleGroup Self="pstyleroot">')
    out.append('<ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" '
               'AppliedFont="Pretendard"><Properties><AppliedFont type="string">Pretendard</AppliedFont></Properties></ParagraphStyle>')
    out.append('<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" '
               'AppliedFont="Pretendard"><Properties><AppliedFont type="string">Pretendard</AppliedFont></Properties></ParagraphStyle>')
    for n, d in PSTYLES:
        hyph = ' Hyphenation="true"' if d.get("just") == J_FULL else ""
        out.append(f'<ParagraphStyle Self="{pstyle_id(n)}" Name="{escape(n)}" {_common_attrs(d)}{hyph}>'
                   f'{_props(d.get("font"), d.get("lead"))}</ParagraphStyle>')
    out.append('</RootParagraphStyleGroup>')

    # Object styles — PRINT_SPEC §4
    out.append('<RootObjectStyleGroup Self="ostyleroot">')
    out.append('<ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]" '
               'AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]"/>')
    out.append('<ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]" '
               f'FillColor="{cid("Ivory")}" StrokeWeight="0.6" StrokeColor="{cid("Charcoal")}" '
               'AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]"/>')
    out.append('<ObjectStyle Self="ObjectStyle/ImageFrame" Name="Image Frame" '
               f'FillColor="{cid("Ivory")}" StrokeWeight="0.6" StrokeColor="{cid("Charcoal")}" '
               'AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]"/>')
    out.append('<ObjectStyle Self="ObjectStyle/FullBleed" Name="Full-Bleed Fill" StrokeWeight="0" '
               'AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]"/>')
    out.append('<ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]" '
               'AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]"/>')
    out.append('</RootObjectStyleGroup>')

    # TOC / trap presets minimal
    out.append('<TextWrapPreference Self="TextWrapPreference/0" Inverse="false" '
               'ApplyToMasterPageOnly="false" TextWrapSide="BothSides" TextWrapMode="None"/>')
    out.append('</idPkg:Styles>')
    return "".join(out)

def preferences_xml():
    return (xml_header() +
        f'<idPkg:Preferences xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="{DOM}">'
        f'<DocumentPreference PageHeight="{PAGE_H}" PageWidth="{PAGE_W}" PagesPerDocument="26" '
        f'FacingPages="true" PageOrientation="Portrait" '
        f'DocumentBleedTopOffset="{BLEED}" DocumentBleedBottomOffset="{BLEED}" '
        f'DocumentBleedInsideOrLeftOffset="{BLEED}" DocumentBleedOutsideOrRightOffset="{BLEED}" '
        f'DocumentBleedUniformSize="true" ColumnDirection="Horizontal">'
        f'<Properties><PageSize type="string">A4</PageSize></Properties></DocumentPreference>'
        f'<MarginPreference Top="{M_TOP}" Bottom="{M_BOT}" Left="{M_IN}" Right="{M_OUT}" '
        f'ColumnCount="{COLS}" ColumnGutter="{GUT}"/>'
        f'<ViewPreference HorizontalMeasurementUnits="Millimeters" VerticalMeasurementUnits="Millimeters" '
        f'RulerOrigin="PageOrigin"/>'
        f'<TextDefault AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]" AppliedFont="Pretendard"/>'
        f'</idPkg:Preferences>')


# ════════════════════════════════════════════════════════════════════════════
#  Content model — the 13 spreads (copy from Portfolio Draft.html / CONTENT_MAP)
# ════════════════════════════════════════════════════════════════════════════
# Each page: surface (paper|ink|crimson), folio, blocks [(pstyle, text)], images [(caption, x,y,w,h in mm from trim top-left)]
def P(surface="paper", folio="", blocks=None, images=None):
    return dict(surface=surface, folio=folio, blocks=blocks or [], images=images or [])

SPREADS = [
 # 01 Cover
 dict(label="Cover", no_spine=True,
   verso=P("ink", "ii", [("Meta","序 · EPIGRAPH"),
     ("Epigraph","“A drawing is a promise the building rarely keeps. This book is an account of the distance between the two — written by the person who made both.”"),
     ("Meta","無用 · In·Utile · author's note")]),
   recto=P("ink", "i", [("Cover_Name","TAEYOUNG RO · 노태영"),
     ("Meta","行 PRAXIS · 論 ESSAYS · 思 THEORY · SELF-CRITIQUE EDITION"),
     ("Lockup_CJK","無用"), ("Lockup_Latin","in utile"),
     ("Cover_Title","Arguing with my own drawings"),
     ("Standfirst","Selected works & self-critique · 2018 – 2025 · Architecture"),
     ("Standfirst","A4 / A3 · perfect-bound · edition of one"),
     ("Cover_Year","26")])),
 # 02 Contents
 dict(label="Contents",
   verso=P("paper","02",[("TOC_CJK","目次"),("Heading","Contents"),
     ("Body","Six works, three registers. 行 Praxis collects built and studio projects; 論 Essays sets two of them into argument; 思 Theory states the position the rest are measured against. A retrospective Critique runs beside every project.")]),
   recto=P("paper","03",[("Meta","行 PRAXIS · WORKS — YEAR · TYPE · PP."),
     ("TOC_Num","01"),("TOC_Title","The Unbuilt Pavilion"),("TOC_Stand","A threshold mistaken for a destination."),("TOC_Meta","2019 · Studio · p.08"),
     ("TOC_Num","02"),("TOC_Title","Threshold Housing · 사이"),("TOC_Stand","Forty units around a court I designed before its use."),("TOC_Meta","2021 · Housing · p.14"),
     ("TOC_Num","03"),("TOC_Title","Tidal Library"),("TOC_Stand","A public room that fills and empties with the river."),("TOC_Meta","2022 · Cultural · p.20"),
     ("TOC_Num","04"),("TOC_Title","Seongsu Mixed-Block"),("TOC_Stand","Internship work — and what the office overruled."),("TOC_Meta","2023 · Practice · p.26"),
     ("TOC_Num","05"),("TOC_Title","Reweaving Cheonggye"),("TOC_Stand","An urban seam I drew wider than the city wanted."),("TOC_Meta","2024 · Urban · p.30"),
     ("TOC_Num","06"),("TOC_Title","Quiet Annex"),("TOC_Stand","Thesis: a building that refuses to announce itself."),("TOC_Meta","2025 · Thesis · p.34"),
     ("Meta","論 ESSAYS · p.18    思 THEORY · p.32    歷 CV · p.38")])),
 # 03 Divider 行
 dict(label="Divider 行",
   verso=P("paper","06",[("Meta","Part One"),("Heading","Works, and what they got wrong"),
     ("Body","Six projects in the order I made them. Each opens with what it was meant to be, shows what was drawn, and ends with what I would now say to the student who drew it. The buildings do not change; only the reading does.")]),
   recto=P("ink","07",[("Div_Num","I"),("Div_Title","Praxis"),("Div_CJK","행 · 行"),
     ("Div_Index","01 Pavilion · 02 Threshold Housing · 03 Tidal Library · 04 Seongsu Block · 05 Cheonggye · 06 Quiet Annex")])),
 # 04 P01 Intro
 dict(label="P01 Intro",
   verso=P("paper","08",[("MarkNum","01"),("Meta","行 PRAXIS · DWG 01 / 12"),
     ("Title-Display","The Unbuilt Pavilion"),("Lead","A second-year studio project, revisited six years later."),
     ("Meta_Key","Year"),("Meta_Val","2019 · Studio IV"),("Meta_Key","Type"),("Meta_Val","Open pavilion · 1 bay"),
     ("Meta_Key","Role"),("Meta_Val","Sole author"),("Meta_Key","Site"),("Meta_Val","Riverbank, Sejong"),
     ("Meta_Key","Tools"),("Meta_Val","Graphite, ink on trace · model 1:50"),
     ("Body","The pavilion was conceived as a threshold rather than a destination — a frame that registers the passage of weather and light across a single open bay. The structure resolves into four points of contact with the ground.")]),
   recto=P("paper","09",[], images=[("Drop hero — pavilion render / model (3:4)", -3,-3,216,303)])),
 # 05 P01 Drawings
 dict(label="P01 Drawings",
   verso=P("paper","10",[("Caption","Fig. 01 — Long section, 1:100. Graphite & ink on trace, 2019.   行 01 / 12")],
     images=[("Key drawing — long section 1:100", 15,18,180,232)]),
   recto=P("paper","11",[("Caption","Fig. 02 — Ground plan, 1:200.    Fig. 03 — North elev., 1:200.    Fig. 04 — Eaves junction, 1:20.")],
     images=[("Ground plan 1:200", 20,18,175,120),("North elevation", 20,143,85,62),("Junction detail 1:20", 110,143,85,62)])),
 # 06 P01 Two-voice
 dict(label="P01 Two-voice",
   verso=P("paper","12",[("Eyebrow","行 PRAXIS · 01 · DESCRIPTION"),("Heading","Brief & site conditions"),
     ("Body","The proposal organises a single timber bay over a shared, top-lit threshold. Circulation runs along the north edge, leaving the south face uninterrupted for the river. The roof folds to admit indirect light while shedding rain to a central channel, and the whole resolves as one tectonic move from ground to ridge."),
     ("Body","Materials were specified as cross-laminated timber on a board-marked concrete plinth. The structure was meant to read at a distance as a frame and, up close, as a careful set of joints — a building that explains how it stands."),
     ("Caption","The pavilion was never built. It survives only as drawings and a single 1:50 model, photographed on the studio floor the night before the review.")]),
   recto=P("paper","13",[("Pull","批 “The court is beautiful in section and useless in plan.”"),
     ("Crit_Label","批 Critique · 2026"),
     ("Crit_Body","I designed the light before I designed the work that was supposed to happen under it — and it shows in how thinly the programme is described. The roof does too much; it hides an unresolved plan beneath a gesture."),
     ("Crit_Body","The drawing is honest about ambition and silent about how anyone would actually enter. Six years on, the lesson is simple and unflattering: I had drawn a mood and called it a building."),
     ("Eyebrow","What I'd keep"),
     ("Body","The instinct to make a single structural idea legible was right. The failure was scope, not sensibility — and that distinction is the reason this project opens the book.")])),
 # 07 P02 Intro
 dict(label="P02 Intro",
   verso=P("paper","14",[], images=[("Drop hero — courtyard view / model (4:5)", -3,-3,216,303)]),
   recto=P("paper","15",[("MarkNum","02"),("Meta","行 PRAXIS · COLLECTIVE HOUSING"),
     ("Title-Display","Threshold Housing 사이 주거"),("Lead","Forty units arranged around a court I designed before I understood its use."),
     ("Meta_Key","Year"),("Meta_Val","2021 · Studio VII"),("Meta_Key","Type"),("Meta_Val","Collective housing · 40 units"),
     ("Meta_Key","Role"),("Meta_Val","Sole author"),("Meta_Key","Site"),("Meta_Val","Mangwon-dong, Seoul"),
     ("Body","Three timber volumes share a single top-lit court; circulation runs the north edge so the south face stays open to the lane. The roof folds to bring indirect light to the deep plan.")])),
 # 08 P02 Drawings
 dict(label="P02 Drawings",
   verso=P("paper","16",[("Caption","Fig. 05 — Typical floor, 1:200. The court is the only space every unit must cross."),
     ("Body","Units are paired across a shared stair; each pair brackets a recessed entry — the 사이, the in-between — so that arriving home is a sequence of thresholds rather than a single door. The section keeps the court in view from every landing.")],
     images=[("Typical floor plan 1:200", 15,18,180,118)]),
   recto=P("paper","17",[("Crit_Label","批 Critique"),
     ("Crit_Body","Forty families, and I drew the court for the perspective, not for them. The thresholds are lovely and the units behind them are mean — single-aspect, deep, under-lit."),
     ("Crit_Body","I would trade two metres of court for a second window in every plan. The internship taught me that; the studio didn't.")],
     images=[("Cross-section 1:100", 20,18,95,78),("Court study model", 20,101,95,78)])),
 # 09 Divider 論
 dict(label="Divider 論",
   verso=P("paper","18",[("Meta","Part Two"),("Heading","Two projects, set against each other"),
     ("Body","Where Praxis judges projects one at a time, the essays put two in the same room. The argument here is not which is better, but what they share — and what the repetition of a mistake says about the person making it.")]),
   recto=P("ink","19",[("Div_Num","II"),("Div_Title","Essays"),("Div_CJK","론 · 論"),
     ("Div_Index","On the court, and the window it kept costing me")])),
 # 10 Essay
 dict(label="Essay",
   verso=P("paper","20",[("Eyebrow","論 ESSAY · 01"),("Heading","The court was always an excuse"),
     ("Body","Twice now I have organised a building around a beautiful void and let the rooms around it suffer. The pavilion did it with a roof; the housing did it with a court. In both, the seductive drawing arrived first and the plan was bent to keep it."),
     ("Body","This is not a problem of talent but of order — of what I let myself solve before I had earned the right to. A void is the easiest thing to draw and the hardest to justify, because it asks nothing of programme until programme is the only thing left."),
     ("Body","The correction is procedural. Plan the dark rooms first. Let the void be what remains, not what begins. The internship year, for all its frustrations, was the first time I was made to."),
     ("Crit_Label","批 Margin"),("Crit_Body","Two projects, one habit. The honest portfolio names the habit.")]),
   recto=P("paper","21",[("Pull","“A void is the easiest thing to draw and the hardest to justify.”"),
     ("Caption","Fig. 06 — Two voids, redrawn at the same scale to compare what each subtracts from its plan.")],
     images=[("Comparative diagram — pavilion roof / housing court", 20,55,175,118)])),
 # 11 Divider 思
 dict(label="Divider 思",
   verso=P("paper","32",[("Meta","Part Three"),("Heading","The position the work is measured against"),
     ("Body","A short statement of what I now think architecture is for. It is placed last on purpose: a thesis earns its right to be stated only after the work that tested it.")]),
   recto=P("ink","33",[("Div_Num","III"),("Div_Title","Theory"),("Div_CJK","사 · 思"),
     ("Div_Index","Useful uselessness · 無用 as a working method")])),
 # 12 Theory
 dict(label="Theory",
   verso=P("paper","34",[("Eyebrow","思 THEORY · STATEMENT"),("Heading","On useful uselessness"),
     ("Body","無用 — wú yòng, the useless — is not a rejection of function. It is a discipline: the part of a building that does no measurable work is the part most exposed to judgement, and therefore the part that must be most exact. A threshold carries no load and decides everything."),
     ("Body","My early projects mistook the useless for the free. They are not the same. The free is unaccountable; the useless is accountable precisely because it has no excuse. This portfolio is built to hold me to that."),
     ("Caption","無用 · the useless, drawn exactly.")]),
   recto=P("crimson","35",[("Lockup_CJK","無用"),
     ("Pull","A threshold carries no load and decides everything."),
     ("Meta","思 THEORY · 無用 — USEFUL USELESSNESS")])),
 # 13 CV
 dict(label="CV",
   verso=P("paper","38",[("Title-Display","Taeyoung Ro"),
     ("Meta","歷 EDUCATION"),
     ("Meta_Val","2019—25  M.Arch, Seoul National University · thesis: Quiet Annex"),
     ("Meta_Val","2015—19  B.Sc Architecture, Hanyang University · cum laude"),
     ("Meta","歷 PRACTICE"),
     ("Meta_Val","2023  Architecture Intern, SoA · Seongsu mixed-use, DD set"),
     ("Meta_Val","2022  Summer Intern · competition team"),
     ("Meta","歷 SKILLS & AWARDS"),
     ("Meta_Val","Tools  Rhino · AutoCAD · Affinity · hand drafting · timber & concrete modelling"),
     ("Meta_Val","2024  SNU Thesis Prize, shortlist")]),
   recto=P("paper","39",[("Meta","歷 CONTACT"),
     ("Meta_Key","Email"),("Meta_Val","taeyoung.ro@email.com"),
     ("Meta_Key","Site"),("Meta_Val","taeyoungro.work"),
     ("Meta_Key","Based"),("Meta_Val","Seoul, KR"),
     ("Colophon","無用 · IN·UTILE — TAEYOUNG RO ARCHITECTURE PORTFOLIO · DRAFT v0.1 · 2026"),
     ("Colophon","SET IN BODONI MODA · SPECTRAL · PRETENDARD · CORMORANT GARAMOND · IBM PLEX MONO · NOTO SERIF KR"),
     ("Colophon","A4 PORTRAIT / A3 LANDSCAPE · CMYK · PSO UNCOATED v3 · CRIMSON PRIME · 批 TWO-VOICE SYSTEM")])),
]

SURFACE_COLOR = {"ink": "Ink", "crimson": "Crimson"}


# ── Story + Spread builders ──────────────────────────────────────────────────
_uid = [1000]
def uid(prefix="u"):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"

stories = []  # (self, xml)

def make_story(blocks):
    """One Story holding all paragraphs of a frame, each in its paragraph style."""
    sid = uid("story")
    parts = [f'<Story Self="{sid}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">',
             '<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" '
             'FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>']
    for style, text in blocks:
        ps = pstyle_id(style) if style in PSTYLE_NAMES else "ParagraphStyle/$ID/[No paragraph style]"
        parts.append(f'<ParagraphStyleRange AppliedParagraphStyle="{ps}">')
        parts.append(f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">')
        parts.append(f'<Content>{escape(text)}</Content>')
        parts.append('</CharacterStyleRange>')
        parts.append('</ParagraphStyleRange>')
    parts.append('</Story>')
    stories.append((sid, "".join(parts)))
    return sid

def rect_path(x1, y1, x2, y2):
    return (f'<Properties><PathGeometry><GeometryPathType PathOpen="false">'
            f'<PathPointArray>'
            f'<PathPointType Anchor="{x1} {y1}" LeftDirection="{x1} {y1}" RightDirection="{x1} {y1}"/>'
            f'<PathPointType Anchor="{x1} {y2}" LeftDirection="{x1} {y2}" RightDirection="{x1} {y2}"/>'
            f'<PathPointType Anchor="{x2} {y2}" LeftDirection="{x2} {y2}" RightDirection="{x2} {y2}"/>'
            f'<PathPointType Anchor="{x2} {y1}" LeftDirection="{x2} {y1}" RightDirection="{x2} {y1}"/>'
            f'</PathPointArray></GeometryPathType></PathGeometry></Properties>')

def page_x_origin(side):
    # spread coords: recto left edge at x=0; verso occupies negative x
    return 0.0 if side == "recto" else -PAGE_W

def trim_to_spread(side, x_mm, y_mm):
    """mm from page trim top-left -> spread coords (pt)."""
    x0 = page_x_origin(side)
    return x0 + mm(x_mm), -PAGE_H / 2 + mm(y_mm)

def build_spread(idx, spec):
    sid = f"spread{idx}"
    items = []
    pages_xml = []
    # two pages: verso(left), recto(right)
    for pos, side in ((0, "verso"), (1, "recto")):
        page = spec["verso"] if side == "verso" else spec["recto"]
        pid = uid("page")
        tx = page_x_origin(side)
        # margin preference mirrored
        if side == "verso":
            left, right = M_OUT, M_IN
        else:
            left, right = M_IN, M_OUT
        pages_xml.append(
            f'<Page Self="{pid}" Name="{page["folio"]}" AppliedMaster="n" '
            f'GeometricBounds="0 0 {PAGE_H} {PAGE_W}" ItemTransform="1 0 0 1 {tx} {-PAGE_H/2}" '
            f'OverrideList="">'
            f'<MarginPreference Top="{M_TOP}" Bottom="{M_BOT}" Left="{left}" Right="{right}" '
            f'ColumnCount="{COLS}" ColumnGutter="{GUT}"/></Page>')

        # full-bleed surface fill for dark / crimson
        if page["surface"] in SURFACE_COLOR:
            col = cid(SURFACE_COLOR[page["surface"]])
            bx0 = tx - (BLEED if side == "verso" else 0)
            bx1 = tx + PAGE_W + (BLEED if side == "recto" else 0)
            by0, by1 = -PAGE_H/2 - BLEED, PAGE_H/2 + BLEED
            items.append(
                f'<Rectangle Self="{uid("bg")}" ItemLayer="layer1" ItemTransform="1 0 0 1 0 0" '
                f'AppliedObjectStyle="ObjectStyle/FullBleed" FillColor="{col}" StrokeWeight="0" '
                f'ContentType="GraphicType">{rect_path(bx0,by0,bx1,by1)}</Rectangle>')

        # picture frames
        for cap, ix, iy, iw, ih in page["images"]:
            x1, y1 = trim_to_spread(side, ix, iy)
            x2, y2 = x1 + mm(iw), y1 + mm(ih)
            fr = uid("img")
            cstory = make_story([("Caption", cap)])
            items.append(
                f'<Rectangle Self="{fr}" ItemLayer="layer1" ItemTransform="1 0 0 1 0 0" '
                f'AppliedObjectStyle="ObjectStyle/ImageFrame" '
                f'FillColor="{cid("Ivory")}" StrokeColor="{cid("Charcoal")}" StrokeWeight="0.6" '
                f'ContentType="GraphicType">{rect_path(x1,y1,x2,y2)}'
                f'<TextWrapPreference Inverse="false" ApplyToMasterPageOnly="false" TextWrapSide="BothSides" TextWrapMode="None">'
                f'<Properties><TextWrapOffset Top="0" Left="0" Bottom="0" Right="0"/></Properties></TextWrapPreference>'
                f'</Rectangle>')

        # main text frame with the page copy
        if page["blocks"]:
            story = make_story(page["blocks"])
            lx = (tx + left)
            rx = (tx + PAGE_W - right)
            ty1 = -PAGE_H/2 + M_TOP
            ty2 = PAGE_H/2 - M_BOT
            tf = uid("tf")
            items.append(
                f'<TextFrame Self="{tf}" ParentStory="{story}" ItemLayer="layer1" ItemTransform="1 0 0 1 0 0" '
                f'AppliedObjectStyle="ObjectStyle/$ID/[Normal Text Frame]" '
                f'ContentType="TextType" PreviousTextFrame="n" NextTextFrame="n">'
                f'{rect_path(lx,ty1,rx,ty2)}'
                f'<TextFramePreference TextColumnCount="1" TextColumnGutter="{GUT}" VerticalJustification="TopAlign"/>'
                f'</TextFrame>')

        # folio
        if page["folio"]:
            fcolor = "Ivory" if page["surface"] in SURFACE_COLOR else "Ghost"
            fstory = make_story([("Folio", page["folio"])])
            fx = (tx + mm(15)) if side == "verso" else (tx + PAGE_W - mm(15) - mm(20))
            fy1 = PAGE_H/2 - M_BOT + mm(2)
            ff = uid("fol")
            items.append(
                f'<TextFrame Self="{ff}" ParentStory="{fstory}" ItemLayer="layer1" ItemTransform="1 0 0 1 0 0" '
                f'ContentType="TextType" PreviousTextFrame="n" NextTextFrame="n">'
                f'{rect_path(fx, fy1, fx+mm(20), fy1+mm(6))}'
                f'<TextFramePreference TextColumnCount="1" VerticalJustification="TopAlign"/>'
                f'</TextFrame>')

    spread = (xml_header() +
        f'<idPkg:Spread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="{DOM}">'
        f'<Spread Self="{sid}" PageCount="2" BindingLocation="1" ShowMasterItems="true" '
        f'PageTransitionType="None" PageTransitionDirection="NotApplicable" PageTransitionDuration="Medium" '
        f'AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0">'
        f'<FlattenerPreference LineArtAndTextResolution="300" GradientAndMeshResolution="150" '
        f'ClipComplexRegions="false" ConvertAllStrokesToOutlines="false" ConvertAllTextToOutlines="false"/>'
        + "".join(pages_xml) + "".join(items) +
        f'</Spread></idPkg:Spread>')
    return sid, spread


# ── Layer + master ───────────────────────────────────────────────────────────
def master_xml():
    sid = "MasterSpread/A-Master"
    return (xml_header() +
        f'<idPkg:MasterSpread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="{DOM}">'
        f'<MasterSpread Self="{sid}" Name="A-Master" NamePrefix="A" BaseName="Master" '
        f'ShowMasterItems="true" PageCount="2" ItemTransform="1 0 0 1 0 0">'
        f'<Page Self="mpL" Name="A" AppliedMaster="n" GeometricBounds="0 0 {PAGE_H} {PAGE_W}" '
        f'ItemTransform="1 0 0 1 {-PAGE_W} {-PAGE_H/2}"><MarginPreference Top="{M_TOP}" Bottom="{M_BOT}" '
        f'Left="{M_OUT}" Right="{M_IN}" ColumnCount="{COLS}" ColumnGutter="{GUT}"/></Page>'
        f'<Page Self="mpR" Name="A" AppliedMaster="n" GeometricBounds="0 0 {PAGE_H} {PAGE_W}" '
        f'ItemTransform="1 0 0 1 0 {-PAGE_H/2}"><MarginPreference Top="{M_TOP}" Bottom="{M_BOT}" '
        f'Left="{M_IN}" Right="{M_OUT}" ColumnCount="{COLS}" ColumnGutter="{GUT}"/></Page>'
        f'</MasterSpread></idPkg:MasterSpread>')


def designmap(spread_ids, story_ids):
    out = [xml_header(),
           '<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="16.0(48)"?>',
           f'<Document xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" '
           f'DOMVersion="{DOM}" Self="d_inutile" StoryList="{" ".join(story_ids)}" '
           f'Name="Taeyoung_Ro_Portfolio.idml" ZeroPoint="0 0" ActiveLayer="layer1">']
    out.append('<Language Self="Language/$ID/English%3a USA" Name="$ID/English: USA" '
               'SingleQuotes="‘’" DoubleQuotes="“”" PrimaryLanguageName="$ID/English" '
               'SublanguageName="$ID/USA" Id="269" HyphenationVendor="Hunspell" SpellingVendor="Hunspell"/>')
    out.append('<idPkg:Graphic src="Resources/Graphic.xml"/>')
    out.append('<idPkg:Fonts src="Resources/Fonts.xml"/>')
    out.append('<idPkg:Styles src="Resources/Styles.xml"/>')
    out.append('<idPkg:Preferences src="Resources/Preferences.xml"/>')
    out.append('<Layer Self="layer1" Name="Layout" Visible="true" Locked="false" '
               'IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" '
               'Expendable="true" Printable="true"/>')
    out.append('<Section Self="section1" Length="26" Name="" ContinueNumbering="false" '
               'IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageStart="1"/>')
    out.append('<idPkg:MasterSpread src="MasterSpreads/MasterSpread_A-Master.xml"/>')
    for s in spread_ids:
        fn = s.replace("Spread/", "")
        out.append(f'<idPkg:Spread src="Spreads/Spread_{fn}.xml"/>')
    out.append('<idPkg:BackingStory src="XML/BackingStory.xml"/>')
    for st in story_ids:
        out.append(f'<idPkg:Story src="Stories/Story_{st}.xml"/>')
    out.append('</Document>')
    return "".join(out)


def backing_story():
    return (xml_header() +
        f'<idPkg:BackingStory xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="{DOM}">'
        f'<XmlStory Self="backingstory" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">'
        f'<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" '
        f'StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>'
        f'<InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>'
        f'</XmlStory></idPkg:BackingStory>')


def main():
    spread_ids, spread_xmls = [], []
    for i, spec in enumerate(SPREADS, 1):
        sid, sx = build_spread(i, spec)
        spread_ids.append(sid)
        spread_xmls.append((sid, sx))
    story_ids = [s for s, _ in stories]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        # mimetype MUST be first and stored (uncompressed)
        zi = zipfile.ZipInfo("mimetype")
        zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, "application/vnd.adobe.indesign-idml-package")
        z.writestr("META-INF/container.xml", xml_header() +
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="designmap.xml" '
            'media-type="text/xml"/></rootfiles></container>')
        z.writestr("designmap.xml", designmap(spread_ids, story_ids))
        z.writestr("Resources/Graphic.xml", graphic_xml())
        z.writestr("Resources/Fonts.xml", fonts_xml())
        z.writestr("Resources/Styles.xml", styles_xml())
        z.writestr("Resources/Preferences.xml", preferences_xml())
        z.writestr("MasterSpreads/MasterSpread_A-Master.xml", master_xml())
        for sid, sx in spread_xmls:
            fn = sid.replace("Spread/", "")
            z.writestr(f"Spreads/Spread_{fn}.xml", sx)
        for st, sx in stories:
            z.writestr(f"Stories/Story_{st}.xml", sx)
        z.writestr("XML/BackingStory.xml", backing_story())

    print(f"✓ IDML written → {os.path.relpath(OUT, os.getcwd())}")
    print(f"  spreads: {len(spread_ids)}  pages: {len(spread_ids)*2}  stories: {len(story_ids)}  "
          f"swatches: {len(SWATCHES)}  para-styles: {len(PSTYLES)}  char-styles: {len(CSTYLES)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the SVG artwork used by profile/README.md.

All lettering is converted to outlines, so the images render in Geist on
every machine (GitHub serves README SVGs through <img>, which cannot load
web fonts).

    pip install fonttools uharfbuzz
    python scripts/generate_assets.py               # macOS: reads ~/Library/Fonts
    python scripts/generate_assets.py --fonts DIR   # elsewhere

The fonts directory must contain the Geist variable fonts
("Geist[wght].ttf" and "GeistMono[wght].ttf", from https://vercel.com/font).
Output goes to profile/assets/, one light and one dark file per image.
"""

from __future__ import annotations

import argparse
import io
from html import escape
from dataclasses import dataclass
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "profile" / "assets"

# --------------------------------------------------------------------------
# Brand
# --------------------------------------------------------------------------

MAGENTA = "#EA258B"
VIOLET = "#BF17D9"
BLUE = "#1A73E8"
SIM = "#F29900"

THEMES = {
    "light": dict(
        bg="#FFFFFF",
        border="#E4E4E7",
        text="#09090B",
        muted="#52525B",
        faint="#A1A1AA",
        dot="#E4E4E7",
        lane="#F4F4F5",
        trace="#3F3F46",
        wave=BLUE,
        pill_bg="#F4F4F5",
        pill_text="#3F3F46",
    ),
    "dark": dict(
        bg="#0E0E10",
        border="#27272A",
        text="#FAFAFA",
        muted="#A1A1AA",
        faint="#52525B",
        dot="#232327",
        lane="#161618",
        trace="#A1A1AA",
        wave="#4C94F5",
        pill_bg="#1C1C1F",
        pill_text="#D4D4D8",
    ),
}

LOGO = (
    '<path d="M225 244.124C195.463 244.124 166.139 240.878 138.85 234.574C111.561 228.268 '
    "86.7656 219.028 65.8793 207.378C44.993 195.728 28.4251 181.897 17.1215 166.675C5.81793 "
    "151.454 0 135.14 0 118.665C0 102.189 5.81793 85.8749 17.1215 70.6536C28.4251 55.4322 "
    "44.993 41.6017 65.8793 29.9517C86.7656 18.3019 111.561 9.06055 138.85 2.75566C166.139 "
    '-3.54925 225 -7.87646 225 95.1235V118.666V244.124Z" fill="#EA258B"/>'
    '<path d="M225 244.124C271.413 244.124 315.925 252.047 348.744 266.15C381.562 280.255 400 '
    "299.383 400 319.329C400 339.275 381.818 359.442 349 373.547C316.18 387.65 225 431.134 225 "
    '362.447V319.329V244.124Z" fill="#BF17D9"/>'
)


def logo(x: float, y: float, size: float) -> str:
    s = size / 400
    return f'<g transform="translate({x} {y}) scale({s:.5f})">{LOGO}</g>'


# --------------------------------------------------------------------------
# Text to outlines
# --------------------------------------------------------------------------


@dataclass
class Face:
    tt: TTFont
    hb_font: hb.Font
    upem: int


class Fonts:
    def __init__(self, directory: Path):
        self.dir = directory
        self.cache: dict[tuple[str, int], Face] = {}

    def get(self, family: str, weight: int) -> Face:
        key = (family, weight)
        if key not in self.cache:
            path = self.dir / f"{family}[wght].ttf"
            tt = instantiateVariableFont(TTFont(path), {"wght": weight})
            buf = io.BytesIO()
            tt.save(buf)
            tt = TTFont(io.BytesIO(buf.getvalue()))
            hb_font = hb.Font(hb.Face(buf.getvalue()))
            self.cache[key] = Face(tt, hb_font, tt["head"].unitsPerEm)
        return self.cache[key]


FONTS: Fonts


def _shape(face: Face, text: str, tracking: float):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(face.hb_font, buf, {"kern": True, "liga": True})
    order = face.tt.getGlyphOrder()
    out, pen_x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((order[info.codepoint], pen_x + pos.x_offset, pos.y_offset))
        pen_x += pos.x_advance + tracking * face.upem
    return out, pen_x - tracking * face.upem


def text_width(text: str, size: float, family="Geist", weight=400, tracking=0.0) -> float:
    face = FONTS.get(family, weight)
    _, adv = _shape(face, text, tracking)
    return adv * size / face.upem


def text(
    s: str,
    x: float,
    y: float,
    size: float,
    fill: str,
    family="Geist",
    weight=400,
    tracking=0.0,
    anchor="start",
) -> str:
    """Return an outlined <path> for `s` with its baseline at y."""
    face = FONTS.get(family, weight)
    glyphs, adv = _shape(face, s, tracking)
    k = size / face.upem
    if anchor == "middle":
        x -= adv * k / 2
    elif anchor == "end":
        x -= adv * k
    gs = face.tt.getGlyphSet()
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    for name, gx, gy in glyphs:
        tp = TransformPen(pen, (k, 0, 0, -k, x + gx * k, y - gy * k))
        gs[name].draw(tp)
    d = pen.getCommands()
    return f'<path fill="{fill}" d="{d}"/>' if d else ""


# --------------------------------------------------------------------------
# Shared pieces
# --------------------------------------------------------------------------


def svg(w: int, h: int, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title>{body}</svg>\n"
    )


def dot_grid(id_: str, color: str, gap=20) -> str:
    return (
        f'<pattern id="{id_}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{color}"/></pattern>'
    )


PILL_SIZE, PILL_PAD, PILL_DOT = 15, 12, 14


def pill_width(label: str, dot: bool) -> float:
    return text_width(label, PILL_SIZE, weight=500) + PILL_PAD * 2 + (PILL_DOT if dot else 0)


def pill(x: float, y: float, label: str, t: dict, dot_color: str | None = None) -> str:
    size, pad = PILL_SIZE, PILL_PAD
    dot_w = PILL_DOT if dot_color else 0
    w = pill_width(label, bool(dot_color))
    h = 28
    out = f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{t["pill_bg"]}" stroke="{t["border"]}"/>'
    if dot_color:
        out += f'<circle cx="{x + pad + 3}" cy="{y + h / 2}" r="3.5" fill="{dot_color}"/>'
    out += text(label, x + pad + dot_w, y + 19.5, size, t["pill_text"], weight=500)
    return out


# --------------------------------------------------------------------------
# Banner
# --------------------------------------------------------------------------

W, H = 1280, 400


def wave_path(levels: list[int], x0: float, step: float, hi: float, lo: float) -> str:
    """Digital trace from a list of 0/1 levels, one per step."""
    y = lambda v: hi if v else lo
    d = f"M{x0} {y(levels[0])}"
    x = x0
    for i, v in enumerate(levels):
        if i and v != levels[i - 1]:
            d += f"V{y(v)}"
        x += step
        d += f"H{x:.1f}"
    return d


def bus(values: list[str], x0: float, step: float, top: float, bot: float, t: dict, color: str) -> str:
    """A bus lane with hex values, the usual hexagon-ended segments."""
    mid = (top + bot) / 2
    out = ""
    x = x0
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[j + 1] == values[i]:
            j += 1
        x1 = x0 + (j + 1) * step
        e = 5
        d = (
            f"M{x:.1f} {mid}L{x + e:.1f} {top}H{x1 - e:.1f}L{x1:.1f} {mid}"
            f"L{x1 - e:.1f} {bot}H{x + e:.1f}Z"
        )
        out += f'<path d="{d}" fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-width="1.6" stroke-linejoin="round"/>'
        if x1 - x > 54:
            out += text(values[i], (x + x1) / 2, mid + 5, 13, t["text"], family="GeistMono", weight=500, anchor="middle")
        x = x1
        i = j + 1
    return out


def banner(t: dict) -> str:
    b = "<defs>"
    b += dot_grid("dots", t["dot"])
    b += (
        '<clipPath id="card"><rect x="1" y="1" width="1278" height="398" rx="20"/></clipPath>'
    )
    b += "</defs>"
    b += (
        "<style>"
        "@keyframes sweep{0%{transform:translateX(0)}50%{transform:translateX(308px)}100%{transform:translateX(0)}}"
        ".cursor{animation:sweep 14s cubic-bezier(.65,0,.35,1) infinite}"
        "@media (prefers-reduced-motion:reduce){.cursor{animation:none}}"
        "</style>"
    )
    b += f'<rect x="1" y="1" width="1278" height="398" rx="20" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
    b += '<g clip-path="url(#card)">'

    # --- right: waveform panel -------------------------------------------
    px, py, pw, ph = 650, 56, 580, 288
    b += f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="url(#dots)"/>'
    b += f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="none" stroke="{t["border"]}" stroke-width="1.5"/>'
    # panel header
    b += f'<line x1="{px}" x2="{px + pw}" y1="{py + 40}" y2="{py + 40}" stroke="{t["border"]}" stroke-width="1.5"/>'
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        b += f'<circle cx="{px + 20 + i * 18}" cy="{py + 20}" r="5.5" fill="{c}"/>'
    b += text("waves.vcd", px + 84, py + 25, 14, t["muted"], family="GeistMono", weight=500)
    b += text("ibex_tb · 22.055 µs", px + pw - 18, py + 25, 13, t["faint"], family="GeistMono", anchor="end")

    names = ["clk", "rst_ni", "instr_valid", "alu_op", "result[31:0]"]
    label_x = px + 18
    x0 = px + 140
    step = 28
    n = 14
    row_h = 44
    top0 = py + 62
    for r, name in enumerate(names):
        cy = top0 + r * row_h + 14
        b += text(name, label_x, cy + 5, 13.5, t["muted"], family="GeistMono", weight=500)
        if r % 2 == 0:
            b += f'<rect x="{x0 - 8}" y="{cy - 20}" width="{pw - (x0 - px) + 8}" height="{row_h - 4}" fill="{t["lane"]}" opacity="0.55"/>'
    hi = lambda r: top0 + r * row_h + 2
    lo = lambda r: top0 + r * row_h + 26

    clk = [i % 2 for i in range(n * 2)]
    b += f'<path d="{wave_path(clk, x0, step / 2, hi(0), lo(0))}" fill="none" stroke="{t["trace"]}" stroke-width="1.6"/>'
    rst = [0, 0] + [1] * (n - 2)
    b += f'<path d="{wave_path(rst, x0, step, hi(1), lo(1))}" fill="none" stroke="{t["wave"]}" stroke-width="1.8"/>'
    valid = [0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1]
    b += f'<path d="{wave_path(valid, x0, step, hi(2), lo(2))}" fill="none" stroke="{t["wave"]}" stroke-width="1.8"/>'
    ops = ["IDLE"] * 2 + ["ADD"] * 3 + ["SLL"] * 3 + ["XOR"] * 3 + ["SUB"] * 3
    b += bus(ops, x0, step, hi(3), lo(3), t, VIOLET)
    res = ["0"] * 2 + ["0000002A"] * 3 + ["00000150"] * 3 + ["DEADBEEF"] * 3 + ["00000007"] * 3
    b += bus(res, x0, step, hi(4), lo(4), t, MAGENTA)

    # simulation cursor (sim accent), sweeps gently
    cx = x0 + step * 3.5
    cur_top = py + 46
    cur_bot = py + ph - 8
    b += '<g class="cursor">'
    b += f'<line x1="{cx}" x2="{cx}" y1="{cur_top}" y2="{cur_bot}" stroke="{SIM}" stroke-width="2"/>'
    b += f'<path d="M{cx - 6} {cur_top}h12l-6 8z" fill="{SIM}"/>'
    b += "</g>"

    # --- left: wordmark, headline, subline -------------------------------
    lx = 72
    b += logo(lx, 70, 34)
    b += text("Sigdraw", lx + 46, 98, 28, t["text"], weight=600, tracking=-0.01)
    b += text("Build Chips", lx - 3, 190, 74, t["text"], weight=700, tracking=-0.035)
    b += text("Faster.", lx - 3, 268, 74, t["text"], weight=700, tracking=-0.035)
    b += text("Native tools for hardware engineers.", lx, 318, 23, t["muted"], weight=400)
    b += text("Find bugs and ship.", lx, 349, 23, t["muted"], weight=400)

    b += "</g>"
    return svg(W, H, b, "Sigdraw — Build Chips Faster")


# --------------------------------------------------------------------------
# Project cards
# --------------------------------------------------------------------------

CW, CH = 640, 260


def icon_redstone(x: float, y: float, t: dict) -> str:
    """A tile holding a clock edge driving a gate: a simulator."""
    s = f'<rect x="{x}" y="{y}" width="52" height="52" rx="12" fill="url(#brand)"/>'
    s += (
        f'<path d="M{x + 11} {y + 34}h7v-16h8v16h7v-16h8" fill="none" stroke="#fff" '
        f'stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    return s


def icon_rainglass(x: float, y: float, t: dict) -> str:
    """Stacked translucent panes: layers composited into a UI."""
    s = f'<rect x="{x}" y="{y}" width="52" height="52" rx="12" fill="url(#brand)"/>'
    s += f'<rect x="{x + 11}" y="{y + 11}" width="22" height="22" rx="4" fill="#fff" fill-opacity="0.45"/>'
    s += f'<rect x="{x + 19}" y="{y + 19}" width="22" height="22" rx="4" fill="#fff" fill-opacity="0.95"/>'
    return s


def card(t: dict, name: str, icon, status: str, lines: list[str], meta: str, title: str) -> str:
    b = "<defs>"
    b += dot_grid("dots", t["dot"])
    b += (
        '<linearGradient id="brand" x1="0" x2="1" y1="0" y2="1">'
        f'<stop offset="0" stop-color="{MAGENTA}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
    )
    b += "</defs>"
    b += f'<rect x="1" y="1" width="{CW - 2}" height="{CH - 2}" rx="18" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
    b += icon(36, 36, t)
    b += text(name, 104, 72, 32, t["text"], weight=600, tracking=-0.02)
    # status pill, top-right
    pw = pill_width(status, dot=True)
    b += pill(CW - 36 - pw, 47, status, t, dot_color=SIM)
    for i, line in enumerate(lines):
        b += text(line, 36, 138 + i * 32, 23, t["muted"])
    b += f'<line x1="36" x2="{CW - 36}" y1="198" y2="198" stroke="{t["border"]}" stroke-width="1.5"/>'
    b += text(meta, 36, 232, 17, t["faint"], family="GeistMono", weight=500)
    return svg(CW, CH, b, title)


# --------------------------------------------------------------------------


def main() -> None:
    global FONTS
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", type=Path, default=Path.home() / "Library" / "Fonts")
    args = ap.parse_args()
    FONTS = Fonts(args.fonts.expanduser())
    OUT.mkdir(parents=True, exist_ok=True)

    for mode, t in THEMES.items():
        (OUT / f"banner-{mode}.svg").write_text(banner(t), encoding="utf-8")
        (OUT / f"redstone-{mode}.svg").write_text(
            card(
                t,
                "Redstone",
                icon_redstone,
                "Pre-alpha · Coming soon",
                ["A SystemVerilog simulator written in Rust.", "Four-state, multithreaded, built on slang."],
                "Rust · IEEE 1800-2017/2023 · MIT OR Apache-2.0",
                "Redstone — a SystemVerilog simulator written in Rust",
            ),
            encoding="utf-8",
        )
        (OUT / f"rainglass-{mode}.svg").write_text(
            card(
                t,
                "Rainglass",
                icon_rainglass,
                "Early · Coming soon",
                ["A UI framework for Rust, drawn on the GPU.", "Headless core, wgpu renderer, themes as data."],
                "Rust · wgpu · MIT OR Apache-2.0",
                "Rainglass — a UI framework for Rust",
            ),
            encoding="utf-8",
        )
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()

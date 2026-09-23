"""Sinh file .ass cho caption kieu top-band vertical.

Tai sao dung ASS chu khong phai drawtext:
  - drawtext khong lam duoc animation (whip-in, typewriter, pop overshoot).
  - libass ho tro \\move, \\frz, \\t, \\clip -> tai tao duoc DUNG cac hieu ung
    da do tu video mau, va \\clip dong chinh la typewriter wipe trai->phai.
  - Mot file .ass burn o pass cuoi = caption luon nam TREN moi overlay.

Toa do ASS = toa do pixel that vi PlayResX/Y dat bang kich thuoc canvas.
"""

from __future__ import annotations

import os
from typing import Any

try:
    from PIL import ImageFont
except Exception:  # pragma: no cover
    ImageFont = None


# ---------------------------------------------------------------- mau sac ---

def _rgb(hexstr: str) -> tuple[int, int, int]:
    h = hexstr.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def ass_color(hexstr: str, alpha: int = 0) -> str:
    """ASS dung thu tu &HAABBGGRR - dao nguoc so voi hex RGB thong thuong."""
    r, g, b = _rgb(hexstr)
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"


def ass_color_inline(hexstr: str) -> str:
    r, g, b = _rgb(hexstr)
    return f"&H{b:02X}{g:02X}{r:02X}&"


def _ts(t: float) -> str:
    if t < 0:
        t = 0.0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


# ------------------------------------------------------------- do rong chu ---

class TextMeasurer:
    """Do be rong chu bang chinh font se render, de hop nen om sat chu.

    Video mau cho thay hop caption TU CO GIAN theo do dai chu (hop hep cho dong
    ngan, rong cho dong dai) - nen phai do that chu khong uoc luong.
    """

    def __init__(self, font_file: str | None):
        self.font_file = font_file if font_file and os.path.exists(font_file) else None
        self._cache: dict[tuple[str, int], tuple[int, int]] = {}
        if self.font_file is None:
            print(f"[assgen] CANH BAO: khong tim thay font file ({font_file}). "
                  "Be rong hop caption se uoc luong tho.")

    def size(self, text: str, px: int) -> tuple[int, int]:
        key = (text, px)
        if key in self._cache:
            return self._cache[key]
        if self.font_file and ImageFont is not None:
            f = ImageFont.truetype(self.font_file, px)
            box = f.getbbox(text)
            out = (box[2] - box[0], box[3] - box[1])
        else:
            out = (int(len(text) * px * 0.46), int(px * 0.74))
        self._cache[key] = out
        return out


# ------------------------------------------------------------------ header ---

def ass_header(cfg: dict[str, Any]) -> str:
    W = cfg["canvas"]["width"]
    H = cfg["canvas"]["height"]
    fam = cfg["font"]["family"]
    size = int(cfg["caption"]["size_ratio"] * H)
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,{fam},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,6,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _ev(layer: int, start: float, end: float, text: str) -> str:
    return f"Dialogue: {layer},{_ts(start)},{_ts(end)},Base,,0,0,0,,{text}\n"


# -------------------------------------------------------------- animations ---

def _anim_tags(anim: str, dur_ms: int, x: int, y: int,
               clip_box: tuple[int, int, int, int] | None) -> str:
    """Sinh tag animation vao. dur_ms = do dai animation, khong phai do dai caption."""
    if anim == "typewriter" and clip_box:
        x1, y1, x2, y2 = clip_box
        return (f"\\clip({x1},{y1},{x1},{y2})"
                f"\\t(0,{dur_ms},\\clip({x1},{y1},{x2},{y2}))")
    if anim == "wipe" and clip_box:
        x1, y1, x2, y2 = clip_box
        return (f"\\clip({x1},{y1},{x1},{y2})"
                f"\\t(0,{dur_ms},\\clip({x1},{y1},{x2},{y2}))")
    if anim == "whip":
        # Bay vao tu ngoai khung trai, xoay -20deg -> 0, giong video mau.
        return (f"\\move({x - 900},{y + 120},{x},{y},0,{dur_ms})"
                f"\\frz-20\\t(0,{dur_ms},\\frz0)")
    if anim == "pop":
        a = int(dur_ms * 0.55)
        return (f"\\fscx85\\fscy85"
                f"\\t(0,{a},\\fscx120\\fscy120)"
                f"\\t({a},{dur_ms},\\fscx100\\fscy100)")
    return ""


# ------------------------------------------------------------------ styles ---

def _resolve(cfg: dict, name: str, default: str | None = None) -> str | None:
    if name is None:
        return default
    return cfg["colors"].get(name, name)


def render_caption(cfg: dict, cap: dict, t0: float, t1: float,
                   meas: TextMeasurer) -> list[str]:
    """Dung cac dong Dialogue cho mot caption.

    cap = {"lines": [...], "style": "edu", "anim": "typewriter",
           "attribution": "...", "box_colors": [...]}
    lines co the la chuoi, hoac dict {"text":..., "color":...}.
    """
    W = cfg["canvas"]["width"]
    H = cfg["canvas"]["height"]
    st = cfg["styles"][cap.get("style", "edu")]

    base_px = int(cfg["caption"]["size_ratio"] * H * st.get("size_mult", 1.0))
    line_h = int(base_px * cfg["caption"]["line_spacing"])
    baseline = int(cfg["caption"]["baseline_ratio"] * H)

    raw = cap["lines"]
    lines: list[dict] = []
    line_colors = st.get("line_colors")
    for i, ln in enumerate(raw):
        if isinstance(ln, str):
            col = None
            if line_colors:
                col = line_colors[min(i, len(line_colors) - 1)]
            lines.append({"text": ln, "color": col or st["fill"]})
        else:
            col = ln.get("color") or (line_colors[min(i, len(line_colors) - 1)]
                                      if line_colors else st["fill"])
            lines.append({"text": ln["text"], "color": col})

    n = len(lines)
    # Khoi chu neo DAY o baseline -> dong cuoi nam ngay tren duong seam.
    centers = [baseline - (n - 1 - i) * line_h - base_px // 2 for i in range(n)]

    anim = cap.get("anim") or st.get("anim") or "wipe"
    anim_ms = int(cap.get("anim_ms", 450))
    events: list[str] = []

    box_name = st.get("box")
    if box_name:
        box_col = _resolve(cfg, cap.get("box_color") or box_name)
        pad_x, pad_y = st.get("box_pad", [38, 22])
        widths = [meas.size(l["text"], base_px)[0] for l in lines]
        bw = max(widths) + pad_x * 2
        bw = min(bw, int(W * cfg["caption"]["max_width_ratio"]))
        top = centers[0] - base_px // 2 - pad_y
        bot = centers[-1] + base_px // 2 + pad_y
        bh = bot - top
        bx = (W - bw) // 2

        bord = ""
        if st.get("box_border"):
            bord = (f"\\bord{st.get('box_border_w', 3)}"
                    f"\\3c{ass_color_inline(_resolve(cfg, st['box_border']))}")
        else:
            bord = "\\bord0"

        clip = (bx, top, bx + bw, bot)
        tags = _anim_tags("wipe" if anim in ("wipe", "typewriter") else anim,
                          int(anim_ms * 0.45), W // 2, (top + bot) // 2, clip)
        shape = f"m 0 0 l {bw} 0 l {bw} {bh} l 0 {bh}"
        events.append(_ev(
            0, t0, t1,
            f"{{\\an7\\pos({bx},{top})\\1c{ass_color_inline(box_col)}"
            f"{bord}\\shad0{tags}\\p1}}{shape}{{\\p0}}"))

        # Dau ngoac kep trang tri cho style quote.
        if st.get("quote_marks"):
            qc = ass_color_inline(_resolve(cfg, st["quote_marks"]))
            qs = int(base_px * 1.5)
            events.append(_ev(
                1, t0, t1,
                f"{{\\an7\\pos({bx + 14},{top - 6})\\fs{qs}\\1c{qc}\\bord0\\shad0}}“"))
            events.append(_ev(
                1, t0, t1,
                f"{{\\an1\\pos({bx + bw - 14},{bot + 10})\\fs{qs}\\1c{qc}\\bord0\\shad0}}”"))

    # Cac dong chu. Hop wipe truoc, chu hien sau -> tre text_delay.
    text_delay = int(anim_ms * 0.35) if box_name else 0
    for i, ln in enumerate(lines):
        cy = centers[i]
        w, _ = meas.size(ln["text"], base_px)
        w = min(w, int(W * cfg["caption"]["max_width_ratio"]))
        clip = (W // 2 - w // 2 - 8, cy - base_px, W // 2 + w // 2 + 8, cy + base_px)

        # Dong sau tre ~2 frame so voi dong truoc (do duoc tren video mau).
        stagger = i * 0.035
        tags = _anim_tags(anim, anim_ms, W // 2, cy, clip)

        col = ass_color_inline(_resolve(cfg, ln["color"]))
        ow = st.get("outline_w", 0)
        oc = st.get("outline")
        deco = f"\\bord{ow}" + (f"\\3c{ass_color_inline(_resolve(cfg, oc))}" if oc and ow else "")
        sh = st.get("shadow", 0)
        deco += f"\\shad{sh}" + (f"\\4c{ass_color_inline('#000000')}" if sh else "")

        events.append(_ev(
            2, t0 + text_delay / 1000.0 + stagger, t1,
            f"{{\\an5\\pos({W // 2},{cy})\\fs{base_px}\\1c{col}{deco}{tags}}}{ln['text']}"))

    if cap.get("attribution"):
        ac = ass_color_inline(_resolve(cfg, st.get("attribution_color", "white")))
        ay = centers[-1] + line_h
        events.append(_ev(
            2, t0 + 0.25, t1,
            f"{{\\an5\\pos({W // 2},{ay})\\fs{int(base_px * 0.42)}\\1c{ac}"
            f"\\bord0\\shad0\\fsp4}}{cap['attribution']}"))

    return events


def build_ass(cfg: dict, beats: list[dict], meas: TextMeasurer) -> str:
    out = [ass_header(cfg)]
    for b in beats:
        cap = b.get("caption")
        if not cap or not cap.get("lines"):
            continue
        t0 = b["start"] + float(cap.get("offset", 0.0))
        t1 = b["end"] if cap.get("hold_to_end", True) else t0 + float(cap.get("dur", 2.0))
        if cap.get("dur"):
            t1 = t0 + float(cap["dur"])
        out.extend(render_caption(cfg, cap, t0, max(t1, t0 + 0.4), meas))
    return "".join(out)


def build_endcard_ass(cfg: dict, lines: list[str], dur: float) -> str:
    """End card co ASS rieng vi no render tren clip rieng, toa do doc lap."""
    H = cfg["canvas"]["height"]
    W = cfg["canvas"]["width"]
    ec = cfg["endcard"]
    px = int(ec["size_ratio"] * H)
    lh = int(px * 1.30)
    n = len(lines)
    cy0 = H // 2 - (n - 1) * lh // 2
    col = ass_color_inline(_resolve(cfg, ec.get("text_color", "white")))
    out = [ass_header(cfg)]
    for i, ln in enumerate(lines):
        y = cy0 + i * lh
        # Scale-up ease-out ~2s nhu video mau.
        tags = "\\fscx70\\fscy70\\t(0,900,\\fscx100\\fscy100)"
        out.append(_ev(2, 0.0, dur,
                       f"{{\\an5\\pos({W // 2},{y})\\fs{px}\\1c{col}\\bord0\\shad0{tags}}}{ln}"))
    return "".join(out)

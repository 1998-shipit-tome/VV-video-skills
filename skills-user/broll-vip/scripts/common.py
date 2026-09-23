# -*- coding: utf-8 -*-
"""Lop dung chung cho ca hai bo cuc Broll Top va Broll Vip.

Moi tham so doc tu preset.json — KHONG hardcode con so trong code.
"""
import json, os, re, subprocess, sys, time, unicodedata
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PRESET = json.loads((HERE / "preset.json").read_text(encoding="utf-8"))
CV = PRESET["canvas"]
W, H, FPS = CV["w"], CV["h"], CV["fps"]
CS = PRESET["caption_style"]
ENC = PRESET["encode"]
COL = CS["colors"]
SS = 4                                     # sieu lay mau khi ve mat na / vien
TRANSPARENT = "color=black@0.0:s=%dx%d:r=%d,format=yuva444p10le" % (W, H, FPS)


def font_path():
    for p in (HERE / CS["font"],
              HERE.parent.parent.parent.parent / "tinh-media-workflow" / "pipeline" / "fonts" / CS["font"],
              Path(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts")) / CS["font"]):
        if p.exists():
            return str(p)
    raise SystemExit("Khong tim thay font %s — chep vao scripts/" % CS["font"])


FONT = font_path()


# ---------------------------------------------------------------- tien ich
def run(cmd, out=None):
    """Chay ffmpeg. Neu co `out`: ghi ten tam roi doi ten (ghi nguyen tu).

    LOI DA GAP: tien trinh bi giet giua chung de lai file ghi do; ham kiem tra
    "da xong chua" chi xet kich thuoc nen nhan nham la hop le, concat dung ngay
    tai do -> track cut con 55s tren tong 333s.
    """
    if out is not None:
        tmp = str(Path(out).with_name(".part_" + Path(out).name))
        cmd = [tmp if c == str(out) else c for c in cmd]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.stderr.write(" ".join(str(c) for c in cmd[:14]) + "\n")
        sys.stderr.write((r.stderr or "")[-2500:] + "\n")
        raise SystemExit(1)
    if out is not None:
        for _ in range(6):
            try:
                if os.path.exists(out):
                    os.remove(out)
                os.replace(tmp, out)
                return
            except PermissionError:
                time.sleep(1.5)      # Windows: file dang bi trinh chi muc/antivirus giu
        raise SystemExit("khong doi ten duoc: %s" % out)


def nf(t):
    return max(1, round(t * FPS))


def dur_of(p):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def frames_of(p, count=False):
    a = (["-count_frames", "-show_entries", "stream=nb_read_frames"] if count
         else ["-show_entries", "stream=nb_frames"])
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", *a,
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout
    return int((o.strip().rstrip(",").split(",") or ["0"])[0] or 0)


def ease(t):
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def layout(style):
    L = PRESET["layouts"][style]
    c = L["card"]
    return L, c["w"], c["h"], c["x"], c["y"]


# ---------------------------------------------------------------- mat na / vien
def mask_ring(cw, ch, radius, border):
    """Tra (mat na 'L', vong vien 'RGBA'). Ca hai dung CHUNG bien ngoai.

    LOI DA GAP: mat na ve tren [0,0,W,H] con vong vien ve tren [B/2,...] — hai
    duong cong khac nhau nen B-roll tho ra ngoai mep trang o goc bo.
    Ve o 4x roi thu nho de khu rang cua.
    """
    if radius <= 0 and border <= 0:
        m = Image.new("L", (cw, ch), 255)
        return m, Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    w, h, r, b = cw * SS, ch * SS, radius * SS, border * SS
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    inner = Image.new("L", (w, h), 0)
    ImageDraw.Draw(inner).rounded_rectangle([b, b, w - 1 - b, h - 1 - b], max(r - b, 0), fill=255)
    a = (np.asarray(m).astype(int) - np.asarray(inner).astype(int)).clip(0, 255).astype("uint8")
    ring = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    col = PRESET["layouts"]["vip"].get("border_color", [255, 255, 255])
    ring.paste(tuple(col) + (255,), (0, 0, w, h))
    ring.putalpha(Image.fromarray(a))
    return (m.resize((cw, ch), Image.LANCZOS), ring.resize((cw, ch), Image.LANCZOS))


# ---------------------------------------------------------------- caption
def cap_parts(lines):
    """'*' la CONG TAC bat/tat chay xuyen suot ca khoi caption.

    Hai loi ich: tu khoa vat qua 2 dong van to dung mau, va MOI dau '*' deu bi
    nuot ke ca dau le -> khong bao gio lot len man hinh.
    """
    out, kw = [], False
    for line in lines:
        parts, buf = [], ""
        for ch in line:
            if ch == "*":
                if buf:
                    parts.append((buf, kw))
                    buf = ""
                kw = not kw
            else:
                buf += ch
        if buf:
            parts.append((buf, kw))
        out.append(parts)
    return out


def cap_repair(d1, d2):
    """Dien not dau '*' con thieu + chuan hoa space khong ngat.

    Quy tac: DAU DINH LIEN PHIA NAO THI THUOC PHIA DO.
      'CHONG DUOC *OXY HOA MO' -> dau mo  -> tu khoa chay toi het dong
      'NHIEU BANG SANG CHE*'   -> dau dong -> tu khoa tinh tu dau dong
      'VAO CO THE *'           -> lung hai phia -> bo dau, HOI lai nguoi dung
    """
    notes = []
    a, b = (d1 or ""), (d2 or "")
    if "\xa0" in a + b:
        a, b = a.replace("\xa0", " "), b.replace("\xa0", " ")
        notes.append("doi space khong ngat thanh space thuong")
    if (a + b).count("*") % 2 == 0:
        return a, b, notes

    def fix(line):
        if line.count("*") % 2 == 0:
            return line, None
        i = line.index("*")
        right, left = line[i + 1:i + 2], (line[i - 1:i] if i else "")
        if right and right != " ":
            return line + "*", "them dau dong cuoi dong"
        if left and left != " ":
            return "*" + line, "them dau mo dau dong"
        return line.replace("*", "", 1), "bo dau * lung — NEN HOI LAI nguoi dung"

    a, n1 = fix(a)
    if (a + b).count("*") % 2 == 1:
        b, n2 = fix(b)
        if n2:
            notes.append(n2)
    if n1:
        notes.append(n1)
    return a, b, notes


def cap_img(d1, d2, variant):
    """Ve khoi caption ra anh RGBA (da can giua ngang trong khung)."""
    d1, d2, _ = cap_repair(d1, d2)
    lines = [l.upper() for l in (d1, d2) if l]
    if not lines:
        return None
    sch = CS["scheme"].get(variant, CS["scheme"]["product"])
    size = CS["size_1line"] if len(lines) == 1 else CS["size_2line"]
    px, py, gap, rad, mar = CS["pad_x"], CS["pad_y"], CS["line_gap"], CS["radius"], CS["margin"]
    while size >= CS["size_min"]:
        f = ImageFont.truetype(FONT, size)
        if all(f.getbbox(l.replace("*", ""))[2] + 2 * px <= W - 2 * mar for l in lines):
            break
        size -= 2
    font = ImageFont.truetype(FONT, size)
    asc, desc = font.getmetrics()
    lh = asc + desc
    boxes = []
    for i, (line, parts) in enumerate(zip(lines, cap_parts(lines))):
        names = sch[i] if i < len(sch) else sch[-1]
        bg, fg, kw = (COL[n] for n in names)
        w = sum(font.getbbox(t)[2] - font.getbbox(t)[0] for t, _ in parts)
        boxes.append((parts, bg, fg, kw, w + 2 * px, lh + 2 * py))
    th = sum(b[5] for b in boxes) + gap * (len(boxes) - 1)
    img = Image.new("RGBA", (W, th), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    y = 0
    for parts, bg, fg, kw, bw, bh in boxes:
        x0 = (W - bw) // 2
        dr.rounded_rectangle([x0, y, x0 + bw, y + bh], rad, fill=bg)
        x = x0 + px
        for t, is_kw in parts:
            dr.text((x, y + py), t, font=font, fill=(kw if is_kw else fg))
            x += font.getbbox(t)[2] - font.getbbox(t)[0]
        y += bh + gap
    return img


def cap_ref_height():
    """Chieu cao khoi 2 dong chuan — moc de neo theo TAM (bo cuc top)."""
    f = ImageFont.truetype(FONT, CS["size_2line"])
    asc, desc = f.getmetrics()
    return 2 * (asc + desc + 2 * CS["pad_y"]) + CS["line_gap"]


def cap_y(style, img_h):
    """Toa do Y de dat khoi caption, theo kieu neo cua tung bo cuc."""
    L = PRESET["layouts"][style]["caption"]
    if L["anchor"] == "bottom":
        return L["y"] - img_h            # chu moc LEN TREN — khong de len the
    return L["y"] + max(0, (cap_ref_height() - img_h) // 2)   # neo TAM


# ---------------------------------------------------------------- doan B-roll
def segments(plan):
    """Gop nhip co B-roll thanh doan.

    - nhip lien nhau dung CUNG file -> MOT doan lien tuc, khong tua lai
    - hai B-roll lien nhau -> LUON khep kin, khong de ho frame nao
    - co nhip CO Y bo trong chen giua -> giu khoang trong, KHONG bac cau
    """
    segs, blank = [], False
    for r in plan:
        if not r.get("path"):
            blank = True
            continue
        t0, t1 = r.get("t", r.get("t0")), r.get("t_end", r.get("t1"))
        if segs and segs[-1]["src"] == r["path"] and not blank:
            segs[-1]["e"] = nf(t1)
            continue
        if segs and not blank:
            segs[-1]["e"] = nf(t0)
        blank = False
        segs.append({"s": nf(t0), "e": nf(t1), "src": r["path"],
                     "off": float(r.get("src_start") or r.get("off") or 0)})
    return segs


def fill_vf(cw, ch):
    """Lap kin khung the: phong vua BE NGANG roi cat tren/duoi. Khong bao gio pad den.

    fps=%d BAT BUOC: hau het clip nguon la 30fps. Thieu no thi -frames:v n ngon
    n frame NGUON (= n/30 giay) -> B-roll chay nhanh gap doi va troi don ca track.
    """
    return ("scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,fps=%d"
            % (cw, ch, cw, ch, FPS))


def is_img(p):
    return Path(p).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}


def src_args(src, off, n):
    """Tra (tien to, tham so -ss). Loop nguon neu khong du frame."""
    if is_img(src):
        return ["-loop", "1"], []
    loop = (dur_of(src) - off) < (n / FPS) + 0.10
    return (["-stream_loop", "-1"] if loop else []), ["-ss", "%.3f" % off]

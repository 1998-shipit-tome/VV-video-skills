# -*- coding: utf-8 -*-
"""Render B-roll + caption cho video doc 1080x1920. MOT bo code, HAI bo cuc.

    python render.py <plan.json> <aroll.mp4> --style top|vip [--out-dir DIR]
                     [--name TEN] [--overlay] [--card-only] [--caption-only]

Mac dinh xuat 2 lop:
    <ten>_broll.mp4      A-roll + B-roll burn san (H.264, co tieng) — de xem duyet
    <ten>_caption.mov    chi chu, nen trong suot (ProRes 4444)

--overlay        xuat them <ten>_broll_overlay.mov (lop B-roll rieng, alpha that)
--card-only      chi dung lai lop hinh
--caption-only   chi dung lai lop chu

plan.json: [{t, t_end, d1, d2, variant, path, src_start, note}, ...]
"""
import argparse, json, shutil, sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ENC, FPS, H, PRESET, TRANSPARENT, W, cap_img, cap_y, dur_of,
                    ease, fill_vf, layout, mask_ring, nf, run, segments, src_args)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def card_png(src, off, n, out_dir, cw, ch):
    out_dir.mkdir(parents=True, exist_ok=True)
    pre, ss = src_args(src, off, n)
    run(["ffmpeg", "-y", "-v", "error", *pre, *ss, "-i", str(src),
         "-frames:v", str(n), "-vf", fill_vf(cw, ch), str(out_dir / "%05d.png")])
    return sorted(out_dir.glob("*.png"))


def static_card(src, off, n, out, tmp, cw, ch, cx, cy):
    """Doan the DUNG YEN — ffmpeg lam het.

    THU TU BAT BUOC: cat the (con DUC) -> phu vien LEN NEN DUC -> bo goc ->
    PAD vao khung. KHONG dung overlay len nen trong suot: mau se bi NHAN VOI
    ALPHA lam the toi han (do duoc 31 so voi 125 cua clip goc).
    """
    pre, ss = src_args(src, off, n)
    fc = ("[0:v]%s,format=rgba[c];[c][2:v]overlay=0:0:format=auto[cr];"
          "[1:v]format=gray[m];[cr][m]alphamerge,"
          "pad=%d:%d:%d:%d:color=0x00000000,format=yuva444p10le[v]"
          % (fill_vf(cw, ch), W, H, cx, cy))
    run(["ffmpeg", "-y", "-v", "error", *pre, *ss, "-i", str(src),
         "-loop", "1", "-i", str(tmp / "mask.png"),
         "-loop", "1", "-i", str(tmp / "ring.png"),
         "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n),
         *PRESET["encode"]["prores"], str(out)], out=out)


def blank(n, out):
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", TRANSPARENT,
         "-frames:v", str(n), *PRESET["encode"]["prores"], str(out)], out=out)


def build_card_layer(plan, total, tmp, style, mask, ring):
    """Lop hinh o KHUNG DAY DU co alpha, ghep tu 3 loai doan."""
    L, cw, ch, cx, cy = layout(style)
    push = L.get("push_frames", 0) if L.get("anim") == "push" else 0
    gap = L.get("push_gap", 0)
    segs = segments(plan)
    print("%d doan B-roll" % len(segs))
    parts, cur = [], 0
    for i, sg in enumerate(segs):
        s, e = max(sg["s"], cur), sg["e"]
        if e <= s:
            continue
        if s > cur:
            p = tmp / ("g%04d.mov" % i)
            blank(s - cur, p)
            parts.append(p)

        npush = min(push, e - s) if push else 0
        if npush:
            fdir = tmp / ("f%04d" % i)
            fr_new = card_png(sg["src"], sg["off"], npush, fdir, cw, ch)
            fr_old = []
            if i > 0 and s == cur:
                prev = segs[i - 1]
                pdir = tmp / ("p%04d" % i)
                fr_old = card_png(prev["src"], prev["off"] + (prev["e"] - prev["s"]) / FPS,
                                  npush, pdir, cw, ch)
            xdir = tmp / ("x%04d" % i)
            xdir.mkdir()
            step = cw + gap
            for k in range(npush):
                canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                dx = int(ease((k + 1) / npush) * step)
                if fr_old:
                    c = Image.open(fr_old[min(k, len(fr_old) - 1)]).convert("RGBA")
                    c.putalpha(mask)
                    c.alpha_composite(ring)
                    canvas.alpha_composite(c, (cx - dx, cy))
                c = Image.open(fr_new[min(k, len(fr_new) - 1)]).convert("RGBA")
                c.putalpha(mask)
                c.alpha_composite(ring)
                canvas.alpha_composite(c, (cx + step - dx, cy))
                canvas.save(xdir / ("%05d.png" % k))
            p = tmp / ("b%04d.mov" % i)
            run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                 "-i", str(xdir / "%05d.png"), "-frames:v", str(npush),
                 *PRESET["encode"]["prores"], str(p)], out=p)
            parts.append(p)
            for d in (fdir, tmp / ("p%04d" % i), xdir):
                shutil.rmtree(d, ignore_errors=True)

        rest = (e - s) - npush
        if rest > 0:
            q = tmp / ("s%04d.mov" % i)
            static_card(sg["src"], sg["off"] + npush / FPS, rest, q, tmp, cw, ch, cx, cy)
            parts.append(q)
        cur = e
        sys.stdout.write("  hinh %d/%d ... %.1fs   \r" % (i + 1, len(segs), cur / FPS))
        sys.stdout.flush()
    if total > cur:
        p = tmp / "gz.mov"
        blank(total - cur, p)
        parts.append(p)
    print("")
    lst = tmp / "l1.txt"
    lst.write_text("".join("file '%s'\n" % p.resolve().as_posix() for p in parts), encoding="utf-8")
    card = tmp / "cardlayer.mov"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(card)], out=card)
    return card


def build_caption_layer(plan, total, tmp, style, out):
    parts, cur = [], 0
    caps = [r for r in plan if r.get("d1") or r.get("d2")]
    sl, sf = PRESET["caption_style"]["slide_px"], PRESET["caption_style"]["slide_frames"]
    for i, r in enumerate(caps):
        t0, t1 = r.get("t", r.get("t0")), r.get("t_end", r.get("t1"))
        s, e = nf(t0), nf(t1)
        if s - cur >= 2:
            p = tmp / ("cg%04d.mov" % i)
            blank(s - cur, p)
            parts.append(p)
        else:
            s = cur
        if e <= s:
            continue
        img = cap_img(r.get("d1", ""), r.get("d2", ""), r.get("variant", "product"))
        png = tmp / ("cap%04d.png" % i)
        img.save(png)
        n, fi = e - s, min(sf, e - s)
        x = "if(lt(n,%d),-%d+%d*n/%d,0)" % (fi, sl, sl, fi)
        fc = ("[1:v]format=rgba[c];[0:v][c]overlay=x='%s':y=%d:format=auto,"
              "format=yuva444p10le" % (x, cap_y(style, img.height)))
        p = tmp / ("cc%04d.mov" % i)
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", TRANSPARENT,
             "-loop", "1", "-i", str(png), "-frames:v", str(n),
             "-filter_complex", fc, *PRESET["encode"]["prores"], str(p)], out=p)
        parts.append(p)
        cur = e
        sys.stdout.write("  chu %d/%d   \r" % (i + 1, len(caps)))
        sys.stdout.flush()
    if total - cur >= 2:
        p = tmp / "cgz.mov"
        blank(total - cur, p)
        parts.append(p)
    print("")
    lst = tmp / "l2.txt"
    lst.write_text("".join("file '%s'\n" % p.resolve().as_posix() for p in parts), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(out)], out=out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("aroll")
    ap.add_argument("--style", choices=["top", "vip"], required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--name", default=None)
    ap.add_argument("--overlay", action="store_true")
    ap.add_argument("--card-only", action="store_true")
    ap.add_argument("--caption-only", action="store_true")
    a = ap.parse_args()

    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    aroll = Path(a.aroll)
    outdir = Path(a.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    name = a.name or aroll.stem.replace(" ", "_")
    total = nf(dur_of(aroll))
    L, cw, ch, cx, cy = layout(a.style)
    tmp = outdir / ("_tmp_%s" % name)
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    mask, ring = mask_ring(cw, ch, L.get("radius", 0), L.get("border", 0))
    mask.save(tmp / "mask.png")
    ring.save(tmp / "ring.png")
    print("bo cuc %s — the %dx%d tai (%d,%d) — %d frame" % (a.style, cw, ch, cx, cy, total))

    if not a.caption_only:
        card = build_card_layer(plan, total, tmp, a.style, mask, ring)
        if a.overlay:
            ov = outdir / ("%s_broll_overlay.mov" % name)
            run(["ffmpeg", "-y", "-v", "error", "-i", str(card), "-c", "copy", str(ov)], out=ov)
            print("%s  %.1f GB" % (ov.name, ov.stat().st_size / 1e9))
        mp4 = outdir / ("%s_broll.mp4" % name)
        run(["ffmpeg", "-y", "-v", "error", "-i", str(aroll), "-i", str(card),
             "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
             "-map", "[v]", "-map", "0:a?", "-fps_mode", "cfr", "-r", str(FPS),
             "-frames:v", str(total), *PRESET["encode"]["final_mp4"],
             "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(mp4)], out=mp4)
        print("%s  %.0f MB" % (mp4.name, mp4.stat().st_size / 1e6))

    if not a.card_only:
        mov = outdir / ("%s_caption.mov" % name)
        build_caption_layer(plan, total, tmp, a.style, mov)
        print("%s  %.1f GB" % (mov.name, mov.stat().st_size / 1e9))

    shutil.rmtree(tmp, ignore_errors=True)
    print("\nXONG — chay qc.py de kiem tra truoc khi giao.")


if __name__ == "__main__":
    main()

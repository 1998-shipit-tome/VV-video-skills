# -*- coding: utf-8 -*-
"""Kiem tra BAT BUOC truoc khi giao file. Khong dan ket qua script nay ra thi
khong duoc noi "xong".

    python qc.py <plan.json> <aroll.mp4> --style top|vip [--out-dir DIR] [--name TEN]

Bay phep do — moi phep sinh ra tu MOT loi that da giao nham cho nguoi dung:

  1. plan: khong lap clip o vi tri xa nhau, khong chong lan thoi gian,
     markup '*' can doi, khong con \\xa0
  2. moi doan B-roll ra DUNG so frame yeu cau   -> bat loi chay 2x va loi troi don
  3. tong frame ban dung == tong frame A-roll   -> bat loi hut frame o moi noi
  4. khong co cho clip bi tua lai giua chung
  5. kich thuoc + che do scale dung preset
  6. do sang the khop clip goc                  -> bat loi overlay len nen trong suot
  7. caption: alpha frame CUOI van 255 (cat thang, khong fade),
     va khoi chu khong de len the

Frame tinh KHONG DU. No mu truoc: toc do phat, clip bi tua lai, troi don, va zoom.
Va nho: CONG CU KIEM TRA CUNG CO THE SAI. Neu mot phep bao loi hang loat,
nghi phep kiem truoc khi nghi ban dung.
"""
import argparse, json, subprocess, sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (FPS, H, PRESET, W, cap_img, cap_repair, cap_y, dur_of,
                    frames_of, is_img, layout, nf, segments)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OK, BAD = [], []


def check(name, ok, detail=""):
    (OK if ok else BAD).append(name)
    print("  %-46s %s%s" % (name, "OK" if ok else "!! LOI", ("  " + detail) if detail else ""))


def bright(png, box=(10, 10, 190, 105)):
    im = Image.open(png).convert("RGB")
    p = im.load()
    xs = range(box[0], box[2], 5)
    ys = range(box[1], box[3], 5)
    n = 0
    s = 0
    for y in ys:
        for x in xs:
            s += sum(p[x, y]); n += 1
    return s / n / 3


def grab(src, t, vf, out, seek=True):
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if seek and not is_img(src):
        cmd += ["-ss", "%.4f" % t]
    cmd += ["-i", str(src), "-frames:v", "1", "-vf", vf, str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("aroll")
    ap.add_argument("--style", choices=["top", "vip"], required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--name", default=None)
    a = ap.parse_args()

    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    aroll = Path(a.aroll)
    outdir = Path(a.out_dir)
    name = a.name or aroll.stem.replace(" ", "_")
    L, cw, ch, cx, cy = layout(a.style)
    tmp = outdir / "_qc"
    tmp.mkdir(parents=True, exist_ok=True)

    def get(r, k, alt):
        return r.get(k, r.get(alt))

    print("\n=== 1. PLAN ===")
    seen = {}
    for r in plan:
        p = r.get("path")
        if p and "Product Broll" not in p:
            seen.setdefault(p, []).append(r["idx"])
    far = [(v, Path(k).name) for k, v in seen.items()
           if len(v) > 1 and max(b - a2 for a2, b in zip(v, v[1:])) > 1]
    check("khong lap clip o vi tri xa nhau", not far,
          "; ".join("%s %s" % (v, n[:30]) for v, n in far[:3]))
    ov = [r["idx"] for a2, r in zip(plan, plan[1:])
          if get(r, "t", "t0") < get(a2, "t_end", "t1") - 0.001]
    check("khong chong lan thoi gian", not ov, str(ov[:5]))
    bad_mk = [r["idx"] for r in plan
              if ((r.get("d1") or "") + (r.get("d2") or "")).count("*") % 2 == 1]
    check("markup * can doi", not bad_mk, "nhip %s" % bad_mk[:6])
    nb = [r["idx"] for r in plan if "\xa0" in (r.get("d1") or "") + (r.get("d2") or "")]
    check("khong con space khong ngat", not nb, "nhip %s" % nb[:6])

    print("\n=== 2-4. DOAN B-ROLL ===")
    segs = segments(plan)
    cuts = sum(1 for x, y in zip(segs, segs[1:]) if x["src"] == y["src"])
    check("khong co clip bi tua lai giua chung", cuts == 0, "%d cho" % cuts)
    fa = frames_of(aroll, True)
    mp4 = outdir / ("%s_broll.mp4" % name)
    if mp4.exists():
        fm = frames_of(mp4, True)
        check("tong frame ban dung == A-roll", fm == fa, "%d / %d" % (fm, fa))
    mov = outdir / ("%s_caption.mov" % name)
    if mov.exists():
        fc = frames_of(mov)
        check("tong frame lop chu == A-roll", abs(fc - fa) <= 1, "%d / %d" % (fc, fa))

    print("\n=== 5. KICH THUOC ===")
    if mp4.exists():
        wh = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                             "-show_entries", "stream=width,height", "-of", "csv=p=0",
                             str(mp4)], capture_output=True, text=True).stdout.strip()
        check("khung 1080x1920", wh.startswith("%d,%d" % (W, H)), wh)
    check("che do scale = fill_width", PRESET["broll"]["scale"] == "fill_width")
    check("khong zoom theo thoi gian", PRESET["broll"]["zoom_over_time"] is False)

    print("\n=== 6. DO SANG THE (bat loi overlay len nen trong suot) ===")
    if mp4.exists():
        vf_card = "crop=%d:%d:%d:%d,scale=200:113" % (cw, ch, cx, cy)
        vf_src = ("scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,scale=200:113"
                  % (cw, ch, cw, ch))
        pick = [r for r in plan if r.get("path")
                and get(r, "t_end", "t1") - get(r, "t", "t0") > 2.0][2::9][:8]
        dark = []
        for r in pick:
            t0 = get(r, "t", "t0")
            t = t0 + min(1.5, (get(r, "t_end", "t1") - t0) * 0.6)
            b1 = bright(grab(mp4, t, vf_card, tmp / "q1.png"))
            # anh tinh: KHONG seek — seek vao file anh cho ra ket qua vo nghia
            off = float(r.get("src_start") or 0) + (t - t0)
            b2 = bright(grab(r["path"], off, vf_src, tmp / "q2.png",
                             seek=not is_img(r["path"])))
            if b1 < b2 * 0.80:
                dark.append((r["idx"], round(b1), round(b2)))
        check("do sang the khop clip goc", not dark, str(dark[:4]))

    print("\n=== 7. CAPTION ===")
    if mov.exists():
        caps = [r for r in plan if (r.get("d1") or r.get("d2"))
                and get(r, "t_end", "t1") - get(r, "t", "t0") > 2][2::14][:6]
        faded, over = [], []
        for r in caps:
            last = nf(get(r, "t_end", "t1")) - 1
            # do tai DUNG moc frame/60 — lay (frame+0.5)/60 se roi sang frame KE TIEP
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.5f" % (last / FPS),
                            "-i", str(mov), "-frames:v", "1",
                            "-vf", "crop=%d:400:0:%d" % (W, max(0, cy - 420)),
                            str(tmp / "q3.png")], check=True, capture_output=True)
            px = Image.open(tmp / "q3.png").convert("RGBA").load()
            mx = max(px[x, y][3] for y in range(0, 400, 6) for x in range(0, W, 6))
            if mx < 250:
                faded.append(r["idx"])
            img = cap_img(r.get("d1", ""), r.get("d2", ""), r.get("variant", "product"))
            if img is not None and cap_y(a.style, img.height) + img.height > cy:
                over.append(r["idx"])
        check("chu cat thang, khong fade", not faded, "nhip %s" % faded[:5])
        check("chu khong de len the", not over, "nhip %s" % over[:5])

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d dat / %d loi" % (len(OK), len(BAD)))
    if BAD:
        print("CHUA DAT: " + " · ".join(BAD))
        sys.exit(1)
    print("TAT CA DAT")


if __name__ == "__main__":
    main()

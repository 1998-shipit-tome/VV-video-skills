# -*- coding: utf-8 -*-
"""plan.json -> copy clip đã dùng vào <project>/assets/broll/ + sinh snippet
<video> cho HyperFrames + soát luật (lặp clip, thiếu nguồn, clip dọc).

    python place.py plan.json --project D:/HYPERFRAME/my-video [--layout top|vip|full] [--fps 30]

plan.json:
{
  "layout": "top",                      # tuỳ chọn, --layout ghi đè
  "items": [
    {"id": "abc123def456", "start": 12.4, "duration": 3.2, "media_start": 2.0,
     "caption": "MẢNG XƠ VỮA BÁM THÀNH MẠCH", "note": "ý 3"}
  ]
}
Snippet KHÔNG tự chèn vào index.html — đọc references/hyperframes-placement.md
rồi chèn bằng Edit ở đúng lớp, không đặt trong phần tử cha có data-start.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

from common import abs_path, load_config, read_manifest

LAYOUT = {
    # bố cục dải trên đỉnh: 1080x608 ghim mép trên, tràn bề ngang, cắt thẳng
    "top": {"w": 1080, "h": 608, "top": 0, "left": 0, "radius": 0, "border": 0},
    # thẻ nổi nửa dưới: 918x516, bo 40px, viền trắng 11px (Broll Vip)
    "vip": {"w": 918, "h": 516, "top": 1056, "left": 81, "radius": 40, "border": 11},
    # toàn khung
    "full": {"w": 1080, "h": 1920, "top": 0, "left": 0, "radius": 0, "border": 0},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--project", required=True)
    ap.add_argument("--layout", choices=list(LAYOUT))
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--track", type=int, default=2)
    ap.add_argument("--no-copy", action="store_true")
    args = ap.parse_args()

    cfg = load_config(); m = read_manifest(cfg)
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    layout = args.layout or plan.get("layout") or "top"
    L = LAYOUT[layout]
    proj = Path(args.project)
    adir = proj / "assets" / "broll"; adir.mkdir(parents=True, exist_ok=True)

    errors, warns, lines = [], [], []
    seen = Counter()
    items = sorted(plan["items"], key=lambda x: x["start"])
    prev_end = None
    for k, it in enumerate(items):
        rec = m.get(it["id"])
        if not rec:
            errors.append(f"#{k} id {it['id']} không có trong manifest"); continue
        src = abs_path(cfg, rec)
        dur = float(it["duration"]); ms = float(it.get("media_start", 0.0)); st = float(it["start"])
        native = rec.get("dur") or 0
        is_product = rec.get("pool") == "product"
        if rec["kind"] == "video":
            if ms + dur > native + 0.05:
                errors.append(f"#{k} {rec['filename']}: media_start {ms} + {dur}s vượt nguồn {native}s — đổi offset/clip hoặc loop")
            if rec.get("orient") == "portrait":
                warns.append(f"#{k} {rec['filename']}: clip DỌC — dải/thẻ sẽ cắt mất ~2/3 nội dung")
            if rec.get("low_res"):
                warns.append(f"#{k} {rec['filename']}: độ phân giải thấp {rec.get('w')}x{rec.get('h')}")
        if not is_product:
            seen[it["id"]] += 1
        # nhịp liền nhau cùng file = 1 đoạn liên tục, không tính lặp
        if prev_end is not None and st < prev_end - 1 / args.fps:
            warns.append(f"#{k} start {st} chồng lên clip trước (kết thúc {prev_end:.2f})")
        prev_end = st + dur

        ext = src.suffix.lower()
        dst = adir / f"{rec['id']}{ext}"
        if not args.no_copy and not dst.is_file():
            shutil.copy2(src, dst)
        rel = f"assets/broll/{dst.name}"
        cap = (it.get("caption") or it.get("note") or "").replace("--", "- -")
        eid = f"broll-{k + 1:02d}"
        if rec["kind"] == "video":
            lines.append(
                f'  <!-- {eid}: {cap} | {rec["rel_path"]} -->\n'
                f'  <video id="{eid}" class="broll-media" src="{rel}" muted playsinline preload="auto"\n'
                f'         data-start="{st:.3f}" data-duration="{dur:.3f}" data-media-start="{ms:.3f}" data-track-index="{args.track}"></video>'
            )
        else:
            lines.append(
                f'  <!-- {eid}: {cap} | {rec["rel_path"]} -->\n'
                f'  <img id="{eid}" class="broll-media" src="{rel}" data-start="{st:.3f}" data-duration="{dur:.3f}" data-track-index="{args.track}">'
            )

    dups = [(i, n) for i, n in seen.items() if n > 1]
    for i, n in dups:
        # kiểm tra có phải các nhịp liền nhau không
        starts = sorted((it["start"], it["start"] + it["duration"]) for it in items if it["id"] == i)
        contiguous = all(abs(starts[j + 1][0] - starts[j][1]) < 0.5 for j in range(len(starts) - 1))
        if not contiguous:
            errors.append(f"clip {m[i]['filename']} dùng {n} lần không liền nhau — luật không lặp clip không-sản-phẩm")

    css = (
        f".broll-frame{{position:absolute;left:{L['left']}px;top:{L['top']}px;width:{L['w']}px;height:{L['h']}px;"
        f"overflow:hidden;border-radius:{L['radius']}px;"
        + (f"box-sizing:border-box;border:{L['border']}px solid #fff;" if L['border'] else "")
        + "z-index:5}\n"
        ".broll-frame .broll-media{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center}\n"
    )
    snippet = (
        f"<!-- add-footage: layout={layout}, {len(lines)} clip. Wrapper KHÔNG có data-start (video bên trong đã timed). -->\n"
        f"<style>\n{css}</style>\n"
        f'<div class="broll-frame" id="broll-frame" data-layout-allow-overflow="true">\n' + "\n".join(lines) + "\n</div>\n"
    )
    out = proj / "broll-snippet.html"
    out.write_text(snippet, encoding="utf-8")

    print(f"snippet: {out}  ({len(lines)} clip, layout={layout})")
    for w in warns:
        print("⚠", w)
    for e in errors:
        print("✖", e)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()

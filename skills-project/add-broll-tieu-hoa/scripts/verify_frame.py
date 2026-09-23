# -*- coding: utf-8 -*-
"""Trích frame tại ĐÚNG đoạn sẽ render (media_start .. media_start+span) để
xác minh bằng mắt trước khi chốt clip. Mặc định 3 frame: đầu / giữa / cuối.

    python verify_frame.py <id> --at 2.0 --span 3.5 [--frames 3] [--out DIR]
    python verify_frame.py <id> --at 2.0 --strip      # 1 ảnh dải 6 frame liền nhau

Lỗi đã trả giá: xác minh ở t=0 rồi render ở offset khác -> cảnh hoàn toàn khác.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from common import abs_path, load_config, read_manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--at", type=float, default=0.0, help="media_start (giây trong file nguồn)")
    ap.add_argument("--span", type=float, default=0.0, help="thời lượng sẽ dùng")
    ap.add_argument("--frames", type=int, default=3)
    ap.add_argument("--strip", action="store_true")
    ap.add_argument("--width", type=int, default=480)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load_config(); m = read_manifest(cfg)
    rec = m.get(args.id)
    if not rec:
        sys.exit(f"không có id {args.id}")
    src = abs_path(cfg, rec)
    dur = rec.get("dur") or 0
    out = Path(args.out) if args.out else cfg["index_dir"] / "verify"
    out.mkdir(parents=True, exist_ok=True)

    if rec["kind"] == "image":
        print(f"ảnh tĩnh: {src}"); return
    if args.at >= dur:
        sys.exit(f"media_start {args.at} >= độ dài nguồn {dur}s")
    span = args.span if args.span > 0 else max(0.0, dur - args.at)
    end = min(dur, args.at + span)
    if args.at + span > dur + 0.05:
        print(f"⚠ cần {span:.2f}s nhưng nguồn chỉ còn {dur - args.at:.2f}s từ offset -> phải loop hoặc chọn offset khác")

    if args.strip:
        n = 6
        fps = n / max(0.1, end - args.at)
        dst = out / f"{rec['id']}_{args.at:.1f}_strip.jpg"
        vf = f"fps={fps:.5f},scale={args.width}:-2,tile={n}x1"
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{args.at:.3f}", "-t", f"{end - args.at:.3f}", "-i", str(src),
               "-vf", vf, "-frames:v", "1", "-q:v", "3", str(dst)]
        subprocess.run(cmd, check=False)
        print(dst); return

    n = max(1, args.frames)
    for i in range(n):
        t = args.at if n == 1 else args.at + (end - args.at) * i / (n - 1)
        t = min(t, max(0.0, dur - 0.05))
        dst = out / f"{rec['id']}_{t:.2f}.jpg"
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src),
               "-vf", f"scale={args.width}:-2", "-frames:v", "1", "-q:v", "3", str(dst)]
        subprocess.run(cmd, check=False)
        print(f"{t:6.2f}s  {dst}")


if __name__ == "__main__":
    main()

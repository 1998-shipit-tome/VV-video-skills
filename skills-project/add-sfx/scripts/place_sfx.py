# -*- coding: utf-8 -*-
"""sfx-plan.json -> WAV chuẩn hóa vào <project>/assets/sfx/ + snippet <audio> HyperFrames + soát luật.

    python place_sfx.py sfx-plan.json --project D:/HYPERFRAME/my-video [--track 20] [--peak -6] [--no-convert]

sfx-plan.json:
{"items": [
  {"id": "abc123def456", "hit": 12.41, "volume": 0.15, "event": "caption 'ĐỘT QUỴ' hiện", "duration": null}
]}
`hit` = thời điểm SỰ KIỆN hình ảnh trên timeline. data-start = hit - lead_s (khoảng lặng đầu file),
để phần tiếng thật rơi đúng lúc chữ hiện. `duration` bỏ trống = cả file.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from common import abs_path, load_config, read_manifest


def measure_peak(src: Path) -> float | None:
    """Đo peak bằng đúng chuỗi decode sẽ dùng khi convert. Peak trong index đo
    lúc build có thể lệch vài dB (decoder/resample khác) -> đo lại cho chắc."""
    import re
    try:
        r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(src), "-vn", "-af", "aresample=48000,volumedetect",
                            "-ac", "2", "-f", "null", "-"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        m = re.search(r"max_volume:\s*(-?[\d.]+) dB", r.stderr)
        return float(m.group(1)) if m else None
    except subprocess.TimeoutExpired:
        return None


def convert(src: Path, dst: Path, peak_db: float | None, target_peak: float) -> bool:
    """WAV 48k stereo, đẩy peak về target (gain = target - peak). Không bao giờ tăng quá +24 dB (file lỗi)."""
    measured = measure_peak(src)
    if measured is not None:
        peak_db = measured
    gain = 0.0
    if peak_db is not None:
        gain = max(-40.0, min(24.0, target_peak - peak_db))
    af = f"aresample=48000,volume={gain:.2f}dB"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vn", "-af", af, "-ac", "2", "-c:a", "pcm_s16le", str(dst)]
    try:
        return subprocess.run(cmd, capture_output=True, timeout=120).returncode == 0 and dst.is_file()
    except subprocess.TimeoutExpired:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--project", required=True)
    ap.add_argument("--track", type=int, default=20); ap.add_argument("--peak", type=float, default=-6.0)
    ap.add_argument("--fps", type=float, default=30.0); ap.add_argument("--no-convert", action="store_true")
    args = ap.parse_args()
    cfg = load_config(); m = read_manifest(cfg)
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    proj = Path(args.project); adir = proj / "assets" / "sfx"; adir.mkdir(parents=True, exist_ok=True)

    items = sorted(plan["items"], key=lambda x: x["hit"])
    lines, warns, errors = [], [], []
    prev = None; streak = Counter()
    last_id = None; run = 0
    for k, it in enumerate(items):
        rec = m.get(it["id"])
        if not rec:
            errors.append(f"#{k} id {it['id']} không có trong manifest"); continue
        src = abs_path(cfg, rec)
        lead = float(rec.get("lead_s") or 0.0)
        hit = float(it["hit"]); start = max(0.0, hit - lead)
        dur = float(it["duration"]) if it.get("duration") else float(rec["dur"])
        vol = float(it.get("volume", 0.15))
        if dur > 3.0 and rec.get("category") not in ("riser", "drama", "ambience", "crowd"):
            warns.append(f"#{k} {rec['filename']}: dài {dur:.1f}s ở vị trí nhấn — cân nhắc cắt duration")
        if vol > 0.35:
            warns.append(f"#{k} {rec['filename']}: volume {vol} cao hơn mức khuyên (≤0.25 dưới lời nói)")
        if prev is not None and start - prev < 0.15:
            warns.append(f"#{k} {rec['filename']}: cách tiếng trước {start - prev:.2f}s (<0.15s) — hai tiếng dính nhau")
        prev = start
        if rec["id"] == last_id: run += 1
        else: run = 1; last_id = rec["id"]
        if run > 3:
            warns.append(f"#{k} {rec['filename']}: lặp {run} lần liên tiếp — đổi biến thể")
        dst = adir / f"{rec['id']}.wav"
        if not args.no_convert and not dst.is_file():
            if not convert(src, dst, rec.get("peak_db"), args.peak):
                errors.append(f"#{k} không convert được {src}"); continue
        rel = f"assets/sfx/{dst.name}"
        ev = (it.get("event") or "").replace("--", "- -")
        lines.append(
            f'  <audio id="sfx-{k + 1:02d}" src="{rel}" data-start="{start:.3f}" data-duration="{dur:.3f}" '
            f'data-track-index="{args.track}" data-volume="{vol:.2f}"></audio>  <!-- {ev} | hit {hit:.2f}s lead {lead:.2f}s | {rec["rel_path"]} -->'
        )
    snippet = (f"<!-- add-sfx: {len(lines)} tiếng, track {args.track}, peak chuẩn hóa {args.peak} dBFS. "
               f"Đặt ở cấp con của #root, KHÔNG bọc trong phần tử có data-start. -->\n" + "\n".join(lines) + "\n")
    out = proj / "sfx-snippet.html"; out.write_text(snippet, encoding="utf-8")
    print(f"snippet: {out}  ({len(lines)} tiếng)")
    for w in warns: print("⚠", w)
    for e in errors: print("✖", e)
    if errors: sys.exit(1)


if __name__ == "__main__":
    main()

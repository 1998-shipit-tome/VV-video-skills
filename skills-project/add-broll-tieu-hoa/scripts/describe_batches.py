# -*- coding: utf-8 -*-
"""Chia clip chưa mô tả thành lô cho agent (hoặc API) xem contact sheet và
viết mô tả; rồi gộp mô tả vào manifest.

    python describe_batches.py make [--topic id | --folder "tên" | --all] [--batch-size 20] [--redo]
    python describe_batches.py merge [--file index/descriptions/003.jsonl]
    python describe_batches.py auto --batch 003   # cần ANTHROPIC_API_KEY + pip install anthropic

Batch = index/batches/NNN.json: {"batch": "NNN", "frame_interval_hint": ..., "items": [{id, sheet, dur, filename, folder, topics, w, h}]}
Mô tả = index/descriptions/NNN.jsonl: mỗi dòng {"id":..., "scene":..., ...} theo references/describe-prompt.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from common import (REF_DIR, fold, load_config, nfc, read_manifest,
                    write_manifest)

REQUIRED = ("scene", "subject_type", "mood")
ENUM_SUBJECT = {"real_person", "anatomy_3d", "product", "metaphor_object", "lifestyle_scene", "text_graphic", "screen_ui"}
ENUM_MOOD = {"positive", "negative", "neutral", "painful", "tense"}


def cmd_make(args):
    cfg = load_config(); m = read_manifest(cfg)
    bdir = cfg["index_dir"] / "batches"; bdir.mkdir(parents=True, exist_ok=True)
    recs = [r for r in m.values() if r["kind"] == "video" and r.get("sheet") and not r.get("broken")]
    if not args.redo:
        recs = [r for r in recs if not r.get("scene")]
    if args.topic:
        recs = [r for r in recs if args.topic in (r.get("topics") or [])]
    if args.folder:
        recs = [r for r in recs if fold(args.folder) in fold(r.get("folder", ""))]
    if not (args.topic or args.folder or args.all):
        sys.exit("chọn --topic / --folder / --all")
    recs.sort(key=lambda r: (r["folder"], r["rel_path"]))
    if not recs:
        print("không còn clip nào cần mô tả với bộ lọc này"); return
    existing = sorted(int(p.stem) for p in bdir.glob("*.json") if p.stem.isdigit())
    n0 = (existing[-1] + 1) if existing else 1
    made = []
    for i in range(0, len(recs), args.batch_size):
        chunk = recs[i:i + args.batch_size]
        bid = f"{n0 + i // args.batch_size:03d}"
        items = [{
            "id": r["id"], "sheet": str(cfg["index_dir"] / r["sheet"]), "dur": r.get("dur"),
            "w": r.get("w"), "h": r.get("h"), "filename": r["filename"], "folder": r["folder"],
            "topics": r.get("topics"), "frame_interval": round((r.get("dur") or 0) / cfg["sheet_frames"], 2),
        } for r in chunk]
        (bdir / f"{bid}.json").write_text(json.dumps({
            "batch": bid, "sheet_frames": cfg["sheet_frames"], "sheet_cols": cfg["sheet_cols"],
            "hint": "khung thứ k (0-based, đọc trái->phải, trên->dưới) ứng với t = k * frame_interval giây",
            "prompt_ref": str(REF_DIR / "describe-prompt.md"),
            "output": str(cfg["index_dir"] / "descriptions" / f"{bid}.jsonl"),
            "items": items,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        made.append((bid, len(chunk)))
    print(f"{len(recs)} clip -> {len(made)} batch trong {bdir}")
    for bid, n in made:
        print(f"  {bid}.json  ({n} clip)")
    print(f"\nHướng dẫn mô tả: {REF_DIR / 'describe-prompt.md'}")


def validate(d: dict) -> list[str]:
    errs = []
    for k in REQUIRED:
        if not d.get(k):
            errs.append(f"thiếu {k}")
    if d.get("subject_type") and d["subject_type"] not in ENUM_SUBJECT:
        errs.append(f"subject_type lạ: {d['subject_type']}")
    if d.get("mood") and d["mood"] not in ENUM_MOOD:
        errs.append(f"mood lạ: {d['mood']}")
    for s in d.get("segments") or []:
        if not all(k in s for k in ("t0", "t1", "scene")):
            errs.append("segment thiếu t0/t1/scene")
    return errs


def cmd_merge(args):
    cfg = load_config(); m = read_manifest(cfg)
    ddir = cfg["index_dir"] / "descriptions"
    files = [Path(args.file)] if args.file else sorted(ddir.glob("*.jsonl"))
    n_ok = n_bad = 0
    for f in files:
        for ln, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"{f.name}:{ln} JSON lỗi: {e}"); n_bad += 1; continue
            rec = m.get(d.get("id"))
            if not rec:
                print(f"{f.name}:{ln} id không có trong manifest: {d.get('id')}"); n_bad += 1; continue
            errs = validate(d)
            if errs:
                print(f"{f.name}:{ln} {d['id']}: {'; '.join(errs)}"); n_bad += 1; continue
            for k in ("scene", "subject_type", "mood", "action", "body_part", "mechanism", "setting",
                      "has_text", "color_tone", "segments", "tags", "quality_flags", "topics_seen"):
                if k in d:
                    rec[k] = d[k]
            if d.get("topics_seen"):
                rec["topics"] = sorted(set(rec.get("topics") or []) | set(d["topics_seen"]))
            rec["scene"] = nfc(rec["scene"])
            rec["described_by"] = d.get("described_by", "agent")
            rec["described_at"] = int(time.time())
            n_ok += 1
    write_manifest(cfg, m)
    print(f"gộp {n_ok} mô tả · lỗi {n_bad} · từ {len(files)} file")


def cmd_auto(args):
    """Chạy mô tả tự động qua API Anthropic. Chỉ khi có key; nếu không, dùng
    quy trình agent (make -> Read sheet -> ghi jsonl -> merge)."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("thiếu ANTHROPIC_API_KEY — dùng quy trình agent thay thế")
    try:
        import anthropic  # noqa
    except ImportError:
        sys.exit("pip install anthropic")
    import base64
    cfg = load_config()
    bpath = cfg["index_dir"] / "batches" / f"{args.batch}.json"
    b = json.loads(bpath.read_text(encoding="utf-8"))
    prompt = (REF_DIR / "describe-prompt.md").read_text(encoding="utf-8")
    client = anthropic.Anthropic()
    out = Path(b["output"]); out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", encoding="utf-8") as fo:
        for it in b["items"]:
            img = base64.b64encode(Path(it["sheet"]).read_bytes()).decode()
            meta = {k: it[k] for k in ("id", "dur", "w", "h", "filename", "folder", "topics", "frame_interval")}
            msg = client.messages.create(
                model=args.model, max_tokens=1200,
                system=prompt,
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img}},
                    {"type": "text", "text": "Metadata: " + json.dumps(meta, ensure_ascii=False) + "\nTrả về đúng 1 object JSON, không giải thích."},
                ]}],
            )
            txt = "".join(c.text for c in msg.content if c.type == "text").strip()
            txt = txt[txt.find("{"): txt.rfind("}") + 1]
            try:
                d = json.loads(txt); d["id"] = it["id"]; d["described_by"] = args.model
                fo.write(json.dumps(d, ensure_ascii=False) + "\n"); fo.flush()
                print(it["id"], "ok")
            except Exception as e:
                print(it["id"], "lỗi parse:", e)
    print(f"-> {out}; chạy: describe_batches.py merge --file \"{out}\"")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    mk = sub.add_parser("make")
    mk.add_argument("--topic"); mk.add_argument("--folder"); mk.add_argument("--all", action="store_true")
    mk.add_argument("--batch-size", type=int, default=20); mk.add_argument("--redo", action="store_true")
    mg = sub.add_parser("merge"); mg.add_argument("--file")
    au = sub.add_parser("auto"); au.add_argument("--batch", required=True); au.add_argument("--model", default="claude-sonnet-5")
    args = ap.parse_args()
    {"make": cmd_make, "merge": cmd_merge, "auto": cmd_auto}[args.cmd](args)


if __name__ == "__main__":
    main()

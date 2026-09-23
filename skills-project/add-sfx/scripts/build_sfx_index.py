# -*- coding: utf-8 -*-
"""Quét các kho SFX -> manifest.jsonl. Mỗi file: id hash, thời lượng, peak dB,
khoảng lặng đầu (lead_s), category theo từ khóa, nhãn cảm xúc theo thư mục.

    python build_sfx_index.py update [--force] [--no-analyze]
    python build_sfx_index.py stats
    python build_sfx_index.py show <id>
    python build_sfx_index.py tag --id <id> [--cat whoosh] [--tags "ngắn, sáng"]
    python build_sfx_index.py favorite --event "caption hiện" --id <id> [--volume 0.15] [--note ...]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import (abs_path, fold, load_config, load_taxonomy, nfc, quick_hash,
                    read_favs, read_manifest, tokens, write_favs, write_manifest)


def probe(path: Path) -> dict | None:
    cmd = ["ffprobe", "-v", "error", "-select_streams", "a:0",
           "-show_entries", "stream=codec_name,sample_rate,channels:format=duration",
           "-of", "json", str(path)]
    try:
        j = json.loads(subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout or "{}")
        st = (j.get("streams") or [{}])[0]
        dur = float((j.get("format") or {}).get("duration") or 0)
        if not st or dur <= 0:
            return None
        return {"codec": st.get("codec_name"), "sr": int(st.get("sample_rate") or 0),
                "ch": int(st.get("channels") or 0), "dur": round(dur, 3)}
    except Exception:
        return None


def analyze(path: Path, max_sec: float) -> dict:
    """peak dB (volumedetect) + khoảng lặng đầu file (silencedetect). Chỉ đọc
    max_sec giây đầu để file dài (ambience, nhạc) không kéo cả run."""
    out = {}
    base = ["ffmpeg", "-v", "info", "-t", f"{max_sec}", "-i", str(path)]
    try:
        r = subprocess.run(base + ["-af", "volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        m = re.search(r"max_volume:\s*(-?[\d.]+) dB", r.stderr)
        m2 = re.search(r"mean_volume:\s*(-?[\d.]+) dB", r.stderr)
        if m: out["peak_db"] = float(m.group(1))
        if m2: out["mean_db"] = float(m2.group(1))
        r = subprocess.run(base + ["-af", "silencedetect=noise=-45dB:d=0.03", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", r.stderr)]
        ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", r.stderr)]
        lead = ends[0] if ends and (not starts or starts[0] <= 0.02) else 0.0
        out["lead_s"] = round(lead, 3)
    except Exception:
        pass
    return out


def categorize(rec: dict, tax: dict) -> tuple[str, list[str]]:
    """category từ từ khóa trong tên file + thư mục; nhãn cảm xúc từ thư mục."""
    fname = fold(rec["filename"]); fdir = fold(rec["rel_path"].rsplit("/", 1)[0])
    ftoks = set(tokens(fname)); dtoks = set(tokens(fdir))
    best, best_n = "misc", 0
    for cat, kws in (tax.get("categories") or {}).items():
        kws = [fold(str(k)) for k in kws]  # YAML đọc 'no'/'on'/'yes' thành bool -> ép về chuỗi
        # tên file nói về CHÍNH tiếng đó -> nặng gấp đôi thư mục (thư mục 'Drama' chứa cả whoosh/impact)
        n = 2 * sum(1 for k in kws if (k in ftoks if " " not in k else k in fname)) \
            + sum(1 for k in kws if (k in dtoks if " " not in k else k in fdir))
        if n > best_n:
            best, best_n = cat, n
    tags = []
    for folder_key, labels in (tax.get("folder_labels") or {}).items():
        if fold(folder_key) in fold(rec["rel_path"]):
            tags.extend(labels)
    return best, sorted(set(tags))


def cmd_update(args):
    cfg = load_config(); tax = load_taxonomy()
    idx: Path = cfg["index_dir"]; idx.mkdir(parents=True, exist_ok=True)
    old = read_manifest(cfg)
    by_rel = {r["rel_path"]: r for r in old.values()}
    by_hash = {r["id"]: r for r in old.values()}
    aext = set(cfg["audio_ext"]); vext = set(cfg["video_ext"])
    prio = {r["name"]: r.get("priority", 3) for r in cfg["sfx_roots"]}

    files: list[tuple[str, Path, Path]] = []
    for root in cfg["sfx_roots"]:
        if not root["path"].is_dir():
            print(f"⚠ bỏ qua root '{root['name']}': không tồn tại {root['path']}"); continue
        for p in root["path"].rglob("*"):
            if p.is_file() and (p.suffix.lower() in aext or p.suffix.lower() in vext):
                files.append((root["name"], root["path"], p))
    print(f"kho: {len(files)} file âm thanh trong {len(cfg['sfx_roots'])} root")

    new: dict[str, dict] = {}; todo = []; n_keep = n_new = n_moved = n_dup = 0
    for rname, rpath, p in files:
        rel = rname + "/" + nfc(str(p.relative_to(rpath)).replace("\\", "/"))
        st = p.stat()
        prev = by_rel.get(rel)
        if prev and not args.force and prev.get("size") == st.st_size and abs(prev.get("mtime", 0) - st.st_mtime) < 2:
            if prev["id"] in new and new[prev["id"]]["rel_path"] != rel:
                new[prev["id"]].setdefault("dups", []).append(rel); n_dup += 1
            else:
                new[prev["id"]] = prev; n_keep += 1
            continue
        h = quick_hash(p)
        moved = by_hash.get(h)
        if h in new:
            first = new[h]
            # ưu tiên root có priority thấp hơn làm đường dẫn chính
            if prio.get(rname, 3) < prio.get(first["rel_path"].split("/")[0], 3):
                first.setdefault("dups", []).append(first["rel_path"])
                first["rel_path"] = rel; first["filename"] = p.name; first["root"] = rname
            else:
                first.setdefault("dups", []).append(rel)
            n_dup += 1
            continue
        rec = dict(moved) if moved else {"id": h}
        if moved and moved.get("rel_path") != rel: n_moved += 1
        elif not moved: n_new += 1
        rec.update({"rel_path": rel, "filename": p.name, "root": rname, "size": st.st_size, "mtime": st.st_mtime,
                    "folder": "/".join(rel.split("/")[1:-1]), "kind": "video" if p.suffix.lower() in vext else "audio"})
        rec.pop("dups", None)
        rec["category"], rec["folder_tags"] = categorize(rec, tax)
        new[h] = rec
        if not rec.get("dur") or args.force:
            todo.append((p, rec))
    for rec in new.values():
        if rec.get("dups"):
            rec["dups"] = sorted(set(d for d in rec["dups"] if d != rec["rel_path"]))
    n_lost = len(set(old) - set(new))
    print(f"giữ nguyên {n_keep} · mới {n_new} · dời {n_moved} · trùng {n_dup} · mất {n_lost} · cần probe {len(todo)}")

    def _work(item):
        p, rec = item
        meta = probe(p)
        if not meta:
            rec["broken"] = True; return
        rec.update(meta)
        if not args.no_analyze:
            rec.update(analyze(p, cfg["analyze_max_sec"]))

    if todo:
        t0 = time.time(); done = 0
        with ThreadPoolExecutor(max_workers=8) as ex:
            for _ in ex.map(_work, todo):
                done += 1
                if done % 500 == 0:
                    print(f"  ... {done}/{len(todo)} ({time.time() - t0:.0f}s)", flush=True)
                    write_manifest(cfg, new)  # checkpoint
        print(f"probe+analyze xong {len(todo)} trong {time.time() - t0:.0f}s")
    write_manifest(cfg, new)
    print(f"manifest: {len(new)} record -> {cfg['index_dir'] / 'manifest.jsonl'}")


def cmd_stats(args):
    cfg = load_config(); m = read_manifest(cfg)
    ok = [r for r in m.values() if not r.get("broken")]
    print(f"manifest: {len(m)} record · đọc được {len(ok)} · hỏng {len(m) - len(ok)}")
    print("root:", dict(Counter(r["root"] for r in ok)))
    print("category:", dict(Counter(r.get("category") for r in ok).most_common()))
    d = Counter("<0.5s" if r["dur"] < 0.5 else "0.5-1.5s" if r["dur"] < 1.5 else "1.5-3s" if r["dur"] < 3 else "3-10s" if r["dur"] < 10 else ">10s" for r in ok if r.get("dur"))
    print("thời lượng:", dict(d))
    print("có peak/lead:", sum(1 for r in ok if "peak_db" in r), "/", len(ok))
    print("trùng nội dung:", sum(1 for r in ok if r.get("dups")))


def cmd_recat(args):
    """Phân loại lại toàn bộ theo taxonomy hiện tại, không probe. Giữ category người dùng gắn tay."""
    cfg = load_config(); tax = load_taxonomy(); m = read_manifest(cfg)
    changed = 0
    for r in m.values():
        if r.get("tagged_by") == "user":
            continue
        cat, tags = categorize(r, tax)
        if cat != r.get("category") or tags != r.get("folder_tags"):
            r["category"], r["folder_tags"] = cat, tags; changed += 1
    write_manifest(cfg, m); print(f"recat: đổi {changed}/{len(m)} record")


def cmd_show(args):
    cfg = load_config(); m = read_manifest(cfg)
    rec = m.get(args.id)
    if not rec: sys.exit("không có id")
    rec = dict(rec); rec["abs_path"] = str(abs_path(cfg, rec))
    print(json.dumps(rec, ensure_ascii=False, indent=1))


def cmd_tag(args):
    cfg = load_config(); m = read_manifest(cfg)
    rec = m.get(args.id)
    if not rec: sys.exit("không có id")
    if args.cat: rec["category"] = args.cat
    if args.tags: rec["tags"] = sorted(set((rec.get("tags") or []) + [t.strip() for t in args.tags.split(",") if t.strip()]))
    rec["tagged_by"] = "user"
    write_manifest(cfg, m); print("đã gắn:", rec["rel_path"], rec["category"], rec.get("tags"))


def cmd_favorite(args):
    cfg = load_config(); m = read_manifest(cfg)
    if args.id not in m: sys.exit("không có id")
    f = read_favs(cfg)
    f["items"] = [x for x in f["items"] if not (x["event"] == args.event and x["id"] == args.id)]
    f["items"].append({"event": nfc(args.event), "tokens": sorted(set(tokens(args.event))), "id": args.id,
                       "volume": args.volume, "note": args.note, "ts": int(time.time())})
    write_favs(cfg, f); print(f"favorite: '{args.event}' -> {m[args.id]['rel_path']} @vol {args.volume}")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("update"); u.add_argument("--force", action="store_true"); u.add_argument("--no-analyze", action="store_true")
    sub.add_parser("stats"); sub.add_parser("recat")
    s = sub.add_parser("show"); s.add_argument("id")
    t = sub.add_parser("tag"); t.add_argument("--id", required=True); t.add_argument("--cat"); t.add_argument("--tags")
    f = sub.add_parser("favorite"); f.add_argument("--event", required=True); f.add_argument("--id", required=True)
    f.add_argument("--volume", type=float, default=0.15); f.add_argument("--note", default="")
    args = ap.parse_args()
    {"update": cmd_update, "stats": cmd_stats, "recat": cmd_recat, "show": cmd_show, "tag": cmd_tag, "favorite": cmd_favorite}[args.cmd](args)


if __name__ == "__main__":
    main()

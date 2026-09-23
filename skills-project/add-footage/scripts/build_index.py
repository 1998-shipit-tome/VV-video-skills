# -*- coding: utf-8 -*-
"""Quét kho footage -> manifest.jsonl (+ contact sheet, thumb). Tăng dần: file
đã có trong manifest với cùng size+mtime thì bỏ qua; đổi tên/dời thư mục thì
nhận lại theo hash nên giữ nguyên mô tả đã sinh.

Usage:
    python build_index.py update [--sheets] [--force]
    python build_index.py stats
    python build_index.py approve --concept "mất ngủ" --id abc123def456 [--media-start 2.0] [--note "..."]
    python build_index.py show <id>
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import (abs_path, fold, load_config, load_taxonomy, nfc,
                    quick_hash, read_graph, read_manifest, write_graph,
                    write_manifest)

# ---------- phân loại tên file ----------
_NAME_CLASS = [
    ("described", re.compile(r"^\d{3} - .+")),               # "003 - Ngồi trên xe lăn..." (prompt AI, hay bị cắt cụt)
    ("canva", re.compile(r"^Thiết kế chưa có tên")),
    ("stock_id", re.compile(r"^\d{5,}[-_]")),                # pexels/pixabay
    ("junk", re.compile(r"^\d+ \(\d+\)\.|^\d+\.\w+$|^[0-9a-f]{20,}")),
]


def name_class(name: str) -> str:
    n = nfc(name)
    for k, rx in _NAME_CLASS:
        if rx.match(n):
            return k
    stem = Path(n).stem
    if "-" in stem and " " not in stem.strip():
        return "slug"  # "mo-mau-cao,mo-mau,mo-trong-mau" — người dùng tự đặt theo ý
    return "free"


# ---------- ffprobe / ffmpeg ----------
def probe(path: Path) -> dict | None:
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=width,height,r_frame_rate:format=duration",
           "-of", "json", str(path)]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
        j = json.loads(out or "{}")
        st = (j.get("streams") or [{}])[0]
        w, h = int(st.get("width", 0)), int(st.get("height", 0))
        num, _, den = (st.get("r_frame_rate") or "0/1").partition("/")
        fps = round(float(num) / float(den or 1), 3) if float(den or 1) else 0.0
        dur = float((j.get("format") or {}).get("duration") or 0.0)
        if not w or not h:
            return None
        return {"w": w, "h": h, "fps": fps, "dur": round(dur, 3)}
    except Exception:
        return None


def _run(cmd: list[str], timeout: int) -> bool:
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout).returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


LONG_CLIP_S = 45.0  # trên ngưỡng này filter fps (giải mã cả clip) quá chậm -> seek từng khung


def make_sheet(src: Path, dst: Path, dur: float, frames: int, cols: int, width: int) -> bool:
    """Contact sheet: `frames` khung trải đều toàn clip, xếp lưới cols x rows.
    Khung thứ i ứng với thời điểm i * dur / frames (ghi trong batch để agent
    suy ra segments). Clip ngắn: 1 lệnh ffmpeg (fps+tile). Clip dài: seek nhanh
    12 lần rồi ghép lưới bằng PIL — clip 12 phút từng làm ffmpeg quá 120s."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    rows = -(-frames // cols)
    if dur <= 0:
        return False
    if dur <= LONG_CLIP_S:
        vf = f"fps={frames / dur:.6f},scale={width}:-2,tile={cols}x{rows}"
        ok = _run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", vf,
                   "-frames:v", "1", "-q:v", "4", str(dst)], timeout=180)
        if ok and dst.is_file():
            return True
    # đường chậm/an toàn: seek từng khung
    try:
        from PIL import Image
    except ImportError:
        return False
    tmpdir = dst.parent / "_tmp"
    tmpdir.mkdir(exist_ok=True)
    tiles = []
    for k in range(frames):
        t = min(k * dur / frames, max(0.0, dur - 0.1))
        tmp = tmpdir / f"{dst.stem}_{k}.jpg"
        if _run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src),
                 "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "4", str(tmp)], timeout=60) and tmp.is_file():
            tiles.append(tmp)
        else:
            tiles.append(None)
    got = [t for t in tiles if t]
    if not got:
        return False
    try:
        first = Image.open(got[0]); tw, th = first.size
        grid = Image.new("RGB", (cols * tw, rows * th), (16, 16, 16))
        for k, t in enumerate(tiles):
            if t:
                im = Image.open(t).convert("RGB").resize((tw, th))
                grid.paste(im, ((k % cols) * tw, (k // cols) * th))
        grid.save(dst, quality=85)
        return True
    except Exception:
        return False
    finally:
        for t in tiles:
            if t:
                try: t.unlink()
                except OSError: pass


def make_thumb(src: Path, dst: Path, dur: float, width: int, is_image: bool) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if is_image:
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", f"scale={width}:-2", "-q:v", "4", str(dst)]
    else:
        t = min(1.0, max(0.0, dur / 2))
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src),
               "-vf", f"scale={width}:-2", "-frames:v", "1", "-q:v", "4", str(dst)]
    return _run(cmd, timeout=60) and dst.is_file()


# ---------- gán chủ đề từ thư mục ----------
def classify_folder(rel: Path, tax: dict) -> dict:
    top = nfc(rel.parts[0]) if len(rel.parts) > 1 else ""
    out = {"folder": top, "topics": [], "pool": "topic", "product_id": None, "asset_role": None}
    fmap = {nfc(k): v for k, v in (tax.get("folders") or {}).items()}
    info = fmap.get(top)
    if info:
        out["topics"] = list(info.get("topics") or [])
        out["pool"] = info.get("pool", "topic")
    if out["pool"] == "product" and len(rel.parts) > 2:
        pname = nfc(rel.parts[1])
        pmap = {nfc(k): v for k, v in (tax.get("product_folders") or {}).items()}
        out["product_id"] = pmap.get(pname, fold(pname).replace(" ", "_")[:24])
        sub = nfc(rel.parts[2]).lower() if len(rel.parts) > 3 else ""
        out["asset_role"] = {"video": "video", "nguyên liệu": "nguyen_lieu", "ảnh": "anh"}.get(sub, "other")
    return out


# ---------- update ----------
def cmd_update(args):
    cfg = load_config()
    tax = load_taxonomy()
    root: Path = cfg["broll_root"]
    if not root.is_dir():
        sys.exit(f"broll_root không tồn tại: {root} (sửa config.json)")
    idx: Path = cfg["index_dir"]
    idx.mkdir(parents=True, exist_ok=True)
    old = read_manifest(cfg)
    by_rel = {r["rel_path"]: r for r in old.values()}
    by_hash = {r["id"]: r for r in old.values()}
    vext = set(cfg["video_ext"]); iext = set(cfg["image_ext"])
    skip = {nfc(s) for s in cfg["skip_dirs"]}

    files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if rel.parts and nfc(rel.parts[0]) in skip:
            continue
        if p.suffix.lower() in vext or p.suffix.lower() in iext:
            files.append(p)
    print(f"kho: {len(files)} file media trong {root}")

    new: dict[str, dict] = {}
    todo_probe: list[tuple[Path, dict]] = []
    n_keep = n_new = n_moved = n_dup = 0

    POOL_RANK = {"chuan_hoa": 0, "product": 1, "topic": 1, "dilim_quay": 2, "cta": 3, "lon_xon": 5}
    NAME_RANK = {"slug": 0, "described": 0, "free": 1, "canva": 2, "stock_id": 2, "junk": 3}

    def rank(r: dict) -> tuple:
        return (POOL_RANK.get(r.get("pool"), 4), NAME_RANK.get(r.get("name_class"), 3))

    def put(rec: dict, rel: str) -> bool:
        """Đưa record vào manifest mới. Cùng id ở 2 đường dẫn (vd Đã Chuẩn Hóa
        chứa bản sao của thư mục chủ đề) -> giữ MỘT record; đường dẫn chính là
        bản có pool ưu tiên cao hơn / tên có nghĩa hơn, các đường dẫn còn lại
        vào dups. Vì người dùng tìm Đã Chuẩn Hóa trước và search chấm điểm theo
        pool, để bản Lộn Xộn làm đường dẫn chính sẽ kéo clip tốt xuống đáy."""
        nonlocal n_dup
        first = new.get(rec["id"])
        if first and first["rel_path"] != rel:
            topics = sorted(set(first.get("topics") or []) | set(rec.get("topics") or []))
            dups = [d for d in (first.get("dups") or []) if d != rel]
            if rank(rec) < rank(first):
                # rec thắng: kế thừa lớp ngữ nghĩa/sheet của first, first thành dup
                for k in ("scene", "subject_type", "action", "mood", "body_part", "mechanism", "setting",
                          "has_text", "color_tone", "segments", "tags", "quality_flags", "topics_seen",
                          "described_by", "described_at", "w", "h", "fps", "dur", "orient", "low_res", "broken"):
                    if k in first and k not in rec:
                        rec[k] = first[k]
                dups.append(first["rel_path"])
                rec["dups"] = dups
                rec["topics"] = topics
                new[rec["id"]] = rec
            else:
                dups.append(rel)
                first["dups"] = dups
                first["topics"] = topics
            n_dup += 1
            return False
        new[rec["id"]] = rec
        return True

    for p in files:
        rel = nfc(str(p.relative_to(root)).replace("\\", "/"))
        st = p.stat()
        prev = by_rel.get(rel)
        if prev and not args.force and prev.get("size") == st.st_size and abs(prev.get("mtime", 0) - st.st_mtime) < 2:
            if put(prev, rel):
                n_keep += 1
            continue
        h = quick_hash(p)
        moved = by_hash.get(h)
        rec = dict(moved) if moved else {"id": h}
        if moved and moved.get("rel_path") != rel:
            n_moved += 1
        elif not moved:
            n_new += 1
        rec.update({
            "rel_path": rel, "filename": p.name, "size": st.st_size, "mtime": st.st_mtime,
            "kind": "image" if p.suffix.lower() in iext else "video",
            "name_class": name_class(p.name),
        })
        rec.update(classify_folder(Path(rel), tax))
        rec.pop("dups", None)
        if not put(rec, rel):
            continue
        if rec["kind"] == "video" and (not rec.get("w") or args.force):
            todo_probe.append((p, rec))
        elif rec["kind"] == "image" and not rec.get("w"):
            todo_probe.append((p, rec))

    # dups trỏ tới file đã bị xóa (clean_kho.py) -> cắt bỏ
    n_dead = 0
    for rec in new.values():
        if rec.get("dups"):
            alive = [d for d in rec["dups"] if (root / d).is_file()]
            n_dead += len(rec["dups"]) - len(alive)
            if alive:
                rec["dups"] = alive
            else:
                rec.pop("dups", None)
    n_lost = len(set(old) - set(new))
    print(f"giữ nguyên {n_keep} · mới {n_new} · đổi tên/dời {n_moved} · trùng nội dung {n_dup} · mất {n_lost} · cần probe {len(todo_probe)}"
          + (f" · dups chết đã cắt {n_dead}" if n_dead else ""))

    def _probe(item):
        p, rec = item
        meta = probe(p)
        if meta:
            rec.update(meta)
            rec["orient"] = "portrait" if meta["h"] > meta["w"] * 1.3 else ("landscape" if meta["w"] > meta["h"] * 1.3 else "square")
            rec["low_res"] = meta["w"] < 1000 and meta["h"] < 1000
        else:
            rec["broken"] = True
        return rec

    if todo_probe:
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(_probe, todo_probe))
        print(f"probe xong {len(todo_probe)} file trong {time.time() - t0:.0f}s")

    def _refresh_media_fields():
        for rec in new.values():
            rec["sheet"] = f"sheets/{rec['id']}.jpg" if (idx / "sheets" / f"{rec['id']}.jpg").is_file() else None
            rec["thumb"] = f"thumbs/{rec['id']}.jpg" if (idx / "thumbs" / f"{rec['id']}.jpg").is_file() else None

    # ghi manifest NGAY sau probe: bước sheet có thể chạy rất lâu, không để mất kết quả probe
    _refresh_media_fields()
    write_manifest(cfg, new)

    # sheets / thumbs
    if args.sheets:
        jobs = []
        for rec in new.values():
            if rec.get("broken"):
                continue
            src = abs_path(cfg, rec)
            thumb = idx / "thumbs" / f"{rec['id']}.jpg"
            if not thumb.is_file():
                jobs.append(("thumb", src, thumb, rec))
            if rec["kind"] == "video":
                sheet = idx / "sheets" / f"{rec['id']}.jpg"
                if not sheet.is_file():
                    jobs.append(("sheet", src, sheet, rec))
        print(f"tạo {len(jobs)} sheet/thumb ...")

        def _job(j):
            kind, src, dst, rec = j
            try:
                if kind == "sheet":
                    return make_sheet(src, dst, rec.get("dur", 0), cfg["sheet_frames"], cfg["sheet_cols"], cfg["sheet_width"])
                return make_thumb(src, dst, rec.get("dur", 0), cfg["thumb_width"], rec["kind"] == "image")
            except Exception as e:  # một file hỏng không được làm sập cả run
                print(f"  lỗi {kind} {rec['rel_path']}: {e}")
                return False

        t0 = time.time()
        done = 0
        with ThreadPoolExecutor(max_workers=6) as ex:
            oks = []
            for ok in ex.map(_job, jobs):
                oks.append(ok); done += 1
                if done % 500 == 0:
                    print(f"  ... {done}/{len(jobs)} ({time.time() - t0:.0f}s)", flush=True)
        print(f"xong {sum(oks)}/{len(jobs)} trong {time.time() - t0:.0f}s")
        failed = [j[3]["rel_path"] for j, ok in zip(jobs, oks) if not ok]
        if failed:
            print(f"  không tạo được {len(failed)} sheet/thumb:", *[f"\n    {f}" for f in failed[:15]])
        _refresh_media_fields()

    write_manifest(cfg, new)
    print(f"manifest: {len(new)} record -> {cfg['index_dir'] / 'manifest.jsonl'}")

    if args.prune:
        # sheet/thumb của record không còn trong manifest (file đã xóa/mất)
        n_pr = 0
        for sub in ("sheets", "thumbs"):
            d = idx / sub
            if not d.is_dir():
                continue
            for p in d.glob("*.jpg"):
                if p.stem not in new:
                    p.unlink(); n_pr += 1
        print(f"prune: xóa {n_pr} sheet/thumb mồ côi")


def cmd_stats(args):
    cfg = load_config()
    m = read_manifest(cfg)
    vids = [r for r in m.values() if r["kind"] == "video"]
    desc = [r for r in vids if r.get("scene")]
    print(f"manifest: {len(m)} record · video {len(vids)} · ảnh {len(m) - len(vids)}")
    print(f"đã mô tả: {len(desc)}/{len(vids)} video ({len(desc) * 100 // max(1, len(vids))}%)")
    print(f"có sheet: {sum(1 for r in vids if r.get('sheet'))}/{len(vids)}")
    broken = [r for r in m.values() if r.get("broken")]
    if broken:
        print(f"⚠ không probe được {len(broken)} file:", *[f"\n    {r['rel_path']}" for r in broken[:10]])
    dups = [r for r in m.values() if r.get("dups")]
    if dups:
        print(f"trùng nội dung: {len(dups)} record có bản sao ở đường dẫn khác (xem trường dups)")
    from collections import Counter
    print("\nname_class:", dict(Counter(r["name_class"] for r in vids)))
    print("orient:", dict(Counter(r.get("orient") for r in vids)))
    print("\n% mô tả theo thư mục:")
    byf = Counter(); byd = Counter()
    for r in vids:
        byf[r["folder"]] += 1
        if r.get("scene"):
            byd[r["folder"]] += 1
    for f, n in byf.most_common():
        print(f"  {byd[f]:4d}/{n:<4d} {f}")


def resolve_id(m: dict, id_: str | None, path: str | None) -> str:
    """Nhận id trực tiếp, hoặc rel_path / tên file (so không dấu, không phân biệt hoa thường)."""
    if id_:
        if id_ not in m:
            sys.exit(f"không có id {id_} trong manifest")
        return id_
    key = fold(path.replace("\\", "/").split("broll/", 1)[-1])
    hits = [r for r in m.values() if fold(r["rel_path"]) == key or key in [fold(d) for d in r.get("dups", [])]]
    if not hits:
        hits = [r for r in m.values() if fold(r["filename"]) == fold(Path(path).name)]
    if len(hits) != 1:
        sys.exit(f"path '{path}' khớp {len(hits)} record — dùng --id")
    return hits[0]["id"]


def cmd_approve(args):
    cfg = load_config()
    m = read_manifest(cfg)
    if not (args.id or args.path):
        sys.exit("cần --id hoặc --path")
    args.id = resolve_id(m, args.id, args.path)
    g = read_graph(cfg)
    g["edges"] = [e for e in g["edges"] if not (e["concept"] == args.concept and e["id"] == args.id)]
    g["edges"].append({
        "concept": nfc(args.concept), "tokens": sorted(set(fold(args.concept).split())),
        "id": args.id, "media_start": args.media_start, "weight": args.weight,
        "note": args.note, "source": args.source, "ts": int(time.time()),
    })
    write_graph(cfg, g)
    print(f"đã ghi: '{args.concept}' -> {m[args.id]['rel_path']} @ {args.media_start}s")


def cmd_show(args):
    cfg = load_config()
    m = read_manifest(cfg)
    rec = m.get(args.id)
    if not rec:
        sys.exit("không có id")
    rec = dict(rec)
    rec["abs_path"] = str(abs_path(cfg, rec))
    for k in ("sheet", "thumb"):
        if rec.get(k):
            rec[k] = str(cfg["index_dir"] / rec[k])
    print(json.dumps(rec, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("update"); u.add_argument("--sheets", action="store_true"); u.add_argument("--force", action="store_true")
    u.add_argument("--prune", action="store_true", help="xóa sheet/thumb của record đã mất")
    sub.add_parser("stats")
    a = sub.add_parser("approve")
    a.add_argument("--concept", required=True); a.add_argument("--id"); a.add_argument("--path", help="rel_path hoặc tên file thay cho --id")
    a.add_argument("--media-start", type=float, default=0.0); a.add_argument("--weight", type=int, default=1)
    a.add_argument("--note", default=""); a.add_argument("--source", default="user")
    s = sub.add_parser("show"); s.add_argument("id")
    args = ap.parse_args()
    {"update": cmd_update, "stats": cmd_stats, "approve": cmd_approve, "show": cmd_show}[args.cmd](args)


if __name__ == "__main__":
    main()

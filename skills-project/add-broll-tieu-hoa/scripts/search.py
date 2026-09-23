# -*- coding: utf-8 -*-
"""Tìm B-roll theo Ý (không chỉ theo tên file).

    python search.py "người đàn ông lớn tuổi xoa đầu gối, nhăn mặt" --topic xuong_khop -n 8
    python search.py "sáp mía cuba" --product raydel
    python search.py "mất ngủ" --kind real_person --mood negative --exclude-used used.txt --json

Điểm = khớp token có trọng số trên scene/tags/action/segments/tên file/thư mục
+ từ đồng nghĩa trong taxonomy + ưu tiên pool + cạnh đã duyệt (concept_graph).
Kết quả in kèm đường dẫn sheet để mở xem trước khi chọn.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

from common import (abs_path, fold, load_config, load_taxonomy, read_graph,
                    read_manifest, tokens)

W = {"scene": 3.0, "tags": 3.0, "action": 2.5, "segments": 2.0, "filename": 1.5,
     "dups": 1.5,  # bản sao ở thư mục khác thường mang tên có nghĩa hơn (slug Đã Chuẩn Hóa)
     "body_part": 2.0, "mechanism": 2.0, "setting": 1.0, "folder": 0.8, "topics": 1.0}
POOL_BONUS = {"chuan_hoa": 1.5, "product": 0.0, "topic": 0.8, "dilim_quay": 0.5, "cta": 0.0, "lon_xon": -0.6}


def expand(qtoks: list[str], tax: dict) -> Counter:
    """Token gốc trọng số 1; token đồng nghĩa 0.6."""
    out = Counter({t: 1.0 for t in qtoks})
    syn = tax.get("synonyms") or {}
    joined = " ".join(qtoks)
    for key, alts in syn.items():
        k = fold(key)
        if k in joined:
            for a in alts:
                for t in tokens(a):
                    out[t] = max(out[t], 0.6)
    return out


def field_text(rec: dict, f: str) -> str:
    v = rec.get(f)
    if not v:
        return ""
    if f == "segments":
        return " ".join(s.get("scene", "") for s in v)
    if isinstance(v, list):
        return " ".join(map(str, v))
    return str(v)


def score(rec: dict, q: Counter, df: Counter, n_docs: int) -> tuple[float, list[str]]:
    total = 0.0
    hits: list[str] = []
    for f, w in W.items():
        ft = set(tokens(field_text(rec, f)))
        if not ft:
            continue
        for t, qw in q.items():
            if t in ft:
                idf = math.log(1 + n_docs / (1 + df[t]))
                total += w * qw * idf
                hits.append(f"{f}:{t}")
    total += POOL_BONUS.get(rec.get("pool", "topic"), 0)
    if rec.get("low_res"):
        total -= 1.0
    if not rec.get("scene"):
        total -= 0.5  # chưa mô tả -> chỉ khớp theo tên, kém tin cậy
    return total, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("-n", type=int, default=10)
    ap.add_argument("--topic"); ap.add_argument("--kind"); ap.add_argument("--mood")
    ap.add_argument("--product"); ap.add_argument("--folder")
    ap.add_argument("--orient", choices=["landscape", "portrait", "square"])
    ap.add_argument("--min-dur", type=float, default=0.0)
    ap.add_argument("--images", action="store_true", help="gồm cả ảnh tĩnh")
    ap.add_argument("--exclude-used", help="file txt mỗi dòng 1 id đã dùng trong video này")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg = load_config(); tax = load_taxonomy()
    m = read_manifest(cfg); g = read_graph(cfg)
    used = set()
    if args.exclude_used and Path(args.exclude_used).is_file():
        used = {l.strip() for l in Path(args.exclude_used).read_text(encoding="utf-8").splitlines() if l.strip()}

    recs = []
    for r in m.values():
        if r.get("broken"):
            continue
        if r["kind"] == "image" and not args.images and not args.product:
            continue
        if args.product and r.get("product_id") != args.product:
            continue
        if not args.product and r.get("pool") == "product":
            continue  # clip sản phẩm chỉ lấy khi được yêu cầu đúng sản phẩm
        if args.topic and args.topic not in (r.get("topics") or []):
            continue
        if args.kind and r.get("subject_type") != args.kind:
            continue
        if args.mood and r.get("mood") != args.mood:
            continue
        if args.folder and fold(args.folder) not in fold(r.get("folder", "")):
            continue
        if args.orient and r.get("orient") != args.orient:
            continue
        if args.min_dur and (r.get("dur") or 0) < args.min_dur:
            continue
        if r["id"] in used:
            continue
        recs.append(r)

    qt = tokens(args.query)
    q = expand(qt, tax)
    df = Counter()
    for r in recs:
        seen = set()
        for f in W:
            seen |= set(tokens(field_text(r, f)))
        for t in seen:
            df[t] += 1

    scored = []
    for r in recs:
        s, hits = score(r, q, df, len(recs)) if q else (0.0, [])
        if q and s <= 0:
            continue
        scored.append((s, r, hits))
    scored.sort(key=lambda x: -x[0])

    # cạnh đã duyệt: mọi token của concept nằm trong query -> đưa lên đầu
    approved = []
    if qt:
        qset = set(qt)
        for e in g.get("edges", []):
            if e["id"] in m and e["id"] not in used and set(e["tokens"]) <= qset | set(q.keys()):
                approved.append(e)

    out = []
    for e in approved:
        r = m[e["id"]]
        out.append({"approved": True, "concept": e["concept"], "media_start": e.get("media_start", 0), "note": e.get("note", ""), **view(cfg, r, 99.0, ["APPROVED"])})
    for s, r, hits in scored[: args.n]:
        out.append(view(cfg, r, s, hits))

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1)); return
    if not out:
        print("không có kết quả — thử bỏ bớt filter, đổi cách tả cảnh, hoặc kiểm tra build_index.py stats (chủ đề này đã mô tả chưa?)"); return
    for o in out:
        tag = "APPROVED " if o.get("approved") else ""
        print(f"\n[{o['id']}] {tag}{o['score']:.1f}  {o['dur']}s {o['orient']} {o.get('subject_type') or '?'}/{o.get('mood') or '?'}  pool={o['pool']}")
        print(f"  {o['rel_path']}")
        if o.get("scene"):
            print(f"  scene: {o['scene']}")
        if o.get("segments"):
            for s in o["segments"]:
                print(f"    {s.get('t0', 0):>6.1f}-{s.get('t1', 0):<6.1f} {s.get('scene', '')}")
        if o.get("concept"):
            print(f"  concept: {o['concept']} @ {o['media_start']}s  {o.get('note', '')}")
        print(f"  sheet: {o['sheet']}")
        print(f"  hits: {', '.join(o['hits'][:8])}")


def view(cfg, r, s, hits):
    return {
        "id": r["id"], "score": round(s, 2), "rel_path": r["rel_path"], "abs_path": str(abs_path(cfg, r)),
        "dur": r.get("dur"), "orient": r.get("orient"), "pool": r.get("pool"), "product_id": r.get("product_id"),
        "subject_type": r.get("subject_type"), "mood": r.get("mood"), "scene": r.get("scene"),
        "segments": r.get("segments"), "tags": r.get("tags"),
        "sheet": str(cfg["index_dir"] / r["sheet"]) if r.get("sheet") else None,
        "thumb": str(cfg["index_dir"] / r["thumb"]) if r.get("thumb") else None,
        "hits": hits,
    }


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Tìm SFX theo loại + sắc thái + thời lượng.

    python search_sfx.py "whoosh ngắn" --cat whoosh --max-dur 1
    python search_sfx.py "đúng ding tích cực" -n 8
    python search_sfx.py "quê xệ" --root sound-effect --json
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter

from common import abs_path, fold, load_config, load_taxonomy, read_favs, read_manifest, tokens

W = {"filename": 3.0, "folder": 2.0, "folder_tags": 3.0, "tags": 3.0, "category": 2.0, "dups": 1.0}


def expand(qtoks, tax):
    out = Counter({t: 1.0 for t in qtoks})
    joined = " ".join(qtoks)
    for key, alts in (tax.get("synonyms") or {}).items():
        if fold(key) in joined or any(fold(a) in joined for a in alts):
            for a in [key] + list(alts):
                for t in tokens(a):
                    out[t] = max(out[t], 0.7)
    return out


def ftext(rec, f):
    v = rec.get(f)
    if not v: return ""
    return " ".join(map(str, v)) if isinstance(v, list) else str(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("-n", type=int, default=10)
    ap.add_argument("--cat"); ap.add_argument("--root")
    ap.add_argument("--min-dur", type=float, default=0.0); ap.add_argument("--max-dur", type=float, default=0.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    cfg = load_config(); tax = load_taxonomy(); m = read_manifest(cfg); favs = read_favs(cfg)
    prio = {r["name"]: r.get("priority", 3) for r in cfg["sfx_roots"]}

    recs = []
    for r in m.values():
        if r.get("broken") or not r.get("dur"): continue
        if args.cat and r.get("category") != args.cat: continue
        if args.root and r.get("root") != args.root: continue
        if args.min_dur and r["dur"] < args.min_dur: continue
        if args.max_dur and r["dur"] > args.max_dur: continue
        recs.append(r)

    qt = tokens(args.query); q = expand(qt, tax)
    df = Counter()
    for r in recs:
        for t in set(sum((tokens(ftext(r, f)) for f in W), [])): df[t] += 1
    n = len(recs)
    scored = []
    for r in recs:
        s = 0.0; hits = []
        for f, w in W.items():
            ft = set(tokens(ftext(r, f)))
            for t, qw in q.items():
                if t in ft:
                    s += w * qw * math.log(1 + n / (1 + df[t])); hits.append(f"{f}:{t}")
        if q and s <= 0: continue
        s -= 0.4 * prio.get(r["root"], 3)         # kho ưu tiên lên trước
        if r.get("tagged_by") == "user": s += 1.5
        if r["dur"] > 3 and (args.cat or "") not in ("riser", "drama", "ambience", "crowd"): s -= 1.0
        scored.append((s, r, hits))
    scored.sort(key=lambda x: -x[0])

    out = []
    if qt:
        qset = set(q.keys())
        for fv in favs.get("items", []):
            if fv["id"] in m and set(fv["tokens"]) <= qset:
                out.append({"favorite": True, "event": fv["event"], "volume": fv.get("volume"), **view(cfg, m[fv["id"]], 99, ["FAVORITE"])})
    for s, r, h in scored[: args.n]:
        out.append(view(cfg, r, s, h))
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1)); return
    if not out:
        print("không có kết quả — bỏ bớt filter hoặc đổi từ (xem synonyms trong taxonomy-sfx.yaml)"); return
    for o in out:
        tag = "FAVORITE " if o.get("favorite") else ""
        print(f"\n[{o['id']}] {tag}{o['score']:.1f}  {o['dur']:.2f}s  peak {o.get('peak_db')}dB  lead {o.get('lead_s')}s  cat={o['category']}  root={o['root']}")
        print(f"  {o['rel_path']}")
        if o.get("folder_tags"): print(f"  nhãn: {', '.join(o['folder_tags'])}")
        if o.get("event"): print(f"  event: {o['event']} @vol {o['volume']}")
        print(f"  hits: {', '.join(o['hits'][:6])}")


def view(cfg, r, s, hits):
    return {"id": r["id"], "score": round(s, 2), "rel_path": r["rel_path"], "abs_path": str(abs_path(cfg, r)),
            "dur": r.get("dur"), "peak_db": r.get("peak_db"), "lead_s": r.get("lead_s"), "category": r.get("category"),
            "root": r.get("root"), "folder_tags": r.get("folder_tags"), "tags": r.get("tags"), "hits": hits}


if __name__ == "__main__":
    main()

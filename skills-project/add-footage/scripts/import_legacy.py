# -*- coding: utf-8 -*-
"""Nhập cặp ý↔clip đã duyệt từ pipeline cũ (tinh-media-workflow/broll_memory.json)
vào concept_graph.json. Đường dẫn cũ trỏ D:\\download\\Footage B-roll\\... ->
khớp theo rel_path (NFC, không phân biệt hoa thường) với manifest hiện tại.

    python import_legacy.py "D:/tinh-media-workflow/pipeline/broll_memory.json"
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from common import fold, load_config, nfc, read_graph, read_manifest, write_graph


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cfg = load_config(); m = read_manifest(cfg); g = read_graph(cfg)
    by_rel = {fold(r["rel_path"]): r for r in m.values()}
    by_name = {}
    for r in m.values():
        by_name.setdefault(fold(r["filename"]), []).append(r)
    src = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    have = {(e["concept"], e["id"]) for e in g["edges"]}
    n_ok = n_miss = 0
    for e in src:
        p = e["path"].replace("\\", "/")
        rel = p.split("Footage B-roll/", 1)[-1]
        rec = by_rel.get(fold(rel))
        if not rec:
            cands = by_name.get(fold(Path(rel).name), [])
            rec = cands[0] if len(cands) == 1 else None
        if not rec:
            n_miss += 1; print("không khớp:", rel); continue
        concept = nfc(e["y"]).replace(" / ", " ").replace(" | ", " ")
        if (concept, rec["id"]) in have:
            continue
        g["edges"].append({
            "concept": concept, "tokens": sorted(set(e.get("tok") or fold(concept).split())),
            "id": rec["id"], "media_start": float(e.get("src_start_s", 0.0)), "weight": 1,
            "note": "", "source": e.get("nguon", "legacy"), "ts": int(time.time()),
        })
        have.add((concept, rec["id"])); n_ok += 1
    write_graph(cfg, g)
    print(f"nhập {n_ok} cạnh · không khớp {n_miss} · tổng {len(g['edges'])}")


if __name__ == "__main__":
    main()

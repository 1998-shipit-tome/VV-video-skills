# -*- coding: utf-8 -*-
"""Dọn kho footage theo các luật AN TOÀN (không mất footage tốt), dựa trên manifest.

    python clean_kho.py --dry-run                      # chỉ liệt kê
    python clean_kho.py --apply                        # xóa thật, ghi log
    ... --rules dups,junk,broken,long,web_images,badname_lonxon  (mặc định: dups,junk,broken)
    ... --long-min 180   --badname-folder "Lộn Xộn Xà bần"

Luật:
  dups           bản sao trùng nội dung 100% (trường dups) — giữ đường dẫn chính
  junk           file không phải video/ảnh (mp3, gif, desktop.ini...) — quét thư mục, bỏ Music
  broken         file ffprobe không đọc được
  long           video dài hơn --long-min giây (YouTube/screensaver, không phải B-roll)
  web_images     ảnh trong --badname-folder (ảnh web tải về), TRỪ tên có dấu hiệu sản phẩm
  badname_lonxon video tên vô nghĩa (canva/stock_id/junk) CHỈ trong --badname-folder

Không bao giờ xóa: clip có trong concept_graph (đã duyệt), pool product.
Sau khi --apply: chạy build_index.py update để manifest bỏ record đã mất.
Log: <index_dir>/cleanup-<timestamp>.txt — mỗi dòng: luật <TAB> rel_path (khôi phục từ kho gốc theo rel_path).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from common import fold, load_config, nfc, read_graph, read_manifest

PRODUCT_HINT = ("san pham", "sun", "gluchongel", "q10", "coenzyme", "raydel", "policosanol", "ellagic",
                "inulin", "nghe", "okinawa", "natto", "hau", "nano", "dha", "epa", "collagen", "fucoidan",
                "nmn", "insuna", "dilim", "dili", "hop", "combo", "gmp", "cong bo", "nhan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--rules", default="dups,junk,broken")
    ap.add_argument("--long-min", type=float, default=180.0)
    ap.add_argument("--badname-folder", default="Lộn Xộn Xà bần")
    ap.add_argument("--show", type=int, default=12, help="số mẫu in ra mỗi luật")
    args = ap.parse_args()
    if not (args.dry_run or args.apply):
        sys.exit("chọn --dry-run hoặc --apply")
    rules = {r.strip() for r in args.rules.split(",") if r.strip()}

    cfg = load_config(); m = read_manifest(cfg); g = read_graph(cfg)
    root: Path = cfg["broll_root"]
    approved = {e["id"] for e in g.get("edges", [])}
    bad_folder = nfc(args.badname_folder)
    plan: dict[str, list[tuple[str, int]]] = defaultdict(list)  # rule -> [(rel_path, size)]
    protected: list[str] = []

    def protect(rec) -> bool:
        if rec["id"] in approved or rec.get("pool") == "product":
            protected.append(rec["rel_path"]); return True
        return False

    if "dups" in rules:
        for r in m.values():
            for d in r.get("dups") or []:
                plan["dups"].append((d, r.get("size", 0)))

    if "junk" in rules:
        vext = set(cfg["video_ext"]); iext = set(cfg["image_ext"]); skip = {nfc(s) for s in cfg["skip_dirs"]}
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if rel.parts and nfc(rel.parts[0]) in skip:
                continue
            if p.suffix.lower() not in vext and p.suffix.lower() not in iext:
                plan["junk"].append((nfc(str(rel).replace("\\", "/")), p.stat().st_size))

    if "broken" in rules:
        for r in m.values():
            if r.get("broken") and not protect(r):
                plan["broken"].append((r["rel_path"], r.get("size", 0)))

    if "long" in rules:
        for r in m.values():
            if r["kind"] == "video" and (r.get("dur") or 0) > args.long_min and not protect(r):
                plan["long"].append((r["rel_path"], r.get("size", 0)))

    if "web_images" in rules:
        for r in m.values():
            if r["kind"] == "image" and nfc(r.get("folder", "")) == bad_folder:
                name = fold(r["filename"])
                if any(h in name for h in PRODUCT_HINT):
                    protected.append(r["rel_path"] + "  (tên gợi sản phẩm)"); continue
                if not protect(r):
                    plan["web_images"].append((r["rel_path"], r.get("size", 0)))

    if "badname_lonxon" in rules:
        for r in m.values():
            if r["kind"] == "video" and nfc(r.get("folder", "")) == bad_folder \
                    and r.get("name_class") in ("canva", "stock_id", "junk") and not protect(r):
                plan["badname_lonxon"].append((r["rel_path"], r.get("size", 0)))

    # gộp, bỏ trùng giữa các luật
    seen = set(); total_b = 0; n = 0
    for rule in ("dups", "junk", "broken", "long", "web_images", "badname_lonxon"):
        items = [(p, s) for p, s in plan.get(rule, []) if not (p in seen or seen.add(p))]
        plan[rule] = items
        b = sum(s for _, s in items); total_b += b; n += len(items)
        print(f"[{rule:15}] {len(items):5d} file  {b / 1e9:6.2f} GB")
        for p, _ in items[: args.show]:
            print(f"      {p}")
        if len(items) > args.show:
            print(f"      ... +{len(items) - args.show}")
    print(f"\nTỔNG: {n} file, {total_b / 1e9:.2f} GB")
    if protected:
        print(f"\nĐược bảo vệ (không xóa): {len(protected)}")
        for p in protected[:20]:
            print(f"      {p}")

    if not args.apply:
        print("\n(dry-run — chưa xóa gì; thêm --apply để xóa)"); return

    log = cfg["index_dir"] / f"cleanup-{time.strftime('%Y%m%d-%H%M%S')}.txt"
    deleted = missing = 0
    with open(log, "w", encoding="utf-8") as f:
        for rule, items in plan.items():
            for rel, _ in items:
                p = root / rel
                try:
                    os.remove(p); deleted += 1
                    f.write(f"{rule}\t{rel}\n")
                except FileNotFoundError:
                    missing += 1
                except OSError as e:
                    f.write(f"LỖI {rule}\t{rel}\t{e}\n")
    # dọn thư mục rỗng
    for d in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
        try:
            d.rmdir()
        except OSError:
            pass
    print(f"\nđã xóa {deleted} file (không thấy {missing}) — log: {log}")
    print("chạy tiếp: python build_index.py update")


if __name__ == "__main__":
    main()

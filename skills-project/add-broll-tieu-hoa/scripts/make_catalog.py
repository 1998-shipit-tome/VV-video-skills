# -*- coding: utf-8 -*-
"""Sinh references/catalog.md từ index/manifest.jsonl — bảng tra nhanh toàn bộ
kho để agent đọc một lần thay vì search mò. Chạy lại sau mỗi lần thêm clip
hoặc merge mô tả mới:

    python make_catalog.py
"""
from __future__ import annotations

from pathlib import Path

from common import REF_DIR, load_config, read_manifest


def main():
    cfg = load_config(); m = read_manifest(cfg)
    lines = ["# Danh mục kho B-roll tiêu hóa", "",
             "Sinh tự động bởi `scripts/make_catalog.py` — đừng sửa tay. Mỗi dòng: `id` · thời lượng · "
             "loại chủ thể/sắc thái · **tên file** → cảnh (kèm mốc đoạn nếu clip nhiều cảnh). Đường dẫn tương đối "
             "so với `footage/`. Clip chưa có cảnh thì tên file chính là mô tả.", ""]
    groups: dict[str, list] = {}
    for r in m.values():
        groups.setdefault(str(Path(r["rel_path"]).parent).replace("\\", "/"), []).append(r)
    n_all = sum(len(v) for v in groups.values())
    n_desc = sum(1 for r in m.values() if r.get("scene"))
    lines.append(f"Tổng {n_all} file · {n_desc} đã có mô tả cảnh."); lines.append("")
    for g in sorted(groups):
        rs = sorted(groups[g], key=lambda r: r["rel_path"])
        n_v = sum(1 for r in rs if r["kind"] == "video")
        lines.append(f"## {g}  ({n_v} video, {len(rs) - n_v} ảnh)"); lines.append("")
        for r in rs:
            dur = f"{r['dur']:.0f}s" if r.get("dur") and r["kind"] == "video" else "ảnh"
            st = r.get("subject_type") or "?"; mood = r.get("mood") or "?"
            flags = " ⚠" + ",".join(r["quality_flags"]) if r.get("quality_flags") else ""
            line = f"- `{r['id']}` {dur} {st}/{mood}{flags} — **{r['filename']}**"
            if r.get("scene"):
                line += f" → {r['scene']}"
            lines.append(line)
            for s in r.get("segments") or []:
                lines.append(f"    - {s.get('t0', 0):.0f}–{s.get('t1', 0):.0f}s: {s.get('scene', '')}")
        lines.append("")
    out = REF_DIR / "catalog.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"catalog: {out} ({n_all} file, {n_desc} mô tả)")


if __name__ == "__main__":
    main()

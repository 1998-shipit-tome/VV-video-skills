# -*- coding: utf-8 -*-
"""Dùng chung cho mọi script add-footage: config, chuẩn hóa Unicode, hash id,
đọc/ghi manifest. Không import gì ngoài stdlib + yaml."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL_DIR = Path(__file__).resolve().parent.parent
REF_DIR = SKILL_DIR / "references"

_DEFAULT_CFG = {
    "broll_root": r"D:\HYPERFRAME\footage\broll",
    "index_dir": r"D:\HYPERFRAME\footage\index",
    "sheet_frames": 12,
    "sheet_cols": 4,
    "sheet_width": 320,
    "thumb_width": 480,
    "skip_dirs": ["Music"],
    "video_ext": [".mp4", ".mov", ".webm", ".mkv", ".m4v"],
    "image_ext": [".jpg", ".jpeg", ".png", ".webp", ".jfif"],
}


def find_config() -> Path | None:
    env = os.environ.get("ADD_FOOTAGE_CONFIG")
    cands = [Path(env)] if env else []
    cands += [
        Path(r"D:\HYPERFRAME\footage\config.json"),
        Path.cwd() / "footage" / "config.json",
        Path.cwd() / "config.json",
    ]
    for c in cands:
        if c and c.is_file():
            return c
    return None


def load_config() -> dict:
    cfg = dict(_DEFAULT_CFG)
    p = find_config()
    if p:
        cfg.update(json.loads(p.read_text(encoding="utf-8")))
        cfg["_config_path"] = str(p)
    cfg["broll_root"] = Path(os.path.expandvars(cfg["broll_root"]))
    cfg["index_dir"] = Path(os.path.expandvars(cfg["index_dir"]))
    return cfg


# ---------- chuỗi ----------
def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def fold(s: str) -> str:
    """Bỏ dấu tiếng Việt + lowercase để so khớp: 'Mất ngủ' -> 'mat ngu'."""
    s = nfc(s).replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.lower()


_TOK = re.compile(r"[a-z0-9]+")
# từ nối/phổ biến không mang nghĩa hình ảnh — bỏ để khỏi kéo điểm lệch
STOP = {"va", "la", "cua", "tren", "trong", "roi", "dang", "thi", "co", "khong", "mot", "nhu",
        "de", "cho", "voi", "tu", "den", "bi", "duoc", "cac", "nhung", "ra", "len", "xuong",
        "lam", "vao", "ve", "sau", "truoc", "khi", "hai", "ba", "mp4", "mov", "png", "jpg"}


def tokens(s: str) -> list[str]:
    return [t for t in _TOK.findall(fold(s)) if len(t) > 1 and t not in STOP]


# ---------- id ----------
def quick_hash(path: Path, chunk: int = 1 << 20) -> str:
    """Hash nhanh: size + 1MB đầu + 1MB cuối. Đủ ổn định để nhận lại file khi
    đổi tên/dời thư mục, mà không phải đọc hết 77 GB."""
    h = hashlib.sha1()
    size = path.stat().st_size
    h.update(str(size).encode())
    with open(path, "rb") as f:
        h.update(f.read(chunk))
        if size > chunk * 2:
            f.seek(-chunk, os.SEEK_END)
            h.update(f.read(chunk))
        elif size > chunk:
            f.seek(chunk)
            h.update(f.read())
    return h.hexdigest()[:12]


# ---------- manifest ----------
def manifest_path(cfg: dict) -> Path:
    return cfg["index_dir"] / "manifest.jsonl"


def read_manifest(cfg: dict) -> dict[str, dict]:
    p = manifest_path(cfg)
    out: dict[str, dict] = {}
    if not p.is_file():
        return out
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[rec["id"]] = rec
    return out


def write_manifest(cfg: dict, recs: dict[str, dict]) -> None:
    p = manifest_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for rec in sorted(recs.values(), key=lambda r: r["rel_path"]):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, p)


def graph_path(cfg: dict) -> Path:
    return cfg["index_dir"] / "concept_graph.json"


def read_graph(cfg: dict) -> dict:
    p = graph_path(cfg)
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"version": 1, "edges": []}


def write_graph(cfg: dict, g: dict) -> None:
    p = graph_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")


def load_taxonomy() -> dict:
    import yaml  # PyYAML có sẵn trên máy này
    return yaml.safe_load((REF_DIR / "taxonomy.yaml").read_text(encoding="utf-8"))


def abs_path(cfg: dict, rec: dict) -> Path:
    return cfg["broll_root"] / rec["rel_path"]

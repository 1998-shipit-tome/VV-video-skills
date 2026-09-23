# -*- coding: utf-8 -*-
"""Dùng chung cho add-sfx: config nhiều root, chuẩn hóa Unicode, hash id, manifest."""
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
    "sfx_roots": [{"name": "sfx", "path": r"D:\HYPERFRAME\footage\sfx", "priority": 1}],
    "index_dir": r"D:\HYPERFRAME\footage\sfx-index",
    "audio_ext": [".wav", ".mp3", ".aac", ".m4a", ".ogg", ".flac", ".aif", ".aiff", ".wma"],
    "video_ext": [".mp4", ".mov", ".webm", ".mkv"],
    "analyze_max_sec": 30,
}


def find_config() -> Path | None:
    env = os.environ.get("ADD_SFX_CONFIG")
    cands = [Path(env)] if env else []
    cands += [Path(r"D:\HYPERFRAME\footage\sfx-config.json"), Path.cwd() / "sfx-config.json"]
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
    cfg["index_dir"] = Path(os.path.expandvars(cfg["index_dir"]))
    roots = []
    for r in cfg["sfx_roots"]:
        roots.append({**r, "path": Path(os.path.expandvars(r["path"]))})
    cfg["sfx_roots"] = roots
    return cfg


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def fold(s: str) -> str:
    s = nfc(s).replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.lower()


_TOK = re.compile(r"[a-z0-9]+")
STOP = {"va", "la", "cua", "the", "and", "for", "with", "of", "to", "in", "on", "by", "sound", "effect",
        "effects", "sfx", "fx", "free", "royalty", "hd", "com", "www", "y2mate", "mp3", "wav", "aac", "m4a",
        "tiengdong", "epidemic", "es", "sba", "premium"}


def tokens(s: str) -> list[str]:
    return [t for t in _TOK.findall(fold(s)) if len(t) > 1 and t not in STOP]


def quick_hash(path: Path, chunk: int = 256 << 10) -> str:
    """size + 256 KB đầu + 256 KB cuối. SFX phần lớn < 2 MB nên khối nhỏ vẫn
    phân biệt tốt, và không phải đọc hết 21 GB thư viện mỗi lần build."""
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


def manifest_path(cfg: dict) -> Path:
    return cfg["index_dir"] / "manifest.jsonl"


def read_manifest(cfg: dict) -> dict[str, dict]:
    p = manifest_path(cfg)
    out: dict[str, dict] = {}
    if p.is_file():
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line); out[rec["id"]] = rec
    return out


def write_manifest(cfg: dict, recs: dict[str, dict]) -> None:
    p = manifest_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for rec in sorted(recs.values(), key=lambda r: r["rel_path"]):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, p)


def fav_path(cfg: dict) -> Path:
    return cfg["index_dir"] / "favorites.json"


def read_favs(cfg: dict) -> dict:
    p = fav_path(cfg)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {"version": 1, "items": []}


def write_favs(cfg: dict, d: dict) -> None:
    p = fav_path(cfg); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def load_taxonomy() -> dict:
    import yaml
    return yaml.safe_load((REF_DIR / "taxonomy-sfx.yaml").read_text(encoding="utf-8"))


def abs_path(cfg: dict, rec: dict) -> Path:
    root_name, _, rest = rec["rel_path"].partition("/")
    for r in cfg["sfx_roots"]:
        if r["name"] == root_name:
            return r["path"] / rest
    return Path(rec["rel_path"])

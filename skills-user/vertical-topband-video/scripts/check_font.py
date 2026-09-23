"""Kiem tra mot font co du ky tu dau tieng Viet khong.

Ly do ton tai: Bebas Neue va Impact co dung cai look condensed dam ma format nay
can, nen rat hay bi chon - nhung ca hai THIEU dau tieng Viet. Loi chi lo ra sau
khi da render xong ca video, luc do sua rat dat.

    python check_font.py "C:/Windows/Fonts/Anton-Regular.ttf"
    python check_font.py --scan          # quet moi font da cai
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

from fontTools.ttLib import TTFont

# Console Windows mac dinh cp1252, khong in duoc chinh cac ky tu ma script nay
# di kiem tra -> phai ep UTF-8, neu khong script crash dung luc bao loi.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Nguyen am doi + dau thanh - phan ma font Latin thong thuong hay thieu nhat.
VN_HARD = ("ẾỀỂỄỆỐỒỔỖỘỚỜỞỠỢỨỪỬỮỰẤẦẨẪẬẮẰẲẴẶ"
           "ĐƯƠĂÂÊÔÍÌỈĨỊÚÙỦŨỤÝỲỶỸỴ")

FONT_DIRS = [
    "C:/Windows/Fonts",
    os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
    "/usr/share/fonts", "/Library/Fonts", os.path.expanduser("~/Library/Fonts"),
]


def check(path: str) -> tuple[bool, str, list[str]]:
    f = TTFont(path, fontNumber=0, lazy=True)
    cmap: set[int] = set()
    for t in f["cmap"].tables:
        cmap |= set(t.cmap.keys())
    family = f["name"].getDebugName(1) or os.path.basename(path)
    f.close()
    missing = [c for c in VN_HARD if ord(c) not in cmap]
    return (not missing), family, missing


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("font", nargs="?")
    ap.add_argument("--scan", action="store_true",
                    help="Quet moi font da cai, chi liet ke font DAT")
    args = ap.parse_args()

    if args.scan:
        seen: set[str] = set()
        ok_list: list[tuple[str, str]] = []
        for d in FONT_DIRS:
            for p in glob.glob(os.path.join(d, "*.ttf")) + glob.glob(os.path.join(d, "*.otf")):
                b = os.path.basename(p).lower()
                if b in seen:
                    continue
                seen.add(b)
                try:
                    ok, fam, _ = check(p)
                except Exception:
                    continue
                if ok:
                    ok_list.append((fam, os.path.basename(p)))
        ok_list.sort()
        print(f"{len(ok_list)} font du dau tieng Viet:\n")
        for fam, fn in ok_list:
            print(f"  {fam:<38} {fn}")
        return

    if not args.font:
        ap.error("can duong dan font, hoac --scan")
    if not os.path.exists(args.font):
        raise SystemExit(f"Khong thay file: {args.font}")

    ok, family, missing = check(args.font)
    n = len(VN_HARD)
    if ok:
        print(f"DAT  {n}/{n}  family='{family}'")
        print(f"     Dat vao preset:  \"font\": {{ \"family\": \"{family}\", "
              f"\"file\": \"{args.font.replace(chr(92), '/')}\" }}")
    else:
        print(f"THIEU {n - len(missing)}/{n}  family='{family}'")
        print(f"      Ky tu thieu: {''.join(missing)}")
        print("      Dung font nay se ra o vuong hoac dau hoi. "
              "Thay bang Anton / Be Vietnam Pro Black / Montserrat Black.")
        sys.exit(1)


if __name__ == "__main__":
    main()

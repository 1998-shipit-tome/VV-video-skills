"""Render video doc 9:16 layout top-band split tu mot file ke hoach JSON.

Pipeline (thu tu nay khong tuy tien - moi buoc chua mot bay da gap):

  1. Cat A-roll thanh cac segment theo ranh gioi beat.
     Moi segment: A-roll dich xuong + dai B-roll overlay + Ken Burns.
  2. Concat cac segment bang -c copy (khong encode lai).
  3. Pass cuoi: overlay logo, roi BURN CAPTION SAU CUNG.
     Caption phai o cuoi chuoi filter, neu khong overlay se de len chu.
  4. Ghep am thanh goc cua A-roll nguyen ven.
     Khong cat bo thoi gian nao nen khong can afade chong pop.
  5. End card noi bang concat demuxer (params encode giong het).

Dung:
    python build.py plan.json -o final.mp4
    python build.py plan.json -o preview.mp4 --preview
    python build.py plan.json --lint-only
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assgen import TextMeasurer, build_ass, build_endcard_ass  # noqa: E402

HERE = Path(__file__).resolve().parent
PRESET_DIR = HERE.parent / "presets"


# --------------------------------------------------------------- tien ich ---

def run(cmd: list[str], cwd: str | None = None, quiet: bool = True) -> None:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.stderr.write("\n=== FFMPEG LOI ===\n")
        sys.stderr.write(" ".join(cmd[:14]) + " ...\n")
        sys.stderr.write((r.stderr or "")[-3500:] + "\n")
        raise SystemExit(1)
    if not quiet and r.stderr:
        sys.stderr.write(r.stderr[-1500:])


def probe(path: str) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"Khong doc duoc file: {path}")
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    if v is None:
        raise SystemExit(f"File khong co luong video: {path}")
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den or 1)
    has_audio = any(s["codec_type"] == "audio" for s in d["streams"])
    return {
        "width": int(v["width"]), "height": int(v["height"]), "fps": fps,
        "duration": float(d["format"].get("duration") or v.get("duration") or 0),
        "has_audio": has_audio,
    }


def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_cfg(plan: dict, plan_dir: Path) -> dict:
    name = plan.get("preset", "dilim")
    p = Path(name)
    if not p.suffix:
        p = PRESET_DIR / f"{name}.json"
    elif not p.is_absolute():
        p = plan_dir / p
    cfg = json.loads(p.read_text(encoding="utf-8"))
    return deep_merge(cfg, plan.get("brand", {}))


def resolve(path: str | None, plan_dir: Path) -> str | None:
    if not path:
        return None
    p = Path(path)
    return str(p if p.is_absolute() else (plan_dir / p))


# ------------------------------------------------------------- kiem tra ke hoach ---

def lint(plan: dict, cfg: dict, dur: float) -> list[str]:
    """Kiem tra nhip - phan de sai nhat va cung de sua nhat.

    Ba loi hay gap: beat qua ngan/dai, khong co breather (man hinh khong bao gio
    nghi -> nguoi xem moi mat), va mat do B-roll lech xa video mau.
    """
    rh = cfg["rhythm"]
    msgs: list[str] = []
    beats = plan["beats"]

    covered = 0.0
    last_end = 0.0
    gaps: list[tuple[float, float]] = []
    for i, b in enumerate(beats):
        d = b["end"] - b["start"]
        if d < rh["beat_min"]:
            msgs.append(f"  beat {i} ({b['start']:.2f}s) chi {d:.2f}s "
                        f"- nhanh hon nguong {rh['beat_min']}s, chu se khong kip doc")
        if d > rh["beat_max"]:
            msgs.append(f"  beat {i} ({b['start']:.2f}s) dai {d:.2f}s "
                        f"- qua nguong {rh['beat_max']}s, man hinh dung yen qua lau")
        if b["start"] < last_end - 1e-6:
            msgs.append(f"  beat {i} chong len beat truoc ({b['start']:.2f} < {last_end:.2f})")
        if b["start"] > last_end + 1e-6:
            gaps.append((last_end, b["start"]))
        if b.get("broll"):
            covered += d
        last_end = max(last_end, b["end"])
    if dur > last_end + 1e-6:
        gaps.append((last_end, dur))

    real_gaps = [g for g in gaps if g[1] - g[0] >= rh["breather_min"]]
    density = covered / dur if dur else 0
    lo, hi = rh["broll_density_target"]
    if density < lo:
        msgs.append(f"  mat do B-roll {density:.0%} - thap hon muc tieu {lo:.0%}. "
                    "Video mau phu ~83%. Tim them clip, dung ha chuan de lap cho.")
    if density > hi:
        msgs.append(f"  mat do B-roll {density:.0%} - cao hon {hi:.0%}, "
                    "man hinh khong con cho nghi.")

    # Khoang cach giua cac breather
    marks = [0.0] + [g[0] for g in real_gaps] + [dur]
    for a, b2 in zip(marks, marks[1:]):
        if b2 - a > rh["breather_every"] * 1.35:
            msgs.append(f"  {a:.1f}s -> {b2:.1f}s ({b2 - a:.1f}s) khong co breather nao "
                        f"- video mau cu ~{rh['breather_every']:.0f}s lai co 1 nhip A-roll sach")

    print(f"[lint] {len(beats)} beat | mat do B-roll {density:.0%} | "
          f"{len(real_gaps)} breather | thoi luong {dur:.1f}s")
    return msgs


# --------------------------------------------------------------- filtergraph ---

def band_chain(cfg: dict, W: int, BH: int, fps: float, beat: dict,
               dur: float, label_in: str, label_out: str) -> str:
    br = beat["broll"]
    k = float(br.get("kenburns", cfg["kenburns"]["default"]))
    nf = max(1, int(round(dur * fps)))
    parts = [
        # fps PHAI chuan hoa TRUOC zoompan. Neu dua luong fps khac (vd clip 25fps)
        # thang vao zoompan, filter treo vo han - khong bao loi, chi dung im.
        # Day la bug that da gap khi dung script nay lan dau.
        f"[{label_in}]fps={fps:g}",
        f"scale={W * 2}:{BH * 2}:force_original_aspect_ratio=increase",
        f"crop={W * 2}:{BH * 2}",
    ]
    if abs(k - 1.0) > 1e-3:
        # Pre-scale 2x truoc zoompan la bat buoc: zoompan tren anh dung kich thuoc
        # dich se giat tung frame vi no lam tron toa do crop ve so nguyen.
        parts.append(
            f"zoompan=z='min(1+{k - 1:.4f}*on/{nf},{k})'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d=1:s={W}x{BH}")
    else:
        parts.append(f"scale={W}:{BH}")
    parts += ["setsar=1", f"fps={fps:g}", "format=yuva420p"]

    tin = br.get("in_transition", cfg["transitions"]["band_in"])
    if tin == "dissolve":
        d = cfg["transitions"]["dissolve_dur"]
        parts.append(f"fade=t=in:st=0:d={d}:alpha=1")
    return "".join([",".join(parts), f"[{label_out}]"])


def overlay_xy(cfg: dict, W: int, BH: int, beat: dict, dur: float) -> tuple[str, str]:
    br = beat["broll"]
    tin = br.get("in_transition", cfg["transitions"]["band_in"])
    tout = br.get("out_transition", cfg["transitions"]["band_out"])
    sd = cfg["transitions"]["slide_dur"]
    x, y = "0", "0"
    if tin == "slide_left":
        x = f"'-{W}+{W}*min(1,t/{sd})'"
    if tout == "slide_up":
        y = f"'-{BH}*max(0,(t-({dur:.4f}-{sd}))/{sd})'"
    return x, y


def render_segment(cfg: dict, aroll: str, beat: dict, idx: int,
                   workdir: Path, plan_dir: Path, scale: float) -> Path:
    W = int(cfg["canvas"]["width"] * scale)
    H = int(cfg["canvas"]["height"] * scale)
    W -= W % 2
    H -= H % 2
    fps = cfg["canvas"]["fps"]
    BH = int(cfg["layout"]["band_height_ratio"] * H)
    BH -= BH % 2
    TY = int(cfg["layout"]["aroll_translate_ratio"] * H)
    TY -= TY % 2

    s, e = beat["start"], beat["end"]
    dur = e - s
    nf = max(1, int(round(dur * fps)))
    out = workdir / f"seg_{idx:04d}.mp4"

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{s:.4f}", "-t", f"{dur + 0.5:.4f}", "-i", aroll]

    ar = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},setsar=1,fps={fps:g}[ar]")

    if not beat.get("broll"):
        fc = f"{ar};[ar]null[v]"
    else:
        br = beat["broll"]
        src = resolve(br["src"], plan_dir)
        if not src or not os.path.exists(src):
            raise SystemExit(f"Khong tim thay clip B-roll cua beat {idx}: {br['src']}")
        bin_ = float(br.get("in", 0.0))
        cmd += ["-ss", f"{bin_:.4f}", "-t", f"{dur + 0.5:.4f}", "-i", src]

        bandf = band_chain(cfg, W, BH, fps, beat, dur, "1:v", "band")
        ox, oy = overlay_xy(cfg, W, BH, beat, dur)
        fc = (f"{ar};"
              f"color=c=black:s={W}x{H}:d={dur + 0.5:.4f}:r={fps:g}[bg];"
              f"[bg][ar]overlay=x=0:y={TY}:shortest=1[base];"
              f"{bandf};"
              f"[base][band]overlay=x={ox}:y={oy}:eof_action=pass[v]")

    cmd += ["-filter_complex", fc, "-map", "[v]", "-frames:v", str(nf), "-an"]
    cmd += vcodec(cfg, scale) + [str(out)]
    run(cmd)
    return out


def vcodec(cfg: dict, scale: float) -> list[str]:
    crf = "20" if scale < 1.0 else "16"
    preset = "veryfast" if scale < 1.0 else "medium"
    return ["-c:v", "libx264", "-preset", preset, "-crf", crf,
            "-pix_fmt", "yuv420p", "-r", f"{cfg['canvas']['fps']:g}"]


def acodec() -> list[str]:
    return ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


# ------------------------------------------------------------------- endcard ---

def render_endcard(cfg: dict, workdir: Path, scale: float, lines: list[str],
                   dur: float) -> Path:
    W = int(cfg["canvas"]["width"] * scale); W -= W % 2
    H = int(cfg["canvas"]["height"] * scale); H -= H % 2
    fps = cfg["canvas"]["fps"]
    ec = cfg["endcard"]

    (workdir / "endcard.ass").write_text(
        build_endcard_ass({**cfg, "canvas": {**cfg["canvas"], "width": W, "height": H}},
                          lines, dur), encoding="utf-8")

    c0 = "0x" + ec["gradient"][0].lstrip("#")
    c1 = "0x" + ec["gradient"][1].lstrip("#")
    inset = int(ec["border_inset_ratio"] * W)
    bw = max(2, int(ec["border_w"] * scale))
    flash_d = ec.get("flash_frames", 1) / fps

    fc = (f"[0:v]drawbox=x={inset}:y={inset}:w={W - 2 * inset}:h={H - 2 * inset}"
          f":color={ec['border_color']}@1:t={bw},"
          f"drawbox=x=0:y=0:w={W}:h={H}:color=white@1:t=fill"
          f":enable='lt(t,{flash_d:.4f})',"
          f"subtitles=endcard.ass,format=yuv420p[v]")

    out = workdir / "endcard.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i",
         f"gradients=s={W}x{H}:c0={c0}:c1={c1}:d={dur}:r={fps:g}:speed=0.015",
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
         "-t", f"{dur}"] + vcodec(cfg, scale) + acodec() + [str(out)],
        cwd=str(workdir))
    return out


# ---------------------------------------------------------------------- main ---

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--preview", action="store_true",
                    help="Render 1/2 do phan giai, encode nhanh - de duyet nhip")
    ap.add_argument("--lint-only", action="store_true")
    ap.add_argument("--keep", action="store_true", help="Giu thu muc tam")
    args = ap.parse_args()

    plan_path = Path(args.plan).resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan_dir = plan_path.parent
    cfg = load_cfg(plan, plan_dir)

    aroll = resolve(plan["aroll"], plan_dir)
    if not aroll or not os.path.exists(aroll):
        raise SystemExit(f"Khong tim thay A-roll: {plan['aroll']}")
    info = probe(aroll)
    cfg["canvas"]["fps"] = plan.get("fps", cfg["canvas"].get("fps") or info["fps"])
    fps = cfg["canvas"]["fps"]
    dur = float(plan.get("duration") or info["duration"])

    # Snap moi moc thoi gian ve frame. Neu khong, -frames:v se lech dan
    # va cuoi video hinh se troi khoi tieng.
    beats = sorted(plan["beats"], key=lambda b: b["start"])
    for b in beats:
        b["start"] = round(b["start"] * fps) / fps
        b["end"] = min(round(b["end"] * fps) / fps, dur)
    beats = [b for b in beats if b["end"] - b["start"] > 1e-6]

    problems = lint({**plan, "beats": beats}, cfg, dur)
    if problems:
        print("[lint] can xem lai:")
        for m in problems:
            print(m)
    else:
        print("[lint] nhip dat chuan")
    if args.lint_only:
        return

    # Chen cac doan trong = breather A-roll sach.
    full: list[dict] = []
    t = 0.0
    for b in beats:
        if b["start"] > t + 1e-6:
            full.append({"start": t, "end": b["start"]})
        full.append(b)
        t = b["end"]
    if dur > t + 1e-6:
        full.append({"start": t, "end": dur})

    scale = 0.5 if args.preview else 1.0
    out_path = Path(args.output or plan.get("output") or "final.mp4")
    if not out_path.is_absolute():
        out_path = plan_dir / out_path

    workdir = Path(tempfile.mkdtemp(prefix="topband_"))
    try:
        print(f"[render] {len(full)} segment @ {int(cfg['canvas']['width'] * scale)}x"
              f"{int(cfg['canvas']['height'] * scale)} {fps:g}fps")
        segs = []
        for i, b in enumerate(full):
            segs.append(render_segment(cfg, aroll, b, i, workdir, plan_dir, scale))
            print(f"\r[render] segment {i + 1}/{len(full)}", end="", flush=True)
        print()

        lst = workdir / "segs.txt"
        lst.write_text("".join(f"file '{p.name}'\n" for p in segs), encoding="utf-8")
        base = workdir / "base.mp4"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", "segs.txt",
             "-c", "copy", str(base)], cwd=str(workdir))

        # Caption: sinh ASS o do phan giai dang render.
        cfg_scaled = json.loads(json.dumps(cfg))
        cfg_scaled["canvas"]["width"] = int(cfg["canvas"]["width"] * scale)
        cfg_scaled["canvas"]["height"] = int(cfg["canvas"]["height"] * scale)
        meas = TextMeasurer(cfg["font"].get("file"))
        (workdir / "captions.ass").write_text(
            build_ass(cfg_scaled, beats, meas), encoding="utf-8")

        W = cfg_scaled["canvas"]["width"]
        logo = resolve(cfg["logo"].get("src"), plan_dir)
        inputs = ["-i", str(base), "-i", aroll]
        chain = "[0:v]"
        if logo and os.path.exists(logo):
            inputs += ["-i", logo]
            lw = int(cfg["logo"]["width_ratio"] * W)
            lx = int(cfg["logo"]["x_ratio"] * W)
            ly = int(cfg["logo"]["y_ratio"] * cfg_scaled["canvas"]["height"])
            chain = (f"[2:v]scale={lw}:-1[lg];[0:v][lg]"
                     f"overlay=x={lx}:y={ly}[wm];[wm]")
        # Caption burn SAU CUNG - neu dat truoc overlay logo/dai thi bi che.
        fc = chain + "subtitles=captions.ass,format=yuv420p[v]"

        maps = ["-map", "[v]"]
        if info["has_audio"]:
            maps += ["-map", "1:a"]
        stage = workdir / "body.mp4"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inputs +
            ["-filter_complex", fc] + maps + ["-t", f"{dur:.4f}"] +
            vcodec(cfg, scale) + (acodec() if info["has_audio"] else ["-an"]) +
            [str(stage)], cwd=str(workdir))

        ec = plan.get("endcard")
        if ec and cfg["endcard"].get("enabled", True) and ec.get("lines"):
            print("[render] end card")
            card = render_endcard(cfg, workdir, scale, ec["lines"],
                                  float(ec.get("duration", cfg["endcard"]["duration"])))
            lst2 = workdir / "final.txt"
            lst2.write_text(f"file '{stage.name}'\nfile '{card.name}'\n", encoding="utf-8")
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-f", "concat", "-safe", "0", "-i", "final.txt",
                 "-c", "copy", str(out_path)], cwd=str(workdir))
        else:
            shutil.copy(str(stage), str(out_path))

        print(f"[xong] {out_path}")
    finally:
        if args.keep:
            print(f"[tam] {workdir}")
        else:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()

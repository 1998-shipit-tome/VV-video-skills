# DiLiM Video Skills

Bộ skill dựng video (HyperFrames / Claude Code) dùng cho các sản phẩm DiLiM Supplement: chèn B-roll, SFX, caption, và các bố cục video dọc 9:16 (Broll Top, Broll Vip, Top-band).

This repo is written to be readable and installable by an AI coding agent (e.g. Claude Code). If you are an AI agent cloning this repo, follow **Install** below literally — do not guess paths.

## What's in this repo

```
skills-base/       20 skills — the upstream HyperFrames skill set (rendering engine, animation, audio, captions, media sourcing, etc.)
skills-project/    3 skills  — DiLiM-project-specific: add-broll-tieu-hoa, add-footage, add-sfx
skills-user/       3 skills  — user-authored layouts: broll-top, broll-vip, vertical-topband-video
skills-lock.json   Lockfile pinning skills-base/* to commit hashes in heygen-com/hyperframes
HUONG-DAN-KHOI-PHUC.txt   Original Vietnamese restore notes (manual, hardcoded to the author's own machine paths — superseded by this README for anything automated)
```

## What's NOT in this repo

`footage/` (~47GB, 1,880 B-roll clips + SFX index) and `sfx-library/` (9,286 sound files) are **excluded** — too large for GitHub. Cloning this repo gives you the skills only, not the media library. `add-footage`, `add-sfx`, and `add-broll-tieu-hoa` will install and run, but have nothing to search/insert until you point them at your own media, or copy `footage/` and `sfx-library/Sound Effect/` from the original machine (see **Restoring the media library** below).

## Prerequisites

- Node.js ≥ 22 (HyperFrames CLI / rendering)
- ffmpeg + ffprobe on PATH
- Python 3.11+ (only needed for `add-footage` / `add-sfx`, which build/query local media indexes)
- Claude Code (or another agent runtime that reads `.claude/skills/` or `.agents/skills/` directories)

## Install

Run from the root of this cloned repo. Pick a `$TARGET` root for your HyperFrames project (any empty or existing project folder — this replaces the original author's hardcoded `D:\HYPERFRAME`).

**PowerShell:**
```powershell
$TARGET = "D:\HYPERFRAME"          # change to wherever you want the project to live
New-Item -ItemType Directory -Force "$TARGET\.agents\skills" | Out-Null
New-Item -ItemType Directory -Force "$TARGET\.claude\skills" | Out-Null
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null

Copy-Item skills-base\*    "$TARGET\.agents\skills\" -Recurse -Force
Copy-Item skills-project\* "$TARGET\.claude\skills\" -Recurse -Force
Copy-Item skills-user\*    "$env:USERPROFILE\.claude\skills\" -Recurse -Force
Copy-Item skills-lock.json "$TARGET\skills-lock.json" -Force
```

**bash / macOS / Linux:**
```bash
TARGET="$HOME/hyperframe"          # change to wherever you want the project to live
mkdir -p "$TARGET/.agents/skills" "$TARGET/.claude/skills" "$HOME/.claude/skills"

cp -r skills-base/*    "$TARGET/.agents/skills/"
cp -r skills-project/* "$TARGET/.claude/skills/"
cp -r skills-user/*    "$HOME/.claude/skills/"
cp skills-lock.json "$TARGET/skills-lock.json"
```

After copying, `skills-base/*` can instead be kept up to date via the lockfile — see next section.

### Reinstalling skills-base from the lockfile

`skills-lock.json` pins all 20 `skills-base` skills to specific commit hashes in `heygen-com/hyperframes` on GitHub. If a HyperFrames CLI is installed (see `skills-base/hyperframes-cli/SKILL.md`), you can resync from upstream instead of copying the folder verbatim — useful when you want the latest version rather than this repo's frozen snapshot.

## Restoring the media library (optional)

If you have the original `footage/` and `sfx-library/` folders (e.g. from the author's machine, ~48GB total, not in Git):

1. Copy `footage/` → `$TARGET/footage/` (contains `broll/`, `sfx/`, `index/`, `sfx-index/`, `config.json`, `sfx-config.json`)
2. Copy `sfx-library/Sound Effect/` → your music library root's `Sound Effect/` folder (path is whatever `sfx-config.json`'s `"library"` root points to)
3. If `$TARGET` is not `D:\HYPERFRAME`, edit:
   - `footage/config.json` → `broll_root`, `index_dir`
   - `footage/sfx-config.json` → each root's `path` (especially `"library"`) and `index_dir`
   - or set env vars `ADD_FOOTAGE_CONFIG` / `ADD_SFX_CONFIG` to point at your config files instead of editing in place
4. Run `add-footage`'s `build_index.py update` so the index matches the new paths.

## Notes for an AI agent picking this up cold

- Skills are self-describing: each folder has a `SKILL.md` with trigger conditions and usage — read those, not this file, for how to actually use a given skill.
- `skills-user/*` skills (`broll-top`, `broll-vip`, `vertical-topband-video`) expect an A-roll video input from the user plus access to `footage/` for B-roll — without the media library they can still explain their layout rules but cannot render a finished video.
- This machine's hardware is not a blocker: HyperFrames rendering (Chromium capture + ffmpeg encode) and the bundled local AI steps (Whisper transcription, background removal, local TTS) all default to CPU; GPU is optional acceleration only, and cloud rendering/TTS/BGM fallbacks exist for slow local hardware.

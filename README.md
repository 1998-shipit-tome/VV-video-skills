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

`add-footage` and `add-sfx` never hardcode which files exist — they read a `config.json` / `sfx-config.json` that lists root folders, then build an index from whatever is actually there. This means there are two independent paths, and you only need one of them.

### Path A — Restore the original author's exact library

Use this if you have a copy of the author's own `footage/` (~48GB, `broll/`, `sfx/`, `index/`, `sfx-index/`) and `sfx-library/Sound Effect/` (21GB, 9,286 files) folders — e.g. pulled from their machine over NAS/Drive, not from Git.

1. Copy `footage/` → `$TARGET/footage/`
2. Copy `sfx-library/Sound Effect/` → wherever your music library root should live (this becomes the `"library"` root's `path` in step 3)
3. Create the config files from the templates already in this repo (they are NOT inside the excluded `footage/` folder, so they exist here regardless of whether you have the media):
   ```powershell
   Copy-Item "$TARGET\.claude\skills\add-footage\config.example.json" "$TARGET\footage\config.json"
   Copy-Item "$TARGET\.claude\skills\add-sfx\config.example.json"     "$TARGET\footage\sfx-config.json"
   ```
   Then edit both (they are plain JSON, an AI agent can just rewrite the paths):
   - `footage/config.json` → `broll_root` (→ `$TARGET/footage/broll`), `index_dir` (→ `$TARGET/footage/index`)
   - `footage/sfx-config.json` → each entry in `sfx_roots[].path`, especially the `"library"` entry (→ wherever you put `sfx-library/Sound Effect/`), and `index_dir` (→ `$TARGET/footage/sfx-index`)
   - Alternative to editing in place: set env vars `ADD_FOOTAGE_CONFIG` / `ADD_SFX_CONFIG` to the full path of your config files, and leave the defaults untouched.
4. Rebuild the index so it matches the new paths (existing hashes reuse their old descriptions automatically — only genuinely new files need re-describing):
   ```bash
   python "$TARGET/.claude/skills/add-footage/scripts/build_index.py" update
   python "$TARGET/.claude/skills/add-sfx/scripts/build_sfx_index.py" update
   ```

### Path B — Point at a brand-new / differently-named media library

Use this if you do **not** have the author's original folders — e.g. you're setting this project up on a different machine with your own B-roll/SFX collection, under any folder names or drive you want. Nothing requires the folders to be called `footage` or `sfx-library`, or to live where the original did.

1. Put your own video clips and sound files anywhere on disk — one root folder for B-roll, one or more root folders for SFX. Sub-folder structure inside each root is up to you; `add-footage`/`add-sfx` will crawl it.
2. Create fresh config files from the same templates as Path A (they are the source of truth for the schema — do not invent new keys):
   ```powershell
   Copy-Item "$TARGET\.claude\skills\add-footage\config.example.json" "$TARGET\footage\config.json"
   Copy-Item "$TARGET\.claude\skills\add-sfx\config.example.json"     "$TARGET\footage\sfx-config.json"
   ```
3. Edit the copies to describe your library, not the author's:
   - `config.json` → set `broll_root` to your B-roll folder's real path, `index_dir` to wherever the generated index should live (any empty folder is fine, it will be created).
   - `sfx-config.json` → replace `sfx_roots` entirely with one entry per SFX folder you actually have: `{"name": "<short-id>", "path": "<real path>", "priority": <1 lower = searched first>}`. You do not need 8 roots like the original — one root named e.g. `"my-sfx"` is a complete, valid config. Set `index_dir` to your chosen index location.
4. Build the index from scratch (first run scans and describes everything, so it takes longer than an `update` on an existing index):
   ```bash
   python "$TARGET/.claude/skills/add-footage/scripts/build_index.py" update
   python "$TARGET/.claude/skills/add-sfx/scripts/build_sfx_index.py" update
   ```
5. Most clips will have meaningless filenames and no description yet — search quality depends on descriptions existing (see each skill's `SKILL.md`, "Quy trình B — Mô tả clip" / describe workflow) before B-roll/SFX selection will work well. This is expected on a first run against a brand-new library, not an error.

## Notes for an AI agent picking this up cold

- Skills are self-describing: each folder has a `SKILL.md` with trigger conditions and usage — read those, not this file, for how to actually use a given skill.
- `skills-user/*` skills (`broll-top`, `broll-vip`, `vertical-topband-video`) expect an A-roll video input from the user plus access to `footage/` for B-roll — without the media library they can still explain their layout rules but cannot render a finished video.
- This machine's hardware is not a blocker: HyperFrames rendering (Chromium capture + ffmpeg encode) and the bundled local AI steps (Whisper transcription, background removal, local TTS) all default to CPU; GPU is optional acceleration only, and cloud rendering/TTS/BGM fallbacks exist for slow local hardware.

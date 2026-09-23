# Schema add-sfx

Mọi file trong `index_dir` (mặc định `D:\HYPERFRAME\footage\sfx-index`). `rel_path` = `<root name>/<đường dẫn con>` để nhiều kho ở nhiều ổ vẫn một manifest; đem sang máy khác chỉ sửa `path` của root.

## manifest.jsonl

```json
{"id": "9c1f2e7a44b0",                 // quick-hash nội dung
 "rel_path": "sound-effect/LỰA CHỌN ĐÚNG - CHUÔNG/ding-correct-1.mp3",
 "filename": "ding-correct-1.mp3", "root": "sound-effect", "folder": "LỰA CHỌN ĐÚNG - CHUÔNG",
 "kind": "audio",                       // audio | video (mp4 có tiếng)
 "size": 48211, "mtime": 1757600000.0,
 "codec": "mp3", "sr": 44100, "ch": 2, "dur": 0.83,
 "peak_db": -3.2, "mean_db": -18.5,     // volumedetect trên 30 s đầu
 "lead_s": 0.06,                        // khoảng lặng đầu file (< -45 dB) — place_sfx trừ đi
 "category": "ding",                    // taxonomy-sfx.yaml
 "folder_tags": ["đúng", "tích cực", "chuông"],
 "tags": ["sáng", "ngắn"], "tagged_by": "user",   // gắn tay sau khi nghe
 "dups": ["library/.../ding-correct-1.mp3"],
 "broken": false}
```

## favorites.json — tiếng đã duyệt cho loại sự kiện

```json
{"version": 1, "items": [
  {"event": "caption hiện", "tokens": ["caption", "hien"], "id": "9c1f2e7a44b0", "volume": 0.13, "note": "user chốt 12/09", "ts": 1757600000}
]}
```

`search_sfx.py` đưa lên đầu (nhãn `FAVORITE`) khi mọi `tokens` của event nằm trong query.

## sfx-plan.json — cho một video

```json
{"video": "raydel-v10", "fps": 30, "track": 20,
 "items": [
   {"id": "9c1f2e7a44b0", "hit": 12.41, "volume": 0.13, "event": "caption 'MỠ MÁU CAO' hiện", "duration": null},
   {"id": "2b77d0e1aa93", "hit": 19.60, "volume": 0.18, "event": "riser trước khi lộ Raydel", "duration": 2.5}
 ]}
```

`hit` = thời điểm sự kiện hình ảnh (giây trên timeline). `place_sfx.py` tính `data-start = hit − lead_s`; `duration` null = cả file.

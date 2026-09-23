# Schema dữ liệu add-broll-tieu-hoa

Mọi file nằm trong `index_dir` (mặc định `<skill>/index`). Đường dẫn clip luôn **tương đối** so với `broll_root` (mặc định `<skill>/footage`).

## manifest.jsonl — mỗi dòng một clip

```json
{
  "id": "e26dc9db3c48",              // quick-hash nội dung (size + 1MB đầu + 1MB cuối). Ổn định khi đổi tên/dời.
  "rel_path": "01-trieu-chung/006 - Ngồi trên bồn cầu, cúi người, nhăn mặt nhíu mày và.mp4",
  "filename": "006 - Ngồi trên bồn cầu ….mp4",
  "folder": "01-trieu-chung",        // thư mục cấp 1 = nhóm
  "size": 15600000, "mtime": 1757600000.0,
  "kind": "video",                   // video | image
  "pool": "topic",                   // topic | product
  "topics": ["trieu_chung", "tao_bon"],
  "product_id": null, "asset_role": null,   // chỉ pool=product: inulin_fuji | nghe_okinawa | gan  /  video | nguyen_lieu | anh
  "w": 1920, "h": 1080, "fps": 30.0, "dur": 13.9,
  "orient": "landscape", "low_res": false,
  "sheet": "sheets/e26dc9db3c48.jpg", "thumb": "thumbs/e26dc9db3c48.jpg",
  "source_id": "e26dc9db3c48", "source_rel_path": "Đã Chuẩn Hóa/006 - …",   // vết về kho tổng DiLiM

  // ---- lớp ngữ nghĩa (search dùng) ----
  "scene": "Người đàn ông áo xanh ngồi trên bồn cầu…, rặn khó khăn",
  "subject_type": "real_person",     // real_person | anatomy_3d | product | metaphor_object | lifestyle_scene | text_graphic | screen_ui
  "action": "ngồi bồn cầu nhăn mặt rặn",
  "mood": "painful",                 // positive | negative | neutral | painful | tense
  "body_part": "bụng", "mechanism": null, "setting": "nhà vệ sinh",
  "has_text": false,
  "segments": [ {"t0": 0, "t1": 14, "scene": "..."} ],   // chỉ khi clip có ≥2 cảnh khác hẳn
  "tags": ["táo bón", "bồn cầu", "rặn"],
  "quality_flags": [],               // watermark | burned_text | low_res | dark | small_subject | name_mismatch
  "described_by": "agent", "described_at": 1757600000
}
```

`search.py` chấm điểm trên: `scene`, `tags`, `action`, `segments[].scene`, `filename`, `body_part`, `mechanism`, `setting`, `folder`, `topics`; trừ điểm `low_res` và clip chưa có `scene`.

## concept_graph.json — cặp ý ↔ clip đã duyệt

```json
{"version": 1, "edges": [
  {"concept": "táo bón", "tokens": ["bon", "tao"], "id": "e26dc9db3c48", "media_start": 0.0,
   "weight": 1, "note": "ngồi bồn cầu rặn khó — mặc định DiLiM", "source": "dilim-seed", "ts": 1757600000}
]}
```

`search.py` đưa cạnh lên đầu (nhãn `APPROVED`) khi mọi `tokens` xuất hiện trong query. Gói này có sẵn 24 cạnh gợi ý (`source: dilim-seed`); người dựng chốt clip khác thì ghi đè bằng `build_index.py approve --concept "…" --path "…"`.

## plan.json — quyết định đặt B-roll cho MỘT video

```json
{
  "video": "inulin-v1", "layout": "top", "fps": 30,
  "items": [
    {"id": "e26dc9db3c48", "start": 12.40, "duration": 3.20, "media_start": 0.00,
     "caption": "TÁO BÓN KÉO DÀI", "idea": "táo bón", "word": "táo bón", "word_t": 12.41, "verified": true}
  ],
  "gaps": [ {"start": 30.1, "end": 34.5, "idea": "ẩn dụ máy lọc nghẹt", "why": "kho không có clip ẩn dụ, để caption animation"} ]
}
```

`start` = thời điểm **từ kích hoạt** được nói (giây trên timeline), `media_start` = offset trong file nguồn. Ghi `gaps` để báo cáo trung thực phần để trống.

## batches/NNN.json và descriptions/NNN.jsonl

Chỉ dùng khi thêm clip mới (Quy trình B trong SKILL.md). Xem `describe-prompt.md`.

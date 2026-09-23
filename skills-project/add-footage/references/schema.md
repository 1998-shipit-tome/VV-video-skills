# Schema dữ liệu add-footage

Mọi file nằm trong `index_dir` (mặc định `D:\HYPERFRAME\footage\index`). Đường dẫn clip luôn **tương đối** so với `broll_root` để đem sang máy khác không phải sửa.

## manifest.jsonl — mỗi dòng một clip

```json
{
  "id": "3f9a1c77b2e4",              // quick-hash nội dung (size + 1MB đầu + 1MB cuối). Ổn định khi đổi tên/dời.
  "rel_path": "Đột quỵ/004 - Đẩy băng ca chở bệnh nhân chạy nhanh qua hành lang.mp4",
  "filename": "004 - Đẩy băng ca ....mp4",
  "folder": "Đột quỵ",               // thư mục gốc cấp 1
  "size": 13321939, "mtime": 1757600000.0,
  "kind": "video",                   // video | image
  "name_class": "described",         // described | canva | stock_id | junk | slug | free  (độ tin cậy của tên)
  "pool": "topic",                   // chuan_hoa | product | topic | dilim_quay | cta | lon_xon
  "topics": ["dot_quy", "mach_mau_than_kinh"],
  "product_id": null, "asset_role": null,   // chỉ pool=product: nano_sun... / video|nguyen_lieu|anh
  "w": 1920, "h": 1080, "fps": 30.0, "dur": 14.2,
  "orient": "landscape",             // landscape | portrait | square
  "low_res": false,
  "sheet": "sheets/3f9a1c77b2e4.jpg", "thumb": "thumbs/3f9a1c77b2e4.jpg",

  // ---- lớp ngữ nghĩa (từ Quy trình B; thiếu = chưa mô tả) ----
  "scene": "Đẩy băng ca có bệnh nhân nằm chạy nhanh qua hành lang bệnh viện, hai nhân viên y tế hai bên",
  "subject_type": "real_person",
  "action": "đẩy băng ca chạy nhanh",
  "mood": "tense",
  "body_part": null, "mechanism": null,
  "setting": "hành lang bệnh viện",
  "has_text": false, "color_tone": "trắng lạnh",
  "segments": [ {"t0": 0, "t1": 14.2, "scene": "..."} ],   // bắt buộc khi dur > 20s và có >1 cảnh
  "tags": ["cấp cứu", "bệnh viện", "băng ca", "khẩn cấp"],
  "topics_seen": ["dot_quy", "kham_benh"],
  "quality_flags": [],               // watermark | shaky | dark | burned_text | low_res | duplicate_of:<id>
  "described_by": "agent", "described_at": 1757600000
}
```

Trường nào `search.py` dùng để chấm điểm: `scene`, `tags`, `action`, `segments[].scene`, `filename`, `body_part`, `mechanism`, `setting`, `folder`, `topics`.

## concept_graph.json — cặp ý ↔ clip đã duyệt

```json
{"version": 1, "edges": [
  {"concept": "mất ngủ", "tokens": ["mat", "ngu"],
   "id": "3f9a1c77b2e4", "media_start": 2.0, "weight": 3,
   "note": "người dùng chốt 17/08/2026", "source": "user", "ts": 1757600000}
]}
```

`search.py` đưa cạnh lên đầu (nhãn `APPROVED`) khi mọi `tokens` của concept xuất hiện trong query (kể cả qua từ đồng nghĩa). `weight` tăng mỗi lần người dùng duyệt lại. Ghi bằng `build_index.py approve`; nhập từ pipeline cũ bằng `import_legacy.py`.

## plan.json — quyết định đặt B-roll cho MỘT video

```json
{
  "video": "rich-q10-v3", "layout": "top", "fps": 30,
  "used_ids_file": "used.txt",
  "items": [
    {"id": "3f9a1c77b2e4", "start": 12.40, "duration": 3.20, "media_start": 2.00,
     "caption": "ĐỘT QUỴ KHÔNG BÁO TRƯỚC", "idea": "đột quỵ bất ngờ", "word": "đột quỵ", "word_t": 12.41,
     "verified": true, "verify_frames": ["verify/3f9a1c77b2e4_2.00.jpg", "..."]}
  ],
  "gaps": [ {"start": 30.1, "end": 34.5, "idea": "hệ vi sinh đường ruột", "why": "không có clip khớp, để caption animation"} ]
}
```

`start` là thời điểm trên timeline composition (giây) = thời điểm **từ kích hoạt** được nói (`word_t`), sớm tối đa 1–3 frame. `media_start` là offset trong file nguồn. Ghi `gaps` để báo cáo trung thực phần để trống.

## batches/NNN.json và descriptions/NNN.jsonl

Xem `describe-prompt.md`. Batch chứa đường dẫn sheet + `frame_interval` (giây giữa 2 khung kề nhau trên sheet) để suy ra `segments`.

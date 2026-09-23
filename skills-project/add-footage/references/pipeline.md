# Pipeline dựng một video DiLiM — ai làm gì, cái gì chạy song song

Mục tiêu: rút thời gian ở bước tốn nhất (tìm + xác minh B-roll, 30–50 ý/video) bằng cách chia cho subagent, **không** rút ở bước người dùng duyệt. Nguyên tắc chia việc: script làm việc máy móc, subagent làm việc cục bộ cần phán đoán, agent cha giữ việc cần nhìn toàn cục.

```
A-roll.mp4
  │
  ├─ [script, chạy NỀN]  transcribe word-level  ──────────────────────────┐
  │     hyperframes transcribe / whisper large-v3 (CUDA) / ElevenLabs     │
  └─ [cha, cùng lúc]  đọc brief, nhận diện sản phẩm + giọng A/B,         │
        chọn bố cục top/vip, build_index.py update (footage + sfx)       │
                                                                          ▼
[cha]  tách transcript thành Ý; với mỗi ý quyết định: B-roll / caption animation / SFX / không gì
       (đây là "quy trình 2 bước" người dùng chốt 17/07: không phải ý nào cũng cần B-roll)
       → chia Ý thành N nhóm liên tiếp (8–10 ý/nhóm)
        │
        ├─► subagent B-roll #1 … #N   (mỗi nhóm 1 agent, chạy song song)
        │     input : nhóm ý + transcript đoạn đó + product_id + used.txt chung
        │     làm   : tưởng tượng cảnh → search.py → mở 3–5 sheet → verify_frame.py
        │     trả về: [{idea, id, media_start, duration, verify_frames, confidence, alt_ids}]
        │     KHÔNG: chèn vào index.html, quyết định bố cục, viết caption
        │
        └─► subagent SFX (1 agent cho cả video)
              input : danh sách sự kiện hình ảnh (từ plan caption/B-roll) + giọng A/B
              làm   : search_sfx.py theo loại + cảm xúc → sfx-plan.json (2–3 ứng viên cho hook/CTA)
                        │
                        ▼
[cha]  gộp N kết quả → soát chéo (chỉ cha thấy đủ):
         • không lặp clip không-sản-phẩm trong video (place.py cũng chặn)
         • sản phẩm đúng thư mục; combo đủ từng sản phẩm
         • đoạn > 5 s không chữ không B-roll → tìm lại hoặc ghi vào gaps có lý do
         • danh sách triệu chứng dồn dập → gộp đôi, đảo vế lượt 2
         • SFX: mật độ 1/3–5 s, không dính < 0,15 s
       → bảng duyệt HTML (lời thoại · caption · ảnh B-roll đúng khung · SFX · ghi chú)
                        │
                 người dùng duyệt / đổi clip   ← KHÔNG render trước khi duyệt (chốt 17/08/2026)
                        │  mỗi lần đổi clip → build_index.py approve (mặc định cho video sau)
                        ▼
[script]  place.py (B-roll) + place_sfx.py (SFX) → chèn index.html → hyperframes lint → render
[cha]     trích frame tại TỪNG data-start mới, đối chiếu cảnh đã tưởng tượng → báo cáo, ghi rõ gaps
```

## Vì sao chia như vậy

- **Transcribe không cần agent.** Là bấm nút chờ GPU; agent ngồi chờ chỉ tốn token. Chạy nền, cha làm việc khác.
- **Tách ý không giao con.** Cần thấy toàn bài để biết nhịp, giọng văn, chỗ nào là ẩn dụ lướt qua vs ẩn dụ chính, chỗ nào liệt kê dồn dập. Con chỉ thấy một khúc sẽ tách sai.
- **Tìm B-roll giao con theo nhóm ý liên tiếp**, không theo chủ đề: hai ý liền nhau dùng chung một file là hợp lệ (đoạn liên tục), con cùng nhóm sẽ thấy điều đó; chia rời sẽ vô tình lặp.
- **`used.txt` chung** giữa các con để `search.py --exclude-used` không đề xuất trùng nhau; cha vẫn soát lại vì các con chạy song song có thể chọn cùng clip cùng lúc.
- **SFX chỉ 1 con**: kho nhỏ, tiếng phải nhất quán trong một video (cùng loại sự kiện → cùng tiếng), chia nhiều con sẽ ra nhiều "ngôn ngữ âm thanh".
- **Bước duyệt của người dùng không đổi** — tốc độ đến từ tìm kiếm song song và kho đã mô tả (mở 2–3 sheet thay vì 8–10), không phải bỏ duyệt.

## Prompt mẫu cho subagent B-roll

```
Skill: D:\HYPERFRAME\.claude\skills\add-footage (đọc SKILL.md + references/selection-rules.md trước)
Video: <tên>, sản phẩm: <product_id hoặc "không">, bố cục: top
Nhóm ý #2 (8 ý), mỗi ý kèm câu gốc + word_t:
  1. "mảng xơ vữa bám dần vào thành mạch" @ 9.62s — cơ chế, cần anatomy_3d
  2. ...
Đã dùng (không đề xuất lại): D:\...\used.txt
Việc: với mỗi ý → viết cảnh lý tưởng 1 câu → search.py (--topic/--kind/--mood phù hợp) →
      mở sheet của ≥3 ứng viên → chọn 1 + 1 dự phòng → verify_frame.py --at <media_start> --span <dur> →
      ghi vào D:\...\group-2.json theo schema plan.items (thêm "confidence": high|medium|low và "why").
Không: chèn HTML, đổi caption, tự vẽ hình. Ý không có clip khớp thật → ghi vào gaps với lý do.
```

## Chạy bằng Workflow (tùy chọn)

Nếu người dùng nói "chạy bằng workflow", dựng script `pipeline(groups, agent B-roll, agent verify)` + `agent SFX` song song, cha gộp — cache kết quả từng con nên sửa một nhóm không chạy lại cả video. Không tự dùng Workflow khi người dùng chưa yêu cầu.

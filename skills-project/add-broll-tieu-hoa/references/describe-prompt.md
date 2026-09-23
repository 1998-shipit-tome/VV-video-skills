# Mô tả clip từ contact sheet

Bạn đang nhìn một contact sheet: 12 khung hình trải đều toàn bộ clip, xếp 4 cột × 3 hàng, đọc trái→phải, trên→dưới. Khung thứ k (0-based) ứng với thời điểm `t = k × frame_interval` giây. Metadata kèm theo cho biết `dur`, `filename`, `folder`, `frame_interval`.

Mục đích của mô tả: để một agent **chưa từng xem clip** tìm được nó khi đang cần minh họa một ý trong lời nói, và loại được nó khi sai sắc thái. Vì vậy mô tả phải trả lời được 4 câu hỏi xác minh mà pipeline đã từng sai:

1. **Cảnh cụ thể là gì** — hành động, chủ thể, bối cảnh. Không phải "chủ đề".
2. **Cơ chế/bộ phận nào** nếu là đồ họa y khoa — "khớp gối bị bào mòn, sụn tách khỏi bề mặt xương" khác "dây thần kinh phát sáng dọc cột sống" dù cùng là "xương khớp".
3. **Sắc thái cảm xúc** — vẻ mặt, không khí. Người ăn salad *vui vẻ* và người ăn salad *chán ghét* là hai ý trái ngược.
4. **Clip có nhiều cảnh không** — nếu nội dung đổi hẳn giữa các khung, ghi `segments` với mốc thời gian để chọn đúng `media_start`.

## Nhìn ảnh, đừng đoán theo tên file

Tên file có thể gợi ý (`003 - Ngồi trên xe lăn, nhìn xa xăm rồi cúi đầu xuống, hai...`) nhưng thường bị **cắt cụt** hoặc **vô nghĩa** (`Thiết kế chưa có tên - 2025-08-18`). Viết theo cái nhìn thấy; tên file chỉ dùng để đối chiếu. Nếu tên file mâu thuẫn với ảnh, ảnh thắng — ghi thêm vào `quality_flags: ["name_mismatch"]`.

## Output — một object JSON mỗi clip, một dòng

```json
{"id": "<id từ batch>",
 "scene": "Cụ ông ngồi ghế sofa, một tay chống gậy, tay kia xoa đầu gối, nhăn mặt vì đau; phòng khách sáng",
 "action": "xoa đầu gối, nhăn mặt",
 "subject_type": "real_person",
 "mood": "painful",
 "body_part": "đầu gối",
 "mechanism": null,
 "setting": "phòng khách",
 "has_text": false,
 "color_tone": "ấm, sáng",
 "segments": [],
 "tags": ["người già", "đau khớp", "chống gậy", "xoa gối", "nhăn mặt"],
 "topics_seen": ["xuong_khop"],
 "quality_flags": []}
```

Quy ước từng trường:

| Trường | Yêu cầu |
|---|---|
| `scene` | 1–2 câu tiếng Việt, **mở đầu bằng động từ hoặc chủ thể + động từ**. Đủ cụ thể để phân biệt với clip cùng chủ đề: ai (tuổi/giới nếu thấy rõ), làm gì, ở đâu, biểu cảm. |
| `action` | cụm động từ ngắn nhất tả hành động chính. Search dựa nhiều vào đây. |
| `subject_type` | một trong `real_person`, `anatomy_3d`, `product`, `metaphor_object`, `lifestyle_scene`, `text_graphic`, `screen_ui` |
| `mood` | `positive` (vui, khỏe, nhẹ nhõm) · `negative` (buồn, chán, lo) · `painful` (đau, khó chịu thể chất) · `tense` (khẩn cấp, căng thẳng) · `neutral` |
| `body_part` / `mechanism` | với đồ họa y khoa: bộ phận + điều đang xảy ra ("mảng bám tích tụ làm hẹp lòng mạch", "sụn mòn lộ xương"). Người thật thì `body_part` là nơi tay chạm/đau, `mechanism` null. |
| `segments` | chỉ khi có **≥2 cảnh khác hẳn nhau**: `[{"t0":0,"t1":8.5,"scene":"..."},{"t0":8.5,"t1":20,"scene":"..."}]`. Mốc lấy từ chỉ số khung × `frame_interval`, làm tròn 0.5s. Clip 1 cảnh liên tục → `[]`. |
| `tags` | 4–8 từ khóa tiếng Việt, gồm cả từ **người dựng hay gõ** khi tìm ("ôm đầu", "trằn trọc", "cụng ly") chứ không chỉ thuật ngữ. |
| `topics_seen` | id trong `taxonomy.yaml` nếu clip rõ ràng thuộc chủ đề khác/thêm so với thư mục (clip trong `Lộn Xộn Xà bần` **bắt buộc** điền). |
| `quality_flags` | `watermark`, `shaky`, `dark`, `burned_text` (chữ burn sẵn), `low_res`, `name_mismatch`, `nsfw_hint`, `duplicate_of:<id>` nếu nhận ra trùng clip đã mô tả trong cùng batch. |

Viết tiếng Việt có dấu. Không bịa chi tiết không thấy trên sheet — thà `scene` ngắn mà đúng.

## Cách chạy theo lô (agent)

1. `python scripts/describe_batches.py make --topic <id>` → `index/batches/NNN.json`
2. Với mỗi item: Read file `sheet` → viết 1 dòng JSON vào `index/descriptions/NNN.jsonl` (append). Làm tuần tự, mỗi clip nhìn ảnh thật; đừng "nhìn 3 cái rồi suy ra 17 cái còn lại".
3. `python scripts/describe_batches.py merge` → báo số dòng hợp lệ/lỗi.
4. Kiểm tra: `search.py "<một ý trong chủ đề>"` rồi mở sheet của 3 kết quả đầu.

Nhiều batch → giao mỗi subagent 1–3 batch, kèm nguyên văn file này. Subagent chỉ ghi vào file `output` ghi trong batch.

## API (tùy chọn)

Khi có `ANTHROPIC_API_KEY` và `pip install anthropic`: `describe_batches.py auto --batch NNN` gửi từng sheet kèm metadata với file này làm system prompt, model mặc định `claude-sonnet-5`. Kết quả cũng qua `merge` như thường.

---
name: add-broll-tieu-hoa
description: Kho B-roll tiêu hóa DiLiM đóng gói sẵn (~222 clip/ảnh, 2,5 GB, đi kèm ngay trong thư mục skill) + công cụ tìm, xác minh và chèn vào composition HyperFrames. Dùng skill này BẤT CỨ KHI NÀO người dùng muốn tìm/chèn B-roll, footage minh họa cho video về tiêu hóa, dạ dày, đại tràng, đường ruột, táo bón, tiêu chảy, đầy hơi, trào ngược, lợi khuẩn, men vi sinh, chất xơ, gan nhiễm mỡ, hoặc cho sản phẩm Inulin Fuji FF, Nghệ Mùa Thu Okinawa, sản phẩm Gan; khi đưa transcript/caption và hỏi "chèn hình cho ý này"; khi nói "kho tiêu hóa", "clip đau bụng", "clip bồn cầu", "hình lợi khuẩn"; hoặc khi skill dựng video khác (general-video, talking-head-recut, broll-top, broll-vip, vertical-topband-video) cần B-roll chủ đề tiêu hóa. Cũng dùng để thêm clip mới vào kho và dời kho sang ổ khác.
---

# add-broll-tieu-hoa — B-roll tiêu hóa vào HyperFrames

## B-roll để làm gì (đọc trước mọi luật)

B-roll tồn tại để người xem **hình dung được điều đang nghe**: mỗi ý trong lời nói cần đúng một clip mô tả đúng cảnh đó. Vai trò thứ hai là **giữ nhịp**: vài giây không có gì mới trên màn hình là người xem lướt đi. Hai vai trò kéo ngược nhau (chính xác vs. dày đặc); cách giải quyết là **tìm kỹ hơn, không hạ chuẩn**. Mọi lỗi nghiêm trọng đều đến từ việc chọn clip "cùng chủ đề" thay vì "đúng cảnh" — xem `references/selection-rules.md`.

## Kho nằm ở đâu

Mọi thứ nằm **trong thư mục skill này**, không cần cấu hình:

| Đường dẫn | Nội dung |
|---|---|
| `footage/01-trieu-chung/` | 32 clip + 1 ảnh, người thật: ôm bụng, nhăn mặt, ngồi bồn cầu lâu, rặn, xoa bụng sau ăn, ấn vùng gan |
| `footage/02-co-che-3d/` | 40 clip + 2 ảnh, đồ họa: dạ dày, ruột, đại tràng, nhung mao, lợi/hại khuẩn, trào ngược, gan nhiễm mỡ, mỡ nội tạng, trục não–ruột |
| `footage/03-nguyen-nhan/` | 53 clip: đồ chiên dầu mỡ, fast food, xúc xích, cà phê, bia rượu, thuốc lá, ăn vội/vừa ăn vừa xem điện thoại, ăn khuya, stress văn phòng, uống nhiều thuốc |
| `footage/04-giai-phap/` | 59 clip: rau xanh, chuối, khoai lang, yến mạch, sữa chua, uống nước, ăn salad vui, đi bộ, hít thở, bác sĩ khám/tư vấn, mô hình gan |
| `footage/05-san-pham/` | Inulin Fuji FF (ảnh), Nghệ Mùa Thu Okinawa (video + ảnh + nguyên liệu bột nghệ), Gan (ảnh) — xem `references/san-pham.md` |
| `index/` | `manifest.jsonl` (mô tả từng clip), `concept_graph.json` (ý ↔ clip gợi ý), `sheets/` (contact sheet 12 khung), `thumbs/` |
| `references/catalog.md` | **Danh mục toàn kho** kèm cảnh + mốc đoạn — đọc một lần đầu phiên là nắm cả kho |

`config.json` cho phép dời `footage/` sang ổ khác (sửa `broll_root`, rồi `build_index.py update`). `id` là hash nội dung, đổi tên/dời không mất mô tả. Scripts cần Python 3.10+ và ffmpeg/ffprobe trên PATH, không cần thư viện ngoài.

```bash
python "<skill>/scripts/search.py" "ngồi bồn cầu lâu bấm điện thoại" --topic trieu_chung -n 6
```

## Quy trình A — Chèn B-roll cho một video

### 1. Nắm kho (rẻ, làm đầu mỗi phiên)

Đọc `references/catalog.md` (≈ 250 dòng). Kho nhỏ nên đọc thẳng nhanh hơn search mò, và search chỉ tìm được điều đã biết là có. Nếu người dùng vừa thêm clip: `python scripts/build_index.py update --sheets` rồi `stats` xem clip mới đã mô tả chưa.

### 2. Nhận diện sản phẩm và giọng văn

Đọc transcript. Nếu video nhắc sản phẩm, B-roll sản phẩm **chỉ** lấy từ `05-san-pham/<đúng sản phẩm>` (`--product inulin_fuji|nghe_okinawa|gan`). Vai trò cố định từng sản phẩm (Inulin = "khóa cửa", Nghệ = "bảo vệ gan") và giọng văn A/B: `references/san-pham.md`.

### 3. Tách ý → tưởng tượng cảnh → rồi mới tìm

Với từng câu/cụm (kể cả câu hook mở đầu — kiểm tra **nội dung**, đừng bỏ vì **hình thức** câu hỏi): câu này nêu triệu chứng / cơ chế / nguyên nhân / hành động cụ thể nào? Có → viết **cảnh lý tưởng bằng lời** ("người ngồi trên bồn cầu, gồng người, tay nắm chặt") rồi rút từ khóa từ cảnh đó. Từ khóa y khoa lấy thẳng từ transcript ("dạ dày") dẫn tới clip cùng bộ phận nhưng sai cơ chế.

```bash
python scripts/search.py "<cảnh lý tưởng>" [--topic trieu_chung|co_che|nguyen_nhan|giai_phap|gan|tao_bon|loi_khuan] [--kind real_person|anatomy_3d|lifestyle_scene] [--mood painful|negative|positive|neutral] [--product id] [--exclude-used used.txt] [-n 8]
```

Kết quả kèm `sheet` (contact sheet) và `segments` nếu clip dài. Ứng viên gắn `APPROVED` là cặp ý↔clip đã chốt trong `concept_graph.json` — dùng luôn nếu ý giống ~90%. Bảng "ý thường gặp → clip" cho kịch bản tiêu hóa: `references/y-tuong-canh.md`.

Thứ tự ưu tiên khi nhiều ứng viên: `01-trieu-chung` (người thật) cho ý cảm xúc/sinh hoạt > `02-co-che-3d` cho ý cơ chế > `03`/`04` cho ý nguyên nhân/giải pháp. Đừng quên hai nhóm hay bị bỏ sót khi video kể chuyện: `03-nguyen-nhan` (stress, ăn khuya, thuốc) và `04-giai-phap` (uống nước, đi bộ).

### 4. Xác minh từng clip — bốn câu hỏi

Mở contact sheet (Read ảnh `sheet`) của **nhiều** ứng viên, đừng chọn theo tên. Trả lời đủ bốn:

1. Đúng **cảnh cụ thể** đã tưởng tượng chưa? (không phải "cùng chủ đề")
2. **Biểu cảm/không khí** khớp sắc thái caption chưa?
3. Đã xem frame tại **đúng điểm sẽ render** chưa? Clip dài hơn nhiều so với đoạn cần → chọn `media_start` từ `segments`, rồi:
   ```bash
   python scripts/verify_frame.py <id> --at <media_start> --span <duration>
   ```
4. Điểm chèn trùng **đúng từ được nói** chưa? Cần timestamp cấp **từ**.

Ghi mỗi quyết định vào `plan.json` (schema: `references/schema.md`). Ý quan trọng mà không có clip thật khớp: **để trống** hoặc caption animation. Không tự vẽ sơ đồ/hình minh họa — luật cứng.

### 5. Soát trước khi đặt

- **Không lặp** một clip không-phải-sản-phẩm trong cùng video; ý lặp lại → clip khác cùng nội dung (kho có ≥3 clip cho mỗi ý chính: táo bón, đau bụng, lợi khuẩn, gan, đồ chiên, rau xanh). Clip sản phẩm được miễn. Hai nhịp liền nhau chung file = một đoạn liên tục.
- Danh sách **triệu chứng** dồn dập (mỗi item < 0,5 s): gộp 2 triệu chứng / 1 clip.
- Ẩn dụ lướt qua → bám chủ đề chính; ẩn dụ kéo dài → caption animation (kho không có clip vật thể ẩn dụ).
- Ý cảm xúc → người thật; ý cơ chế → đồ họa 3D. "Hệ vi sinh" → clip vi khuẩn, không phải clip nhung mao.
- Kho 100% clip ngang 16:9; clip có `quality_flags` (watermark, burned_text, low_res, small_subject) chỉ dùng theo ghi chú ở `selection-rules.md` §10.

### 6. Đặt vào HyperFrames

```bash
python scripts/place.py plan.json --project <thư mục composition> [--layout top|vip|full]
```

Script copy đúng các clip đã dùng vào `<project>/assets/broll/<id>.mp4`, sinh `<project>/broll-snippet.html` (các `<video muted playsinline data-start data-duration data-media-start>` trong wrapper bố cục) và **báo lỗi** nếu lặp clip, `media_start + duration` vượt nguồn, hoặc clip dọc. Chèn snippet vào `index.html` bằng Edit — không đặt `<video data-start>` trong phần tử cha cũng có `data-start`. Chi tiết wrapper, lớp z-index, cắt hard/push: `references/hyperframes-placement.md`; thông số dải trên đỉnh / thẻ nổi lấy từ skill `broll-top` / `broll-vip` nếu có.

Sau khi chèn: `hyperframes lint` → render thử → trích frame tại **từng** điểm B-roll mới. Báo cáo trung thực đoạn nào để trống và vì sao.

### 7. Học từ quyết định của người dùng

Người dùng đổi clip hoặc chỉ định "ý này dùng clip này" → ghi lại để thành mặc định cho video sau:

```bash
python scripts/build_index.py approve --concept "táo bón" --path "01-trieu-chung/020 - Ngồi trên bồn cầu, tư thế căng thẳng, hai tay nắm chặt.mp4" --media-start 0 --note "khách chốt 15/09"
```

Chỉ áp cho **lần xuất hiện đầu** của ý trong một video; lần 2, 3 tìm clip khác cùng cảnh và sắc thái.

## Quy trình B — Thêm clip mới vào kho

Bỏ clip vào `footage/06-them-moi/` (hoặc đúng nhóm 01–05), rồi:

```bash
python scripts/build_index.py update --sheets            # probe + contact sheet cho file mới
python scripts/describe_batches.py make --all             # lô clip chưa mô tả -> index/batches/NNN.json
```

Với từng clip trong batch: Read contact sheet, viết mô tả đúng schema `references/describe-prompt.md` (bắt buộc `scene` mở đầu bằng động từ, `subject_type`, `mood`, `segments` nếu clip có nhiều cảnh) vào `index/descriptions/NNN.jsonl`, rồi:

```bash
python scripts/describe_batches.py merge
python scripts/make_catalog.py                            # cập nhật references/catalog.md
```

Tên file vô nghĩa (`IMG_1234.mp4`) không sao — search dựa vào `scene`/`tags`, không dựa vào tên. Clip nào chưa mô tả thì search chỉ thấy qua tên file và bị trừ điểm.

## Tài liệu tham chiếu

| File | Đọc khi |
|---|---|
| `references/catalog.md` | đầu mỗi phiên — toàn bộ kho, cảnh, mốc đoạn |
| `references/selection-rules.md` | trước khi chọn clip — 4 lỗi xác minh kinh điển + luật cứng + clip cần lưu ý |
| `references/y-tuong-canh.md` | bảng ý thường gặp trong kịch bản tiêu hóa → clip gợi ý |
| `references/san-pham.md` | video nhắc Inulin / Nghệ Okinawa / Gan — vai trò, kho hình, giọng văn |
| `references/hyperframes-placement.md` | chèn snippet đúng hợp đồng HyperFrames |
| `references/schema.md` | đọc/ghi `manifest.jsonl`, `plan.json`, `concept_graph.json` |
| `references/describe-prompt.md` | mô tả clip mới (Quy trình B) |
| `references/taxonomy.json` | id cho `--topic`, `--kind`, `--product`; từ đồng nghĩa search |

---
name: add-footage
description: Index, tìm, xác minh và chèn B-roll từ kho footage DiLiM (D:\HYPERFRAME\footage\broll, ~1.600 clip) vào composition HyperFrames; cũng dùng để dọn kho an toàn (bản sao trùng, file rác). Dùng skill này BẤT CỨ KHI NÀO người dùng muốn thêm/chèn/tìm B-roll, footage minh họa, clip sản phẩm hay "hình cho ý này" vào một video HyperFrames; khi đưa transcript/caption và hỏi "chèn footage vào"; khi nói "kho footage", "tìm clip", "clip nào hợp với câu này", "cập nhật index footage", "mô tả clip mới"; hoặc khi một skill dựng video khác (general-video, talking-head-recut, broll-top, broll-vip, vertical-topband-video) cần lấy clip minh họa từ kho. Cũng dùng để build/cập nhật index sau khi thêm footage mới, hoặc đóng gói kho + index đem sang máy khác.
---

# add-footage — B-roll từ kho DiLiM vào HyperFrames

## B-roll để làm gì (đọc trước mọi luật)

B-roll tồn tại để người xem **hình dung được điều đang nghe** — mỗi ý trong lời nói cần đúng một clip mô tả đúng cảnh đó. Vai trò thứ hai là **giữ nhịp**: vài giây không có gì mới trên màn hình là người xem rời đi. Hai vai trò kéo ngược nhau (chính xác vs. dày đặc); cách giải quyết là **tìm kỹ hơn, không hạ chuẩn**. Mọi lỗi nghiêm trọng trong dự án này đều đến từ việc chọn clip "cùng chủ đề" thay vì "đúng cảnh" — xem `references/selection-rules.md` để biết từng lỗi thật.

## Kho nằm ở đâu

Cấu hình đọc từ `D:\HYPERFRAME\footage\config.json` (tạo từ `config.example.json` nếu chưa có):

| Khóa | Mặc định | Ý nghĩa |
|---|---|---|
| `broll_root` | `D:\HYPERFRAME\footage\broll` | Kho clip gốc (~77 GB). Đem sang máy khác chỉ cần sửa dòng này. |
| `index_dir` | `D:\HYPERFRAME\footage\index` | `manifest.jsonl`, `concept_graph.json`, `sheets/`, `thumbs/` |

Mọi đường dẫn trong manifest là **tương đối so với `broll_root`**, và `id` là hash nội dung file — đổi tên/dời thư mục không mất mô tả đã sinh.

Scripts nằm ở `scripts/` của skill này. Chạy từ bất kỳ đâu:

```bash
python "D:/HYPERFRAME/.claude/skills/add-footage/scripts/search.py" "mảng xơ vữa bám thành mạch" --topic mach_mau_than_kinh
```

## Quy trình A — Chèn B-roll cho một video

### 1. Cập nhật index (rẻ, làm đầu mỗi phiên)

```bash
python scripts/build_index.py update
```

Chỉ quét file mới/đổi. Kết quả search rỗng trên index cũ là **mơ hồ** (thật sự không có vs. chưa index) — đã từng kết luận sai "sản phẩm không có footage" vì index cũ 2 ngày. `build_index.py stats` cho biết % clip đã có mô tả; nếu thấp ở đúng chủ đề đang cần, chạy Quy trình B cho chủ đề đó trước.

### 2. Nhận diện sản phẩm và giọng văn

Đọc transcript. Nếu video nhắc tên sản phẩm, B-roll sản phẩm **chỉ** lấy từ `Product Broll/<đúng sản phẩm>` (`--product <id>`), kiểm tra đủ 3 thư mục con `Video/`, `Nguyên Liệu/`, `Ảnh/`. Bảng ghép sản phẩm ↔ kho chủ đề ↔ vai trò từng sản phẩm: `references/product-map.md`.

### 3. Tách ý → tưởng tượng cảnh → rồi mới tìm

Với từng câu/cụm trong transcript (kể cả câu hook mở đầu — kiểm tra **nội dung**, đừng bỏ qua vì **hình thức** câu hỏi), hỏi: câu này nêu triệu chứng / cơ chế / hành động cụ thể nào? Có → viết ra **cảnh lý tưởng bằng lời** ("người quay nghiêng, đầu cúi dần về trước, đang nhìn màn hình") rồi rút từ khóa từ cảnh đó. Từ khóa y khoa lấy thẳng từ transcript ("cột sống cổ") dẫn tới clip cùng bộ phận nhưng sai cơ chế.

```bash
python scripts/search.py "<cảnh lý tưởng>" [--topic id] [--kind real_person|anatomy_3d|...] [--mood negative] [--product id] [--exclude-used used.txt] [-n 8]
```

Search trả về ứng viên kèm `sheet` (contact sheet 12 frame trải đều) và `segments` nếu clip dài. Ứng viên gắn `APPROVED` là cặp ý↔clip người dùng đã duyệt trong `concept_graph.json` — dùng luôn nếu ý giống ~90%, đừng tìm cái khác (người dùng đã chốt nguyên tắc này).

Thứ tự kho theo thói quen thực tế của người dùng: `Đã Chuẩn Hóa` > `Khám bệnh` > `Thể dục thể thao` > `Ngủ- Ngon- mất ngủ` > `Giảm cân` > `Đồ ăn` = `Nhân Viên văn phòng` > ... > `Lộn Xộn Xà bần` cuối cùng. Hai kho hay bị bỏ quên cho ý mệt mỏi/công việc/giấc ngủ: `Nhân Viên văn phòng` và `Ngủ- Ngon- mất ngủ`.

### 4. Xác minh từng clip — bốn câu hỏi

Mở contact sheet (Read ảnh `sheet`) của **nhiều** ứng viên, đừng chọn theo tên. Trả lời đủ bốn:

1. Đúng **cảnh cụ thể** đã tưởng tượng chưa? (không phải "cùng chủ đề")
2. **Biểu cảm/không khí** khớp sắc thái caption chưa? Người ăn salad vui và người ăn salad chán ghét là hai ý trái ngược.
3. Đã xem frame tại **đúng điểm sẽ render** chưa? Clip dài hơn nhiều so với đoạn cần là dấu hiệu nó chứa nhiều cảnh — chọn `media_start` từ `segments`, rồi xác nhận:
   ```bash
   python scripts/verify_frame.py <id> --at <media_start> [--span <duration>]
   ```
   Lệnh này trích frame đầu/giữa/cuối của đoạn sẽ dùng. Từ chối clip chỉ vì frame đầu cũng là lỗi như chấp nhận vì frame đầu.
4. Điểm chèn trùng **đúng từ được nói** chưa? Cần timestamp cấp **từ** (word-level); timestamp cấp câu lệch vài giây.

Ghi mỗi quyết định vào `plan.json` (schema ở `references/schema.md` mục "plan"). Với ý quan trọng mà không có clip thật khớp: **để trống** hoặc dùng caption có animation. Không tự vẽ sơ đồ/hình minh họa — luật cứng người dùng đặt ra.

### 5. Soát trước khi đặt

- **Không lặp** một clip không-phải-sản-phẩm trong cùng video, kể cả khi ý lặp lại — tìm clip khác cùng nội dung. Clip sản phẩm được miễn. Hai nhịp **liền nhau** dùng chung một file là một đoạn liên tục, không tính là lặp.
- Danh sách **triệu chứng** đọc dồn dập (mỗi item < 0.5s): gộp 2 triệu chứng / 1 clip, chỉ minh họa một vế; lượt liệt kê thứ 2 trong video đảo sang vế kia.
- Ẩn dụ lướt qua ("như cỗ máy rỉ sét"): bám chủ đề chính, đừng đuổi theo vế ví von trừ khi cả câu là ẩn dụ.
- Ý mang tính quan hệ/cảm xúc → ưu tiên **người thật** hơn đồ họa 3D. Ý cơ chế sinh học → đồ họa 3D được.
- Kho 95% clip ngang 16:9; clip dọc (`orient: portrait`) hiện **không dùng** cho dải/thẻ B-roll vì cắt mất 2/3 nội dung.

### 6. Đặt vào HyperFrames

```bash
python scripts/place.py plan.json --project <thư mục composition> [--layout top|vip|full]
```

Script copy đúng các clip đã dùng vào `<project>/assets/broll/<id>.mp4`, sinh `<project>/broll-snippet.html` gồm các `<video muted playsinline data-start data-duration data-media-start>` bọc trong wrapper bố cục, và **báo lỗi** nếu: lặp clip không-sản-phẩm, `media_start + duration` vượt độ dài nguồn (cần loop), clip dọc. Chèn snippet vào `index.html` bằng Edit — không đặt `<video data-start>` bên trong một phần tử cha cũng có `data-start` (lint từ chối). Bố cục dải trên đỉnh / thẻ nổi lấy đúng thông số từ skill `broll-top` / `broll-vip`; hợp đồng `<video>` của framework ở `hyperframes-core/references/variables-and-media.md`. Chi tiết wrapper: `references/hyperframes-placement.md`.

Sau khi chèn: `hyperframes lint` → render thử → trích frame kiểm tra tại **từng** điểm B-roll mới, không chỉ vài mẫu. Báo cáo trung thực đoạn nào để trống và vì sao.

### 7. Học từ quyết định của người dùng

Khi người dùng đổi clip hoặc chỉ định "ý này dùng clip này", ghi vào `concept_graph.json`:

```bash
python scripts/build_index.py approve --concept "mất ngủ" --id <id> --media-start 2.0 --note "user chốt 12/09"
python scripts/build_index.py approve --concept "mất ngủ" --path "Đã Chuẩn Hóa/chong-mat-mat-ngu,thieu-ngu,mat-ngu-1.mp4"   # theo đường dẫn cũng được
```

Đây là mặc định thường trực cho mọi video sau — nhưng chỉ cho **lần xuất hiện đầu** của ý trong một video; lần 2, 3 tìm clip khác có nội dung tương tự clip chuẩn. Lần đầu dựng index trên máy mới, chạy `bash scripts/seed_approved.sh` để nạp các clip ưu tiên đã chốt (`selection-rules.md` §10) và 63 cặp từ pipeline cũ.

## Quy trình B — Mô tả clip (làm cho search hiểu được kho)

60% clip trong kho có tên vô nghĩa (`Thiết kế chưa có tên - ...`, `10348332-hd_1080...`) hoặc mô tả bị cắt cụt giữa chừng. Search theo tên chỉ thấy ~40% kho. Bước mô tả là thứ biến kho thành thứ agent đọc hiểu được — không phải việc phụ.

```bash
python scripts/build_index.py update --sheets          # tạo contact sheet cho clip chưa có
python scripts/describe_batches.py make --topic dot_quy --batch-size 20   # hoặc --all
```

Mỗi batch là một file `index/batches/<n>.json` liệt kê `id`, `sheet`, `dur`, tên file, thư mục. Với từng clip: Read contact sheet, viết mô tả đúng schema trong `references/describe-prompt.md` (trường bắt buộc: `scene` bắt đầu bằng **động từ**, `subject_type`, `mood`, `segments` nếu clip > 20s), ghi vào `index/descriptions/<n>.jsonl`, rồi:

```bash
python scripts/describe_batches.py merge
```

Lô lớn (hàng trăm clip) thì chia cho subagent theo batch, mỗi subagent nhận đúng hướng dẫn trong `describe-prompt.md`. Có API key Anthropic thì `describe_batches.py auto` chạy tự động (xem `references/describe-prompt.md` mục API). Kiểm tra chất lượng: search một ý bất kỳ và mở sheet của 3 kết quả đầu — nếu scene không khớp ảnh, mô tả đang bị "đoán theo tên file" thay vì nhìn ảnh.

## Dọn kho an toàn

```bash
python scripts/clean_kho.py --dry-run                                  # mặc định: bản sao trùng, file không phải media, file hỏng
python scripts/clean_kho.py --dry-run --rules dups,junk,broken,long,web_images,badname_lonxon
python scripts/clean_kho.py --apply --rules ...   &&  python scripts/build_index.py update --prune
```

Luôn dry-run trước và đưa tổng số/dung lượng cho người dùng chốt. Script không bao giờ xóa clip đã duyệt (`concept_graph`) hay clip sản phẩm, và ghi log `index/cleanup-*.txt` để khôi phục từ kho gốc. **Đừng xóa theo "tên vô nghĩa" ngoài `Lộn Xộn Xà bần`**: 135 clip tên Canva nằm trong thư mục chủ đề là do người dùng tự phân loại — tên rác nhưng nội dung tốt; cách sạch là mô tả rồi đổi tên theo nội dung (đã dọn 12/09/2026: 1.240 file, 31,8 GB).

## Quy trình C — Đóng gói đem sang máy khác

Skill (< 1 MB) + `index/` (manifest + thumbs + sheets, vài trăm MB) + footage (77 GB, chuyển riêng qua NAS/Drive). Máy nhận: đặt footage ở đâu tùy ý → sửa `broll_root` trong `config.json` → `build_index.py update` — hash trùng thì mô tả cũ tự khớp, chỉ clip mới cần mô tả thêm.

## Tài liệu tham chiếu

| File | Đọc khi |
|---|---|
| `references/selection-rules.md` | trước khi chọn clip cho bất kỳ video nào — 4 lỗi xác minh kinh điển + luật cứng, kèm lỗi thật |
| `references/product-map.md` | video nhắc sản phẩm — thư mục nào, vai trò gì, giọng văn A/B |
| `references/taxonomy.yaml` | cần id chủ đề/loại hình/sản phẩm cho `--topic`, `--kind`, `--product`; từ đồng nghĩa search |
| `references/schema.md` | đọc/ghi `manifest.jsonl`, `plan.json`, `concept_graph.json` |
| `references/describe-prompt.md` | mô tả clip (Quy trình B) |
| `references/hyperframes-placement.md` | wrapper bố cục, lớp, không nest video trong phần tử timed |
| `references/pipeline.md` | dựng cả video: transcript chạy nền, subagent tìm B-roll theo nhóm ý + subagent SFX (skill `add-sfx`) song song, cha soát chéo → bảng duyệt → place |

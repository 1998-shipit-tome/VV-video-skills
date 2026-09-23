---
name: vertical-topband-video
description: Dựng video dọc 9:16 theo format "top-band split" — dải B-roll full-width ghim trên đỉnh khung, A-roll dịch xuống dưới, caption ALL CAPS đè lên đường seam, nhịp beat 2-6s xen breather A-roll sạch. Kèm script render ffmpeg từ file kế hoạch JSON, 6 style caption và bộ kiểm tra nhịp. Dùng skill này BẤT CỨ KHI NÀO người dùng muốn dựng hoặc edit video dọc cho TikTok/Reels/Shorts có chèn B-roll và chữ, đưa file A-roll người nói kèm kho footage minh họa, hỏi cách chèn B-roll mà không che mặt, hỏi về tỉ lệ dải B-roll / vị trí caption / nhịp cắt / mật độ B-roll, nhờ tái tạo phong cách một video mẫu đã phân tích, gặp lỗi chữ tiếng Việt mất dấu khi burn caption, hoặc nhắc tới "dải B-roll trên đỉnh", "split dọc", "caption đè seam", "video bán hàng dọc" — kể cả khi họ chỉ nói ngắn gọn "dựng video này theo style cũ" hoặc dán một đường dẫn .mp4 kèm thư mục footage mà không giải thích gì thêm.
---

# Video dọc format top-band split

## Format này là gì

Một layout duy nhất, dùng xuyên suốt video, thay vì cắt qua lại giữa A-roll và B-roll toàn khung:

```
y = 0%      ┌──────────────────────────┐
            │ [logo]                   │  watermark, luôn nằm trên cùng
            │    DẢI B-ROLL            │  full width, cạnh dưới CẮT THẲNG
            │    (Ken Burns push-in)   │  không bo góc / viền / đổ bóng
y ≈ 38%     ├──────────────────────────┤  ← đường seam
            │    CAPTION đè lên seam   │  ALL CAPS, 1-2 dòng, căn giữa
            │                          │
            │    A-ROLL (người nói)    │  scale 1.00, dịch xuống 12.5%
y = 100%    └──────────────────────────┘
```

Ba đặc tính làm nên format, và lý do từng cái tồn tại:

**A-roll không bao giờ đổi scale.** Nó chỉ dịch xuống 12.5% chiều cao khung (~240px trên 1920) khi dải bật lên, và dịch tức thì trong 1 frame — không ease. Người nói đứng yên tuyệt đối chính là điểm neo thị giác; nhờ nó mà dải trên có thể thay clip liên tục mà người xem không chóng mặt. Nếu bạn thêm zoom punch-in vào A-roll "cho sinh động", bạn phá đúng thứ đang giữ video ổn định.

**Caption đè lên đường seam, không nằm lower third.** Vị trí này bắc cầu giữa hai lớp hình, khiến mắt đọc chữ mà vẫn thấy cả B-roll lẫn mặt người nói trong một tầm nhìn. Nó cũng tránh hoàn toàn vùng UI của TikTok/Reels ở đáy khung.

**Chuyển động ở mọi lớp trừ A-roll.** Dải có Ken Burns, chữ có animation, footage 3D tự chuyển động. Khung hình không bao giờ chết, nhưng cũng không bao giờ rung.

## Quy trình

### Bước 1 — Đo nguyên liệu
Lấy duration, fps, kích thước của A-roll. Transcribe với **word-level timestamps** — timestamp cấp câu lệch vài giây, không canh được điểm chèn. Nếu đã có transcript cache cho file này thì dùng lại, đừng transcribe lại.

### Bước 2 — Cắt beat theo mệnh đề nói
Một beat = một mệnh đề người nói thốt ra, thường 2-6 giây. Bám ranh giới câu **thật** trong transcript, đừng gộp các ý cách xa nhau chỉ vì cùng chủ đề — gộp lại là tự đánh mất điểm chèn B-roll.

Danh sách liệt kê dồn dập phải tách mỗi item thành một beat riêng. "Đau đầu, vai gáy, chóng mặt, mất ngủ, tê bì" không phải một ý — đó là năm ý, năm beat, năm clip khác nhau, mỗi cái ~2s để tạo cảm giác dồn dập.

### Bước 3 — Chừa breather
Cứ khoảng 12-15 giây phải có một nhịp A-roll sạch: không dải, không chữ. Đây không phải chỗ trống vì lười — nó là dấu chấm câu. Mắt cần nghỉ, và khoảng lặng làm đoạn tiếp theo nổi lên.

Đặt một breather dài hơn (4-5s) đúng chỗ kịch bản chuyển đoạn lớn — ví dụ từ "vấn đề" sang "giải pháp". Nó vừa nghỉ mắt vừa báo hiệu cấu trúc.

Trong `plan.json`, breather đơn giản là **khoảng trống giữa hai beat**. Script tự lấp bằng A-roll sạch.

### Bước 4 — Chọn B-roll và viết caption
Chọn clip là phần khó nhất và nằm ngoài phạm vi skill này. Nếu đang làm cho DiLiM Supplement, đọc skill `dilim-video-broll` — nó có bảng sản phẩm, luật chọn clip, và danh sách lỗi thật đã gặp. Nguyên tắc chung áp dụng cho mọi brand:

- Tưởng tượng cảnh lý tưởng **trước**, rồi mới đi tìm. Tìm bằng từ khóa lấy thẳng từ transcript sẽ ra clip cùng chủ đề nhưng sai nội dung.
- Câu ẩn dụ thì minh họa **cái được ví von**, không phải nội dung kỹ thuật. Nói "quét sơn chống rỉ sét" thì chèn thanh sắt rỉ thật.
- Không tìm được clip khớp thật thì **để trống dải, giữ caption**. Đừng hạ chuẩn để lấp chỗ, và đừng tự vẽ đồ họa thay thế.

Caption **không phải phụ đề**. Nó là title card theo beat — chỉ hiện ở câu đáng nhớ, và nhiều đoạn dài hoàn toàn không có chữ. Trong video mẫu có đoạn gần 10 giây im chữ để phần ẩn dụ hình ảnh tự nói. Mỗi dòng 4-7 từ, tối đa 2 dòng.

Chi tiết 6 style caption, ý nghĩa màu, và cách chọn style theo giai đoạn kịch bản: `references/caption-styles.md`.

### Bước 5 — Viết plan.json và lint
Xem schema bên dưới. Chạy kiểm tra nhịp trước khi render — nó rẻ hơn nhiều so với render xong mới phát hiện sai:

```bash
python scripts/build.py plan.json --lint-only
```

Lint bắt: beat quá ngắn/dài, beat chồng nhau, mật độ B-roll lệch mục tiêu, và đoạn dài không có breather. Nó cảnh báo chứ không chặn — bạn có thể cố tình lệch chuẩn nếu có lý do, nhưng hãy biết mình đang lệch.

### Bước 6 — Render
```bash
python scripts/build.py plan.json -o preview.mp4 --preview   # nửa độ phân giải, nhanh, để duyệt nhịp
python scripts/build.py plan.json -o final.mp4               # bản thật
```

Luôn duyệt `--preview` trước. Nhịp và vị trí chữ nhìn ở nửa độ phân giải là đủ, và nó nhanh hơn nhiều lần.

### Bước 7 — Kiểm tra bằng frame thật
Sau khi render, trích frame tại **từng** điểm chèn mới, không chỉ vài mẫu, và thực sự xem từng frame:

```bash
ffmpeg -y -ss 12.4 -i final.mp4 -frames:v 1 check_12.4.png
```

Bốn thứ phải xác nhận ở mỗi điểm: clip có đúng cảnh đã hình dung không, chữ có bị tràn hoặc mất dấu không, dải có che mặt người nói không, và điểm chèn có trùng đúng từ được nói không.

Báo cáo trung thực: chỉ rõ đoạn nào để trống và vì sao.

## plan.json

```json
{
  "aroll": "aroll.mp4",
  "output": "final.mp4",
  "preset": "dilim",
  "brand": { "logo": { "src": "logo.png" } },

  "beats": [
    {
      "start": 0.0,
      "end": 2.6,
      "broll": {
        "src": "footage/that-nghiep.mp4",
        "in": 3.5,
        "kenburns": 1.13,
        "in_transition": "cut",
        "out_transition": "cut"
      },
      "caption": {
        "style": "hook",
        "lines": ["MẤT VIỆC RỒI TÌM LẠI"],
        "anim": "pop"
      }
    },
    { "start": 2.6, "end": 6.0, "broll": { "src": "footage/nao-3d.mp4", "in": 0 },
      "caption": {
        "style": "quote",
        "lines": ["TẾ BÀO NÃO ĐÃ BỊ TỔN THƯƠNG", "THÌ KHÔNG PHỤC HỒI ĐƯỢC"],
        "attribution": "DILIM SUPPLEMENT"
      } }
  ],

  "endcard": {
    "lines": ["SẢN PHẨM NÀY", "KHÔNG PHẢI LÀ THUỐC"],
    "duration": 4.0
  }
}
```

**Trường bắt buộc:** `aroll`, `beats`. Mọi thứ khác có mặc định.

**Đường dẫn** tính tương đối theo vị trí file `plan.json`.

**Khoảng trống giữa các beat** = breather A-roll sạch. Không cần khai báo.

**`broll` hoặc `caption` có thể bỏ trống** — một beat chỉ có chữ (dải trống) hoặc chỉ có dải (không chữ) đều hợp lệ và đều dùng thật trong video mẫu.

| Trường | Giá trị | Ghi chú |
|---|---|---|
| `broll.in` | giây | Điểm vào trong file nguồn. Một file dài nhiều cảnh nên cắt thành nhiều đoạn nhỏ dùng ở nhiều chỗ khác nhau. |
| `broll.kenburns` | 1.0-1.6 | Zoom cuối. 1.0 = tĩnh. Mặc định 1.13 (~+6%/giây). |
| `broll.in_transition` | `cut` `dissolve` `slide_left` | |
| `broll.out_transition` | `cut` `slide_up` | |
| `caption.style` | `hook` `quote` `plate_red` `edu` `keyword` `cta` | Xem `references/caption-styles.md` |
| `caption.lines` | mảng chuỗi, hoặc `{"text":…, "color":…}` | Tối đa 2 dòng |
| `caption.anim` | `typewriter` `wipe` `whip` `pop` | Mặc định theo style |
| `caption.offset` | giây | Trễ so với đầu beat |
| `caption.dur` | giây | Mặc định giữ hết beat |

## Đổi sang brand khác

Toàn bộ màu, font, hình học, style nằm trong `presets/dilim.json`. Copy nó thành preset mới, sửa giá trị, rồi trỏ `"preset": "ten-moi"` hoặc đè cục bộ bằng khối `"brand"` trong plan. **Không sửa `build.py`** — script không chứa giá trị brand nào.

Muốn đổi nhanh một vài thứ cho riêng một video thì dùng `brand`, nó merge đè lên preset:

```json
"brand": { "colors": { "red": "#C81E1E" }, "layout": { "band_height_ratio": 0.34 } }
```

## Font tiếng Việt — bẫy phải biết trước

**Bebas Neue và Impact THIẾU dấu tiếng Việt.** Chúng có đúng cái look condensed đậm mà format này cần, nên rất hay bị chọn, và kết quả là "TẾ BÀO" ra "T? BÀO" hoặc ô vuông. Lỗi này chỉ lộ ra khi đã render xong.

Font đã kiểm chứng đủ 52/52 ký tự dấu khó (Ế Ồ Ứ Ữ Ợ Ẫ...): **Anton** (mặc định, đúng look nhất), Be Vietnam Pro Black, Montserrat Black, iCiel Koni Black.

Kiểm tra một font trước khi dùng:
```bash
python scripts/check_font.py "C:/Windows/Fonts/YourFont.ttf"
```

## Khi nào nên phá luật

Mọi con số trong preset là giá trị đo được từ một video đã chạy tốt, không phải chân lý. Vài trường hợp nên lệch:

- **Nội dung là màn hình / văn bản** (demo app, biểu đồ): nâng `band_height_ratio` lên 0.5-0.6 để hình đọc được, chấp nhận A-roll nhỏ lại.
- **Video ngắn dưới 30 giây**: bỏ breather. Không đủ thời gian để mắt mỏi, và mỗi giây trống là một giây mất người xem.
- **Người nói dùng tay nhiều**: hạ `aroll_translate_ratio` để tay không bị dải cắt mất.
- **Đoạn ẩn dụ hình ảnh**: bỏ hẳn caption. Hình mạnh hơn chữ, và chữ ở đây chỉ làm loãng.

Điều duy nhất không nên đổi là A-roll giữ scale cố định. Đó là thứ giữ cả format đứng vững.

## File tham chiếu

- `references/caption-styles.md` — 6 style caption, hệ màu theo ý nghĩa, animation nào hợp style nào, cách viết chữ cho từng giai đoạn kịch bản. Đọc ở bước 4.
- `references/layout-spec.md` — toàn bộ số đo hình học, dải giá trị quan sát được, và cách script dựng filtergraph. Đọc khi cần chỉnh preset hoặc gỡ lỗi hình.
- `references/rhythm.md` — nhịp beat, quy tắc breather, cấu trúc kịch bản 12 đoạn của video mẫu. Đọc ở bước 2 và 3.
- `references/troubleshooting.md` — lỗi render thường gặp và nguyên nhân gốc. Đọc khi ffmpeg báo lỗi hoặc output sai.
- `references/plan-example.json` — plan mẫu đầy đủ, chú thích từng beat vì sao đặt như vậy (kể cả breather và đoạn cố tình bỏ caption). Copy ra rồi sửa.
- `presets/dilim.json` — preset mặc định, có chú thích từng nhóm giá trị.

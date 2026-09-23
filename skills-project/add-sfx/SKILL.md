---
name: add-sfx
description: Index, tìm và chèn sound effect (SFX) từ kho âm thanh DiLiM (D:\HYPERFRAME\footage\sfx ~1.300 file + thư viện 9.000 file index tại chỗ) vào composition HyperFrames. Dùng skill này BẤT CỨ KHI NÀO người dùng muốn thêm tiếng động, hiệu ứng âm thanh, whoosh, ding, pop, tiếng "bụp" khi chữ hiện, tiếng chuyển cảnh, tiếng cười/vỗ tay, riser hồi hộp, cash/ka-ching cho video; khi nói "kho SFX", "tìm tiếng", "âm thanh cho caption này", "cập nhật index sfx"; hoặc khi skill dựng video khác (add-footage, broll-top, broll-vip, general-video, talking-head-recut) cần âm thanh nhấn cho caption/B-roll. Không dùng cho nhạc nền dài (BGM) hay mix/ducking — đó là media-use và hyperframes-audio.
---

# add-sfx — sound effect từ kho DiLiM vào HyperFrames

## SFX để làm gì trong video DiLiM

SFX là **dấu chấm câu bằng âm thanh**: nó báo cho tai người xem "có thứ mới vừa xuất hiện" — một caption bật lên, một B-roll đẩy vào, một con số nhảy, một ý sai/đúng. Nó không phải nhạc nền và không phải trang trí đều đặn: mỗi tiếng phải gắn với một **sự kiện hình ảnh** cụ thể tại một **thời điểm** cụ thể. Video bán hàng DiLiM có A-roll lời nói liên tục, nên SFX luôn nằm **dưới** giọng (mức trộn 0,10–0,25) và ngắn (0,1–1,5 s); tiếng nào dài hơn 3 s gần như chắc chắn là nhạc/ambience, không phải SFX nhấn. Luật chi tiết + lỗi thật: `references/sfx-rules.md`.

## Kho nằm ở đâu

Cấu hình `D:\HYPERFRAME\footage\sfx-config.json` (tạo từ `config.example.json`):

| Khóa | Mặc định | Ý nghĩa |
|---|---|---|
| `sfx_roots` | 7 kho trong `D:\HYPERFRAME\footage\sfx\<tên>` + `library` = `D:\DiLi Media\Data\Library\Music\Sound Effect` (index tại chỗ, 21 GB) | Mỗi root có `name` và `path`; `rel_path` trong manifest = `<name>/<đường dẫn con>` |
| `index_dir` | `D:\HYPERFRAME\footage\sfx-index` | `manifest.jsonl`, `favorites.json` |

`id` là hash nội dung → đổi tên/dời file không mất nhãn. Scripts ở `scripts/` của skill; chạy từ bất kỳ đâu.

## Quy trình A — Chèn SFX cho một video

### 1. Cập nhật index (đầu phiên)

```bash
python scripts/build_sfx_index.py update            # chỉ file mới/đổi; probe + đo peak/lead-silence
python scripts/build_sfx_index.py stats
```

### 2. Liệt kê SỰ KIỆN trước, tìm tiếng sau

Đi qua `plan.json` của B-roll/caption (hoặc transcript có timestamp từng từ) và ghi ra danh sách sự kiện: `{t, loại, mô tả}` — caption hiện, B-roll cắt/push, item liệt kê, số liệu, ý đúng/sai, hook, CTA. **Không phải sự kiện nào cũng cần tiếng** — chọn theo `sfx-rules.md` mục "mật độ": trung bình 1 tiếng / 3–5 s, dồn ở liệt kê và chuyển đoạn, thưa ở đoạn giải thích.

### 3. Tìm theo loại + sắc thái

```bash
python scripts/search_sfx.py "whoosh ngắn cho b-roll đẩy vào" --cat whoosh --max-dur 1.0
python scripts/search_sfx.py "ding đúng tích cực" --cat ding
python scripts/search_sfx.py "sai buzzer" --cat buzzer -n 5
python scripts/search_sfx.py "hồi hộp riser trước khi lộ giá" --cat riser --min-dur 1.5 --max-dur 4
```

Kết quả in `dur`, `peak_db`, `lead_s` (khoảng lặng đầu file), `cat`, `root`. Ưu tiên: `favorites` (đã dùng và người dùng duyệt) > kho `sound-effect` (đã phân theo cảm xúc tiếng Việt: BẤT NGỜ, HỒI HỘP, QUÊ XỆ, LỰA CHỌN ĐÚNG/SAI…) > `sfx-pack` (whoosh/riser/UI chuẩn) > `nitrozme` (click/transition) > `library` (9.000 file, tìm khi các kho trên không có).

Không nghe được file thì chọn theo **tên + thời lượng + peak + thư mục cảm xúc**; với tiếng quan trọng (hook, CTA) chọn 2–3 ứng viên và ghi cả vào bảng duyệt để người dùng nghe chọn.

### 4. Ghi plan và đặt vào HyperFrames

`sfx-plan.json` (schema ở `references/schema.md`): mỗi item `{id, hit, volume, event}` — `hit` là **thời điểm sự kiện hình ảnh** (giây trên timeline), không phải thời điểm bắt đầu file. `place_sfx.py` tự trừ `lead_s` để tiếng nổ đúng lúc chữ hiện (lỗi cũ: tiếng chậm hơn chữ vài frame vì file có khoảng lặng đầu).

```bash
python scripts/place_sfx.py sfx-plan.json --project <thư mục composition> [--track 20] [--peak -6]
```

Script chuẩn hóa mỗi file về WAV 48 kHz peak −6 dBFS vào `<project>/assets/sfx/<id>.wav`, sinh `<project>/sfx-snippet.html` gồm các `<audio src data-start data-duration data-track-index data-volume>` và **báo**: hai tiếng chồng nhau < 0,15 s, cùng một SFX lặp > 3 lần liên tiếp, tiếng dài > 3 s ở vị trí nhấn. Chèn snippet vào `index.html` ở cấp con của `#root` (audio không cần wrapper, không đặt trong phần tử có `data-start`). Fade/duck/EQ nếu cần → skill `hyperframes-audio`. Hợp đồng `<audio>`: `hyperframes-core/references/variables-and-media.md`.

### 5. Sau khi chèn

`hyperframes lint` → render bản preview có tiếng → nghe (hoặc đưa người dùng nghe) đúng các mốc đã đặt. Người dùng chốt tiếng nào cho loại sự kiện nào → `build_sfx_index.py favorite --event "caption hiện" --id <id>` để lần sau dùng lại (nhất quán giữa các video cùng series là điểm cộng, không phải lặp).

## Quy trình B — Thêm kho SFX mới

Thêm `{name, path}` vào `sfx_roots` → `update`. Kho mới tên file vô nghĩa (`SFX_001.wav`) thì `category` sẽ là `misc`; gắn nhãn thủ công bằng `build_sfx_index.py tag --id <id> --cat whoosh --tags "ngắn, sáng"` sau khi nghe. Sửa từ khóa trong `taxonomy-sfx.yaml` xong chạy `build_sfx_index.py recat` (phân loại lại, không probe, giữ nhãn tay).

## Tài liệu tham chiếu

| File | Đọc khi |
|---|---|
| `references/sfx-rules.md` | trước khi đặt SFX cho bất kỳ video nào — mật độ, mức trộn, căn thời điểm, lỗi thật |
| `references/taxonomy-sfx.yaml` | id category cho `--cat`, từ đồng nghĩa VN↔EN, nhãn cảm xúc theo thư mục |
| `references/schema.md` | `manifest.jsonl`, `sfx-plan.json`, `favorites.json` |
| `references/hyperframes-audio-placement.md` | `<audio>` trong HyperFrames, track, volume, khi nào sang `hyperframes-audio` |

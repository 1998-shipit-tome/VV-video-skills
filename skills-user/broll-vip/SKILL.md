---
name: broll-vip
description: Dựng video dọc 9:16 cho DiLiM Supplement theo bố cục "Broll Vip" — thẻ B-roll 918×516 nổi ở nửa dưới khung, bo góc 40px kèm viền trắng 11px, chuyển cảnh push cả viền sang trái, caption nằm phía trên thẻ và không đè lên. Dùng skill này khi người dùng nói "Broll Vip", "thẻ nổi", "bo góc viền trắng", "kiểu mới", "giống Video 10", hoặc đưa A-roll kèm yêu cầu dựng theo bố cục thẻ nổi nửa dưới. Cũng dùng khi người dùng chỉ nói ngắn gọn "dựng video này" / dán đường dẫn .mp4 kèm tên sản phẩm DiLiM (Nano Sụn, Gluchongel, Rich Coenzyme Q10, Raydel Policosanol, Ellagic Acid, Inulin Fuji FF, Nghệ Mùa Thu Okinawa, Nano Nattokinase, Hàu Nano Gold, DHA+EPA+SQ) — khi đó HỎI bố cục trước, đừng tự chọn.
---

# Broll Vip — thẻ nổi bo góc ở nửa dưới

## Bố cục này trông thế nào

Thẻ hình chữ nhật bo góc, có viền trắng, nổi ở nửa dưới khung. Che thân và tay người nói, chừa trọn phần đầu và vai. Caption nằm **phía trên** thẻ.

| | |
|---|---|
| Kích thước thẻ | **918 × 516** tại (81, 1056) |
| Tỉ lệ | 85% bề ngang khung, đúng 16:9, mép trên ở 55% chiều cao |
| Bo góc | **40 px** |
| Viền | **11 px** trắng |
| Chuyển cảnh | **push sang trái**, 12 frame, khe hở 36 px — dùng cho **cả** lúc thẻ xuất hiện lần đầu |
| Caption | neo **mép dưới**, y = 1036, chữ mọc **lên trên** |
| Đã dùng cho | Video 10 |

Ba điểm dễ làm sai, cả ba đều đã giao nhầm một lần:

**Viền phải trùng biên ngoài với mặt nạ.** Vẽ mặt nạ trên `[0,0,W,H]` còn viền trên `[B/2,...]` cho ra hai đường cong khác nhau, B-roll thò ra ngoài mép trắng ở góc bo. Vòng viền = chữ nhật bo ngoài **trừ** chữ nhật bo trong, vẽ ở 4× rồi thu nhỏ.

**Không `overlay` lên nền trong suốt.** Màu sẽ bị nhân với alpha làm thẻ tối hẳn — đo được 31 so với 125 của clip gốc. Thứ tự bắt buộc: cắt thẻ (còn đục) → phủ viền lên nền đục → bỏ góc → `pad` vào khung.

**Caption neo mép dưới, không neo mép trên.** Neo mép trên thì caption 2 dòng sẽ tràn xuống đè lên thẻ. `qc.py` phép kiểm số 7 bắt lỗi này.

Sơ đồ con số là **ước lượng từ ảnh chụp màn hình của người dùng**. Hỏi lại trước khi dùng cho video quan trọng.

## Chạy

```bash
python "C:/Users/Admin/.claude/skills/broll-vip/scripts/render.py" plan.json "aroll.mp4" --style vip --out-dir "D:/xuat" --name TenVideo
```

```bash
python "C:/Users/Admin/.claude/skills/broll-vip/scripts/qc.py" plan.json "aroll.mp4" --style vip --out-dir "D:/xuat" --name TenVideo
```

`--style vip` là bắt buộc và **không được đổi** trong skill này. Muốn dải ngang ghim trên đỉnh thì đó là skill `broll-top`, không phải chỉnh cờ ở đây.

Mọi con số bố cục nằm ở `scripts/preset.json` mục `layouts.vip`. Sửa file đó, không sửa code.

### File xuất ra

| | |
|---|---|
| `<tên>_broll.mp4` | A-roll + B-roll burn sẵn, có tiếng — bản preview để duyệt |
| `<tên>_caption.mov` | chỉ chữ, nền trong suốt, ProRes 4444 |

Cờ thêm: `--overlay` xuất `<tên>_broll_overlay.mov` (lớp B-roll riêng, alpha thật, rất nặng — video 6 phút khoảng 12.8 GB) · `--card-only` / `--caption-only` dựng lại một lớp khi lỗi chỉ ảnh hưởng lớp đó.

### plan.json

```json
{"idx": 1, "t": 0.0, "t_end": 2.6,
 "d1": "ĐANG BỊ *MỠ MÁU CAO*", "d2": "",
 "variant": "warning", "path": "D:\...\clip.mp4", "src_start": 1.0, "note": ""}
```

`variant`: `warning` · `positive` · `product` · `cta` · `highlight`. Bọc `*từ khóa*` để đổi màu nhấn.

## Quy trình, luật chọn clip, màu caption

Đọc `references/quy-trinh.md` — 6 bước từ chuẩn bị tới kiểm tra, dùng chung với bố cục Top. Trong đó có luật bảng duyệt và luật render thử.

Chi tiết theo chủ đề:

- `references/broll-rules.md` — toàn bộ luật chọn B-roll kèm lỗi thật đã gặp. Đọc khi bắt đầu chọn clip.
- `references/product-map.md` — bảng sản phẩm ↔ thư mục, hai giọng văn kịch bản A/B. Đọc ở bước 1.
- `references/caption-style.md` — hệ màu, markup, vị trí, animation. Đọc ở bước 2 và 5.
- `references/technical.md` — codec, alpha, các bug kỹ thuật. Mục 6h có thông số đầy đủ cả hai bố cục. Đọc ở bước 6.

## Cấu trúc gói

`scripts/` và `references/` là **symlink tới lõi dùng chung** `.claude/skills/_broll-core/` mà skill `broll-top` cũng trỏ vào. Sửa một luật là cả hai bố cục cùng đổi — cố ý như vậy. Đừng chép file ra thành bản riêng.

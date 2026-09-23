---
name: broll-top
description: Dựng video dọc 9:16 cho DiLiM Supplement theo bố cục "Broll Top" — dải B-roll 1080×608 ghim sát mép trên khung, tràn hết bề ngang, cắt thẳng không chuyển cảnh, caption nằm ngay dưới dải. Dùng skill này khi người dùng nói "Broll Top", "dải trên", "dải B-roll trên đỉnh", "kiểu cũ", "giống loạt Raydel", hoặc đưa A-roll kèm yêu cầu dựng theo bố cục dải ngang trên đầu. Cũng dùng khi người dùng chỉ nói ngắn gọn "dựng video này" / dán đường dẫn .mp4 kèm tên sản phẩm DiLiM (Nano Sụn, Gluchongel, Rich Coenzyme Q10, Raydel Policosanol, Ellagic Acid, Inulin Fuji FF, Nghệ Mùa Thu Okinawa, Nano Nattokinase, Hàu Nano Gold, DHA+EPA+SQ) — khi đó HỎI bố cục trước, đừng tự chọn.
---

# Broll Top — dải B-roll ghim trên đỉnh

## Bố cục này trông thế nào

Dải hình chữ nhật tràn hết bề ngang, dán sát mép trên khung. Người nói bị che phần nền phía trên đầu, mặt vẫn thấy đủ. Caption nằm ngay bên dưới mép dải.

| | |
|---|---|
| Kích thước dải | **1080 × 608** tại (0, 0) |
| Vì sao 608 | đúng 16:9 ở bề ngang 1080 — nguồn 16:9 vừa khít, không mất pixel bề ngang nào |
| Bo góc / viền | **không** — mép cắt thẳng |
| Chuyển cảnh | **cắt thẳng**, không animation |
| Caption | neo **tâm**, y = 618, nằm **dưới** dải |
| Đã dùng cho | 8 video Raydel V2–V9 |

Caption neo theo tâm chứ không theo mép trên: caption 1 dòng phải nằm giữa vùng của caption 2 dòng. Neo mép trên làm chữ 1 dòng bị cao hơn 55px — lỗi này đã giao nhầm một lần.

## Chạy

```bash
python "C:/Users/Admin/.claude/skills/broll-top/scripts/render.py" plan.json "aroll.mp4" --style top --out-dir "D:/xuat" --name TenVideo
```

```bash
python "C:/Users/Admin/.claude/skills/broll-top/scripts/qc.py" plan.json "aroll.mp4" --style top --out-dir "D:/xuat" --name TenVideo
```

`--style top` là bắt buộc và **không được đổi** trong skill này. Muốn thẻ nổi bo góc thì đó là skill `broll-vip`, không phải chỉnh cờ ở đây.

Mọi con số bố cục nằm ở `scripts/preset.json` mục `layouts.top`. Sửa file đó, không sửa code.

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

Đọc `references/quy-trinh.md` — 6 bước từ chuẩn bị tới kiểm tra, dùng chung với bố cục Vip. Trong đó có luật bảng duyệt và luật render thử.

Chi tiết theo chủ đề:

- `references/broll-rules.md` — toàn bộ luật chọn B-roll kèm lỗi thật đã gặp. Đọc khi bắt đầu chọn clip.
- `references/product-map.md` — bảng sản phẩm ↔ thư mục, hai giọng văn kịch bản A/B. Đọc ở bước 1.
- `references/caption-style.md` — hệ màu, markup, vị trí, animation. Đọc ở bước 2 và 5.
- `references/technical.md` — codec, alpha, các bug kỹ thuật. Mục 6h có thông số đầy đủ cả hai bố cục. Đọc ở bước 6.

## Cấu trúc gói

`scripts/` và `references/` là **symlink tới lõi dùng chung** `.claude/skills/_broll-core/` mà skill `broll-vip` cũng trỏ vào. Sửa một luật là cả hai bố cục cùng đổi — cố ý như vậy. Đừng chép file ra thành bản riêng.

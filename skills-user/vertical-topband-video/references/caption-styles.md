# 6 style caption

Đọc file này ở bước 4 (viết caption) và bất cứ khi nào phân vân chọn style nào.

## Quy tắc chung cho mọi style

Tất cả caption trong format này đều: **ALL CAPS**, font sans đậm condensed, **căn giữa**, **1-2 dòng, 4-7 từ mỗi dòng**, và **neo đáy khối chữ vào đường seam** (`baseline_ratio` ≈ 0.385).

Vị trí này là đặc điểm nhận dạng của format. Đừng hạ caption xuống lower third — ở đó nó rời khỏi dải B-roll, mất tác dụng bắc cầu giữa hai lớp hình, và chui vào vùng UI của TikTok/Reels.

**Không bao giờ highlight từng từ kiểu karaoke.** Nhấn mạnh đi theo **dòng** hoặc theo **card**. Đây không phải giới hạn kỹ thuật mà là lựa chọn thiết kế: khi mỗi từ đổi màu, mắt bị kéo theo chuyển động thay vì đọc ý; khi cả dòng một màu, người xem nắm được mệnh đề trong một lần liếc.

## Bảng chọn nhanh

| Style | Hình thức | Dùng cho | Tần suất |
|---|---|---|---|
| `hook` | Chữ vàng kim, viền đen dày, không nền | 2-3 dòng mở đầu, câu móc | Chỉ đầu video |
| `quote` | Hộp navy, chữ trắng, ngoặc kép magenta + attribution | Câu title / luận điểm trung tâm | **Đúng 1 lần** |
| `plate_red` | Hộp đỏ viền trắng mảnh, chữ trắng | Triệu chứng, cảnh báo, rủi ro, hậu quả | Cả đoạn "vấn đề" |
| `edu` | Không nền, dòng 1 trắng / dòng 2 vàng, viền đen | Giải thích cơ chế, lợi ích | Cả đoạn "giải pháp" |
| `keyword` | Một từ, cam viền trắng dày, cỡ lớn hơn 22% | Tên hoạt chất, từ khoá phải nhớ | 1-2 lần, giữ 5-6s |
| `cta` | Hộp đặc xanh lá / đỏ, chữ trắng | Kêu gọi hành động | Cuối video, lặp 2 lần |

## Màu mang nghĩa, không xoay ngẫu nhiên

- **Đỏ** → tiêu cực: triệu chứng, cảnh báo, rủi ro, hậu quả.
- **Vàng / cam** → điều cần nhớ: lợi ích, con số ấn tượng, tên hoạt chất.
- **Trắng** → câu khẳng định trung tính, nền tảng của mệnh đề.
- **Xanh lá** → tích cực và brand: kết quả tốt, CTA.
- **Navy + magenta** → riêng card trích dẫn.

Hệ quả quan trọng: người xem đọc được "đang ở đoạn nào của kịch bản" chỉ qua màu chữ, trước cả khi kịp đọc nội dung. Nếu bạn gán màu tuỳ hứng, bạn ném đi một kênh thông tin miễn phí.

Gán màu rõ ràng cho **mọi** caption. Để rơi vào mặc định là cách sinh ra chữ vàng trên nền trắng không đọc được.

## Animation

| Anim | Mô tả | Hợp với |
|---|---|---|
| `typewriter` | Wipe trái→phải theo ký tự, mép phải cứng, ~0.45s | `edu` — chữ chạy theo lời nói |
| `wipe` | Hộp vẽ ra trước, chữ hiện sau ~0.35s | Mọi style có nền (`quote`, `plate_red`, `cta`) |
| `whip` | Bay vào từ ngoài khung trái, xoay −20°→0°, có motion blur | Câu chuyển đoạn cần cú hích |
| `pop` | Scale 0.85 → 1.20 → 1.00, ease-out-back ~0.45s | `hook`, `keyword` — từ đơn cần bật ra |

Hai dòng trong cùng một caption vào **so le ~2 frame**, dòng trên trước. Script tự làm; không cần khai báo.

## Chi tiết từng style

### `hook`
Video mẫu dùng fill gradient vàng→cam. ASS không vẽ được gradient nên script dùng vàng kim đặc (`#FFC400`) — khác biệt rất khó nhận ra ở tốc độ xem thật. Nếu thật sự cần gradient, render chữ thành PNG có alpha rồi overlay như một lớp riêng.

Viền đen dày (8px ở 1080 rộng) không phải trang trí: hook nằm trên B-roll chưa biết trước sáng hay tối, viền là thứ duy nhất đảm bảo đọc được trong mọi trường hợp.

### `quote`
Dùng đúng một lần cho câu title. Sức mạnh của nó đến từ sự khác biệt — nếu xuất hiện lần hai, nó thành một style caption bình thường và câu title mất trọng lượng.

```json
{ "style": "quote",
  "lines": ["TẾ BÀO NÃO ĐÃ BỊ TỔN THƯƠNG", "THÌ KHÔNG PHỤC HỒI ĐƯỢC"],
  "attribution": "DILIM SUPPLEMENT" }
```

### `plate_red`
Hộp **tự co giãn ôm chữ** — hẹp cho dòng ngắn, rộng cho dòng dài. Script đo bằng chính font sẽ render nên chiều rộng khớp thật. Đừng cố ép mọi hộp cùng chiều rộng: hộp ôm sát chữ là thứ tạo nhịp thị giác khi các caption liên tiếp thay nhau.

### `edu`
Cấu trúc hai dòng có phân vai rõ:

- Dòng 1 **trắng** = mệnh đề khẳng định ("MẠCH MÁU BỀN, SẠCH")
- Dòng 2 **vàng** = hệ quả / lợi ích ("ĐỂ MÁU LƯU THÔNG LÊN NÃO TỐT")

Muốn đảo màu thì khai báo trực tiếp:
```json
"lines": [{"text": "…", "color": "yellow"}, {"text": "…", "color": "white"}]
```

### `keyword`
Một từ, giữ **5-6 giây** — cố tình lệch khỏi nhịp 2s của các caption khác. Nó là neo chủ đề cho cả đoạn, không phải một beat. Trong lúc nó đứng yên, dải B-roll bên trên vẫn thay clip bình thường.

### `cta`
Các dòng xen kẽ hộp xanh lá và hộp đỏ, vào so le. Khai báo màu hộp riêng cho từng caption bằng `box_color`:
```json
{ "style": "cta", "lines": ["ĐỂ LẠI TÊN HOẶC SĐT"], "box_color": "red" }
```

## Khi nào bỏ hẳn caption

Đoạn ẩn dụ bằng hình ảnh (ống đồng sáng cạnh thép rỉ để nói chống oxy hoá) nên để trống chữ. Video mẫu có gần 10 giây liền không một chữ nào ở đúng chỗ đó. Hình đã nói đủ; thêm chữ chỉ làm loãng và buộc người xem chia sự chú ý.

Caption ở format này là **title card theo beat**, không phải phụ đề. Chỉ hiện ở câu đáng nhớ.

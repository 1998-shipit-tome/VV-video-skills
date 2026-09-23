# Sản phẩm DiLiM liên quan tiêu hóa — vai trò và kho hình

Thư mục `footage/05-san-pham/<Sản phẩm>/<Video | Nguyên Liệu | Ảnh>/`. `search.py --product <id>` mới trả về clip sản phẩm; mặc định search ẩn chúng để không lẫn vào B-roll minh họa.

| product_id | Thư mục | Có gì | Vai trò trong kịch bản (lặp gần như nguyên văn qua các video) |
|---|---|---|---|
| `inulin_fuji` | `Inulin Fuji FF/` | `Ảnh/`: 2 ảnh hộp Intestines (hồng) chụp studio + giấy xác nhận quảng cáo Cục ATTP + tờ quảng cáo. **Không có video.** | Chất xơ hòa tan inulin phân tử dài công nghệ Fuji FF = **"khóa cửa lại"**: chặn hấp thu mỡ xấu, nuôi lợi khuẩn, đi ngoài đều. Đoạn nói lợi khuẩn → `02-co-che-3d/loi khuan.mp4`, `men vi sinh.mp4`; đoạn chất xơ → `04-giai-phap` rau/chuối/yến mạch. |
| `nghe_okinawa` | `Nghệ Mùa Thu Okinawa/` | `Video/`: 1 clip hộp quay tay (~2 phút, nhiều góc — chọn `media_start`); `Ảnh/`: 1 ảnh hộp; `Nguyên Liệu/`: 3 clip bột nghệ/nghệ tươi + ảnh củ nghệ + 3 infographic curcumin (chữ tiếng Việt). | Nghệ Mùa Thu = **"bảo vệ gan"**, hấp thu curcumin gấp ~35 lần nghệ thường; cũng dùng cho kháng viêm dạ dày/đại tràng. Đoạn gan → `02-co-che-3d` gan nhiễm mỡ, xơ gan; `04-giai-phap` bác sĩ cầm mô hình gan. |
| `gan` | `Gan/` | `Ảnh/`: 22 ảnh hộp/viên chụp studio và chụp tay. **Không có video.** | Sản phẩm gan (bổ gan, hạ men gan). Ghép với `02-co-che-3d` gan + `03-nguyen-nhan` bia rượu/thuốc. |

Bộ 3 giảm mỡ nội tạng của DiLiM là Ellagic Acid + Inulin Fuji FF + Nghệ Mùa Thu; kho tổng **không có** thư mục Ellagic Acid nên gói này không có hình Ellagic — đoạn nói Ellagic phải crop từ A-roll.

## Cấu trúc kịch bản DiLiM (để đoán ý trước khi nghe hết)

1. Hook giật mình / tương phản → 2. liệt kê triệu chứng dồn dập → 3. nguyên nhân gốc (thường qua ẩn dụ) → 4. giới thiệu sản phẩm, xuất xứ Nhật, chuẩn GMP → 5. thành phần chủ lực + con số → 6. cơ chế bằng phép so sánh → 7. liều dùng, presenter cầm hộp thật → 8. CTA + disclaimer.

Bước 2 là nơi tăng mật độ B-roll dễ nhất (mỗi triệu chứng một nhịp). Bước 4–5 lấy hình từ `05-san-pham`. Bước 7 thường không cần B-roll (presenter đang cầm sản phẩm).

## Giọng văn

- **Giọng A** (liệt kê, số liệu, "anh chị nha"): caption ngắn, mật độ B-roll cao.
- **Giọng B** (tự sự, ẩn dụ kéo dài 4–5 câu, "hãy tưởng tượng một buổi sáng…"): ít nhịp hơn, để caption thở; ẩn dụ chính minh họa bằng caption animation vì kho không có clip vật thể ẩn dụ.

Xác định bằng 2–3 câu đầu transcript, không đoán theo sản phẩm.

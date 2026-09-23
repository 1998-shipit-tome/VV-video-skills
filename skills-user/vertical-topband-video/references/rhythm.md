# Nhịp và cấu trúc

Đọc file này ở bước 2 (cắt beat) và bước 3 (chừa breather).

## Con số

| Thông số | Giá trị | Nguồn |
|---|---|---|
| Độ dài một beat | 2–6s | Đoạn dồn dập ~2s, đoạn giải thích 4–6s |
| Mật độ B-roll | 70–90% | Video mẫu: ~83% |
| Breather cách nhau | 12–15s | |
| Breather ngắn | 1.5–2s | Giữa các đoạn |
| Breather dài | 4–5s | Một lần, ở chỗ chuyển đoạn lớn |

## B-roll là mặc định, không phải điểm nhấn

Đây là điều dễ hiểu sai nhất về format này. Dải B-roll phủ ~83% thời lượng — nó là trạng thái bình thường của khung hình, còn A-roll sạch mới là ngoại lệ.

Hệ quả với cách làm việc: câu hỏi đúng không phải "chèn B-roll ở đâu" mà là **"đoạn nào KHÔNG cần B-roll"**. Nếu bạn tiếp cận theo hướng đầu, bạn sẽ dừng ở mật độ 30-40% và video trông như một talking-head có vài minh hoạ rời rạc, không ra format này.

Cách tăng mật độ là **tìm kỹ hơn**, không phải hạ chuẩn. Nếu thấy mình đang tự thuyết phục rằng một clip "cũng tạm được" — dừng lại, hoặc tìm tiếp, hoặc để trống dải và giữ caption.

## Breather không phải chỗ trống vì lười

Cứ 12–15 giây phải có một nhịp A-roll sạch: không dải, không chữ. Ba lý do:

1. **Mắt cần nghỉ.** Khung hình liên tục thay đổi trong hai phút gây mỏi, và người xem rời đi mà không biết vì sao.
2. **Nó là dấu chấm câu.** Khoảng lặng làm đoạn tiếp theo nổi lên. Không có nó thì mọi luận điểm nghe đều đều như nhau.
3. **Nó trả lại mặt người nói.** Format này che 38% khung liên tục; breather là lúc khán giả kết nối lại với người đang nói.

Đặt **một** breather dài hơn (4–5s) đúng chỗ kịch bản chuyển đoạn lớn. Trong video mẫu, đó là 5 giây ở mốc 0:35–0:40, ngay ranh giới giữa "vấn đề" và "giải pháp". Nó vừa nghỉ mắt vừa báo hiệu cấu trúc — người xem cảm nhận được "phần một đã xong" mà không cần ai nói ra.

Ngoại lệ: **video dưới 30 giây thì bỏ breather**. Không đủ thời gian để mắt mỏi, và mỗi giây trống là một giây mất người xem.

## Một beat = một mệnh đề nói ra

Bám ranh giới câu **thật** trong transcript word-level. Đừng gộp các ý cách xa nhau vào một beat chỉ vì chúng cùng chủ đề — gộp lại là tự đánh mất điểm chèn.

Danh sách liệt kê dồn dập phải tách mỗi item thành một beat riêng. "Đau đầu, vai gáy, chóng mặt, mất ngủ, tê bì" không phải một ý — đó là năm ý, năm beat, năm clip khác nhau, mỗi cái ~2s. Chính sự dồn dập đó tạo cảm giác "triệu chứng nhiều quá", mà một clip duy nhất trải dài 10 giây không bao giờ tạo được.

Ngược lại, đoạn giải thích cơ chế nên giãn ra 4–6s mỗi clip. Người xem cần thời gian để hiểu, và cắt nhanh ở đây làm họ mất mạch.

## Caption và B-roll đổi cùng lúc — nhưng không phải luôn

Ở đoạn nhanh, caption đổi đồng bộ với cú cắt B-roll. Ở đoạn chậm, một clip B-roll có thể đỡ hai caption liên tiếp — khi đó clip phải được re-scale giữa chừng (tách thành hai beat cùng `src`, khác `in` và `kenburns`) để không đứng yên.

## Cấu trúc kịch bản của video mẫu

Không phải khuôn bắt buộc, nhưng là một bố cục đã chạy được cho video bán hàng 2 phút:

| Đoạn | Thời lượng | Vai trò |
|---|---|---|
| Hook mất mát | 3s | Gợi nỗi sợ cụ thể, chưa nhắc sản phẩm |
| Title card | 4s | Câu luận điểm trung tâm, style `quote` |
| Hậu quả | 6s | Nâng mức nghiêm trọng |
| Montage triệu chứng | 11s | ~2s/clip, dồn dập, style `plate_red` |
| **Breather dài** | **5s** | Chuyển đoạn vấn đề → giải pháp |
| Cơ chế | 12s | Giải thích, style `edu` |
| Uy tín | 10s | Nhà máy, chứng nhận, thương hiệu |
| Sản phẩm | 16s | Packshot, công nghệ |
| Thành phần + ẩn dụ | 23s | `keyword` neo 6s; đoạn ẩn dụ bỏ hẳn chữ |
| Chốt lý lẽ | 7s | Vì sao phải hành động ngay |
| CTA | 14s | Lặp 2 lần, style `cta` |
| Disclaimer | 4s | End card riêng, hard cut |

Hai điểm đáng học từ bố cục này: **CTA lặp hai lần** cùng câu chữ khác style hộp, và **disclaimer tách hẳn thành end card** với hard cut + 1 frame flash trắng, không dissolve — nó tách bạch hoàn toàn khỏi nội dung bán hàng.

## Ẩn dụ hình ảnh thay lời giải thích

Video mẫu dành gần 10 giây cho ba clip liên tiếp — ống đồng sáng, thép rỉ, mái tôn rỉ — **không một chữ nào** — để nói về chống oxy hoá. Đây là kỹ thuật đáng chú ý: khi có một hình ảnh đủ mạnh, bỏ chữ đi làm nó mạnh hơn.

Khi cắt beat cho câu ẩn dụ, tìm B-roll minh hoạ **cái được ví von**, không phải nội dung kỹ thuật tương ứng. Nói "quét sơn chống rỉ sét" thì chèn thanh sắt rỉ thật, đừng chèn hình mạch máu.

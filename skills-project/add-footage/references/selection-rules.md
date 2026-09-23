# Luật chọn B-roll — mỗi luật kèm lỗi thật đã trả giá

Phần "lỗi gốc" quan trọng hơn phần "luật": nó cho biết luật này phòng kiểu suy nghĩ sai nào. Tổng hợp từ ~20 lần sửa của người dùng trong pipeline DiLiM (07–08/2026).

## 1. Một ý → một clip, chọn theo nghĩa

"Đau đầu", "đau vai gáy", "mất ngủ" là ba ý, ba clip. Màu sắc đồ họa không quan trọng (não cam hay não xanh đều minh họa "não"), **nhưng sắc thái màu phải khớp caption**: "não bắt đầu tổn thương" → người dùng đổi não xanh sang não đỏ.

**Bám động từ / quá trình, không chỉ danh từ.** Caption "chỉ số mỡ máu TĂNG DẦN" → clip cần thể hiện *tăng*, không phải ảnh xét nghiệm tĩnh. **Tả đúng hành động được nói, không tả cảm xúc quanh nó.** Caption "bỏ cái này, thêm cái kia" → cảnh tay thay đổi món, không phải người đang lo lắng.

**Đừng bắt chước nhịp cắt video mẫu.** Đã đề xuất "cắt qua 5 người trong 5 giây cho động" — bị bác. Cắt nhanh trong video mẫu là hệ quả của mật độ ý dày, không phải phong cách. Bám đúng từng ý thật thì nhịp tự đến.

**Lỗi lớn nhất đo được (đợt 5 video, 28/07/2026): đề xuất quá ÍT, không phải chọn sai.** Khi cân nhắc "để trống vì không có match", hỏi thêm "để trống đoạn này có làm nhịp đứt quá lâu không?" — nếu có, tìm kỹ hơn (cả hình khái niệm/hỗ trợ) trước khi bỏ. Sau bản nháp, quét lại timeline tìm đoạn nhiều giây không chữ không B-roll.

## 2. Bốn lỗi xác minh kinh điển

### 2.1 Đúng chủ đề, sai cơ chế
Caption "cúi 15° cổ chịu lực 12kg" → tìm "cột sống cổ" → ra clip dây thần kinh phát sáng → xem 1 frame "đúng là cột sống" → chấp nhận. Khái niệm cần là **tải trọng cơ học**, không phải dẫn truyền thần kinh. Cải thiện từ khóa **không cứu được** lỗi này; đổi câu hỏi xác minh mới cứu: từ *"có liên quan chủ đề không?"* sang *"có mô tả đúng CẢNH/HÀNH ĐỘNG tôi đã tưởng tượng không?"*. Vì vậy: viết cảnh lý tưởng thành lời **trước khi** search.

### 2.2 Đúng chủ thể, sai cảm xúc
Caption "VẪN ĂN UỐNG HEALTHY HƠN" → chọn người ăn salad. Tên file ghi "vẻ mặt chán ghét", footage là người uể oải chọc đũa. Sắc thái ngược hoàn toàn. Clip đó là clip đúng cho ý *khác*: "chán ăn / ăn kiêng khắc nghiệt". Xác minh phải gồm biểu cảm + không khí.

### 2.3 Đúng file, sai đoạn
Clip 26s "cầm điện thoại xem tin nhắn": cảnh điện thoại ở giây 16–22, render lấy 6.6s **đầu** = cảnh vươn vai. Khi `dur` nguồn dài hơn nhiều so với đoạn cần, coi là rủi ro cao: xem `segments`, chọn `media_start`, rồi `verify_frame.py --at <media_start> --span <duration>`. Và ngược lại: **từ chối clip vì frame đầu cũng là lỗi** — quét cả file trước khi loại.

### 2.4 Bỏ câu vì hình thức
Câu mở "đau vai gáy... đầy bụng khó tiêu không?" bị bỏ vì khớp mẫu "câu hỏi mở đầu → tu từ". Nhưng nó nêu hai triệu chứng cụ thể. Sau lượt quét ý lớn, quét **từng câu** kể cả câu mở đầu với đúng một câu hỏi: *"câu này có nêu triệu chứng/cơ chế/nguyên nhân cụ thể không?"*

## 3. Timing

B-roll bắt đầu **đúng tại từ khóa được nói**, sớm tối đa 1–3 frame (60fps). Timestamp cấp câu của Whisper lệch vài giây; bắt buộc word-level và tra thời điểm của **chính từ kích hoạt**, không phải ranh giới segment.

## 4. Không lặp (trừ sản phẩm)

Dùng lại clip "sụn tách rời" cho hai caption khác nhau với lý lẽ "cùng ý" → bị bác: kho đủ sâu (99 clip riêng xương khớp), lặp đọc như lười. Ý lặp lại → clip **khác** cùng nội dung. Clip sản phẩm miễn trừ (mỗi sản phẩm chỉ có 1–2 clip chính hãng). Hai nhịp **liền nhau** dùng chung file = một đoạn liên tục, không phải lặp. Phạm vi luật: **một video** — giữa các video cùng chủ đề, dùng lại clip đã duyệt là tốt (nhất quán).

## 5. Danh sách triệu chứng dồn dập → gộp đôi

Chỉ khi **cả hai** đúng: là danh sách *triệu chứng* (không phải thành phần/các bước) **và** mỗi item < 0.5s. Gộp 2 triệu chứng / 1 nhịp B-roll, minh họa một vế; lượt liệt kê thứ 2 trong video đảo vế; lượt 3 về như lượt 1. Caption vẫn tách từng triệu chứng. Lý do: 6 clip trong 2.5s với thẻ Broll Vip → *"nhịp này nhanh quá"*.

## 6. Ẩn dụ

Ẩn dụ lướt qua ("giảm phản xạ nhận thức như xe hết xăng") → bám chủ đề chính (não), đừng đuổi theo vế ví von. Cả câu là ẩn dụ (rỉ sét, kênh bồi lắng, xe thiếu dầu, gạo xay qua rây) → minh họa đúng **cái được ví von** (`subject_type: metaphor_object`).

## 7. Người thật vs đồ họa

Ý quan hệ/cảm xúc ("đối tác là gan", "gia đình lo lắng") → **người thật**; người dùng đã đổi đồ họa 3D sang người thật cho loại này. Ý cơ chế ("mảng bám hẹp lòng mạch") → `anatomy_3d`. Bám đúng thuật ngữ khoa học: "hệ vi sinh" → clip vi khuẩn/lợi khuẩn, không phải "niêm mạc đường ruột".

## 8. Sản phẩm

Video nhắc sản phẩm → B-roll sản phẩm **chỉ** từ `Product Broll/<đúng sản phẩm>`; không thay bằng sản phẩm khác dù giống hộp. Kiểm tra cả `Video/`, `Nguyên Liệu/` (clip bubble từng thành phần — dùng cho đoạn liệt kê), `Ảnh/`. Thư mục trống (DHA+EPA+SQ, Natto Xám chỉ có ảnh) → crop cảnh presenter cầm hộp trong A-roll. Chi tiết: `product-map.md`.

## 9. Hai luật cứng của người dùng

- **Cấm tự sinh sơ đồ/hình minh họa** (PIL, SVG, đồ họa thay thế): *"từ giờ cấm bạn tự sinh sơ đồ trừ khi bạn tạo được ảnh 3d người thật"*. Không có footage khớp → A-roll thuần + caption animation.
- **Không Ken Burns / zoom theo thời gian.** Tỉ lệ phóng tĩnh, lấp kín khung, không pad đen bề ngang. Đã dựng lại 8 video vì mượn nhầm preset zoom của skill khác.

## 10. Clip ưu tiên người dùng đã chỉ định (mặc định thường trực)

Ghi trong `concept_graph.json`; `search.py` hiện nhãn `APPROVED`. Lần **đầu** ý xuất hiện trong video → dùng đúng clip đó; lần 2, 3 → clip khác **cùng cảnh và sắc thái** (mất ngủ lần 2 vẫn là người trằn trọc trên giường ban đêm, không đổi sang ngáp ở bàn làm việc). Đã chốt:

| Ý | Clip |
|---|---|
| Mất ngủ | `Đã Chuẩn Hóa/chong-mat-mat-ngu,thieu-ngu,mat-ngu-1.mp4` |
| Ngủ ngon | `Ngủ- Ngon- mất ngủ/Chú 50-60 tuổi ngủ ngon.mp4` |
| Ăn uống lành mạnh (vui, hào hứng) | `Ăn uống lành mạnh/ăn-uong-lanh-manh.mp4`, `.../Thiết kế chưa có tên (15).mp4`, `.../8845448-uhd_4096_2160_24fps.mp4` |
| Chán ăn / ăn kiêng khắc nghiệt | `Giảm cân - Mập, tăng cân/033 - Dùng nĩa xúc rau xà lách ăn, vẻ mặt chán ghét khi ăn.mp4`, `Đã Chuẩn Hóa/032 - Ngồi ăn món salad...` |
| Cơ thể khỏe (ẩn ý qua vận động, nhất là người lớn tuổi) | `Thể dục thể thao/Thiết kế chưa có tên - 2024-12-20T115808.557.mp4` (cặp cô chú chạy bộ cười), `.../Thiết kế chưa có tên (3).mp4`, `.../Thiết kế chưa có tên - 2025-03-26T083741.007.mp4` |

Sau khi build index lần đầu, chạy `import_legacy.py` với `D:\tinh-media-workflow\pipeline\broll_memory.json` (63 cặp đã duyệt) và `approve` các dòng trên để search biết.

## 11. Thứ tự kho theo thói quen thật của người dùng

Đo từ 10 lần người dùng thay clip: `Đã Chuẩn Hóa` (17) > `Khám bệnh` (13) > `Thể dục thể thao` (12) > `Ngủ- Ngon- mất ngủ` (10) > `Giảm cân` (7) > `Đồ ăn` = `Nhân Viên văn phòng` (6) > `Lộn Xộn Xà bần` (5). Hai kho Claude hay bỏ quên: `Nhân Viên văn phòng`, `Ngủ- Ngon- mất ngủ` (ý mệt mỏi / công việc / giấc ngủ). Người dùng ưu tiên thư mục đã phân loại hơn `Lộn Xộn Xà bần` khi có clip tương đương.

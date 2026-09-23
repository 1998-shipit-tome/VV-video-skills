# Bản đồ sản phẩm, cấu trúc kịch bản và giọng văn

Tổng hợp từ việc phân tích ~24 video mẫu do người dùng cung cấp, phủ toàn bộ dòng sản phẩm DiLiM.

## Mục lục
1. [Bảng ghép sản phẩm ↔ thư mục](#1-bảng-ghép-sản-phẩm--thư-mục)
2. [Cấu trúc kịch bản chung](#2-cấu-trúc-kịch-bản-chung)
3. [Hai giọng văn A và B](#3-hai-giọng-văn-a-và-b)
4. [Cụm triệu chứng dùng chung](#4-cụm-triệu-chứng-dùng-chung)
5. [Các phong cách B-roll đã quan sát](#5-các-phong-cách-b-roll-đã-quan-sát)

---

## 1. Bảng ghép sản phẩm ↔ thư mục

Gốc kho: `D:\download\Footage B-roll\`. Thư mục sản phẩm: `Product Broll\<Tên sản phẩm>\`.

| Sản phẩm / combo | Thư mục sản phẩm | Kho chủ đề ghép cặp | Ghi chú quan trọng |
|---|---|---|---|
| **Nano Sụn Cá Mập + Gluchongel** (thoái hóa khớp, đau khớp gối) | `Nano Sụn cá mập Nhật Bản/`, `GLUCHONGEL/` | `Xương khớp - Đau` | Thư mục `Nguyên Liệu/` có **6 clip bubble riêng cho từng thành phần** (Chondroitin, Glucosamine, Hyaluronic Acid, Collagen type 2, MSM, Canxi+D3) — dùng cho đoạn liệt kê thành phần. Các clip này cần crop+pad lại vị trí trước khi dùng, vì bubble nằm lệch so với vùng crop-giữa mặc định. |
| **Rich Coenzyme Q10** (năng lượng tế bào não, thiếu máu não) | `Rich Coenzyme Q10/` | `Mạch Máu - Thần Kinh - TẾ BÀO`, `Đau đầu - Chóng mặt - Mệt mõi - Bệnh`, `Đột quỵ`, `Ngủ- Ngon- mất ngủ`, `Đã Chuẩn Hóa` (có clip "hay quên/trí nhớ kém") | Sản phẩm lõi, xuất hiện trong nhiều combo bên dưới. |
| **Raydel Policosanol** (mỡ máu, xơ vữa mạch máu) | `Raydel Policosanol/` | `Mạch Máu - Thần Kinh - TẾ BÀO` (xơ vữa), `Đột quỵ`, `Đau đầu - Chóng mặt` | File `Video/Video chứa cảnh nguyên liệu, viện nghiên cứu, sáp mía cuba.mp4` dài 115s và chứa **nhiều cảnh khác nhau** (bản đồ Cuba, ảnh biểu đồ nghiên cứu lâm sàng, animation cơ chế LDL/HDL) — phải cắt thành nhiều đoạn riêng, không dùng nguyên một mạch. Thường bán combo với Rich Coenzyme Q10. |
| **Ellagic Acid + Inulin Fuji FF + Nghệ Mùa Thu Okinawa** (bộ 3 giảm mỡ nội tạng) | `Ellagic Acid - Giảm mỡ nội tạng/`, `Chất xơ hoà tan inulin phân tử dài công nghệ Fuji FF/`, `Nghệ Mùa Thu Okinawa Nhật Bản/` | `Giảm cân - Mập, tăng cân`, `Nhân Viên văn phòng`, `NỘI TẠNG` (gan) | Mỗi sản phẩm có **một vai trò cố định** lặp gần như nguyên văn qua mọi video: Ellagic Acid = "đẩy mỡ ra ngoài"; Inulin = "khóa cửa lại" (chặn hấp thu mỡ xấu, nuôi lợi khuẩn); Nghệ Mùa Thu = "bảo vệ gan" (hấp thu Curcumin gấp 35 lần nghệ thường). B-roll ở nhóm này nghiêng hẳn về **ảnh sản phẩm thật** thay vì đồ họa 3D. |
| **Rich Coenzyme Q10 + DHA·EPA+SQ** (combo cam kết 12 tháng) | `Rich Coenzyme Q10/`, `DHA + EPA + SQ/` ⚠️ **thư mục trống** | Như Rich Coenzyme Q10 | SQ (Squalene) = "cung cấp oxy cho tế bào"; DHA = "bổ não sáng mắt"; EPA = giảm mỡ xấu máu. Có cấu trúc bậc: 2 tháng → cải thiện triệu chứng; 6 tháng → ngủ sâu/tập trung; 12 tháng → tặng thêm 1 hộp + hiệu ứng phụ "da trẻ ra ~5 tuổi". Vì thư mục trống, phải crop B-roll sản phẩm từ chính A-roll. |
| **Rich Coenzyme Q10 + Nano Nattokinase 60.000FU** (phòng đột quỵ, tuần hoàn) | `Rich Coenzyme Q10/`, `Natto Xám/` ⚠️ **chỉ có 1 ảnh, không có video** | `Mạch Máu - Thần Kinh - TẾ BÀO`, `Đột quỵ`, `Đau đầu - Chóng mặt` | Nattokinase = enzyme từ natto, vai trò "phân giải fibrin/cục máu đông", luôn nhấn hoạt lực **60.000 FU** đối lập với sản phẩm thị trường chỉ ~20.000 FU. Combo này gần như luôn dùng **giọng văn B**. |
| **Rich Coenzyme Q10 + Hàu Nano Gold** (sinh lực nam giới) | `Rich Coenzyme Q10/`, `Hàu Nano Gold/` | Chưa có kho triệu chứng riêng — thử `Hàu- Vợ chồng` trước, rồi `Nhân Viên văn phòng` cho khung stress/mệt mỏi | Video mẫu nằm trên Google Drive (`G:\My Drive\DILI SUPPLEMENT TỔNG\...\8 HÀU\`), **khác vị trí kho local**. Khung "N trụ cột" (3 hoặc 5 tùy video): Rich Q10 lo năng lượng + bảo vệ mạch máu; Hàu Nano Gold lo sinh lực qua 5 hoạt chất (chiết xuất hàu, tỏi đen lên men, rễ maca, đông trùng hạ thảo). Ẩn dụ nano riêng của nhóm này: **"xay gạo thành bột rồi rây qua sàng mịn"**. ⚠️ Ngách này dùng hình ảnh gợi ý nhạy cảm hơn hẳn (cảnh phòng ngủ, ẩn dụ vật thể) — là quy ước quảng cáo hợp lệ, nhưng nên hỏi người dùng về mức độ táo bạo mong muốn trước khi tái sử dụng. |

---

## 2. Cấu trúc kịch bản chung

Mọi video bán sản phẩm phân tích được đều theo khung này:

1. **Hook** — một sự thật gây giật mình hoặc phép tương phản ("mất tiền tìm lại được, tế bào não tổn thương thì không"; "30 tuổi mà sống với cái đầu 60").
2. **Liệt kê triệu chứng dồn dập** — một cụm triệu chứng đọc liên tiếp trong một hơi.
3. **Giải thích nguyên nhân gốc** — thường qua một ẩn dụ (rỉ sét, đôi giày mòn, dầu nhớt động cơ, điện trong biệt thự).
4. **Giới thiệu sản phẩm** — thương hiệu, xuất xứ, chuẩn sản xuất (GMP Nhật Bản), số nghiên cứu lâm sàng, tính độc quyền.
5. **Nêu bật thành phần chủ lực** — Astaxanthin xuất hiện lặp qua nhiều sản phẩm khác nhau, luôn kèm "mạnh gấp 6.000 lần vitamin C".
6. **Giải thích cơ chế bằng phép so sánh** — LDL/HDL "dọn dẹp"; Coenzyme Q10 là "nhà máy điện"; so sánh dòng flagship (Mercedes Maybach, iPhone Pro Max).
7. **Liều dùng cụ thể** — presenter tự cầm viên/hộp thật, nói rõ liều và thời gian.
8. **CTA đóng** — "để lại tên/SĐT hoặc gọi hotline" + disclaimer bắt buộc "sản phẩm này không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh".

**Quan sát quan trọng**: cùng một sản phẩm được quay nhiều lần với kịch bản gần như giống hệt — nhưng **lựa chọn clip B-roll thì không lặp lại giữa các bản**. Chính video mẫu của người dùng cũng tuân thủ luật không-lặp-clip.

---

## 3. Hai giọng văn A và B

Xác định bằng cách đọc **2-3 câu mở đầu** transcript. Đọc thật, không đoán theo tên sản phẩm — cùng một sản phẩm có thể có video ở cả hai giọng.

### Giọng A — trực tiếp, liệt kê, hào hứng

Dấu hiệu:
- Câu mở là **hỏi-đáp kiến thức trực tiếp**: "anh chị có biết vì sao..." rồi trả lời ngay bằng nguyên nhân.
- Đếm số tường minh, dày đặc: "đầu tiên là...", "thứ nhất... thứ hai... thứ ba...".
- Số liệu/superlative **ném thẳng vào câu** không dẫn dắt: "gấp 6.000 lần vitamin C", "bán chạy số 1 tại Úc", "độ tinh khiết 99%", "top 3 nhà máy Nhật Bản".
- Ẩn dụ (nếu có) gói gọn trong một câu rồi chuyển ý ngay.
- Verbal tic "anh chị nha/anh chị ha" gần như mọi câu; nhịp nói nhanh, ít khoảng lặng.
- Cảm xúc: tự tin bán hàng, "Sơn đã tìm rất lâu mới ra sản phẩm như thế này".

Đã dùng ở: bộ 3 Ellagic Acid (cả 6 video), Raydel Policosanol (cả 2), Rich Coenzyme Q10 bản gốc (cả 2), Rich+DHA 12 tháng.

**Cách viết caption cho giọng A**: caption ngắn, nhịp nhanh, nhồi fact và số liệu. Mật độ điểm chèn cao.

### Giọng B — tự sự, triết lý, ẩn dụ kéo dài

Dấu hiệu:
- Câu mở là câu hỏi hướng vào **nội tâm người xem**: "có một câu hỏi mà Sơn muốn bạn thành thật với chính bản thân mình... lần cuối cùng bạn thực sự nghĩ đến sức khỏe của mình là khi nào?".
- Có bước **trấn an sớm**: "đây không phải là bệnh đâu anh chị, đây là tín hiệu / là lời nhắc".
- **Một ẩn dụ được kể trải dài qua 4-5 câu liên tiếp**, không phải một dòng: con đường nhựa nứt li ti → không ai sửa → một năm sau mặt đường lún xuống → mạch máu đi đúng lộ trình đó. Hoặc: dòng kênh chảy chậm → rác lắng đọng → lòng kênh hẹp dần.
- Khung **"2 gốc rễ" / "3 trục nền tảng"** ("kiềng ba chân") được giải thích chậm rãi thay vì liệt kê nhanh.
- Gần như luôn kết bằng **đoạn hình dung tương lai**: "hãy tưởng tượng một buổi sáng chúng ta thức dậy, đầu nhẹ nhàng, bước xuống giường vững vàng, tối về vẫn còn năng lượng cười đùa với gia đình".
- Mật độ fact/tính năng trên mỗi phút **thấp hơn hẳn**; lặp lại cùng một logic bằng nhiều cách diễn đạt.
- Cảm xúc: điềm tĩnh, đồng cảm — "Sơn hiểu điều này bởi vì Sơn đã chứng kiến quá nhiều lần...", "Sơn tin vào...".

Đã dùng ở: toàn bộ 5 video combo Nano Nattokinase + Rich Coenzyme Q10.

**Cách viết caption cho giọng B**: ít nhịp hơn, câu dài mang tính hình ảnh/ẩn dụ, không vội vàng liệt kê. Để caption thở cùng nhịp nói chậm.

### Vì sao phải khớp giọng
Một kịch bản giọng B mà đem render bằng caption kiểu liệt kê nhanh của giọng A (hoặc ngược lại) sẽ **đá nhau với nhịp nói** và phá vỡ vòng cung cảm xúc mà người viết kịch bản chủ ý xây dựng. Người xem cảm nhận được sự lệch nhịp này ngay cả khi không gọi tên được nó.

---

## 4. Cụm triệu chứng dùng chung

Cụm này xuất hiện **gần như nguyên văn** qua Nano Sụn, Rich Coenzyme Q10, Raydel và Nattokinase — dù khung nguyên nhân gốc khác nhau hoàn toàn (mòn sụn vs. thiếu năng lượng não vs. mỡ máu):

> "đau đầu, vai gáy, chóng mặt, mất ngủ, tê bì tay chân, rối loạn tiền đình, hay quên, kém tập trung"

Khi gặp cụm này, lấy clip từ: `Đau đầu - Chóng mặt - Mệt mõi - Bệnh`, `Ngủ- Ngon- mất ngủ`, `Đã Chuẩn Hóa` (hay quên/trí nhớ).

**Và tách mỗi triệu chứng thành một nhịp caption + B-roll riêng** — đây là nơi dễ tăng mật độ nhất mà vẫn hoàn toàn chính xác, vì mỗi triệu chứng đều rất cụ thể và dễ minh họa.

---

## 5. Các phong cách B-roll đã quan sát

Video mẫu của DiLiM **không dùng một khuôn cố định**. Ít nhất 5 kiểu compositing khác nhau, dùng tùy tình huống:

1. **Hộp chữ nhật cạnh cứng** phủ ~55% trên khung, đục hoàn toàn.
2. **Blend mờ mềm cạnh** toàn khung hoặc gần toàn khung, opacity 40-70%, mép feather.
3. **Cutout người phát sáng** — bóng người có viền glow, nổi trên nền thay vì nằm trong hộp cứng.
4. **Inset PiP nhỏ** — cửa sổ bo góc nhỏ hơn hẳn chiều rộng khung, xếp lớp giữa khung hình.
5. **Split-screen dọc cứng** — chia đôi trái/phải.

Ngoài ra còn các loại B-roll **không phải overlay**: presenter tự cầm hộp/viên thật (chính A-roll, không phải clip chèn), zoom cận cảnh vào chính đồ họa in trên vỏ hộp (ví dụ icon "-LDL/HDL+"), và ảnh chụp biểu đồ nghiên cứu lâm sàng dùng làm B-roll "bằng chứng".

**Hệ quả**: pipeline hiện tại mặc định kiểu #1 (dải trên cứng) — đó chỉ là kiểu được xây và kiểm chứng đầu tiên, **không phải kiểu "đúng chuẩn" duy nhất**. Khi dựng lần đầu cho một sản phẩm hoặc dạng video mới, hỏi lại người dùng muốn giữ kiểu dải trên hay mở rộng sang một trong các kiểu trên, thay vì mặc định.

# Luật chọn B-roll tiêu hóa — mỗi luật kèm lỗi thật đã trả giá

Rút từ ~20 lần người dựng DiLiM sửa lại lựa chọn của agent (07–09/2026). Phần "lỗi gốc" quan trọng hơn phần "luật": nó cho biết luật này phòng kiểu suy nghĩ sai nào.

## 1. Một ý → một clip, chọn theo NGHĨA của cảnh

"Đau bụng", "đầy hơi", "táo bón" là ba ý, ba clip. **Bám động từ / quá trình, không chỉ danh từ**: caption "hại khuẩn TẤN CÔNG niêm mạc" cần clip thành ruột đang bị phá (`02-co-che-3d/022 …` đoạn 88–147s), không phải clip nhung mao lành lặn (`niem-mac-duong-ruotj`). Caption "bỏ đồ chiên, thêm rau" → cảnh tay đổi món, không phải người đang lo lắng.

**Lỗi lớn nhất đo được: đề xuất quá ÍT, không phải chọn sai.** Khi định để trống vì "không có match", hỏi thêm: đoạn trống này có làm nhịp đứt quá 5 giây không? Nếu có, tìm kỹ hơn (kể cả hình khái niệm/hỗ trợ ở `03-nguyen-nhan`, `04-giai-phap`) trước khi bỏ.

## 2. Bốn lỗi xác minh kinh điển

### 2.1 Đúng chủ đề, sai cơ chế
"Dạ dày" có trong tên file không có nghĩa clip mô tả đúng điều đang nói. `NỘI TẠNG/043` là viên thuốc rơi vào dạ dày và tan — đúng cho "thuốc vào dạ dày", **sai** cho "viêm loét dạ dày". Cách phòng duy nhất: **viết cảnh lý tưởng thành lời trước khi search**, rồi xác minh bằng câu hỏi *"có mô tả đúng CẢNH/HÀNH ĐỘNG tôi đã tưởng tượng không?"* thay vì *"có liên quan chủ đề không?"*.

### 2.2 Đúng chủ thể, sai cảm xúc
Caption "ăn uống lành mạnh hơn" → chọn người ăn salad — nhưng có clip người ăn salad **chán ghét** (kho tổng). Trong kho này các clip salad ở `04-giai-phap` đều vui/neutral; vẫn phải mở sheet xem biểu cảm. Ngược lại, ý "ăn kiêng khổ sở" thì đừng lấy clip ăn salad tươi cười.

### 2.3 Đúng file, sai đoạn
`NỘI TẠNG/042` dài 78s: 0–13s toàn thân, 13–26s viên thuốc xuống họng, **26–52s axit trào ngược lên thực quản**, 52–78s cảnh thật hai phụ nữ ăn trưa. Render lấy 5s đầu cho ý "trào ngược" là sai hoàn toàn. Khi `dur` nguồn dài hơn nhiều so với đoạn cần: xem `segments`, chọn `media_start`, rồi `verify_frame.py <id> --at <media_start> --span <duration>`. Và ngược lại: **từ chối clip vì frame đầu cũng là lỗi** — `Dau-bung … (1).mp4` mở đầu bà cụ ngồi bình thường, cảnh đau ở giữa.

### 2.4 Bỏ câu vì hình thức
Câu mở "anh chị có hay đầy bụng, ợ hơi sau ăn không?" bị bỏ vì khớp mẫu "câu hỏi tu từ". Nhưng nó nêu hai triệu chứng cụ thể (`03-nguyen-nhan/… 106 - xoa bụng sau khi ăn`, `01-trieu-chung/012 - Đứng ôm bụng`). Sau lượt quét ý lớn, quét **từng câu** với đúng một câu hỏi: *"câu này có nêu triệu chứng / cơ chế / nguyên nhân / hành động cụ thể không?"*

## 3. Timing

B-roll bắt đầu **đúng tại từ khóa được nói**, sớm tối đa 1–3 frame. Timestamp cấp câu của Whisper lệch vài giây; cần word-level và tra thời điểm của **chính từ kích hoạt** ("táo bón" chứ không phải đầu câu).

## 4. Không lặp clip (trừ sản phẩm)

Một clip không-phải-sản-phẩm chỉ xuất hiện **một lần** trong một video. Ý lặp lại → clip **khác** cùng nội dung: táo bón lần 1 = `006 - Ngồi trên bồn cầu…`, lần 2 = `020 - Ngồi trên bồn cầu, tư thế căng thẳng…`, lần 3 = `dau bụng.mp4`. Clip sản phẩm được miễn. Hai nhịp **liền nhau** dùng chung file = một đoạn liên tục, không tính lặp. Giữa các video khác nhau, dùng lại clip đã duyệt là tốt (nhất quán thương hiệu).

## 5. Danh sách triệu chứng dồn dập → gộp đôi

Chỉ khi **cả hai** đúng: là danh sách *triệu chứng* **và** mỗi item < 0,5 s ("đầy hơi, ợ chua, táo bón, tiêu chảy…"). Gộp 2 triệu chứng / 1 nhịp B-roll, minh họa một vế; lượt liệt kê thứ 2 trong video đảo vế. Caption vẫn tách từng triệu chứng.

## 6. Ẩn dụ

Ẩn dụ lướt qua ("ruột như cái ống nước lâu ngày") → bám chủ đề chính (ruột: `016 - Camera lia dọc theo ống ruột cho thấy các mảng cặn bẩn`). Cả câu là ẩn dụ kéo dài (kênh bồi lắng, máy lọc nghẹt) → kho này **không có** clip vật thể ẩn dụ; để caption animation, đừng cố ép clip y khoa.

## 7. Người thật vs đồ họa

Ý quan hệ / cảm xúc / sinh hoạt ("mỗi lần đi ăn tiệc là lo", "ngồi trong toilet cả buổi") → **người thật** (`01-trieu-chung`). Ý cơ chế ("lợi khuẩn giảm, hại khuẩn tăng", "niêm mạc bị bào mòn", "mỡ bao quanh gan") → `02-co-che-3d`. Bám đúng thuật ngữ: "hệ vi sinh" → clip vi khuẩn (`loi khuan.mp4`, `men vi sinh.mp4`), **không phải** clip nhung mao.

## 8. Sản phẩm

Video nhắc sản phẩm → B-roll sản phẩm **chỉ** từ `05-san-pham/<đúng sản phẩm>` (`--product inulin_fuji | nghe_okinawa | gan`); không thay bằng sản phẩm khác dù hộp giống. Inulin và Gan chỉ có **ảnh**, Nghệ có 1 video + ảnh + 3 clip nguyên liệu (bột nghệ). Đoạn dài về sản phẩm mà thiếu clip → crop cảnh presenter cầm hộp trong chính A-roll. Chi tiết vai trò từng sản phẩm: `san-pham.md`.

## 9. Hai luật cứng

- **Không tự vẽ sơ đồ / hình minh họa thay thế** (PIL, SVG, đồ họa tự sinh). Không có footage khớp → A-roll thuần + caption animation.
- **Không Ken Burns / zoom theo thời gian.** Tỉ lệ phóng tĩnh, lấp kín khung, không pad đen hai bên.

## 10. Clip chất lượng cần lưu ý

| Clip | Vấn đề | Cách dùng |
|---|---|---|
| `02-co-che-3d/022 - Mô phỏng quá trình vi sinh vật gây hại…` (176s) | logo Amlan góc trên phải, 2 đoạn màn đen | chỉ lấy trong các `segments`, tránh 0–14.5s và 73.5–88s; dải trên đỉnh cắt ngang có thể che logo |
| `02-co-che-3d/023 - Vi khuẩn và hạt độc tố…` (93s) | chữ tiếng Anh burn sẵn ở 39–70s, logo nhỏ | dùng 0–7.5s hoặc 23.5–39s (vi khuẩn thuần) |
| `02-co-che-3d/gan-nhiem-mo,mo-noi-tang…` | chú thích tiếng Anh dưới đáy | dải `top` 1080×608 crop giữa thường cắt mất chữ — verify_frame để chắc |
| `02-co-che-3d/042 …` và `043 …` | 1280×720 / 720×480 (`low_res`) | chỉ khi không có clip khác cho "trào ngược"/"thuốc vào dạ dày" |
| `02-co-che-3d/Ruột.mp4`, `dạ dày.mp4` | icon nhỏ giữa khung | dùng cho thẻ `vip` hơn là dải `top` |
| `05-san-pham/…/Gemini_Generated…` | infographic chữ tiếng Việt | hình "bằng chứng"/giải thích, không phải B-roll cảnh |

# Hệ thống caption — style "Dr Sơn"

## 1. Nguyên tắc màu: màu mang NGHĨA

Đây là thay đổi lớn nhất người dùng yêu cầu sau bản dựng đầu tiên. Trước đó màu xoay theo một nhịp định sẵn (trắng/trắng/vàng, và một vòng xoay 50/30/20 cho caption 2 dòng) — kết quả là màu rơi ngẫu nhiên lên nội dung, sinh ra cả lỗi **chữ vàng trên nền trắng không đọc được**.

Quy tắc hiện tại:

| Loại nội dung | Màu | Ghi chú |
|---|---|---|
| **Ý tiêu cực** — triệu chứng, cảnh báo, rủi ro, hậu quả xấu | Đỏ | Nền `#D62828`, chữ trắng, keyword vàng `#FFEA00`. Với caption 2 dòng, dòng thứ hai đảo lại: nền trắng, chữ đỏ, keyword **đen** (không dùng vàng ở đây — vàng trên nền trắng quá mờ). |
| **Ý tích cực** — lợi ích, kết quả tốt, lối sống khỏe mạnh | Xanh lá | Nền trắng chữ xanh `#157A3F` / nền xanh chữ trắng cho 2 dòng, keyword đỏ hoặc vàng. |
| **Sản phẩm** — tên sản phẩm, thành phần, chứng nhận, giá | Trắng + vàng đậm | Nền trắng `#FFFFFF`, chữ xanh `#157A3F`, keyword vàng đậm `#B8860B`. **Tuyệt đối không dùng đỏ hoặc đen** ở bất kỳ vị trí nào (nền/chữ/keyword) trong nhóm này — người dùng chốt rõ. |
| **CTA đóng video** | Trắng | Nền trắng, chữ xanh, keyword đỏ. |

**Gán màu rõ ràng cho mọi caption.** Vòng xoay ngẫu nhiên chỉ nên là dự phòng cuối cùng khi thực sự không phân loại được ý nghĩa — nếu thấy mình đang để nhiều caption rơi vào dự phòng, đó là dấu hiệu chưa đọc kỹ nội dung.

## 2. Markup và format

- Bọc `*từ khóa*` để đổi màu nhấn cho phần đó trong dòng.
- Xuống dòng bằng `\n` — tối đa 2 dòng mỗi caption.
- Toàn bộ chữ được viết hoa khi render, không cần tự viết hoa trong nội dung.

### Cách tách markup: coi `*` là CÔNG TẮC, không phải cặp đóng-mở từng dòng

Duyệt cả khối caption một lượt, gặp `*` thì lật trạng thái keyword. Hai lợi ích:

1. Từ khóa **vắt qua hai dòng** vẫn tô đúng — `MẠCH MÁU *TRƠN` / `LÁNG, SẠCH ĐẸP HƠN*` cho ra cả "TRƠN" lẫn "LÁNG, SẠCH ĐẸP HƠN" là keyword.
2. **Mọi dấu `*` đều bị nuốt**, kể cả dấu lẻ — không bao giờ lọt lên màn hình.

**Lỗi đã gặp**: cách cũ dùng regex tìm cặp `\*[^*]+\*` trong **một dòng**. Dòng nào số dấu lẻ thì không khớp cặp nào và dấu `*` được vẽ nguyên si. **20 dòng trên 7 video** bị lộ dấu sao, người dùng phải tự phát hiện sau khi đã render xong.

### Thiếu dấu thì TỰ ĐIỀN, không bỏ mặc

Người dùng đã chốt: *"nếu dấu tôi điền bị thiếu thì 1 là bạn hỏi lại tôi, 2 là bạn tự điền dấu còn thiếu"*. Không được để dấu lẻ trôi vào bản render.

Quy tắc suy ra dấu thiếu — **dấu dính liền phía nào thì thuộc phía đó**:

| Dạng | Đọc là | Từ khoá |
|---|---|---|
| `CHỐNG ĐƯỢC *OXY HÓA MỠ` | dấu sát chữ bên phải → dấu **mở** | chạy tới hết dòng |
| `NHIỀU BẰNG SÁNG CHẾ*` | dấu sát chữ bên trái → dấu **đóng** | tính từ đầu dòng |
| `FLAGSHIP* CỦA AFC` | dấu sát chữ bên trái → dấu **đóng** | `FLAGSHIP` |
| `VÀO CƠ THỂ *` | lửng cả hai phía → **hỏi lại người dùng** | bỏ dấu, không tô |

Chỉ chạy sửa khi **tổng** số dấu của cả caption là lẻ. Tổng chẵn thì để nguyên — đó có thể là từ khoá cố ý vắt qua hai dòng.

Luôn **báo ra đã sửa gì**, đừng sửa lặng lẽ.

### Chuẩn hoá `\xa0`

Space không ngắt lẫn vào khi dán chữ từ trình duyệt, hiện ra thành khoảng trắng đôi. Đổi thành space thường — đây là chuẩn hoá, không phải đoán ý. Đã đếm ~30 dòng dính lỗi này trong một đợt 8 video.

Ví dụ:
```
"SỤN KHỚP CỦA CHÚNG TA\n*KHÔNG BIẾT KÊU* CHO TỚI KHI MÒN THẬT SỰ"
```

## 3. Font và hình khối

- Font **Anton** (ghi đè font gốc "Inter" của bộ style Dr Sơn — người dùng chỉ định riêng cho DiLiM).
- Cỡ chữ: 68px cho caption 1 dòng, 58px cho 2 dòng. Tự động thu nhỏ dần (tối thiểu 34px) nếu dòng dài nhất tràn khung — lỗi tràn chữ ra ngoài mép phải đã từng xảy ra và phải sửa bằng cơ chế này.
- **Bo góc 14px** cho khung nền caption (người dùng chốt, thay cho góc vuông ban đầu — nhìn mềm hơn hẳn).
- Lề an toàn hai bên: 40px.

## 4. Vị trí

Vị trí caption **cố định cho cả video**, không đổi theo từng caption:
- Nếu B-roll đặt ở dải trên → caption **luôn** nằm ngay dưới dải B-roll (cách mép dưới dải 10px), kể cả ở những đoạn không có B-roll.

**Neo theo TÂM, không neo theo mép trên.** Lấy chiều cao khối caption 2 dòng làm mốc; caption 1 dòng phải nằm giữa mốc đó, tức dịch xuống thêm nửa phần chênh lệch.

Lỗi đã gặp: neo mép trên nên caption 1 dòng và 2 dòng cùng mép trên, làm caption 1 dòng **nằm lệch hẳn lên trên**. Người dùng phát hiện: *"vị trí text 1 dòng chưa nằm giữa text 2 dòng mà nằm phía trên"*. Với cỡ chữ đang dùng, khối 1 dòng cao 131px còn khối 2 dòng cao 242px — lệch tới 55px, mắt thấy chữ nhảy lên xuống giữa các nhịp.
- Nếu B-roll đặt ở dưới → caption luôn ở dưới.

Người dùng nói rõ: *"nếu b-roll ở trên thì text LUÔN LUÔN ở trên"*. Lý do là caption nhảy vị trí giữa chừng làm mắt người xem phải đuổi theo, gây khó chịu — dù về lý thuyết mỗi caption đều "vừa khít" chỗ trống của nó.

Caption không bao giờ được đè lên B-roll hay che mặt người nói.

## 5. Animation

- **Push ngang từ trái sang phải** khi caption xuất hiện: lệch trái 90px rồi trượt vào vị trí trong ~10 frame. (Thiết kế ban đầu là push dọc từ dưới lên, người dùng đổi sang ngang.)
- **Khi biến mất: cắt thẳng, không fade.** Chỉ có animation lúc hiện, không có animation lúc mất.

Chuyển động này không chỉ để đẹp — nó là thứ **giữ nhịp ở những đoạn không có B-roll**. Một caption tĩnh hoàn toàn không tạo được điểm nhấn thị giác; caption có animation thì có.

## 6. Cách cắt caption để tối đa mật độ

Ba nguyên tắc, theo thứ tự tác động:

1. **Bám ranh giới câu thật trong transcript.** Bản dựng "Sụn khớp không biết kêu" tăng từ 51 lên 69 caption chỉ nhờ bám sát ranh giới câu tự nhiên thay vì gộp ý. Không cần nghĩ ra nội dung mới — chỉ cần thôi gộp.

2. **Mỗi item trong danh sách liệt kê = một nhịp riêng.** Đây là nguồn tăng mật độ lớn nhất và an toàn nhất, vì mỗi item vốn đã rất cụ thể.

3. **Giữ caption ở đoạn không có B-roll.** "Để trống nếu không match" chỉ áp dụng cho **lớp B-roll** — không tự động kéo theo bỏ luôn caption. Nhiều video có ý trừu tượng, lan man; caption có animation vẫn giữ được nhịp ở đó.

## 7. Timing caption

Giống B-roll: dùng timestamp **cấp từ**, canh caption xuất hiện đúng tại cụm từ nó diễn giải.

Lỗi đã gặp: caption hiện sớm hơn lời nói vài giây vì lấy mốc từ ranh giới segment của Whisper thay vì mốc của chính cụm từ được nhắc trong caption đó. Khi một caption diễn giải một cụm nằm ở **giữa hoặc cuối** một câu dài, mốc của nó phải lấy từ chính cụm đó — không phải từ đầu câu.

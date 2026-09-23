# Luật chọn B-roll — kèm lỗi thật đã gặp

Mỗi luật dưới đây đến từ một lần làm sai thật trong dự án. Phần "lỗi gốc" quan trọng hơn phần "luật", vì nó cho biết luật này phòng chống kiểu suy nghĩ sai nào.

## Mục lục
1. [Chọn theo ý nghĩa, không theo bề mặt](#1-chọn-theo-ý-nghĩa-không-theo-bề-mặt)
2. [Bốn lỗi xác minh kinh điển](#2-bốn-lỗi-xác-minh-kinh-điển)
3. [Timing](#3-timing)
4. [Tìm ở đâu](#4-tìm-ở-đâu)
5. [Hai luật cứng](#5-hai-luật-cứng)
6. [Clip ưu tiên do người dùng chỉ định](#6-clip-ưu-tiên-do-người-dùng-chỉ-định)

---

## 1. Chọn theo ý nghĩa, không theo bề mặt

**Đơn vị khớp là MỘT Ý → MỘT CLIP.** "Đau đầu" là một ý; "đau vai gáy" là ý khác; "mất ngủ" là ý khác nữa. Mỗi ý một clip riêng khớp nội dung, không gom chung.

Màu sắc không quan trọng. Nếu video mẫu dùng đồ họa não màu cam cho một ý, đồ họa não màu xanh truyền tải cùng khái niệm là thay thế hợp lệ — đừng chờ đúng màu.

**Đừng bắt chước nhịp cắt của video tham khảo như một đặc tả.** Có lần thấy video mẫu cắt qua 5 người khác nhau trong 5 giây và đề xuất dựng lại cho "động" hơn — người dùng bác bỏ hoàn toàn. Nhịp cắt nhanh trong video mẫu là **hệ quả** của mật độ ý dày đặc, không phải phong cách cần sao chép. Bám đúng từng ý thật thì nhịp tự đến.

**Để trống nếu không có match tốt.** Đừng lấp bằng clip không liên quan hay dùng lại clip cũ chỉ để tránh khoảng trống. Người dùng đã từng bắt gỡ bỏ 2 clip chèn chỉ có mục đích lấp thời lượng.

### Ngoại lệ: danh sách TRIỆU CHỨNG đọc dồn dập → gộp đôi

**Điều kiện áp dụng — cả hai phải đúng:**
- là danh sách **triệu chứng** (không phải thành phần, không phải các bước);
- đọc **dồn dập**, mỗi item **dưới nửa giây**.

Ngoài điều kiện này thì giữ nguyên luật gốc: mỗi item một nhịp, một clip.

**Cách làm:** gộp **2 triệu chứng thành MỘT nhịp B-roll**, và nhịp đó chỉ minh hoạ **một vế**:

| Cụm | Lần 1 | Lần 2 | Lần 3 |
|---|---|---|---|
| đau đầu · vai gáy | **đau đầu** | vai gáy | đau đầu |
| chóng mặt · mất ngủ | **mất ngủ** | chóng mặt | mất ngủ |
| tê bì tay chân · rối loạn tiền đình | **tê bì tay chân** | tiền đình | tê bì tay chân |

Danh sách lặp lại lần 2 trong cùng video thì **đảo sang vế còn lại**; lần 3 đảo ngược lại lần 2, tức quay về như lần 1. Nhờ đảo vế mà clip tự khác nhau giữa các lượt, không phạm luật 5.2.

**Lý do:** 6 triệu chứng trong 2.5 giây là 6 clip nhấp nháy — với dải trên đỉnh còn chịu được, nhưng với thẻ Broll Vip (khối hình lớn giữa khung) thì chóng mặt thật. Người dùng chốt sau khi xem bản test: *"nhịp này nhanh quá"*.

**Caption vẫn tách từng triệu chứng như cũ.** Chỉ lớp B-roll gộp đôi — một clip chạy liên tục qua hai nhịp caption, đúng luật 6d trong `technical.md`.

---

## 2. Bốn lỗi xác minh kinh điển

### 2.1 Đúng chủ đề nhưng sai cơ chế

**Lỗi thật** (video "Tư thế ngồi làm việc", đoạn 17-27s, nội dung "cúi 15° cổ chịu lực 12kg"): tìm bằng thuật ngữ trong transcript "cột sống cổ", ra một clip đồ họa cột sống có dây thần kinh phát sáng, xem một frame, thấy "đúng là cột sống" → chấp nhận. Nhưng khái niệm cần minh họa là **tải trọng cơ học** (lực do góc cúi đầu), không phải dẫn truyền thần kinh. Clip chỉ khớp phạm trù giải phẫu chung.

**Điều KHÔNG cứu được lỗi này**: cải thiện từ khóa tìm kiếm. Tìm kiếm văn bản luôn có thể trả về kết quả cùng phạm trù nhưng sai khái niệm.

**Điều cứu được**: đổi câu hỏi ở bước xác minh, từ câu hỏi lỏng *"clip này có liên quan chủ đề không?"* sang câu hỏi hẹp *"clip này có mô tả đúng CẢNH/HÀNH ĐỘNG cụ thể tôi đã tưởng tượng không?"*. Clip chỉ lân cận chủ đề (cùng bộ phận cơ thể, cùng lĩnh vực) mà không mô tả đúng cơ chế phải bị loại, không được chấp nhận là "gần đúng".

Kèm theo: trước khi tìm, hãy **diễn đạt cảnh lý tưởng thành lời cụ thể** — ví dụ "người quay nghiêng, đầu cúi dần về trước, đang nhìn màn hình" — rồi rút từ khóa từ cảnh đó, thay vì lấy thẳng thuật ngữ y khoa từ transcript.

### 2.2 Đúng chủ thể nhưng sai cảm xúc

**Lỗi thật** (video "Để sống khỏe thì làm gì", ~96s, caption "VẪN ĂN UỐNG HEALTHY HƠN"): chọn một clip người phụ nữ ăn salad vì chủ thể khớp. Nhưng tên file ghi rõ "vẻ mặt chán ghét" và footage cho thấy người này đang uể oải chọc đũa vào đồ ăn — **sắc thái cảm xúc ngược hoàn toàn** với thông điệp tích cực. Clip đó thực ra là clip đúng cho một ý khác: "chán ăn / ăn kiêng khắc nghiệt".

**Bài học**: khi caption mang sắc thái cảm xúc (tích cực/hào hứng vs. tiêu cực/miễn cưỡng), câu hỏi xác minh phải bao gồm cả **biểu cảm khuôn mặt và không khí**, không chỉ chủ thể. "Người ăn salad" không phải một ý — đó là ít nhất hai ý trái ngược tùy vào vẻ mặt.

### 2.3 Đúng file nhưng sai đoạn trong file

**Lỗi thật** (video "Tư thế ngồi làm việc"): một clip dài 26 giây tên "cầm điện thoại xem tin nhắn". Cảnh cầm điện thoại nằm ở giây 16-22, nhưng đoạn được render là 6.6 giây **đầu tiên** của file — vốn là cảnh vươn vai, không hề có điện thoại. Chọn file đúng, chỉ sai offset.

**Bài học có hai phần**:
- Khi native duration của file **dài hơn nhiều** so với thời lượng cần dùng, coi đó là dấu hiệu rủi ro cao: file có thể chứa nhiều cảnh khác nhau. Kiểm tra xem hành động cần thiết nằm ở **đâu** trong file trước khi tin vào một frame xác minh lấy ngẫu nhiên.
- Sau khi đặt clip, trích frame xác minh tại **đúng điểm bắt đầu sẽ render** (tính cả offset), không phải t=0 hay một điểm tùy ý. Một frame kiểm tra ở sai offset có thể trông "đã xác nhận ổn" trong khi bản render thật hiện cảnh hoàn toàn khác.

### 2.4 Bỏ qua câu vì hình thức, không vì nội dung

**Lỗi thật** (video "dây thần kinh phế vị"): câu mở đầu "đau vai gáy... đầy bụng khó tiêu không?" bị bỏ qua không chèn B-roll, vì nó khớp mẫu "câu hỏi mở đầu → thường là tu từ → không cần minh họa". Nhưng câu này nêu **hai triệu chứng cụ thể, hoàn toàn minh họa được**.

**Lỗi gốc**: áp luật bỏ qua dựa trên **vị trí/hình thức** của câu (nằm ở đầu, dạng câu hỏi) thay vì kiểm tra lại **nội dung thật** của nó.

**Cách phòng**: sau lượt quét ý lớn đầu tiên, làm thêm một lượt quét **từng câu một trên toàn bộ transcript** — kể cả câu mở đầu — chỉ hỏi đúng một câu: *"câu này có nêu tên một triệu chứng/cơ chế/nguyên nhân cụ thể nào không?"*, bất kể nó nằm ở đâu hay được diễn đạt thế nào.

---

## 3. Timing

B-roll phải bắt đầu **đúng tại từ khóa được nói**, sớm hơn tối đa 1-3 khung hình ở 60fps.

Timestamp cấp câu của Whisper quá thô — có thể lệch vài giây. Bắt buộc dùng `word_timestamps=True` và tra thời điểm của **chính từ kích hoạt**, độc lập với thời điểm bắt đầu của B-roll bao quanh nó (vốn thường sớm hơn và rộng hơn).

Lỗi đã gặp: caption hiện sớm hơn lời nói vì lấy mốc từ ranh giới segment thay vì mốc từ cụ thể được nhắc tới trong caption đó.

---

## 4. Tìm ở đâu

### Thứ tự ưu tiên
1. **`Đã Chuẩn Hóa/`** — kho người dùng tự đặt tên theo ý, tìm ở đây trước tiên. Tên file là các slug tiếng Việt mô tả rõ ý (`dau-dau-2,chong-mat,Roi-loan-tien-dinh.mp4`).
2. Thư mục chủ đề tương ứng (xem `product-map.md` để biết chủ đề nào ghép với sản phẩm nào).
3. **`Lộn Xộn Xà bần/`** — kho chưa phân loại, ~1650 file tên vô nghĩa. Chỉ tìm khi các kho khác không có.

### Rebuild catalog trước khi search
Catalog là snapshot tĩnh, không phải index sống. Bất kỳ file/thư mục nào thêm sau lần build cuối đều **vô hình** với search dù đã nằm trên ổ đĩa.

**Lỗi thật**: search "nano sụn" không ra kết quả → kết luận sản phẩm không có footage trong kho. Thực tế catalog build từ 2 ngày trước, còn thư mục sản phẩm mới được thêm sau đó. Kết quả rỗng là **mơ hồ** (thật sự không có vs. index cũ) trừ khi vừa rebuild.

Nếu giữa phiên làm việc mà search rỗng dù đã build một lần, build lại trước khi tin vào kết quả rỗng — người dùng có thể vừa thêm file.

### Xử lý file Unicode tiếng Việt
Khi so tên file có dấu, dùng chuẩn hóa NFC + lowercase khi so sánh với kết quả liệt kê thư mục. Tên hardcode trực tiếp có nguy cơ lệch NFC/NFD hoặc lệch hoa thường (ví dụ `Não-thiếu-năng-lượng.mp4` có chữ hoa) và thất bại âm thầm.

---

## 5. Hai luật cứng

### 5.1 Cấm tự sinh sơ đồ/hình minh họa

Người dùng đã thử một lần và bác bỏ dứt khoát: *"từ giờ cấm bạn tự sinh sơ đồ trừ khi bạn tạo được ảnh 3d người thật"*. Vì không có khả năng tạo ảnh chân thực trong môi trường này, đây thực tế là **lệnh cấm tuyệt đối** với mọi hình vẽ tự tạo (PIL, SVG, đồ họa thay thế).

Khi không có footage thật khớp khái niệm cụ thể: để đoạn đó là A-roll thuần + caption có animation. Không chế ra hình ảnh nào để lấp chỗ.

### 5.2 Không lặp lại clip (trừ sản phẩm)

**Lỗi thật** (video "Sụn khớp không biết kêu"): dùng lại clip "sụn tách rời" hai lần cho hai caption khác nhau, với lý lẽ "cùng một ý thì dùng lại cùng clip". Người dùng bác bỏ rõ ràng cho B-roll thường: kho đủ sâu (riêng "Xương khớp - Đau" có 99 file) nên việc lặp đọc ra là **lười**, không phải trung thành với ý.

Ngay cả khi một ý lặp lại, hãy tìm một clip thật **khác** mô tả ý đó. B-roll sản phẩm được **miễn trừ** — mỗi sản phẩm thường chỉ có một clip chính hãng, lặp lại là bình thường và đúng kỳ vọng.

**Cách áp dụng**: trước khi chốt danh sách B-roll, liệt kê mọi đường dẫn clip không-phải-sản-phẩm đã dùng và soát trùng.

**Định nghĩa "lặp" cho đúng**: các nhịp **liền nhau** dùng chung một file là MỘT đoạn liên tục (xem `technical.md` mục 6d) — đó là cách dựng đúng, không phải lặp. Chỉ tính là vi phạm khi cùng một clip xuất hiện ở hai vị trí **cách xa nhau** trong video. Bộ soát trùng phải phân biệt được hai trường hợp này, nếu không sẽ báo động giả hàng loạt.

---

## 6. Clip ưu tiên do người dùng chỉ định

Khi người dùng chỉ định một file cụ thể cho một ý, coi đó là **mặc định thường trực** cho ý đó ở mọi video sau, không chỉ lần đổi đó.

### Khi một ý xuất hiện nhiều lần trong CÙNG một video

Luật này và luật 5.2 (không lặp clip) từng đá nhau: video có ba lượt liệt kê triệu chứng thì "mất ngủ" xuất hiện ba lần — clip ưu tiên bảo dùng lại, luật 5.2 cấm lặp. Cách giải người dùng đã chốt:

- **Lần 1** ý đó xuất hiện → dùng **đúng clip đã chỉ định**.
- **Lần 2, 3, 4...** → tìm clip **khác có nội dung tương tự clip đã chỉ định**, không dùng lại clip cũ.

Nghĩa là clip ưu tiên định ra **chuẩn mực nội dung** cho ý đó, chứ không phải một file duy nhất được phép dùng. Các lần sau vẫn phải bám sát cảnh và sắc thái của clip gốc, chỉ đổi file.

Ví dụ: "mất ngủ" lần đầu dùng `chong-mat-mat-ngu,thieu-ngu,mat-ngu-1.mp4`; lần hai tìm một clip mất ngủ khác — vẫn là người nằm trằn trọc trên giường ban đêm, không được đổi sang cảnh ngáp ở văn phòng ban ngày.

Lưu ý: hai nhịp **liền nhau** dùng chung một clip là **một đoạn liên tục** (xem `technical.md` mục 6d), không tính là lần xuất hiện thứ hai.

Đã chốt:

| Ý | Clip ưu tiên |
|---|---|
| Mất ngủ | `Đã Chuẩn Hóa/chong-mat-mat-ngu,thieu-ngu,mat-ngu-1.mp4` |
| Ngủ ngon | `Ngủ- Ngon- mất ngủ/Chú 50-60 tuổi ngủ ngon.mp4` (người dùng chốt 17/08/2026 khi duyệt combo Raydel+Q10: "ngủ ngon thì ưu tiên clip này trước") |
| Ăn uống lành mạnh (vui vẻ, hào hứng) | `Ăn uống lành mạnh/ăn-uong-lanh-manh.mp4`, `Ăn uống lành mạnh/Thiết kế chưa có tên (15).mp4`, `Ăn uống lành mạnh/8845448-uhd_4096_2160_24fps.mp4` |
| Chán ăn / ăn kiêng khắc nghiệt (miễn cưỡng, khó chịu) | `Giảm cân - Mập, tăng cân/033 - Dùng nĩa xúc rau xà lách ăn, vẻ mặt chán ghét khi ăn.mp4`, `Đã Chuẩn Hóa/032 - Ngồi ăn món saladmì rau trộn bằng nĩa trong bếp, vẻ...mp4` |
| Cơ thể khỏe mạnh (ẩn ý qua hình ảnh vận động, nhất là người lớn tuổi) | `Thể dục thể thao/Thiết kế chưa có tên - 2024-12-20T115808.557.mp4` (đôi cô chú chạy bộ, tươi cười), `Thể dục thể thao/Thiết kế chưa có tên (3).mp4`, `Thể dục thể thao/Thiết kế chưa có tên - 2025-03-26T083741.007.mp4` |

Ghi chú về nhóm cuối: ý người dùng là hình ảnh người đang vận động đóng vai trò **phát biểu ngầm về một cơ thể khỏe mạnh** — ưu tiên nhóm này khi luận điểm là "cơ thể khỏe", thay vì khi câu chữ đang hướng dẫn "hãy tập thể dục".

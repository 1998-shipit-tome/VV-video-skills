# Ghi chú kỹ thuật render

Các quyết định và bug đã trả giá để tìm ra. Không lặp lại chúng.

## 1. Codec xuất file overlay

**Dùng ProRes 4444** (`prores_ks`, profile 4, pix_fmt `yuva444p10le`, fourcc `ap4h`).

**Không dùng HAP Alpha.** Đã thử và thất bại: file HAP không import được vào DaVinci Resolve trên Windows (nhiều khả năng thiếu component QuickTime/HAP). ProRes 4444 là định dạng Resolve hỗ trợ native, không cần cài thêm gì, và giữ kênh alpha chính xác.

Đánh đổi: ProRes 4444 rất nặng — video 5.4 phút cho ra file ~16GB. Khi chỉ cần bản cho người dùng xem duyệt, xuất preview nhẹ (ghép sẵn lên A-roll, scale 540x960, crf 28) thay vì đưa file overlay gốc.

## 2. Bẫy alpha channel trong ffmpeg

Chuỗi `format=yuva444p10le` **phải nằm cùng một chuỗi filter lavfi** với nguồn `color=...@0.0`, ví dụ:

```
color=black@0.0:s=1080x1920:r=60,format=yuva444p10le
```

**Không** tách ra thành option `-vf` riêng phía sau. Nếu tách, giá trị alpha bị âm thầm loại bỏ (đặt về 255 = đục hoàn toàn) dù pix_fmt trên danh nghĩa vẫn hỗ trợ alpha. Lỗi này rất khó phát hiện vì file xuất ra trông "đúng định dạng".

Cách kiểm chứng đã dùng: ghép một đoạn trong suốt và một đoạn đục, overlay lên nền đỏ. Làm đúng thì nền đỏ xuyên qua đoạn trong suốt; làm sai thì ra khối đen đặc.

## 3. Ghép track — dùng concat theo frame, không dùng enable/between

Dựng track B-roll và track caption **độc lập**, mỗi track ghép bằng cách nối chính xác theo frame các đoạn trong suốt (gap) với các đoạn có nội dung. Sau đó overlay hai track lên một nền trong suốt.

Không dùng cơ chế bật/tắt theo thời gian (`enable=between(...)`) — đã chứng minh gây giật hình.

## 4. Offset điểm bắt đầu trong file nguồn

Mỗi clip B-roll cần một tham số **offset điểm bắt đầu lấy từ nguồn** (không phải vị trí trên timeline).

Bug đã gặp: ban đầu hàm cắt clip không có tham số này, luôn lấy từ giây 0 của file nguồn bất kể cảnh cần dùng nằm ở đâu. Hậu quả: một clip 26 giây có cảnh cầm điện thoại ở giây 16-22 lại render ra 6.6 giây đầu (cảnh vươn vai, không có điện thoại) — chọn đúng file, sai đoạn.

Đây là lỗi **hệ thống**, không phải một lần: nó ảnh hưởng mọi clip trong pipeline cho tới khi được sửa.

## 5. Clip nguồn ngắn hơn thời lượng cần

Nếu (native duration − offset) < thời lượng cần, phải **loop nguồn** (`-stream_loop -1`). Không làm thì thiếu frame — đã từng hụt ~291 frame trong một bản render vì clip nguồn chỉ 5.2s mà cần 10.05s.

## 6. Dải B-roll

- Chiều cao dải trên: **608px** trên khung 1080x1920 (~32% chiều cao).
- Mép dưới của dải: **cắt thẳng**, không xử lý gì thêm.
- Caption bám ngay dưới mép dải: `y = chiều cao dải + 10`. Đổi chiều cao dải thì **bắt buộc dựng lại cả track caption**.

Vì sao 608 chứ không phải 672 như bản đầu: 608 là đúng 16:9 ở bề ngang 1080. Kết hợp với luật 6b (phóng vừa bề ngang), nguồn 16:9 lấp khít dải mà **không mất một pixel bề ngang nào**. Nếu để dải 672px thì muốn lấp kín phải phóng lên 1194px rồi cắt 114px bề ngang — vi phạm chính luật 6b. **Chiều cao dải và luật scale bị ràng buộc với nhau, đổi cái này phải xét cái kia.**

### 6b. Dải phải KÍN KHUNG — không bao giờ có viền đen

Cách làm đúng: **phóng cho vừa bề ngang** (`scale=1080:-1`) rồi **cắt bớt trên/dưới** cho khớp chiều cao dải. Không bao giờ dùng `force_original_aspect_ratio=decrease` + `pad` cho dải.

- Nguồn 16:9 (93% kho): vừa khít, không mất gì.
- Ảnh/clip sản phẩm dạng đứng hoặc vuông: cắt bớt trên dưới — hộp sản phẩm luôn nằm giữa khung nên không mất nội dung.
- **Clip dọc 9:16: hiện không dùng.** Phóng vừa bề ngang sẽ cắt mất ~68% chiều cao, không có cách nào vừa kín khung vừa giữ đủ nội dung. Người dùng đã chốt: *"hiện tại tôi không dùng broll dọc"* — khi nào cần sẽ tự bổ sung và yêu cầu riêng. Đến lúc đó phải hỏi lại, đừng tự chọn cách xử lý.

Đã sai một lần: hiểu "không xén B-roll" thành fit-toàn-khung rồi pad đen, kết quả **18.9% thời lượng dải có hai dải đen hai bên**, nặng nhất đúng ở ảnh sản phẩm (combo 176s, Raydel Policosanol 2 111s). Người dùng chỉ ra ngay: *"cái broll sản phẩm này đáng lẽ bạn phải zoom lên để vừa bề ngang khung hình nhưng lại để nó đen 2 bên"*.

Hiểu cho đúng ý "không xén": **không được cắt bề NGANG**. Cắt bớt trên/dưới để lấp đầy khung là chấp nhận được và bắt buộc.

## 6c. Tỉ lệ phóng: TĨNH và lấp kín khung — cấm phóng THEO THỜI GIAN

Tách rõ hai khái niệm vì chúng từng dùng chung một chữ "zoom" và gây hiểu ngược:

- **Tỉ lệ phóng tĩnh** — chọn một lần, giữ nguyên suốt đoạn, chọn sao cho lấp kín khung theo luật 6b. Ảnh sản phẩm dạng đứng **buộc phải** phóng lên cho vừa bề ngang. Đây là bắt buộc, không phải "zoom".
- **Phóng thay đổi theo thời gian** — Ken Burns, push-in dần, đẩy máy vào. Đây là thứ **bị cấm**.

Câu của người dùng *"đáng lẽ bạn phải zoom lên để vừa bề ngang khung hình"* nói về vế thứ nhất, không nghịch với lệnh cấm ở vế thứ hai.

Đã sai một lần: lấy `kenburns: 1.13` từ preset của skill `vertical-topband-video` — một skill KHÁC — rồi áp vào đây. **Cấm mượn tham số mặc định từ skill khác.** Nếu file này không nói gì về một tham số, hỏi người dùng, đừng đi mượn.

## 6d. Một clip trải qua nhiều ý phải CHẠY LIÊN TỤC

Các nhịp caption liền nhau dùng CÙNG một file phải gộp thành **một đoạn duy nhất**, lấy mốc vào của nhịp đầu. Clip chạy xuyên suốt, không tua lại ở mỗi ranh giới ý.

Đã sai một lần: dựng mỗi nhịp caption thành một đoạn riêng vì tiện cho code — sinh ra **317 chỗ clip bị tua lại giữa chừng** trên 8 video. Người dùng phải tự phát hiện.

Ba hệ quả phải nhớ, nếu không sẽ hiểu luật này ngược với các luật khác:

**Không nghịch với "một ý = một clip".** Luật đó nói về khâu **chọn** — mỗi ý đi tìm clip riêng, đừng gom nhiều ý vào một clip cho tiện. Luật 6d nói về khâu **dựng** — khi một clip đã hợp lệ trải qua nhiều nhịp thì đừng tua lại nó. Chọn thì tách, dựng thì liền.

**Không tính là lặp clip.** Bộ soát trùng phải coi các nhịp **liền nhau** dùng chung một file là **một đoạn**, không phải hai lần dùng. Chỉ khi cùng một clip xuất hiện ở hai vị trí **cách xa nhau** mới là vi phạm luật 5.2 trong `broll-rules.md`.

**Luật canh timing chỉ áp cho đầu đoạn.** Yêu cầu "B-roll vào đúng tại từ khóa, sớm tối đa 1-3 frame" áp cho điểm bắt đầu của đoạn. Các nhịp caption thứ hai trở đi bên trong đoạn không có điểm vào mới — đó là điều mong muốn, không phải lỗi timing.

## 6dd. Bắc cầu khoảng trống — KHÔNG được nuốt nhịp cố ý bỏ trống

Phân biệt **hai** tình huống, đừng gộp làm một:

**Hai B-roll đứng LIỀN NHAU** (không có nhịp bỏ trống nào chen giữa) → **LUÔN kéo dài
clip trước tới đúng frame bắt đầu của clip sau. Không ngưỡng, không ngoại lệ.** Chỉ cần
hở một frame là mắt thấy giật. Người dùng chốt: *"đừng để giữa 2 broll liền nhau có
frame bị trống gây giật hình"*.

**Có nhịp CỐ Ý bỏ trống chen giữa** → đó là quyết định biên tập, giữ nguyên khoảng
trống, không bắc cầu (xem bên dưới).

Ngưỡng 1.2 giây trước đây gộp chung hai tình huống nên vừa bắc cầu nhầm qua nhịp cố ý
bỏ trống, vừa bỏ sót lỗ hở giữa hai clip liền nhau khi lỗ đó rộng hơn ngưỡng.

**Nhưng tuyệt đối không bắc cầu qua một nhịp mà biên tập CỐ Ý bỏ trống B-roll.** Nhịp để trống là một quyết định biên tập, máy không được ghi đè.

Đã sai một lần: luật bắc cầu nuốt mất 2 nhịp, trong đó có nhịp "MỠ MÁU CAO" ở V3 mà chính người dùng yêu cầu thêm vào — lớp B-roll của nó bị clip liền trước phủ lên.

Cách làm đúng: chỉ xét bắc cầu khi khoảng trống nằm **giữa hai đoạn có B-roll**, và trong khoảng đó **không có nhịp nào có caption mà cột B-roll để trống**.

## 6e. Nhịp frame nguồn — nguyên nhân lỗi nặng nhất đã gặp

Hầu hết clip trong kho là **30fps**, khung dựng là 60fps. Phải có bộ lọc `fps=60` **thật** trong chuỗi lọc. Tham số `fps=` bên trong `zoompan` chỉ *gắn nhãn* nhịp frame, **không nhân đôi frame**.

Thiếu nó thì `-frames:v n` ngốn n frame NGUỒN (= n/30 giây) thay vì n/60 giây, gây hai hậu quả cùng lúc:
1. **B-roll chạy nhanh gấp đôi** — frame tĩnh không thể phát hiện, sống sót qua nhiều vòng kiểm tra.
2. Clip nào hết frame giữa chừng thì đoạn bị ngắn, thiếu hụt **cộng dồn làm trôi cả track dải** về trước.

Phép thử bắt được ngay: đếm số frame mỗi đoạn dựng ra, so với số frame yêu cầu. Phải bằng nhau tuyệt đối.

## 6h. Hai bố cục B-roll — "Broll Top" và "Broll Vip"

Dự án có **hai** bố cục, gọi tên rõ để khỏi lẫn:

| | **Broll Top** | **Broll Vip** |
|---|---|---|
| Vị trí | dải ghim sát mép trên, tràn hết bề ngang | thẻ nổi ở nửa dưới, chừa lề hai bên |
| Kích thước | 1080 × 608 | 918 × 516 tại (81, 1056) |
| Hình khối | cắt thẳng bốn cạnh, không viền | bo góc 40px, viền trắng 11px |
| Vùng bị che | mái che / nền phía trên đầu | thân và tay người nói |
| Caption | bám mép dưới dải (y = 618) | nằm PHÍA TRÊN thẻ, không đè |

Mọi luật về scale (6b), cấm zoom theo thời gian (6c), clip chạy liên tục (6d),
nhịp frame nguồn (6e) áp **cho cả hai bố cục**.

### Broll Vip — thông số đầy đủ

| Tham số | Giá trị |
|---|---|
| Thẻ | 918 × 516 (85% bề ngang, đúng 16:9) |
| Vị trí | x = 81 (canh giữa), y = 1056 (mép trên ở 55% chiều cao) |
| Bo góc | 40px |
| Viền trắng | 11px |
| Xuất hiện | phóng 0.92 → 1.0 kèm hiện dần, **14 frame**, `ease_out_cubic` |
| Chuyển cảnh | **push cả viền** sang trái, **12 frame**, `ease_in_out_cubic`, khe hở 36px |

**Số đo thẻ vẫn là ƯỚC LƯỢNG** đọc từ ảnh chụp màn hình, chưa đo từ file gốc.

### Caption của Broll Vip: neo theo MÉP DƯỚI, nằm trên thẻ

Người dùng chốt: *"phần caption bạn làm nằm phía trên không đè lên broll"*.

Neo theo **mép dưới** khối chữ, cách mép trên thẻ 20px — tức `đáy chữ = CARD_Y − 20`,
khối chữ mọc **lên trên**. Khác hẳn Broll Top (neo theo tâm, mọc xuống dưới).

Vì sao phải neo mép dưới chứ không neo tâm: neo tâm thì khối 2 dòng cao hơn sẽ
thò xuống và **đè lên thẻ**. Neo mép dưới thì caption 1 dòng hay 2 dòng đều kết
thúc ở cùng một đường, không bao giờ chạm B-roll — đúng yêu cầu, bất kể chữ dài
ngắn thế nào.

### Vẽ viền: vòng viền phải TRÙNG BIÊN với mặt nạ

Vòng viền là hình **ĐẶC** = bo góc ngoài (bán kính R) **trừ** bo góc trong
(bán kính R−B, thụt vào B). Biên ngoài của vòng viền trùng khớp tuyệt đối với
biên của mặt nạ. Vẽ ở **4×** rồi thu nhỏ để khử răng cưa.

**Lỗi đã gặp**: mặt nạ vẽ trên `[0,0,W,H]` còn vòng viền vẽ trên `[B/2,…,W−B/2]`
— hai đường cong khác nhau nên **B-roll thò ra ngoài mép trắng ở góc bo**, viền
lại răng cưa. Người dùng phát hiện: *"viền bạn vẽ cái broll nó vẫn còn lộ ra"*.

### "Push cả viền" khác "push nội dung"

- **Push cả viền** (đang dùng): hai **thẻ hoàn chỉnh** — mỗi thẻ mang viền và bo
  góc riêng — trượt ngang cạnh nhau, giữa chúng lộ ra nền A-roll.
- **Push nội dung**: khung đứng yên, chỉ ảnh bên trong trượt.

Hai kiểu nhìn rất khác nhau. Người dùng chọn **push cả viền**.

### Dựng hoạt ảnh: PIL từng frame, không phải ffmpeg overlay

Hoạt ảnh cần đổi tỉ lệ và độ mờ theo từng frame nên dựng **từng frame lớp thẻ
bằng PIL** rồi mới overlay lên A-roll. Mặt nạ áp **sau** khi ghép hai clip, nhờ
vậy góc bo giữ nguyên suốt lúc trượt.

Cảnh báo quy mô: clip test 2.75s = 166 frame, PIL chạy vài giây. Video 6 phút =
~23.000 frame — lúc đó phải dựng frame **chỉ cho các đoạn có hoạt ảnh**, còn
đoạn tĩnh để ffmpeg lo.

**Bẫy**: đưa ảnh vào bằng `-loop 1` mà không đặt `-frames:v` thì ffmpeg **chạy
vô tận** — ảnh lặp không có điểm dừng.

## 6f. Kiểm tra bản dựng — frame tĩnh là KHÔNG ĐỦ

Frame tĩnh mù trước bốn thứ: tốc độ phát, clip có bị tua lại hay không, trôi dồn tích luỹ, và hiệu ứng zoom. Cả bốn lỗi đó đều đã lọt qua nhiều vòng "đã kiểm tra đạt" chỉ vì chỉ soi ảnh tĩnh.

Trước khi báo xong, bắt buộc chạy và dán kết quả các phép đo sau:

1. Số frame **mỗi đoạn** dựng ra == số frame yêu cầu (bắt lỗi 2x và lỗi trôi).
2. Tổng frame bản dựng == tổng frame A-roll (bắt lỗi hụt frame ở mối nối).
3. Số chỗ một clip bị tua lại giữa chừng == 0.
4. Kích thước dải và chế độ scale đúng như mục 6b.
5. Không clip lặp ở vị trí xa nhau, không frame đen, không nhịp chồng thời gian.

Cẩn thận: **công cụ kiểm tra cũng có thể sai**. Đã gặp hai lần trong một phiên — khoá cache ảnh xem trước bị cắt ngắn làm mọi mốc giây của cùng một file dùng chung một ảnh; và bộ lọc crop trả về khung đen với clip rộng hơn 16:9 làm loại oan clip tốt. Khi công cụ soi hỏng thì mọi kết luận "đạt" đều vô giá trị. Nếu một phép kiểm báo lỗi hàng loạt, nghi ngờ phép kiểm trước khi nghi ngờ bản dựng.

## 6g. Render thử — chỉ với dạng video CHƯA TỪNG dựng

(Người dùng sửa luật ngày 17/08/2026.) Nếu **dạng video sản phẩm chưa từng dựng** (sản phẩm mới, bố cục mới): render đúng **một** video cho người dùng xem trước, đạt rồi mới render phần còn lại — một sai lầm hệ thống nhân với 8 video là mất cả buổi.

Nếu **dạng video đã từng dựng và được duyệt** (ví dụ combo đã có video mẫu duyệt style): sau khi người dùng chốt bảng duyệt thì render thẳng cả loạt, **không cần** bước render thử.

Cổng duyệt bắt buộc trước mọi render là **bảng duyệt HTML** (`4_make_table.py`) — xem quy trình ở SKILL.md. File giao sau render: `_broll_overlay.mov` (bật `--overlay`) + `caption.mov`, kèm preview nhẹ đã ghép.

## 7. Tránh chạy chồng tiến trình render

Chỉ chạy **một** tiến trình render tại một thời điểm. Đã có lần vô tình chạy hai lệnh render chồng lên nhau (tưởng lệnh đầu không chạy vì output rỗng) — hai tiến trình giẫm lên nhau, ghi cùng thư mục tạm, treo máy nhiều giờ và phải kill thủ công.

Nếu lệnh render có vẻ không phản hồi, **kiểm tra tiến trình đang chạy trước** khi khởi động lại lệnh mới.

## 8. Môi trường

- Python 3.12 cho mọi thao tác liên quan pipeline. Python 3.11 (mặc định trong PATH) crash khi import thư viện DaVinci Resolve.
- Whisper: `faster_whisper`, model `medium`, `language="vi"`, `vad_filter=True`, **`word_timestamps=True`** (bắt buộc — xem lý do trong `broll-rules.md` phần timing).
- Xuất log/stdout tiếng Việt: đặt encoding UTF-8, nếu không sẽ lỗi `UnicodeEncodeError` với codepage mặc định của Windows.

## 9. Bug tìm kiếm catalog (đã sửa, ghi lại để tham chiếu)

Hàm tìm kiếm B-roll từng dùng phép so khớp **chuỗi con thô** làm phương án dự phòng, cho phép khớp xuyên qua ranh giới từ. Ví dụ tìm "ô tô" (chuẩn hóa thành "o to") lại khớp nhầm vào "mỡ **tố**t trong máu" vì chuỗi "o to" nằm vắt ngang giữa "mỡ" và "tốt".

Đã sửa bằng cách bỏ hẳn nhánh chuỗi con, chỉ giữ kiểm tra biên từ. Nếu gặp kết quả tìm kiếm vô lý trong tương lai, kiểm tra lại logic so khớp trước khi nghĩ tới việc đổi tên hàng nghìn file.

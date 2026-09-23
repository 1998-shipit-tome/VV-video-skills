# Quy trình dựng video DiLiM — phần dùng chung cho cả hai bố cục

> File này là **lõi dùng chung** của hai skill `broll-top` và `broll-vip`.
> Sửa ở đây là cả hai bố cục cùng đổi. Đừng chép nội dung file này vào SKILL.md
> của từng bố cục — hai bản chép tay sẽ lệch nhau, đã từng xảy ra.

## Mở phiên mới — đọc trước khi làm bất cứ gì

Hai skill `broll-top` và `broll-vip` nạp tự động ở **mọi** thư mục (junction trong `~/.claude/skills/`). Người dùng không cần mở đúng folder nào.

Nơi chứa đồ:

| Nơi | Chứa gì |
|---|---|
| `D:\claude-editer-video\.claude\skills\_broll-core\` | **LÕI DÙNG CHUNG** — `scripts/` (render, qc, preset) + `references/` (luật). Đây là bản duy nhất. |
| `...\skills\broll-top\` · `...\skills\broll-vip\` | chỉ có `SKILL.md`; `scripts/` và `references/` là junction trỏ về lõi |
| `D:\tinh-media-workflow\pipeline\` | catalog kho B-roll, transcribe, `4_make_table.py` (bảng duyệt HTML) |
| `D:\tinh-media-workflow\jobs\<tên>\` | file làm việc của **một** video: `plan.json`, `words.json` |

⚠️ `D:\tinh-media-workflow\skills\dilim-video-broll\` là **bản cũ mồ côi** (03/08). Không đọc, không sửa, không lấy luật từ đó.

⚠️ Skill `vertical-topband-video` cũng nạp trong mọi phiên và có preset **zoom Ken Burns**. Đã một lần mượn nhầm tham số của nó và phải dựng lại 8 video. Bố cục DiLiM **không zoom** — mọi con số lấy từ `scripts/preset.json`, không lấy từ skill khác.

⚠️ **Không tạo symlink bằng `ln -s` trong Git Bash trên máy này** — nó âm thầm COPY thay vì tạo link, và bản sao sẽ lệch khỏi lõi mà không ai biết. Dùng `cmd /c mklink /J <link> <đích>` (junction, không cần quyền admin). Kiểm tra bằng `test -L` hoặc `fsutil reparsepoint query`.

## B-roll tồn tại để làm gì

Trước mọi luật lệ bên dưới, hiểu điều này: **B-roll không phải để trang trí, mà để người xem HÌNH DUNG ĐƯỢC điều đang nghe.** Một video dài chứa rất nhiều ý riêng biệt; mỗi ý cần đúng một hình ảnh minh họa cho riêng nó.

Vai trò thứ hai quan trọng không kém: **giữ nhịp**. Cứ vài giây nên có một điểm nhấn mới (chữ, B-roll, hoặc cả hai). Một đoạn dài không có gì thay đổi trên màn hình sẽ khiến người xem rời đi, dù lời nói vẫn đang hay. Mắt người bị hút bởi chuyển động trong khung hình tĩnh — nên khi không có clip nào khớp, **caption có animation vẫn đủ giữ nhịp**; đừng bỏ trắng cả hai lớp.

Hai vai trò này kéo về hai hướng ngược nhau (chính xác vs. dày đặc), và phần lớn sai lầm trong dự án này đến từ việc nghiêng quá về một phía. Cách giải quyết không phải là thỏa hiệp ở giữa, mà là **tìm kỹ hơn**: nâng ngưỡng "đã tìm đủ" lên cao, giữ nguyên ngưỡng "đủ chính xác để dùng".

## Quy trình làm việc với người dùng (chốt 17/08/2026)

1. Người dùng gửi source A-roll → hỏi bố cục (`top` hay `vip`) nếu chưa rõ → `catalog.py update` → transcribe → plan.
2. Sinh **bảng duyệt HTML** (`4_make_table.py`: lời thoại gốc + caption + màu + ảnh B-roll đúng khung render + SFX + ghi chú) và gửi người dùng. **Không render trước khi có bảng duyệt đã chốt.**
3. Người dùng sửa bảng, bấm "Tải quyết định (JSON)" gửi lại → đọc từng thay đổi, **xác nhận lại các thay đổi và nêu chỗ thắc mắc** cho người dùng chốt.
4. Người dùng chốt → render → `qc.py` → giao **file overlay của B-roll (`--overlay`, alpha thật) + file caption.mov**, kèm bản preview nhẹ đã ghép để xem nhanh.

**Luật render thử:** chỉ áp dụng cho **dạng video sản phẩm CHƯA TỪNG dựng** — khi đó render đúng 1 video cho người dùng xem trước, đạt rồi mới render phần còn lại. Sản phẩm/dạng video **đã từng dựng và được duyệt** (ví dụ combo đã có video mẫu duyệt style) thì sau khi chốt bảng duyệt được render thẳng cả loạt, không cần bước thử. (Luật cũ "dựng thử 30s cho mọi video" đã được người dùng thay bằng luật này.)


## Quy trình

### Bước 0 — Chuẩn bị
- Catalog kho B-roll: chạy `python pipeline/catalog.py update` (chỉ quét file mới/mất, in ra vài dòng). **Không** rebuild toàn bộ mỗi phiên — tốn thời gian mà kết quả như nhau. Chỉ rebuild full khi catalog hỏng hoặc người dùng đổi cấu trúc thư mục lớn. Nhưng **phải** update trước khi search: đã có lần "kho không có footage sản phẩm này" hóa ra chỉ vì catalog cũ hơn ổ đĩa 2 ngày.
- Transcribe với **word-level timestamps**. Timestamp cấp câu lệch tới vài giây, không dùng được để canh điểm chèn.
- Lấy duration/fps → tính tổng số frame.

### Bước 1 — Nhận diện sản phẩm (nếu video có nhắc)
Đọc transcript, xác định chính xác sản phẩm hoặc combo được nhắc. Nhiều video bán 2-3 sản phẩm cùng lúc.

Tra bảng ghép sản phẩm ↔ thư mục trong `product-map.md`. Trong đó cũng có phần nhận diện **giọng văn kịch bản (A hay B)** — làm ngay ở bước này vì nó quyết định cách viết caption ở bước 2.

Ba điều bắt buộc:
- B-roll sản phẩm **chỉ** lấy từ đúng thư mục sản phẩm đó trong `Product Broll`. Không dùng sản phẩm khác thay thế dù trông tương tự — người xem nhận ra ngay và nó phá vỡ độ tin cậy của cả video.
- Kiểm tra **cả ba** thư mục con `Video/`, `Nguyên Liệu/`, `Ảnh/`. Thư mục `Nguyên Liệu/` thường chứa các clip bubble riêng cho từng thành phần — cực kỳ hữu ích cho đoạn liệt kê thành phần, và rất dễ bị bỏ sót nếu chỉ nhìn `Video/`.
- Nếu thư mục sản phẩm trống hoặc quá sơ sài: crop lại chính cảnh presenter cầm hộp thật trong A-roll làm B-roll. Không tự vẽ, không tạo hình giả (xem luật cấm sơ đồ trong `broll-rules.md`).

### Bước 2 — Cắt caption
Bám sát ranh giới câu/cụm **thật** trong transcript. Đừng gộp các ý cách xa nhau vào một caption chỉ vì chúng cùng chủ đề — mỗi câu ngắn tự nhiên trong lời nói là một điểm có thể chèn B-roll, gộp lại là tự đánh mất điểm chèn.

Với mọi danh sách liệt kê dồn dập (triệu chứng, thành phần, các bước), tách **mỗi item thành một nhịp caption riêng**. "Đau đầu, vai gáy, chóng mặt, mất ngủ, tê bì, tiền đình" không phải một ý — đó là sáu ý, sáu nhịp caption.

**Nhưng lớp B-roll thì khác:** với danh sách **triệu chứng** đọc dồn dập (mỗi item dưới nửa giây), gộp **2 triệu chứng dùng chung 1 clip** và chỉ minh hoạ một vế — sáu clip nhấp nháy trong 2.5 giây là quá nhanh. Bảng cụm ưu tiên và cách đảo vế khi danh sách lặp lại nằm ở `broll-rules.md` mục 1.

Nếu một câu là **phép ẩn dụ** (rỉ sét, dòng kênh bị bồi lắng, xe hơi thiếu dầu, gạo xay qua rây) chứ không phải mô tả y khoa, hãy tìm B-roll minh họa đúng **cái được ví von**, không phải nội dung y khoa tương ứng. Video mẫu của DiLiM làm điều này rất rõ: nói "quét sơn chống rỉ sét" thì chèn cảnh thanh sắt rỉ thật.

Chi tiết cách viết caption theo từng giọng văn: `product-map.md`.

### Bước 3 — Tìm B-roll
**Tưởng tượng cảnh lý tưởng trước, rồi mới tìm.** Đừng nhảy thẳng vào từ khóa lấy từ transcript — thuật ngữ y khoa trong lời nói thường dẫn tới clip cùng chủ đề nhưng sai cơ chế.

Khi thư mục có nhiều lựa chọn (kho "Xương khớp - Đau" có tới 99 file), **thực sự mở nhiều ứng viên ra xem**. Đọc tên file rồi chọn đại là nguyên nhân trực tiếp của lần dựng thất bại nhất trong dự án: chỉ dùng 5/99 clip có sẵn, để trắng phần lớn các đoạn nói về đau khớp trong khi kho thừa clip phù hợp.

Một file B-roll dài nhiều cảnh (video nghiên cứu sản phẩm 115s, bộ clip bubble thành phần) nên được **cắt thành nhiều đoạn nhỏ** dùng ở nhiều thời điểm khác nhau, không dùng nguyên một đoạn dài trải qua nhiều ý.

**Không lặp lại cùng một clip không-phải-sản-phẩm trong cùng một video.** Ý lặp lại thì tìm clip thật khác — kho đủ sâu để làm được, và chính video mẫu của người dùng cũng không bao giờ lặp. B-roll sản phẩm được miễn trừ (thường chỉ có một clip chính hãng).

Nếu đã tìm nghiêm túc mà vẫn không có clip khớp thật: **để trống**. Không hạ chuẩn để lấp chỗ.

### Bước 4 — Xác minh từng clip
Đây là bước hay bị bỏ qua khi đang vội tăng mật độ, và cũng là nơi mọi lỗi nghiêm trọng đã xảy ra. Bốn câu hỏi, phải trả lời được cả bốn:

1. Clip này có đúng **cảnh cụ thể** tôi đã tưởng tượng không? (không phải "có cùng chủ đề không")
2. **Biểu cảm/không khí** có khớp sắc thái caption không? Cùng một người ăn salad, vẻ mặt vui và vẻ mặt chán là hai ý hoàn toàn trái ngược.
3. Tôi đã xem frame tại **đúng điểm sẽ render thật** chưa (tính cả offset trong file nguồn)? So native duration với needed duration trước — file dài hơn nhiều so với đoạn cần dùng là dấu hiệu nó chứa nhiều cảnh khác nhau.
4. Điểm chèn có trùng **đúng từ được nói** không (sớm tối đa 1-3 frame ở 60fps)?

Chi tiết từng lỗi thật đã gặp và cách phòng: `broll-rules.md`.

### Bước 5 — Màu caption theo ý nghĩa
Màu không xoay ngẫu nhiên — nó mang nghĩa:
- **Đỏ** → ý tiêu cực: triệu chứng, cảnh báo, rủi ro, hậu quả.
- **Xanh lá** → ý tích cực: lợi ích, kết quả tốt, lối sống khỏe mạnh.
- **Trắng/vàng đậm** → nhắc sản phẩm, thành phần, chứng nhận, giá. **Không dùng đỏ hoặc đen** ở bất kỳ vị trí nào trong nhóm này.
- CTA đóng video có style riêng.

Gán màu rõ ràng cho **mọi** caption. Để rơi vào vòng xoay mặc định là cách sinh ra lỗi chữ vàng trên nền trắng (không đọc được) mà người dùng đã phải chỉ ra.

Bảng màu đầy đủ, format markup, quy tắc vị trí: `caption-style.md`.

### Bước 6 — Render và kiểm tra
Chi tiết kỹ thuật (codec, alpha channel, kích thước dải B-roll): `technical.md`.

Sau khi render, trích frame kiểm tra tại **từng** điểm B-roll/caption mới — không chỉ vài mẫu — và thực sự xem từng frame đó, đối chiếu với cảnh đã tưởng tượng ở bước 3.

Báo cáo trung thực: chỉ rõ đoạn nào để trống và vì sao. Nếu phát hiện lỗi trong chính công việc mình vừa làm, nói ra trước khi người dùng phải tự tìm thấy.


## Nguyên tắc xuyên suốt

**Không tự tạo hình ảnh minh họa.** Không vẽ sơ đồ PIL/SVG, không dựng đồ họa thay thế. Đây là luật cứng do người dùng đặt ra sau khi từ chối một sơ đồ tự vẽ. Khi không có footage thật khớp: để trống lớp B-roll, giữ caption.

**Tăng mật độ bằng cách tìm kỹ hơn, không phải bằng cách hạ chuẩn.** Đây là câu tóm gọn toàn bộ skill này. Nếu thấy mình đang tự thuyết phục rằng một clip "cũng tạm được", dừng lại — hoặc tìm tiếp, hoặc để trống.

**Đọc file reference khi cần, đừng đoán.** Bảng sản phẩm và các luật chi tiết tồn tại vì trí nhớ về chúng dễ trôi; tra lại rẻ hơn nhiều so với dựng lại cả video.


## Bảy phép kiểm của `qc.py`

Mỗi phép sinh ra từ **một lỗi thật đã từng giao nhầm cho người dùng**:

1. plan sạch — không lặp clip xa nhau, không chồng lấn thời gian, markup `*` cân đối
2. mỗi đoạn ra **đúng** số frame yêu cầu → bắt lỗi B-roll chạy 2× và lỗi trôi dồn
3. tổng frame bản dựng bằng A-roll → bắt lỗi hụt frame ở mối nối
4. không có chỗ clip bị tua lại giữa chừng
5. kích thước và chế độ scale đúng preset
6. **độ sáng thẻ khớp clip gốc** → bắt lỗi `overlay` lên nền trong suốt làm tối hình
7. caption cắt thẳng không fade, và không đè lên thẻ

`qc.py` báo lỗi **không phải lúc nào cũng là hỏng** — đôi khi là sai lệch có lý do, ví dụ kho hết clip nên buộc phải lặp. Nhưng phải **quyết định có ý thức**, không được lờ đi.

Và nhớ: **công cụ kiểm tra cũng có thể sai** — đã gặp năm lần trong một phiên. Nếu một phép kiểm báo lỗi hàng loạt, nghi phép kiểm trước khi nghi bản dựng.



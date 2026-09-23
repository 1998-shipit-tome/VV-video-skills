# Lỗi thường gặp

Mọi mục dưới đây là lỗi thật đã xảy ra khi xây và chạy skill này, kèm nguyên nhân gốc.

## ffmpeg đứng im, không báo lỗi, không kết thúc

**Nguyên nhân:** `zoompan` nhận luồng có framerate khác framerate đích. Filter treo vô hạn, không phát ra lỗi, tiến trình chỉ ngồi im. Rất dễ tưởng là "render chậm" và chờ vô ích.

**Cách sửa:** chuẩn hoá `fps=` **trước** `zoompan` trong chuỗi filter. `build.py` đã làm; nếu bạn tự viết filtergraph thì phải nhớ.

**Cách nhận ra:** một segment mất hàng phút trong khi các segment tương tự xong trong dưới 1 giây. Chạy riêng lệnh ffmpeg của segment đó với `timeout 60` để xác nhận.

## Chữ tiếng Việt ra ô vuông hoặc dấu hỏi

**Nguyên nhân:** font thiếu ký tự dấu. Bebas Neue và Impact là hai thủ phạm hay gặp nhất — chúng có đúng cái look condensed đậm mà format cần nên rất hay bị chọn.

**Cách sửa:** dùng Anton (mặc định), Be Vietnam Pro Black, Montserrat Black hoặc iCiel Koni Black. Kiểm tra trước khi render:

```bash
python scripts/check_font.py "C:/Windows/Fonts/YourFont.ttf"
python scripts/check_font.py --scan
```

Lỗi này chỉ lộ ra sau khi render xong cả video, nên kiểm tra trước rẻ hơn nhiều.

## `drawtext` làm ffmpeg segfault

**Triệu chứng:** `Fontconfig error: Cannot load default config file` rồi `Segmentation fault`.

**Nguyên nhân:** một số build ffmpeg trên Windows không kèm cấu hình fontconfig mà `drawtext` cần.

**Cách sửa:** đừng dùng `drawtext` cho caption. Skill này dùng ASS + `subtitles` (libass) — vốn mạnh hơn hẳn vì làm được animation, và không dính lỗi này. Nếu chỉ cần dán nhãn debug lên frame thì dùng PIL thay vì drawtext.

## Caption biến mất trong bản render

**Nguyên nhân:** filter `subtitles` bị đặt trước một overlay nào đó, và overlay đè lên chữ. Video vẫn render thành công — đây là lỗi im lặng.

**Cách sửa:** `subtitles` phải là filter **cuối cùng** trong chuỗi, sau mọi overlay kể cả logo.

## `subtitles` không tìm thấy file trên Windows

**Nguyên nhân:** trong filtergraph, dấu `:` phân tách tham số, nên đường dẫn kiểu `C:/...` bị hiểu sai.

**Cách sửa:** `build.py` chạy ffmpeg với `cwd` đặt tại thư mục tạm và tham chiếu tên file trần (`captions.ass`), né hoàn toàn chuyện escape. Nếu bạn buộc phải dùng đường dẫn tuyệt đối thì escape thành `C\\:/duong/dan.ass`.

## Concat báo lỗi hoặc video ghép bị giật

**Nguyên nhân:** concat demuxer với `-c copy` đòi mọi file có **cùng** codec, độ phân giải, pixel format, framerate, và với audio thì cùng codec/sample rate/số kênh.

**Cách sửa:** encode mọi segment và end card bằng đúng một bộ tham số. `build.py` tập trung việc này ở hàm `vcodec()` và `acodec()` — sửa ở đó chứ đừng sửa rải rác.

## Hình trôi khỏi tiếng ở cuối video

**Nguyên nhân:** mốc thời gian beat không nằm đúng biên frame. Mỗi segment lệch nửa frame, tích luỹ dần qua vài chục segment thành sai lệch thấy được.

**Cách sửa:** làm tròn mọi mốc về biên frame trước khi render. `build.py` làm tự động ở đầu `main()`.

## Dải B-roll che mất mặt người nói

**Nguyên nhân:** A-roll được quay với đầu đặt cao trong khung, nên sau khi dịch xuống 12.5% vẫn bị dải cắt.

**Cách sửa:** tăng `layout.aroll_translate_ratio`, hoặc giảm `layout.band_height_ratio`, trong khối `brand` của plan. Kiểm tra bằng một frame thật trước khi render cả video:

```bash
python scripts/build.py plan.json -o test.mp4 --preview
ffmpeg -y -ss 5 -i test.mp4 -frames:v 1 check.png
```

## Hộp caption tràn ra ngoài khung

**Nguyên nhân:** dòng chữ quá dài. Script kẹp chiều rộng hộp ở `caption.max_width_ratio` (mặc định 86%) nhưng chữ vẫn có thể tràn.

**Cách sửa:** viết lại cho ngắn — 4-7 từ mỗi dòng, tối đa 2 dòng. Đây là ràng buộc thiết kế chứ không phải giới hạn kỹ thuật: caption dài không đọc kịp ở nhịp 2 giây.

## Render bản thật quá chậm

Bản đầy đủ 1080×1920 @60fps với `crf 16 preset medium` là chủ ý — đây là bản giao. Để duyệt nhịp thì dùng `--preview` (nửa độ phân giải, `veryfast`), nhanh hơn khoảng một bậc độ lớn.

Chỉ render bản thật sau khi đã duyệt xong nhịp và vị trí chữ trên bản preview.

# Đặt B-roll vào composition HyperFrames

`place.py` sinh `broll-snippet.html`; phần này nói cách chèn nó đúng hợp đồng framework. Hợp đồng đầy đủ: `hyperframes-core/references/variables-and-media.md` và `tracks-and-clips.md`.

## Cấu trúc snippet

```html
<style> .broll-frame{...} .broll-frame .broll-media{... object-fit:cover} </style>
<div class="broll-frame" id="broll-frame" data-layout-allow-overflow="true">   <!-- KHÔNG có data-start -->
  <video id="broll-01" class="broll-media" src="assets/broll/3f9a1c77b2e4.mp4" muted playsinline preload="auto"
         data-start="12.400" data-duration="3.200" data-media-start="2.000" data-track-index="2"></video>
  ...
</div>
```

Ba điều framework bắt buộc, và lý do:

- **Wrapper không được timed.** `<video data-start>` nằm trong một phần tử cha cũng có `data-start` bị `lint` từ chối (`video_nested_in_timed_element`) — frame extractor tính offset hai lần. Wrapper chỉ để cắt khung (`overflow:hidden`) và định vị; thời gian nằm trên từng `<video>`.
- **`muted playsinline`, không `crossorigin`, không gọi `.play()`/seek.** HyperFrames sở hữu playback; render pre-extract frame qua FFmpeg nên HEVC/4K từ kho đều render đúng, preview tự proxy.
- **Âm thanh tách riêng.** B-roll DiLiM luôn câm (A-roll giữ tiếng). Nếu một clip sản phẩm cần tiếng, thêm `<audio src=... data-start data-duration data-media-start>` riêng.

## Chèn vào index.html

Đặt `<div class="broll-frame">` ở cấp con trực tiếp của `#root` (composition gốc), **sau** lớp A-roll và **trước** lớp caption trong thứ tự DOM, hoặc dùng `z-index` (A-roll 0 < B-roll 5 < caption 10). `data-track-index="2"` chỉ là làn hiển thị trong Studio, không ảnh hưởng render.

Cắt hard giữa hai B-roll liền nhau: hai `<video>` có `data-start` khít nhau (`b.start = a.start + a.duration`). Chuyển cảnh push (Broll Vip): animate `x` của wrapper trên timeline GSAP đã có của composition, không tạo timeline mới.

## Bố cục theo skill DiLiM

| layout | Khung | Nguồn thông số |
|---|---|---|
| `top` | 1080×608 ghim mép trên, tràn bề ngang, cắt thẳng; caption ngay dưới dải (y≈618) | skill `broll-top` |
| `vip` | 918×516 nổi nửa dưới, bo 40px, viền trắng 11px, push trái 12 frame; caption trên thẻ (y≈1036) | skill `broll-vip` |
| `full` | toàn khung 1080×1920 — chỉ cho video không có A-roll | — |

Nguồn 16:9 vào dải `top` 1080×608 lấp khít không mất pixel bề ngang — đó là lý do chọn 608 chứ không phải 672. Ảnh/clip đứng: `object-fit:cover` cắt trên/dưới (được), **không bao giờ pad đen hai bên** (người dùng đã bắt sửa 18.9% thời lượng có viền đen). Không Ken Burns / zoom theo thời gian — tỉ lệ phóng tĩnh, chọn một lần.

## Nguồn ngắn hơn đoạn cần

`place.py` báo lỗi khi `media_start + duration > dur nguồn`. Cách xử lý theo thứ tự: chọn `media_start` sớm hơn → cắt `duration` theo ranh giới caption → chọn clip khác. Loop nguồn là phương án cuối (HyperFrames không tự loop `<video>`; phải nhân đôi phần tử với `data-start` nối tiếp và `data-media-start="0"`).

## Sau khi chèn

```bash
hyperframes lint index.html
hyperframes render index.html --out renders/check.mp4   # hoặc snapshot tại từng data-start của B-roll
```

Trích frame tại **mỗi** `data-start` B-roll mới (`ffmpeg -ss <t> -i renders/check.mp4 -frames:v 1`) và xem thật — không lấy vài mẫu. Frame kiểm tra phải khớp cảnh đã tưởng tượng ở bước tìm, không chỉ "có hình".

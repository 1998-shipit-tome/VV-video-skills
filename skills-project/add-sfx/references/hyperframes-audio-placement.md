# `<audio>` SFX trong HyperFrames

Hợp đồng đầy đủ: `hyperframes-core/references/variables-and-media.md`, `tracks-and-clips.md`. Mix/fade/duck: skill `hyperframes-audio`.

## Snippet `place_sfx.py` sinh ra

```html
<audio id="sfx-01" src="assets/sfx/9c1f2e7a44b0.wav" data-start="12.350" data-duration="0.830"
       data-track-index="20" data-volume="0.13"></audio>  <!-- caption 'MỠ MÁU CAO' | hit 12.41s lead 0.06s -->
```

- `data-start` đã trừ `lead_s`; `data-duration` mặc định = độ dài file (audio có thể bỏ, nhưng ghi rõ để Studio hiển thị đúng).
- `data-track-index="20"` — làn hiển thị trong Studio, không ảnh hưởng render. Quy ước dự án: A-roll/dialogue 10, BGM 12, SFX 20 (theo `trao-nguoc-recut`). Hai `<audio>` cùng track và chồng thời gian → `lint` cảnh báo `duplicate_audio_track` — với SFX dồn dập (liệt kê) dùng track 20/21 xen kẽ.
- `data-volume` là mức trộn tĩnh. Fade/duck → animate `volume` trên timeline GSAP đã có (`tl.to("#sfx-05", {volume: 0, duration: 0.3}, t)`), không đổi `data-volume` giữa chừng.
- Không `crossorigin`, không gọi `.play()`, không đặt `<audio data-start>` bên trong phần tử có `data-start`. Đặt ở cấp con của `#root`, sau khối A-roll.
- File đã convert sang WAV 48 kHz (render dùng FFmpeg nên .aac/.m4a cũng được, nhưng WAV tránh lỗi preview với `.aac` raw không có container).

## Chèn vào index.html

Mở `index.html`, tìm khối `<audio>` dialogue/BGM hiện có, dán nội dung `sfx-snippet.html` ngay sau. `hyperframes lint index.html` → render preview có tiếng.

## Khi nào sang hyperframes-audio

- Muốn SFX **nổi hơn giọng** ở hook → duck dialogue 2–3 dB trong 0,5 s (voiceover carve), không tăng SFX > 0,35.
- SFX nghe "khô" giữa nhạc nền → reverb ngắn trên track SFX (`data-fx-chain`).
- Cả bộ SFX cần fader chung → `<hf-audio-group>` cho track 20.

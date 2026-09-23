# Luật đặt SFX trong video DiLiM

Tổng hợp từ pipeline cũ (`vr_build_sfx.py`, đợt 5 video VR 06/2026), composition `trao-nguoc-recut` (bản HyperFrames đầu tiên có SFX) và nguyên tắc chung của video bán hàng dọc có A-roll nói liên tục.

## 1. Mỗi tiếng gắn với một sự kiện hình ảnh

SFX không "rải" theo nhịp; nó **xác nhận** một thay đổi trên màn hình. Trước khi tìm tiếng, phải có danh sách sự kiện với thời điểm chính xác (từ `plan.json` B-roll/caption hoặc word-timestamps). Không có sự kiện → không có tiếng. Tiếng đặt ở chỗ không có gì đổi trên hình khiến người xem tìm "cái gì vừa xảy ra?" rồi mất tập trung khỏi lời nói.

Loại sự kiện ↔ loại tiếng (mặc định, đổi khi người dùng chốt khác):

| Sự kiện | Category | Thời lượng | Volume |
|---|---|---|---|
| Caption thường hiện | `pop` / `click` (tick) | 0,1–0,3 s | 0,10–0,15 |
| Caption nhấn mạnh (con số, cảnh báo, hook) | `impact` nhẹ / `drama` stinger ngắn | 0,3–1 s | 0,15–0,25 |
| B-roll cắt vào / thẻ push (Broll Vip) | `whoosh` ngắn | 0,3–0,6 s | 0,10–0,15 |
| Item liệt kê triệu chứng (dồn dập) | `pop` cùng một biến thể, hoặc 2 biến thể xen kẽ | 0,1–0,2 s | 0,10–0,13 |
| Ý tích cực / lợi ích / "đúng" | `ding` / chime | 0,5–1,5 s | 0,12–0,18 |
| Ý tiêu cực / "sai" / cảnh báo | `buzzer` nhẹ hoặc `drama` | 0,3–1 s | 0,12–0,18 |
| Trước khi lộ giá / lộ sản phẩm | `riser` | 1,5–4 s, kết đúng lúc lộ | 0,15–0,20 |
| Giá / tiết kiệm / khuyến mãi | `cash` | 0,5–1 s | 0,15–0,20 |
| Hài, quê, troll (giọng B kể chuyện) | `cartoon_meme` / `laugh` | ≤ 1,5 s | 0,12–0,18 |
| CTA cuối | `ding` sáng hoặc `notification` | 0,5–1 s | 0,15–0,20 |

Tham chiếu thực tế: `trao-nguoc-recut` dùng `whoosh` 0,12 · `impact_low` 0,20 · `pop` 0,13 · `tick` cho từng triệu chứng — người dùng đã chấp nhận mức này.

## 2. Mật độ

Trung bình **1 tiếng / 3–5 giây**, không đều: dồn ở danh sách liệt kê và chuyển đoạn (hook → triệu chứng → nguyên nhân → sản phẩm → CTA), thưa hoặc không có ở đoạn giải thích cơ chế dài. Đoạn 20 giây không tiếng nào là bình thường nếu hình cũng không đổi; 6 tiếng trong 3 giây chỉ chấp nhận cho liệt kê triệu chứng dồn dập — và khi đó dùng **một** biến thể pop, không đổi tiếng mỗi item (đổi tiếng liên tục nghe như lỗi).

Kiểm tra sau khi đặt: liệt kê mọi khoảng cách giữa hai tiếng liền nhau; < 0,15 s là dính (trừ liệt kê), > 15 s ở đoạn có caption đổi liên tục là đang bỏ sót.

## 3. Căn thời điểm — trừ khoảng lặng đầu file

Nhiều file SFX có 30–200 ms im lặng ở đầu. Nếu `data-start` = thời điểm chữ hiện, tiếng nổ **chậm hơn** chữ vài frame và cảm giác "lỏng". Index đo `lead_s` cho từng file; `place_sfx.py` đặt `data-start = hit − lead_s`. Đây là lỗi hệ thống pipeline cũ đã sửa (`vr_build_sfx.py`: "đẩy SFX lùi đúng bằng khoảng lặng đầu file").

Thời điểm `hit` lấy từ **frame chữ/B-roll thật sự xuất hiện** (đầu animation), không phải mốc segment Whisper. Với whoosh cho B-roll push: `hit` = frame bắt đầu push, tiếng kết thúc ≈ khi thẻ dừng.

## 4. Mức trộn — peak chuẩn hóa rồi mới chỉnh volume

Mọi file được đưa về **peak −6 dBFS** khi convert (`place_sfx.py --peak -6`), sau đó `data-volume` là mức trộn dưới lời nói. Hai bước tách biệt để cùng một `data-volume` cho cùng cảm giác to nhỏ giữa các file nguồn khác nhau (kho có file peak −1 dB lẫn file −25 dB). Không dùng SFX để "át" giọng; nếu tiếng nào cần nổi hơn giọng (rất hiếm: impact hook đầu video), duck giọng bằng skill `hyperframes-audio` thay vì tăng volume SFX lên > 0,35.

## 5. Không lặp cứng, nhưng nhất quán

Trong **một** video: cùng loại sự kiện → cùng tiếng (caption nào cũng `pop` A) là **đúng**, đó là ngôn ngữ âm thanh của video. Lặp cùng một tiếng > 3 lần **liên tiếp không có sự kiện khác chen giữa** → đổi biến thể (pop A / pop B). Giữa các video cùng series: dùng lại bộ tiếng đã duyệt (`favorites.json`) là điểm cộng.

## 6. Tiếng dài không phải SFX nhấn

`dur > 3 s` chỉ hợp lệ cho `riser`, `drama` (stinger dài), `ambience`, `crowd`. Một "whoosh" 4 giây là transition cinematic — dùng ở B-roll thường sẽ đè lên lời nói 4 giây. `search_sfx.py` trừ điểm và `place_sfx.py` cảnh báo.

## 7. Không nghe được thì làm gì

Agent không nghe được file. Chọn theo: category + thư mục cảm xúc (`sound-effect/BẤT NGỜ`…) + `dur` + `peak_db` (file peak < −30 dB thường là ambience/nhiễu) + tên. Với sự kiện quan trọng (hook, lộ giá, CTA), đưa **2–3 ứng viên** vào bảng duyệt để người dùng nghe chọn; sau khi chốt, ghi `favorite` để lần sau không phải hỏi lại. Đừng đoán "chắc nghe ổn" cho tiếng đặt ở 3 giây đầu video — đó là chỗ người xem quyết định lướt hay ở lại.

## 8. Thứ tự kho

`favorites` > `hyperframe-base` (9 file đã dùng, người dùng đã nghe) > `sound-effect` (phân cảm xúc tiếng Việt, hợp giọng B kể chuyện/hài) > `sfx-pack` (whoosh/riser/UI chuẩn, hợp giọng A) > `nitrozme` (click, transition kỹ thuật) > `sound-vlog` > `library` (9.000 file, chỉ khi các kho trên không có; tên file kiểu `SBA-300156894` ít nghĩa hơn).

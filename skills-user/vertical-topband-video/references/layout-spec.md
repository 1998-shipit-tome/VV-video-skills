# Thông số hình học

Mọi số dưới đây đo trực tiếp từ một video 1080×1920 @60fps đã chạy tốt (2:11, dựng bằng DaVinci Resolve), đối chiếu bằng cách ghim watermark cố định để loại trừ zoom toàn khung.

## Khung và dải

| Thông số | Giá trị | Dải quan sát được |
|---|---|---|
| Canvas | 1080×1920, 9:16 | |
| fps | 60 | |
| Chiều cao dải B-roll | **38%** (729px) | 34–41% tuỳ clip |
| A-roll dịch xuống | **12.5%** (240px) | cố định |
| A-roll scale | **1.00** | không bao giờ đổi |
| Logo | x 5–29%, y 3–8% | luôn trên cùng |
| Đáy khối caption | 38.5% | 26–39% tuỳ số dòng |

Cạnh dưới dải: **cắt thẳng, cứng**. Không bo góc, không viền, không đổ bóng, không feather. Đây là lựa chọn có chủ ý — cạnh cứng khiến hai lớp đọc như một khung chia đôi, còn bo góc/đổ bóng sẽ biến nó thành "cửa sổ nổi" và phá cảm giác liền mạch.

## Ba điều đã kiểm chứng bằng đo pixel

**A-roll không hề zoom.** Ban đầu nhìn qua rất dễ kết luận A-roll bị punch-in khi dải bật lên, vì mặt người nói trông thấp hơn. Đo khoảng cách ngang giữa các vật thể nền cho thấy tỉ lệ không đổi — đó là **dịch dọc thuần**, không phải scale. Nhầm chỗ này sẽ dẫn tới việc thêm zoom vào A-roll và làm hỏng điểm neo thị giác của cả format.

**Cú dịch là step, không ease.** A-roll snap xuống trong đúng 1 frame khi dải vào, và snap lên trong 1 frame khi dải ra. Không có transition. Ease ở đây sẽ tạo cảm giác trôi và làm người xem chú ý vào chuyển động thay vì nội dung.

**Watermark nằm trên tất cả.** Kể cả trên frame flash trắng ở outro. Nó là lớp cao nhất tuyệt đối.

## Chuyển cảnh dải

| Kiểu | Thời lượng | Ghi chú |
|---|---|---|
| `cut` | 0 frame | Phổ biến nhất. Dải và offset A-roll cùng biến mất trong 1 frame |
| `slide_left` | 0.30–0.40s tuyến tính | Đổi clip **bên trong** dải, không dissolve, không flash |
| `slide_up` | ~0.30s | Dải trượt lên khỏi khung khi thoát |
| `dissolve` | 0.45s ease-out | Opacity 0→100%; video mẫu còn cho chiều cao dải mọc 33%→41% cùng lúc |

Chi tiết "dải mọc" khi dissolve không được cài trong script vì nó cần mask alpha động, tốn nhiều hơn giá trị mang lại. Nếu thật sự cần, làm bằng `geq` trên kênh alpha trong cửa sổ transition.

## Ken Burns

Push-in tuyến tính, neo giữa: **1.00 → 1.13** (~+6%/giây), **reset về 1.00 mỗi clip mới**. Có clip đẩy tới 1.55 khi cần nhấn mạnh mạnh.

Khi một clip B-roll kéo dài qua hai caption, nó được re-scale/re-crop giữa chừng để không bao giờ đứng yên. Trong `plan.json`, cách làm là tách thành hai beat cùng `src` nhưng khác `in` và khác `kenburns`.

## Cách script dựng filtergraph

Đọc phần này khi cần sửa `build.py` hoặc gỡ lỗi hình.

```
[0:v] scale=W:H:force_original_aspect_ratio=increase, crop=W:H, setsar=1, fps  → [ar]
color=black:WxH                                                                → [bg]
[bg][ar] overlay=x=0:y=TRANSLATE                                               → [base]

[1:v] fps ▸ scale=2W:2BH (increase) ▸ crop=2W:2BH ▸ zoompan ▸ fps ▸ yuva420p   → [band]
        (+ fade alpha nếu dissolve)
[base][band] overlay=x=<expr trượt>:y=<expr trượt>                             → segment
```

Sau đó: concat `-c copy` → overlay logo → **burn caption cuối cùng** → ghép audio gốc.

Ba chi tiết trong chuỗi này không tuỳ tiện:

- **`fps` phải đứng trước `zoompan`.** Đưa luồng khác framerate thẳng vào zoompan sẽ làm filter treo vô hạn — không báo lỗi, chỉ đứng im. Đây là lỗi thật đã gặp khi chạy script lần đầu.
- **Pre-scale 2× trước zoompan.** zoompan làm tròn toạ độ crop về số nguyên; zoom trên ảnh đúng kích thước đích sẽ giật từng frame.
- **Caption burn sau cùng.** Đặt trước bất kỳ overlay nào thì overlay sẽ đè lên chữ. Lỗi này im lặng — video vẫn render thành công, chỉ là mất chữ.

## Snap về frame

Mọi mốc thời gian trong plan được làm tròn về biên frame trước khi render. Nếu không, `-frames:v` mỗi segment sẽ lệch nửa frame, tích luỹ dần, và cuối video hình trôi khỏi tiếng. Script làm việc này tự động — nhưng nếu bạn tự viết filtergraph thì phải nhớ.

## Audio

Format này **không cắt bỏ thời gian nào** — beat chỉ chia timeline chứ không xoá đoạn. Nhờ vậy audio gốc được ghép nguyên vẹn ở pass cuối, và không cần fade 30ms chống pop ở biên segment như khi dựng cut-based.

Nếu bạn mở rộng script để cắt bỏ đoạn, phải thêm afade 30ms mỗi biên, nếu không sẽ nghe tách ở từng mối nối.

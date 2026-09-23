add-broll-tieu-hoa — bộ B-roll tiêu hóa DiLiM + skill Claude Code
=====================================================================

CÀI ĐẶT (máy Windows/Mac/Linux đều được)
1. Giải nén, copy nguyên thư mục "add-broll-tieu-hoa" vào thư mục skill của dự án:
       <dự án>/.claude/skills/add-broll-tieu-hoa/
   (hoặc skill cá nhân: ~/.claude/skills/add-broll-tieu-hoa/)
2. Cần có sẵn: Python 3.10+, ffmpeg + ffprobe trên PATH. Không cần cài thư viện Python nào.
3. Mở Claude Code trong dự án, gõ thử:  "tìm clip táo bón trong kho tiêu hóa"
   hoặc chạy tay:
       python .claude/skills/add-broll-tieu-hoa/scripts/search.py "ngồi bồn cầu lâu" -n 5

CẤU TRÚC
   SKILL.md            hướng dẫn cho Claude (đọc file này trước)
   footage/            222 file, ~2.5 GB, 5 nhóm:
       01-trieu-chung  người thật: đau bụng, bồn cầu/táo bón, đầy hơi, đau gan
       02-co-che-3d    đồ họa: dạ dày, ruột, đại tràng, niêm mạc, lợi/hại khuẩn, trào ngược, gan
       03-nguyen-nhan  đồ chiên, fast food, bia rượu, cà phê, thuốc lá, ăn vội, stress, thuốc
       04-giai-phap    rau/chất xơ, chuối, yến mạch, sữa chua, uống nước, đi bộ, bác sĩ
       05-san-pham     Inulin Fuji FF, Nghệ Mùa Thu Okinawa, Gan (ảnh + video + nguyên liệu)
   index/              manifest.jsonl (mô tả từng clip), concept_graph.json, sheets/ (contact sheet), thumbs/
   references/         catalog.md (danh mục toàn kho), luật chọn clip, cách đặt vào HyperFrames, sản phẩm
   scripts/            search / verify_frame / place / build_index / describe_batches / make_catalog
   config.json         đổi "broll_root" nếu muốn để clip ở ổ khác

MUỐN ĐỂ CLIP Ở CHỖ KHÁC (ví dụ ổ E:)
   Dời thư mục footage/ đi, sửa config.json: "broll_root": "E:/broll-tieu-hoa"
   rồi chạy: python scripts/build_index.py update   (id là hash nội dung nên mô tả không mất)

THÊM CLIP MỚI
   Bỏ vào footage/06-them-moi/ (hoặc đúng nhóm), chạy:
       python scripts/build_index.py update --sheets
       python scripts/describe_batches.py make --all
   rồi nhờ Claude mô tả theo references/describe-prompt.md và merge. Chi tiết trong SKILL.md.

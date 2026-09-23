# -*- coding: utf-8 -*-
"""[CHỈ DÙNG PHÍA DiLiM] Rút bộ B-roll tiêu hóa từ kho tổng (skill add-footage)
vào thư mục skill này: copy clip theo 5 nhóm, chuyển mã file quá nặng, sinh
manifest/concept_graph/catalog riêng. Khách hàng KHÔNG cần chạy file này.

    python build_package.py [--dry-run] [--master-config D:/HYPERFRAME/footage/config.json]

Chọn clip bằng tiền tố rel_path trong kho tổng (SELECT). Mỗi mục:
    (tiền tố, đích) với đích = "01-trieu-chung" ... hoặc "05-san-pham/<Sản phẩm>/<Vai trò>".
Clip tên vô nghĩa (Canva/stock) nhưng đã có mô tả thì đổi tên theo mô tả.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from common import SKILL_DIR, fold, load_config, load_taxonomy, nfc, quick_hash, write_graph, write_manifest

SIZE_LIMIT = 5 * 1000 ** 3  # yêu cầu: gói < 5 GB

# ---------------------------------------------------------------- lựa chọn
TC, CC, NN, GP = "01-trieu-chung", "02-co-che-3d", "03-nguyen-nhan", "04-giai-phap"
INU_A, INU_NL = "05-san-pham/Inulin Fuji FF/Ảnh", "05-san-pham/Inulin Fuji FF/Nguyên Liệu"
NGHE_V, NGHE_A, NGHE_NL = ("05-san-pham/Nghệ Mùa Thu Okinawa/Video", "05-san-pham/Nghệ Mùa Thu Okinawa/Ảnh",
                           "05-san-pham/Nghệ Mùa Thu Okinawa/Nguyên Liệu")
GAN_A = "05-san-pham/Gan/Ảnh"

DB = "Đau Bụng - Tiêu hóa/"
NT = "NỘI TẠNG/"
CH = "Đã Chuẩn Hóa/"
LX = "Lộn Xộn Xà bần/"
DA = "Đồ ăn - Ăn uống/"
AU = "Ăn uống lành mạnh/"
VP = "Nhân Viên văn phòng/"
BR = "Bia Rượu - Nhậu/"
KB = "Khám bệnh - Bác Sĩ - uống Thuốc- bệnh khác/"

SELECT: list[tuple[str, str]] = [
    # ---- 01 triệu chứng (người thật) ----
    *[(DB + p, TC) for p in ["001", "007", "008", "009", "010", "012", "013", "017", "019", "020", "HIN (15)",
                             "Dau-bung,cac-van-de-tieuhoa-1 (1).mp4", "Dau-bung,cac-van-de-tieuhoa-1 (2)",
                             "Dau-bung,cac-van-de-tieuhoa-1 (3)", "Dau-bung,cac-van-de-tieuhoa-1 (4)",
                             "Dau-bung,cac-van-de-tieuhoa-1 (5)", "Dau-bung,cac-van-de-tieuhoa-1 (1).mov",
                             "ChatGPT Image"]],
    (CH + "006 - Ngồi trên bồn cầu", TC), (CH + "011 - Đứng ôm bụng dưới", TC), (CH + "dau bụng.mp4", TC),
    (LX + "đau bụng.mp4", TC), (LX + "ĐAU GAN.mp4", TC),
    ("Nghiện Điện Thoại MXH/011", TC), ("Nghiện Điện Thoại MXH/012", TC),
    (DA + "106", TC), (DA + "114", TC),
    (NT + "003", TC), (NT + "004", TC), (NT + "Thiết kế chưa có tên - 2025-02-26", TC),
    ("Hàu- Vợ chồng/019", TC), ("Giảm cân - Mập, tăng cân/021", TC),
    # ---- 02 cơ chế (đồ họa) ----
    *[(DB + p, CC) for p in ["003", "016", "021", "022", "023", "Dây thần kinh phế vị"]],
    *[(NT + p, CC) for p in ["001", "005", "006", "008", "009", "010", "012", "013", "014", "015", "016", "017",
                             "018", "019", "020", "021", "029", "034", "035", "036", "037", "039", "042", "043",
                             "Thiết kế chưa có tên (1).png", "Thiết kế chưa có tên - 2024-12-16T145049",
                             "Thiết kế chưa có tên - 2024-12-16T151551"]],
    *[(CH + p, CC) for p in ["gan-nhiem-mo,ap-luc", "gan-nhiem-mo,mo-noi-tang", "gan-nhiem-mo.mp4",
                             "niem-mac-duong-ruotj", "xo-gan"]],
    *[(LX + p, CC) for p in ["Ruột.mp4", "dạ dày.mp4", "loi khuan.mp4", "men vi sinh.mp4"]],
    # ---- 03 nguyên nhân ----
    *[(CH + p, NN) for p in ["003 - chien ngap dau", "dau-an-tai-su-dung", "do-chien-ran,nhieu-dau-mo-2",
                             "do-chien-ran,nhieu-dau-mo.-3", "164 - Cắn một miếng lớn", "165 - Cầm ly trà sữa",
                             "103 - Cắn và nhai", "046 - Máy quay tĩnh cận cảnh chồng các vỉ thuốc",
                             "uong-thuoc,uong-nhieu-loai-thuoc", "uong-thuoc-khong-hieu-qua"]],
    *[(DA + p, NN) for p in ["002", "105", "107", "120", "161", "180", "115", "130", "049", "043", "110", "148",
                             "169", "042", "045", "145", "085", "091", "017", "168"]],
    (AU + "004", NN), (AU + "074", NN),
    *[(VP + p, NN) for p in ["037", "008", "015", "016", "019", "029", "030", "031", "010"]],
    (LX + "vưa an vua xem dien thoai", NN), (LX + "vien thuoc.mp4", NN), (LX + "thuốc lá.mp4", NN),
    *[(BR + p, NN) for p in ["005", "006", "016", "018", "019", "009", "021", "014"]],
    (KB + "010 - Nguoi lon tuoi ngoi truoc dong lo thuoc", NN), (KB + "052 - Bop vien thuoc", NN),
    (KB + "028 - cam lo thuoc", NN),
    # ---- 04 giải pháp ----
    *[(AU + p, GP) for p in ["006", "015", "016", "017", "050", "066", "ĂN RAU", "036", "069", "071", "072", "077",
                             "008", "086", "012", "024", "013", "039", "032 - Khuấy ly nước hạt chia", "058", "063",
                             "Thiết kế chưa có tên (15).mp4", "8845448"]],
    *[(CH + p, GP) for p in ["056 - Dùng nĩa ăn salad", "178 - Cầm nĩa xới trộn salad", "uong-2-lit", "083 - Rót nước"]],
    *[(DA + p, GP) for p in ["071", "109", "022", "019", "141", "142", "122", "127", "027", "156", "157", "158",
                             "010", "125"]],
    (LX + "uong nuoc.mp4", GP),
    *[(KB + p, GP) for p in ["053", "007", "008", "021", "029", "038", "044", "045", "049", "055", "070", "071", "077"]],
    *[("Thể dục thể thao/" + p, GP) for p in ["047", "013", "071"]],
    ("Thiền - Đọc sách/005", GP),
    # ---- 05 sản phẩm ----
    ("Product Broll/Chất xơ hoà tan inulin", INU_A),
    (LX + "inulin_men_tieu_hoa_page", INU_A),
    ("Product Broll/Nghệ Mùa Thu Okinawa Nhật Bản/Video", NGHE_V),
    ("Product Broll/Nghệ Mùa Thu Okinawa Nhật Bản/Ảnh", NGHE_A),
    *[(DB + p, NGHE_NL) for p in ["002", "004", "005", "Thiết kế chưa có tên (58)", "Gemini_Generated"]],
    ("Product Broll/Gan/", GAN_A),
]

# File quá nặng so với giá trị -> chuyển mã H.264 1080p (id mới, giữ mô tả cũ)
TRANSCODE = {
    DB + "Dau-bung,cac-van-de-tieuhoa-1 (1).mov": "Dau-bung - nam ngoi sofa bam dien thoai roi om bung dung day.mp4",
}

# Mô tả bổ sung cho clip chưa có lớp ngữ nghĩa trong kho tổng (đã xem contact sheet 12/09/2026)
MANUAL: dict[str, dict] = {
    LX + "Ruột.mp4": dict(scene="Đồ họa 2D: icon dạ dày nối xuống ruột màu đỏ cam, nhỏ ở giữa khung trên nền xanh đen, rung/nhấp nháy nhẹ", action="icon dạ dày-ruột nhấp nháy", subject_type="anatomy_3d", mood="negative", body_part="dạ dày, ruột", tags=["dạ dày", "ruột", "icon", "đồ họa 2D", "tiêu hóa"], quality_flags=["small_subject"]),
    LX + "dạ dày.mp4": dict(scene="Đồ họa 2D: icon dạ dày màu xanh lá phát sáng, nhấp nháy giữa nền đen", action="icon dạ dày phát sáng", subject_type="anatomy_3d", mood="neutral", body_part="dạ dày", tags=["dạ dày", "bao tử", "icon", "đồ họa 2D"]),
    LX + "loi khuan.mp4": dict(scene="Đồ họa 3D: vi khuẩn que màu tím và xanh lá cùng các hạt tròn cam trôi nổi dày đặc, nền xanh đen — hệ vi sinh đường ruột", action="vi khuẩn trôi nổi", subject_type="anatomy_3d", mood="neutral", mechanism="hệ vi sinh đường ruột nhiều chủng", tags=["lợi khuẩn", "vi khuẩn", "hệ vi sinh", "probiotic", "đường ruột"]),
    LX + "men vi sinh.mp4": dict(scene="Đồ họa 3D: vi khuẩn que màu xanh dương sáng xếp dày đặc trên nền trắng xanh, chuyển động chậm — men vi sinh/lợi khuẩn", action="vi khuẩn que xếp dày", subject_type="anatomy_3d", mood="positive", mechanism="lợi khuẩn dạng que (lactobacillus)", tags=["men vi sinh", "lợi khuẩn", "probiotic", "vi khuẩn que"]),
    LX + "ĐAU GAN.mp4": dict(scene="Người mặc áo len xám ngồi trên ghế, tay ấn và xoa vùng hạ sườn phải (vị trí gan), không thấy mặt, nền phòng sáng", action="ấn vùng gan", subject_type="real_person", mood="painful", body_part="hạ sườn phải / gan", tags=["đau gan", "ấn bụng phải", "hạ sườn", "gan"]),
    LX + "đau bụng.mp4": dict(scene="Phụ nữ áo thun trắng đứng cạnh cửa sổ sáng, hai tay ôm bụng, nhăn mặt rồi khom người vì đau", action="ôm bụng khom người", subject_type="real_person", mood="painful", body_part="bụng", tags=["đau bụng", "ôm bụng", "khom người", "quặn bụng"]),
    LX + "vien thuoc.mp4": dict(scene="Cận cảnh hai bàn tay người lớn tuổi cầm lọ thuốc, mở nắp và đổ viên thuốc ra lòng bàn tay", action="đổ viên thuốc ra tay", subject_type="real_person", mood="neutral", tags=["viên thuốc", "lọ thuốc", "uống thuốc", "người già", "thuốc"]),
    LX + "thuốc lá.mp4": dict(scene="Cận cảnh đống đầu mẩu thuốc lá và tàn thuốc chất chồng, camera lia chậm", action="đầu thuốc lá chất đống", subject_type="lifestyle_scene", mood="negative", tags=["thuốc lá", "hút thuốc", "tàn thuốc", "thói quen xấu"]),
    LX + "uong nuoc.mp4": dict(scene="Cận cảnh nghiêng gương mặt phụ nữ ngửa cổ uống nước từ chai nhựa, ánh sáng ấm", action="uống nước từ chai", subject_type="real_person", mood="positive", tags=["uống nước", "chai nước", "đủ nước", "giải khát"]),
    LX + "vưa an vua xem dien thoai.mp4": dict(scene="Phụ nữ áo len xám ngồi ở bàn ăn, vừa cầm điện thoại lướt vừa ăn, trước mặt có burger và đĩa salad, không nhìn đồ ăn", action="vừa ăn vừa xem điện thoại", subject_type="real_person", mood="neutral", tags=["ăn vội", "vừa ăn vừa xem điện thoại", "burger", "thói quen xấu", "mất tập trung khi ăn"]),
    CH + "006 - Ngồi trên bồn cầu": dict(scene="Người đàn ông áo xanh ngồi trên bồn cầu trong nhà vệ sinh trắng, hai tay ôm đầu rồi ôm bụng, nhăn mặt nhíu mày, rặn khó khăn", action="ngồi bồn cầu nhăn mặt rặn", subject_type="real_person", mood="painful", body_part="bụng", tags=["táo bón", "bồn cầu", "toilet", "rặn", "khó đi ngoài", "ôm đầu"]),
    CH + "011 - Đứng ôm bụng dưới": dict(scene="Người mặc quần jeans áo xanh đứng trước bồn cầu, hai tay ôm và ấn bụng dưới, xoay người khó chịu như đang cố nhịn; không thấy mặt", action="ôm bụng dưới trước bồn cầu", subject_type="real_person", mood="painful", body_part="bụng dưới", tags=["đau bụng", "nhịn", "bồn cầu", "tiêu chảy", "quặn bụng", "toilet"]),
    CH + "dau bụng.mp4": dict(scene="Người đàn ông áo xanh ngồi trên bồn cầu, cúi người về trước, tay ôm đầu rồi ôm bụng, vẻ mặt đau khổ (cảnh gần giống clip 006, góc máy khác)", action="ngồi bồn cầu ôm bụng", subject_type="real_person", mood="painful", body_part="bụng", tags=["táo bón", "bồn cầu", "toilet", "đau bụng", "ôm bụng"]),
    BR + "019": dict(scene="Cô gái trẻ trong quán uống một hơi vại bia lớn, cười; khoảng giây 14 cắt sang hoạt hình cơ thể trong suốt với lá gan sáng vàng cam và các đốm nóng", action="uống bia rồi gan sáng lên", subject_type="real_person", mood="neutral", body_part="gan", segments=[{"t0": 0, "t1": 14, "scene": "cô gái uống một hơi vại bia trong quán"}, {"t0": 14, "t1": 19, "scene": "hoạt hình cơ thể trong suốt, lá gan sáng vàng cam"}], tags=["uống bia", "bia rượu", "gan", "hại gan", "nhậu"]),
    DB + "ChatGPT Image": dict(scene="Ảnh: chân người mặc quần đen ngồi trên bồn cầu, hai bàn chân đặt trên ghế kê chân trắng (squatty potty), nền gạch xám", subject_type="real_person", mood="neutral", tags=["bồn cầu", "ghế kê chân", "tư thế đi vệ sinh", "táo bón"]),
    NT + "Thiết kế chưa có tên (1).png": dict(scene="Ảnh minh họa 3D lá gan đỏ với mạch máu xanh-đỏ, nền trắng", subject_type="anatomy_3d", mood="neutral", body_part="gan", tags=["gan", "lá gan", "ảnh minh họa"]),
    DB + "Dây thần kinh phế vị": dict(scene="Ảnh minh họa dây thần kinh phế vị nối não và đường ruột (trục não–ruột): đầu người nhìn nghiêng với não phát sáng, ống tiêu hóa hồng, các sợi thần kinh xanh; nền tối", subject_type="anatomy_3d", mood="neutral", mechanism="trục não - ruột", tags=["thần kinh phế vị", "trục não ruột", "stress tiêu hóa", "não", "ruột"]),
    DB + "Gemini_Generated_Image_exv3": dict(scene="Infographic: 'Tác dụng kháng viêm của Curcumin' — dạ dày và ruột hồng, mũi tên, chữ tiếng Việt, hình củ nghệ; nền be", subject_type="text_graphic", mood="positive", has_text=True, tags=["curcumin", "nghệ", "kháng viêm", "infographic", "dạ dày", "đại tràng"]),
    DB + "Gemini_Generated_Image_ihyn": dict(scene="Infographic: hai hệ tiêu hóa (dạ dày+ruột) so sánh, nhãn CURCUMIN, nền xanh ngọc, chữ tiếng Việt", subject_type="text_graphic", mood="positive", has_text=True, tags=["curcumin", "nghệ", "infographic", "so sánh", "tiêu hóa"]),
    DB + "Gemini_Generated_Image_sasx": dict(scene="Infographic: hai hệ tiêu hóa 3D nền hồng nhạt, nhãn CURCUMIN ở giữa, hạt vàng bao quanh, chữ tiếng Việt", subject_type="text_graphic", mood="positive", has_text=True, tags=["curcumin", "nghệ", "infographic", "tiêu hóa"]),
    DB + "Thiết kế chưa có tên (58)": dict(scene="Ảnh củ nghệ tươi cắt lát và đống bột nghệ vàng cam, nền đen", subject_type="lifestyle_scene", mood="neutral", tags=["nghệ", "bột nghệ", "curcumin", "nguyên liệu"]),
    LX + "inulin_men_tieu_hoa_page_1": dict(scene="Ảnh giấy xác nhận nội dung quảng cáo của Cục An toàn thực phẩm cho sản phẩm Intestines Beauty Queen (chất xơ inulin), có dấu đỏ", subject_type="product", mood="neutral", has_text=True, tags=["giấy công bố", "chứng nhận", "inulin", "Intestines Beauty Queen", "cục ATTP"]),
    LX + "inulin_men_tieu_hoa_page_2": dict(scene="Ảnh tờ quảng cáo sản phẩm Intestines Beauty Queen: hộp hồng, người mẫu nữ, nhiều chữ tiếng Việt", subject_type="product", mood="positive", has_text=True, tags=["inulin", "Intestines Beauty Queen", "tờ quảng cáo", "hộp hồng"]),
    "Product Broll/Chất xơ hoà tan inulin phân tử dài  công nghệ Fuji FF/Ảnh/IMG_4139": dict(scene="Ảnh hộp sản phẩm Intestines (chất xơ hòa tan inulin Fuji FF) màu hồng-trắng đặt trên nền studio xám, góc chính diện", subject_type="product", mood="neutral", tags=["inulin", "hộp sản phẩm", "Intestines", "chất xơ"]),
    "Product Broll/Chất xơ hoà tan inulin phân tử dài  công nghệ Fuji FF/Ảnh/IMG_4141": dict(scene="Ảnh hộp sản phẩm Intestines (chất xơ hòa tan inulin Fuji FF) màu hồng-trắng trên nền studio xám, góc nghiêng", subject_type="product", mood="neutral", tags=["inulin", "hộp sản phẩm", "Intestines", "chất xơ"]),
    "Product Broll/Nghệ Mùa Thu Okinawa Nhật Bản/Ảnh/IMG_4133": dict(scene="Ảnh hộp Nghệ Mùa Thu Okinawa (chữ Nhật, hộp trắng) đặt trên nền studio xám", subject_type="product", mood="neutral", tags=["nghệ okinawa", "hộp sản phẩm", "curcumin"]),
}

# Cặp ý ↔ clip gợi ý sẵn (search.py hiện nhãn APPROVED). Khách có thể ghi đè bằng build_index.py approve.
SEED_CONCEPTS: list[tuple[str, str, float, str]] = [
    ("táo bón", CH + "006 - Ngồi trên bồn cầu", 0.0, "ngồi bồn cầu rặn khó — mặc định DiLiM"),
    ("ngồi bồn cầu lâu", DB + "009", 0.0, "bấm điện thoại trên bồn cầu"),
    ("đau bụng", DB + "Dau-bung,cac-van-de-tieuhoa-1 (1).mp4", 0.0, "bà cụ ôm bụng trên sofa"),
    ("đau bụng sau ăn", DB + "Dau-bung,cac-van-de-tieuhoa-1 (4)", 0.0, "đang ăn cơm thì ôm bụng"),
    ("đầy hơi khó tiêu", DA + "106", 0.0, "xoa bụng sau khi ăn burger"),
    ("trào ngược dạ dày", NT + "042", 26.0, "dịch axit trào lên thực quản (đoạn 26–52s)"),
    ("niêm mạc ruột", CH + "niem-mac-duong-ruotj", 0.0, "nhung mao ruột cam ấm"),
    ("lợi khuẩn", LX + "loi khuan.mp4", 0.0, "hệ vi sinh nhiều chủng"),
    ("men vi sinh", LX + "men vi sinh.mp4", 0.0, "vi khuẩn que xanh"),
    ("hại khuẩn tấn công ruột", DB + "022", 88.0, "thành ruột thủng lỗ (đoạn 88–103s), có logo"),
    ("gan nhiễm mỡ", CH + "gan-nhiem-mo.mp4", 0.0, "bác sĩ hoạt hình soi gan mỡ"),
    ("mỡ nội tạng bao quanh gan", CH + "gan-nhiem-mo,mo-noi-tang", 0.0, "có chữ tiếng Anh burn sẵn"),
    ("đại tràng", NT + "017", 0.0, "đại tràng sáng đỏ trong cơ thể trong suốt"),
    ("hệ tiêu hóa", NT + "016", 0.0, "dạ dày-ruột non tách riêng phóng to"),
    ("đồ chiên dầu mỡ", CH + "do-chien-ran,nhieu-dau-mo.-3", 0.0, "chiên ngập dầu"),
    ("bia rượu hại gan", BR + "019", 0.0, "uống bia rồi gan sáng lên"),
    ("stress công việc", VP + "019", 0.0, "gục đầu xoa thái dương"),
    ("uống nhiều loại thuốc", CH + "uong-thuoc,uong-nhieu-loai-thuoc", 0.0, ""),
    ("ăn rau xanh chất xơ", AU + "ĂN RAU", 0.0, ""),
    ("ăn uống lành mạnh vui vẻ", AU + "Thiết kế chưa có tên (15).mp4", 0.0, "người dùng DiLiM đã chốt"),
    ("sữa chua", DA + "157", 0.0, "xúc sữa chua ăn"),
    ("uống đủ nước", CH + "uong-2-lit", 0.0, ""),
    ("bác sĩ giải thích mô hình gan", KB + "071", 0.0, ""),
    ("nghệ curcumin", DB + "002", 0.0, "thìa bột nghệ"),
]

SEM_FIELDS = ("scene", "subject_type", "action", "mood", "body_part", "mechanism", "setting", "has_text",
              "color_tone", "segments", "tags", "topics_seen", "quality_flags", "described_by", "described_at")


def load_master(cfg_path: Path):
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    root = Path(cfg["broll_root"]); idx = Path(cfg["index_dir"])
    recs = [json.loads(l) for l in (idx / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return root, idx, recs


def safe_name(s: str, limit: int = 80) -> str:
    s = re.sub(r'[\\/:*?"<>|]+', " ", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:limit].rstrip(" .,;")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master-config", default=r"D:\HYPERFRAME\footage\config.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root, midx, recs = load_master(Path(args.master_config))
    pkg = load_config()
    dst_root: Path = pkg["broll_root"]; dst_idx: Path = pkg["index_dir"]
    tax = load_taxonomy()

    # ghép tiền tố -> record (kể cả đường dẫn dups)
    chosen: dict[str, tuple[dict, str]] = {}
    unmatched = []
    for prefix, dest in SELECT:
        pre = nfc(prefix); hit = 0
        for r in recs:
            paths = [r["rel_path"]] + list(r.get("dups") or [])
            if any(nfc(p).startswith(pre) for p in paths):
                if r["id"] not in chosen:
                    chosen[r["id"]] = (r, dest)
                hit += 1
        if not hit:
            unmatched.append(prefix)
    if unmatched:
        print("⚠ không khớp:", *[f"\n   {u}" for u in unmatched])

    manual = {nfc(k): v for k, v in MANUAL.items()}
    transcode = {nfc(k): v for k, v in TRANSCODE.items()}
    fmap = {nfc(k): v for k, v in tax["folders"].items()}
    pmap = {nfc(k): v for k, v in tax["product_folders"].items()}

    from common import read_manifest
    prev = read_manifest(pkg)  # chạy lại: giữ mô tả đã merge trong gói (khớp theo source_id)
    prev_by_src = {r.get("source_id"): r for r in prev.values() if r.get("source_id")}
    out: dict[str, dict] = {}
    total = 0
    used_names: set[str] = set()
    for rid, (r, dest) in sorted(chosen.items(), key=lambda kv: (kv[1][1], kv[1][0]["rel_path"])):
        src = root / r["rel_path"]
        if not src.is_file():  # bản chính đã bị dọn -> thử dups
            alt = [root / d for d in (r.get("dups") or []) if (root / d).is_file()]
            if not alt:
                print("✖ thiếu file:", r["rel_path"]); continue
            src = alt[0]
        rel_nfc = nfc(r["rel_path"])
        # tên đích
        if rel_nfc in transcode:
            fname = transcode[rel_nfc]
        elif r.get("name_class") in ("canva", "stock_id", "junk") and r.get("scene"):
            fname = safe_name(r["scene"]) + src.suffix.lower()
        else:
            fname = src.name
        if dest.startswith("05-san-pham") and fname.startswith("Gemini_Generated_Image") and r.get("scene") is None:
            pass
        key = f"{dest}/{fname}"
        if fold(key) in used_names:
            fname = f"{Path(fname).stem} [{rid}]{Path(fname).suffix}"; key = f"{dest}/{fname}"
        used_names.add(fold(key))
        dst = dst_root / dest / fname

        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if rel_nfc in transcode:
                if not dst.is_file():
                    print("⏳ chuyển mã", src.name, "->", fname)
                    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", "scale=1920:-2",
                                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                                    "-an", "-movflags", "+faststart", str(dst)], check=True)
            elif not dst.is_file() or dst.stat().st_size != src.stat().st_size:
                shutil.copy2(src, dst)

        rec = {k: v for k, v in r.items() if k in ("kind", "w", "h", "fps", "dur", "orient", "low_res", "broken")}
        rec.update({k: r[k] for k in SEM_FIELDS if k in r})
        if rid in prev_by_src:  # mô tả đã làm riêng trong gói thắng mô tả kho tổng
            rec.update({k: prev_by_src[rid][k] for k in SEM_FIELDS if k in prev_by_src[rid]})
        # lớp ngữ nghĩa bổ sung
        for mk, mv in manual.items():
            if rel_nfc.startswith(mk):
                rec.update(mv); rec.setdefault("described_by", "agent"); rec.setdefault("described_at", int(time.time()))
        top = dest.split("/")[0]
        info = fmap.get(nfc(top), {"pool": "topic", "topics": []})
        rec.update({
            "rel_path": key, "filename": fname, "folder": top, "pool": info["pool"], "topics": list(info["topics"]),
            "product_id": None, "asset_role": None, "name_class": r.get("name_class", "free"),
            "source_id": rid, "source_rel_path": r["rel_path"],
        })
        if info["pool"] == "product":
            parts = dest.split("/")
            rec["product_id"] = pmap.get(nfc(parts[1]), fold(parts[1]).replace(" ", "_"))
            rec["asset_role"] = {"video": "video", "nguyên liệu": "nguyen_lieu", "ảnh": "anh"}.get(nfc(parts[2]).lower(), "other")
        # chủ đề phụ theo nội dung
        txt = fold(" ".join([rec.get("scene") or "", " ".join(rec.get("tags") or []), fname]))
        extra = []
        if re.search(r"\bgan\b|xo gan|nhiem mo", txt): extra.append("gan")
        if re.search(r"bon cau|toilet|tao bon|giay ve sinh|ve sinh", txt): extra.append("tao_bon")
        if re.search(r"loi khuan|vi khuan|men vi sinh|probiotic|khang sinh|hai khuan", txt): extra.append("loi_khuan")
        rec["topics"] = sorted(set(rec["topics"]) | set(extra))

        if args.dry_run:
            rec["id"] = rid; size = src.stat().st_size
        else:
            rec["id"] = quick_hash(dst) if rel_nfc in transcode else rid
            st = dst.stat(); size = st.st_size
            rec["size"] = st.st_size; rec["mtime"] = st.st_mtime
            if rel_nfc in transcode:  # đo lại
                pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                     "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(dst)],
                                    capture_output=True, text=True).stdout
                j = json.loads(pr or "{}"); st0 = (j.get("streams") or [{}])[0]
                num, _, den = (st0.get("r_frame_rate") or "0/1").partition("/")
                rec.update({"w": st0.get("width"), "h": st0.get("height"), "fps": round(float(num) / float(den or 1), 3),
                            "dur": round(float(j["format"]["duration"]), 3)})
            # sheet/thumb
            for sub in ("sheets", "thumbs"):
                s = midx / sub / f"{rid}.jpg"; d = dst_idx / sub / f"{rec['id']}.jpg"
                if s.is_file():
                    d.parent.mkdir(parents=True, exist_ok=True)
                    if not d.is_file():
                        shutil.copy2(s, d)
                rec["sheet" if sub == "sheets" else "thumb"] = f"{sub}/{rec['id']}.jpg" if d.is_file() else None
        total += size
        out[rec["id"]] = rec

    # thống kê
    by: dict[str, list] = {}
    for rec in out.values():
        by.setdefault(rec["folder"], [0, 0])
        by[rec["folder"]][0] += 1; by[rec["folder"]][1] += rec.get("size", 0)
    print(f"\nchọn {len(out)} file, {total / 1e9:.2f} GB" + (" (dry-run, size nguồn)" if args.dry_run else ""))
    for k, v in sorted(by.items()):
        print(f"  {v[0]:4d}  {v[1] / 1e6:8.1f} MB  {k}")
    n_desc = sum(1 for r in out.values() if r.get("scene"))
    print(f"  đã có mô tả: {n_desc}/{len(out)}")
    if total > SIZE_LIMIT:
        print(f"✖ vượt {SIZE_LIMIT / 1e9:.0f} GB")
    if args.dry_run:
        return

    write_manifest(pkg, out)
    # concept graph
    by_src = {r["source_rel_path"]: r for r in out.values()}
    edges = []
    for concept, prefix, ms, note in SEED_CONCEPTS:
        hit = [r for p, r in by_src.items() if nfc(p).startswith(nfc(prefix))]
        if not hit:
            print("⚠ seed không khớp:", concept, prefix); continue
        edges.append({"concept": nfc(concept), "tokens": sorted(set(fold(concept).split())), "id": hit[0]["id"],
                      "media_start": ms, "weight": 1, "note": note, "source": "dilim-seed", "ts": int(time.time())})
    write_graph(pkg, {"version": 1, "edges": edges})
    print(f"manifest: {len(out)} record; concept_graph: {len(edges)} cạnh")
    import make_catalog
    make_catalog.main()



if __name__ == "__main__":
    main()

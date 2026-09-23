#!/usr/bin/env bash
# Seed concept_graph.json với các clip ưu tiên người dùng đã chốt (selection-rules.md §10)
# + 63 cặp đã duyệt từ pipeline cũ. Chạy SAU khi build_index.py update xong.
set -u
S="$(cd "$(dirname "$0")" && pwd)"
export PYTHONIOENCODING=utf-8
A="python $S/build_index.py approve --source user"

$A --concept "mất ngủ"            --path "Đã Chuẩn Hóa/chong-mat-mat-ngu,thieu-ngu,mat-ngu-1.mp4" --weight 3 --note "chốt 22/07/2026"
$A --concept "ngủ ngon"           --path "Ngủ- Ngon- mất ngủ/Chú 50-60 tuổi ngủ ngon.mp4" --weight 3 --note "chốt 17/08/2026 combo Raydel+Q10"
$A --concept "ăn uống lành mạnh"  --path "Ăn uống lành mạnh/ăn-uong-lanh-manh.mp4" --weight 3 --note "vui, hào hứng"
$A --concept "ăn uống lành mạnh"  --path "Ăn uống lành mạnh/Thiết kế chưa có tên (15).mp4" --weight 2
$A --concept "ăn uống lành mạnh"  --path "Ăn uống lành mạnh/8845448-uhd_4096_2160_24fps.mp4" --weight 2
$A --concept "chán ăn ăn kiêng"   --path "Giảm cân - Mập, tăng cân/033 - Dùng nĩa xúc rau xà lách ăn, vẻ mặt chán ghét khi ăn.mp4" --weight 3 --note "miễn cưỡng, khó chịu"
$A --concept "cơ thể khỏe mạnh"   --path "Thể dục thể thao/Thiết kế chưa có tên - 2024-12-20T115808.557.mp4" --weight 3 --note "cặp cô chú chạy bộ cười — ẩn ý cơ thể khỏe"
$A --concept "cơ thể khỏe mạnh"   --path "Thể dục thể thao/Thiết kế chưa có tên (3).mp4" --weight 2
$A --concept "cơ thể khỏe mạnh"   --path "Thể dục thể thao/Thiết kế chưa có tên - 2025-03-26T083741.007.mp4" --weight 2

LEGACY="D:/tinh-media-workflow/pipeline/broll_memory.json"
[ -f "$LEGACY" ] && python "$S/import_legacy.py" "$LEGACY"

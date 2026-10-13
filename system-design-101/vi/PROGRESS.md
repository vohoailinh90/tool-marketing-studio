# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

26/404 vị trí đã viết; 15 nhóm và 400 nguồn duy nhất giữ nguyên.

## Đã có

- **API và phát triển web:** bảy bài sd-01-001 đến sd-01-007, nhập từ repo cũ. Mỗi bài có evidence review ở repo cũ
  (prior_reviews, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5); evidence này không
  duyệt tổ hợp trong repo mới. PR #40 đã được merge vào main.
- **Hệ thống hoạt động thế nào?:** 18 bài sd-12-001 đến sd-12-018, viết mới ngày 2026-10-13 theo yêu cầu người dùng
  (danh sách ByteByteGo “How it Works?”), trên nhánh claude/funny-archimedes-253vvb. Chưa mở PR.

- **sd-01-008** (Trình duyệt dựng trang web thế nào?): viết ngày 2026-10-13 theo thứ tự nguồn, trên nhánh claude/sd-01-008 xếp chồng
  lên PR #51 (chưa merge, đang chờ review); chưa mở PR riêng. Cùng trạng thái draft như nhóm sd-12 bên dưới.

## Trạng thái 18 bài sd-12

Tất cả là bản nháp (`content_status: draft` trong metadata). Đã làm: đọc bài nguồn ở commit ghim (blob SHA khớp, có
hash nội dung đã tải), viết độc lập và vẽ sơ đồ mới, kiểm tra bằng máy (`scripts/sd101_check.py`), kiểm tra hiển thị
trên Chromium ở 320/375/430 px với mọi phần tùy chọn mở. Chưa làm: kiểm chứng claim với tài liệu chính thức (môi trường
viết không mở được các trang đó, nên `claims` còn pending), review kỹ thuật, kiểm tra trên GitHub hoặc điện thoại thật,
user testing.

## Thứ tự

ID kế tiếp theo thứ tự nguồn là sd-01-009. Nhóm sd-12 được viết trước vì người dùng yêu cầu rõ danh sách này;
các bài còn lại tiếp tục theo bảng đối chiếu, mỗi đợt 1–3 bài.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. User testing chưa thực hiện; không tự merge/deploy
hoặc đăng bài.

Đồng bộ main đích tại 3edff99314afa7435a4519b700e380eac8d6bc1c (trước đó f9f79246cf7b05979fc1343734e02ea8afc201be);
sửa adopted_main_sha theo finding4252903469 và finding4253959699. Mốc main repo cũ giữ previous_repository_main_sha.
Review tổ hợp mới vẫn pending.

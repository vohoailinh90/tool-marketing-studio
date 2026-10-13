# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

19/404 vị trí đã viết (7 bài nhóm API và phát triển web, 12 bài nhóm Nền tảng máy tính); 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đợt hiện tại: nhập bảy bài trên nhánh codex/system-design-vi-import; PR #40 (base main). Review tích hợp đang chờ. Sau khi đạt review/checks, tiếp tục sd-01-008 rồi đúng thứ tự source-map.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài.

Đồng bộ main đích tại 3edff99314afa7435a4519b700e380eac8d6bc1c (trước đó f9f79246cf7b05979fc1343734e02ea8afc201be); sửa adopted_main_sha theo finding4252903469 và finding4253959699. Mốc main repo cũ giữ previous_repository_main_sha. Review tổ hợp mới vẫn pending.

## Đợt 2026-10-13: nhóm Nền tảng máy tính (sd-15-001 đến sd-15-012)

Theo yêu cầu người dùng, viết nhóm cuối của mục lục nguồn trước; `next_id` vẫn là sd-01-008 vì nhóm API chưa viết hết. Mười hai bài viết độc lập từ kiến thức và tiêu chuẩn kỹ thuật, sơ đồ tự thiết kế, không dùng ảnh nguồn. Đã đọc thân bài nguồn tại commit ghim và đối chiếu blob SHA; tiêu đề tiếng Việt được điền vào bảng đối chiếu.

Chưa làm: kiểm chứng claim với tài liệu chuẩn (môi trường biên soạn không mở được rfc-editor.org, postgresql.org, mysql.com, man7.org), review kỹ thuật, kiểm tra mobile toàn bài trên trình duyệt (chữ trong sơ đồ được đo bằng công cụ tạm khi vẽ là vừa khung; repo chưa có kiểm tra tự động cho việc này), thử người học. Mọi bài ở trạng thái draft; không tự merge, deploy hay phê duyệt.

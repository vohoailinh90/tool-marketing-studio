# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

10/404 vị trí đã viết; 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đợt hiện tại: sd-01-008, sd-01-009, sd-01-010, viết tiếp theo thứ tự source-map. Bài mới ở trạng thái review, chờ review kỹ thuật; user testing chưa thực hiện; chưa tự merge hay phát hành.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài.

Đồng bộ main đích tại 3edff99314afa7435a4519b700e380eac8d6bc1c (trước đó f9f79246cf7b05979fc1343734e02ea8afc201be); sửa adopted_main_sha theo finding4252903469 và finding4253959699. Mốc main repo cũ giữ previous_repository_main_sha. PR #40 đã được merge; review tổ hợp trên head 5ce5e2b70b của PR đó không có finding trước khi merge.

Theo yêu cầu2026-10-13: CI xếp hàng không chặn PR tiếp theo khi review/checks cục bộ đạt. Đợt008–010 đang có sẵn PR53, tiếp nhận thay vì viết trùng CSS; active_pr=53. Danh sách PR chờCI trong progress.json; snapshot cũ không duyệt head mới. Không merge/deploy hoặc nhân đôi trạng thái lên YAML.

Đồng bộ main 42f9d80897f41cda6867c064893c37368cc639b2 sau PR #44. Giữ một canonical bài 008 của PR #53 đã đối chiếu nguồn; sửa paint/raster và điều kiện script chờ stylesheet theo review. Review tổ hợp mới pending; CI không được coi là đạt khi chưa có kết quả.

Đồng bộ main b6cde8cf8065c430756f20c1329ca84f56e25e7b (PR #63 giảm CI trùng), bảo toàn nguyên workflow/tests/mutations. Bài/hình không đổi; review và CI của head trước không duyệt tổ hợp mới.

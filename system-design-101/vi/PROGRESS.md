# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

10/404 vị trí đã viết; 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đợt hiện tại: đợt ba của nhóm Bảo mật (sd-14-007..sd-14-009). Các đợt trước (sd-14-001..003 ở PR #57, sd-14-004..006 ở PR #58) được viết song song và chưa nằm trong nhánh này, nên các PR cùng sửa các tệp chỉ mục (README, PROGRESS, progress.json, source-map) và PR merge sau cần gộp main rồi tạo lại các tệp đó. Bài mới ở trạng thái review, chờ review kỹ thuật; user testing chưa thực hiện; chưa tự merge hay phát hành.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài.

Đồng bộ main đích tại 3edff99314afa7435a4519b700e380eac8d6bc1c (trước đó f9f79246cf7b05979fc1343734e02ea8afc201be); sửa adopted_main_sha theo finding4252903469 và finding4253959699. Mốc main repo cũ giữ previous_repository_main_sha. PR #40 đã được merge; review tổ hợp trên head 5ce5e2b70b của PR đó không có finding trước khi merge.

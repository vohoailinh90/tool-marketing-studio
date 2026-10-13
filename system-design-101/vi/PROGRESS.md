# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

34/404 vị trí đã viết (7 bài nhập từ repo cũ và 27 bài sd-13); 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đợt nhập bảy bài (trước đợt sd-13): nhánh codex/system-design-vi-import; PR #40 (base main). Review tích hợp đang chờ. Sau khi đạt review/checks, tiếp tục sd-01-008 rồi đúng thứ tự source-map.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài.

Đồng bộ main đích tại 3edff99314afa7435a4519b700e380eac8d6bc1c (trước đó f9f79246cf7b05979fc1343734e02ea8afc201be); sửa adopted_main_sha theo finding4252903469 và finding4253959699. Mốc main repo cũ giữ previous_repository_main_sha. Review tổ hợp mới vẫn pending.

## Đợt sd-13 (2026-10-13): DevOps và CI/CD

Theo yêu cầu người dùng, viết nháp 27 bài của nhóm DevOps và CI/CD (sd-13-001 đến sd-13-027) trên nhánh claude/optimistic-galileo-ins11l. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân 27 bài nguồn đã đọc tại snapshot ghim và blob SHA khớp.

Chưa làm: kiểm chứng claim với tài liệu ngoài (môi trường soạn không truy cập được các trang đó; URL nguồn trong metadata chưa mở được), review kỹ thuật, kiểm tra hình trên thiết bị thật, user testing. Một kiểm tra đo chiều rộng chữ bằng phông DejaVu cho thấy chữ nằm trong khung; đó chưa phải kiểm tra mobile nên bước `mobile` vẫn pending. next_id vẫn là sd-01-008. Không tự merge, deploy hay đăng bài.

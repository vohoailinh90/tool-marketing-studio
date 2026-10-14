# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

43/404 vị trí đã viết (16 bài đã có trên main và 27 bài sd-13 của nhánh này); 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài đầu nhập từ repo cũ (PR #40, đã merge vào main) có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đợt trước trên main: đợt ba của nhóm Bảo mật (sd-14-007..sd-14-009), nhánh claude/sd101-sd14-batch3, đã gộp main sau khi PR #56 đưa nhóm Phỏng vấn kỹ thuật (sd-05) vào main. Các PR khác đang viết song song (sd-03 ở PR #49, sd-14-001..003 ở PR #57, sd-14-004..006 ở PR #58 và sd-14-010..012 ở PR #61) và chưa nằm trong nhánh này, nên các PR cùng sửa các tệp chỉ mục (README, PROGRESS, progress.json, source-map) và PR merge sau cần gộp main rồi tạo lại các tệp đó. Bài mới ở trạng thái review, chờ review kỹ thuật; user testing chưa thực hiện; chưa tự merge hay phát hành.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài. Mốc main repo cũ giữ previous_repository_main_sha. Review tổ hợp vẫn pending.

## Đợt sd-13 (2026-10-13): DevOps và CI/CD

Theo yêu cầu người dùng, viết nháp 27 bài của nhóm DevOps và CI/CD (sd-13-001 đến sd-13-027) trên nhánh claude/optimistic-galileo-ins11l. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân 27 bài nguồn đã đọc tại snapshot ghim và blob SHA khớp.

Chưa làm: kiểm chứng claim với tài liệu ngoài (môi trường soạn không truy cập được các trang đó; URL nguồn trong metadata chưa mở được), review kỹ thuật, kiểm tra hình trên thiết bị thật, user testing. Một kiểm tra đo chiều rộng chữ bằng phông DejaVu cho thấy chữ nằm trong khung; đó chưa phải kiểm tra mobile nên bước `mobile` vẫn pending. next_id theo main là sd-01-009. Không deploy hay đăng bài; việc merge theo quy trình review và CI của repo.

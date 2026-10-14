# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

60/404 vị trí đã viết (33 bài đã có trên main và 27 bài sd-13 của nhánh này); 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài đầu nhập từ repo cũ (PR #40, đã merge vào main) có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đợt gần nhất trên main: nhóm AI và học máy (sd-03-001..sd-03-008), nhánh claude/serene-bohr-75qxpq, đã vào main qua PR #49 sau khi PR #58 đưa sd-14-004..006 vào main. Các nhóm khác đã nằm trong main (sd-05-001..005 và sd-14-001..012); các bài từ sd-14-013 trở đi chưa viết. Nhóm DevOps và CI/CD (sd-13-001..027) nằm ở nhánh này và chưa vào main. Bài mới ở trạng thái review, chờ review kỹ thuật; user testing chưa thực hiện; chưa tự merge hay phát hành.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài. Mốc main repo cũ giữ previous_repository_main_sha. Review tổ hợp vẫn pending.

## Đợt sd-13 (2026-10-13): DevOps và CI/CD

Theo yêu cầu người dùng, viết nháp 27 bài của nhóm DevOps và CI/CD (sd-13-001 đến sd-13-027) trên nhánh claude/optimistic-galileo-ins11l. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân 27 bài nguồn đã đọc tại snapshot ghim và blob SHA khớp.

Đã làm: qua các vòng phản biện, nhiều claim kỹ thuật được đối chiếu với tài liệu chính thức ở dạng mã nguồn công khai trên GitHub (Kubernetes, Docker, BuildKit, Prometheus, PostgreSQL, nginx, DORA, Twelve-Factor App); martinfowler.com và dora.dev không mở được từ môi trường soạn. Chưa làm: người rà toàn bộ 141 claim trong metadata, review kỹ thuật, kiểm tra hình trên thiết bị thật, user testing. Một kiểm tra đo chiều rộng chữ bằng phông DejaVu cho thấy chữ nằm trong khung; đó chưa phải kiểm tra mobile nên bước `mobile` vẫn pending. next_id theo main là sd-01-009. Không deploy hay đăng bài; việc merge theo quy trình review và CI của repo.

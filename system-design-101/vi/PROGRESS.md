# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

86/404 vị trí đã viết (74 bài đã có trên main và 12 bài sd-15-001..012 của nhánh này); 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài đầu nhập từ repo cũ (PR #40, đã merge vào main) có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đã vào main: nhóm API và phát triển web đến sd-01-016 (PR #53 cho sd-01-008..010, PR #54 cho sd-01-011..013, PR #55 cho sd-01-014..016, PR #62 cho sd-01-017..019), nhóm sd-03, sd-05, nhóm DevOps và CI/CD sd-13-001..027 (PR #50) và nhóm Bảo mật sd-14-001..015 (đến PR #72). Đợt hiện tại: nhóm Nền tảng máy tính (sd-15-001 đến sd-15-012) ở PR #48. Review tổ hợp mới vẫn chờ.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài. Mốc main repo cũ giữ previous_repository_main_sha. Review tổ hợp vẫn pending.

## Đợt sd-13 (2026-10-13): DevOps và CI/CD

Theo yêu cầu người dùng, viết 27 bài của nhóm DevOps và CI/CD (sd-13-001 đến sd-13-027) trên nhánh claude/optimistic-galileo-ins11l. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân 27 bài nguồn đã đọc tại snapshot ghim và blob SHA khớp.

Trạng thái từng bài và bằng chứng kiểm chứng (claim, review kỹ thuật, hình trên thiết bị thật, người học thử) nằm ở `metadata/sd-13-*.json`, không nhân đôi ở đây. ID kế tiếp và PR đang mở ghi ở `progress.json`, không nhắc lại ở đây. Không deploy hay đăng bài; việc merge theo quy trình review và CI của repo.

## Đợt sd-14-013..015 (2026-10-14): Bảo mật

Theo yêu cầu người dùng, viết tiếp ba bài của nhóm Bảo mật (sd-14-013 tường lửa, sd-14-014 bốn cơ chế xác thực, sd-14-015 chữ ký số) trên nhánh claude/sd101-sd14-batch5. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân ba bài nguồn đã đọc tại snapshot ghim và blob SHA khớp. Hành vi nêu trong bài được chạy thử (nftables, OpenSSH dựng từ mã nguồn ghim, Python ssl, git, thư viện cryptography); kết quả và giới hạn ghi ở `metadata/sd-14-013.json` đến `sd-14-015.json`.

## Đợt 2026-10-13: nhóm Nền tảng máy tính (sd-15-001 đến sd-15-012)

Theo yêu cầu người dùng, viết nhóm cuối của mục lục nguồn trước; `next_id` giữ theo thứ tự source-map vì nhóm API chưa viết hết. Mười hai bài viết độc lập từ kiến thức và tiêu chuẩn kỹ thuật, sơ đồ tự thiết kế, không dùng ảnh nguồn. Đã đọc thân bài nguồn tại commit ghim và đối chiếu blob SHA; tiêu đề tiếng Việt được điền vào bảng đối chiếu.

Chưa làm: kiểm chứng claim với tài liệu chuẩn (môi trường biên soạn không mở được rfc-editor.org, postgresql.org, mysql.com, man7.org), review kỹ thuật, kiểm tra mobile toàn bài trên trình duyệt (chữ trong sơ đồ được đo bằng công cụ tạm khi vẽ là vừa khung; repo chưa có kiểm tra tự động cho việc này), thử người học. Mọi bài ở trạng thái draft; không tự merge, deploy hay phê duyệt.

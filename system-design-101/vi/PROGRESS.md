# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

68/404 vị trí đã viết (65 bài đã có trên main và 3 bài sd-14-013..015 của nhánh này); 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài đầu nhập từ repo cũ (PR #40, đã merge vào main) có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đã vào main: nhóm API và phát triển web đến sd-01-010 (PR #53; sd-01-008 là bản đã đối chiếu nguồn và sửa theo review), nhóm sd-03, sd-05, sd-14-001..012 nhóm DevOps và CI/CD sd-13-001..027 (PR #50) và sd-01-011..013 (PR #54). Đợt hiện tại (sd-14-013..015, nhóm Bảo mật) nằm ở PR #72. Review tổ hợp mới vẫn chờ.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài. Mốc main repo cũ giữ previous_repository_main_sha. Review tổ hợp vẫn pending.

## Đợt sd-13 (2026-10-13): DevOps và CI/CD

Theo yêu cầu người dùng, viết 27 bài của nhóm DevOps và CI/CD (sd-13-001 đến sd-13-027) trên nhánh claude/optimistic-galileo-ins11l. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân 27 bài nguồn đã đọc tại snapshot ghim và blob SHA khớp.

Trạng thái từng bài và bằng chứng kiểm chứng (claim, review kỹ thuật, hình trên thiết bị thật, người học thử) nằm ở `metadata/sd-13-*.json`, không nhân đôi ở đây. ID kế tiếp và PR đang mở ghi ở `progress.json`, không nhắc lại ở đây. Không deploy hay đăng bài; việc merge theo quy trình review và CI của repo.

## Đợt sd-14-013..015 (2026-10-14): Bảo mật

Theo yêu cầu người dùng, viết tiếp ba bài của nhóm Bảo mật (sd-14-013 tường lửa, sd-14-014 bốn cơ chế xác thực, sd-14-015 chữ ký số) trên nhánh claude/sd101-sd14-batch5. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân ba bài nguồn đã đọc tại snapshot ghim và blob SHA khớp. Hành vi nêu trong bài được chạy thử (nftables, OpenSSH dựng từ mã nguồn ghim, Python ssl, git, thư viện cryptography); kết quả và giới hạn ghi ở `metadata/sd-14-013.json` đến `sd-14-015.json`.

## Điều phối nhiều phiên (2026-10-15)

Nhiều phiên Claude viết bài cùng lúc, nên `claims.jsonl` ghi từng trong 404 vị trí là chưa ai nhận, đang có phiên viết hay đã viết xong. Phiên nào cũng phải nhận bài trước khi viết và ghi xong khi viết xong (`scripts/sd101_claims.py`, quy trình ở `docs/sd101-claims.md`). Lúc tạo, 68 bài đã có trên disk được ghi là đã viết, không ghi chủ hay ngày vì không ai ghi lại; 336 bài còn lại chưa ai nhận. `next_id` trong `progress.json` chỉ là bài đầu tiên chưa viết, không phải lệnh nhận bài.

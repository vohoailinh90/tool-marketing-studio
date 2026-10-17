# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

92/404 vị trí đã viết (89 bài đã có trên main và 3 bài sd-02-001..003 của nhánh này); 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài đầu nhập từ repo cũ (PR #40, đã merge vào main) có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đã vào main: nhóm API và phát triển web đến sd-01-022 (PR #53 cho sd-01-008..010, PR #54 cho sd-01-011..013, PR #55 cho sd-01-014..016, PR #62 cho sd-01-017..019, PR #73 cho sd-01-020..022), nhóm sd-03, sd-05, nhóm DevOps và CI/CD sd-13-001..027 (PR #50) nhóm Bảo mật sd-14-001..015 (đến PR #72) và nhóm Nền tảng máy tính sd-15-001..012 (PR #48). Đợt hiện tại: ba bài đầu của nhóm Tình huống thực tế (sd-02-001 đến sd-02-003) ở PR #102. Review tổ hợp mới vẫn chờ.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài. Mốc main repo cũ giữ previous_repository_main_sha. Review tổ hợp vẫn pending.

## Đợt sd-13 (2026-10-13): DevOps và CI/CD

Theo yêu cầu người dùng, viết 27 bài của nhóm DevOps và CI/CD (sd-13-001 đến sd-13-027) trên nhánh claude/optimistic-galileo-ins11l. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân 27 bài nguồn đã đọc tại snapshot ghim và blob SHA khớp.

Trạng thái từng bài và bằng chứng kiểm chứng (claim, review kỹ thuật, hình trên thiết bị thật, người học thử) nằm ở `metadata/sd-13-*.json`, không nhân đôi ở đây. ID kế tiếp và PR đang mở ghi ở `progress.json`, không nhắc lại ở đây. Không deploy hay đăng bài; việc merge theo quy trình review và CI của repo.

## Đợt sd-14-013..015 (2026-10-14): Bảo mật

Theo yêu cầu người dùng, viết tiếp ba bài của nhóm Bảo mật (sd-14-013 tường lửa, sd-14-014 bốn cơ chế xác thực, sd-14-015 chữ ký số) trên nhánh claude/sd101-sd14-batch5. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân ba bài nguồn đã đọc tại snapshot ghim và blob SHA khớp. Hành vi nêu trong bài được chạy thử (nftables, OpenSSH dựng từ mã nguồn ghim, Python ssl, git, thư viện cryptography); kết quả và giới hạn ghi ở `metadata/sd-14-013.json` đến `sd-14-015.json`.

## Điều phối nhiều phiên (2026-10-15)

Nhiều phiên Claude viết bài cùng lúc, nên `claims.jsonl` ghi từng trong 404 vị trí là chưa ai nhận, đang có phiên viết hay đã viết xong. Phiên nào cũng phải nhận bài trước khi viết và ghi xong khi viết xong (`scripts/sd101_claims.py`, quy trình ở `docs/sd101-claims.md`). Lúc tạo, 68 bài đã có trên disk được ghi là đã viết, không ghi chủ hay ngày vì không ai ghi lại; 336 bài còn lại chưa ai nhận. Khi một nhánh làm việc merge `main` và nhận thêm bài của phiên khác (ở nhánh này có thêm 21 bài như vậy), chạy `python3 scripts/sd101_claims.py sync` để ghi các bài đó là đã viết. `next_id` trong `progress.json` chỉ là bài đầu tiên chưa viết, không phải lệnh nhận bài.

## Đợt 2026-10-13: nhóm Nền tảng máy tính (sd-15-001 đến sd-15-012)

Theo yêu cầu người dùng, viết nhóm cuối của mục lục nguồn trước; `next_id` giữ theo thứ tự source-map vì nhóm API chưa viết hết. Mười hai bài viết độc lập từ kiến thức và tiêu chuẩn kỹ thuật, sơ đồ tự thiết kế, không dùng ảnh nguồn. Đã đọc thân bài nguồn tại commit ghim và đối chiếu blob SHA; tiêu đề tiếng Việt được điền vào bảng đối chiếu.

Chưa làm: kiểm chứng claim với tài liệu chuẩn (môi trường biên soạn không mở được rfc-editor.org, postgresql.org, mysql.com, man7.org), review kỹ thuật, kiểm tra mobile toàn bài trên trình duyệt (chữ trong sơ đồ được đo bằng công cụ tạm khi vẽ là vừa khung; repo chưa có kiểm tra tự động cho việc này), thử người học. Mọi bài ở trạng thái draft; không tự merge, deploy hay phê duyệt.

## Đợt sd-02-001..003 (2026-10-16): Tình huống thực tế

Theo yêu cầu người dùng, viết ba bài đầu của nhóm Tình huống thực tế (Figma mở rộng Postgres, nối ứng dụng bằng trigger và action, Pinterest và refspec) sau khi nhận bài bằng `claims.jsonl`. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn; thân ba bài nguồn đã đọc tại snapshot ghim và blob SHA khớp. Hành vi của Postgres 16.15 (sd-02-001) và của Git 2.43.0 (sd-02-003) được chạy thử cục bộ; các con số của Figma và Pinterest chỉ theo nguồn thứ cấp, và trang tài liệu chuẩn không mở được từ máy biên soạn. Chi tiết kiểm chứng và giới hạn ở `metadata/sd-02-001.json` đến `sd-02-003.json`; review kỹ thuật, thử người học chưa làm, và không tự deploy hay đăng bài.

## Đợt làm sâu năm bài sát nguồn (2026-10-16)

Theo yêu cầu người dùng, quét xem bài nào bám nguồn nhất rồi làm sâu để bài độc lập hơn. `scripts/sd101_source_distance.py` lấy thân nguồn ghim (kiểm blob SHA, lưu ngoài repo) và xếp hạng 92 bài theo mức lặp lại từ vựng và thứ tự của nguồn; năm bài đứng đầu là sd-05-005, sd-01-003, sd-01-012, sd-15-012 và sd-03-005. Cả năm được viết lại quanh lập luận riêng thay vì thứ tự của nguồn, có thử nghiệm của người biên soạn (máy khách HTTP trước mã lạ, hành vi số cổng trên Linux, đọc và đếm ba tài liệu ôn phỏng vấn, PostgreSQL và SQLite, giấy phép các kho cùng đo Faiss); đổi tiêu đề ở metadata, bảng đối chiếu và README, vẽ lại hình. Các con số của lần quét sau khi sửa nằm dưới 0,1 cho cả năm bài (trước đó 0,12 đến 0,39; đã tính lại sau khi bộ lọc bỏ mảnh ASCII của từ tiếng Việt, từ tiếng Việt không dấu và thẻ HTML, thứ hạng năm bài đầu không đổi); xem đó là chỉ báo, không phải bằng chứng pháp lý.

Ghi chú cho phiên sau: ngoài các trang tài liệu chính không mở được, `raw.githubusercontent.com` mở được, nên có thể đọc bản RFC của nhóm HTTP (`httpwg/httpwg.github.io`, thư mục `specs`), tài liệu nhân Linux, man-pages, nguồn tài liệu PostgreSQL và mã nguồn thư viện. Mọi bản đọc ở nhánh chính, không ghim, nên metadata ghi ngày đọc. Review kỹ thuật và thử người học chưa làm.

# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

100/404 vị trí đã viết (89 bài đã có trên main; 023 trong PR75, 024–025 trong PR76, 026 trong PR77, 027 trong PR78, 028 trong PR79, 029 trong PR80, 030 trong PR81, 031 trong PR82, 032 trong PR83 và 033 của nhánh này); 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài đầu nhập từ repo cũ (PR #40, đã merge vào main) có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

Đã vào main: nhóm API và phát triển web đến sd-01-022 (PR #53 cho sd-01-008..010, PR #54 cho sd-01-011..013, PR #55 cho sd-01-014..016, PR #62 cho sd-01-017..019, PR #73 cho sd-01-020..022), nhóm sd-03, sd-05, nhóm DevOps và CI/CD sd-13-001..027 (PR #50) và nhóm Bảo mật sd-14-001..015 (đến PR #72). Nhóm Nền tảng máy tính sd-15-001..012 đã có trên main qua PR #48. PR75 cho sd-01-023 có review sạch 6189117443 trên head 1546428 và CI38714324531 success, vẫn open. PR76 có review5531739397 trên f3b6c65; P2 về PR75 đã merged được bác bằng GitHub API tại thread4282519794 theo protocol§16, không gọi đây là verdict bot sạch. CI76 đã success đúng f3b6c65. PR77 có review6192364922 sạch/CI38735906200 success đúng67832e5; các PR vẫn open, metadata chưa tự đổi done. Đợt hiện tại là bài033 xếp trên PR83; review6201942706 sạch và CI38804432707success đúng653f15ed; các PR vẫn open, không tự đổi done.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài. Mốc main repo cũ giữ previous_repository_main_sha. Review tổ hợp vẫn pending.

## Đợt sd-13 (2026-10-13): DevOps và CI/CD

Theo yêu cầu người dùng, viết 27 bài của nhóm DevOps và CI/CD (sd-13-001 đến sd-13-027) trên nhánh claude/optimistic-galileo-ins11l. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân 27 bài nguồn đã đọc tại snapshot ghim và blob SHA khớp.

Trạng thái từng bài và bằng chứng kiểm chứng (claim, review kỹ thuật, hình trên thiết bị thật, người học thử) nằm ở `metadata/sd-13-*.json`, không nhân đôi ở đây. ID kế tiếp và PR đang mở ghi ở `progress.json`, không nhắc lại ở đây. Không deploy hay đăng bài; việc merge theo quy trình review và CI của repo.

## Đợt sd-14-013..015 (2026-10-14): Bảo mật

Theo yêu cầu người dùng, viết tiếp ba bài của nhóm Bảo mật (sd-14-013 tường lửa, sd-14-014 bốn cơ chế xác thực, sd-14-015 chữ ký số) trên nhánh claude/sd101-sd14-batch5. Bài viết độc lập, sơ đồ thiết kế mới, không dùng ảnh nguồn. Thân ba bài nguồn đã đọc tại snapshot ghim và blob SHA khớp. Hành vi nêu trong bài được chạy thử (nftables, OpenSSH dựng từ mã nguồn ghim, Python ssl, git, thư viện cryptography); kết quả và giới hạn ghi ở `metadata/sd-14-013.json` đến `sd-14-015.json`.

## Đợt 2026-10-13: nhóm Nền tảng máy tính (sd-15-001 đến sd-15-012)

Theo yêu cầu người dùng, viết nhóm cuối của mục lục nguồn trước; `next_id` giữ theo thứ tự source-map vì nhóm API chưa viết hết. Mười hai bài viết độc lập từ kiến thức và tiêu chuẩn kỹ thuật, sơ đồ tự thiết kế, không dùng ảnh nguồn. Đã đọc thân bài nguồn tại commit ghim và đối chiếu blob SHA; tiêu đề tiếng Việt được điền vào bảng đối chiếu.

Chưa làm: kiểm chứng claim với tài liệu chuẩn (môi trường biên soạn không mở được rfc-editor.org, postgresql.org, mysql.com, man7.org), review kỹ thuật, kiểm tra mobile toàn bài trên trình duyệt (chữ trong sơ đồ được đo bằng công cụ tạm khi vẽ là vừa khung; repo chưa có kiểm tra tự động cho việc này), thử người học. Mọi bài ở trạng thái draft; không tự merge, deploy hay phê duyệt.

## Bài sd-01-023 (2026-10-15)

Thêm bài tiếp theo theo thứ tự nguồn trên nhánh codex/sd01-023-gateway-use-cases, từ main e4af7d6. Không thay các bài hoặc evidence của phiên khác. Trạng thái và evidence của bài mới chỉ ở metadata JSON. Chưa thử người học, không merge/deploy.

## Bài 024–025 (2026-10-15)

Hai bài mới về SemVer và thành phần URL. Nhánh xếp trên head 1546428 của PR75 (review sạch 6189117443; CI 38714324531 còn queued), main nền e4af7d6. Không coi CI chờ là thành công. Giữ 023; không thay tooling. Evidence và trạng thái draft của từng bài ở metadata. Số PR mới sẽ được ghi khi có đợt nội dung thực chất; không push chỉ cập nhật trạng thái.

## Bài026 (2026-10-15)

Bốn kiểu tập đích của gói, hình tự thiết kế; anycast chọn một đích theo định tuyến, không phải multicast. Đọc chuẩn đối chiếu và ghi scope tại metadata. Không đổi các bài trước/tooling; main nền vẫn e4af7d6. PR75/76 chưa merged tại lúc viết. Số PR mới chưa có khi initial commit, ghi ở đợt nội dung thực chất tiếp theo; không push chỉ state.

## Bài027 (2026-10-15)

Thêm bản đồ vai trò của ứng dụng web, không coi mười chủ đề là mười máy chủ bắt buộc. Đối chiếu tài liệu chính thức; ví dụ và hình nguyên bản. Giữ nguyên bài trước và tooling. Main nền e4af7d6; PR75/76/77 vẫn open lúc viết. Số PR mới chưa có lúc initialcommit, bổ sung trong đợt nội dung thực chất; không push state-only.

## Hòa nhập main7397e5c và glossary (2026-10-15)

PR68 đã vào main, quy tắc mới yêu cầu mục Từ viết tắt ngay sau hình. Giữ nguyên main và checker, thêm glossary cho023–027. MAJOR/MINOR là tên trường SemVer, dùng code/cách viết thường thay vì giải thích sai thành acronym. PR78 vẫn xếp trên PR77; tích hợp main bằng parent thứ hai, chưa merge PR. Review6193640376/CI38744382938 sạch trên e596fe4 chỉ là evidence trước hòa nhập; cần review head mới. 94 bài không đồng nghĩa94done.

## Sửa P1 hiệu năng loại URL trong checker (2026-10-15)

Finding4284532128 trên bc5753e đã tái hiện: regex scheme không neo quét lặp hậu tố chuỗi dài không có URL. Sửa bằng quét dấu :// rồi xác định scheme/đích, giữ hành vi loại URL và phát hiện acronym ở prose. Thêm test hồi quy và mutation hiệu năng, cập nhật anchor mutation cũ, không bỏ quy tắc glossary hoặc loại trường hợp dài khỏi test. Nội dung/hình023–027 không đổi; review/CIbc5753e chỉ là evidence prior cho fix mới. Chưa tiếp028.

Xác minh fix: 58 test liên quan (glossary, pathological Markdown và URL scanner) đạt; ba test URL mới nằm trong số này. Mutation regex cũ và tám mutation liên quan URL đều caught, 554 anchor mutation cũ áp được. Checker94bài/0lỗi. Không coi test suite bổ sung chưa kết thúc là pass; CI head mới cần kiểm riêng.

## Bài028 (2026-10-15)

Bài URI/URL/URN, hình và ví dụ tự thiết kế. Đọc chuẩn, sửa ngộ nhận URN không thể phân giải. PR78review6195858816 sạch đúng66c0caf,CI38760239431 còn queued; xếp bài028 trên nhánhPR78, không coi queue là success/done. Giữ main nền7397e5c và nội dung/tooling đã review của PR78. Active PR chưa có số lúc initialcommit; ghi ở đợt nội dung thực chất sau, không push chỉstate.

## Bài029 (2026-10-15)

API/SDK với ví dụ thư viện và sơ đồ mới, giới hạn API không chỉ là địa chỉ mạng và SDK không tự bảo đảm tương thích/hiệu năng. PR79review6197133407 sạch đúng0c1428a; CI79queued/CI78in_progress chưa là success. Giữ main7397e5c và bản checker78; không tooling. Active PR chưa có số lúc initialcommit, ghi ở đợt nội dung thực chất tiếp; metadata draft/technicalpending, chưa thử người học/merge/deploy.

## Bài030 (2026-10-15)

Bảng kiểm bảo vệ API, ví dụ hồ sơ thú cưng và hình mới. Giữ giới hạn của từng lớp; không hứa một biện pháp đủ ngăn mọi tấn công. PR80 review6198578083 sạch đúngb7bbb013; CI78/79/80 success đúnghead được lưu cùng nội dung này, bỏ khỏi pending queue. Main7397e5c/lastmerged68 giữ, PR74registry cònopen chưaáp. Active PR chưa có số lúc initialcommit; ghi ở đợt nội dung thực chất tiếp, không push chỉstate; không merge/deploy/markdone.

## Bài031 (2026-10-15)

Năm nhóm mã phản hồi HTTP, sơ đồ mới, ví dụ202 chưa xử lý xong/304 liên quan bản lưu. PR81 review6199390252 sạch và CI38785896699success đúngf43150c8, evidence lưu cùng nội dung031; main7397e5c/lastmerged68 giữ, registryPR74open chưaáp. Active PR chưa có số lúc initialcommit, ghi ở đợt nội dung thực chất sau; không merge/deploy/markdone.

## Bài032 (2026-10-15)

Bốn góc nhìn SOAP/REST/GraphQL/RPC; body nguồn ngắn và ảnh chưa đọc nên đối chiếu chuẩn trực tiếp, hình mới không timeline. PR82 review6200875301 sạch/CI38796468467success đúnge7f1d60d lưu evidence cùng nội dung032. Main7397e5c/lastmerged68 giữ, PR74registryopen chưaáp. Active PR chưa có số lúc initialcommit; ghi ở đợt nội dung thực chất tiếp, không merge/deploy/markdone.

## Bài033 (2026-10-15)

Sáu cách giao tiếp và ba câu hỏi chọn theo nhu cầu; hình mới, không xếp hạng hoặc coi sáu mục cùng cấp. PR83review6201942706 sạch/CI38804432707success đúng653f15ed lưu cùng nội dung033; giữ bản sửa related032→019, không đụng032/tooling. Main7397e5c/lastmerged68 giữ, registryPR74open chưaáp. Active PR chưa số lúc initialcommit, ghi ở đợt nội dung thực chất tiếp; không merge/deploy/markdone.

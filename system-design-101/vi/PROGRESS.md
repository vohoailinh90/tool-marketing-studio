# Tiến độ System Design tiếng Việt

Chuyển sang vohoailinh90/tool-marketing-studio ngày 2026-10-13 theo yêu cầu người dùng.
Repo cũ tạm dừng; không merge/đóng/xóa các PR cũ.

56/404 vị trí đã viết (7 bài đã nhập và 49 bài nhóm Đám mây và hệ thống phân tán); 15 nhóm và 400 nguồn duy nhất giữ nguyên. Bảy bài có evidence review ở repo cũ, kể cả bài 7 tại comment6133492501/headb8dff434ff75499137bbb10b61122958fdaaafa5. Các evidence này là prior_reviews, không duyệt tổ hợp trong repo mới.

PR nhập bảy bài #40 đã merge trước đợt này (HEAD nền 5831cdc). Evidence review của bảy bài vẫn giữ nguyên, chưa nâng trạng thái chỉ từ việc PR đã merge.

Đợt hiện tại: PR #47, viết đủ 49 bài từ sd-11-001 đến sd-11-049 theo danh sách người dùng giao, trên nhánh codex/cloud-distributed-systems-vi. Nguồn Markdown ghim đã đọc và đối chiếu Git blob; không dùng ảnh nguồn. Review claim và review kỹ thuật đang chờ; chưa user testing/phê duyệt phát hành. Kiểm kho: 56 bài, 0 lỗi schema/nguồn ghim/liên kết. Mobile: Chromium render đủ 49 bài ở 320/375/430 px, mở các phần tùy chọn, không tràn ngang và không có chữ ra khỏi viewBox; chữ hình nhỏ nhất 14,4 px ở 320 px và 17,15 px ở 375 px. Đã xem ảnh mẫu của layout chung. 83 URL tài liệu đối chiếu truy cập được; điều này không thay kiểm chứng claim. Đây là preview Markdown tĩnh, chưa thử trực tiếp trên GitHub/điện thoại.

Theo thứ tự toàn bộ source-map, ID chưa viết đầu tiên vẫn là sd-01-008. Viết nhóm 11 theo yêu cầu hiện tại không đánh dấu các nhóm trước đó là đã hoàn thành.

Metadata JSON duy nhất giữ trạng thái; YAML chỉ id/metadata_ref. Hình/bài giữ nguyên byte khi nhập. User testing chưa thực hiện; không tự merge/deploy hoặc đăng bài.

Base main của đợt Cloud/PR #47 là 5831cdcef96a2c83664e02d83a4e803cf47f259c; adopted_main_sha và destination_base_sha cùng ghi mốc này. Base đích khi nhập bảy bài trước đó là 3edff99314afa7435a4519b700e380eac8d6bc1c, được giữ riêng ở import_destination_base_sha. Mốc main repo cũ giữ previous_repository_main_sha. Review tổ hợp mới vẫn pending.

Kiểm tra đợt Cloud ngày 2026-10-13: sd101_check đạt 56 bài/0 lỗi; layout_check đạt 0 lỗi; git diff --check sạch; tests/test_sd101_check.py đạt 209 test và 2.960 subtest. Các kiểm tra này xác nhận cấu trúc kho và schema, không thay review nội dung.

Review vòng đầu của PR #47 tại 2ba16889c479b8b0f53e3398f10ce50f1b4c5696 nêu ba finding P2: kết quả Lambda (4255709360), số sách trong lịch sử event sourcing (4255709374) và base SHA (4255709389). Đã đối chiếu, xác nhận và sửa; cần review lại head mới. Các bài vẫn là bản thảo, chưa tuyên bố claim đã kiểm chứng đầy đủ.

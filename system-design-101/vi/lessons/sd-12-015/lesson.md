# Thông báo đẩy tới điện thoại hoạt động ra sao?

**Thông báo đẩy không đi thẳng từ máy chủ của ứng dụng tới điện thoại.** Nó đi qua một dịch vụ trung gian, nên điện thoại chỉ cần duy trì kết nối chung thay vì mỗi ứng dụng giữ một kết nối riêng.

![Sáu thẻ dọc: ứng dụng đăng ký với FCM và nhận registration token; ứng dụng gửi token cho máy chủ riêng, máy chủ lưu kèm thời gian; máy chủ ứng dụng gửi tin kèm token qua Admin SDK hoặc HTTP; FCM nhận và xếp hàng, giữ tin nếu thiết bị ngoại tuyến; FCM chuyển qua kênh của nền tảng như Android, APNs của iOS hoặc web; thiết bị hiển thị thông báo. Chú thích: token là địa chỉ của một bản cài ứng dụng, không phải của người dùng.](../../diagrams/sd-12-015-main.svg)

## Từ viết tắt

- **FCM** (Firebase Cloud Messaging) — dịch vụ nhắn tin đám mây của Firebase: nhận tin từ máy chủ ứng dụng, xếp hàng rồi chuyển tới thiết bị.
- **APN** (Apple Push Notification) — thông báo đẩy của Apple: bài nhắc APNs, kênh của iOS mà FCM chuyển tin qua, bên cạnh kênh của Android và web.
- **SDK** (Software Development Kit) — bộ công cụ phát triển phần mềm: thư viện và công cụ để gọi một dịch vụ; bài nói máy chủ ứng dụng gửi tin qua Admin SDK hoặc HTTP.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời; máy chủ ứng dụng có thể gửi tin tới FCM bằng HTTP.

## Đọc hình

**1–2. Đăng ký.** Lần đầu chạy, ứng dụng đăng ký với FCM bằng thông tin cấu hình của dự án và nhận về một **registration token** đại diện cho bản cài này. Ứng dụng gửi token cho **máy chủ của mình**, nơi lưu nó (kèm thời gian cập nhật để sau này dọn token cũ).

**3. Gửi.** Máy chủ ứng dụng gửi tin tới FCM, kèm token của thiết bị đích, bằng Admin SDK hoặc HTTP. Cũng có thể soạn tin tay trong bảng điều khiển.

**4–6. Chuyển tới thiết bị.** FCM nhận tin và xếp hàng nếu thiết bị đang ngoại tuyến, chuyển qua kênh riêng của từng nền tảng (Android, iOS qua APNs, web), và thiết bị hiển thị thông báo theo cấu hình đi kèm.

## Giới hạn cần nhớ

Thông báo đẩy là **nỗ lực tốt nhất**: không bảo đảm tới, không bảo đảm đúng giờ, người dùng có thể tắt thông báo, và token có thể đổi hoặc hết hạn. Đừng chỉ đặt dữ liệu quan trọng trong thông báo; ứng dụng nên tải lại dữ liệu khi được mở.

## Nhìn hình trả lời

Người dùng gỡ ứng dụng rồi cài lại. Token cũ lưu ở máy chủ còn dùng được không? Máy chủ nên làm gì?

<details>
<summary>Xem đáp án</summary>

Thường không còn: token gắn với bản cài cũ. Máy chủ nên nhận token mới từ ứng dụng và xóa các token mà FCM báo không hợp lệ hoặc quá hạn.

</details>

<details>
<summary>Xem sâu hơn: loại tin, thời hạn và quản lý token</summary>

- **Hai loại tin:** tin “thông báo” để hệ thống hiển thị và tin “dữ liệu” để ứng dụng tự xử lý.
- **Thời hạn sống và độ ưu tiên:** tin có thể có thời hạn; hết hạn mà thiết bị chưa nhận được thì bị bỏ. Có thể gộp các tin cùng loại để người dùng không nhận một loạt tin cũ.
- **Quản lý token:** lưu kèm thời gian, làm mới khi ứng dụng báo token đổi, xóa token không hợp lệ.
- **Bảo mật:** thông tin xác thực của máy chủ gửi tin phải nằm ở máy chủ, không đặt trong ứng dụng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-are-notifications-pushed-to-our-phones-or-pcs.md): luồng đăng ký token và gửi thông báo qua Firebase Cloud Messaging.
- [Firebase — FCM](https://firebase.google.com/docs/cloud-messaging): tổng quan dịch vụ.
- [Firebase — Kiến trúc FCM](https://firebase.google.com/docs/cloud-messaging/fcm-architecture): các thành phần và luồng gửi.
- [Firebase — Quản lý token](https://firebase.google.com/docs/cloud-messaging/manage-tokens): làm mới và dọn token.
- [Apple — Máy chủ thông báo từ xa (APNs)](https://developer.apple.com/documentation/usernotifications/setting-up-a-remote-notification-server): kênh nền tảng của iOS.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-015.json).

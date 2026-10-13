# Thiết kế ứng dụng chat 1–1

**Tin nhắn 1–1 nghe đơn giản, nhưng phải đúng thứ tự, không mất và tới đúng nơi dù người nhận đang trực tuyến hay không.** Cách làm: lưu tin trước, rồi mới phân phối theo trạng thái của người nhận.

![Bảy thẻ dọc: Alice đăng nhập và nối WebSocket, dịch vụ hiện diện đánh dấu cô trực tuyến và báo bạn bè; Alice gửi tin cho Bob tới chat service A; dịch vụ đánh số cấp ID duy nhất cho tin; tin được lưu bền; tin đi vào hàng đợi đồng bộ; hệ thống hỏi dịch vụ hiện diện xem Bob có trực tuyến không; nếu có thì chuyển tới chat service B và đẩy qua WebSocket, nếu không thì chuyển cho máy chủ thông báo đẩy tới thiết bị của Bob. Chú thích: lưu trước, rồi mới phân phối.](../../diagrams/sd-12-013-main.svg)

## Đọc hình

**Đăng nhập.** Alice nối **WebSocket** tới máy chủ. Dịch vụ hiện diện ghi nhận cô đang trực tuyến và báo cho bạn bè.

**Gửi tin.** Tin của Alice tới **chat service A**. Dịch vụ đánh số cấp cho nó một **ID duy nhất** để sắp thứ tự, rồi tin được **lưu bền** vào kho tin nhắn. Sau đó nó vào **hàng đợi đồng bộ** để chuyển tới Bob.

**Chọn đường tới Bob.** Trước khi chuyển, hệ thống hỏi dịch vụ hiện diện. Nếu Bob **trực tuyến**, tin đi tới **chat service B** nơi Bob đang kết nối và được đẩy qua WebSocket. Nếu **không**, tin được giao cho máy chủ thông báo đẩy ([xem bài thông báo đẩy](../sd-12-015/lesson.md)) để báo tới thiết bị của Bob.

## Giới hạn cần nhớ

Hiện diện thay đổi từng giây nên có thể cũ: tin có thể bị đẩy sai đường. Vì thế máy khách cần xác nhận đã nhận (ack) và máy chủ gửi lại khi chưa có ack. Gửi lại có thể gây trùng, nên mỗi tin cần ID để loại trùng. Một người còn có thể dùng nhiều thiết bị cùng lúc.

## Nhìn hình trả lời

Bob vừa mất kết nối đúng lúc tin được đẩy đi. Làm sao tin không bị mất?

<details>
<summary>Xem đáp án</summary>

Tin đã được lưu bền trước khi đẩy. Khi nối lại, Bob lấy các tin có ID lớn hơn tin cuối cùng anh đã nhận; ack cho máy chủ biết khi nào cần gửi lại.

</details>

<details>
<summary>Xem sâu hơn: ID, hiện diện và đa thiết bị</summary>

- **ID để sắp thứ tự:** cấp ID tăng dần theo từng cuộc trò chuyện dễ hơn nhiều so với một thứ tự toàn cục duy nhất cho mọi tin.
- **Hiện diện:** thường dựa vào nhịp tim (heartbeat) định kỳ từ máy khách; mất nhịp một thời gian thì coi là ngoại tuyến. Đặt thời hạn nhịp là đánh đổi giữa độ chính xác và chi phí.
- **Đa thiết bị:** mỗi thiết bị có kết nối riêng và cần đồng bộ trạng thái đã đọc.
- **Mã hóa đầu cuối** là một chủ đề riêng, không nằm trong hình.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-design-a-chat-application-like-whatsapp-facebook-messenger-or-discord.md): luồng đăng nhập và gửi tin 1–1 đơn giản hóa.
- [RFC 6455 — WebSocket](https://www.rfc-editor.org/rfc/rfc6455.html): kết nối hai chiều bền vững sau bắt tay.
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging): thông báo đẩy cho thiết bị ngoại tuyến.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-013.json).

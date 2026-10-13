# Email được gửi đi như thế nào?

**Email giống bưu thiếp hơn là tin nhắn tức thời.** Thư được nộp cho một máy chủ, chuyển tiếp qua máy chủ khác, rồi nằm chờ trong hộp thư cho tới khi người nhận mở.

![Năm thẻ dọc: người gửi soạn thư và nộp cho máy chủ của mình; máy chủ gửi hỏi DNS bản ghi MX của tên miền người nhận; thư được chuyển bằng SMTP giữa các máy chủ; máy chủ nhận lưu thư vào hộp thư; người nhận đọc thư bằng IMAP hoặc POP3. Chú thích: SMTP đẩy thư đi, IMAP và POP3 chỉ để đọc thư đã nằm sẵn.](../../diagrams/sd-12-002-main.svg)

## Đọc hình

**MUA** (mail user agent) là ứng dụng bạn dùng, như Outlook hay Thunderbird. **MTA** (mail transfer agent) là máy chủ chuyển thư bằng **SMTP**. **MDA** (mail delivery agent) đặt thư vào hộp thư của người nhận.

**1.** MUA nộp thư cho máy chủ của người gửi. **2.** Máy chủ này tra DNS, tìm bản ghi **MX** của tên miền người nhận để biết gửi tới đâu. **3.** Nó mở phiên SMTP tới máy chủ đó; thư có thể qua thêm vài chặng trung gian. **4.** Máy chủ cuối lưu thư vào hộp thư. **5.** Người nhận đọc thư bằng IMAP, POP3 hoặc webmail.

## Giới hạn cần nhớ

SMTP báo “đã nhận” nghĩa là máy chủ kế tiếp đã nhận trách nhiệm chuyển thư, không có nghĩa người nhận đã đọc, cũng không bảo đảm thư vào hộp thư chính. Thư chưa giao được sẽ được thử lại một thời gian rồi người gửi nhận thông báo lỗi (bounce). Thư còn có thể bị lọc thành spam.

## Nhìn hình trả lời

Bob đọc thư trên điện thoại. Giao thức nào kéo thư từ hộp thư về máy của Bob: SMTP hay IMAP?

<details>
<summary>Xem đáp án</summary>

IMAP (hoặc POP3). SMTP dùng để đẩy thư giữa các máy chủ, và từ ứng dụng của người gửi tới máy chủ của họ.

</details>

<details>
<summary>Xem sâu hơn: IMAP, POP3 và chống giả mạo</summary>

- **POP3** thường tải thư về một thiết bị; **IMAP** giữ thư trên máy chủ và đồng bộ trạng thái (đã đọc, thư mục) giữa nhiều thiết bị.
- Máy chủ nhận có thể kiểm tra **SPF** (máy chủ gửi có được tên miền cho phép không), **DKIM** (chữ ký số trên thư) và **DMARC** (chính sách khi hai kiểm tra đó không khớp tên miền hiển thị). Đây là lớp bảo vệ thêm, không nằm trong đường đi cơ bản.
- Việc nộp thư từ ứng dụng thường dùng cổng và xác thực riêng, tách khỏi việc chuyển thư giữa các máy chủ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-is-email-delivered.md): MUA, MTA, MDA và SMTP/IMAP/POP3 qua phép so sánh với thư giấy.
- [RFC 5321 — SMTP](https://www.rfc-editor.org/rfc/rfc5321.html): chuyển thư giữa máy chủ, bản ghi MX, trách nhiệm sau khi nhận.
- [RFC 9051 — IMAP](https://www.rfc-editor.org/rfc/rfc9051.html): truy cập và đồng bộ hộp thư.
- [RFC 1939 — POP3](https://www.rfc-editor.org/rfc/rfc1939.html): tải thư về thiết bị.
- [RFC 7208 — SPF](https://www.rfc-editor.org/rfc/rfc7208.html): kiểm tra máy chủ gửi.
- [RFC 6376 — DKIM](https://www.rfc-editor.org/rfc/rfc6376.html): chữ ký số trên thư.
- [RFC 7489 — DMARC](https://www.rfc-editor.org/rfc/rfc7489.html): chính sách khi SPF/DKIM không khớp.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-002.json).

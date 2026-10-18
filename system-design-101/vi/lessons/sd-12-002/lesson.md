# Email được gửi đi như thế nào?

**Email giống bưu thiếp hơn là tin nhắn tức thời.** Thư được nộp cho một máy chủ, chuyển tiếp qua máy chủ khác, rồi nằm chờ trong hộp thư cho tới khi người nhận mở.

![Năm thẻ dọc: người gửi soạn thư và nộp cho máy chủ của mình; máy chủ gửi hỏi DNS bản ghi MX của tên miền người nhận, và nếu không có MX thì dùng địa chỉ A hoặc AAAA của chính tên miền; thư được chuyển bằng SMTP giữa các máy chủ; máy chủ nhận lưu thư vào hộp thư; người nhận đọc thư bằng IMAP hoặc POP3. Chú thích: SMTP đẩy thư đi, IMAP và POP3 chỉ để đọc thư đã nằm sẵn.](../../diagrams/sd-12-002-main.svg)

## Từ viết tắt

- **MUA** (Mail User Agent) — ứng dụng thư của người dùng, như Outlook hay Thunderbird: nơi soạn thư, gửi đi và đọc thư.
- **MTA** (Mail Transfer Agent) — máy chủ chuyển thư: nhận thư và chuyển tiếp tới máy chủ khác bằng SMTP.
- **MDA** (Mail Delivery Agent) — thành phần đặt thư vào hộp thư của người nhận.
- **SMTP** (Simple Mail Transfer Protocol) — giao thức truyền thư đơn giản: dùng để gửi thư và chuyển thư giữa các máy chủ thư; trong bài, SMTP đẩy thư đi còn IMAP và POP chỉ để đọc thư đã nằm sẵn.
- **IMAP** (Internet Message Access Protocol) — giao thức truy cập thư Internet: cho người dùng đọc thư ngay trên máy chủ thư, nhiều thiết bị cùng thấy một hộp thư; người nhận có thể đọc thư bằng IMAP, POP hoặc webmail.
- **POP** (Post Office Protocol) — giao thức bưu điện: cho người dùng tải thư về máy; POP3 là phiên bản 3 của giao thức này; một cách khác để người nhận đọc thư.
- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" của Internet, đổi tên miền như example.com thành địa chỉ mạng của máy chủ để biết gửi tới đâu; máy chủ gửi tra DNS để tìm bản ghi MX của tên miền người nhận.
- **MX** (Mail eXchange) — bản ghi trao đổi thư: loại bản ghi DNS chỉ máy chủ nhận thư của một tên miền; máy chủ gửi dùng nó để biết thư phải gửi tới đâu.
- **AAAA** (Quad A) — bản ghi AAAA, đọc là "quad A": loại bản ghi DNS trả về địa chỉ mạng thế hệ mới của một tên; bài dùng nó, cùng bản ghi A, khi tên miền không có bản ghi MX.
- **SPF** (Sender Policy Framework) — khung chính sách người gửi: cho biết máy nào được gửi thư thay mặt một tên miền.
- **DKIM** (DomainKeys Identified Mail) — thư được định danh bằng khóa miền: chữ ký số gắn trên thư để máy nhận kiểm tra thư có đúng từ tên miền gửi không.
- **DMARC** (Domain-based Message Authentication, Reporting and Conformance) — chính sách xử lý thư khi kiểm tra SPF và DKIM không khớp với tên miền hiển thị; bài xếp ba thứ này vào lớp bảo vệ thêm, không nằm trong đường đi cơ bản.

## Đọc hình

**MUA** (mail user agent) là ứng dụng bạn dùng, như Outlook hay Thunderbird. **MTA** (mail transfer agent) là máy chủ chuyển thư bằng **SMTP**. **MDA** (mail delivery agent) đặt thư vào hộp thư của người nhận.

**1.** MUA nộp thư cho máy chủ của người gửi. **2.** Máy chủ này tra DNS, tìm bản ghi **MX** của tên miền người nhận để biết gửi tới đâu. Nếu tên miền không có bản ghi MX nhưng có địa chỉ (A hoặc AAAA), SMTP coi chính tên miền đó như một máy chủ nhận có mức ưu tiên 0. **3.** Nó mở phiên SMTP tới máy chủ đó; thư có thể qua thêm vài chặng trung gian. **4.** Máy chủ cuối lưu thư vào hộp thư. **5.** Người nhận đọc thư bằng IMAP, POP3 hoặc webmail.

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

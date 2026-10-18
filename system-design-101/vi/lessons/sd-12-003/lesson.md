# Thiết kế dịch vụ thư điện tử kiểu Gmail

**Alice dùng Outlook gửi cho Bob dùng Gmail.** Hai nhà cung cấp nói chuyện với nhau bằng SMTP; việc cần thiết kế là điều xảy ra bên trong máy chủ nhận.

![Sáu thẻ dọc: Alice nộp thư cho máy chủ Outlook; máy chủ Outlook tra MX; thư chuyển bằng SMTP sang máy chủ Gmail; máy chủ Gmail kiểm tra nguồn gửi và lọc spam; thư được lưu cùng chỉ mục và nhãn; Bob mở ứng dụng và đồng bộ thư. Chú thích: đây là ví dụ thiết kế, không phải kiến trúc nội bộ thật.](../../diagrams/sd-12-003-main.svg)

## Từ viết tắt

- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" của Internet, đổi tên miền thành địa chỉ mạng của máy chủ; trong bài, máy chủ Outlook tra bản ghi MX của tên miền Gmail để biết thư phải gửi tới đâu.
- **SMTP** (Simple Mail Transfer Protocol) — giao thức truyền thư đơn giản: dùng để gửi thư và chuyển thư giữa các máy chủ thư; Outlook và Gmail trao đổi thư với nhau bằng SMTP.
- **MX** (Mail eXchange) — bản ghi trao đổi thư: loại bản ghi DNS chỉ máy chủ nhận thư của một tên miền; máy chủ Outlook tra MX để biết thư của Alice phải gửi tới đâu.
- **IMAP** (Internet Message Access Protocol) — giao thức truy cập thư Internet: cho người dùng đọc thư ngay trên máy chủ thư, nhiều thiết bị cùng thấy một hộp thư; ứng dụng của Bob lấy thư mới qua IMAP, POP hoặc giao diện riêng của nhà cung cấp.
- **POP** (Post Office Protocol) — giao thức bưu điện: cho người dùng tải thư về máy; POP3 là phiên bản 3 của giao thức này; một lựa chọn để ứng dụng của Bob lấy thư.

## Đọc hình

Đường đi cơ bản của thư đã có ở bài [Email được gửi đi như thế nào?](../sd-12-002/lesson.md). Ở đây ta nhìn vào bước 4–6, nơi máy chủ nhận phải quyết định.

**Nhận và lọc:** kiểm tra nguồn gửi, chống spam và mã độc trước khi cho thư vào hộp thư. **Lưu:** nội dung và tệp đính kèm là dữ liệu lớn, ít sửa; nhãn, trạng thái đã đọc và chỉ mục tìm kiếm là dữ liệu nhỏ, đổi thường xuyên, nên thường được tách riêng. **Đọc:** ứng dụng của Bob lấy thư mới qua IMAP/POP hoặc giao diện riêng của nhà cung cấp.

## Giới hạn cần nhớ

Các nhà cung cấp không công bố đầy đủ kiến trúc nội bộ, nên đây là một thiết kế minh họa để học. Hai điều dễ bỏ sót: thư phải được **lưu bền trước khi** máy chủ nhận báo “đã nhận”, và bộ lọc spam có thể nhầm thư tốt thành thư rác.

## Nhìn hình trả lời

Vì sao máy chủ nhận nên lưu thư bền vững rồi mới báo “đã nhận” cho máy chủ gửi?

<details>
<summary>Xem đáp án</summary>

Khi nghe “đã nhận”, máy chủ gửi coi việc của mình xong và có thể xóa bản của nó. Nếu thư mất sau đó, không bên nào còn bản để thử lại.

</details>

<details>
<summary>Xem sâu hơn: câu hỏi thiết kế khi lượng thư tăng</summary>

- **Hàng đợi và thử lại:** khi máy chủ nhận tạm ngừng, bên gửi xếp thư vào hàng đợi và thử lại theo khoảng cách tăng dần.
- **Tìm kiếm:** mỗi hộp thư cần chỉ mục riêng; thêm thư mới là cập nhật chỉ mục, nên có độ trễ nhỏ giữa lúc thư tới và lúc tìm thấy.
- **Nhiều thiết bị:** nhãn, trạng thái đã đọc và thao tác xóa phải đồng bộ; cần quy tắc khi hai thiết bị sửa cùng lúc.
- **Tệp đính kèm lớn:** thường để ở kho đối tượng và giữ tham chiếu trong thư.

Không mục nào khẳng định Gmail hay Outlook thật sự làm như vậy.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/design-gmail.md): ví dụ Alice (Outlook) gửi cho Bob (Gmail).
- [RFC 5321 — SMTP](https://www.rfc-editor.org/rfc/rfc5321.html): quan hệ máy chủ gửi/nhận và việc nhận trách nhiệm sau khi nhận thư.
- [RFC 5322 — định dạng thư](https://www.rfc-editor.org/rfc/rfc5322.html): cấu trúc phần đầu và nội dung thư.
- [RFC 9051 — IMAP](https://www.rfc-editor.org/rfc/rfc9051.html): đọc và đồng bộ hộp thư.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-003.json).

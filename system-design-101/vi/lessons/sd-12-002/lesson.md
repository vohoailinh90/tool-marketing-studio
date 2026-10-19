# Thư điện tử đi từ người gửi tới người nhận: bốn vai và hai nhóm giao thức

**Một lá thư điện tử không đi thẳng từ máy bạn tới máy người nhận: nó qua hai máy chủ thư, mỗi nơi giữ một vai riêng, và hai nhóm giao thức lo hai việc khác nhau, đẩy thư đi và lấy thư về.**
Tách được bốn vai và hai việc đó, bạn đọc được hầu hết sơ đồ gửi thư và đoán được thư kẹt ở đâu khi có lỗi.

![Hai khung. Khung một, bốn vai nối nhau: ứng dụng thư của người gửi, máy chủ thư của người gửi, máy chủ thư của người nhận, chương trình giao thư bỏ thư vào hộp thư của người nhận. Khung hai, ba điều cần nhớ: SMTP đẩy thư từ ứng dụng của người gửi tới máy chủ của họ rồi sang máy chủ của người nhận, còn IMAP hoặc POP3 là việc riêng: ứng dụng của người nhận lấy thư về từ hộp thư; máy chủ gửi tìm máy chủ nhận nhờ bản ghi MX trong DNS; nếu máy chủ nhận chưa sẵn sàng thì thư xếp hàng và được thử lại.](../../diagrams/sd-12-002-main.svg)

## Từ viết tắt

- **MUA** (Mail User Agent) — ứng dụng thư của người dùng: chương trình bạn soạn và đọc thư, như Outlook hay ứng dụng Gmail.
- **MTA** (Mail Transfer Agent) — chương trình chuyển thư: nhận thư từ MUA hoặc từ MTA khác rồi chuyển tiếp tới nơi gần đích hơn.
- **MDA** (Mail Delivery Agent) — chương trình giao thư: bỏ thư đã nhận vào hộp thư của người nhận trên máy chủ.
- **SMTP** (Simple Mail Transfer Protocol) — giao thức truyền thư đơn giản: ngôn ngữ để đẩy thư đi, từ ứng dụng sang máy chủ và giữa các máy chủ.
- **IMAP** (Internet Message Access Protocol) — giao thức truy cập thư Internet: cho ứng dụng đọc thư vẫn nằm trên máy chủ, nhiều thiết bị cùng thấy một hộp thư.
- **POP** (Post Office Protocol) — giao thức bưu điện: bản đang dùng là POP3; cho ứng dụng lấy thư về máy, thường để máy chủ xóa bản của nó.
- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" đổi tên miền thành thông tin để máy tìm nhau; ở đây nó cho biết máy chủ nào nhận thư của một tên miền.
- **MX** (Mail eXchange) — bản ghi trao đổi thư: một dòng trong DNS chỉ ra máy chủ nhận thư của một tên miền.
- **RFC** (Request For Comments) — tài liệu xin ý kiến: loạt văn bản kỹ thuật của Internet, trong đó có chuẩn SMTP.

## Đọc hình

**Bốn vai.** MUA là phần mềm bạn mở ra để soạn thư. MTA là người chuyển phát: nhận thư rồi chuyển tiếp, và trên đường đi có thể có nhiều MTA. MDA đứng ở cuối: bỏ thư vào hộp thư của người nhận. Hộp thư nằm trên máy chủ của người nhận, không nằm trên điện thoại hay máy tính của họ.

**Đẩy thư đi.** MUA đưa thư cho máy chủ của người gửi bằng SMTP. Máy chủ đó nhìn phần tên miền sau dấu @, hỏi DNS bản ghi MX của tên miền, và biết phải nói chuyện với máy chủ nào. Nếu tên miền không có bản ghi MX thì chuẩn SMTP (RFC 5321, mục 5.1) cho dùng chính địa chỉ của tên miền. Rồi hai máy chủ trao thư với nhau, cũng bằng SMTP.

**Lấy thư về.** Máy chủ nhận không chạy tới đưa thư vào máy bạn. Thư nằm trong hộp thư cho tới khi MUA của người nhận hỏi: bằng IMAP nếu muốn để thư trên máy chủ, bằng POP3 nếu muốn tải về.

**Khi máy chủ nhận chưa sẵn sàng.** Máy chủ gửi không vứt thư. RFC 5321 (mục 4.5.4.1) yêu cầu giữ thư trong hàng đợi và thử lại, khuyến nghị cách nhau ít nhất 30 phút và bỏ cuộc sau khoảng 4 đến 5 ngày; khi bỏ cuộc, người gửi nhận thư báo lỗi.

## Giới hạn cần nhớ

Bài nguồn viết MTA là "mail transmission agent"; tên trong chuẩn SMTP là Mail Transfer Agent, nên bài này dùng tên đó. Bài chỉ vẽ đường đi bình thường của một thư. Việc kiểm tra thư rác, xác thực người gửi và mã hóa kết nối giữa các máy chủ là những lớp có thật nhưng nằm ngoài hình và ngoài bài này. Hai con số của hàng đợi là *khuyến nghị* của chuẩn; mỗi phần mềm máy chủ tự đặt giá trị của nó.

## Nhìn hình trả lời

Máy chủ của người nhận bảo trì ba tiếng đúng lúc bạn bấm gửi. Thư của bạn đã mất chưa, và ai quyết định chuyện gì xảy ra tiếp?

<details>
<summary>Xem đáp án</summary>

Chưa mất. Máy chủ *của bạn* (MTA gửi) giữ thư trong hàng đợi và thử lại sau một khoảng, nên ba tiếng chờ thường là chuyện thư tới chậm chứ không phải thư mất. Chỉ khi nó thử mãi tới hạn bỏ cuộc mà vẫn thất bại, nó mới gửi thư báo lỗi về cho bạn.
Phần lập luận về ba tiếng là suy ra từ khuyến nghị của RFC 5321; chưa thử với một phần mềm máy chủ cụ thể.

</details>

<details>
<summary>Xem sâu hơn: điều đã đổi so với bài nguồn</summary>

Bài nguồn so sánh đường đi của thư với bưu điện: hòm thư, bưu cục, hòm thư người nhận. Bài này bỏ phép so sánh đó để dành chỗ cho hai chi tiết mà nguồn không có: máy chủ gửi tìm máy chủ nhận bằng bản ghi MX, và thư được xếp hàng, thử lại khi đích chưa sẵn sàng.
Hai chi tiết đó, cùng số cổng và các giá trị hàng đợi, lấy từ trí nhớ của người biên soạn về RFC 5321; trang chuẩn chưa mở được trong phiên viết bài nên chưa đối chiếu từng câu, ngoài hai con số 30 phút và 4 đến 5 ngày đã khớp với một trích dẫn của RFC.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-is-email-delivered.md): các vai MUA, MTA, MDA và hai giao thức lấy thư. Phần bản ghi MX và hàng đợi là của người biên soạn.
- RFC 5321 (Simple Mail Transfer Protocol) mục 2.3, 5.1 và 4.5.4.1: tên các vai, tìm máy chủ nhận và thử lại (nhớ lại từ chuẩn; chưa mở được trang trong phiên này).

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

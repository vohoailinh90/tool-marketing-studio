# SWIFT: tin nhắn thanh toán giữa các ngân hàng

**SWIFT là hệ thống nhắn tin an toàn nối các ngân hàng trên thế giới. Một tin thanh toán được lưu lại ở bên gửi, chuyển sang bên nhận, rồi một báo cáo xác nhận chạy ngược về: hai lần lưu, hai lần xác nhận.**

![Ba khung nối nhau, mỗi khung một lược đồ. Khung một, phía ngân hàng gửi: Bank A gửi tin tới Regional Processor A, nơi kiểm tra định dạng rồi chuyển cho Slice Processor A lưu, sau đó Bank A nhận ACK hoặc NAK. Khung hai, sang London: Slice Processor A chuyển tin cho Regional Processor B, nơi gán số MON; Slice Processor B kiểm tra MON và cho phép gửi. Khung ba, phía ngân hàng nhận: Regional Processor B gửi tin cho Bank B, Bank B trả UAK hoặc UNK, báo cáo được lưu và một bản sao về lại Slice Processor A.](../../diagrams/sd-07-005-main.svg)

## Từ viết tắt

- **SWIFT** (Society for Worldwide Interbank Financial Telecommunication) — hiệp hội viễn thông tài chính liên ngân hàng toàn cầu: hệ thống nhắn tin an toàn chính nối các ngân hàng trên thế giới.
- **ACK** (ACKnowledgment) — xác nhận: Bank A nhận ACK nghĩa là tin sẽ được gửi tới Bank B.
- **NAK** (Negative AcKnowledgment) — xác nhận âm: Bank A nhận NAK nghĩa là tin sẽ *không* được gửi tới Bank B.
- **MON** (Message Output Number) — số đầu ra của tin: mã số duy nhất mà Regional Processor B gán cho tin trước khi gửi cho Bank B.
- **UAK** (User AcKnowledgment) — xác nhận dương của người dùng: Bank B đã nhận tin không có lỗi.
- **UNK** (User NegativeacKnowledgment) — xác nhận âm của người dùng: Bank B nhận tin nhưng kiểm tra tổng kiểm (checksum) bị lỗi.

## Đọc hình

Nguồn dùng ví dụ một tin đi từ Bank A ở New York tới Bank B ở London. Có hai loại máy xử lý ở mỗi bên: **Regional Processor** (bộ xử lý vùng) kiểm tra tin đầu vào và xếp hàng tin đầu ra, còn **Slice Processor** lưu và định tuyến tin một cách an toàn.

**1. Ngân hàng A gửi (bước 1 đến 5).** Bank A gửi tin với chi tiết chuyển tiền tới Regional Processor A, đích là Bank B. Regional Processor kiểm tra định dạng rồi chuyển sang Slice Processor A. Slice Processor A lưu tin, báo lại đã lưu. Khi đó Regional Processor A trả cho Bank A một ACK hoặc NAK.

**2. Sang London (bước 6 đến 10).** Slice Processor A gửi tin tới Regional Processor B ở London. Regional Processor B lưu tạm, gán cho tin một số MON duy nhất rồi gửi sang Slice Processor B. Slice Processor B kiểm tra MON và cho phép Regional Processor B gửi tin cho Bank B.

**3. Ngân hàng B nhận (bước 11 đến 17).** Regional Processor B gửi tin cho Bank B; Bank B nhận và lưu, rồi trả UAK hoặc UNK. Regional Processor B làm báo cáo từ phản hồi đó và gửi cho Slice Processor B, nơi lưu lại. Slice Processor B gửi một bản sao báo cáo về Slice Processor A, nơi cũng lưu lại.

Điều đáng nhìn kỹ: ACK ở bước 5 đến *trước* khi Bank B có tin. ACK chỉ nói tin đã được nhận và lưu an toàn ở phía gửi và sẽ được gửi đi. Việc Bank B nhận đúng hay lỗi thì chỉ UAK hoặc UNK, ở bước 13, mới cho biết. Phần kiểm tra MON và báo cáo ở cuối giúp cả hai phía có cùng một bản ghi về chuyện gì đã xảy ra với tin.

## Giới hạn cần nhớ

SWIFT là hệ thống *nhắn tin*. Người biên soạn hiểu rằng tin chứa chỉ dẫn chuyển tiền, còn tiền thật được thanh toán qua các kênh và tài khoản khác giữa các ngân hàng; nguồn chỉ gọi SWIFT là hệ thống nhắn tin và không nói về việc tiền đi đâu, nên điểm này chưa được đối chiếu với tài liệu của SWIFT.
Nguồn mô tả một luồng chuẩn của ví dụ; mạng thật có nhiều loại tin và nhiều tình huống lỗi mà bài không đi vào.

## Nhìn hình trả lời

Bank A nhận ACK. Điều này có nghĩa Bank B đã nhận được tin chưa? Và nếu Bank B nhận tin nhưng kiểm tra tổng kiểm bị lỗi, bên gửi biết qua tin nào?

<details>
<summary>Xem đáp án</summary>

Chưa. ACK chỉ cho biết tin đã qua kiểm tra định dạng, đã được lưu ở phía gửi và sẽ được gửi tới Bank B; lúc đó tin còn chưa rời New York. Bank B có nhận được hay không thì phải chờ phản hồi từ Bank B.
Nếu tổng kiểm lỗi, Bank B trả UNK (còn UAK là nhận không lỗi). Regional Processor B ghi vào báo cáo, báo cáo được lưu ở Slice Processor B và một bản sao gửi về Slice Processor A. Nguồn mô tả đường đi của báo cáo; việc ngân hàng gửi xử lý tiếp ra sao nguồn không nói.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê 17 bước liền nhau. Bài này chia chúng thành ba lược đồ theo bên đang hoạt động, đưa các tên viết tắt vào phần giải thích riêng, và nhấn vào việc ACK đến sớm hơn việc giao tin. Bước 7 (lưu tạm) và các bước kiểm tra MON được gộp trong hình nhưng vẫn có trong phần chữ.
Bài chưa đối chiếu với tài liệu của SWIFT.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/swift-payment-messaging-system.md): vai trò của SWIFT, 17 bước của luồng tin, và ý nghĩa ACK, NAK, MON, UAK, UNK. Nhận xét về việc ACK đến trước khi giao tin là suy ra từ định nghĩa của chính nguồn; phần "SWIFT chỉ nhắn tin" là kiến thức chung của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

# Hệ sinh thái thanh toán qua một giao dịch thẻ

**Một giao dịch thẻ đi qua nhiều bên: ngân hàng phát hành thẻ, ISO hoặc MSP đăng ký cho người bán, cổng thanh toán, bộ xử lý bên thu, mạng thẻ và bộ xử lý bên phát hành. Mỗi công ty thanh toán thường bắt đầu từ một mảng rồi mở rộng sang nhiều mảng.**
Đi theo giao dịch là cách dễ nhất để nhớ ai làm gì.

![Ba khung. Khung một, chuẩn bị (bước 0 và 1): chủ thẻ mở tài khoản ở ngân hàng phát hành và nhận thẻ; người bán đăng ký với ISO hoặc MSP, đơn vị này hợp tác với bộ xử lý thanh toán để mở tài khoản người bán. Khung hai, bên thu (bước 2 đến 5): cổng thanh toán nhận giao dịch và thông tin thanh toán, chuyển cho bộ xử lý bên thu, bộ xử lý này gửi giao dịch cho mạng thẻ và giữ tài khoản người bán lúc quyết toán. Khung ba, bên phát hành (bước 6 đến 8): bộ xử lý bên phát hành nói chuyện với mạng thẻ thay ngân hàng phát hành, xác nhận và vận hành tài khoản của khách.](../../diagrams/sd-07-014-main.svg)

## Từ viết tắt

- **ISO** (Independent Sales Organization) — tổ chức bán hàng độc lập: đơn vị mà người bán đăng ký cùng để bán tại cửa hàng.
- **MSP** (Member Service Provider) — nhà cung cấp dịch vụ thành viên: gọi chung với ISO; người bán đăng ký với một trong hai.

## Đọc hình

Nguồn mở đầu bằng câu hỏi: các startup công nghệ tài chính tìm cơ hội mới thế nào giữa vô số công ty thanh toán, và PayPal, Stripe, Square thực sự làm gì. Phần đáp nằm ở bức sơ đồ liệt kê các công ty theo từng mảng; bài này chỉ kể lại các bước.

**Chuẩn bị (bước 0 và 1).** Chủ thẻ mở tài khoản ở *ngân hàng phát hành* (issuing bank) và nhận thẻ ghi nợ hoặc thẻ tín dụng. Người bán đăng ký với một ISO hoặc MSP để bán tại cửa hàng. ISO hoặc MSP hợp tác với các *bộ xử lý thanh toán* (payment processor) để mở tài khoản người bán.

**Bên thu (bước 2 đến 5): quá trình "acquiring".** *Cổng thanh toán* (payment gateway) nhận giao dịch mua và thu thập thông tin thanh toán, rồi chuyển cho một bộ xử lý thanh toán, bộ này dùng thông tin của khách để thu tiền. Bộ xử lý bên thu gửi giao dịch cho *mạng thẻ* (card network). Nó cũng sở hữu và vận hành tài khoản người bán trong lúc quyết toán, và việc quyết toán này không xảy ra theo thời gian thực.

**Bên phát hành (bước 6 đến 8): quá trình "issuing".** *Bộ xử lý bên phát hành* nói chuyện với mạng thẻ thay mặt ngân hàng phát hành. Nó xác nhận và vận hành tài khoản của khách.

Nguồn còn lưu ý một điều ở cuối: các công ty thanh toán thường bắt đầu từ một mảng, rồi mở rộng ra nhiều mảng.

## Giới hạn cần nhớ

Bài nguồn là một bức sơ đồ kèm ba đoạn chữ ngắn; chữ không nói bước nào dùng công ty nào, nên bài này không đặt PayPal, Stripe hay Square vào bước nào. Nó cũng không nói điều gì xảy ra khi thẻ bị từ chối, và quyết toán "không theo thời gian thực" được giữ nguyên, không bổ sung thời gian cụ thể.
Câu hỏi "tìm cơ hội ở đâu" nguồn không trả lời bằng chữ; bài này không trả lời thay.

## Nhìn hình trả lời

Người bán đăng ký với ISO hoặc MSP chứ không đăng ký thẳng với mạng thẻ. Theo nguồn, ISO hoặc MSP làm gì để người bán có tài khoản? Và bộ xử lý bên phát hành làm việc với ngân hàng phát hành thế nào?

<details>
<summary>Xem đáp án</summary>

ISO hoặc MSP hợp tác với các bộ xử lý thanh toán để mở tài khoản người bán (bước 1). Nguồn không nói thêm thủ tục cụ thể.
Bộ xử lý bên phát hành nói chuyện với mạng thẻ thay mặt ngân hàng phát hành, đồng thời xác nhận và vận hành tài khoản của khách (bước 6 đến 8). Nguồn không nói ngân hàng phát hành và bộ xử lý này trao đổi gì với nhau.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn viết ba đoạn theo dải bước (0 đến 1, 2 đến 5, 6 đến 8) và kèm một sơ đồ liệt kê công ty theo mảng. Bài này giữ nguyên ba dải đó thành ba khung, đưa chữ viết tắt ISO và MSP vào phần giải nghĩa, và không chép tên các công ty trên sơ đồ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-payments-ecosystem.md): ba dải bước của một giao dịch thẻ: chuẩn bị, bên thu, bên phát hành. Phần giới hạn và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

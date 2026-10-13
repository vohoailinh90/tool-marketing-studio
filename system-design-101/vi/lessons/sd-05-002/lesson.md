# Gõ google.com vào trình duyệt thì chuyện gì xảy ra?

**Một câu hỏi phỏng vấn quen thuộc, và cách trả lời tốt là kể đúng thứ tự.** Từ lúc nhấn Enter tới lúc trang hiện ra
có sáu việc nối nhau: kiểm tra cache, tra DNS, mở kết nối, gửi yêu cầu HTTP, nhận phản hồi, dựng trang.

![Sáu thẻ nối nhau từ trên xuống. 1 Nhập địa chỉ: gõ rồi nhấn Enter. 2 Kiểm tra cache: đã có gì dùng lại được chưa. 3 Tra DNS: tên miền ra địa chỉ IP. 4 Mở kết nối: bắt tay TCP, HTTPS thêm TLS. 5 Yêu cầu HTTP: gửi yêu cầu, nhận HTML. 6 Dựng trang: DOM, CSSOM, layout, paint. Ghi chú: đây là đường chính, không phải đường duy nhất.](../../diagrams/sd-05-002-main.svg)

## Từ viết tắt

- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" của Internet, đổi tên miền như example.com thành địa chỉ IP.
- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ và chuyển gói tin giữa các máy; địa chỉ IP là địa chỉ của một máy trên mạng.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: tạo kết nối đáng tin cậy bằng bắt tay ba bước SYN, SYN-ACK, ACK.
- **SYN** (SYNchronize) — "đồng bộ": gói đầu tiên của bắt tay TCP, báo "tôi muốn mở kết nối".
- **ACK** (ACKnowledgement) — "xác nhận": gói báo "tôi đã nhận được"; bước cuối của bắt tay TCP.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa giữ kín dữ liệu đi giữa trình duyệt và máy chủ.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu (request) và máy chủ gửi trả lời (response).
- **HTTPS** (HyperText Transfer Protocol Secure) — HTTP chạy trên TLS: cách gửi yêu cầu và trả lời như HTTP nhưng nội dung được mã hóa.
- **HSTS** (HTTP Strict Transport Security) — "bảo mật truyền tải nghiêm ngặt của HTTP": máy chủ dặn trình duyệt lần sau chỉ truy cập qua HTTPS.
- **HTML** (HyperText Markup Language) — ngôn ngữ đánh dấu siêu văn bản: văn bản dùng thẻ để mô tả cấu trúc của một trang web.
- **DOM** (Document Object Model) — mô hình đối tượng tài liệu: cây các phần tử của trang mà trình duyệt dựng từ HTML; JavaScript có thể sửa cây này.
- **CSS** (Cascading Style Sheets) — bảng kiểu xếp tầng: các luật mô tả màu sắc, cỡ chữ và cách bố trí của trang.
- **CSSOM** (CSS Object Model) — mô hình đối tượng CSS: các luật CSS sau khi trình duyệt đọc xong, xếp thành cấu trúc để tra cứu.
- **QUIC** (Quick UDP Internet Connections) — tên gọi ban đầu của giao thức truyền tải mà HTTP/3 dùng thay cho TCP; ngày nay QUIC thường được dùng như một tên riêng.

## Đọc hình

**1–2. Nhập địa chỉ và kiểm tra cache.** Trước khi ra mạng, trình duyệt xem đã có gì dùng lại được chưa:
một phản hồi đã lưu, hoặc địa chỉ IP đã tra gần đây.

**3. Tra DNS.** DNS là hệ thống đặt tên phân cấp và phi tập trung, đổi tên miền thành địa chỉ IP.
Nếu chưa ai trong chuỗi cache biết, trình duyệt (qua hệ điều hành) hỏi một máy chủ phân giải đệ quy. Máy đó tự hỏi lần xuống từ máy chủ gốc:
máy chủ gốc và máy chủ tên miền cấp cao chỉ trả về chỉ dẫn tới máy chủ kế tiếp, còn máy chủ có thẩm quyền của tên miền trả địa chỉ IP.

**4. Mở kết nối.** Với HTTP qua TCP, hai bên bắt tay ba bước SYN, SYN-ACK, ACK. Với địa chỉ HTTPS, thêm một bước
bắt tay TLS để mã hóa đường truyền.

**5. Yêu cầu HTTP.** Trình duyệt gửi yêu cầu; máy chủ trả HTML. Trang thường kéo thêm CSS, JavaScript, ảnh bằng các yêu cầu khác.

**6. Dựng trang.** Phân tích HTML và CSS, tính layout, vẽ ra màn hình.

## Giới hạn cần nhớ

Đây là đường chính chứ không phải đường duy nhất. Có cache thì bỏ được DNS hoặc cả yêu cầu mạng; kết nối đã mở có thể được dùng lại;
HTTP/3 chạy trên QUIC thay vì bắt tay TCP. Khi trả lời phỏng vấn, hãy nói rõ bạn đang kể trường hợp cơ bản.

## Nhìn hình trả lời

Trình duyệt vừa tra địa chỉ IP của tên miền đó cách đây ít phút và còn lưu. Bước nào trong hình có thể được bỏ qua?

<details>
<summary>Xem đáp án</summary>

Bước 3, tra DNS: địa chỉ IP đã có sẵn trong cache. Các bước từ mở kết nối trở đi vẫn cần, trừ khi có phản hồi đã lưu dùng lại được
hoặc một kết nối cũ còn mở.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn chỉ kể bắt tay TCP của HTTP/1.1 và không nhắc TLS. Hình này thêm bước TLS cho địa chỉ HTTPS, vì
với HTTPS đường truyền được mã hóa bằng TLS; HSTS còn khiến trình duyệt tự nâng các lần truy cập HTTP sau đó lên HTTPS.

Chi tiết dựng trang nằm ở bước 6 và được giải thích riêng trong bài về cách trình duyệt dựng trang.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-happens-when-you-type-google.md): tám bước.
- [MDN — DNS](https://developer.mozilla.org/en-US/docs/Glossary/DNS), [TCP handshake](https://developer.mozilla.org/en-US/docs/Glossary/TCP_handshake), [TLS](https://developer.mozilla.org/en-US/docs/Glossary/TLS): các thuật ngữ.
- [MDN — Connection management in HTTP/1.x](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Connection_management_in_HTTP_1.x): kết nối ngắn hạn và kết nối bền (dùng lại).
- [BIND 9 — giới thiệu DNS và truy vấn](https://github.com/isc-projects/bind9/blob/main/doc/arm/intro-dns-bind.inc.rst): truy vấn đệ quy của stub resolver, truy vấn lặp từ máy chủ gốc, chỉ dẫn (referral). Đọc từ bản clone của kho.
- [MDN — HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching) và [Strict-Transport-Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security): cache dùng lại phản hồi; HSTS.

Đã đọc nguồn ngày 2026-10-13. Các trang MDN được đọc từ bản clone của kho mdn/content (developer.mozilla.org không mở được trong môi trường biên soạn).
Luồng phân giải đệ quy và chỉ dẫn được đối chiếu với tài liệu BIND 9; việc cache DNS ở nhiều tầng (trình duyệt, hệ điều hành, mạng cục bộ, nhà cung cấp) lấy từ bài nguồn, chưa đối chiếu riêng. Bài viết và hình được thiết kế độc lập.

# Tám giao thức mạng phổ biến

**Giao thức là thỏa thuận về cách hai bên nói chuyện.** Tám cái dưới đây hay bị trộn lẫn vì chúng xếp chồng lên nhau: cái trên mượn cái dưới để chuyển dữ liệu.

![Ba khung dọc: trên TCP gồm HTTP lấy tài nguyên web (bản 1.1 và 2), HTTPS là HTTP trong TLS cho bản 1.1 và 2, WebSocket bắt tay bằng HTTP rồi hai chiều và cũng chạy trên HTTP/3, SMTP chuyển thư, FTP chuyển file bằng kênh điều khiển và kênh dữ liệu; trên UDP gồm UDP gửi gói không kết nối và HTTP/3 chạy trên QUIC trên UDP và QUIC đã gồm TLS 1.3; nền gồm TCP kết nối, giao đủ, đúng thứ tự.](../../diagrams/sd-15-011-main.svg)

## Đọc hình

- **TCP:** tạo kết nối, giao dữ liệu đủ và đúng thứ tự. Nhiều giao thức ứng dụng chạy trên đó.
- **HTTP:** cách lấy tài nguyên web; mô hình client hỏi, server đáp.
- **HTTPS:** HTTP được bảo vệ bằng mã hóa. Với HTTP/1.1 và HTTP/2, HTTP chạy trong kênh TLS trên TCP. Với HTTP/3, HTTP chạy thẳng trên các luồng QUIC; QUIC tích hợp bắt tay TLS 1.3 và dùng khóa của nó để bảo vệ gói, nên HTTP/3 không nằm trong lớp bản ghi TLS riêng.
- **WebSocket:** bắt đầu bằng yêu cầu HTTP rồi nâng lên kênh hai chiều, cho phép server chủ động đẩy dữ liệu. Chạy trên TCP với HTTP/1.1 và HTTP/2, hoặc trên một luồng của kết nối HTTP/3 (QUIC).
- **SMTP:** chuyển thư điện tử giữa các máy chủ thư (và từ ứng dụng gửi lên máy chủ thư).
- **FTP:** chuyển file; dùng một kết nối điều khiển và một kết nối dữ liệu riêng.
- **UDP:** gửi từng gói độc lập, không kết nối, không bảo đảm giao.
- **HTTP/3:** HTTP chạy trên QUIC; QUIC chạy trên UDP và tự lo gửi lại, mã hóa.

## Giới hạn cần nhớ

Bảng này là bản đồ, không phải danh sách đầy đủ. HTTP có phiên bản chạy trên TCP (HTTP/1.1, HTTP/2) và phiên bản trên QUIC (HTTP/3); ngữ nghĩa HTTP không đổi nhưng đường vận chuyển khác. HTTP/3 giảm một số điểm nghẽn của TCP, không có nghĩa trang nào cũng nhanh hơn. FTP gửi thông tin ở dạng thô nếu không có lớp bảo vệ; SFTP là giao thức khác, chạy trên SSH.

## Nhìn hình thử trả lời

Một ứng dụng chat mở WebSocket tới server. Kết nối bắt đầu bằng giao thức nào, và chạy trên nền nào?

<details>
<summary>Xem đáp án</summary>

Với HTTP/1.1, bắt đầu bằng một yêu cầu HTTP xin nâng cấp lên WebSocket; sau khi được chấp nhận, hai bên trao đổi khung WebSocket trên cùng kết nối TCP (thường trong TLS nếu dùng wss). Với HTTP/2 và HTTP/3 dùng CONNECT mở rộng và chạy trên một luồng của kết nối đó: TCP với HTTP/2, QUIC với HTTP/3.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **HTTPS không phải giao thức riêng hoàn toàn:** là HTTP được bảo vệ bằng TLS (đặt trong TLS trên TCP, hoặc chạy trên QUIC với HTTP/3); cổng mặc định khác.
- **SMTP:** máy chủ với máy chủ thường dùng cổng 25; ứng dụng gửi thư thường qua cổng submission 587.
- **FTP:** kênh điều khiển gửi lệnh, kênh dữ liệu mang file; chế độ chủ động và bị động khác nhau ở bên nào mở kênh dữ liệu.
- **QUIC:** tích hợp TLS 1.3 và nhiều luồng độc lập trong một kết nối.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/explaining-8-popular-network-protocols-in-1-diagram.md).
- [RFC 9110 — HTTP](https://www.rfc-editor.org/rfc/rfc9110), [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114), [RFC 9000 — QUIC](https://www.rfc-editor.org/rfc/rfc9000).
- [RFC 6455 — WebSocket](https://www.rfc-editor.org/rfc/rfc6455), [RFC 8441](https://www.rfc-editor.org/rfc/rfc8441), [RFC 9220](https://www.rfc-editor.org/rfc/rfc9220), [RFC 9293 — TCP](https://www.rfc-editor.org/rfc/rfc9293), [RFC 768 — UDP](https://www.rfc-editor.org/rfc/rfc768).
- [RFC 5321 — SMTP](https://www.rfc-editor.org/rfc/rfc5321), [RFC 959 — FTP](https://www.rfc-editor.org/rfc/rfc959), [RFC 8446 — TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446).

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

# Tám giao thức mạng phổ biến

**Giao thức là thỏa thuận về cách hai bên nói chuyện.** Tám cái dưới đây hay bị trộn lẫn vì chúng xếp chồng lên nhau: cái trên mượn cái dưới để chuyển dữ liệu.

![Ba khung dọc: trên TCP gồm HTTP lấy tài nguyên web, HTTPS là HTTP trong TLS, WebSocket bắt tay bằng HTTP rồi hai chiều, SMTP chuyển thư, FTP chuyển file bằng kênh điều khiển và kênh dữ liệu; trên UDP gồm UDP gửi gói không kết nối và HTTP/3 chạy trên QUIC trên UDP; nền gồm TCP kết nối, giao đủ, đúng thứ tự.](../../diagrams/sd-15-011-main.svg)

## Đọc hình

- **TCP:** tạo kết nối, giao dữ liệu đủ và đúng thứ tự. Nhiều giao thức ứng dụng chạy trên đó.
- **HTTP:** cách lấy tài nguyên web; mô hình client hỏi, server đáp.
- **HTTPS:** HTTP chạy trong kênh được mã hóa bởi TLS.
- **WebSocket:** bắt đầu bằng yêu cầu HTTP rồi nâng lên kênh hai chiều, cho phép server chủ động đẩy dữ liệu.
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

Bắt đầu bằng một yêu cầu HTTP xin nâng cấp lên WebSocket; sau khi được chấp nhận, hai bên trao đổi khung WebSocket trên cùng kết nối TCP (thường trong TLS nếu dùng wss).

</details>

<details>
<summary>Xem sâu hơn</summary>

- **HTTPS không phải giao thức riêng hoàn toàn:** là HTTP đặt trong TLS; cổng mặc định khác.
- **SMTP:** máy chủ với máy chủ thường dùng cổng 25; ứng dụng gửi thư thường qua cổng submission 587.
- **FTP:** kênh điều khiển gửi lệnh, kênh dữ liệu mang file; chế độ chủ động và bị động khác nhau ở bên nào mở kênh dữ liệu.
- **QUIC:** tích hợp TLS 1.3 và nhiều luồng độc lập trong một kết nối.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/explaining-8-popular-network-protocols-in-1-diagram.md).
- [RFC 9110 — HTTP](https://www.rfc-editor.org/rfc/rfc9110), [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114), [RFC 9000 — QUIC](https://www.rfc-editor.org/rfc/rfc9000).
- [RFC 6455 — WebSocket](https://www.rfc-editor.org/rfc/rfc6455), [RFC 9293 — TCP](https://www.rfc-editor.org/rfc/rfc9293), [RFC 768 — UDP](https://www.rfc-editor.org/rfc/rfc768).
- [RFC 5321 — SMTP](https://www.rfc-editor.org/rfc/rfc5321), [RFC 959 — FTP](https://www.rfc-editor.org/rfc/rfc959), [RFC 8446 — TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446).

Đã đọc nguồn ngày 2026-10-13. Bài viết và hình được thiết kế độc lập; không giữ nhận định về VR của bài nguồn vì không có bằng chứng kèm theo.

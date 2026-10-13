# 18 cổng mạng thường gặp

**Địa chỉ IP tìm ra máy; cổng (port) chỉ ra dịch vụ trên máy đó.** Một máy có thể chạy web, thư và cơ sở dữ liệu cùng lúc; số cổng cho biết gói tin dành cho dịch vụ nào.

![Sáu khung dọc chia mười tám cổng theo mục đích: truy cập từ xa gồm 22 SSH, 23 Telnet, 3389 RDP; web gồm 80 HTTP, 443 HTTPS; thư điện tử gồm 25 SMTP, 110 POP3, 143 IMAP; hạ tầng mạng gồm 53 DNS dùng UDP và TCP, 67 và 68 DHCP dùng UDP, 123 NTP dùng UDP; chia sẻ tệp gồm 21 FTP, 139 NetBIOS, 445 SMB; cơ sở dữ liệu gồm 1521 Oracle, 3306 MySQL, 5432 PostgreSQL. Cổng mặc định chỉ là quy ước.](../../diagrams/sd-01-012-main.svg)

## Đọc hình

Cổng là một số 16 bit (0 đến 65535). Kết hợp với giao thức vận chuyển (TCP hoặc UDP), nó xác định điểm cuối của một kết nối trên máy. IANA chia dải số thành cổng hệ thống (0–1023), cổng đã đăng ký (1024–49151) và cổng động (49152–65535), dải sau thường được máy khách dùng tạm khi kết nối đi.

Mười tám cổng trong hình gom theo việc chúng làm:

- **Truy cập từ xa:** SSH (22) là cách đăng nhập có mã hóa; Telnet (23) cũ và không mã hóa; RDP (3389) là màn hình từ xa của Windows.
- **Web:** HTTP (80) và HTTPS (443).
- **Thư:** SMTP (25) gửi và chuyển thư; POP3 (110) và IMAP (143) cho người dùng đọc thư.
- **Hạ tầng mạng:** DNS (53) dùng cả UDP và TCP; DHCP dùng UDP 67 cho máy chủ và 68 cho máy khách; NTP (123) đồng bộ giờ.
- **Chia sẻ tệp:** FTP (21), NetBIOS (139) và SMB (445).
- **Cơ sở dữ liệu:** Oracle (1521), MySQL (3306), PostgreSQL (5432).

## Giới hạn cần nhớ

Số cổng mặc định chỉ là quy ước: dịch vụ có thể chạy ở cổng khác, và một cổng mở không bảo đảm đúng dịch vụ đó đang chạy. Telnet, FTP và POP3 truyền dữ liệu không mã hóa nên thường được thay bằng SSH, SFTP và các bản có TLS. Cơ sở dữ liệu, SMB và RDP thường không nên mở thẳng ra Internet.

## Nhìn hình thử trả lời

Bạn dựng máy chủ web cho trình duyệt truy cập. Cần mở cổng nào, và vì sao không nên mở 3306 ra Internet?

<details>
<summary>Xem đáp án</summary>

Mở 443 (và 80 nếu cần chuyển hướng sang HTTPS). Cổng 3306 là của MySQL; mở ra Internet cho phép bất kỳ ai thử kết nối và dò mật khẩu cơ sở dữ liệu. Thường chỉ cho phép máy ứng dụng trong mạng nội bộ truy cập cổng này.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Thư hiện đại:** nhiều dịch vụ dùng cổng 587 để người dùng gửi thư, 465 cho SMTP qua TLS, 993 cho IMAP qua TLS, 995 cho POP3 qua TLS.
- **NetBIOS:** ngoài TCP 139 còn có UDP 137 và 138; SMB hiện đại chạy trực tiếp qua TCP 445.
- **DHCP:** máy khách chưa có địa chỉ gửi yêu cầu bằng quảng bá từ cổng 68 tới cổng 67 của máy chủ.
- **Đổi cổng không phải bảo mật:** chạy dịch vụ ở cổng lạ chỉ làm giảm nhiễu dò quét, không thay cho xác thực và tường lửa.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/18-common-ports-worth-knowing.md).
- [IANA — Service Name and Transport Protocol Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml) và [RFC 6335](https://www.rfc-editor.org/rfc/rfc6335): số cổng và các dải.
- [RFC 959 — FTP](https://www.rfc-editor.org/rfc/rfc959), [RFC 854 — Telnet](https://www.rfc-editor.org/rfc/rfc854), [RFC 5321 — SMTP](https://www.rfc-editor.org/rfc/rfc5321), [RFC 1035 — DNS](https://www.rfc-editor.org/rfc/rfc1035), [RFC 2131 — DHCP](https://www.rfc-editor.org/rfc/rfc2131), [RFC 1939 — POP3](https://www.rfc-editor.org/rfc/rfc1939), [RFC 5905 — NTP](https://www.rfc-editor.org/rfc/rfc5905), [RFC 9051 — IMAP](https://www.rfc-editor.org/rfc/rfc9051), [RFC 9110 — HTTP](https://www.rfc-editor.org/rfc/rfc9110).
- [PostgreSQL — Connection settings](https://www.postgresql.org/docs/current/runtime-config-connection.html) và [MySQL — cổng mặc định](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_port).

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

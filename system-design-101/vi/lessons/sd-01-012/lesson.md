# 18 cổng mạng thường gặp

**Địa chỉ IP tìm ra máy; cổng (port) chỉ ra dịch vụ trên máy đó.** Một máy có thể chạy web, thư và cơ sở dữ liệu cùng lúc; số cổng cho biết gói tin dành cho dịch vụ nào.

![Sáu khung dọc chia mười tám cổng theo mục đích: truy cập từ xa gồm 22 SSH, 23 Telnet, 3389 RDP; web gồm 80 HTTP, 443 HTTPS; thư điện tử gồm 25 SMTP, 110 POP3, 143 IMAP; hạ tầng mạng gồm 53 DNS dùng UDP và TCP, 67 và 68 DHCPv4 dùng UDP, 123 NTP dùng UDP; chia sẻ tệp gồm 21 FTP, 139 NetBIOS, 445 SMB; cơ sở dữ liệu gồm 1521 Oracle, 3306 MySQL, 5432 PostgreSQL. Cổng mặc định là quy ước.](../../diagrams/sd-01-012-main.svg)

## Từ viết tắt

- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ và chuyển gói tin giữa các máy; địa chỉ IP là địa chỉ của một máy trên mạng.
- **IPv4** (Internet Protocol version 4) — phiên bản 4 của giao thức IP: địa chỉ gồm bốn số từ 0 đến 255 như 203.0.113.10.
- **IPv6** (Internet Protocol version 6) — phiên bản 6 của giao thức IP: địa chỉ dài hơn IPv4 nhiều, dùng khi IPv4 hết địa chỉ.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: tạo kết nối đáng tin cậy, dữ liệu đến đủ và đúng thứ tự.
- **UDP** (User Datagram Protocol) — giao thức gói dữ liệu người dùng: gửi gói tin đơn giản, nhanh, không có kết nối và không bảo đảm đến đủ hay đúng thứ tự.
- **IANA** (Internet Assigned Numbers Authority) — tổ chức giữ danh sách đăng ký chính thức các con số và tên dùng trên Internet, trong đó có số cổng.
- **SSH** (Secure SHell) — vỏ lệnh an toàn: cách đăng nhập và điều khiển máy từ xa có mã hóa.
- **RDP** (Remote Desktop Protocol) — giao thức màn hình từ xa: cho xem và điều khiển màn hình của một máy Windows từ máy khác.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời.
- **HTTPS** (HyperText Transfer Protocol Secure) — HTTP chạy trên TLS: cách gửi yêu cầu và trả lời như HTTP nhưng nội dung được mã hóa.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa giữ kín dữ liệu khi đi qua mạng.
- **SMTP** (Simple Mail Transfer Protocol) — giao thức truyền thư đơn giản: dùng để gửi thư và chuyển thư giữa các máy chủ thư.
- **POP** (Post Office Protocol) — giao thức bưu điện: cho người dùng tải thư về máy; POP3 là phiên bản 3 của giao thức này.
- **IMAP** (Internet Message Access Protocol) — giao thức truy cập thư Internet: cho người dùng đọc thư ngay trên máy chủ thư, nhiều thiết bị cùng thấy một hộp thư.
- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" của Internet, đổi tên miền như example.com thành địa chỉ IP.
- **DHCP** (Dynamic Host Configuration Protocol) — giao thức cấu hình máy chủ động: tự cấp địa chỉ IP và thông số mạng cho máy vừa vào mạng; DHCPv4 dùng cho IPv4, DHCPv6 dùng cho IPv6.
- **NTP** (Network Time Protocol) — giao thức giờ mạng: giữ đồng hồ của các máy khớp nhau.
- **FTP** (File Transfer Protocol) — giao thức truyền tệp: chuyển tệp giữa hai máy, ở dạng gốc không mã hóa.
- **SFTP** (SSH File Transfer Protocol) — giao thức truyền tệp qua SSH: chuyển tệp có mã hóa, thường thay cho FTP.
- **SMB** (Server Message Block) — khối thông điệp máy chủ: giao thức chia sẻ tệp và máy in trong mạng, hay gặp trên Windows.
- **NetBIOS** (Network Basic Input/Output System) — hệ thống nhập xuất cơ bản qua mạng: giao thức cũ để máy trong mạng nội bộ tìm nhau theo tên và chia sẻ tệp, dùng các cổng 137, 138 và 139.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; MySQL và PostgreSQL là hai hệ là hệ cơ sở dữ liệu dùng nó.

## Đọc hình

Cổng là một số 16 bit (0 đến 65535). Kết hợp với giao thức vận chuyển (TCP hoặc UDP), nó xác định điểm cuối liên lạc trên máy: với TCP là một đầu của kết nối, với UDP là nơi nhận và gửi từng gói tin (UDP không có kết nối). IANA chia dải số thành cổng hệ thống (0–1023), cổng đã đăng ký (1024–49151) và cổng động (49152–65535), dải sau thường được máy khách dùng tạm khi mở kết nối hoặc gửi gói đi.

Mười tám cổng trong hình gom theo việc chúng làm:

- **Truy cập từ xa:** SSH (22) là cách đăng nhập có mã hóa; Telnet (23) cũ và không mã hóa; RDP (3389) là màn hình từ xa của Windows, chạy chủ yếu trên TCP và có thể kèm UDP.
- **Web:** HTTP (80) và HTTPS (443).
- **Thư:** SMTP (25) gửi và chuyển thư; POP3 (110) và IMAP (143) cho người dùng đọc thư.
- **Hạ tầng mạng:** DNS (53) dùng cả UDP và TCP; DHCP cho IPv4 (DHCPv4) dùng UDP 67 cho máy chủ và 68 cho máy khách, còn DHCPv6 dùng UDP 547 cho máy chủ hoặc relay và 546 cho máy khách; NTP (123) đồng bộ giờ.
- **Chia sẻ tệp:** FTP (21), NetBIOS (139) và SMB (445).
- **Cơ sở dữ liệu:** Oracle (1521), MySQL (3306), PostgreSQL (5432).

## Giới hạn cần nhớ

Số cổng mặc định chỉ là quy ước: dịch vụ có thể chạy ở cổng khác, và một cổng mở không bảo đảm đúng dịch vụ đó đang chạy. Telnet, FTP và POP3 ở dạng gốc truyền dữ liệu không mã hóa nên thường được thay bằng SSH, SFTP và các bản có TLS. Cơ sở dữ liệu, SMB và RDP thường không nên mở thẳng ra Internet.

## Nhìn hình thử trả lời

Bạn dựng máy chủ web cho trình duyệt truy cập. Cần mở cổng nào, và vì sao không nên mở 3306 ra Internet?

<details>
<summary>Xem đáp án</summary>

Mở 443 trên TCP (thêm UDP 443 nếu bật HTTP/3) và 80 nếu cần chuyển hướng sang HTTPS. Cổng 3306 là của MySQL; mở ra Internet cho phép bất kỳ ai thử kết nối và dò mật khẩu cơ sở dữ liệu. Thường chỉ cho phép máy ứng dụng trong mạng nội bộ truy cập cổng này.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Thư hiện đại:** nhiều dịch vụ dùng cổng 587 để người dùng gửi thư, 465 cho SMTP qua TLS, 993 cho IMAP qua TLS, 995 cho POP3 qua TLS.
- **FTP:** cổng 21 là kênh điều khiển; kênh dữ liệu dùng cổng 20 ở chế độ chủ động hoặc một cổng do máy chủ chỉ định ở chế độ bị động.
- **NetBIOS:** có ba dịch vụ: dịch vụ tên dùng cổng 137 (cả UDP và TCP), dịch vụ gói dữ liệu dùng UDP 138 và dịch vụ phiên dùng TCP 139; SMB hiện đại chạy trực tiếp qua TCP 445.
- **DHCPv4:** máy khách chưa có địa chỉ gửi yêu cầu bằng quảng bá từ cổng 68 tới cổng 67 của máy chủ.
- **Đổi cổng không phải bảo mật:** chạy dịch vụ ở cổng lạ chỉ làm giảm nhiễu dò quét, không thay cho xác thực và tường lửa.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/18-common-ports-worth-knowing.md).
- [RFC 768 — UDP](https://www.rfc-editor.org/rfc/rfc768) và [RFC 9293 — TCP](https://www.rfc-editor.org/rfc/rfc9293): số cổng 16 bit trong tiêu đề.
- [IANA — Service Name and Transport Protocol Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml) và [RFC 6335](https://www.rfc-editor.org/rfc/rfc6335): số cổng và các dải.
- [RFC 959 — FTP](https://www.rfc-editor.org/rfc/rfc959), [RFC 854 — Telnet](https://www.rfc-editor.org/rfc/rfc854), [RFC 5321 — SMTP](https://www.rfc-editor.org/rfc/rfc5321), [RFC 1035 — DNS](https://www.rfc-editor.org/rfc/rfc1035), [RFC 2131 — DHCPv4](https://www.rfc-editor.org/rfc/rfc2131), [RFC 8415 — DHCPv6](https://www.rfc-editor.org/rfc/rfc8415), [RFC 1939 — POP3](https://www.rfc-editor.org/rfc/rfc1939), [RFC 5905 — NTP](https://www.rfc-editor.org/rfc/rfc5905), [RFC 9051 — IMAP](https://www.rfc-editor.org/rfc/rfc9051), [RFC 9110 — HTTP](https://www.rfc-editor.org/rfc/rfc9110), [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114).
- [RFC 4253 — SSH](https://www.rfc-editor.org/rfc/rfc4253), [RFC 1001](https://www.rfc-editor.org/rfc/rfc1001) và [RFC 1002](https://www.rfc-editor.org/rfc/rfc1002) (NetBIOS), [RFC 6409](https://www.rfc-editor.org/rfc/rfc6409) và [RFC 8314](https://www.rfc-editor.org/rfc/rfc8314) (cổng thư), [MS-RDPBCGR](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/) và [MS-SMB2](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/).
- [Oracle — Net Listener](https://docs.oracle.com/en/database/oracle/oracle-database/19/netag/configuring-and-administering-oracle-net-listener.html), [PostgreSQL — Connection settings](https://www.postgresql.org/docs/current/runtime-config-connection.html) và [MySQL — cổng mặc định](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_port).

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

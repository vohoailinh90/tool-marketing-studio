# Cổng mạng: 18 cổng quen thuộc và điều hệ điều hành làm với số cổng

**Địa chỉ IP tìm ra máy; cổng cùng giao thức vận chuyển chỉ ra chỗ nhận gói tin trong máy đó.** Hệ điều hành chỉ biết con số, không biết dịch vụ nào đang nói chuyện. Bài này đo vài hành vi thật của số cổng trên Linux, rồi xếp 18 cổng quen thuộc theo câu hỏi thực dụng: cổng nào có thể mở ra Internet, cổng nào thì không.

![Năm khung dọc đo trên Linux. Một: cổng cùng giao thức vận chuyển mới tạo thành một chỗ nhận, nên TCP 53 và UDP 53 cùng tồn tại được còn hai TCP cùng số thì báo địa chỉ đang dùng. Hai: cổng dưới 1024 cần quyền, người dùng thường bind 80 bị từ chối nhưng 1024 thì được. Ba: máy khách mượn cổng tạm, Linux mặc định dùng dải 32768 đến 60999. Bốn: cổng TCP đóng từ chối ngay, còn UDP đóng thì socket chưa kết nối chỉ thấy hết giờ chờ, giống cổng UDP mở mà im lặng. Năm: một máy chủ web chạy trên cổng 3306 vẫn trả lời, vì số cổng không nói ai đang nghe. Kết quả đo một lần trên một máy.](../../diagrams/sd-01-012-main.svg)

## Từ viết tắt

- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ và chuyển gói tin giữa các máy; địa chỉ IP là địa chỉ của một máy trên mạng.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: tạo kết nối đáng tin cậy, dữ liệu đến đủ và đúng thứ tự.
- **UDP** (User Datagram Protocol) — giao thức gói dữ liệu người dùng: gửi gói tin đơn giản, nhanh, không có kết nối và không bảo đảm đến đủ hay đúng thứ tự.
- **ICMP** (Internet Control Message Protocol) — giao thức thông điệp điều khiển Internet: giao thức máy mạng dùng để báo lỗi, ví dụ "không có chương trình nào nghe ở cổng này".
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
- **DHCP** (Dynamic Host Configuration Protocol) — giao thức cấu hình máy chủ động: tự cấp địa chỉ IP và thông số mạng cho máy vừa vào mạng.
- **NTP** (Network Time Protocol) — giao thức giờ mạng: giữ đồng hồ của các máy khớp nhau.
- **FTP** (File Transfer Protocol) — giao thức truyền tệp: chuyển tệp giữa hai máy, ở dạng gốc không mã hóa.
- **SFTP** (SSH File Transfer Protocol) — giao thức truyền tệp qua SSH: chuyển tệp có mã hóa, thường thay cho FTP.
- **SMB** (Server Message Block) — khối thông điệp máy chủ: giao thức chia sẻ tệp và máy in trong mạng, hay gặp trên Windows.
- **NetBIOS** (Network Basic Input/Output System) — hệ thống nhập xuất cơ bản qua mạng: giao thức cũ để máy trong mạng nội bộ tìm nhau theo tên và chia sẻ tệp.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; MySQL và PostgreSQL là hai hệ cơ sở dữ liệu dùng nó.
- **RFC** (Request for Comments) — "đề nghị bình luận": loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; nhiều RFC là tiêu chuẩn.

## Đọc hình

Cổng là một số 16 bit (0 đến 65535). Mọi phép đo dưới đây chạy ngày 2026-10-16 trên Linux nhân 6.18 với Python 3.13 (đoạn mã ở phần "Xem sâu hơn" tái hiện được xung đột bind, tên dịch vụ và dải cổng tạm; các phép đo còn lại, như cổng đặc quyền với người dùng thường, UDP và máy chủ web trên cổng 3306, chỉ được mô tả, không kèm mã); máy khác, nhân khác hay cấu hình khác có thể cho số khác.

1. **Cổng cộng giao thức là một chỗ nhận.** Mở hai socket TCP trên cùng địa chỉ và cùng số cổng thì socket thứ hai bị từ chối với lỗi `EADDRINUSE` (địa chỉ đang được dùng). Nhưng một socket UDP lấy được đúng số cổng đó khi TCP đang giữ. Vì vậy "cổng 53" của DNS có thể có mặt ở cả TCP lẫn UDP. Ghi nhớ: khi nói "cổng 53", nên nói cả giao thức vận chuyển.
2. **Cổng dưới 1024 cần quyền.** Người dùng thường (`nobody`) bind cổng 80 và 1023 đều bị từ chối (`EACCES`), còn cổng 1024 thì được; tài khoản root bind được cả ba. Tài liệu nhân Linux ghi ngưỡng mặc định là 1024 (`ip_unprivileged_port_start`) và có thể đổi theo từng không gian tên mạng. Hệ quả: chương trình muốn nghe ở cổng 80 hoặc 443 phải có quyền (hoặc được cấp riêng quyền bind cổng thấp), còn chương trình thường tự chọn cổng từ 1024 trở lên.
3. **Máy khách mượn cổng tạm.** Mỗi kết nối đi ra cần một cổng phía mình. Trên máy thử, 200 kết nối cục bộ đều nhận cổng nằm trong 32768–60999, dải mặc định ghi trong tài liệu nhân Linux. Chúng gom trong một khoảng hẹp (khoảng 1.800 số) và khoảng đó đổi chỗ giữa các lần chạy: trong năm lần chạy, ba lần cả 200 cổng nằm dưới 49152 và hai lần cả 200 cổng nằm từ 49152 trở lên (dải IANA gọi là cổng động). Vì vậy một lần chạy không nói được cổng tạm nằm ở đâu; hãy dựa vào dải của nhân (đọc `/proc/sys/net/ipv4/ip_local_port_range`) khi viết luật tường lửa hay đọc nhật ký, và đừng giả định cổng tạm luôn từ 49152 trở lên hay luôn dưới đó.
4. **Đóng và im lặng khác nhau.** Kết nối tới cổng TCP không ai nghe bị từ chối gần như tức thì (khoảng 2 mili giây trên máy thử). Với UDP, hệ điều hành đích gửi lại một thông báo ICMP khi cổng đóng, nhưng chương trình có thấy nó hay không tùy cách mở socket: socket đã `connect` thấy `ECONNREFUSED` khi thông báo đó đến được nơi gửi; socket chưa kết nối trên máy thử chỉ thấy hết giờ chờ, giống hệt trường hợp cổng UDP mở mà dịch vụ không trả lời. Bật tùy chọn `IP_RECVERR` thì socket chưa kết nối cũng thấy lỗi. Hệ quả: một lần dò UDP hết giờ chờ chưa nói được cổng đóng hay mở, và một gói bị chặn giữa đường cũng trông như vậy.
5. **Số cổng không nói ai đang nghe.** Trên máy thử, bảng tên dịch vụ của hệ thống ghi 3306 là `mysql`, nhưng một máy chủ web chạy trên 3306 vẫn trả lời `curl` bình thường. Công cụ đổi số thành tên chỉ tra một bảng.

## 18 cổng và bốn cổng liên quan, xếp theo cái giá khi mở ra Internet

Bảng dưới gom 18 cổng quen thuộc theo một câu hỏi: nếu mở ra Internet thì có gì cần nghĩ thêm? Nó nêu thêm bốn cổng liên quan là 465, 587, 993 và 995, vì chúng là cổng gửi thư của người dùng hoặc bản có TLS của các cổng thư gốc, nên tổng cộng bài nhắc tới 22 số cổng.

- **Cặp "bản trần" và "bản có mã hóa".** Telnet (TCP 23) gửi dữ liệu không mã hóa; SSH (TCP 22) thường thay nó. HTTP (TCP 80) thường được thay bằng HTTPS (TCP 443; HTTP/3 chạy trên UDP và thường dùng cùng số 443). FTP (TCP 21) thường được thay bằng SFTP, một giao thức riêng chạy qua SSH nên dùng chung cổng 22. Với thư thì phải tách hai việc. Đọc thư: POP3 (110) và IMAP (143) có bản dùng TLS ngay từ đầu ở 995 và 993. Gửi thư: SMTP ở cổng 25 chủ yếu chuyển thư giữa các máy chủ thư (có thể nâng cấp lên TLS giữa chừng), còn người dùng gửi thư qua cổng submission 587 hoặc 465, trong đó 465 dùng TLS ngay từ đầu; 465 là cổng gửi thư của người dùng chứ không phải bản TLS của cổng 25. Bảng dịch vụ của máy thử gọi 25 là `smtp`, 587 là `submission` và 465 là `submissions`; các RFC về việc này chưa mở được để đối chiếu.
- **Hạ tầng mạng: tùy vai trò.** DNS (53, cả UDP và TCP) có hai vai rất khác nhau. Máy chủ DNS có thẩm quyền cho một tên miền công khai phải nhận truy vấn từ Internet (cả UDP và TCP) thì mới phục vụ được tên miền đó. Còn trình phân giải (resolver) làm hộ người dùng thường nên chỉ phục vụ mạng của chính nó, vì một resolver mở cho mọi địa chỉ hay bị lạm dụng; đây là thông lệ vận hành, bài chưa đối chiếu tài liệu chuẩn về việc này. NTP (UDP 123) cũng vậy: máy khách chỉ cần đi ra, chỉ máy chủ giờ công cộng mới nhận truy vấn từ Internet. DHCP (UDP 67 cho máy chủ, 68 cho máy khách) lúc đầu dùng quảng bá trong mạng cục bộ nên thường không cần ra Internet.
- **Dịch vụ nội bộ không nên lộ.** NetBIOS (139), SMB (445), RDP (3389), Oracle (1521), MySQL (3306), PostgreSQL (5432). Nếu cần truy cập từ xa, đặt sau một lớp truy cập có xác thực, hoặc ít nhất lọc theo địa chỉ nguồn, thay vì mở cho mọi địa chỉ.

## Giới hạn cần nhớ

Số cổng mặc định là quy ước, không phải bảo đảm: một dịch vụ có thể chạy ở cổng khác và cổng "quen" có thể đang chạy chương trình khác. Đổi cổng nhiều lắm chỉ làm bớt tiếng ồn dò quét, không thay cho xác thực và tường lửa. Các phép đo chỉ chạy trên một máy Linux; bài chưa thử hệ điều hành khác, tường lửa thật hay mạng thật. Riêng phép đo UDP còn khác với câu trong trang `udp(7)` của Linux (xem phần dưới). Các con số cổng mặc định lấy từ bảng tên dịch vụ của máy thử, đối chiếu với tài liệu phần mềm khi mở được; những chỗ chưa mở được tài liệu chuẩn được ghi rõ ở phần nguồn.

## Nhìn hình thử trả lời

Bạn gửi một gói UDP tới cổng 123 của một máy lạ rồi chờ 1 giây mà không thấy gì. Có nên kết luận "cổng đóng" không?

<details>
<summary>Xem đáp án</summary>

Không. Một lần hết giờ chờ không phân biệt được ba trường hợp: cổng đóng, cổng mở mà dịch vụ im lặng, và gói bị chặn hay bị mất giữa đường (một tường lửa có thể chặn mà không gửi lời từ chối). Chỉ một thông báo từ chối thật sự đến nơi mới là bằng chứng cổng đóng; với socket đã `connect` hoặc có bật `IP_RECVERR` nó hiện thành lỗi `ECONNREFUSED`. Nhưng `connect` hay `IP_RECVERR` không làm cho việc hết giờ chờ có nghĩa: vắng thông báo thì vẫn chưa kết luận được gì. Muốn biết dịch vụ có đang chạy, gửi một yêu cầu NTP thật và kiểm tra có trả lời đúng hay không; im lặng kéo dài vẫn là kết quả chưa kết luận.

</details>

<details>
<summary>Xem sâu hơn: cách tự thử, và những chỗ đối chiếu chưa khớp</summary>

Cách thử nhanh, chỉ cần Python:

```python
import socket, errno
a = socket.socket(); a.bind(("127.0.0.1", 0)); a.listen()
port = a.getsockname()[1]
b = socket.socket()
try: b.bind(("127.0.0.1", port))
except OSError as e: print("TCP thứ hai:", errno.errorcode[e.errno])
u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
u.bind(("127.0.0.1", port)); print("UDP cùng số cổng: được")
print(socket.getservbyport(3306, "tcp"), open("/proc/sys/net/ipv4/ip_local_port_range").read().split())
```

Kết quả thử: `EADDRINUSE` cho TCP thứ hai, UDP cùng số thì được, tên dịch vụ ở 3306 là `mysql`, dải cổng tạm là 32768 và 60999.

Thêm vài kết quả cùng ngày:

- **Bind sau khi tắt dịch vụ.** Khi phía máy chủ đóng kết nối trước, bind lại ngay cùng cổng trên socket chưa đặt `SO_REUSEADDR` bị `EADDRINUSE`; đặt `SO_REUSEADDR` thì được. Đó là lý do một dịch vụ khởi động lại nhanh đôi khi báo "địa chỉ đang được dùng".
- **Địa chỉ nghe.** Khi `127.0.0.1:p` đang nghe, bind `0.0.0.0:p` (mọi địa chỉ) trên cùng cổng cũng bị từ chối. Còn khi `127.0.0.1:p` đang nghe, bind `127.0.0.2:p` (một địa chỉ cụ thể khác, cùng số cổng) được.
- **Tên theo bảng của hệ thống.** Bảng tên dịch vụ trên máy thử (gói `netbase`, ghi là cập nhật từ danh sách IANA) gọi 143 là `imap2`, 465 là `submissions`, 3389 là `ms-wbt-server`, và không có mục cho 1521. Nhãn tên có thể khác lời gọi quen thuộc; tên hiển thị chưa phải nguồn chính thức cho nghĩa của một cổng.
- **Chỗ đối chiếu chưa khớp.** Trang `udp(7)` của Linux (kho man-pages) viết rằng mọi lỗi nghiêm trọng đều được trả về cho người dùng kể cả khi socket chưa kết nối; trên máy thử, socket UDP chưa kết nối và chưa bật `IP_RECVERR` chỉ thấy hết giờ chờ. Bài không tìm ra nguyên nhân (có thể do tài liệu, nhân hay cấu hình khác nhau); hãy tự thử trên hệ thống của bạn trước khi dựa vào hành vi này.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/18-common-ports-worth-knowing.md): danh sách 18 cổng gốc.
- [Linux ip-sysctl](https://github.com/torvalds/linux/blob/master/Documentation/networking/ip-sysctl.rst): `ip_local_port_range` (32768–60999) và `ip_unprivileged_port_start` (1024); [man ip(7)](https://github.com/mkerrisk/man-pages/blob/master/man7/ip.7), [man udp(7)](https://github.com/mkerrisk/man-pages/blob/master/man7/udp.7) và [man bind(2)](https://github.com/mkerrisk/man-pages/blob/master/man2/bind.2): cổng đặc quyền, lỗi `EADDRINUSE`, lỗi UDP.
- [PostgreSQL — cấu hình `port`](https://github.com/postgres/postgres/blob/master/doc/src/sgml/config.sgml): TCP 5432 theo mặc định; [mã nguồn MySQL](https://github.com/mysql/mysql-server/blob/trunk/sql/mysqld.cc): 3306 là giá trị mặc định cuối cùng.
- [RFC 9110](https://httpwg.org/specs/rfc9110.html): cổng mặc định của lược đồ `https` là 443 (ví dụ trong phần origin).
- [Registry số cổng của IANA](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml) và [RFC 6335](https://www.rfc-editor.org/rfc/rfc6335) (các dải 0–1023, 1024–49151, 49152–65535): chưa mở được trong lần biên soạn này; đối chiếu phụ bằng bảng dịch vụ `netbase` của máy thử.
- Cổng của Telnet, FTP, SMTP, POP3, IMAP, DHCP, NTP, NetBIOS, SMB, RDP, Oracle theo bảng dịch vụ trên máy thử và hiểu biết chung; tài liệu chuẩn tương ứng (RFC 854, 959, 5321, 1939, 9051, 2131, 5905, 1001/1002, MS-RDPBCGR, Oracle Net) chưa được mở để đối chiếu.

Các phép đo chạy trên máy biên soạn ngày 2026-10-16. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-01-012.json).

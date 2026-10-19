# Tấn công mạng theo bảy tầng OSI: tầng nào chịu đòn gì?

**Mỗi tầng OSI có một thứ riêng bị nhắm tới và một cách đỡ riêng. Cách xếp đòn vào tầng chỉ là quy ước: có đòn trải qua nhiều tầng, và cách đỡ tốt nhất thường nằm ở tầng khác với chỗ đòn đánh.**
Bài chọn một đòn tiêu biểu mỗi tầng kèm một cách đỡ có nguồn, rồi chỉ ra chỗ xếp tầng còn tranh cãi; không hướng dẫn thực hiện. Về tường lửa xem [bài sd-14-007](../sd-14-007/lesson.md).

![Ba khung dọc. Phía chương trình: tầng 7 yêu cầu HTTP chậm, đỡ bằng tốc độ nhận tối thiểu; tầng 6 chuỗi định dạng, đỡ bằng chuỗi do lập trình viên viết; tầng 5 cố định mã phiên, đỡ bằng cấp mã mới. Phía đường truyền: tầng 4 ngập SYN, đỡ bằng SYN cookie; tầng 3 giả địa chỉ IP, đỡ bằng lọc ở router biên; tầng 2 ARP giả, đỡ bằng lọc gói ARP; tầng 1 cắt cáp hoặc nghe lén, đỡ bằng đường dự phòng và mã hóa. Khung ba: bốn ghi chú quy ước.](../../diagrams/sd-14-030-main.svg)

## Từ viết tắt

- **OSI** (Open Systems Interconnection) — kết nối các hệ thống mở: mô hình mạng bảy tầng.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: ngôn ngữ giữa trình duyệt và máy chủ web.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: kết nối đáng tin cậy, mở bằng cú bắt tay ba gói.
- **IP** (Internet Protocol) — giao thức liên mạng: đánh địa chỉ máy, chuyển gói tin giữa các mạng.
- **SYN** (SYNchronize) — đồng bộ: gói đầu của cú bắt tay TCP, hỏi "mở kết nối được không?".
- **ARP** (Address Resolution Protocol) — giao thức phân giải địa chỉ: trong mạng cục bộ, tìm địa chỉ phần cứng ứng với một địa chỉ IP.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa chạy trên TCP.
- **MITM** (Manipulator In The Middle) — kẻ thao túng xen giữa: chen vào giữa hai bên để đọc hoặc sửa dữ liệu.
- **DDoS** (Distributed Denial of Service) — từ chối dịch vụ phân tán: nhiều máy cùng gửi tải làm dịch vụ không dùng được.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng về bảo mật ứng dụng.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, tài liệu tra cứu công nghệ web.

## Đọc hình

**7 · Ứng dụng.** Yêu cầu HTTP gửi cực chậm khiến máy chủ giữ kết nối chờ cho đến khi hết chỗ. Đỡ: tốc độ nhận tối thiểu và thời hạn đọc yêu cầu (OWASP).

**6 · Trình bày.** Chương trình C dùng dữ liệu người dùng làm chính chuỗi định dạng của `printf`, nên `%p` hay `%s` trong dữ liệu bị thực hiện như lệnh. Đỡ: chuỗi định dạng luôn do lập trình viên viết. Lỗi nằm trong mã chương trình, không ở giao thức nào (OWASP: nhóm injection).

**5 · Phiên.** Phiên đăng nhập của ứng dụng web: máy chủ giữ dữ liệu, trình duyệt giữ một mã ([bài sd-14-008](../sd-14-008/lesson.md)). Kẻ tấn công đưa mã nó biết vào trình duyệt nạn nhân rồi chờ nạn nhân đăng nhập. Đỡ: cấp mã mới sau đăng nhập, việc OWASP gọi là bắt buộc dù có TLS hay không.

**4 · Giao vận.** Bắt tay TCP có ba gói, mở đầu bằng SYN. Đến gói thứ ba, máy chủ phải nhớ mỗi kết nối nửa mở trong một hàng chờ hữu hạn; gửi nhiều SYN rồi bỏ làm đầy hàng chờ. Đỡ: khi hàng chờ tràn, Linux có thể gửi "cookie" thay vì nhớ mục (`tcp_syncookies`); thời gian giữ mục cũng chỉnh được.

**3 · Mạng.** Địa chỉ nguồn trong gói IP do bên gửi tự điền nên có thể điền sai. Đỡ: router biên của nhà cung cấp mạng lọc địa chỉ nguồn không hợp lệ (OWASP).

**2 · Liên kết dữ liệu.** ARP giả gắn địa chỉ phần cứng của kẻ tấn công với IP của máy khác, nên gói dành cho máy kia chạy sang kẻ tấn công. Đỡ: OWASP nêu lọc gói ARP đáng ngờ, hoặc bảng ARP cố định (khó bảo trì). Bài chỉ giải thích, không chạy giả mạo.

**1 · Vật lý.** OWASP xếp phá hủy, cản trở và làm hỏng phần cứng, như cắt cáp, vào tầng này. Đỡ: không để điểm hỏng duy nhất, tức có đường dự phòng. TLS không ngăn việc nghe lén, nhưng theo OWASP nó giữ bí mật nội dung nên kẻ nghe không đọc được.

## Giới hạn cần nhớ

Cách xếp tầng là quy ước; với DDoS, OWASP gom bảy tầng thành ba mặt (ứng dụng, phiên hay giao thức, băng thông) và bàn riêng tầng 1, 2. Ba chỗ còn tranh cãi:

- **Một tên, nhiều tầng.** DDoS ở cả ba mặt; MDN dùng "session hijacking" cho cả ăn cắp mã phiên (ứng dụng) lẫn chiếm một phiên TCP (giao vận).
- **Một cuộc tấn công, nhiều tầng.** MITM, theo OWASP, chia kết nối TCP làm hai, nhưng công cụ trong mạng cục bộ dùng ARP giả, thứ bị đọc là HTTP, và cách đỡ chính, TLS, nằm trên TCP.
- **Một cách thử, không phải một tầng.** Brute force nhắm mật khẩu, mã phiên hoặc trang ẩn (OWASP).

OSI là mô hình để học; Internet thật chạy theo TCP/IP, gom tầng 5 đến 7 làm một (hiểu biết chung).

## Nhìn hình trả lời

Điểm truy cập Wi-Fi giả ở quán cà phê đọc được cookie phiên của bạn trên trang không dùng TLS. Đòn này ở tầng nào, và nếu trang bật TLS thì còn lỗ hổng phiên nào không?

<details>
<summary>Xem đáp án</summary>

Không riêng tầng nào: điểm truy cập giả chen vào ở tầng thấp, thứ bị đọc là cookie HTTP ở tầng ứng dụng. Theo OWASP, TLS đỡ việc ăn cắp mã phiên qua MITM nhưng không đỡ cố định phiên, đoán mã phiên hay brute force; trang bật TLS mà giữ nguyên mã sau đăng nhập vẫn bị cố định phiên (thử nghiệm 3).

</details>

<details>
<summary>Xem sâu hơn: ba thử nghiệm cục bộ và chỗ bài nguồn chưa khớp</summary>

Chạy trên máy biên soạn (Python 3.13.16), chỉ trên `127.0.0.1` hoặc trong bộ nhớ; số đo là một lần đo.

**1. Làm cạn chỗ chờ (tầng 4).** Máy chủ một luồng, hàng chờ nghe là 2; "kẻ tấn công" là 8 ổ cắm chỉ kết nối rồi im lặng. Máy chủ chờ mãi: chỉ 4 ổ kết nối được, khách thật không kết nối được trong 3 giây. Bỏ kết nối sau 0,2 giây im lặng: khách thật được trả lời sau 0,5 giây (ba lần chạy giống nhau). Đây chưa phải ngập SYN, vì các kết nối đã bắt tay xong.

**2. Hàng chờ nửa mở (mô hình, không có gói tin).** Hàng chờ nhớ tối đa 8 mục, 40 lượt, mỗi lượt một khách thật cùng 4 hoặc 10 SYN giả không đáp. Khách thật kết nối được trên 40: chỉ hàng chờ, mục sống 5 lượt: 15 và 7; sống 1 lượt: 40 và 29; thêm cookie khi đầy: 40 và 40. Số 40 do cách dựng mô hình; tài liệu Linux gọi SYN cookie là biện pháp dự phòng, vi phạm giao thức TCP.

**3. Cố định phiên (kho phiên giả trong bộ nhớ).** Hai công tắc: đổi mã sau đăng nhập, và chế độ nghiêm ngặt (chỉ nhận mã do máy chủ cấp). Máy chủ giữ nguyên mã: kẻ tấn công thấy tài khoản nạn nhân, với mã tự bịa thì chỉ ở chế độ dễ dãi. Máy chủ đổi mã: không thấy gì trong cả bốn tổ hợp, khớp OWASP (đổi mã là bắt buộc). Chưa mô phỏng cách mã tới được nạn nhân.

**Điều đã chỉnh so với bài nguồn.** Bài nguồn chỉ liệt kê đòn; bài này thêm cách đỡ và chỗ tranh cãi.
- Không có trong nguồn đã đọc: "Pushing" (có thể là "phishing", suy đoán; MDN gọi đó là kỹ thuật xã hội, không thuộc tầng mạng nào), "Malware injection", "Malicious code injection", "Encoding/decoding vulnerabilities" (OWASP dùng "code injection").
- Bài nguồn gọi đòn tầng giao vận khác ngập SYN (SYN flood) của MDN và Linux; OWASP mô tả session hijacking, fixation, brute force nhắm phiên web, mật khẩu hay trang ẩn, không riêng tầng phiên.
- Sửa bảng định tuyến, nhảy giữa các mạng cục bộ ảo, giả địa chỉ phần cứng, can thiệp phần cứng, nhiễu điện từ: không có nguồn độc lập đọc được nên không giải thích.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-network-security-cheatsheet.md).
- OWASP Cheat Sheet Series: [Denial of Service](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Denial_of_Service_Cheat_Sheet.md), [Session Management](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Session_Management_Cheat_Sheet.md), [Transport Layer Security](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Transport_Layer_Security_Cheat_Sheet.md).
- OWASP Community: [Format string attack](https://github.com/OWASP/www-community/blob/ce2814653f497a7a9ebadce39ce7f84bb3c603e4/pages/attacks/Format_string_attack.md), [Man-in-the-middle](https://github.com/OWASP/www-community/blob/ce2814653f497a7a9ebadce39ce7f84bb3c603e4/pages/attacks/Man-in-the-middle_attack.md), [Session fixation](https://github.com/OWASP/www-community/blob/ce2814653f497a7a9ebadce39ce7f84bb3c603e4/pages/attacks/Session_fixation.md), [Brute force](https://github.com/OWASP/www-community/blob/ce2814653f497a7a9ebadce39ce7f84bb3c603e4/pages/attacks/Brute_force_attack.md).
- MDN: [MITM](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/attacks/mitm/index.md), [Phishing](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/attacks/phishing/index.md), [Session hijacking](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/session_hijacking/index.md), [TCP handshake](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/tcp_handshake/index.md), [Denial of Service](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/denial_of_service/index.md).
- Linux kernel: [ip-sysctl.rst](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/Documentation/networking/ip-sysctl.rst).

Đã đọc nguồn ngày 2026-10-18. Các đặc tả chuẩn Internet, báo cáo mà OWASP trích và Wikipedia không đọc được nên không được trích dẫn. Việc chọn đòn tiêu biểu, cách chia khung, các ghi chú quy ước và ba thử nghiệm là của người biên soạn. Bài viết và hình được thiết kế độc lập.

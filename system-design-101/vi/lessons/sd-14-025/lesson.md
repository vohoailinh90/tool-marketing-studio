# VPN hoạt động thế nào? Đường hầm, mã hóa và điều nó không làm

**VPN thường đặt một đường hầm mã hóa (bài mô hình trường hợp này) giữa thiết bị của bạn và một máy chủ VPN, rồi để máy chủ đó thay bạn đi tiếp tới trang web. Đường hầm chỉ che đoạn từ bạn tới máy chủ VPN: người nghe trên đoạn đó không đọc được nữa, nhưng máy chủ VPN thì thấy bạn đang gửi tới đâu (và gửi gì, nếu trang không dùng HTTPS), còn trang web vẫn nhận ra bạn qua cookie hay tài khoản.**
Bài này không hướng dẫn cài VPN và không so sánh nhà cung cấp. Nó dùng một mô hình nhỏ tự viết (không phải giao thức VPN thật) để quan sát ai thấy gì ở từng đoạn, rồi đối chiếu với tài liệu của OpenVPN, WireGuard, MDN và OWASP. Chuyện nhà cung cấp có ghi nhật ký hay không, tốc độ và pháp lý nằm ngoài bài.

![Hình có hai phần. Phần một là bốn thẻ nối bằng mũi tên theo đường đi của một yêu cầu qua VPN. Thiết bị của bạn bọc tin vào đường hầm mã hóa. Người nghe, như Wi-Fi hay nhà mạng, chỉ thấy kết nối từ bạn tới máy chủ VPN, kích thước và giờ gửi. Máy chủ VPN giải mã, thấy đích, và cả nội dung nếu trang không dùng HTTPS, rồi gửi tiếp bằng địa chỉ của nó. Trang web thấy địa chỉ máy chủ VPN nhưng vẫn thấy cookie hay tài khoản của bạn. Phần hai là bốn điều cần nhớ: đoạn sau máy chủ VPN chỉ được che nếu trang dùng HTTPS; phải tin máy chủ VPN; trang vẫn nhận ra bạn; tin đi ngoài đường hầm vẫn lộ địa chỉ thật.](../../diagrams/sd-14-025-main.svg)

## Từ viết tắt

- **VPN** (Virtual Private Network) — mạng riêng ảo: dịch vụ đưa tin của bạn qua một đường hầm tới một máy chủ trung gian, rồi máy chủ đó mới đưa tin ra Internet.
- **IP** (Internet Protocol) — giao thức Internet: địa chỉ IP là một dãy số định danh thiết bị trên mạng, và trang web thấy dãy số này của bên gửi.
- **IPv6** (Internet Protocol version 6) — phiên bản 6 của giao thức Internet: kiểu địa chỉ IP mới, dài hơn kiểu bốn số.
- **DNS** (Domain Name System) — hệ thống tên miền: dịch tên trang web thành địa chỉ IP; truy vấn này có thể đi ngoài đường hầm nếu cấu hình sót.
- **AES** (Advanced Encryption Standard) — chuẩn mã hóa tiên tiến: thuật toán mã hóa dùng một khóa chung để khóa và mở.
- **GCM** (Galois/Counter Mode) — chế độ Galois/Counter: cách dùng AES vừa mã hóa vừa gắn một thẻ xác thực để phát hiện tin bị sửa.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: giao thức mã hóa nằm dưới HTTPS.
- **HTTPS** (HyperText Transfer Protocol Secure) — cách vào trang web có mã hóa bằng TLS giữa trình duyệt và trang, nên người đứng giữa không đọc được nội dung.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

Các số dưới đây đến từ một mô hình tôi viết bằng Python 3.13 và thư viện `cryptography` 50.0.1, chạy ba lần trên máy biên soạn (cổng ngẫu nhiên, khóa tạm, chỉ địa chỉ 127.x.x.x). Mô hình không phải giao thức VPN thật; mục “Xem sâu hơn” nói nó có gì và thiếu gì.

**1 · Thiết bị của bạn.** Bật VPN là đổi cách thiết bị chọn đường: tin gửi tới những đích nhất định được đưa vào đường hầm thay vì đi thẳng ra mạng. MDN định nghĩa đường hầm (tunneling) là truyền dữ liệu của mạng riêng qua mạng công cộng bằng cách đóng gói nó. Tài liệu OpenVPN mô tả tùy chọn `--redirect-gateway`: nó chuyển mọi tin IP đi ra vào VPN bằng ba việc, là giữ một đường riêng tới chính máy chủ VPN, xóa đường mặc định, rồi đặt đường mặc định mới trỏ vào VPN. Với WireGuard, danh sách `AllowedIPs` của mỗi bên cho biết đích nào được gửi vào đường hầm. Tin gốc gồm đích và nội dung rồi được bọc vào một tin ngoài mã hóa bằng AES-GCM. Trong mô hình, tin gốc 39 byte thành tin ngoài 71 byte: thêm 32 byte, gồm 4 byte độ dài, 12 byte số dùng một lần và 16 byte thẻ xác thực. Đó là con số của mô hình, không phải của giao thức nào có thật.

**2 · Người nghe trên đường.** Đây là người ngồi cùng Wi-Fi hay nhà mạng. Không có đường hầm, trong mô hình người nghe đọc được tên đích, đường dẫn và cookie ngay trong 39 byte đi qua. Có đường hầm, người nghe thấy một kết nối từ địa chỉ của bạn tới địa chỉ máy chủ VPN, một tin đi 71 byte, một tin về 59 byte, và tin về tới sau tin đi khoảng 1,8 đến 2,6 ms trong ba lần chạy. Trong các byte đó người nghe không tìm thấy tên đích, đường dẫn hay cookie. Nhưng kích thước vẫn lộ: khi tin gốc dài thêm 32 byte (39 thành 71), tin ngoài cũng dài thêm đúng 32 byte (71 thành 103). Người nghe cũng không sửa được tin mà không bị phát hiện: lật một bit của tin ngoài thì máy chủ VPN của mô hình báo `InvalidTag` và không chuyển gì tới trang web.

**3 · Máy chủ VPN.** Nó giải mã được nên thấy cả địa chỉ của bạn, đích và nội dung: nhật ký của nó trong mô hình ghi đủ ba thứ, vì tin gốc của mô hình không có lớp bảo vệ nào khác. Rồi nó gửi tin gốc đi tiếp từ địa chỉ của chính nó. Vậy đường hầm không xóa người đọc được tin; nó đổi người đó từ người nghe trên đường sang máy chủ VPN. Đây là điều bài nguồn gọi ngắn là “tin cậy nhà cung cấp VPN”. Mô hình dùng một khóa chung tạm. VPN thật còn phải xác thực máy chủ và thỏa thuận khóa: OpenVPN hỗ trợ khóa chia sẻ trước hoặc chứng chỉ ở hai phía, WireGuard gắn khóa công khai với từng bên. Về khóa và chứng chỉ, xem [bài sd-14-014](../sd-14-014/lesson.md).

**4 · Trang web.** Khi không có đường hầm, trang web ghi địa chỉ nguồn 127.0.0.2, nhãn của “địa chỉ của bạn”. Khi có đường hầm, nó ghi 127.0.0.3, nhãn của “địa chỉ máy chủ VPN”. Đó là điều bài nguồn gọi là che địa chỉ IP; MDN mô tả cùng cơ chế cho proxy: yêu cầu trông như xuất phát từ địa chỉ của proxy. Nhưng cả hai yêu cầu đều mang cùng cookie `sid-4711`, nên trang vẫn nhận ra cùng một phiên (về cookie, xem [bài sd-14-008](../sd-14-008/lesson.md)). Thêm một điều: mô hình có người nghe thứ hai ở đoạn giữa máy chủ VPN và trang, và người này đọc được nội dung ở dạng văn bản không mã hóa. Đường hầm kết thúc ở máy chủ VPN, nên đoạn sau nó chỉ được che nếu chính trang dùng HTTPS.

## Giới hạn cần nhớ

**Che địa chỉ không phải là ẩn danh.** VPN đổi bên nhìn thấy địa chỉ thật của bạn ở đầu kia: trang web thấy địa chỉ máy chủ VPN, còn máy chủ VPN thấy địa chỉ thật của bạn. Người nghe trên đường từ bạn tới máy chủ VPN vẫn thấy địa chỉ của bạn nối tới máy chủ VPN (ý 2 ở trên). Mọi thứ khác bạn gửi cho trang vẫn tới trang. MDN nêu ba công dụng của cookie: quản lý phiên (như trạng thái đăng nhập), cá nhân hóa và theo dõi. Vì thế các chữ “riêng tư” và “ẩn danh” trong danh sách ưu điểm của bài nguồn chỉ đúng với nội dung tin trước người nghe ở đoạn đầu; không đúng với địa chỉ của bạn trước người nghe đó, không đúng với máy chủ VPN và không đúng với trang bạn đã đăng nhập.

**Đường hầm chỉ che tin được đưa vào nó.** Trong mô hình, một yêu cầu tới đích được đặt cho đi thẳng khiến trang thấy 127.0.0.2, tức địa chỉ thật. Tài liệu OpenVPN nhắc cùng loại vấn đề: tin IPv6 có thể rò quanh một dịch vụ VPN chỉ xử lý địa chỉ IP kiểu cũ bốn số, DNS có thể rò (có tùy chọn `--block-outside-dns` cho Windows để chặn), và muốn bảo vệ đầy đủ thì cần thêm luật định tuyến hoặc luật tường lửa. Tài liệu `wg-quick` của WireGuard cũng cho một luật tường lửa “kill-switch” để chặn gói không đi qua đường hầm (về tường lửa, xem [bài sd-14-007](../sd-14-007/lesson.md)). Và vào được một mạng qua VPN chưa phải là được phép dùng mọi thứ trong mạng đó: OWASP viết rằng một kết nối VPN tự nó không được cấp quyền vào tài nguyên khác.

## Nhìn hình trả lời

Bạn bật VPN ở quán cà phê rồi đăng nhập vào một trang chỉ dùng kết nối không mã hóa. Người ngồi cùng Wi-Fi, máy chủ VPN và trang web, mỗi bên thấy gì về bạn?

<details>
<summary>Xem đáp án</summary>

Người ngồi cùng Wi-Fi chỉ thấy một kết nối tới máy chủ VPN, kích thước và thời điểm của các tin; tên tài khoản và nội dung nằm trong tin ngoài đã mã hóa nên họ không đọc được.
Máy chủ VPN thấy địa chỉ thật của bạn, đích và toàn bộ nội dung, kể cả thông tin đăng nhập, vì trang không dùng HTTPS. Ai nghe được đoạn từ máy chủ VPN tới trang cũng đọc được như vậy, vì đoạn đó không có đường hầm.
Trang web thấy địa chỉ của máy chủ VPN thay vì địa chỉ của bạn, nhưng nhận ra tài khoản của bạn vì chính bạn vừa đăng nhập vào nó.

</details>

<details>
<summary>Xem sâu hơn: mô hình đã chạy gì và điều đã chỉnh so với bài nguồn</summary>

Mô hình gồm một “thiết bị”, một “máy chủ VPN” và một “trang web”, cộng các “người nghe” là bộ chuyển tiếp chép lại từng đoạn byte đi qua rồi chuyển đi nguyên vẹn, giữ nguyên địa chỉ của bên gửi như một bộ định tuyến. Tất cả chạy trên 127.0.0.1, mỗi dịch vụ ở một cổng ngẫu nhiên trên 20000. Hai địa chỉ 127.0.0.2 và 127.0.0.3 chỉ là nhãn cho “địa chỉ của bạn” và “địa chỉ máy chủ VPN”; trên mạng thật chúng là địa chỉ công cộng. Tin ngoài dùng AES-GCM với khóa 256 bit sinh mới ở mỗi lần chạy. Mô hình không có: bắt tay và thỏa thuận khóa, xác thực máy chủ, chống phát lại tin cũ, gói IP và bảng định tuyến thật, DNS, IPv6, đo hiệu năng. Nó chạy bằng luồng Python nên thời gian của nó không nói gì về độ chậm của một VPN thật. Cả ba lần chạy cho cùng các kích thước; chỉ thời gian khác nhau chút ít.

Điều đã chỉnh so với bài nguồn:

- Bài nguồn nói bên ngoài không thấy dữ liệu đi qua. Điều đó chỉ đúng với đoạn nằm trong đường hầm; máy chủ VPN và đoạn sau nó thì không (bước 3 và 4).
- Bài nguồn coi mã hóa là một phần của VPN. Tài liệu OpenVPN nói nó cũng hỗ trợ đường hầm không mã hóa, nên đường hầm và mã hóa là hai việc riêng, thường đi cùng nhau.
- Bài nguồn coi “mọi lưu lượng đi qua máy chủ VPN” là một bước chắc chắn. Thực ra bảng định tuyến (OpenVPN) hay danh sách `AllowedIPs` (WireGuard) quyết định tin nào vào đường hầm, và tin ngoài danh sách đi đường thường.
- Bài nguồn ghi “riêng tư”, “ẩn danh”, “bảo mật”, “mã hóa” và “che địa chỉ IP” như năm ưu điểm riêng. Bài này gộp thành ba câu hỏi quan sát được: người nghe thấy gì, trang thấy địa chỉ nào, bạn phải tin ai; và cookie vẫn cho trang nhận ra phiên.
- Về nhược điểm: OWASP nêu rằng một trang có thể đòi thêm bước xác minh khi địa chỉ gắn với dịch vụ proxy hoặc VPN, nên địa chỉ chung của VPN có thể bị đối xử khác; “tin cậy nhà cung cấp” là điều bước 3 cho thấy; còn “chậm” thì mô hình không đo được nên bài không khẳng định.
- Bài nguồn không nói về đoạn sau máy chủ VPN, rò rỉ hay kill-switch; bài này thêm các phần đó.
- Điều “HTTPS che nội dung khỏi cả máy chủ VPN” là hiểu biết chung của người biên soạn: OWASP nói TLS che nội dung khỏi người đọc trộm giữa trình duyệt và trang, nhưng mô hình không thử HTTPS.
- Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-a-vpn-work.md): bốn bước, danh sách ưu điểm và nhược điểm.
- [OpenVPN — openvpn.8.rst](https://github.com/OpenVPN/openvpn/blob/43aee864957280d3fd060d477f90cb977708ddf9/doc/openvpn.8.rst) và [vpn-network-options.rst](https://github.com/OpenVPN/openvpn/blob/43aee864957280d3fd060d477f90cb977708ddf9/doc/man-sections/vpn-network-options.rst): đường hầm không mã hóa, khóa chia sẻ trước hoặc chứng chỉ, `--redirect-gateway`, rò IPv6, bảo vệ chống rò. Mục [windows-options.rst](https://github.com/OpenVPN/openvpn/blob/43aee864957280d3fd060d477f90cb977708ddf9/doc/man-sections/windows-options.rst): `--block-outside-dns`. Đọc từ bản clone của kho.
- [WireGuard — wg.8](https://github.com/WireGuard/wireguard-tools/blob/a998407747005ea7e4e0258d96f105c97241e1d3/src/man/wg.8) và [wg-quick.8](https://github.com/WireGuard/wireguard-tools/blob/a998407747005ea7e4e0258d96f105c97241e1d3/src/man/wg-quick.8): khóa công khai của từng bên, `AllowedIPs`, đường mặc định, “kill-switch”. Đọc từ bản clone của kho.
- [MDN — Proxy servers and tunneling](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/proxy_servers_and_tunneling/index.md) và [Using HTTP cookies](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/cookies/index.md): đường hầm là đóng gói dữ liệu, proxy khiến yêu cầu trông như từ địa chỉ của nó, công dụng của cookie. Đọc từ bản clone của kho.
- [OWASP — Transport Layer Security Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Transport_Layer_Security_Cheat_Sheet.md), [Credential Stuffing Prevention](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.md) và [Zero Trust Architecture](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Zero_Trust_Architecture_Cheat_Sheet.md): TLS che nội dung, địa chỉ gắn với dịch vụ VPN làm trang đòi thêm xác minh, kết nối VPN không tự cấp quyền. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-18. Mô hình chạy bằng Python 3.13 và `cryptography` 50.0.1; số liệu là ba lần chạy trên máy biên soạn. Cách chia bốn thẻ, mô hình và cách đối chiếu từng ý của bài nguồn là của người biên soạn. Bài viết và hình được thiết kế độc lập.

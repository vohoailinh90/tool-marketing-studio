# Các loại VPN: mỗi loại giải bài toán nào?

**VPN chia loại dễ nhất theo bài toán: đưa một máy lẻ vào mạng riêng (truy cập từ xa), nối hai mạng (site-to-site), hay cho mọi lưu lượng của một máy ra Internet qua một máy chủ trung gian (VPN riêng tư cá nhân). Cả ba dùng cùng một đường hầm; khác ở đầu bên kia và ở những địa chỉ được đưa vào hầm.**
Bài này chỉ phân loại và gợi cách chọn, không giải thích bên trong một đường hầm. Bài nguồn chỉ có một ảnh và một câu, nên bài dựng từ tài liệu và thử nghiệm riêng.

![Hai khung xếp dọc. Khung trên có ba thẻ, mỗi thẻ là một bài toán. Truy cập từ xa: một máy lẻ vào mạng riêng, chỉ dải của mạng riêng vào hầm. Nối hai mạng: hai cổng, mỗi cổng khai dải của cả hai đầu. VPN riêng tư cá nhân: mọi gói của máy vào hầm tới một máy chủ trung gian. Khung dưới có bốn câu hỏi để chọn, về đầu bên kia, địa chỉ vào hầm, tầng của hầm và quyền sau khi vào mạng.](../../diagrams/sd-14-027-main.svg)

## Từ viết tắt

- **VPN** (Virtual Private Network) — mạng riêng ảo: đường hầm mã hóa qua mạng công cộng để máy hoặc mạng ở xa nói chuyện như trong một mạng riêng.
- **IPsec** (Internet Protocol SECurity) — an toàn giao thức Internet: một họ giao thức mã hóa gói IP, nhiều phần mềm VPN dùng.
- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ và chuyển gói tin giữa các máy; địa chỉ IP là địa chỉ của một máy trên mạng.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng về bảo mật ứng dụng; bài dùng hướng dẫn của họ để đối chiếu.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, tài liệu tra cứu công nghệ web; bài dùng nó để đối chiếu.

## Đọc hình

Đường hầm là bọc dữ liệu riêng vào gói khác để đi qua mạng công cộng (định nghĩa của MDN). Mỗi công cụ có một danh sách dải địa chỉ quyết định gói nào vào hầm: WireGuard ghi ở `AllowedIPs`, OpenVPN ở `route` và `redirect-gateway`, strongSwan (phần mềm VPN dùng IPsec) ở `local_ts` và `remote_ts`.

**1 · Truy cập từ xa.** Một người ở ngoài cần dùng mạng riêng của cơ quan: một đầu là máy lẻ, đầu kia là cổng của mạng. README của strongSwan gọi máy lẻ là roadwarrior và nói cổng phục vụ số máy khách bất kỳ, thường có địa chỉ thay đổi; nên cổng không ghi địa chỉ máy khách, chỉ ghi dải của mạng mình, `local_ts = 10.1.0.0/16` (`/16` nghĩa là mọi địa chỉ bắt đầu bằng `10.1`). Mẫu `server.conf` của OpenVPN: một máy chủ, nhiều máy khách; thêm `push "route 192.168.10.0 255.255.255.0"` để máy khách với tới mạng sau máy chủ, còn gói tới nơi khác vẫn ra Internet bình thường.

**2 · Nối hai mạng (site-to-site).** Hai văn phòng, mỗi nơi một mạng riêng, máy bên này tới máy bên kia như cùng một mạng; hai đầu hầm là hai cổng. Ví dụ Site-to-Site của strongSwan nối `10.1.0.0/16` với `10.2.0.0/16`: chỉ hai cổng được cấu hình, mỗi cổng khai cả `local_ts` lẫn `remote_ts`. Với mạng nằm sau một máy khách, OpenVPN dùng hai dòng: `route` đưa gói từ hệ điều hành vào OpenVPN, `iroute` đưa tiếp tới đúng máy khách đó.

**3 · VPN riêng tư cá nhân.** Không có mạng riêng nào để vào; bài toán là đi ra Internet qua một máy chủ khác. Cơ chế vẫn là danh sách ấy, nhưng là mọi địa chỉ: man page wg-quick có ví dụ máy khách "tunneling all traffic" với `AllowedIPs = 0.0.0.0/0` và một dòng `DNS`, còn mẫu `server.conf` của OpenVPN mô tả `redirect-gateway` là cho mọi lưu lượng, kể cả tra tên miền, đi qua VPN. Giấu địa chỉ thật hay tránh Wi-Fi công cộng là mục đích của người dùng, không phải điều hầm tự bảo đảm (hiểu biết chung của người biên soạn).

**Hầm ở tầng nào.** Trục thứ hai chọn thứ được chở, không chọn bài toán. OpenVPN `dev tun` chở gói IP (mặc định), `dev tap` chở khung Ethernet để bắc cầu Ethernet; hai đầu phải cùng loại. Tài liệu nhân Linux cũng chia thiết bị tun (gói IP) và tap (khung Ethernet). Mã WireGuard trong nhân chỉ xử lý gói IP. Mỗi đầu hầm còn phải chứng minh mình là ai: xem [bài sd-14-014](../sd-14-014/lesson.md).

## Giới hạn cần nhớ

Đường hầm chỉ quyết định gói nào đi qua; nó không quyết định ai được làm gì sau đó, và không che gói nằm ngoài danh sách.

Về quyền: Zero Trust cheat sheet của OWASP viết rằng một kết nối VPN tự nó không được cấp quyền vào tài nguyên khác.

Về phạm vi: tuyến cụ thể hơn thắng tuyến chung, nên mạng cục bộ vẫn đi thẳng dù mọi thứ khác vào hầm; OpenVPN có cờ `block-local` để chặn điều đó, và wg-quick có ví dụ "kill switch" bằng luật tường lửa ([bài sd-14-013](../sd-14-013/lesson.md)). VPN riêng tư cũng chỉ bảo vệ đoạn tới máy chủ VPN; người vận hành máy chủ đó thấy phần không được mã hóa riêng (hiểu biết chung của người biên soạn).

## Nhìn hình trả lời

Một máy xách tay có `AllowedIPs = 10.1.0.0/16` mở một trang web công cộng. Gói có vào hầm không? Muốn máy này thành VPN riêng tư cá nhân thì đổi gì?

<details>
<summary>Xem đáp án</summary>

Không: địa chỉ trang không thuộc `10.1.0.0/16` nên gói đi thẳng. Đổi danh sách thành `0.0.0.0/0` (wg-quick khi gặp tuyến này dùng `ip-rule` để thay đường mặc định) và giữ một đường riêng tới chính máy chủ VPN, nếu không gói đã mã hóa gửi tới nó cũng bị đưa vào hầm; OpenVPN làm việc này ở bước đầu của `redirect-gateway`.

</details>

<details>
<summary>Xem sâu hơn: thử trên nhân Linux và một mô hình bảng chỉ đường</summary>

Máy tác giả không có `wg` hay `openvpn`, nhân cũng không có WireGuard, nhưng có `/dev/net/tun`. Nên không chạy VPN thật mà làm ba việc bằng Python 3.13 (một lần chạy trên máy này).

**1 · Đọc cấu hình mẫu.** Man page wg-quick có ba cấu hình mẫu: một máy khách với `0.0.0.0/0`, một máy chủ ba peer (peer thứ hai có `192.168.0.0/16`) và một cấu hình chỉ đưa cổng 22 vào hầm. `server.conf` mẫu của OpenVPN có 14 lệnh bật và 26 dòng tùy chọn bị comment, trong đó có `redirect-gateway` và `client-config-dir`.

**2 · Thử trên bảng chỉ đường thật của nhân Linux.** Trong một không gian mạng riêng (`unshare -n`; mọi thứ mất khi script thoát), script mở hai thiết bị tun, `tunA` làm "hầm" và `tunB` làm "đường thường", thêm tuyến, gửi một gói tin tới từng địa chỉ rồi xem thiết bị nào đọc được nó.
- Một phần vào hầm: `0.0.0.0/0` qua `tunB`, `10.1.0.0/16` qua `tunA`. `10.1.5.9` tới `tunA`; `203.0.113.10` tới `tunB`.
- Kiểu `def1` của OpenVPN: `0.0.0.0/0` vẫn qua `tunB`, thêm `0.0.0.0/1` và `128.0.0.0/1` qua `tunA`. `10.20.30.40` và `203.0.113.10` tới `tunA`: tuyến mặc định gốc còn đó nhưng không được chọn. Thêm tuyến `198.51.100.7/32` qua `tunB` (địa chỉ giả định của máy chủ VPN) thì riêng nó ra ngoài hầm; bỏ tuyến ấy thì nó tới `tunA`.
- Chồng lấn: `10.1.0.0/16` qua `tunA`, `10.1.5.0/24` qua `tunB`. `10.1.5.9` tới `tunB`, `10.1.6.9` tới `tunA`: tiền tố dài nhất thắng. Địa chỉ không khớp tuyến nào thì gửi thất bại ngay (`ENETUNREACH`).
- Chở gì: từ tun đọc ra chính gói IP đã gửi (byte đầu `0x45`, tức phiên bản 4). Từ tap, thứ đọc được đầu tiên là một khung Ethernet 42 byte gửi quảng bá, hỏi ai giữ `10.28.0.7`, chưa phải gói đã gửi.

**3 · Mô hình** (`ipaddress`, tiền tố dài nhất thắng) cho cùng kết quả ở các ca trên, và mô phỏng thêm điều không thử được vì nhân thiếu WireGuard: với ba peer của ví dụ man page, `192.168.5.5` tới peer 2, `203.0.113.10` không khớp peer nào, và thêm peer `10.192.0.0/16` thì `10.192.122.3` vẫn tới peer 1. Chiều nhận (đọc mã `receive.c`, chưa chạy): nguồn của gói đã giải mã phải thuộc peer gửi nó, nên peer 2 gửi gói nguồn `10.192.122.3` (của peer 1) thì bị bỏ.

Bài nguồn chỉ có một câu nói VPN phức tạp, không có gì để kiểm chứng; bài thay nó bằng nội dung có nguồn riêng và không dùng ảnh của nó. Bài không bàn giao thức VPN khác hay VPN chạy trong trình duyệt.

</details>

## Nguồn đối chiếu

- [ByteByteGo: bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/types-of-vpns.md).
- OpenVPN: [vpn-network-options](https://github.com/OpenVPN/openvpn/blob/1b0bd8c6f60df96356e956b9982550902a622c5a/doc/man-sections/vpn-network-options.rst), [server-options](https://github.com/OpenVPN/openvpn/blob/1b0bd8c6f60df96356e956b9982550902a622c5a/doc/man-sections/server-options.rst), [server.conf](https://github.com/OpenVPN/openvpn/blob/1b0bd8c6f60df96356e956b9982550902a622c5a/sample/sample-config-files/server.conf).
- WireGuard: [wg.8](https://github.com/WireGuard/wireguard-tools/blob/a998407747005ea7e4e0258d96f105c97241e1d3/src/man/wg.8), [wg-quick.8](https://github.com/WireGuard/wireguard-tools/blob/a998407747005ea7e4e0258d96f105c97241e1d3/src/man/wg-quick.8).
- Nhân Linux: [tuntap.rst](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/Documentation/networking/tuntap.rst), [allowedips.c](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/drivers/net/wireguard/allowedips.c), [device.c](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/drivers/net/wireguard/device.c), [receive.c](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/drivers/net/wireguard/receive.c).
- strongSwan: [README.md](https://github.com/strongswan/strongswan/blob/f9cd483cd97182def563e17b86e4fbd3a90c03d2/README.md).
- MDN: [Proxy servers and tunneling](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/proxy_servers_and_tunneling/index.md).
- OWASP: [Zero Trust Architecture Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Zero_Trust_Architecture_Cheat_Sheet.md).

Đã đọc nguồn ngày 2026-10-18. Cách chia ba bài toán, tên "VPN riêng tư cá nhân" và mô hình bảng chỉ đường là của người biên soạn. Bài viết và hình được thiết kế độc lập.

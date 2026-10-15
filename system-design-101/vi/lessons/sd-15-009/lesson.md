# Mô hình OSI

**Gửi một yêu cầu HTTP qua mạng là việc của nhiều tầng, mỗi tầng một nhiệm vụ.** OSI chia chức năng mạng thành bảy tầng để mỗi tầng chỉ cần biết tiêu đề của chính nó, không cần hiểu ý nghĩa dữ liệu tầng trên.

![Hai khung dọc: bảy tầng OSI từ ứng dụng, trình bày, phiên, giao vận, mạng, liên kết đến vật lý; khi gửi đi, dữ liệu HTTP lần lượt được thêm tiêu đề TCP, tiêu đề IP, rồi tiêu đề và phần cuối Ethernet; bên nhận gỡ ngược lại từng lớp. Địa chỉ MAC đổi qua từng chặng, địa chỉ IP đi suốt đường.](../../diagrams/sd-15-009-main.svg)

## Từ viết tắt

- **OSI** (Open Systems Interconnection) — kết nối các hệ thống mở: mô hình chia chức năng mạng thành bảy tầng.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu (request) và máy chủ gửi trả lời (response).
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: tạo kết nối đáng tin cậy, dữ liệu đến đủ và đúng thứ tự.
- **UDP** (User Datagram Protocol) — giao thức gói dữ liệu người dùng: gửi gói tin đơn giản, nhanh, không có kết nối và không bảo đảm đến đủ hay đúng thứ tự.
- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ và chuyển gói tin giữa các máy; địa chỉ IP là địa chỉ của một máy trên mạng.
- **MAC** (Media Access Control) — điều khiển truy cập phương tiện: địa chỉ MAC là địa chỉ của card mạng, chỉ có nghĩa trên một đoạn mạng và đổi qua từng chặng.
- **FCS** (Frame Check Sequence) — chuỗi kiểm tra khung: đoạn ở cuối khung Ethernet để phát hiện khung bị lỗi.
- **NAT** (Network Address Translation) — dịch địa chỉ mạng: thiết bị đổi địa chỉ nguồn hoặc đích của gói tin khi đi qua; nhờ nó nhiều máy dùng chung được một địa chỉ công cộng.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa giữ kín dữ liệu giữa client và máy chủ.
- **QUIC** (Quick UDP Internet Connections) — tên gọi ban đầu của giao thức truyền tải mà HTTP/3 dùng thay cho TCP; ngày nay QUIC thường được dùng như một tên riêng.

## Đọc hình

**Gửi đi.** Ứng dụng tạo dữ liệu HTTP. Tầng giao vận thêm tiêu đề TCP (cổng nguồn, cổng đích, số thứ tự). Tầng mạng thêm tiêu đề IP (địa chỉ nguồn, đích). Tầng liên kết thêm tiêu đề Ethernet (địa chỉ MAC) và phần cuối kiểm tra lỗi. Tầng vật lý đưa thành bit lên dây hoặc sóng.

**Nhận về.** Máy nhận gỡ ngược: bỏ tiêu đề Ethernet, rồi IP, rồi TCP, cuối cùng đưa dữ liệu HTTP cho ứng dụng.

## Giới hạn cần nhớ

OSI là *mô hình tham chiếu* để hiểu và đặt tên, không phải bản thiết kế mà mạng thật tuân theo từng tầng. Internet chạy theo bộ giao thức TCP/IP gọn hơn, và nhiều giao thức không nằm vừa một tầng: TLS thường được xếp ở khoảng tầng 5–6 hoặc ngay dưới ứng dụng; QUIC kết hợp chức năng giao vận với mã hóa trên nền UDP. Hai tầng 5 và 6 ít khi được tách riêng trong thực tế.

## Nhìn hình thử trả lời

Gói đi từ máy A tới máy B qua hai router. Địa chỉ IP đích và địa chỉ MAC đích thay đổi thế nào dọc đường?

<details>
<summary>Xem đáp án</summary>

IP đích giữ nguyên suốt đường (ngoại trừ khi có NAT hay cơ chế tương tự). MAC đích đổi qua từng chặng: mỗi chặng chỉ tới thiết bị kế tiếp trong cùng mạng liên kết.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Tên gọi dữ liệu:** thường gọi là segment ở TCP, datagram ở UDP, packet ở IP, frame ở tầng liên kết; cách gọi có thể khác theo tài liệu.
- **Tiêu đề và phần cuối:** Ethernet có thêm đoạn kiểm tra lỗi (FCS) ở cuối khung, nên hình có "FCS".
- **Dùng khi gỡ lỗi:** "tầng nào hỏng?" giúp thu hẹp: dây và đèn (1), địa chỉ MAC và switch (2), IP và định tuyến (3), cổng và kết nối (4), ứng dụng (7).
- **TCP/IP:** thường mô tả bằng bốn hoặc năm tầng, gộp các tầng ứng dụng, trình bày và phiên.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-osi-model.md).
- [ISO/IEC 7498-1](https://www.iso.org/standard/20269.html): mô hình tham chiếu OSI.
- [RFC 1122](https://www.rfc-editor.org/rfc/rfc1122): các tầng của bộ giao thức Internet.
- [RFC 9293 — TCP](https://www.rfc-editor.org/rfc/rfc9293) và [RFC 791 — IPv4](https://www.rfc-editor.org/rfc/rfc791).
- [IEEE 802.3 — Ethernet](https://www.ieee802.org/3/): địa chỉ MAC và FCS của khung.

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

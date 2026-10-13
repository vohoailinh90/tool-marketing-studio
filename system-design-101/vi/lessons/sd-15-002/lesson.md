# IPv4 và IPv6

**Mỗi thiết bị trên Internet cần một địa chỉ để gói tin tìm tới.** IPv4 dùng địa chỉ 32 bit; IPv6 ra đời chủ yếu vì số địa chỉ IPv4 đã không còn đủ rộng rãi.

![Ba khung dọc: địa chỉ IPv4 32 bit ví dụ 192.0.2.12 và IPv6 128 bit ví dụ 2001:db8::1; tiêu đề IPv4 từ 20 byte có checksum, tiêu đề IPv6 đúng 40 byte không có checksum; dual stack chạy cả hai giao thức và dùng bản ghi A hoặc AAAA.](../../diagrams/sd-15-002-main.svg)

## Đọc hình

**Địa chỉ.** IPv4 có 2³² giá trị (khoảng 4,3 tỷ), viết bốn số thập phân cách dấu chấm. IPv6 có 2¹²⁸ giá trị, viết tám nhóm số hex cách dấu hai chấm; được rút gọn bằng cách bỏ số 0 đầu và dùng `::` một lần để thay chuỗi nhóm toàn 0.

**Tiêu đề gói tin.** Tiêu đề IPv4 tối thiểu 20 byte, dài thay đổi theo phần tùy chọn, và có checksum riêng. Tiêu đề IPv6 cố định 40 byte, bỏ checksum; thông tin hiếm dùng nằm trong *extension header* tùy chọn. Router không phân mảnh gói IPv6; chỉ máy gửi làm việc đó.

**Chuyển đổi.** *Dual stack* nghĩa là một máy chạy cả hai giao thức cùng lúc. DNS có thể trả bản ghi A (IPv4) và AAAA (IPv6); phần mềm chọn địa chỉ nào kết nối được.

## Giới hạn cần nhớ

IPv6 giải quyết bài toán số địa chỉ, không tự khiến mạng nhanh hơn. IPv4 vẫn tồn tại lâu nhờ NAT và các cách dùng chung địa chỉ; hai giao thức không nói chuyện trực tiếp với nhau nên cần dual stack hoặc cơ chế chuyển đổi. Dùng IPv6 không thay thế tường lửa hay kiểm soát truy cập.

## Nhìn hình thử trả lời

Một tên miền có cả bản ghi A và AAAA. Máy của bạn chỉ có kết nối IPv4. Chuyện gì nên xảy ra?

<details>
<summary>Xem đáp án</summary>

Phần mềm nên dùng địa chỉ IPv4 từ bản ghi A. Có AAAA không có nghĩa mọi máy đều đi được bằng IPv6; client thường thử các địa chỉ và chọn đường kết nối được.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Địa chỉ ví dụ:** 192.0.2.0/24 và 2001:db8::/32 là dải dành cho tài liệu; không trỏ tới máy thật.
- **Kích thước IPv6 128 bit:** khoảng 3,4×10³⁸ giá trị; con số lớn để gán theo cấp bậc dễ, không phải để dùng hết từng địa chỉ.
- **Chọn địa chỉ:** thuật toán "Happy Eyeballs" thử song song IPv6 và IPv4 để người dùng không phải chờ khi một đường hỏng.
- **Phân mảnh IPv4:** router có thể phân mảnh gói IPv4 (trừ khi gói đặt cờ cấm); trong IPv6 máy gửi tự quản kích thước, thường qua Path MTU Discovery.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/ipv4-vs-ipv6.md).
- [RFC 791 — IPv4](https://www.rfc-editor.org/rfc/rfc791) và [RFC 8200 — IPv6](https://www.rfc-editor.org/rfc/rfc8200): tiêu đề, extension header, phân mảnh.
- [RFC 4291 — Địa chỉ IPv6](https://www.rfc-editor.org/rfc/rfc4291): dạng viết và rút gọn.
- [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737) và [RFC 3849](https://www.rfc-editor.org/rfc/rfc3849): địa chỉ dành cho tài liệu.
- [RFC 8305 — Happy Eyeballs](https://www.rfc-editor.org/rfc/rfc8305).

Đã đọc nguồn ngày 2026-10-13. Bài viết và hình được thiết kế độc lập; không giữ câu "dual stack là cách tốt nhất" của bài nguồn vì còn tùy hạ tầng.

# Phân biệt WAN, LAN, PAN và MAN

**Mạng được gọi tên theo phạm vi nó phủ.** Bốn tên này, từ nhỏ tới lớn, giúp nói nhanh "mạng này nằm ở quy mô nào" và thường gợi ý cả công nghệ, người quản lý và chi phí.

![Bốn khung dọc theo phạm vi tăng dần: PAN quanh một người trong vài mét như Bluetooth hoặc USB; LAN trong một nơi như nhà, văn phòng hoặc tòa nhà bằng Ethernet hoặc Wi-Fi để dùng chung máy in và máy chủ tệp; MAN phủ cả một thành phố hoặc khuôn viên lớn và nối nhiều cơ sở; WAN trải nhiều thành phố và quốc gia qua nhà mạng, VPN hoặc đường thuê riêng, trong đó Internet là mạng của các mạng. Ranh giới là quy ước, không cứng.](../../diagrams/sd-01-013-main.svg)

## Đọc hình

- **PAN (Personal Area Network):** quanh một người, cỡ vài mét. Ví dụ: điện thoại nối tai nghe Bluetooth, máy tính nối điện thoại qua USB.
- **LAN (Local Area Network):** trong một nơi như nhà, văn phòng, tòa nhà. Thường dùng Ethernet hoặc Wi-Fi; dùng để chung máy in, máy chủ tệp, đường ra Internet.
- **MAN (Metropolitan Area Network):** phủ một thành phố hoặc khuôn viên lớn, ví dụ nối nhiều cơ sở của một trường đại học hoặc các cơ quan trong một thành phố.
- **WAN (Wide Area Network):** trải nhiều thành phố, quốc gia, thường dựa trên đường truyền thuê từ nhà mạng, VPN hoặc đường thuê riêng. Ví dụ: nối các chi nhánh của một công ty đa quốc gia.

## Giới hạn cần nhớ

Các ngưỡng chỉ là quy ước: một khuôn viên lớn có thể gọi là LAN lớn hay MAN tùy người. Ngày nay người ta hay phân biệt theo ai quản lý và dùng đường truyền nào: LAN thường thuộc một tổ chức và tự quản, còn WAN thường phải thuê hoặc đi qua mạng của bên khác. Internet không phải một WAN của một tổ chức; nó là sự nối nhau của rất nhiều mạng do nhiều bên vận hành.

## Nhìn hình thử trả lời

Một công ty có ba văn phòng ở ba thành phố, nối với nhau bằng VPN chạy qua Internet. Bên trong từng văn phòng là mạng gì, và phần nối giữa các văn phòng là mạng gì?

<details>
<summary>Xem đáp án</summary>

Bên trong từng văn phòng là LAN. Phần nối ba văn phòng qua các thành phố là WAN, ở đây được dựng bằng VPN trên Internet.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **WLAN:** LAN không dây, thường dùng Wi-Fi; PAN không dây thường dùng Bluetooth.
- **Công nghệ điển hình:** họ chuẩn IEEE 802 mô tả chủ yếu mạng LAN và MAN; Ethernet là 802.3, Wi-Fi là 802.11, Bluetooth là 802.15.1.
- **SD-WAN:** cách quản lý nhiều đường WAN bằng phần mềm; không đổi ý nghĩa của "WAN" là mạng nối các nơi ở xa.
- **Khác:** còn có các tên như mạng khuôn viên (CAN) hay mạng lưu trữ (SAN); bài này chỉ bàn bốn tên phổ biến.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-differences-between-wan-lan-pan-and-man.md).
- [IEEE 802 LAN/MAN Standards Committee](https://www.ieee802.org/): họ chuẩn LAN và MAN.
- [Cloudflare — What is a LAN?](https://www.cloudflare.com/learning/network-layer/what-is-a-lan/) và [What is a WAN?](https://www.cloudflare.com/learning/network-layer/what-is-a-wan/).
- [RFC 1983 — Internet Users' Glossary](https://www.rfc-editor.org/rfc/rfc1983): định nghĩa các thuật ngữ mạng.

Đã đọc nguồn ngày 2026-10-13; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

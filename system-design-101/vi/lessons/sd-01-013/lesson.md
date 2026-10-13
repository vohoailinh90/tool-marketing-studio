# Phân biệt WAN, LAN, PAN và MAN

**Mạng được gọi tên theo phạm vi nó phủ.** Bốn tên này, từ nhỏ tới lớn, giúp nói nhanh "mạng này nằm ở quy mô nào" và thường gợi ý cả công nghệ, người quản lý và chi phí.

![Bốn khung dọc theo phạm vi tăng dần: PAN quanh một người trong vài mét như Bluetooth hoặc USB, ví dụ đồng hồ thông minh nối điện thoại; LAN trong một nơi như nhà, văn phòng hoặc tòa nhà bằng Ethernet hoặc Wi-Fi, ví dụ TV, loa và máy tính cùng một mạng Wi-Fi trong nhà; MAN phủ cả một thành phố hoặc khuôn viên lớn, ví dụ mạng cáp quang trong thành phố; WAN trải nhiều thành phố và quốc gia qua nhà mạng, cáp biển hoặc VPN, trong đó Internet là mạng của các mạng. Ranh giới là quy ước, không cứng.](../../diagrams/sd-01-013-main.svg)

## Đọc hình

- **PAN (Personal Area Network):** quanh một người, cỡ vài mét. Ví dụ: đồng hồ thông minh hoặc vòng đeo tay nối với điện thoại, tay cầm chơi game nối với máy.
- **LAN (Local Area Network):** trong một nơi như nhà, văn phòng, tòa nhà. Thường dùng Ethernet hoặc Wi-Fi; các thiết bị cùng thuộc một mạng cục bộ, nối qua switch hoặc điểm truy cập; chúng thường có chung đường ra Internet nhưng không bắt buộc. Ví dụ: TV, loa và máy tính cùng dùng một router Wi-Fi trong một căn nhà.
- **MAN (Metropolitan Area Network):** phủ một thành phố hoặc khuôn viên lớn. Ví dụ: mạng cáp quang của một nhà mạng trong thành phố, hoặc mạng nối các chi nhánh của một ngân hàng trong cùng thành phố.
- **WAN (Wide Area Network):** trải nhiều thành phố, quốc gia, thường dựa trên đường truyền thuê từ nhà mạng, cáp biển, VPN hoặc đường thuê riêng. Ví dụ: một chuỗi cửa hàng nối mọi cửa hàng về một trung tâm dữ liệu.

## Giới hạn cần nhớ

Các ngưỡng chỉ là quy ước, và khuôn viên lớn là ca ở biên: có người gọi là LAN lớn, có người gọi là MAN hay CAN. Ngày nay người ta hay phân biệt theo ai quản lý và dùng đường truyền nào: LAN thường thuộc một tổ chức và tự quản, còn WAN thường phải thuê hoặc đi qua mạng của bên khác. Internet không phải một WAN của một tổ chức; nó là sự nối nhau của rất nhiều mạng do nhiều bên vận hành.

## Nhìn hình thử trả lời

Một công ty có ba văn phòng ở ba thành phố, nối với nhau bằng VPN chạy qua Internet. Bên trong từng văn phòng là mạng gì, và phần nối giữa các văn phòng là mạng gì?

<details>
<summary>Xem đáp án</summary>

Bên trong từng văn phòng là LAN. Phần nối ba văn phòng qua các thành phố là WAN, ở đây được dựng bằng VPN trên Internet.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **WLAN:** LAN không dây, thường dùng Wi-Fi; PAN không dây thường dùng Bluetooth.
- **Công nghệ điển hình:** họ chuẩn IEEE 802 mô tả chủ yếu mạng LAN và MAN; Ethernet là 802.3 và Wi-Fi là 802.11. Bluetooth do Bluetooth SIG duy trì; IEEE 802.15.1 là chuẩn được xây dựng từ đặc tả Bluetooth đời đầu (v1.1).
- **SD-WAN:** cách quản lý nhiều đường WAN bằng phần mềm; không đổi ý nghĩa của "WAN" là mạng nối các nơi ở xa.
- **Khác:** còn có các tên như mạng khuôn viên (CAN) hay mạng lưu trữ (SAN); bài này chỉ bàn bốn tên phổ biến.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-differences-between-wan-lan-pan-and-man.md).
- [IEEE 802 LAN/MAN Standards Committee](https://www.ieee802.org/): họ chuẩn LAN và MAN.
- [Cloudflare — What is a LAN?](https://www.cloudflare.com/learning/network-layer/what-is-a-lan/) và [What is a WAN?](https://www.cloudflare.com/learning/network-layer/what-is-a-wan/).
- [Cloudflare — What is SD-WAN?](https://www.cloudflare.com/learning/network-layer/what-is-sd-wan/).
- [RFC 1122 §1.1](https://www.rfc-editor.org/rfc/rfc1122): Internet gồm nhiều mạng nối nhau; [IEEE 802.3](https://www.ieee802.org/3/), [802.11](https://www.ieee802.org/11/), [802.15](https://www.ieee802.org/15/pub/TG1.html) và [Bluetooth SIG](https://www.bluetooth.com/specifications/).

Đã đọc nguồn ngày 2026-10-13; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

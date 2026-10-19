# Kiến trúc microservice của Airbnb qua ba giai đoạn

**Theo bài nguồn, Airbnb đi qua ba giai đoạn: một khối nguyên (2008–2017), microservice (2017–2020), rồi kết hợp microservice và macroservice (từ 2020); mỗi bước giải quyết vấn đề của bước trước và sinh ra vấn đề mới.**
Bài này đọc ba giai đoạn theo cặp "giải pháp, vấn đề mới", dựa trên bài nói của Jessica Tai mà nguồn dẫn lại.

![Ba bước nối nhau. Bước một, khối nguyên 2008 đến 2017: một ứng dụng Ruby on Rails; vấn đề là quyền sở hữu mã giữa các đội rối, có mã không ai sở hữu, và triển khai chậm. Bước hai, microservice 2017 đến 2020: dịch vụ lấy dữ liệu, dịch vụ dữ liệu cho logic nghiệp vụ, dịch vụ quy trình ghi, dịch vụ gộp cho giao diện, mỗi dịch vụ có một đội sở hữu; vấn đề là hàng trăm dịch vụ và phụ thuộc khó cho con người quản lý. Bước ba, micro kết hợp macroservice từ 2020: tập trung thống nhất các API. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-022-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình gọi chức năng của chương trình khác.
- **UI** (User Interface) — giao diện người dùng: phần màn hình người dùng nhìn và bấm.

## Đọc hình

**Khối nguyên (2008–2017).** Airbnb bắt đầu là một chợ đơn giản giữa chủ nhà và khách, xây trong một ứng dụng Ruby on Rails. Vấn đề theo nguồn:
- Quyền sở hữu giữa các đội rối, có mã không ai sở hữu.
- Triển khai chậm.

**Microservice (2017–2020).** Microservice nhắm vào hai vấn đề đó. Các loại dịch vụ chính:
- Dịch vụ lấy dữ liệu.
- Dịch vụ dữ liệu cho logic nghiệp vụ.
- Dịch vụ cho quy trình ghi.
- Dịch vụ gộp dữ liệu cho UI.
- Mỗi dịch vụ có đúng một đội sở hữu.

Vấn đề mới: hàng trăm dịch vụ và các phụ thuộc giữa chúng khó cho con người quản lý.

**Micro kết hợp macroservice (từ 2020).** Đây là hướng Airbnb đang làm khi bài nói diễn ra. Mô hình lai này tập trung vào việc thống nhất các API.

## Giới hạn cần nhớ

Bài nguồn không định nghĩa macroservice, không nói thống nhất API nghĩa là gì cụ thể, và không có con số về số dịch vụ hay tốc độ triển khai. Chữ "hiện nay" của nguồn là thời điểm bài nói, không phải hôm nay. Cách hiểu macroservice ở phần dưới là của người biên soạn.

## Nhìn hình thử trả lời

Ở giai đoạn khối nguyên, một lỗi trong phần thanh toán có thể chờ lâu mới được sửa. Theo hình, hai vấn đề nào góp phần, và microservice giải quyết chúng thế nào?

<details>
<summary>Xem đáp án</summary>

Quyền sở hữu rối (không rõ đội nào phải sửa phần mã đó) và triển khai chậm (sửa xong vẫn phải chờ đưa cả khối lên). Microservice cho mỗi dịch vụ một đội sở hữu, và mỗi dịch vụ được triển khai riêng.

</details>

<details>
<summary>Xem sâu hơn: macroservice có thể là gì</summary>

- Một cách hiểu thường gặp: gộp nhiều microservice nhỏ có liên quan sau một dịch vụ lớn hơn, với một API chung ra bên ngoài.
- Bên trong vẫn có thể là nhiều dịch vụ nhỏ; bên ngoài chỉ thấy ít điểm gọi hơn.
- Mục đích: giảm số phụ thuộc mà mỗi đội phải nắm.

Đây là cách hiểu của người biên soạn, không phải định nghĩa của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/evolution-of-airbnb's-microservice.md): ba giai đoạn, vấn đề của từng giai đoạn và các loại dịch vụ.

Đã đọc nguồn ngày 2026-10-19. Bài nói của Jessica Tai mà nguồn dẫn chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

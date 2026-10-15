# 3 tình huống dùng API Gateway

**Cùng một cửa vào API, ba bài toán tổ chức khác nhau.** Hình dùng ví dụ giả định để phân biệt kết nối đối tác, cung cấp API như sản phẩm và nối các nền tảng.

![Ba khung dọc: đối tác gọi API giao hàng qua gateway; nhà phát triển khám phá và đăng ký gói API qua portal rồi gọi gateway; web và ứng dụng di động gọi gateway để tới các dịch vụ cũ và mới. Gateway xử lý lời gọi, còn portal và quản lý sản phẩm có vai riêng.](../../diagrams/sd-01-023-main.svg)

## Đọc hình

1. **Kết nối đối tác.** Một cửa hàng cho hãng vận chuyển gọi API tra cứu đơn. Gateway định tuyến và áp chính sách truy cập; dịch vụ đơn hàng vẫn kiểm tra hãng đó có quyền xem đơn cụ thể hay không.
2. **Cung cấp API như sản phẩm.** Nhóm dữ liệu mở API thời tiết cho nhiều ứng dụng. Portal giúp tìm tài liệu và đăng ký gói; gateway xử lý các lời gọi theo cấu hình. Danh mục, đăng ký, tính phí và hỗ trợ khách hàng cần các thành phần hoặc tích hợp thích hợp; cài gateway không tự tạo ra một chợ API hoàn chỉnh.
3. **Nối nhiều nền tảng.** Web và ứng dụng di động dùng một cửa vào trước dịch vụ cũ và mới. Gateway có thể định tuyến và đổi định dạng theo cấu hình. Hợp đồng API, ý nghĩa dữ liệu và việc chuyển đổi vẫn phải được thiết kế; nó không tự làm mọi nền tảng tương thích.

## Giới hạn cần nhớ

Ba tình huống không loại trừ nhau. Gateway thêm một chặng xử lý và có thể thành nút nghẽn hoặc điểm lỗi tập trung. Cần thiết kế khả năng chịu lỗi và chặn đường đi vòng trực tiếp vào backend nếu chính sách ở gateway phải được thực thi. Các ví dụ không khẳng định một sản phẩm hỗ trợ sẵn mọi chức năng.

## Nhìn hình thử trả lời

Bạn đã có gateway nhưng đối tác chưa biết API nào tồn tại, không có tài liệu hay chỗ đăng ký. Còn thiếu phần nào trong hình?

<details>
<summary>Xem đáp án</summary>

Phần khám phá và tiếp nhận nhà phát triển: portal, tài liệu và quy trình đăng ký sản phẩm API. Đổi thuật toán định tuyến ở gateway không giải quyết việc đối tác chưa biết cách bắt đầu.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **API** là giao diện lập trình ứng dụng; **portal** là cổng thông tin cho người dùng API, khác gateway xử lý lời gọi lúc chạy.
- **Tách vai theo sản phẩm:** Azure API Management có gateway, mặt phẳng quản lý và developer portal. Đây là một ví dụ triển khai, không phải quy tắc mọi hệ thống phải có đúng ba dịch vụ.
- **Khóa API:** trong usage plan của AWS, khóa dùng nhận diện client cho kế hoạch sử dụng; không dùng nó thay cơ chế xác thực và phân quyền. Hạn mức cũng không phải bảo đảm tuyệt đối chống quá tải.

</details>

## Nguồn đối chiếu

- [ByteByteGo, body tại snapshot ghim](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-3-api-gateway-use-cases.md): ba chủ đề của vị trí mục lục này; ví dụ và hình do bài tự thiết kế.
- [Microsoft — API Management: tình huống và thành phần](https://learn.microsoft.com/en-us/azure/api-management/api-management-key-concepts).
- [Microsoft — Gateway Routing](https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-routing): định tuyến và giới hạn vận hành.
- [AWS — Usage plans và API keys](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-api-usage-plans.html).

Đã đọc body nguồn ghim và các phần tài liệu phục vụ claim ngày 2026-10-15. Không dùng hình nguồn. Chưa thử với người học hoặc phê duyệt phát hành.

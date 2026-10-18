# API gateway: chọn đích, áp chính sách

**Cùng một cửa vào, nhưng yêu cầu có thể đi tới các dịch vụ khác nhau.** Ứng dụng thư viện gọi cổng chung để tìm sách hoặc xem phiếu mượn. Gateway dựa vào quy tắc đã cấu hình để chọn đích và áp chính sách cho lưu lượng.

![Ứng dụng gửi yêu cầu vào API gateway. Quy tắc /books chọn dịch vụ danh mục, /loans chọn dịch vụ mượn trả; hai nhánh là các đích khác nhau, không phải một yêu cầu chạy qua cả hai. Gateway có chính sách được cấu hình; dịch vụ mượn trả vẫn xử lý quyền trên phiếu và nghiệp vụ.](../../diagrams/sd-01-042-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện để chương trình yêu cầu dữ liệu hoặc chức năng; gateway là cổng nhận và chuyển các yêu cầu đó.

## Đọc hình

- **Chọn dịch vụ.** Trong ví dụ, đường dẫn bắt đầu bằng `/books` được chuyển tới danh mục; `/loans` tới mượn trả. Đây là định tuyến theo loại yêu cầu. Chọn một bản sao bên trong cùng dịch vụ là quyết định khác.
- **Áp chính sách chung.** Tùy sản phẩm và cấu hình, gateway có thể kiểm tra thông tin xác thực, hạn chế tần suất, biến đổi dữ liệu hoặc lưu tạm phản hồi. Chức năng có trong danh sách không có nghĩa tự bật, cũng không quy định mọi yêu cầu phải trải qua cùng thứ tự.
- **Giữ đúng ranh giới.** Dịch vụ mượn trả vẫn phải bảo đảm người gọi được đọc phiếu cụ thể và xử lý quy tắc nghiệp vụ. Gateway nhận diện được người gọi chưa đủ kết luận người đó được đọc mọi phiếu.

## Nhìn hình thử trả lời

Nếu dịch vụ mượn trả chậm, gateway có tự sửa dịch vụ đó bằng cách chuyển mọi yêu cầu `/loans` sang danh mục không?

<details>
<summary>Xem đáp án</summary>

Không. Danh mục không thực hiện hợp đồng mượn trả. Đổi đích chỉ đúng khi đích thay thế thực sự cung cấp hành vi tương ứng. Nếu có cấu hình ngắt mạch, gateway có thể tạm chặn lời gọi có khả năng lỗi, nhưng không biến một dịch vụ khác chức năng thành bản thay thế.

</details>

<details>
<summary>Đi sâu: chính sách không phải phép tự sửa lỗi</summary>

Ngắt mạch (circuit breaker) tạm ngừng gọi thao tác đang có khả năng thất bại, rồi cho thử lại có kiểm soát. Nó giúp hạn chế lỗi lan rộng trong lúc hệ thống phục hồi; việc sửa nguyên nhân lỗi là việc khác. Không phải gateway nào cũng có hoặc đã bật cơ chế này.

Gateway có thể áp chính sách lên cả yêu cầu đi vào lẫn phản hồi đi ra. Ví dụ, Azure API Management phân chính sách thành phần trước chuyển tiếp, phía dịch vụ, phản hồi và xử lý lỗi. Đó là mô hình của sản phẩm này, không phải chuỗi mười hai bước bắt buộc cho mọi gateway. Biến đổi định dạng cũng không tự làm hai hợp đồng nghiệp vụ tương thích.

Cổng chung thêm một chặng và có thể thành nút nghẽn hoặc điểm lỗi chung. Cần thiết kế năng lực, dự phòng và quan sát phù hợp; không suy một hộp trong hình là chỉ một máy, hay đặt gateway là hệ thống tự tăng công suất. Nếu dịch vụ vẫn mở đường truy cập ngoài chính sách, cần xử lý cả đường đi vòng đó.

</details>

## Nguồn đối chiếu

- [ByteByteGo — body ghim](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-does-api-gateway-do.md): chủ đề chức năng; không dùng ảnh hoặc coi các bước nguồn là quy trình chung.
- [Microsoft — định tuyến qua cổng](https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-routing): chọn dịch vụ, nút nghẽn và đường truy cập phía sau.
- [Microsoft — chính sách cổng API](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-policies): cấu hình theo yêu cầu, phản hồi và lỗi.
- [Microsoft — ngắt mạch](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker): hạn chế lời gọi có khả năng thất bại, không tự sửa nguyên nhân.
- [Quyền trên từng đối tượng](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/): người gọi, hành động và tài nguyên cụ thể.

Đã đọc body ghim và các mục tài liệu cho claim ngày2026-10-16. Ví dụ và sơ đồ mới; chưa dựng gateway, đo tải, thử sự cố hoặc thử người học.

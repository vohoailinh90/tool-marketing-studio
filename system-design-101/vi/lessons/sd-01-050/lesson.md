# Sáu giao thức API: chọn theo kiểu hội thoại

**REST, Webhook, GraphQL, SOAP, WebSocket và gRPC đều là cách hai chương trình nói chuyện với nhau; khác nhau trước hết ở chỗ ai mở lời và kênh có giữ mở không.**
Bài nguồn chỉ liệt kê sáu giao thức phổ biến năm 2023 và trỏ sang một bài viết dài hơn. Bài này không nhắc lại danh sách mà xếp sáu cái tên vào ba kiểu hội thoại, để người mới biết nên hỏi câu gì trước khi chọn.

![Ba nhóm thẻ xếp dọc. Nhóm hỏi rồi đáp, máy khách mở lời: REST dùng địa chỉ tài nguyên và phương thức HTTP; SOAP gửi thông điệp văn bản có thẻ theo khuôn chặt; GraphQL để máy khách tự chọn trường dữ liệu; gRPC gọi hàm từ xa bằng thông điệp nhị phân trên HTTP/2. Nhóm gọi lại: ứng dụng đăng ký một Webhook, dịch vụ khác gửi tới khi có sự kiện, ứng dụng báo đã nhận. Nhóm kênh mở: trình duyệt bắt tay để nâng cấp kết nối WebSocket, sau đó hai bên gửi tin bất cứ lúc nào. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-01-050-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình yêu cầu chức năng hoặc dữ liệu của chương trình khác.
- **REST** (REpresentational State Transfer) — kiểu thiết kế dịch vụ qua HTTP: mỗi tài nguyên có một địa chỉ riêng và được thao tác bằng các phương thức chuẩn.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để một bên gửi yêu cầu và bên kia gửi trả lời trên web.
- **SOAP** (Simple Object Access Protocol) — tên mở rộng lịch sử của một khung trao đổi thông điệp dạng văn bản có thẻ, với khuôn mẫu và hợp đồng chặt.
- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, cho biết máy khách dùng nó để mô tả dữ liệu muốn lấy.
- **gRPC** (gRPC Remote Procedure Calls) — khung gọi thủ tục từ xa mã nguồn mở: máy khách gọi một hàm chạy trên máy chủ như gọi hàm trong chương trình.

## Đọc hình

**Hỏi rồi đáp.** Bốn giao thức đầu cùng một nhịp: máy khách gửi yêu cầu, máy chủ trả lời, xong. Chúng khác nhau ở hình dạng của yêu cầu:
- REST: địa chỉ chỉ tài nguyên, phương thức `GET`, `POST`... nói việc cần làm.
- SOAP: mọi yêu cầu là một thông điệp văn bản có thẻ, theo khuôn. Bản mô tả dịch vụ, nếu có, được công bố riêng như một hợp đồng; nó không đi kèm từng yêu cầu.
- GraphQL: máy khách gửi một truy vấn nói rõ cần những trường nào, máy chủ trả đúng các trường đó.
- gRPC: hai bên dùng chung định nghĩa hàm và kiểu dữ liệu; thông điệp được mã hóa nhị phân.

**Gọi lại.** Với Webhook, chiều đi đảo ngược: ứng dụng của bạn đăng ký trước một địa chỉ, rồi dịch vụ kia gọi tới địa chỉ đó khi có sự kiện. Bạn không phải hỏi đi hỏi lại "có gì mới chưa".

**Kênh mở.** WebSocket bắt đầu bằng một lần bắt tay, sau đó kết nối được giữ lại và hai bên gửi tin độc lập với nhau. Hợp với chat, bảng giá cập nhật liên tục, trò chơi nhiều người.

## Giới hạn cần nhớ

Ba nhóm này là cách người biên soạn sắp xếp để dễ nhớ, không phải phân loại chuẩn. Ranh giới cũng không tuyệt đối: gRPC có kiểu luồng dữ liệu hai chiều, GraphQL có subscription để nhận cập nhật. Bài nguồn có nói tới lợi ích và thách thức của từng giao thức nhưng chỉ ở bài viết dài mà nó trỏ sang; bài viết đó chưa được mở để đối chiếu, nên các mô tả ở đây là kiến thức chung của người biên soạn.

## Nhìn hình thử trả lời

Cửa hàng của bạn muốn biết ngay khi một đơn thanh toán thành công ở cổng thanh toán, mà không phải cứ vài giây lại hỏi. Nhóm nào trong hình hợp nhất, và bạn phải chuẩn bị gì trước?

<details>
<summary>Xem đáp án</summary>

Nhóm gọi lại: Webhook. Bạn phải có sẵn một địa chỉ mà cổng thanh toán gọi tới được, đăng ký địa chỉ đó với họ, và trả lời "đã nhận" khi có sự kiện tới.
Hỏi rồi đáp vẫn dùng được, nhưng là hỏi định kỳ, đúng việc đề bài muốn tránh.

</details>

<details>
<summary>Xem sâu hơn: câu hỏi nên đặt trước khi chọn</summary>

- Ai cần mở lời? Máy khách hỏi khi cần thì nghĩ tới nhóm hỏi rồi đáp; bên kia cần báo khi có sự kiện thì nghĩ tới Webhook hoặc WebSocket.
- Người gọi là ai? Trình duyệt và đối tác bên ngoài thường dễ dùng REST hoặc GraphQL; các dịch vụ nội bộ cùng một đội có thể dùng gRPC vì chung được định nghĩa hàm.
- Có hệ thống cũ không? Nhiều hệ thống doanh nghiệp cũ đã có hợp đồng SOAP; nối vào chúng thường rẻ hơn thay chúng.

Đây là gợi ý của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-evolving-landscape-of-api-protocols-in-2023.md): danh sách sáu giao thức API phổ biến năm 2023.

Đã đọc nguồn ngày 2026-10-19. Bài viết dài trên blog mà bài nguồn trỏ tới chưa được mở; mô tả từng giao thức là kiến thức chung của người biên soạn.
Bài viết và hình được thiết kế độc lập.

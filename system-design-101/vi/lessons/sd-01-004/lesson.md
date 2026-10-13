# gRPC hoạt động thế nào?

**Dịch vụ đơn hàng cần nhờ dịch vụ thanh toán làm việc.** Nó gọi một phương thức như gọi hàm,
nhưng dữ liệu thực sự phải đi qua mạng. Đó là ý tưởng của RPC — gọi thủ tục từ xa.

![Luồng dọc: khách gửi REST/JSON tới dịch vụ đơn hàng; dịch vụ gọi client stub; message được mã hóa thành bytes và gửi qua HTTP/2; phía gRPC server giải mã rồi gọi hàm thanh toán; response được mã hóa, truyền về, giải mã và trả cho khách. Stub là mã hỗ trợ, không phải dữ liệu được gửi qua mạng.](../../diagrams/sd-01-004-main.svg)

## Từ viết tắt

- **RPC** (Remote Procedure Call) — gọi thủ tục từ xa: chương trình này gọi một hàm chạy trên máy khác như gọi hàm trong cùng chương trình.
- **REST** (REpresentational State Transfer) — kiểu thiết kế dịch vụ qua HTTP: mỗi tài nguyên có một địa chỉ riêng, thường trao đổi dữ liệu dạng JSON.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản biểu diễn dữ liệu bằng các cặp tên và giá trị, dễ đọc với cả người và máy.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản; HTTP/2 là phiên bản gửi nhiều yêu cầu song song trên một kết nối, và gRPC dùng nó để chuyên chở message.

## Đọc hình

**Chuẩn bị trước:** file `.proto` mô tả phương thức và kiểu message. Công cụ sinh mã tạo
client stub và mã phía server để hai phía dùng cùng định nghĩa.

**1–2. Nhận yêu cầu, gọi stub.** Trong ví dụ, khách gửi REST/JSON tới dịch vụ đơn hàng.
Dịch vụ này đóng vai gRPC client, gọi `Pay(request)` qua stub — mã hỗ trợ gọi dịch vụ từ xa.

**3–5. Gửi message.** Theo cách dùng mặc định, request được mã hóa bằng Protocol Buffers
thành bytes, truyền qua HTTP/2. Phía server giải mã message và gọi phương thức tương ứng.
**Message được mã hóa, không phải bản thân stub.**

**6–8. Trả kết quả.** Dịch vụ thanh toán tạo response. Nó được mã hóa, gửi về và giải mã
ở phía client; dịch vụ đơn hàng trả kết quả cho khách.

REST/JSON là cửa vào của ví dụ, không phải điều kiện bắt buộc của mọi ứng dụng gRPC.

## Giới hạn cần nhớ

Gọi từ xa có lỗi mạng và thời gian chờ, khác một hàm chỉ chạy trong bộ nhớ.
Nên đặt **deadline** — thời điểm tối đa còn chấp nhận chờ. Timeout không chứng minh
rằng thao tác phía server chưa xảy ra, nên không gửi lại yêu cầu thanh toán một cách mù quáng.

## Nhìn hình trả lời

Trong bước 3, thành phần nào được mã hóa để gửi qua mạng: client stub hay request message?

<details>
<summary>Xem đáp án</summary>

Request message. Stub là mã hỗ trợ ở phía client; nó không được gửi sang máy chủ để thực thi.

</details>

<details>
<summary>Xem sâu hơn: unary và streaming</summary>

Hình mô tả **unary RPC**: một request, một response. gRPC còn hỗ trợ server streaming,
client streaming và hai chiều; không phải mọi lời gọi đều có đúng một message mỗi phía.

Deadline hết hạn khiến client dừng chờ. Công việc đã làm ở server không tự được hoàn tác.
Ứng dụng cần quyết định cách kiểm tra kết quả hoặc chống xử lý trùng khi gửi lại.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-grpc-work.md): tình huống đơn hàng → thanh toán.
- [gRPC — Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/): stub, message, unary/streaming và vòng đời RPC.
- [gRPC — Introduction](https://grpc.io/docs/what-is-grpc/introduction/): `.proto`, sinh mã và Protocol Buffers mặc định.
- [gRPC — Protocol over HTTP/2](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md): truyền request/response qua HTTP/2.
- [gRPC — Deadlines](https://grpc.io/docs/guides/deadlines/): giới hạn thời gian chờ.

Đã đọc nguồn ngày 2026-10-12. Bài viết và hình được thiết kế độc lập.
Không giữ tuyên bố “nhanh hơn JSON 5 lần” từ bài nguồn vì chưa có phép đo và điều kiện so sánh.

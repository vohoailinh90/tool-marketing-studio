# Nhập môn API Gateway

**API gateway là một máy chủ đứng ở cửa trước của các API: nhận yêu cầu, áp chính sách bảo mật và giới hạn tốc độ, chuyển tới dịch vụ phía sau rồi trả kết quả về cho client.** Bài này đi qua sáu chức năng mà nguồn liệt kê, rồi nói thêm cái giá phải trả.

![Năm khung dọc: điểm vào chung, API gateway nằm giữa client và các dịch vụ phía sau, nhận yêu cầu và trả kết quả; định tuyến và cân bằng tải, đưa yêu cầu tới đúng dịch vụ và rải đều giữa các bản chạy; bảo mật và giới hạn tốc độ, gồm xác thực, phân quyền, mã hóa và giới hạn số yêu cầu của một client trong một khoảng thời gian; gom API và cache, gộp nhiều lời gọi phía sau thành một và lưu tạm phản hồi; cái giá phải trả là thêm một chặng và nếu chỉ chạy một bản thì thành điểm đơn lỗi.](../../diagrams/sd-01-022-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách để một chương trình gọi chức năng hoặc lấy dữ liệu của chương trình khác theo quy ước đã định.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu (request) và máy chủ gửi trả lời (response).
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa giữ kín dữ liệu giữa client và máy chủ.
- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; bài chỉ dẫn tới tài liệu của họ.
- **RFC** (Request for Comments) — "đề nghị bình luận": loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; nhiều RFC là tiêu chuẩn.

## Đọc hình

1. **Điểm vào chung.** Gateway ở giữa client và máy chủ phía sau, quản lý và tối ưu lưu lượng API. Theo suy luận của bài, client chỉ cần biết địa chỉ của gateway.
2. **Định tuyến và cân bằng tải.** Định tuyến yêu cầu (request routing) đưa mỗi yêu cầu tới đúng dịch vụ phía sau. Cân bằng tải (load balancing) phân bố yêu cầu giữa nhiều máy chủ; nếu tổng nhu cầu vượt năng lực phục vụ thì các máy vẫn có thể quá tải.
3. **Bảo mật, giới hạn tốc độ.** Gateway áp các biện pháp như xác thực (biết người gọi là ai), phân quyền (người đó được làm gì) và mã hóa dữ liệu. Giới hạn tốc độ (rate limiting) và làm chậm (throttling) kiểm soát số yêu cầu một client được gửi trong một khoảng thời gian.
4. **Gom API và cache.** Gom API (API composition) kết hợp nhiều lời gọi tới các dịch vụ phía sau thành một yêu cầu phía trước để tối ưu hiệu năng. Cache lưu phản hồi tạm thời để khỏi xử lý lặp lại.
5. **Cái giá.** Khung này do bài bổ sung, không có trong nguồn: gateway thêm một chặng mạng, và nếu chỉ chạy một bản thì nó thành điểm đơn lỗi cho mọi API phía sau.

## Giới hạn cần nhớ

Nguồn chỉ liệt kê chức năng, không nói sản phẩm nào có chức năng nào và không có số liệu. Những điểm sau là suy luận của bài. Gateway thường kết thúc TLS (Transport Layer Security, giao thức mã hóa đường truyền) ở phía client; đoạn từ gateway tới dịch vụ có được mã hóa hay không là cấu hình riêng. Khi vượt giới hạn tốc độ, gateway thường trả mã HTTP 429 (Too Many Requests, quá nhiều yêu cầu). Chỉ nên cache phản hồi dùng chung được; phản hồi theo từng người dùng cần khóa cache đúng hoặc không cache. Gom API dễ kéo logic nghiệp vụ vào gateway; khi đó mỗi thay đổi nhỏ của dịch vụ lại đòi sửa gateway. Và gateway không thay việc kiểm quyền theo từng tài nguyên ở dịch vụ, vì dịch vụ biết ngữ cảnh nghiệp vụ còn gateway thường không.

## Nhìn hình thử trả lời

Bạn có 12 dịch vụ nhỏ, và mỗi dịch vụ tự làm xác thực và giới hạn tốc độ. Đặt một API gateway phía trước có lợi gì, và cần chuẩn bị cho rủi ro nào?

<details>
<summary>Xem đáp án</summary>

Lợi: việc chung được làm một lần, chính sách đồng nhất, dịch vụ nhẹ hơn và client chỉ cần một địa chỉ. Rủi ro: thêm một chặng và độ trễ; gateway thành điểm đơn lỗi nên cần chạy nhiều bản; gateway có thể phình ra thành nơi chứa logic; và nếu dịch vụ vẫn truy cập được trực tiếp từ bên ngoài thì kẻ tấn công đi vòng qua gateway, nên dịch vụ chỉ nên nhận lưu lượng từ gateway.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Giới hạn tốc độ và làm chậm:** nhiều sản phẩm dùng hai từ gần như đồng nghĩa. Cách hiểu thường gặp: giới hạn tốc độ đặt mức tối đa số yêu cầu trong một khoảng thời gian (ví dụ theo khóa API), còn làm chậm là giảm hoặc từ chối khi tải vượt mức. Thuật toán hay dùng là token bucket (xô token) và cửa sổ trượt. Mức này thường là mục tiêu theo nỗ lực tối đa chứ không phải trần tuyệt đối: tài liệu của AWS API Gateway nói rõ giới hạn của họ có tính chất đó, nên đừng coi chúng là bảo đảm một dịch vụ phía sau không bao giờ quá tải.
- **Cân bằng tải ở gateway:** gateway có thể tự chọn một trong các bản chạy của dịch vụ, hoặc chuyển yêu cầu tới bộ cân bằng tải phía sau để bộ đó chọn bản chạy. Một bộ cân bằng tải phía trước gateway lại chia tải giữa các bản sao của gateway; cách xếp tùy sản phẩm.
- **Gom API:** là mẫu "Gateway Aggregation" trong tài liệu kiến trúc của Microsoft, hợp khi client gọi nhiều dịch vụ cho một màn hình.
- **Cache:** quy tắc cache của HTTP nằm ở RFC 9111; phản hồi riêng của từng người dùng thường dùng Cache-Control: private hoặc không lưu.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/api-gateway-101.md): định nghĩa và sáu chức năng của API gateway.
- [RFC 6585 — mã 429](https://www.rfc-editor.org/rfc/rfc6585) và [RFC 9111 — HTTP caching](https://www.rfc-editor.org/rfc/rfc9111).
- [Microsoft — mẫu Gateway Aggregation](https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-aggregation) và [mẫu Gateway Routing](https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-routing).
- [AWS — API Gateway, giới hạn tốc độ](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html).

Đã đọc body nguồn ByteByteGo ghim và đối chiếu các claim được liệt kê trong metadata ngày 2026-10-15. Phạm vi và giới hạn evidence nằm trong metadata; các đánh đổi và giả định của bài được ghi riêng. Bài viết và hình được thiết kế độc lập; chưa thử với người học.

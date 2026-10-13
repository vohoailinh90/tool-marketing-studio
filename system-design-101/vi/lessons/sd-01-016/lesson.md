# Reverse Proxy, API Gateway và Load Balancer

**Ba tên hay bị dùng lẫn, vì phần mềm thật thường làm cả ba.** Cách phân biệt là hỏi: mỗi cái giải quyết câu hỏi gì?

![Bốn khung dọc: reverse proxy đứng trước máy chủ gốc, che máy gốc và lo TLS, cache; API gateway là cửa vào chung của các API với định tuyến, xác thực và giới hạn tốc độ; load balancer chia tải trong một dịch vụ và loại máy lỗi khỏi nhóm; chúng hay xếp chồng, client tới gateway rồi tới load balancer, gateway chọn dịch vụ còn load balancer chọn máy trong dịch vụ. Một phần mềm có thể làm cả ba.](../../diagrams/sd-01-016-main.svg)

## Đọc hình

- **Reverse proxy:** một máy trung gian đứng *phía máy chủ*. Client nói chuyện với proxy như với chính máy chủ, proxy chuyển yêu cầu tới máy gốc. Việc thường làm: che địa chỉ máy gốc, kết thúc TLS, cache, nén. (Khác *forward proxy*, đứng phía client.)
- **API gateway:** cửa vào chung cho nhiều dịch vụ. Nó hiểu API: định tuyến theo đường dẫn (`/orders` tới dịch vụ đơn hàng), xác thực, giới hạn tốc độ, đổi định dạng. Có thể coi nó là reverse proxy có thêm quản lý API.
- **Load balancer:** chia request giữa nhiều bản sao của *cùng một* dịch vụ, kiểm tra sức khỏe và loại máy lỗi khỏi nhóm.
- **Xếp chồng:** gateway chọn *dịch vụ*, load balancer chọn *máy trong dịch vụ*.

## Giới hạn cần nhớ

Ranh giới không cứng: NGINX, Envoy, HAProxy hay dịch vụ cloud có thể đóng nhiều vai trong một cấu hình. "Che máy gốc" không phải là bảo mật đầy đủ: reverse proxy giảm bề mặt bị tấn công nhưng không thay xác thực hay tường lửa. Thêm một lớp trung gian cũng thêm độ trễ và thêm một chỗ có thể lỗi.

## Nhìn hình thử trả lời

Bạn cần chuyển `/orders` tới dịch vụ đơn hàng, `/users` tới dịch vụ người dùng, cùng kiểm tra khóa API và giới hạn 100 request mỗi phút cho mỗi khách. Cần vai nào trước, và LB đứng ở đâu?

<details>
<summary>Xem đáp án</summary>

API gateway: nó lo định tuyến theo đường dẫn, xác thực và giới hạn tốc độ. Sau gateway, nếu mỗi dịch vụ có nhiều bản sao thì load balancer chia tải giữa các bản sao đó.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Trung gian trong HTTP:** chuẩn HTTP gọi chung các máy đứng giữa client và máy gốc là trung gian (proxy, gateway, tunnel); các tên trong bài là cách dùng thông dụng.
- **CDN:** mạng phân phối nội dung cũng hoạt động như reverse proxy có cache, đặt gần người dùng.
- **Sidecar và service mesh:** với giao tiếp giữa các dịch vụ, một proxy nhỏ đi kèm từng dịch vụ có thể làm các việc tương tự ở phía trong.
- **Đừng nhầm:** "gateway" trong mạng cục bộ thường chỉ router mặc định, khác với API gateway.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/reverse-proxy-vs-api-gateway-vs-load-balancer.md).
- [NGINX — Reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/), [Envoy](https://www.envoyproxy.io/docs/envoy/latest/) và [HAProxy](https://docs.haproxy.org/).
- [AWS — API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html) và [Azure — API gateway pattern](https://learn.microsoft.com/en-us/azure/architecture/microservices/design/gateway).
- [RFC 9110 — Trung gian (§3.7)](https://www.rfc-editor.org/rfc/rfc9110).

Đã đọc bản nguồn ByteByteGo ngày 2026-10-13; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

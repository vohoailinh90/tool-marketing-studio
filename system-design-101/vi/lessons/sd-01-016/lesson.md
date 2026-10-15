# Reverse Proxy, API Gateway và Load Balancer

**Ba cái tên cùng đứng trước máy chủ của bạn. Chúng khác nhau ở đâu?** Khác ở việc chính mỗi vai đảm nhận, và ba vai thường chồng lên nhau trong cùng một phần mềm.

![Bốn khung dọc: reverse proxy thay mặt máy gốc, che máy gốc và có thể kết thúc TLS, nén hoặc cache; load balancer chia request cho nhiều bản sao của cùng một dịch vụ và loại máy lỗi khỏi nhóm; API gateway là một cửa vào cho nhiều dịch vụ, định tuyến theo đường dẫn, xác thực và giới hạn tần suất; ba tên này là vai trò chứ không phải ba hộp riêng, một phần mềm như NGINX có thể đảm nhiệm cả ba.](../../diagrams/sd-01-016-main.svg)

## Đọc hình

**1. Reverse proxy.** Nhận request thay cho máy gốc rồi chuyển tiếp vào trong; client chỉ làm việc với proxy. Nhờ vậy proxy có chỗ để kết thúc TLS, nén, lưu cache và che địa chỉ máy gốc.

**2. Load balancer.** Chia request cho nhiều bản sao của cùng một dịch vụ và loại máy lỗi khỏi nhóm. Câu hỏi nó trả lời là "request này đi tới bản sao nào?".

**3. API gateway.** Một cửa vào cho nhiều dịch vụ khác nhau: định tuyến theo đường dẫn (`/orders` tới dịch vụ đơn hàng, `/users` tới dịch vụ người dùng) và làm những việc chung của API như xác thực, giới hạn tần suất, ghi log. Câu hỏi của nó là "request này thuộc dịch vụ nào, và có được vào không?".

**4. Vai trò, không phải hộp.** Chuẩn HTTP gọi gateway là reverse proxy, và coi chia tải là một công dụng của nó. "API gateway" là tên của một nhóm sản phẩm thêm các tính năng riêng cho API. Một phần mềm như NGINX có thể cấu hình để đóng cả ba vai.

## Giới hạn cần nhớ

Che máy gốc không phải là bảo vệ: máy gốc vẫn cần xác thực, vá lỗi và chặn truy cập trực tiếp (ví dụ chỉ nhận kết nối từ proxy), vì địa chỉ có thể lộ qua cấu hình hay tiêu đề phản hồi. Mỗi tầng xếp thêm là thêm một chặng mạng, thêm một chỗ có thể lỗi, và một cổng quá nhiều logic nghiệp vụ sẽ thành điểm nghẽn của cả hệ thống. Xếp tầng nào trước tầng nào tùy kiến trúc, không có thứ tự duy nhất.

## Nhìn hình thử trả lời

Bạn có ba bản sao của dịch vụ đơn hàng, và muốn `/orders` đi tới dịch vụ đơn hàng còn `/users` đi tới dịch vụ người dùng. Việc nào thuộc vai nào?

<details>
<summary>Xem đáp án</summary>

Chọn một trong ba bản sao của dịch vụ đơn hàng là việc của load balancer. Phân biệt `/orders` với `/users` để tới đúng dịch vụ là việc của API gateway. Cả hai có thể cùng nằm trong một phần mềm, vì đó là hai vai chứ không phải hai hộp.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Chuẩn HTTP:** RFC 9110 định nghĩa gateway (còn gọi reverse proxy) là trung gian đóng vai máy chủ gốc với client, dịch yêu cầu rồi chuyển vào máy khác; công dụng gồm bọc dịch vụ cũ, tăng tốc nhờ cache và chia tải.
- **NGINX làm ví dụ:** `proxy_pass` chuyển tiếp request, nhóm `upstream` chia tải (mặc định vòng tròn, có trọng số), `proxy_cache` lưu cache, `limit_req` giới hạn tần suất và `auth_request` ủy việc xác thực cho dịch vụ khác. Đây là khả năng cấu hình được, không có nghĩa nó thay một cổng API đầy đủ.
- **Đám mây:** các nhà cung cấp thường bán load balancer và API gateway thành hai dịch vụ riêng; phạm vi tính năng khác nhau theo từng nhà.
- **Tầng chia tải:** chia theo kết nối khác chia theo request HTTP (xem bài về các tình huống dùng bộ cân bằng tải).

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/reverse-proxy-vs-api-gateway-vs-load-balancer.md).
- [RFC 9110 §3.7](https://www.rfc-editor.org/rfc/rfc9110.html#name-intermediaries): trung gian, gateway (reverse proxy) và chia tải.
- [NGINX — ngx_http_proxy_module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html), [ngx_http_upstream_module](https://nginx.org/en/docs/http/ngx_http_upstream_module.html), [ngx_http_limit_req_module](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html) và [ngx_http_auth_request_module](https://nginx.org/en/docs/http/ngx_http_auth_request_module.html).

Đã đọc nguồn ngày 2026-10-15. Định nghĩa gateway trong RFC 9110 và các chỉ thị NGINX được đối chiếu với bản RFC và mã nguồn tài liệu NGINX; cấu hình thực tế chưa được chạy thử. Bài viết và hình được thiết kế độc lập.

# Nginx làm reverse proxy cho một API: năm chỗ hay sai

Cách học Nginx nhanh nhất là đặt nó trước một API và xem chỗ nào hay sai: đường dẫn, địa chỉ client, timeout, kết nối tới backend và cách đổi cấu hình.

![Năm chỗ hay sai khi dùng Nginx làm reverse proxy cho một API: dấu gạch chéo cuối của proxy_pass đổi đường dẫn, backend không thấy địa chỉ client thật và header của client có thể bị giả mạo, lỗi 502 khi không nối được hoặc backend không trả phản hồi hợp lệ và lỗi 504 khi quá hạn ở bước nối, gửi hay đọc từ backend (proxy_read_timeout chỉ đo khoảng giữa hai lần đọc), mở lại kết nối tới backend liên tục (trước Nginx 1.29.7 phải bật keepalive trong upstream, HTTP/1.1 và bỏ header Connection, từ 1.29.7 chúng là mặc định), và đổi cấu hình mà không kiểm tra.](../../diagrams/sd-13-024-main.svg)

**Đọc hình:** mỗi thẻ là một chỗ hay sai, không theo thứ tự; cấu hình mẫu nằm ở phần sâu.

## Nhìn hình thử trả lời

Với `location /api/ { proxy_pass http://backend/; }`, request tới `/api/users` đến backend với đường dẫn nào?

<details>
<summary>Xem đáp án</summary>

`/users`. Vì `proxy_pass` có phần URI (dấu `/` cuối), phần khớp `/api/` được thay bằng `/`. Nếu viết `proxy_pass http://backend;` không có URI thì backend nhận nguyên `/api/users`. Quy tắc này dành cho location tiền tố thông thường: với location regex hoặc location đặt tên, `proxy_pass` phải viết không có URI, và `rewrite ... break` hay biến trong `proxy_pass` làm đổi kết quả.

</details>

## Giới hạn cần nhớ

Cấu hình mẫu cần chỉnh theo ứng dụng của bạn, nhất là timeout và số kết nối giữ sẵn. Mặc định của kết nối tới backend khác nhau giữa các bản Nginx (xem ý keepalive ở phần sâu), nên hãy đối chiếu tài liệu của bản bạn dùng. Đây không phải hướng dẫn đầy đủ về bảo mật hay hiệu năng; luôn chạy `nginx -t` trước khi reload và thử trên môi trường phụ trước.

<details>
<summary>Xem sâu hơn</summary>

```nginx
upstream backend {
    server 127.0.0.1:8080;
    keepalive 32;    # trước 1.29.7 phải ghi rõ; từ 1.29.7 đã bật mặc định
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://backend/;
        # từ 1.29.7 hai dòng dưới đã là mặc định; ghi rõ để chạy đúng cả trên bản cũ
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        # Nginx là cổng công khai: ghi đè, không nối vào header client gửi
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;   # giữa hai lần đọc từ backend, không phải cả phản hồi
    }
}
```

```bash
nginx -t && nginx -s reload
```

- **Host:** mặc định Nginx gửi `$proxy_host` cho backend; muốn giữ tên miền client dùng thì đặt `Host $host`.
- **X-Forwarded-For:** nếu Nginx là cổng công khai, ghi đè bằng `$remote_addr` để client không chèn địa chỉ giả vào đầu chuỗi. `$proxy_add_x_forwarded_for` giữ nguyên header client gửi rồi nối thêm địa chỉ vào cuối; chỉ dùng khi phía trước còn proxy tin cậy, và khi đó backend phải chỉ phân tích phần chuỗi sau các proxy tin cậy, hoặc dùng `ngx_http_realip_module` với `set_real_ip_from`.
- **502 và 504:** 502 xảy ra khi Nginx không nối được tới backend hoặc backend đóng kết nối trước khi trả phản hồi hợp lệ. 504 xảy ra khi quá một trong ba thời hạn với backend: `proxy_connect_timeout` (nối, thường không vượt quá 75 giây), `proxy_send_timeout` (gửi request, tính giữa hai lần ghi) và `proxy_read_timeout` (nhận phản hồi, tính giữa hai lần đọc); cả ba mặc định 60 giây. Vì `proxy_read_timeout` chỉ đo khoảng lặng giữa hai lần đọc, một phản hồi dài hơn 60 giây vẫn không bị cắt nếu dữ liệu đến thường xuyên hơn.
- **keepalive:** giữ sẵn một số kết nối rảnh tới backend để dùng lại. Trước Nginx 1.29.7 nó chỉ có tác dụng khi đồng thời đặt `keepalive` trong `upstream`, `proxy_http_version 1.1` và xóa header `Connection`. Từ 1.29.7, giữ kết nối tới upstream và HTTP/1.1 đã là mặc định, nên các dòng đó chỉ còn để ghi rõ ý định và để cấu hình chạy đúng cả trên bản cũ; số kết nối rảnh mặc định xem trong tài liệu của bản bạn dùng.
- **Reload:** `nginx -s reload` nạp cấu hình mới; worker cũ xử lý nốt kết nối hiện có rồi thoát.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/why-is-nginx-so-popular.md).
- Nginx: [ngx_http_proxy_module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html), [ngx_http_upstream_module](https://nginx.org/en/docs/http/ngx_http_upstream_module.html), [tham số dòng lệnh](https://nginx.org/en/docs/switches.html), [hướng dẫn cơ bản](https://nginx.org/en/docs/beginners_guide.html), [giữ kết nối tới upstream là mặc định từ 1.29.7](https://blog.nginx.org/blog/keep-alive-to-upstreams-is-now-default-in-nginx-1-29-7).

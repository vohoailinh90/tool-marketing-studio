# Nginx làm reverse proxy cho một API: năm chỗ hay sai

Cách học Nginx nhanh nhất là đặt nó trước một API và xem chỗ nào hay sai: đường dẫn, địa chỉ client, timeout, kết nối tới backend và cách đổi cấu hình.

![Năm chỗ hay sai khi dùng Nginx làm reverse proxy cho một API: dấu gạch chéo cuối của proxy_pass đổi đường dẫn, backend không thấy địa chỉ client thật và header của client có thể bị giả mạo, lỗi 502 và 504, mở lại kết nối tới backend liên tục, và đổi cấu hình mà không kiểm tra.](../../diagrams/sd-13-024-main.svg)

**Đọc hình:** mỗi thẻ là một chỗ hay sai, không theo thứ tự; cấu hình mẫu nằm ở phần sâu.

## Nhìn hình thử trả lời

Với `location /api/ { proxy_pass http://backend/; }`, request tới `/api/users` đến backend với đường dẫn nào?

<details>
<summary>Xem đáp án</summary>

`/users`. Vì `proxy_pass` có phần URI (dấu `/` cuối), phần khớp `/api/` được thay bằng `/`. Nếu viết `proxy_pass http://backend;` không có URI thì backend nhận nguyên `/api/users`.

</details>

## Giới hạn cần nhớ

Cấu hình mẫu cần chỉnh theo ứng dụng của bạn, nhất là timeout và số kết nối giữ sẵn. Đây không phải hướng dẫn đầy đủ về bảo mật hay hiệu năng; luôn chạy `nginx -t` trước khi reload và thử trên môi trường phụ trước.

<details>
<summary>Xem sâu hơn</summary>

```nginx
upstream backend {
    server 127.0.0.1:8080;
    keepalive 32;
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        # Nginx là cổng công khai: ghi đè, không nối vào header client gửi
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_read_timeout 30s;
    }
}
```

```bash
nginx -t && nginx -s reload
```

- **Host:** mặc định Nginx gửi `$proxy_host` cho backend; muốn giữ tên miền client dùng thì đặt `Host $host`.
- **X-Forwarded-For:** nếu Nginx là cổng công khai, ghi đè bằng `$remote_addr` để client không chèn địa chỉ giả vào đầu chuỗi. `$proxy_add_x_forwarded_for` giữ nguyên header client gửi rồi nối thêm địa chỉ vào cuối; chỉ dùng khi phía trước còn proxy tin cậy, và khi đó backend phải chỉ phân tích phần chuỗi sau các proxy tin cậy, hoặc dùng `ngx_http_realip_module` với `set_real_ip_from`.
- **keepalive:** giữ sẵn một số kết nối rảnh tới backend; cần `proxy_http_version 1.1` và xóa header `Connection` thì mới có tác dụng.
- **Reload:** `nginx -s reload` nạp cấu hình mới; worker cũ xử lý nốt kết nối hiện có rồi thoát.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/why-is-nginx-so-popular.md).
- Nginx: [ngx_http_proxy_module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html), [ngx_http_upstream_module](https://nginx.org/en/docs/http/ngx_http_upstream_module.html), [tham số dòng lệnh](https://nginx.org/en/docs/switches.html), [hướng dẫn cơ bản](https://nginx.org/en/docs/beginners_guide.html).

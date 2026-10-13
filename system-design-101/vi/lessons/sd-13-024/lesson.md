# Vì sao Nginx nhanh và phổ biến

Cách dễ nhớ Nginx là qua bốn tình huống vận hành, mỗi tình huống cho thấy một lựa chọn thiết kế của nó.

![Bốn tình huống và lý do thiết kế: nhiều kết nối chờ chậm nhờ vòng lặp sự kiện, đổi cấu hình không rớt kết nối nhờ master và worker, máy chủ phía sau quá tải nhờ reverse proxy chia tải và cache, HTTPS nhờ kết thúc TLS ở rìa.](../../diagrams/sd-13-024-main.svg)

**Đọc hình:** tình huống thứ hai và thứ nhất đến từ kiến trúc master–worker; hai tình huống sau là vai trò Nginx đảm nhận.

## Nhìn hình thử trả lời

Chạy `nginx -s reload` khi đang có kết nối: kết nối đang xử lý có bị cắt không?

<details>
<summary>Xem đáp án</summary>

Không cắt đột ngột. Master kiểm tra cấu hình mới, mở worker mới và yêu cầu worker cũ ngừng nhận kết nối mới rồi thoát sau khi xử lý xong kết nối hiện có.

</details>

## Giới hạn cần nhớ

Vòng lặp sự kiện rất hợp với nhiều kết nối ít việc; thao tác nặng CPU hoặc chặn lâu trong một worker làm chậm các kết nối khác trên worker đó. Số worker thường đặt theo số lõi CPU.

<details>
<summary>Xem sâu hơn</summary>

- **Master** đọc cấu hình và quản lý worker; **worker** xử lý kết nối.
- **Reverse proxy:** nhận request từ client, chuyển tới máy chủ phía sau, trả kết quả về; có thể chia tải giữa nhiều máy chủ.
- **Cache nội dung:** lưu phản hồi để giảm tải cho máy chủ phía sau.
- **Kết thúc TLS:** Nginx giải mã HTTPS rồi chuyển tiếp nội bộ, nên ứng dụng không phải lo chứng chỉ.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/why-is-nginx-so-popular.md).
- Nginx: [hướng dẫn cơ bản](https://nginx.org/en/docs/beginners_guide.html), [kiến trúc, bài "Inside NGINX"](https://blog.nginx.org/blog/inside-nginx-how-we-designed-for-performance-scale).

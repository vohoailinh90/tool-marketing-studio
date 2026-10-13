# Gõ google.com vào trình duyệt thì chuyện gì xảy ra?

**Một câu hỏi phỏng vấn quen thuộc, và cách trả lời tốt là kể đúng thứ tự.** Từ lúc nhấn Enter tới lúc trang hiện ra
có sáu việc nối nhau: kiểm tra cache, tra DNS, mở kết nối, gửi yêu cầu HTTP, nhận phản hồi, dựng trang.

![Sáu thẻ nối nhau từ trên xuống. 1 Nhập địa chỉ: gõ rồi nhấn Enter. 2 Kiểm tra cache: đã có gì dùng lại được chưa. 3 Tra DNS: tên miền ra địa chỉ IP. 4 Mở kết nối: bắt tay TCP, HTTPS thêm TLS. 5 Yêu cầu HTTP: gửi yêu cầu, nhận HTML. 6 Dựng trang: DOM, CSSOM, layout, paint. Ghi chú: đây là đường chính, không phải đường duy nhất.](../../diagrams/sd-05-002-main.svg)

## Đọc hình

**1–2. Nhập địa chỉ và kiểm tra cache.** Trước khi ra mạng, trình duyệt xem đã có gì dùng lại được chưa:
một phản hồi đã lưu, hoặc địa chỉ IP đã tra gần đây.

**3. Tra DNS.** DNS là hệ thống đặt tên phân cấp và phi tập trung, đổi tên miền thành địa chỉ IP.
Nếu chưa ai trong chuỗi cache biết, yêu cầu đi qua các máy chủ DNS (gốc, tên miền cấp cao, máy chủ có thẩm quyền).

**4. Mở kết nối.** Với HTTP qua TCP, hai bên bắt tay ba bước SYN, SYN-ACK, ACK. Với địa chỉ HTTPS, thêm một bước
bắt tay TLS để mã hóa đường truyền.

**5. Yêu cầu HTTP.** Trình duyệt gửi yêu cầu; máy chủ trả HTML. Trang thường kéo thêm CSS, JavaScript, ảnh bằng các yêu cầu khác.

**6. Dựng trang.** Phân tích HTML và CSS, tính layout, vẽ ra màn hình.

## Giới hạn cần nhớ

Đây là đường chính chứ không phải đường duy nhất. Có cache thì bỏ được DNS hoặc cả yêu cầu mạng; kết nối đã mở có thể được dùng lại;
HTTP/3 chạy trên QUIC thay vì bắt tay TCP. Khi trả lời phỏng vấn, hãy nói rõ bạn đang kể trường hợp cơ bản.

## Nhìn hình trả lời

Trình duyệt vừa tra địa chỉ IP của tên miền đó cách đây ít phút và còn lưu. Bước nào trong hình có thể được bỏ qua?

<details>
<summary>Xem đáp án</summary>

Bước 3, tra DNS: địa chỉ IP đã có sẵn trong cache. Các bước từ mở kết nối trở đi vẫn cần, trừ khi có phản hồi đã lưu dùng lại được
hoặc một kết nối cũ còn mở.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn chỉ kể bắt tay TCP của HTTP/1.1 và không nhắc TLS. Hình này thêm bước TLS cho địa chỉ HTTPS, vì
với HTTPS đường truyền được mã hóa bằng TLS; HSTS còn khiến trình duyệt tự nâng các lần truy cập HTTP sau đó lên HTTPS.

Chi tiết dựng trang nằm ở bước 6 và được giải thích riêng trong bài về cách trình duyệt dựng trang.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-happens-when-you-type-google.md): tám bước.
- [MDN — DNS](https://developer.mozilla.org/en-US/docs/Glossary/DNS), [TCP handshake](https://developer.mozilla.org/en-US/docs/Glossary/TCP_handshake), [TLS](https://developer.mozilla.org/en-US/docs/Glossary/TLS): các thuật ngữ.
- [MDN — HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching) và [Strict-Transport-Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security): cache dùng lại phản hồi; HSTS.

Đã đọc nguồn ngày 2026-10-13. Các trang MDN được đọc từ bản clone của kho mdn/content (developer.mozilla.org không mở được trong môi trường biên soạn).
Tên các loại máy chủ DNS và việc cache DNS ở nhiều tầng lấy từ bài nguồn, chưa đối chiếu riêng. Bài viết và hình được thiết kế độc lập.

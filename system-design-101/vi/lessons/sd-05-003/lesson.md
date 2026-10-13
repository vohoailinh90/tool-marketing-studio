# Một URL biến thành yêu cầu HTTP thế nào?

**Không phải phần nào của URL cũng được gửi tới máy chủ.** Mỗi phần có một việc riêng: chọn giao thức, tìm máy chủ,
chỉ ra tài nguyên, hoặc ở lại trình duyệt.

![Các thẻ xếp dọc cho URL ví dụ https://example.com/phone?color=black#specs. Scheme https chọn giao thức kết nối. Host example.com được tra DNS và vào header Host. Path cộng query /phone?color=black nằm trong dòng yêu cầu. Fragment #specs không bao giờ gửi tới server. Yêu cầu gửi đi gồm dòng GET /phone?color=black HTTP/1.1 và header Host example.com. Phản hồi gồm dòng HTTP/1.1 200 OK, các header, một dòng trống và nội dung.](../../diagrams/sd-05-003-main.svg)

## Đọc hình

**scheme.** `https` cho trình duyệt biết cần dùng giao thức nào để kết nối.

**host.** `example.com` được tra DNS ra địa chỉ IP, rồi đi vào header `Host` của yêu cầu.

**path và query.** `/phone?color=black` là cái máy chủ cần để biết bạn muốn tài nguyên nào. Hai phần này nằm trong dòng đầu của yêu cầu.

**fragment.** `#specs` không bao giờ được gửi tới máy chủ. Nó chỉ dành cho trình duyệt, ví dụ để cuộn tới một đoạn của trang.

**Thông điệp.** Yêu cầu HTTP/1.1 gồm dòng đầu (`GET /phone?color=black HTTP/1.1`), các header như `Host`, rồi một dòng trống.
Phản hồi bắt đầu bằng dòng trạng thái (`HTTP/1.1 200 OK`), tiếp theo là header, một dòng trống và nội dung.

## Giới hạn cần nhớ

Vì fragment không rời trình duyệt, máy chủ không thể phân biệt `#specs` với `#reviews`. Đừng dùng fragment để truyền thông tin
mà máy chủ cần: hãy đưa nó vào path hoặc query.

## Nhìn hình trả lời

Với URL `https://example.com/phone?color=black#specs`, phần nào xuất hiện trong dòng đầu của yêu cầu HTTP/1.1, và phần nào không bao giờ xuất hiện?

<details>
<summary>Xem đáp án</summary>

`/phone?color=black` (path và query) nằm trong dòng đầu. `#specs` không bao giờ xuất hiện. Cả `https://` lẫn tên miền cũng không nằm trong dòng đầu:
tên miền đi vào header `Host`.

</details>

<details>
<summary>Xem sâu hơn: thử trên máy chủ cục bộ</summary>

Khi gọi `curl --http1.1 "http://localhost:<cổng>/products/phone?color=black#specs"` tới một máy chủ ghi lại byte nhận được, dòng đầu là
`GET /products/phone?color=black HTTP/1.1` và có header `Host: localhost:<cổng>`; không có dấu hiệu nào của `#specs`.

Bài nguồn liệt kê URL thành bốn phần gồm cả “resource” và dùng đường dẫn `product/electric` khác với `/phone` trong yêu cầu mẫu.
Hình này dùng một ví dụ nhất quán và gộp tài nguyên vào path.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-happens-when-you-type-a-url-into-your-browser.md): các phần của URL, yêu cầu và phản hồi mẫu.
- [MDN — What is a URL?](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_URL): các phần của URL; fragment không bao giờ gửi tới máy chủ.
- [MDN — HTTP messages](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages): dòng yêu cầu, dòng trạng thái, header, dòng trống, nội dung.

Đã đọc nguồn ngày 2026-10-13. Các trang MDN được đọc từ bản clone của kho mdn/content (developer.mozilla.org không mở được trong môi trường biên soạn);
yêu cầu mẫu được bắt lại từ một máy chủ cục bộ với curl 8.5.0. Bài viết và hình được thiết kế độc lập.

# Trình duyệt dựng trang web thế nào?

HTML mô tả nội dung, CSS mô tả cách trình bày. Trình duyệt biến chúng thành hình bạn thấy.

![HTML tạo DOM, CSS tạo CSSOM; hai đầu vào đi tới style/render tree, layout, paint, raster và composite, rồi hiển thị Xin chào.](../../diagrams/sd-01-008-main.svg)

**Đọc hình:** DOM là cây nội dung; CSSOM là mô hình quy tắc CSS. Layout tính vị trí và kích thước; paint ghi việc cần vẽ. Raster tạo pixel, composite ghép các phần đã vẽ thành khung hình.

## Nhìn hình thử trả lời

Bước nào quyết định hộp “Xin chào” rộng bao nhiêu và nằm ở đâu: Layout hay Composite?

<details>
<summary>Xem đáp án</summary>

Layout. Composite ghép các phần đã vẽ theo thứ tự phù hợp.

</details>

## Giới hạn cần nhớ

Đây là luồng khái niệm, không phải mọi lần cập nhật đều chạy đủ các bước. Đổi màu chữ có thể bỏ qua layout; đổi chiều rộng thường cần tính lại bố cục.

<details>
<summary>Xem sâu hơn</summary>

HTML có thể được phân tích khi dữ liệu còn đang tải. JavaScript có thể sửa DOM hoặc style, khiến trình duyệt cập nhật hình tiếp; không cần JavaScript để trang tĩnh hiện ra.

`display: none` không tạo hộp trong render tree. `visibility: hidden` vẫn giữ chỗ trong bố cục dù không vẽ nội dung đó. “Không nhìn thấy” không đồng nghĩa “không cần layout”.

Cách chia paint/raster/composite, luồng xử lý và dùng GPU tùy engine. Không hiểu hình thành một quy tắc rằng toàn bộ trang luôn được gửi nguyên khối sang GPU sau mỗi thay đổi.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-the-browser-render-a-web-page.md).
- [MDN: Parsing và Render](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work).
- [web.dev: pixel pipeline, raster và các bước có thể bỏ qua](https://web.dev/articles/rendering-performance).

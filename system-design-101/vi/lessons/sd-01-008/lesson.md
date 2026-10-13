# Trình duyệt dựng trang web thế nào?

**Máy chủ gửi về chữ, trình duyệt phải biến chúng thành hình.** Việc đó đi qua một chuỗi bước: hiểu HTML, hiểu CSS, tính chỗ đặt từng phần tử, rồi vẽ.

![Sáu khung dọc: HTML được phân tích thành cây DOM, script thường làm parser dừng; CSS thành cây CSSOM chứa các quy tắc kiểu và chặn việc dựng hình; DOM và CSSOM được khớp và giải cascade cho từng phần tử để thành cây hiển thị, bỏ phần tử display none còn visibility hidden vẫn chiếm chỗ; layout tính vị trí và kích thước; paint vẽ nội dung ra từng lớp; composite ghép các lớp để GPU hiển thị. Đổi DOM hoặc CSS có thể chạy lại từ layout, paint hoặc composite.](../../diagrams/sd-01-008-main.svg)

## Đọc hình

**1. DOM.** Trình duyệt đọc HTML dần dần và dựng *cây DOM*: mỗi thẻ là một nút. Khi gặp `<script>` thường (không `async`/`defer`), nó thường phải dừng đọc để chạy script trước.

**2. CSSOM.** CSS được phân tích thành *cây CSSOM*: cấu trúc chứa các quy tắc kiểu của trang, kể cả những quy tắc rốt cuộc không được áp dụng. Việc hiện trang thường phải chờ CSS, nên CSS "chặn dựng hình".

**3. Cây hiển thị.** Trình duyệt khớp các quy tắc của CSSOM với từng phần tử DOM và giải cascade cho từng phần tử để ra kiểu tính toán, rồi chỉ giữ những gì có hộp để vẽ. Phần tử `display: none` bị bỏ; `visibility: hidden` thì vẫn chiếm chỗ nhưng không thấy.

**4. Layout.** Tính vị trí và kích thước từng hộp.

**5. Paint.** Vẽ nội dung (chữ, màu, ảnh) ra từng lớp.

**6. Composite.** Ghép các lớp theo thứ tự; việc này thường do GPU làm.

## Giới hạn cần nhớ

Sáu bước không chạy đúng một lần theo hàng thẳng. Trình duyệt dựng dần khi dữ liệu còn đang về, và chạy lại một phần khi trang thay đổi: đổi kích thước hay vị trí thường kéo theo cả layout, paint, composite; đổi màu có thể bỏ qua layout. Tên gọi và chi tiết (như "render tree") khác nhau giữa các engine.

## Nhìn hình thử trả lời

Muốn một ô trượt mượt, bạn đổi `left` mỗi khung hình hay dùng `transform`? Vì sao?

<details>
<summary>Xem đáp án</summary>

Thường nên dùng `transform`. Đổi `left` làm đổi vị trí hộp nên có thể buộc chạy lại layout (có khi cho cả trang) rồi paint; `transform` thường chỉ cần ghép lại lớp ở bước composite, nhất là khi phần tử đã được trình duyệt đưa lên lớp riêng. Mức chênh lệch tùy trình duyệt và trang.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Script và CSS:** script thường làm dừng parser; `async` hoặc `defer` giúp parser không phải chờ. CSS chặn dựng hình. Script cổ điển (không `async`, không `defer`) còn phải chờ các stylesheet đang tải trước nó rồi mới chạy; script `async` hoặc được chèn bằng mã có thể chạy ngay khi tải xong, không chờ như vậy.
- **Cây hiển thị khác DOM:** `::before` và `::after` có hộp để vẽ nhưng không có nút DOM; `<head>` mặc định bị ẩn.
- **Dựng lại:** đọc kích thước (ví dụ `offsetHeight`) ngay sau khi ghi có thể buộc trình duyệt tính layout sớm; làm lặp lại nhiều lần gây chậm.
- **Chỉ là mô hình:** engine thật còn có nhiều bước tối ưu và tách luồng.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-the-browser-render-a-web-page.md).
- [MDN — Critical rendering path](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Critical_rendering_path).
- [HTML Standard — Parsing](https://html.spec.whatwg.org/multipage/parsing.html) và [Rendering](https://html.spec.whatwg.org/multipage/rendering.html), [CSS Display Module](https://www.w3.org/TR/css-display-3/) và [CSS 2 — visibility](https://www.w3.org/TR/CSS22/visufx.html#visibility).
- [web.dev — Rendering performance](https://web.dev/articles/rendering-performance).

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

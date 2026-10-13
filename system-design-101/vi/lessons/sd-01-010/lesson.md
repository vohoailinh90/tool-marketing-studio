# CSS là gì?

**CSS tách việc “tài liệu nói gì” khỏi việc “nó trông thế nào”.** HTML mô tả cấu trúc, CSS mô tả cách trình bày.
Khi hai quy tắc xung đột, cascade quyết định quy tắc nào thắng.

![Bốn thẻ xếp dọc kèm một thẻ ví dụ. Thẻ đầu: một quy tắc gồm selector và khai báo, ví dụ p mở ngoặc nhọn color blue đóng ngoặc nhọn. Dải tiêu đề: khi hai quy tắc xung đột. Bước 1, nguồn gốc và important, mức cao hơn thắng trước. Bước 2, độ cụ thể, selector cụ thể hơn thắng dù viết trước. Bước 3, thứ tự xuất hiện, cùng mức thì quy tắc viết sau thắng. Ví dụ: lớp note màu đỏ thắng p màu xanh dù p viết sau.](../../diagrams/sd-01-010-main.svg)

## Đọc hình

**Một quy tắc.** Gồm **selector** (chọn phần tử) và các **khai báo** (thuộc tính: giá trị).
`p { color: blue; }` làm chữ của mọi đoạn văn thành xanh. Muốn đổi giao diện, bạn sửa CSS mà không đụng tới HTML.

**Cascade.** Khi nhiều quy tắc cùng đặt một thuộc tính cho một phần tử, trình duyệt xét lần lượt:

1. **Nguồn gốc và `!important`:** mức cao hơn thắng trước.
2. **Độ cụ thể:** selector cụ thể hơn thắng, dù được viết trước.
3. **Thứ tự xuất hiện:** cùng mức thì quy tắc viết sau thắng.

**Ngoài màu sắc.** CSS còn lo bố cục (Flexbox, Grid), chuyển động (`transition`, `@keyframes`)
và thích ứng kích thước màn hình (media query).

## Giới hạn cần nhớ

“Viết sau thì thắng” chỉ đúng khi hai quy tắc cùng nguồn và cùng độ cụ thể. Với `.note { color: red; }` viết trước
và `p { color: blue; }` viết sau, đoạn `<p class="note">` vẫn đỏ. Thấy một quy tắc không có tác dụng thì đừng vội
thêm `!important`: hãy kiểm tra độ cụ thể và thứ tự trước.

## Nhìn hình trả lời

Trang có `.note { color: red; }` rồi `p { color: blue; }`. Đoạn `<p class="note">` có màu gì, và vì sao?

<details>
<summary>Xem đáp án</summary>

Màu đỏ. Selector lớp `.note` cụ thể hơn selector phần tử `p`, nên thắng ở bước 2,
trước khi thứ tự xuất hiện được xét. Khi thử trên Chromium 141, `.note` cho `rgb(255, 0, 0)`.

</details>

<details>
<summary>Xem sâu hơn: điều hình đã lược</summary>

Thuật toán cascade đầy đủ còn có cascade layer và độ gần theo phạm vi (`@scope`) giữa các bước; hình giữ ba bước
để nhớ được. Với hai quy tắc cùng độ cụ thể và cùng nguồn, Chromium 141 áp quy tắc viết sau.

Bài nguồn gọi CSS là “markup language”. CSS thường được mô tả là ngôn ngữ style sheet: nó không đánh dấu cấu trúc,
việc đó thuộc về HTML.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-css-cascading-style-sheets.md): các khía cạnh của CSS.
- [MDN — Cascade: giới thiệu](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Introduction): thuật toán cascade, nguồn gốc, thứ tự xuất hiện.
- [MDN — Specificity](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity): so sánh độ cụ thể, `!important`, kiểu nội tuyến.
- [MDN — Xử lý xung đột trong CSS](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Handling_conflicts): cascade, độ cụ thể, thứ tự nguồn, mức quan trọng.
- Phép thử trên Chromium 141 (Playwright): `.note` thắng `p`; hai quy tắc ngang nhau thì quy tắc sau thắng.

Đã đọc nguồn ngày 2026-10-13. Các bài MDN được đọc từ bản clone của kho mdn/content; trang developer.mozilla.org
không mở được trong môi trường biên soạn. Bài viết và hình được thiết kế độc lập.

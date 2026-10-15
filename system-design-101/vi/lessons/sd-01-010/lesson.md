# CSS là gì?

**CSS tách việc “tài liệu nói gì” khỏi việc “nó trông thế nào”.** HTML mô tả cấu trúc, CSS mô tả cách trình bày.
Khi hai quy tắc xung đột, cascade quyết định quy tắc nào thắng.

![Bốn thẻ xếp dọc kèm một thẻ ví dụ. Thẻ đầu: một quy tắc gồm selector và khai báo, ví dụ p mở ngoặc nhọn color blue đóng ngoặc nhọn. Dải tiêu đề: khi hai quy tắc xung đột. Bước 1, nguồn gốc và important, mức cao hơn thắng trước. Bước 2, độ cụ thể, selector cụ thể hơn thắng dù viết trước. Bước 3, thứ tự xuất hiện, khi các bước trước hòa thì quy tắc viết sau thắng. Hình lược bớt các bước ngữ cảnh, thuộc tính style, layer và phạm vi @scope. Ví dụ: lớp note màu đỏ thắng p màu xanh dù p viết sau.](../../diagrams/sd-01-010-main.svg)

## Từ viết tắt

- **CSS** (Cascading Style Sheets) — bảng kiểu xếp tầng: các luật mô tả màu sắc, cỡ chữ và cách bố trí của trang.
- **HTML** (HyperText Markup Language) — ngôn ngữ đánh dấu siêu văn bản: văn bản dùng thẻ để mô tả cấu trúc của một trang web.
- **DOM** (Document Object Model) — mô hình đối tượng tài liệu: cây các phần tử của trang mà trình duyệt dựng từ HTML; JavaScript có thể sửa cây này.

## Đọc hình

**Một quy tắc.** Gồm **selector** (chọn phần tử) và các **khai báo** (thuộc tính: giá trị).
`p { color: blue; }` chọn các đoạn văn và khai báo màu xanh; màu cuối cùng còn phụ thuộc cascade. Muốn đổi giao diện, bạn sửa CSS mà không đụng tới HTML.

**Cascade.** Khi nhiều quy tắc cùng đặt một thuộc tính cho một phần tử, hình dưới lược ba bước cho khai báo thông thường, không có animation/transition đang hoạt động, và bỏ qua các bước xét ngữ cảnh, thuộc tính `style`, layer và `@scope` (xem mục “Xem sâu hơn”):

1. **Nguồn gốc và `!important`:** mức cao hơn thắng trước.
2. **Độ cụ thể:** selector cụ thể hơn thắng, dù được viết trước.
3. **Thứ tự xuất hiện:** khi các bước trước hòa, quy tắc viết sau thắng.

**Ngoài màu sắc.** Cùng cơ chế quy tắc đó còn dùng để bố trí các khối trên trang, tạo chuyển động
và điều chỉnh giao diện theo kích thước màn hình.

## Giới hạn cần nhớ

Trong ví dụ hai quy tắc trong stylesheet của tác giả, cùng cây DOM (không Shadow DOM), không animation/transition,
không cascade layer và không `@scope`, thứ tự xuất hiện chỉ phân xử khi độ cụ thể hòa. Với `.note { color: red; }` viết trước
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

Hình giữ ba bước để nhớ được; thứ tự đầy đủ theo CSS Cascade dài hơn. Từ ưu tiên cao xuống thấp: (1) nguồn gốc và mức quan trọng, gồm cả animation và transition; (2) ngữ cảnh đóng gói, ví dụ Shadow DOM: với khai báo thông thường ngữ cảnh ngoài thắng, với `!important` thì ngữ cảnh trong thắng; (3) khai báo gắn thẳng vào phần tử, như thuộc tính `style`, thắng khai báo đi qua quy tắc có selector khi cùng mức quan trọng; (4) cascade layer; (5) độ cụ thể; (6) độ gần theo phạm vi (`@scope`); (7) thứ tự xuất hiện. Ba bước trong hình là mục 1, 5 và 7; các mục 2, 3, 4 và 6 chỉ phân định khi hai khai báo khác nhau ở chính mục đó. Với hai quy tắc không layer, không `@scope`, cùng độ cụ thể và cùng nguồn, Chromium 141 áp quy tắc viết sau trong ví dụ không có animation/transition đang hoạt động.

Animation và transition cũng có nguồn riêng trong bước nguồn gốc/mức quan trọng. Giá trị đang được CSS animation tạo ra thắng các khai báo thông thường nhưng thua khai báo `!important`. Giá trị đang được transition tạo ra có ưu tiên cao hơn cả `!important`. Ví dụ đỏ/xanh trong bài không bật hai cơ chế này.

Bài nguồn gọi CSS là “markup language”. CSS thường được mô tả là ngôn ngữ style sheet: nó không đánh dấu cấu trúc,
việc đó thuộc về HTML.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-css-cascading-style-sheets.md): các khía cạnh của CSS.
- [MDN — Cascade: giới thiệu](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Introduction): thuật toán cascade, nguồn gốc, thứ tự xuất hiện.
- [MDN — Specificity](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity): so sánh độ cụ thể, `!important`, kiểu nội tuyến.
- [MDN — Xử lý xung đột trong CSS](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Handling_conflicts): cascade, độ cụ thể, thứ tự nguồn, mức quan trọng.
- [MDN — CSS](https://developer.mozilla.org/en-US/docs/Web/CSS): ngôn ngữ style sheet, bố cục và chuyển động.
- [CSS Cascade §6.1](https://www.w3.org/TR/css-cascade-5/#cascade-sort): nguồn animation/transition và thứ tự ưu tiên.
- [CSS Cascade Level 6, mục Cascade Sorting Order — bản nguồn tại commit cố định](https://github.com/w3c/csswg-drafts/blob/1c249b342ee7a0dfe0fcf7f7dc75272b1e794d52/css-cascade-6/Overview.bs): thứ tự đầy đủ gồm nguồn gốc, ngữ cảnh, thuộc tính style, layer, độ cụ thể, độ gần phạm vi, thứ tự xuất hiện.
- Phép thử trên Chromium 141 (Playwright), với hai quy tắc stylesheet của tác giả, cùng ngữ cảnh, không layer, không `@scope`, không animation/transition: `.note` thắng `p`; hai quy tắc ngang độ cụ thể thì quy tắc sau thắng.

Đã đọc nguồn ghim và trực tiếp đối chiếu MDN ngày 2026-10-13. Evidence đọc từ clone/phép đo Chromium của phiên trước được giữ riêng trong metadata; lượt này đối chiếu bổ sung các trang chính thức về cascade, specificity và CSS. Chưa thử với người học.

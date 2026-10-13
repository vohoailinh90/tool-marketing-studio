# CSS là gì?

**HTML nói trang có gì, CSS nói trang trông thế nào.** Tách hai việc giúp đổi giao diện mà không đụng vào nội dung: đổi bảng màu cả site chỉ cần sửa tệp CSS.

![Ba khung dọc: một quy tắc gồm bộ chọn p, thuộc tính color và giá trị blue; cascade giải quyết xung đột giữa quy tắc p xanh dương, .note đỏ và #intro xanh lá cho phần tử p có id intro và class note, kết quả là xanh lá vì id đặc hiệu hơn, ngang nhau thì quy tắc sau thắng; bố cục có Flexbox một chiều, Grid hai chiều, và @media đổi kiểu theo kích thước màn hình. Hiệu ứng dùng transition và @keyframes.](../../diagrams/sd-01-010-main.svg)

## Đọc hình

**Một quy tắc.** CSS gồm các quy tắc dạng *bộ chọn* + *khai báo*. `p { color: blue; }`: `p` chọn mọi đoạn văn, `color` là thuộc tính, `blue` là giá trị.

**Cascade — khi quy tắc xung đột.** Chữ "C" trong CSS là *cascading*. Nhiều quy tắc có thể cùng áp lên một phần tử, trình duyệt chọn theo thứ tự ưu tiên: nguồn và độ quan trọng (`!important`), rồi *độ đặc hiệu* của bộ chọn (id mạnh hơn class, class mạnh hơn tên thẻ), rồi thứ tự xuất hiện (cùng độ đặc hiệu thì quy tắc đứng sau thắng). Với `<p id="intro" class="note">` và ba quy tắc trong hình, kết quả là xanh lá.

**Bố cục và responsive.** Flexbox sắp xếp theo một chiều (hàng hoặc cột); Grid là lưới hai chiều. `@media` áp kiểu khác nhau theo kích thước màn hình.

## Giới hạn cần nhớ

Độ đặc hiệu không phải là "đếm quy tắc nào dài hơn": khi cùng nguồn, cùng lớp và cùng mức quan trọng, id thắng class bất kể thứ tự, nên khi "sửa mãi không ăn" nên kiểm tra quy tắc nào đang thắng thay vì thêm `!important`. CSS cũng không phải ngôn ngữ lập trình; nó mô tả kiểu, còn logic nằm ở nơi khác.

## Nhìn hình thử trả lời

Hai quy tắc `.note { color: red; }` rồi `.note { color: green; }` cùng áp lên một đoạn có class `note`. Màu nào, vì sao?

<details>
<summary>Xem đáp án</summary>

Xanh lá. Hai quy tắc có cùng độ đặc hiệu nên quy tắc đứng sau thắng.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **CSS là ngôn ngữ bảng kiểu (style sheet language),** không phải ngôn ngữ đánh dấu như HTML.
- **Thứ tự đầy đủ của cascade** còn có nguồn (kiểu của trình duyệt, của tác giả, của người dùng), `!important` và các lớp `@layer`.
- **Độ đặc hiệu:** kiểu viết trực tiếp trên phần tử mạnh hơn id; id mạnh hơn class, thuộc tính và pseudo-class; những cái này mạnh hơn tên thẻ.
- **Hiệu ứng:** `transition` chuyển mượt giữa hai trạng thái; `@keyframes` mô tả chuỗi hoạt họa; không cần JavaScript cho các hiệu ứng đơn giản.
- **Responsive:** thường kết hợp `@media`, đơn vị tương đối và Flexbox hoặc Grid.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-css-cascading-style-sheets.md).
- [MDN — CSS là gì](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/What_is_CSS) và [Cascade, specificity và inheritance](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Handling_conflicts).
- [CSS Cascading and Inheritance](https://www.w3.org/TR/css-cascade-5/), [Selectors](https://www.w3.org/TR/selectors-4/), [Flexbox](https://www.w3.org/TR/css-flexbox-1/), [Grid](https://www.w3.org/TR/css-grid-1/) và [Media Queries](https://www.w3.org/TR/mediaqueries-4/).
- [CSS Transitions](https://www.w3.org/TR/css-transitions-1/) và [CSS Animations](https://www.w3.org/TR/css-animations-1/).

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

# CSS là gì?

**CSS (Cascading Style Sheets) là ngôn ngữ mô tả cách một tài liệu HTML được trình bày: màu sắc, phông chữ, khoảng cách, bố cục và chuyển động.** HTML nói phần tử là gì, CSS nói nó trông thế nào; nhờ tách hai việc này, đổi giao diện không cần viết lại nội dung.

![Sáu thẻ dọc. Thẻ một, tách nội dung và kiểu: HTML nói nội dung là gì, CSS nói nó trông thế nào. Thẻ hai, một luật CSS p { color: blue; }: p là bộ chọn, color là thuộc tính, blue là giá trị. Thẻ ba, xếp tầng: khi hai luật xung đột, trình duyệt chọn luật thắng theo thứ tự ưu tiên. Thẻ bốn, bố cục: Flexbox sắp theo một chiều, Grid theo hai chiều. Thẻ năm, chuyển động: transition và @keyframes chạy không cần JavaScript. Thẻ sáu, đáp ứng: media query đổi kiểu theo cỡ màn hình. Chú thích: độ đặc hiệu của bộ chọn được xét trước thứ tự viết.](../../diagrams/sd-01-010-main.svg)

## Đọc hình

**1. Tách nội dung và kiểu.** HTML mô tả cấu trúc và ý nghĩa: đâu là tiêu đề, đoạn văn, danh sách. Ngày trước, cách trình bày được nhúng thẳng vào HTML bằng các thẻ như `<font>`; nay chuẩn HTML xếp chúng vào loại lỗi thời. CSS tách phần trình bày ra khỏi HTML; vì thế nó là ngôn ngữ biểu định kiểu (style sheet language), không phải ngôn ngữ đánh dấu: đánh dấu cấu trúc là việc của HTML. Có ba cách gắn CSS vào trang: một file riêng qua `<link rel="stylesheet" href="...">`, một khối `<style>` trong trang, hoặc thuộc tính `style` của một phần tử. File riêng được nhiều trang dùng chung, nên đổi bảng màu ở một nơi thì mọi trang dùng file đó đổi theo.

**2. Một luật CSS.** Mỗi luật gồm một **bộ chọn (selector)** để chọn phần tử cần tạo kiểu, và một khối khai báo trong ngoặc nhọn; mỗi khai báo là một cặp **thuộc tính: giá trị**. Ví dụ `p { color: blue; }` làm chữ của mọi đoạn văn `<p>` có màu xanh. Bộ chọn có thể chọn theo tên thẻ (`p`), theo lớp (`.note` chọn mọi phần tử có `class="note"`) hoặc theo mã (`#intro` chọn phần tử có `id="intro"`).

**3. Xếp tầng (cascade).** Một phần tử thường bị nhiều luật cùng chạm tới và chúng có thể xung đột: kiểu mặc định của trình duyệt, file của trang, thuộc tính `style`. Chuẩn quy định cách chọn khai báo thắng bằng cách so lần lượt từng tiêu chí; chỉ khi các tiêu chí trước bằng nhau mới xét tiêu chí sau. Hai tiêu chí hay gặp nhất hằng ngày là **độ đặc hiệu** của bộ chọn (bộ chọn mã mạnh hơn bộ chọn lớp, bộ chọn lớp mạnh hơn bộ chọn tên thẻ) và **thứ tự viết** (cùng độ đặc hiệu thì luật viết sau thắng). Thứ tự đầy đủ nằm ở phần xem sâu hơn.

**4. Bố cục.** CSS không chỉ chỉnh màu hay phông chữ mà còn dàn trang. **Flexbox** sắp các phần tử theo một chiều (một hàng hoặc một cột) và chia chỗ trống giữa chúng; **Grid** chia vùng thành hàng và cột để đặt phần tử theo hai chiều. Hai mô-đun này làm được những việc mà trước đây người ta phải lách bằng bảng HTML hay `float`. Bảng HTML vẫn đúng chỗ cho dữ liệu dạng bảng; chỉ không nên dùng nó để dàn trang.

**5. Chuyển động.** Thuộc tính `transition` làm một giá trị đổi dần từ cũ sang mới thay vì nhảy tức thì, ví dụ nút đổi màu mượt khi rê chuột vào. Quy tắc `@keyframes` cùng thuộc tính `animation` mô tả một chuỗi trạng thái chạy theo thời gian. Cả hai chạy mà không cần JavaScript, dù JavaScript vẫn có thể bật hoặc tắt chúng, chẳng hạn bằng cách thêm hoặc bỏ một lớp.

**6. Đáp ứng (responsive).** Cùng một HTML có thể hiện khác nhau trên điện thoại và máy tính nhờ CSS: dùng đơn vị tương đối (phần trăm, `rem`), cho Flexbox hoặc Grid xuống hàng khi hết chỗ (`flex-wrap: wrap` ở Flexbox, `auto-fit` hoặc `auto-fill` ở Grid), và dùng **media query** như `@media (min-width: 600px) { ... }` để thêm luật khi màn hình đủ rộng. Trên điện thoại, trang cần thẻ `<meta name="viewport" content="width=device-width, initial-scale=1">` thì trình duyệt mới dàn trang theo bề rộng thật của màn hình thay vì một bề rộng giả lớn hơn.

**Đọc hình:** mũi tên không vẽ vì sáu thẻ là sáu mảng của CSS, không phải một dây chuyền; riêng xếp tầng (thẻ ba) là chỗ quyết định luật nào có hiệu lực khi có xung đột.

## Giới hạn cần nhớ

CSS mô tả kết quả mong muốn, không phải chương trình chạy từng bước; trình duyệt tự quyết định cách đạt được nó. **Khác biệt giữa trình duyệt:** tính năng mới được hỗ trợ không đều, nên trước khi dựa vào một tính năng hãy kiểm tra bảng tương thích (MDN, Can I use). **Xung đột khó đoán:** khi một luật không có tác dụng, nguyên nhân thường là luật khác thắng ở bước xếp tầng; `!important` ép thắng được nhưng làm các luật sau càng khó đè lên, nên chỉ là lựa chọn cuối. **Chi phí:** trình duyệt thường chờ các stylesheet chặn dựng hình tải xong mới vẽ lần đầu, và một số hiệu ứng, như đổi kích thước liên tục, có thể buộc tính lại bố cục nhiều lần (xem bài về cách trình duyệt dựng trang). **Không phải bảo mật:** ẩn nội dung bằng `display: none` chỉ ẩn nó khỏi trang hiển thị (thường cả khỏi trình đọc màn hình); nội dung vẫn nằm trong HTML đã tải về.

## Nhìn hình trả lời

Trang có hai luật theo thứ tự: `.note { color: red; }` rồi `p { color: blue; }`. Đoạn `<p class="note">` hiện màu gì? Nếu cả hai luật đều dùng bộ chọn `.note` thì sao?

<details>
<summary>Xem đáp án</summary>

Màu đỏ: bộ chọn lớp `.note` có độ đặc hiệu cao hơn bộ chọn tên thẻ `p`, nên thắng dù được viết trước; tiêu chí thứ tự viết chỉ được xét khi các tiêu chí trước đó bằng nhau. Nếu cả hai luật cùng dùng bộ chọn `.note` thì độ đặc hiệu bằng nhau, luật viết sau thắng và đoạn văn có màu xanh.

</details>

<details>
<summary>Xem sâu hơn: xếp tầng đầy đủ, độ đặc hiệu, kế thừa, biến CSS</summary>

- **Thứ tự xếp tầng đầy đủ:** chuẩn so lần lượt: nguồn gốc và `!important` (kiểu của trình duyệt, của người dùng, của tác giả trang; khai báo `!important` đảo thứ bậc các nguồn), ngữ cảnh (cây shadow, hiếm gặp ở trang thường), kiểu gắn trực tiếp bằng thuộc tính `style`, lớp xếp tầng `@layer`, độ đặc hiệu, và cuối cùng là thứ tự xuất hiện.
- **Độ đặc hiệu tính thế nào:** đếm theo ba nhóm: số bộ chọn mã, số bộ chọn lớp, thuộc tính hoặc lớp giả, số bộ chọn tên thẻ hoặc phần tử giả. So nhóm đầu trước, hòa mới so nhóm sau. Vì vậy `#a p` (1, 0, 1) thắng `.x .y .z` (0, 3, 0): nhóm đầu so trước, 1 lớn hơn 0.
- **Kế thừa:** một số thuộc tính, như `color` và `font-family`, được phần tử con thừa hưởng từ phần tử cha nếu không đặt riêng; số khác, như `margin` và `border`, thì không.
- **Biến CSS:** thuộc tính tùy biến như `--brand: #0a5;` được dùng bằng `var(--brand)`, nên đổi màu thương hiệu ở một chỗ là mọi luật dùng biến đó đổi theo.
- **Flexbox hay Grid:** thường dùng Flexbox cho một dãy (thanh menu, hàng nút) và Grid khi bố cục có cả hàng lẫn cột (khung trang, lưới thẻ); hai thứ dùng chung được, ví dụ Grid cho khung và Flexbox bên trong từng ô.
- **Chuyển động và hiệu năng:** đổi `transform` hoặc `opacity` thường rẻ hơn đổi `width` hay `height` vì không buộc tính lại bố cục; đây là quy tắc ngón tay cái, tùy engine. Người dùng có thể đặt “giảm chuyển động” trong hệ điều hành, và CSS đọc được lựa chọn đó bằng `@media (prefers-reduced-motion: reduce)`; khi đó nên tắt hoặc giảm hiệu ứng.
- **Không có một “CSS3” duy nhất:** sau CSS 2.1, chuẩn được chia thành các mô-đun (bộ chọn, Flexbox, Grid, Transitions, Animations…) phát triển độc lập, nên “CSS3” chỉ là cách gọi chung; tính năng nào dùng được tùy mô-đun và trình duyệt.
- **Media query và container query:** media query hỏi về cỡ khung nhìn hay thiết bị; container query hỏi về cỡ của phần tử chứa, hợp với thành phần được dùng lại ở nhiều chỗ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-css-cascading-style-sheets.md): tách nội dung và kiểu, luật CSS, xếp tầng, bố cục Flexbox và Grid, hoạt ảnh và thiết kế đáp ứng.
- [W3C — CSS](https://www.w3.org/Style/CSS/): mô tả CSS là ngôn ngữ cho việc trình bày tài liệu có cấu trúc.
- [W3C — CSS Snapshot](https://www.w3.org/TR/CSS/): danh sách các mô-đun CSS hiện hành.
- [CSS Syntax](https://www.w3.org/TR/css-syntax-3/): luật, bộ chọn, khai báo.
- [Selectors Level 4](https://www.w3.org/TR/selectors-4/): các loại bộ chọn và cách tính độ đặc hiệu.
- [CSS Cascading and Inheritance](https://www.w3.org/TR/css-cascade-5/): thứ tự xếp tầng, lớp, kế thừa.
- [CSS Flexible Box Layout](https://www.w3.org/TR/css-flexbox-1/): Flexbox.
- [CSS Grid Layout](https://www.w3.org/TR/css-grid-1/): Grid.
- [CSS Transitions](https://www.w3.org/TR/css-transitions-1/): transition.
- [CSS Animations](https://www.w3.org/TR/css-animations-1/): @keyframes và animation.
- [Media Queries Level 5](https://www.w3.org/TR/mediaqueries-5/): media query và prefers-reduced-motion.
- [MDN — thẻ meta viewport](https://developer.mozilla.org/en-US/docs/Web/HTML/Viewport_meta_tag): vì sao trang cho điện thoại cần viewport.
- [HTML Standard — tính năng lỗi thời](https://html.spec.whatwg.org/multipage/obsolete.html): font và các thẻ trình bày cũ.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-01-010.json).

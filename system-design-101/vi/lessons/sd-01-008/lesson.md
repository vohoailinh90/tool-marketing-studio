# Trình duyệt dựng trang web thế nào?

**Từ HTML tới điểm ảnh trên màn hình là một chuỗi bước.** Hiểu chuỗi này giúp bạn biết vì sao một dòng CSS
hay một thẻ script có thể làm trang hiện chậm.

![Sáu thẻ xếp dọc. Bước 1, HTML được phân tích thành cây DOM. Bước 2, CSS được phân tích thành cây CSSOM. Bước 3, hai cây được gộp thành render tree: bỏ head và phần tử display none, giữ phần tử visibility hidden. Bước 4, layout tính kích thước và vị trí. Bước 5, paint vẽ ra điểm ảnh. Bước 6, đôi khi ghép lớp bằng GPU. Ghi chú: đổi kích thước hay vị trí thì layout tính lại, gọi là reflow.](../../diagrams/sd-01-008-main.svg)

## Đọc hình

**1–2. DOM và CSSOM.** Trình duyệt phân tích HTML thành cây DOM (cấu trúc tài liệu) và phân tích CSS
thành cây CSSOM (các luật kiểu dáng).

**3. Render tree.** Gộp DOM với CSSOM và chỉ giữ các nút sẽ được hiển thị. `<head>` và phần tử `display: none`
bị bỏ. Phần tử `visibility: hidden` vẫn có mặt vì nó còn chiếm chỗ.

**4. Layout.** Tính kích thước và vị trí của từng nút trong render tree.

**5. Paint.** Biến kết quả đó thành điểm ảnh.

**6. Ghép lớp.** Đôi khi một phần nội dung được đưa lên lớp riêng và ghép bằng GPU,
nhờ vậy luồng chính được nhẹ bớt.

## Giới hạn cần nhớ

Các bước này không phải một dây chuyền cứng. Chờ tải CSS không chặn việc phân tích HTML, nhưng chặn việc chạy JavaScript,
vì script có thể hỏi về kiểu dáng. Một script đồng bộ cũng dừng phân tích HTML cho tới khi nó được xử lý xong.
Sau lần dựng đầu, đổi kích thước hay vị trí một phần tử buộc tính lại layout, gọi là reflow.

## Nhìn hình trả lời

Hai phần tử, một có `display: none`, một có `visibility: hidden`. Phần tử nào nằm trong render tree, và vì sao?

<details>
<summary>Xem đáp án</summary>

Phần tử `visibility: hidden`: nó không nhìn thấy nhưng vẫn chiếm chỗ trong layout.
Phần tử `display: none` không được đưa vào render tree.

</details>

<details>
<summary>Xem sâu hơn: thử trong trình duyệt</summary>

Khi đo trên Chromium 141, một `div` cao 40 px có `visibility: hidden` vẫn cho chiều cao 40 px,
còn `div` tương tự với `display: none` cho chiều cao 0.

Bài nguồn gộp phần cuối thành một bước “hiển thị”, nơi trình duyệt gửi điểm ảnh cho GPU. Hình này tách paint
khỏi ghép lớp, vì tài liệu của MDN mô tả ghép lớp chỉ xảy ra trong một số trường hợp.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-the-browser-render-a-web-page.md): các bước dựng trang.
- [MDN — How browsers work](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work): render tree, `display: none` và `visibility: hidden`, layout, reflow, ghép lớp, CSS chặn JavaScript.
- [MDN — Critical rendering path](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Critical_rendering_path): các yêu cầu chặn phân tích HTML.

Đã đọc nguồn ngày 2026-10-13. Trang developer.mozilla.org không mở được trong môi trường biên soạn;
hai bài MDN được đọc từ bản clone của kho mdn/content. Bài viết và hình được thiết kế độc lập.

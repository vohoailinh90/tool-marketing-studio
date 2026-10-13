# Trình duyệt dựng trang web thế nào?

**Trình duyệt nhận về chữ (HTML và CSS) và phải biến nó thành hình trên màn hình.** Các bước đi theo một thứ tự khá cố định; hiểu thứ tự đó giúp bạn biết vì sao một đoạn CSS hay script có thể làm trang hiện chậm.

![Sáu thẻ dọc: nhận HTML và dựng cây DOM; tải CSS và dựng cây CSSOM; ghép hai cây thành cây dựng hình chỉ gồm phần tử có tạo hộp cùng kiểu dáng; bố cục tính vị trí và kích thước; vẽ ghi lại các lệnh vẽ như màu nền, viền và chữ; raster hóa biến lệnh vẽ thành điểm ảnh, rồi ghép lớp và hiển thị trên màn hình, thường nhờ GPU. Chú thích: DOM và CSSOM được dựng riêng; phải có cả hai mới ghép được.](../../diagrams/sd-01-008-main.svg)

## Đọc hình

**1. DOM.** Khi nhận HTML, trình duyệt đọc dần và dựng **DOM**: một cây, mỗi thẻ là một nút.

**2. CSSOM.** CSS được tải và đọc thành **CSSOM**, cây các quy tắc kiểu dáng. DOM và CSSOM là hai cây riêng.

**3. Cây dựng hình (render tree).** Ghép hai cây: chỉ giữ những phần tử có tạo hộp (box) trên trang, mỗi phần tử kèm kiểu dáng đã tính. Thẻ `<head>` và phần tử `display: none` không tạo hộp nên không có trong cây này.

**4. Bố cục (layout).** Tính vị trí và kích thước hình học của từng phần tử.

**5. Vẽ (paint).** Ghi lại các **lệnh vẽ** cho từng phần tử: tô màu nền, kẻ viền, vẽ chữ, theo thứ tự. Ở trình duyệt hiện đại, bước này thường chỉ ghi lại lệnh vẽ chứ chưa tạo ra điểm ảnh.

**6. Raster hóa, ghép lớp và hiển thị.** Các lệnh vẽ được **raster hóa** thành điểm ảnh (bitmap hoặc các ô ảnh trên GPU), các lớp được ghép lại (composite), rồi lên màn hình. Các bước này thường chạy nhờ GPU và có thể do tiến trình hoặc luồng khác lo.

## Giới hạn cần nhớ

Đây là mô hình đã đơn giản hóa. Trình duyệt thật chạy nhiều bước chồng lên nhau, có thể vẽ từng phần khi trang còn đang tải, và cách chia bước khác nhau giữa các trình duyệt. Khi script đổi DOM hoặc kiểu dáng, một phần của chuỗi này chạy lại.

## Nhìn hình trả lời

Hai phần tử, một cái đặt `display: none`, một cái đặt `visibility: hidden`. Cái nào không nằm trong cây dựng hình? Cái còn lại có chiếm chỗ trên trang không?

<details>
<summary>Xem đáp án</summary>

`display: none` không nằm trong cây dựng hình và không chiếm chỗ. `visibility: hidden` vẫn nằm trong cây và chiếm chỗ, chỉ là không nhìn thấy.

</details>

<details>
<summary>Xem sâu hơn: thứ gì làm trang hiện chậm?</summary>

- **CSS chặn dựng hình:** trình duyệt thường chờ CSS cần thiết tải xong trước khi vẽ lần đầu, để khỏi hiện một trang chưa có kiểu dáng. CSS nặng ở đầu trang làm trang hiện chậm.
- **Script đồng bộ chặn dựng DOM:** gặp `<script>` cổ điển (không phải module) không có `async` hoặc `defer`, bộ đọc HTML tạm dừng để tải và chạy nó; script nội tuyến chạy ngay khi gặp. Script đó có thể phải chờ CSS phía trước tải xong.
- **Bố cục lại và vẽ lại:** đổi kích thước hay vị trí thường buộc tính bố cục lại; đổi màu thường chỉ cần vẽ lại; một số hiệu ứng như `transform` và `opacity` thường chỉ cần ghép lớp. Mức tác động cụ thể phụ thuộc trình duyệt.
- **Cây dựng hình không bằng DOM:** có phần tử có trong DOM mà không có trong cây dựng hình (như `display: none`), và có phần như `::before` có trong cây dựng hình mà không có nút DOM.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-the-browser-render-a-web-page.md): các bước từ HTML và CSS tới điểm ảnh trên màn hình.
- [WHATWG HTML — Parsing](https://html.spec.whatwg.org/multipage/parsing.html): cách đọc HTML thành cây.
- [WHATWG HTML — Phần tử script](https://html.spec.whatwg.org/multipage/scripting.html#the-script-element): script, async và defer.
- [W3C — CSS Display](https://www.w3.org/TR/css-display-3/): display: none không tạo hộp.
- [W3C — CSS 2.1, visibility](https://www.w3.org/TR/CSS2/visufx.html#visibility): visibility: hidden vẫn chiếm chỗ.
- [web.dev — CSS chặn dựng hình](https://web.dev/articles/critical-rendering-path/render-blocking-css): CSS ảnh hưởng thời điểm vẽ lần đầu.
- [Chrome — Kiến trúc RenderingNG](https://developer.chrome.com/docs/chromium/renderingng-architecture): các giai đoạn dựng hình của một trình duyệt cụ thể.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-01-008.json).

# Bản đồ kỹ năng của lập trình viên full-stack

**Full-stack nghĩa là làm được việc ở nhiều vùng của một ứng dụng, từ màn hình người dùng tới hạ tầng chạy ứng dụng; bảy vùng dưới đây là tấm bản đồ.**
Bài nguồn chỉ nêu tên bảy vùng; bài này giữ đúng bảy vùng đó, xếp thành ba nhóm theo vị trí trong một ứng dụng, và tự giải thích từng vùng bằng lời của người biên soạn cùng vài tài liệu của MDN.

![Ba nhóm thẻ xếp dọc. Phía người dùng: frontend là phần chạy trong trình duyệt với HTML, CSS và JavaScript; phát triển di động là ứng dụng cài trên điện thoại; thiết kế giao diện và trải nghiệm quyết định bố cục, luồng thao tác và độ dễ dùng. Phía máy chủ: backend là chương trình nhận yêu cầu, xử lý rồi trả lời; cơ sở dữ liệu lưu dữ liệu có tổ chức. Phía vận hành: điện toán đám mây là thuê máy và dịch vụ; hạ tầng và DevOps giữ ứng dụng chạy và đưa bản mới lên qua CI/CD. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-003-main.svg)

## Từ viết tắt

- **HTML** (HyperText Markup Language) — ngôn ngữ đánh dấu siêu văn bản: văn bản dùng thẻ để mô tả cấu trúc của một trang web.
- **CSS** (Cascading Style Sheets) — bảng kiểu xếp tầng: các luật mô tả màu sắc, cỡ chữ và cách bố trí của trang.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu (request) và máy chủ gửi trả lời (response).
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.
- **DevOps** (Development and Operations) — phát triển và vận hành: cách làm gắn việc viết phần mềm với việc đưa nó lên chạy và giữ nó chạy.
- **CI** (Continuous Integration) — tích hợp liên tục: tự động gộp và kiểm tra mã mỗi khi có thay đổi.
- **CD** (Continuous Delivery) — chuyển giao liên tục: tự động đưa bản đã kiểm tra tới bước phát hành; CI/CD là đường ống gồm cả hai.

## Đọc hình

Hình chia bảy vùng theo vị trí trong một ứng dụng; cả cách chia lẫn lời giải thích dưới đây là của người biên soạn, chỉ có tên bảy vùng là của bài nguồn.

**Phía người dùng.**
- Frontend là phần chạy ngay trong trình duyệt. Theo MDN, HTML mô tả cấu trúc của trang, CSS quyết định trang trông ra sao, và JavaScript thường dùng cho các đoạn mã động chạy phía người dùng. Đây là phần người dùng nhìn thấy và bấm vào.
- Phát triển di động đưa chức năng tương tự vào ứng dụng cài trên điện thoại. Ứng dụng đó thường nói chuyện với cùng một backend với trang web (đây là kiến thức chung của người biên soạn).
- Thiết kế giao diện và trải nghiệm quyết định bố cục màn hình, luồng thao tác và độ dễ dùng, thường trước khi có mã. Việc này gần với con người hơn là với mã.

**Phía máy chủ.**
- Backend là chương trình chạy trên máy chủ. Theo MDN, máy chủ web chờ thông điệp yêu cầu từ trình duyệt, xử lý khi nó tới rồi trả lời bằng thông điệp HTTP; với trang động, nội dung trả về thường được dựng từ dữ liệu lấy trong cơ sở dữ liệu.
- Cơ sở dữ liệu là nơi lưu dữ liệu bền vững. MDN định nghĩa nó là hệ thống lưu trữ gom dữ liệu có tổ chức, giúp việc tìm, sắp xếp và mở rộng dễ hơn.

**Phía vận hành.**
- Điện toán đám mây là thuê máy và dịch vụ từ một nhà cung cấp để chạy ứng dụng, thay vì tự mua và tự đặt máy (kiến thức chung của người biên soạn).
- Hạ tầng và DevOps giữ cho ứng dụng chạy được và đưa bản mới lên chạy; CI/CD là đường ống tự động hóa việc kiểm tra rồi chuyển giao các thay đổi (kiến thức chung của người biên soạn).

## Giới hạn cần nhớ

Bài nguồn nêu **vùng**, không nêu công nghệ cụ thể, mức thành thạo hay thứ tự học. Thứ tự trong hình chỉ để đọc, không phải thứ tự phải học.
Bảy vùng cũng không có nghĩa một người phải sâu ở cả bảy; nguồn chỉ nói người làm full-stack cần thành thạo một dải rộng công nghệ và công cụ.

## Nhìn hình trả lời

Một nhóm nhỏ làm chức năng đặt lịch hẹn: người dùng chọn giờ trên màn hình, lịch được ghi lại, và bản mới phải được đưa lên chạy. Mỗi việc thuộc vùng nào trong hình?

<details>
<summary>Xem đáp án</summary>

Màn hình chọn giờ là frontend (và mobile nếu làm ứng dụng điện thoại); cách bố trí và độ dễ dùng thuộc thiết kế giao diện và trải nghiệm.
Nhận yêu cầu và kiểm tra giờ trống là logic backend, còn ghi lại lịch là việc của cơ sở dữ liệu.
Đưa bản mới lên chạy thuộc điện toán đám mây, hạ tầng và DevOps, qua đường ống CI/CD.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê bảy vùng theo thứ tự frontend, backend, cơ sở dữ liệu, di động, đám mây, thiết kế giao diện và trải nghiệm, hạ tầng và DevOps, mỗi vùng một câu mô tả ngắn. Bài này chỉ giữ tên bảy vùng; không dịch hay diễn đạt lại các câu mô tả đó mà tự giải thích từng vùng, dựa vào tài liệu MDN ở phần frontend, backend và cơ sở dữ liệu, còn lại là kiến thức chung của người biên soạn.
Hình đổi thứ tự để các vùng gần nhau trong một ứng dụng đứng cạnh nhau. Bài không dùng ảnh lộ trình của nguồn nên không nêu tên công nghệ nào (trừ HTML, CSS, JavaScript lấy từ MDN).

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-roadmap-for-full-stack-development.md): tên bảy vùng kỹ thuật của người làm full-stack.
- MDN tại commit cố định: [HTML](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/html/index.md), [CSS](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/css/index.md), [JavaScript](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/javascript/index.md), [Database](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/database/index.md) và [giới thiệu lập trình phía máy chủ](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/learn_web_development/extensions/server-side/first_steps/introduction/index.md): vai trò của frontend, backend và cơ sở dữ liệu. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Phần giải thích di động, thiết kế giao diện, đám mây và hạ tầng cùng các câu giải nghĩa DevOps, CI, CD, HTTP trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

# Tám chuẩn mọi lập trình viên nên biết

**Tám chuẩn: TCP/IP, HTTP, SQL, OAuth, HTML và CSS, ECMAScript, định dạng ngày giờ ISO 8601 và OpenAPI; mỗi chuẩn giải một việc mà lập trình viên gặp thường xuyên.**
Bài nguồn dành cho mỗi chuẩn một hai câu; bài này gom chúng thành ba nhóm theo việc chuẩn lo, và đối chiếu thêm ba chuẩn với tài liệu của chính chúng.

![Ba nhóm thẻ và một khung ghi nhớ. Mạng và web: TCP/IP, HTTP, HTML và CSS. Dữ liệu và trao đổi: SQL, định dạng ngày giờ ISO 8601, OpenAPI. Truy cập và ngôn ngữ: OAuth, ECMAScript. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-014-main.svg)

## Từ viết tắt

- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: quy ước để hai máy truyền dữ liệu tin cậy; cùng với IP làm nên bộ giao thức TCP/IP.
- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ để dữ liệu tìm đúng máy.
- **IETF** (Internet Engineering Task Force) — nhóm đặc nhiệm kỹ thuật Internet: cộng đồng soạn các tiêu chuẩn của Internet; nguồn nói nhóm này phát triển TCP/IP và HTTP.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để hỏi và ghi dữ liệu trong cơ sở dữ liệu.
- **OAuth** (Open AUTHorization) — ủy quyền mở: chuẩn cho một ứng dụng được làm một số việc thay bạn mà không phải biết mật khẩu của bạn.
- **HTML** (HyperText Markup Language) — ngôn ngữ đánh dấu siêu văn bản: văn bản dùng thẻ để mô tả cấu trúc của một trang web.
- **CSS** (Cascading Style Sheets) — bảng kiểu xếp tầng: các luật mô tả màu sắc, cỡ chữ và cách bố trí của trang.
- **ECMA** (European Computer Manufacturers Association) — hiệp hội các nhà sản xuất máy tính châu Âu, nay gọi là Ecma International: tổ chức ban hành đặc tả ECMAScript mà JavaScript tuân theo.
- **ISO** (International Organization for Standardization) — Tổ chức Tiêu chuẩn hóa Quốc tế: nơi ban hành chuẩn ngày giờ ISO 8601.
- **OAS** (OpenAPI Specification) — đặc tả OpenAPI: văn bản chuẩn của OpenAPI, định dạng mô tả API.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: tập quy ước để một chương trình dùng chức năng của chương trình khác.

## Đọc hình

**Mạng và web.**
- TCP/IP: nguồn nói IETF phát triển, là nền của Internet và là một trong những chuẩn mạng nổi tiếng nhất.
- HTTP: cũng do IETF phát triển, thiết yếu với mọi người làm web.
- HTML và CSS: nhờ HTML mà trang web hiển thị đồng nhất giữa các trình duyệt, giảm công sức xử lý khác biệt giữa chúng. CSS thường dùng cùng HTML.

**Dữ liệu và trao đổi.**
- SQL: ngôn ngữ chuyên biệt (domain-specific language) để quản lý dữ liệu.
- ISO 8601: lập trình viên hay gặp rắc rối vì định dạng ngày giờ không thống nhất. ISO 8601 là chuẩn ngày giờ do ISO soạn để trao đổi dữ liệu ngày giờ chung giữa các nước, văn hóa và ngành.
- OpenAPI, còn gọi là OAS: định dạng chuẩn để mô tả và ghi tài liệu cho các API kiểu RESTful.

**Truy cập và ngôn ngữ.**
- OAuth: chuẩn mở về ủy quyền truy cập, thường dùng để cho một trang web hoặc ứng dụng quyền truy cập hạn chế vào thông tin người dùng mà không lộ mật khẩu.
- ECMAScript: đặc tả ngôn ngữ kịch bản đã được chuẩn hóa, làm nền cho nhiều ngôn ngữ; JavaScript là ngôn ngữ nổi tiếng nhất trong số đó.

**Gặp lại trong tài liệu gốc.**
- Tài liệu OpenAPI nói đặc tả này định nghĩa một cách mô tả giao diện chuẩn, không phụ thuộc ngôn ngữ lập trình, cho các API chạy trên HTTP. Câu này rộng hơn chữ "RESTful" trong nguồn.
- Kho mã của ECMA-262 ghi đây là bản nháp hiện hành của "ECMAScript Language Specification". Tài liệu MDN nói: từ tháng 11 năm 1996, Netscape cùng Ecma International đưa JavaScript thành chuẩn công nghiệp, và JavaScript đã chuẩn hóa được gọi là ECMAScript, quy định trong ECMA-262.
- Kho mã của chuẩn HTML tự giới thiệu là nơi chứa HTML Standard.

## Giới hạn cần nhớ

Nguồn không nói chi tiết kỹ thuật của chuẩn nào, không xếp hạng và không nói vì sao chọn đúng tám cái này. Hai ý về IETF (phát triển TCP/IP và HTTP), ISO 8601 do ISO soạn và OAuth là chuẩn mở là lời của nguồn, bài chưa đối chiếu.
Nguồn viết câu về HTML còn dở dang (đuôi câu có chữ "HTML tags" lạc vào); bài chỉ giữ phần hiểu được. Nguồn cũng không phân biệt chuẩn nào là giao thức, ngôn ngữ hay định dạng; cách chia nhóm trong hình là của bài.

## Nhìn hình trả lời

Hai hệ thống ở hai nước trao đổi dữ liệu có ngày giờ và hay hiểu nhầm nhau vì mỗi bên ghi theo một kiểu. Chuẩn nào trong tám chuẩn nhắm đúng vấn đề này? Còn muốn một ứng dụng đọc được thông tin của người dùng mà không biết mật khẩu thì dùng chuẩn nào?

<details>
<summary>Xem đáp án</summary>

Chuẩn ngày giờ ISO 8601: một định dạng chung do ISO soạn để trao đổi dữ liệu ngày giờ giữa các nước, văn hóa và ngành.
Chuẩn OAuth: cho một trang web hoặc ứng dụng quyền truy cập hạn chế vào thông tin người dùng mà không lộ mật khẩu.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và tám đoạn ngắn theo thứ tự TCP/IP, HTTP, SQL, OAuth, HTML/CSS, ECMAScript, ISO Date, OpenAPI. Hình ở đây gom chúng thành ba nhóm theo việc chuẩn lo và không dùng ảnh nguồn.
Mục "Gặp lại trong tài liệu gốc" lấy từ README của OpenAPI, ECMA-262 và HTML Standard cùng tài liệu MDN tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-8-standards-every-developer-should-know.md): tám chuẩn và việc mỗi chuẩn lo.
- [OpenAPI — README](https://github.com/OAI/OpenAPI-Specification/blob/8273770d983c99bb07b389d1706a9f8312ced503/README.md), [ECMA-262 — README](https://github.com/tc39/ecma262/blob/4feb0272b799ea795c5eadee9b482aea0c10ce45/README.md) và [HTML Standard — README](https://github.com/whatwg/html/blob/de953a7cf0523f5873a1904ba2ce010c689dfb66/README.md): OpenAPI mô tả API trên HTTP, ECMA-262 là đặc tả ngôn ngữ ECMAScript, kho mã của HTML Standard. Đọc từ kho mã.
- [MDN — thuật ngữ JavaScript](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/javascript/index.md): JavaScript được chuẩn hóa là ECMAScript, quy định trong ECMA-262. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa viết tắt trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

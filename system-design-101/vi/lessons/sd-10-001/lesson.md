# Sáu loại máy chủ thường gặp

**Cùng gọi là "máy chủ", nhưng mỗi loại làm một việc khác: phát trang web, trả lời chính thức, đứng giữa, dịch tên, chuyển thư, chuyển tệp.**
Bài nguồn chỉ nêu tên sáu loại; bài này giữ đúng sáu tên đó, xếp thành hai nhóm theo vị trí trên đường đi của một yêu cầu, và tự giải thích từng loại bằng lời của người biên soạn cùng vài trang từ điển thuật ngữ của MDN.

![Hai nhóm thẻ xếp dọc. Nhóm đưa nội dung tới người dùng gồm ba thẻ: máy chủ web là phần mềm trả lời trình duyệt bằng nội dung của trang; máy chủ gốc tạo câu trả lời có thẩm quyền cho một tài nguyên còn các máy chủ ở lớp phân phối chỉ giữ bản sao; máy chủ proxy là bên trung gian chuyển yêu cầu đi, trả lời từ bộ đệm hoặc sửa yêu cầu. Nhóm dịch vụ nền của mạng gồm ba thẻ: máy chủ DNS tra tên miền ra địa chỉ IP; máy chủ thư nói SMTP để gửi thư mới và IMAP để lấy và lưu thư; máy chủ FTP chuyển tệp giữa hai máy, không mã hóa nên nhiều nơi thôi hỗ trợ. Khung cuối nhắc rằng đây là sáu vai trò, không phải sáu loại máy.](../../diagrams/sd-10-001-main.svg)

## Từ viết tắt

- **DNS** (Domain Name System) — hệ thống tên miền: hệ thống tra một tên miền ra địa chỉ IP, để người dùng gõ tên dễ nhớ thay vì địa chỉ.
- **IP** (Internet Protocol) — giao thức Internet: địa chỉ IP là địa chỉ ở tầng mạng, gán cho một giao diện mạng của thiết bị để dữ liệu tìm được tới đó.
- **FTP** (File Transfer Protocol) — giao thức truyền tệp: quy ước để chuyển tệp từ máy này sang máy khác qua mạng.
- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhóm máy chủ đặt ở nhiều nơi, giữ bản sao nội dung để máy ở gần người dùng trả lời.
- **SMTP** (Simple Mail Transfer Protocol) — giao thức truyền thư đơn giản: quy ước dùng để gửi một thư mới.
- **IMAP** (Internet Message Access Protocol) — giao thức truy cập thư Internet: quy ước dùng để lấy và lưu thư trên máy chủ.
- **RFC** (Request For Comments) — yêu cầu bình luận: tên của loạt văn bản kỹ thuật mô tả các chuẩn của Internet; RFC 9110 là văn bản mô tả cách các máy trao đổi thông điệp web.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

Hình chia sáu loại theo vị trí trên đường đi của một yêu cầu; cả cách chia lẫn lời giải thích dưới đây là của người biên soạn, chỉ có tên sáu loại là của bài nguồn.

**Nhóm 1 · Đưa nội dung tới người dùng.**
- Máy chủ web là chương trình trả lời trình duyệt bằng nội dung của trang. MDN lưu ý chữ "máy chủ" có hai nghĩa: máy phần cứng đặt trong trung tâm dữ liệu, và phần mềm chạy trên máy đó; "máy chủ web" thường chỉ phần mềm.
- Máy chủ gốc (origin server) là chương trình có thể tạo ra câu trả lời có thẩm quyền cho một tài nguyên được yêu cầu, theo định nghĩa của RFC 9110. Với trang tĩnh, đó thường là tệp nó giữ; với trang động hay cá nhân hóa, nó có thể dựng câu trả lời lúc có yêu cầu từ mã ứng dụng và dữ liệu, nên không nhất thiết có một bản chính để sao chép. Khi có lớp phân phối đứng trước, các máy chủ ở đó giữ bản sao và có thể trả lời thay; MDN mô tả CDN là nhóm máy chủ đặt ở nhiều nơi, giữ bản sao dữ liệu để máy gần người dùng nhất trả lời yêu cầu.
- Máy chủ proxy là bên đứng giữa. Theo MDN, proxy chặn yêu cầu rồi trả lời; nó có thể chuyển yêu cầu đi hoặc không (như khi trả lời từ bộ nhớ đệm), và có thể sửa yêu cầu, chẳng hạn đổi tiêu đề ở ranh giới giữa hai mạng. Có hai kiểu chính: proxy chuyển tiếp (forward) xử lý yêu cầu của người dùng đi tới mọi nơi trên Internet, và proxy ngược (reverse) nhận yêu cầu từ Internet rồi chuyển cho máy chủ trong mạng nội bộ.

**Nhóm 2 · Dịch vụ nền của mạng.**
- Máy chủ DNS phục vụ hệ thống đặt tên của Internet. Theo MDN, DNS là hệ thống đặt tên phân cấp và phi tập trung; việc nổi bật nhất của nó là tra một tên miền thân thiện ra địa chỉ IP, và nó cũng có thể tra ngược từ địa chỉ ra tên miền.
- Máy chủ thư là phần mềm nói các giao thức của thư điện tử. MDN mô tả SMTP là giao thức dùng để gửi một thư mới, còn IMAP là giao thức dùng để lấy và lưu thư, cho phép thư mục và luật ngay trên máy chủ.
- Máy chủ FTP truyền tệp từ máy này sang máy khác. MDN ghi FTP vốn không an toàn, từng là cách chuẩn nhưng nay nhiều dịch vụ lưu trữ thôi hỗ trợ, và nên dùng cách truyền tệp được mã hóa.

## Giới hạn cần nhớ

Sáu loại là sáu **vai trò**, không phải sáu loại máy khác nhau. Một máy có thể đảm nhận nhiều vai trò, và một vai trò có thể chia cho nhiều máy. MDN chỉ nói chữ "server" có thể là phần cứng hoặc phần mềm cung cấp dịch vụ cho máy khách; việc một máy giữ nhiều vai trò là kiến thức chung của người biên soạn.
Danh sách cũng chỉ là "sáu loại thường dùng", không phải mọi loại máy chủ.

## Nhìn hình trả lời

Bạn gõ tên một website vào trình duyệt lần đầu, khi chưa có địa chỉ nào được nhớ sẵn và trình duyệt đi thẳng tới trang. Trong sáu loại ở hình, loại nào được hỏi trước, và để làm gì?

<details>
<summary>Xem đáp án</summary>

Máy chủ DNS. Trình duyệt biết tên nhưng cần địa chỉ IP để gửi yêu cầu đi, nên khi chưa có sẵn địa chỉ thì phải hỏi DNS trước. Nếu địa chỉ đã được nhớ sẵn (bộ nhớ đệm DNS, mà MDN nói giúp giảm độ trễ của việc dịch tên) thì thường không phải hỏi lại, và khi đi qua proxy chuyển tiếp thì việc dịch tên có thể do proxy làm (MDN nói proxy chuyển tiếp lưu và chuyển tiếp các dịch vụ như DNS). Việc kết luận rằng câu trả lời "hỏi DNS trước" chỉ đúng khi chưa có bộ nhớ đệm và không qua proxy là suy luận của người biên soạn.
Có địa chỉ rồi, yêu cầu tới máy chủ web, có thể qua một proxy đứng giữa. Nếu nội dung đã được phân phát tới máy chủ ở lớp phân phối, người dùng nhận từ máy chủ ở lớp phân phối thay vì từ máy chủ gốc.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê sáu loại theo thứ tự web, thư, DNS, proxy, FTP, gốc, mỗi loại một câu mô tả ngắn và không nói loại này liên hệ với loại kia thế nào. Bài này chỉ giữ tên sáu loại; không dịch hay diễn đạt lại các câu mô tả đó mà tự giải thích từng loại, dựa vào các trang từ điển thuật ngữ của MDN (máy chủ, DNS, proxy, FTP, SMTP, IMAP, CDN) và RFC 9110 ở mục nguồn; định nghĩa máy chủ gốc lấy từ RFC 9110, còn cách phân biệt vai trò với máy là kiến thức chung của người biên soạn.
Hình xếp lại thành hai nhóm; máy chủ gốc đứng cạnh máy chủ web vì cùng liên quan tới nội dung phát cho người dùng. Bài không nhắc tới sản phẩm cụ thể nào và không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-most-commonly-used-server-types.md): tên sáu loại máy chủ.
- MDN tại commit cố định: [Server](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/server/index.md), [Web server](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/web_server/index.md), [Proxy server](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/proxy_server/index.md), [CDN](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/cdn/index.md), [DNS](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/dns/index.md), [SMTP](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/smtp/index.md), [IMAP](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/imap/index.md) và [FTP](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/ftp/index.md): vai trò của từng loại. Đọc từ kho mã.
- [RFC 9110 — bản XML của nhóm làm việc HTTP tại commit cố định](https://github.com/httpwg/http-core/blob/bde37f634681bd5462568b73aa722af9c9a3ef5e/rfc9110.xml): định nghĩa máy chủ gốc. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Phần nói về vai trò so với máy, đường đi của một lần tải trang và các câu giải nghĩa IP trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

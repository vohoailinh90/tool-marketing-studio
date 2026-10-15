# Token, cookie và session: nhận ra người dùng thế nào?

**HTTP không nhớ ai, nên mỗi cách “nhớ người dùng” là một lựa chọn về thứ gì đi kèm mỗi yêu cầu và thứ gì máy chủ phải giữ.**
Bốn cách phổ biến: gửi lại tên và mật khẩu, mã session, token ngẫu nhiên (cùng mô hình trạng thái với session, chỉ khác nơi mang mã), hoặc token tự mang thông tin (JWT).

![Sáu thẻ xếp dọc. Thẻ đầu là câu hỏi chung: mỗi yêu cầu đi kèm gì để máy chủ biết đó là ai. Bốn cách. Basic: mỗi yêu cầu gửi lại tên và mật khẩu, mã hóa base64 nên ai cũng giải ngược được. Session cookie: máy chủ giữ dữ liệu, trình duyệt gửi lại một mã. Token ngẫu nhiên: cùng mô hình trạng thái với session, máy chủ vẫn tra cứu; khác ở chỗ client gắn mã vào tiêu đề thay vì cookie. JWT: token tự mang thông tin và chữ ký, kiểm tra được mà không cần tra máy chủ, nhưng nội dung đọc được và khó thu hồi trước hạn. Thẻ cuối là cái giá: càng ít trạng thái ở máy chủ thì càng khó thu hồi.](../../diagrams/sd-14-010-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm các cặp tên và giá trị, được dùng rất rộng rãi để các chương trình trao đổi dữ liệu với nhau.
- **JWT** (JSON Web Token) — token web: chuỗi tự mang thông tin người dùng và có chữ ký, để máy chủ kiểm mà không cần tra bảng.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.
- **HTTPS** (HyperText Transfer Protocol Secure) — HTTP được mã hóa: cùng cách gửi yêu cầu và trả lời như HTTP nhưng nội dung được giữ kín trên đường đi.
- **SSO** (Single Sign-On) — đăng nhập một lần: đăng nhập một lần rồi dùng được nhiều ứng dụng.
- **OAuth** (Open AUTHorization) — chuẩn ủy quyền mở: cho một ứng dụng được làm một số việc thay bạn mà không biết mật khẩu của bạn.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.

## Đọc hình

**Basic.** Trình duyệt hỏi tên và mật khẩu rồi gửi lại trong tiêu đề `Authorization` ở mọi yêu cầu. Khi chạy thử, máy chủ trả 401 kèm `WWW-Authenticate: Basic`, và hai yêu cầu liên tiếp mang cùng một tiêu đề. Phần sau “Basic” chỉ là base64, giải ngược được mà không cần khóa; MDN nhấn mạnh Basic gửi thông tin đăng nhập ở dạng mã hóa ký tự chứ không phải mã hóa bảo mật, nên chỉ nên dùng qua HTTPS.

**Session cookie.** Máy chủ giữ dữ liệu phiên, trình duyệt giữ một mã. Vì dữ liệu nằm ở máy chủ, xóa phiên là mã đó không còn tra ra gì (suy luận từ cách session hoạt động).

**Token ngẫu nhiên.** Về trạng thái, đây chính là một mã phiên: một chuỗi ngẫu nhiên mà máy chủ tra cứu, nên máy chủ phải giữ và có thể thu hồi giống session. Chỗ khác chỉ là cách mang mã: client tự gắn nó vào tiêu đề thay vì dựa vào cookie của trình duyệt. Cookie hay tiêu đề là lựa chọn về đường vận chuyển, không phải một loại token khác, và bài không bàn các cách mang token còn lại (suy luận của người biên soạn).

**JWT.** Token mang sẵn thông tin (ví dụ người dùng, vai trò, hạn dùng) và một chữ ký, nên máy chủ kiểm tra được bằng khóa mà không cần tra kho. Khi chạy thử với PyJWT: đọc phần thông tin không cần khóa; sửa vai trò thành admin thì chữ ký không còn khớp; token quá hạn bị từ chối; token khai thuật toán `none` bị từ chối khi máy chủ chỉ chấp nhận `HS256`.

## Giới hạn cần nhớ

JWT thông thường, loại được ký và là loại chạy thử ở đây, không bị che: ai cầm token cũng đọc được thông tin trong đó, nên đừng để bí mật vào (có dạng JWT được mã hóa riêng, bài không bàn). Vì máy chủ không tra kho, một JWT còn hạn vẫn hợp lệ sau khi người dùng “đăng xuất”;
muốn thu hồi sớm một token cụ thể thì phải giữ lại một danh sách trạng thái, tức là mất đúng cái lợi ban đầu (đã chạy thử: sau khi “đăng xuất” với kho trống, cùng token vẫn qua được bước kiểm tra).

## Nhìn hình trả lời

Một ứng dụng dùng JWT hạn một giờ. Người dùng báo mất điện thoại, và quản trị muốn chặn token ngay. Việc gì làm được, và vì sao không đơn giản?

<details>
<summary>Xem đáp án</summary>

Chữ ký vẫn hợp lệ cho tới khi hết hạn, nên máy chủ không thể “hủy” token chỉ bằng cách kiểm tra chữ ký. Hai cách chặn được ngay một token đã phát: giữ một danh sách token bị thu hồi để kiểm tra mỗi lần, hoặc đổi khóa dùng để kiểm tra chữ ký (làm vô hiệu cả những token khác ký bằng khóa đó). Hạn ngắn kèm cấp lại chỉ thu hẹp thời gian một token bị lộ còn dùng được ở các lần cấp sau; nó không chặn token một giờ đang có.
Mỗi cách thêm một phần trạng thái hoặc một chi phí khác, nên session hay token ngẫu nhiên có kho ở máy chủ thường dễ thu hồi hơn (suy luận của người biên soạn từ thiết kế).

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn xếp các cách theo thứ tự “từ đơn giản tới phức tạp” và lẫn cả SSO lẫn OAuth 2.0 vào cùng danh sách; bài này chỉ giữ các cách nhận ra người dùng ở mỗi yêu cầu, còn SSO và OAuth nằm ở bài riêng vì chúng trả lời câu hỏi khác.
Bài nguồn nói Basic “ít dùng” vì không kiểm soát được vòng đời đăng nhập, cookie “không thân thiện với ứng dụng di động”, và token “tốn thời gian mã hóa, giải mã”; bài này không lặp lại ba nhận định đó vì chưa kiểm. Token ngẫu nhiên không cần mã hóa, chỉ cần tra cứu; JWT thông thường được ký chứ không mã hóa.
Bài nguồn nói JWT khiến máy chủ không cần lưu thông tin phiên; bài này giữ ý đó cho việc kiểm tra, nhưng nêu thêm cái giá là thu hồi.

OWASP lưu ý mã session (hay token) sau khi đăng nhập tương đương với thông tin đăng nhập mạnh nhất của ứng dụng, nên lộ nó là bị mạo danh người dùng. Ví dụ chạy thử dùng máy chủ Python, `curl` và PyJWT 2.15.1 với khóa thử nghiệm ngắn; không phải cấu hình nên dùng thật.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/token-cookie-session.md): danh sách các cách quản lý danh tính từ Basic tới OAuth 2.0.
- [MDN — HTTP authentication](https://github.com/mdn/content/blob/19370346042efad9e179fbf1f55deeeadee98c40/files/en-us/web/http/guides/authentication/index.md): luồng 401 kèm `WWW-Authenticate`, lược đồ Basic gửi thông tin đăng nhập mã hóa ký tự chứ không phải mã hóa bảo mật. Đọc từ bản clone của kho.
- [PyJWT — tài liệu sử dụng](https://github.com/jpadilla/pyjwt/blob/f97b3273d3db3ed7266ae009784d65f1877dba66/docs/usage.rst): đọc thông tin của JWT không cần xác thực là không đáng tin; token quá hạn bị từ chối. Đọc qua nguồn trên GitHub.
- [OWASP — Session Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Session_Management_Cheat_Sheet.md): mã session sau khi xác thực tương đương thông tin đăng nhập mạnh nhất; lộ mã dẫn tới chiếm phiên. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Ví dụ chạy thử bằng máy chủ Python, `curl` và PyJWT 2.15.1; không có tài liệu RFC nào được mở (trang RFC không truy cập được). Bài viết và hình được thiết kế độc lập.

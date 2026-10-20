# Sáu cách nhận ra người dùng: session, token, JWT, SSO, OAuth2 và mã QR

**Sáu cách này khác nhau ở hai chỗ: ai giữ trạng thái đăng nhập, và điều được chứng minh là “bạn là ai” hay “ứng dụng được làm gì”. OAuth2 thuộc nhóm “được làm gì”, còn mã QR đăng nhập được nhờ một điện thoại đã đăng nhập sẵn xác nhận thay cho bạn.**
Bài này gom sáu mục của bài nguồn thành một bản đồ và chỉ đào sâu mã QR, cách kho bài chưa có ở đâu khác. Cookie, session, token, SSO và OAuth đã có bài riêng ([bài sd-14-008](../sd-14-008/lesson.md), [bài sd-14-010](../sd-14-010/lesson.md), [bài sd-14-011](../sd-14-011/lesson.md)). Mã QR được dựng thử bằng máy chủ đồ chơi, không phải dịch vụ thật.

![Bốn khung dọc. Khung một, nhớ người đã đăng nhập: session, token ngẫu nhiên và JWT, khác nhau ở chỗ ai giữ dữ liệu. Khung hai, nhờ bên khác làm chứng: SSO và mã QR chứng minh bạn là ai, còn OAuth2 chỉ chứng minh ứng dụng được làm gì. Khung ba, trình tự đăng nhập bằng mã QR giữa trình duyệt, máy chủ và điện thoại. Khung bốn, hai điều cần nhớ về mã QR.](../../diagrams/sd-14-033-main.svg)

## Từ viết tắt

- **JWT** (JSON Web Token) — token web JSON: token tự mang thông tin người dùng và một chữ ký để kiểm.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm cặp tên và giá trị.
- **SSO** (Single Sign-On) — đăng nhập một lần rồi dùng được nhiều ứng dụng.
- **OAuth** (Open AUTHorization) — chuẩn ủy quyền mở: cho ứng dụng làm một số việc thay bạn, không cần mật khẩu của bạn.
- **QR** (Quick Response) — phản hồi nhanh: hình ô đen trắng mà camera đọc ra thành một chuỗi chữ.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, bài dùng hướng dẫn của họ.
- **CSRF** (Cross-Site Request Forgery) — giả mạo yêu cầu liên trang: bắt trình duyệt gửi yêu cầu mà chủ nó không định gửi; “login CSRF” là khi yêu cầu ấy là đăng nhập.

## Đọc hình

Hai câu hỏi cho mỗi cách: ai giữ trạng thái đã đăng nhập, và điều được chứng minh là bạn là ai (xác thực) hay ứng dụng được làm gì (ủy quyền).

**Khung 1.** Session: máy chủ giữ dữ liệu, trình duyệt giữ một mã. Token ngẫu nhiên: cùng mô hình, chỉ khác nơi mang mã. JWT: dữ liệu và chữ ký nằm trong token, máy chủ chỉ giữ khóa để kiểm. JWT chỉ là khuôn đựng: OWASP kể nó làm token danh tính lẫn access token. Cái giá (OWASP): muốn vô hiệu một phiên phải có danh sách thu hồi, và khi đó nó không còn “không trạng thái”.

**Khung 2.** SSO: một dịch vụ đăng nhập trung tâm giữ phiên, các ứng dụng nhận kết quả xác thực. OAuth2: máy chủ ủy quyền cấp access token cho một ứng dụng; OWASP gọi OAuth là khung ủy quyền, còn nhận ra người dùng cần lớp xác thực xây trên nó.

**Khung 3.** (1) Trình duyệt xin một mã; máy chủ sinh mã ngẫu nhiên, ghi “đang chờ” và cho hết hạn nhanh. (2) Trình duyệt vẽ mã thành hình QR và hỏi máy chủ định kỳ. (3) Điện thoại quét, gửi mã kèm phiên đã đăng nhập sẵn của nó. (4) Ở lần hỏi sau, trình duyệt nhận một phiên mới và mã hết tác dụng. Bằng chứng danh tính là phiên của điện thoại; hình QR chỉ chuyển mã giữa hai thiết bị.

## Giới hạn cần nhớ

Máy chủ chỉ biết “một phiên đã đăng nhập vừa xác nhận mã này”, không biết chủ điện thoại có định đăng nhập trình duyệt đang hiện mã hay không. Khi chạy thử, điện thoại của kẻ tấn công xác nhận mã trên trình duyệt của nạn nhân (giả định kẻ ấy biết mã, không thử cách biết) thì trình duyệt ấy thành tài khoản của kẻ tấn công. Chiều ngược lại, nạn nhân quét mã hiện trên trình duyệt của kẻ tấn công, thì trình duyệt kia thành nạn nhân; OWASP gọi chiều này là `QRLJacking` và khuyên đừng dùng đăng nhập QR trừ khi cần. Máy chủ đồ chơi không có biện pháp giảm rủi ro nào.

## Nhìn hình trả lời

Alice, đã đăng nhập sẵn trên điện thoại, quét một hình QR trên trang lạ bằng ứng dụng của dịch vụ. Máy chủ thấy gì ở bước đó, và thiếu gì để biết cô có chủ ý đăng nhập trình duyệt ấy?

<details>
<summary>Xem đáp án</summary>

Máy chủ thấy một phiên hợp lệ của Alice và một mã còn hạn đang chờ, nên xác nhận. Nó không thấy trình duyệt nào đang hiện mã và ai ngồi ở đó. Nếu mã do trình duyệt của kẻ tấn công xin, trình duyệt ấy nhận phiên của Alice ở lần hỏi sau. Trong các cách giảm rủi ro, OWASP nêu một màn hình xác nhận hiện thông tin phiên.

</details>

<details>
<summary>Xem sâu hơn: thử nghiệm và điều đã chỉnh so với bài nguồn</summary>

**Máy chủ đồ chơi.** Python 3.13, thư viện chuẩn, cổng ngẫu nhiên trên máy cục bộ; mỗi “thiết bị” một kho cookie; quét là giả lập, điện thoại đăng nhập sẵn không cần mật khẩu. Mã là 16 byte ngẫu nhiên (22 ký tự); `segno` 1.6.6 vẽ mã 30 ký tự thành QR 25x25 ô. Một lần chạy trên máy tác giả cho:

1. Mã một mình không đăng nhập ai: chưa xác nhận thì chỉ “đang chờ”; mã làm cookie thì `/me` trả `401`; điện thoại chưa đăng nhập xác nhận cũng `401`.
2. Dùng một lần: lần hỏi thứ hai `410`; xác nhận lại `409`; 20 lần hỏi đồng thời chỉ cấp 1 phiên. Nhưng chỉ một người thắng, chưa chắc đúng người: máy khách chỉ biết mã mà hỏi trước nhận phiên của Alice, trình duyệt thật nhận `410`. Dịch vụ thật có buộc lần hỏi vào trình duyệt xin mã hay không, nguồn tôi đọc không nói.
3. Hết hạn (1 giây cho lần thử): xác nhận sau hạn `410`; xác nhận kịp nhưng lấy muộn cũng `410` (lựa chọn của máy chủ thử).
4. Sai điện thoại: như phần Giới hạn. Máy chủ ghi hai lần xác nhận cùng dạng; trên một máy mọi địa chỉ là `127.0.0.1`, nên lần chạy không nói được kiểm địa chỉ có giúp không.
5. Phiên nhận được khác mã QR, như OWASP đòi: đổi mã phiên khi đăng nhập.

**OWASP nói gì.** Cheat sheet không có trang về đăng nhập QR (QR chỉ hiện ở việc nạp hạt giống cho ứng dụng sinh mã một lần). Trang `QRLJacking` nói mã nên có thời hạn và nêu bốn cách giảm rủi ro: xác nhận phiên, giới hạn theo mạng, theo vị trí, bước âm thanh. Cheat sheet CSRF mô tả login CSRF và cách giảm cho biểu mẫu đăng nhập (phiên trước đăng nhập kèm token); tôi không thử cách đó với luồng QR.

**Điều đã chỉnh so với bài nguồn.**
- “Cookie không hợp nhiều thiết bị”: mỗi thiết bị tự đăng nhập và có mã phiên riêng; đăng xuất máy này không ảnh hưởng máy kia (đã chạy thử). Token cất trong ứng dụng cũng ở một máy, nên đó không phân biệt cookie với token.
- “Token không cần lưu ở máy chủ”: đúng với token tự mang dữ liệu, không đúng với token ngẫu nhiên.
- “Token cần mã hóa/giải mã”: token ngẫu nhiên chỉ cần tra cứu; JWT ký cần ký và kiểm, và đọc nội dung không cần khóa (đã chạy thử với PyJWT 2.14.0). Giữ kín là việc của JWT mã hóa, một lựa chọn riêng (OWASP).
- OAuth2 là ủy quyền, không phải cách nhận ra người dùng.
- Mã QR: nguồn nói quét là xong, bỏ qua việc điện thoại phải đăng nhập sẵn và trình duyệt phải chờ phiên. Trang OWASP còn trích một thiết kế khác (QR chứa địa chỉ máy chủ, điện thoại gửi mã thiết bị), nên “mã ngẫu nhiên” chỉ là một cách cài đặt.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/session-cookie-jwt-token-sso-and-oauth-2.md).
- [OWASP — QRLJacking](https://github.com/OWASP/www-community/blob/ce2814653f497a7a9ebadce39ce7f84bb3c603e4/pages/attacks/Qrljacking.md): tấn công qua mã QR, thời hạn mã, cách giảm rủi ro.
- OWASP Cheat Sheet Series: [CSRF Prevention](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md), [Session Management](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Session_Management_Cheat_Sheet.md), [JSON Web Token](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/JSON_Web_Token_Cheat_Sheet.md), [Authentication](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Authentication_Cheat_Sheet.md).
- [MDN — Using HTTP cookies](https://github.com/mdn/content/blob/19370346042efad9e179fbf1f55deeeadee98c40/files/en-us/web/http/guides/cookies/index.md): trình duyệt lưu cookie và gửi lại cho cùng máy chủ.
- [segno](https://github.com/heuer/segno/blob/9b67a3f2914be966c35dd8f00bef19d01b9ec68e/segno/__init__.py) và [PyJWT — usage](https://github.com/jpadilla/pyjwt/blob/f97b3273d3db3ed7266ae009784d65f1877dba66/docs/usage.rst): dùng trong lần chạy thử.

Đã đọc nguồn ngày 2026-10-18. Bản đồ hai câu hỏi, trình tự mã QR và máy chủ đồ chơi là của người biên soạn; không đọc được RFC nên không trích RFC. Bài viết và hình được thiết kế độc lập.

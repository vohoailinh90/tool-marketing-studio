# Cookie và session khác nhau thế nào?

**Cookie và session đều giúp máy chủ nhận ra bạn qua nhiều yêu cầu HTTP, nhưng chúng khác nhau ở chỗ dữ liệu nằm ở đâu.**
Với cookie, dữ liệu nằm trong trình duyệt. Với session, dữ liệu nằm trên máy chủ và trình duyệt chỉ cầm một mã để tìm ra nó.

![Bốn thẻ xếp dọc, chia thành hai nhánh bằng hai nhãn. Thẻ đầu: HTTP không nhớ ai, nên cần một cách nhận ra người dùng qua nhiều yêu cầu. Hai nhánh. Cookie: máy chủ gửi Set-Cookie, trình duyệt lưu giá trị và gửi lại trong tiêu đề Cookie, dữ liệu nằm ở trình duyệt. Session: máy chủ tạo một mã ngẫu nhiên, cất dữ liệu ở bên mình, chỉ đưa mã cho trình duyệt, thường qua một cookie. Thẻ cuối là hệ quả: mã session sai thì máy chủ không tìm thấy dữ liệu, nhưng ai lấy được mã đúng thì dùng được session đó.](../../diagrams/sd-14-008-main.svg)

## Đọc hình

**Vì sao cần.** HTTP không tự nhớ yêu cầu trước, nên máy chủ cần một cách nối các yêu cầu của cùng một người.

**Cookie.** Máy chủ trả tiêu đề `Set-Cookie`; trình duyệt lưu lại và gửi giá trị đó trong tiêu đề `Cookie` ở các yêu cầu sau tới cùng trang. Dữ liệu nằm ở trình duyệt, nên dung lượng bị giới hạn (thường khoảng 4 KB mỗi cookie theo MDN), và theo mặc định người dùng nhìn thấy được và đổi được giá trị cookie.

**Session.** Máy chủ tạo một mã ngẫu nhiên, lưu dữ liệu của phiên (ví dụ người dùng đã đăng nhập, giỏ hàng) ở phía mình, và đưa mã cho trình duyệt, thường bằng một cookie. Các yêu cầu sau mang mã đó để máy chủ tìm lại dữ liệu.
Khi chạy thử, yêu cầu có mã đúng nhận lại dữ liệu phiên; mã bị đổi hoặc không có cookie thì máy chủ không tìm thấy gì.

## Giới hạn cần nhớ

Session không tự động an toàn hơn cookie: mã session vẫn đi trong một cookie, ai lấy được mã đúng thì dùng được phiên đó nếu máy chủ không có thêm kiểm tra khác, nên cookie mang mã nên có `HttpOnly`, `Secure` và `SameSite` (xem bài về cookie HTTP).
Đổi lại, dữ liệu nằm trên máy chủ nên máy chủ phải lưu và dọn các phiên, và khi có nhiều máy chủ thì cần một chỗ lưu dùng chung (suy luận của người biên soạn).

## Nhìn hình trả lời

Một trang đặt giỏ hàng trong cookie và một trang khác đặt giỏ hàng trong session. Người dùng sửa được gì ở mỗi trang, và việc lộ mã session có nghĩa là gì?

<details>
<summary>Xem đáp án</summary>

Giỏ hàng trong cookie nằm ở trình duyệt, nên người dùng có thể đọc và sửa nó; máy chủ không nên tin giá trị đó mà không kiểm tra. Giỏ hàng trong session nằm trên máy chủ, người dùng chỉ cầm mã, nên không sửa trực tiếp được nội dung, và đổi mã thành giá trị khác chỉ làm máy chủ không tìm thấy phiên (đã chạy thử).
Nhưng nếu ai đó lấy được mã đúng, họ dùng được phiên đó: bảo mật của session dồn vào việc giữ kín mã.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn nói session “bảo mật hơn” vì dữ liệu không do trình duyệt truy cập trực tiếp. Điều đó đúng với nội dung dữ liệu, nhưng bài này bổ sung rằng mã session vẫn là một bí mật phải giữ, và MDN lưu ý nên cấp lại cookie phiên mỗi khi người dùng đăng nhập để chống tấn công cố định phiên (session fixation).
Bài nguồn nói người dùng “có thể cấm cookie”; bài này không dựa vào điều đó vì chưa kiểm và vì nó không ảnh hưởng tới cách phân biệt chính.
Con số 4 KB lấy từ MDN (“thường là 4 KB”), và giới hạn thực tế khác nhau giữa trình duyệt.

Ví dụ chạy thử là một máy chủ Python nhỏ với kho session trong bộ nhớ, thử bằng `curl`; nó không phải cách làm cho môi trường thật (không có hết hạn, không xoay mã).

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-differences-between-cookies-and-sessions.md): cookie lưu ở trình duyệt, session lưu ở máy chủ, mã session trả về qua cookie.
- [MDN — Using HTTP cookies](https://github.com/mdn/content/blob/main/files/en-us/web/http/guides/cookies/index.md): luồng `Set-Cookie` và `Cookie`, giới hạn khoảng 4 KB, `HttpOnly`, `Secure`, `SameSite`, cấp lại cookie phiên khi đăng nhập. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Ví dụ chạy thử bằng máy chủ Python và `curl`. Bài viết và hình được thiết kế độc lập.

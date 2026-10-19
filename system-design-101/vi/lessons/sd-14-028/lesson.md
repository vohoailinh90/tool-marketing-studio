# Cookie là gì? Tấm thẻ khách quen và điều nó không phải

**Cookie là một mẩu chữ nhỏ do máy chủ nhờ trình duyệt giữ hộ; trình duyệt tự gửi nó lại ở các yêu cầu sau tới đúng trang đã đặt nó.** Cookie chỉ là dữ liệu: nó không tự chạy gì, người dùng đọc và sửa được, và tự nó không chứng minh bạn là ai.
Bài mượn tấm thẻ khách quen của một quán cà phê làm điểm vào, rồi chạy thử một máy chủ Python nhỏ để xem ví von ấy đúng ở đâu, sai ở đâu. Thuộc tính cookie xem [bài sd-14-009](../sd-14-009/lesson.md), cookie so với session xem [bài sd-14-008](../sd-14-008/lesson.md), token xem [bài sd-14-010](../sd-14-010/lesson.md).

![Ba nhóm xếp dọc. Cookie đi lại: máy chủ gửi Set-Cookie, trình duyệt giữ hộ, mỗi yêu cầu sau trình duyệt tự gắn tên và giá trị vào tiêu đề Cookie, thuộc tính không gửi lại. Ba kiểu cookie: mang dữ liệu thì người dùng sửa được; mang mã ngẫu nhiên thì máy chủ tra bảng của mình; mang dữ liệu kèm mã xác thực thì sửa bị từ chối nhưng vẫn đọc và sao chép được. Ba điều cookie không phải: chương trình, két sắt, bằng chứng danh tính.](../../diagrams/sd-14-028-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ trả lời.
- **HTTPS** (HyperText Transfer Protocol Secure) — HTTP được mã hóa: nội dung được giữ kín trên đường đi.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, tài liệu tra cứu công nghệ web của Mozilla và cộng đồng; bài dùng nó để đối chiếu.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng về bảo mật ứng dụng; bài dùng hướng dẫn của họ để đối chiếu.

## Đọc hình

Kết quả dưới đây là một lần chạy trên máy biên soạn: máy chủ `http.server` của Python 3.13 trên `127.0.0.1`, "trình duyệt" là `urllib` cùng `http.cookiejar`. Python không phải trình duyệt, nên đây là mô hình để quan sát.

**1 · Tấm thẻ.** Quán phát thẻ khách quen ghi sẵn khách thích gì, lần sau khách mang thẻ tới. Cookie cũng đi một vòng như vậy: máy chủ trả `Set-Cookie: tên=giá trị` kèm thuộc tính, trình duyệt lưu lại, và ở các yêu cầu sau tới trang khớp thì gắn `tên=giá trị` vào tiêu đề `Cookie`.

**2 · Chỗ lệch thứ nhất: không ai đưa thẻ.** Máy chủ đặt `theme=dark` đúng một lần. Ba yêu cầu sau đó (hai tới `/page`, một tới `/other`) đều mang `Cookie: theme=dark`, dù client không có dòng lệnh nào gắn nó; MDN mô tả đúng việc này, trình duyệt thường gửi lại cookie đã lưu cho miền hiện tại. Cookie không đi sang tên khác: cùng máy chủ ấy, gọi bằng `localhost` thay vì `127.0.0.1`, không nhận được cookie nào.

**3 · Chỗ lệch thứ hai: máy chủ chỉ nhận lại nửa tấm thẻ.** Máy chủ đã gửi `Path=/; Max-Age=3600; HttpOnly; SameSite=Lax`, nhưng yêu cầu quay lại chỉ chứa `theme=dark`. Thuộc tính là lời dặn cho trình duyệt, không được gửi ngược; MDN cũng ghi tiêu đề `Cookie` không chứa thuộc tính, nên máy chủ không đọc được hạn dùng hay phạm vi của cookie từ yêu cầu.

**4 · Chỗ lệch thứ ba: "không cần tra cơ sở dữ liệu" chỉ đúng với một kiểu cookie.** Máy chủ thử có ba kiểu và đếm số lần nó tra bảng phiên:

- **Mang dữ liệu** (`theme=dark`): 0 lần tra, vì giá trị chính là dữ liệu. `theme=hotpink` gõ tay được nhận y nguyên; với màu giao diện thì không sao, vì người dùng quyết định việc của mình. Nhưng cookie `user=alice` đổi thành `user=admin` thì máy chủ trả lời `user=admin`: nó tin cái được gửi tới.
- **Mang mã ngẫu nhiên** (`sid=` cùng 22 ký tự ngẫu nhiên): 1 lần tra mỗi yêu cầu. Mã bừa cùng độ dài, hay mã thật bị đổi ký tự cuối, không ra phiên nào: máy chủ coi như chưa đăng nhập. Khi máy chủ xóa phiên, chính cookie cũ hết giá trị.
- **Mang dữ liệu kèm mã xác thực** (`user=alice.` rồi 64 ký tự): 0 lần tra, vì máy chủ tự tính lại mã bằng khóa bí mật của mình. Sửa `alice` thành `admin` thì bị từ chối. Nhưng tên vẫn đọc được, và bản sao nguyên vẹn vẫn dùng được ở nơi khác; chỉ khi máy chủ đổi khóa thì cookie cũ mới bị từ chối.

## Giới hạn cần nhớ

**Cookie không tự chứng minh danh tính.** Nó chỉ cho thấy người gửi đang cầm đúng một chuỗi. Khi chép nguyên mã `sid` thật sang một client khác, máy chủ trả `user=alice`: ai cầm đúng mã thì được nhận là chủ. OWASP nói cùng ý: khi phiên đã xác thực, mã session tạm thời tương đương cách xác thực mạnh nhất của ứng dụng, nên lộ mã là bị mạo danh.
Vì thế cookie mã phiên nên khai `Secure` (chỉ gửi qua HTTPS), `HttpOnly` và `SameSite`, và đừng cất bí mật hay dữ liệu cá nhân thẳng vào giá trị cookie: MDN gợi ý, tùy ứng dụng, dùng mã để máy chủ tra; OWASP muốn giá trị mã vô nghĩa, mọi ý nghĩa nằm ở máy chủ.

## Nhìn hình trả lời

Một trang lưu `role=member` thẳng trong cookie và tin nó ở mỗi yêu cầu. Khách truy cập làm được gì, và có hai cách sửa nào?

<details>
<summary>Xem đáp án</summary>

Khách đổi giá trị thành `role=admin` và trang tin theo, giống lần thử `user=admin` ở trên. Hai cách sửa: cất dữ liệu ở máy chủ và để cookie chỉ mang mã ngẫu nhiên (phải tra bảng, nhưng muốn thu hồi thì xóa phiên); hoặc giữ dữ liệu trong cookie kèm mã xác thực (không tra bảng, sửa là bị từ chối, nhưng vẫn đọc được, và thu hồi sớm một cookie thì phải giữ thêm danh sách ở máy chủ: suy luận của người biên soạn, giống token tự mang thông tin ở [bài sd-14-010](../sd-14-010/lesson.md)).

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn, và thuộc tính cookie</summary>

Bài nguồn nói cookie giúp máy chủ biết danh tính và sở thích mà không cần tra cơ sở dữ liệu. Điều đó chỉ đúng khi cookie mang chính dữ liệu, và với danh tính thì kiểu ấy cần thêm mã xác thực. Ví dụ đăng nhập của MDN dùng cookie mang mã phiên và máy chủ "kiểm mã" đó, nghĩa là phải đối chiếu mã với dữ liệu nó giữ (suy luận của người biên soạn).
Bài nguồn gắn cookie với lúc đăng nhập; MDN liệt kê ba việc: quản lý phiên, cá nhân hóa (ngôn ngữ, giao diện) và theo dõi. MDN còn ghi mỗi cookie thường tối đa khoảng 4 kilôbyte và bị gửi kèm mọi yêu cầu.

Thuộc tính máy chủ có thể đặt (MDN): `Domain` và `Path` quyết định nơi nhận, `Expires` và `Max-Age` quyết định thời hạn, `Secure`, `HttpOnly` và `SameSite` quyết định cách dùng ([bài sd-14-009](../sd-14-009/lesson.md)). Cho mã phiên, OWASP đưa ví dụ `Set-Cookie: __Host-SessionID=<giá trị>; Secure; HttpOnly; SameSite=Strict; Path=/`; MDN ghi tiền tố `__Host-` chỉ bảo đảm được ở trình duyệt hỗ trợ nó. OWASP còn nói ứng dụng không nên chấp nhận mã phiên chưa từng cấp và nên coi đó là dấu hiệu đáng ngờ; máy chủ thử chỉ trả "chưa đăng nhập".

Về thử nghiệm: MDN ghi trình duyệt không cho trang web tự đặt tiêu đề `Cookie` trong `fetch()`, nhưng mặc định người dùng vẫn thấy và sửa được giá trị cookie. Bài này sửa bằng một client Python, chưa thử sửa trong trình duyệt. Mã phiên lấy từ `secrets.token_urlsafe(16)`, mã xác thực tính bằng `hmac` với khóa tạm; bảng phiên nằm trong bộ nhớ, không có hết hạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-a-cookie.md): ví von quán cà phê, cookie giữ danh tính và sở thích.
- MDN (đọc tại commit ghim): [Using HTTP cookies](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/cookies/index.md), [Cookie header](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/reference/headers/cookie/index.md), [Set-Cookie header](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/reference/headers/set-cookie/index.md).
- [OWASP — Session Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Session_Management_Cheat_Sheet.md): mã session tương đương xác thực mạnh nhất, giá trị mã vô nghĩa, mã chưa cấp, thuộc tính và tiền tố; đọc cùng cách.
- Python: [http.cookiejar](https://github.com/python/cpython/blob/cdf010b10c673e1ec4faaf3f8f9be39237986880/Doc/library/http.cookiejar.rst), [secrets](https://github.com/python/cpython/blob/cdf010b10c673e1ec4faaf3f8f9be39237986880/Doc/library/secrets.rst), [hmac](https://github.com/python/cpython/blob/cdf010b10c673e1ec4faaf3f8f9be39237986880/Doc/library/hmac.rst).

Đã đọc nguồn ngày 2026-10-18. Các lần thử dùng Python 3.13, khóa và mã tạm, một lần chạy trên máy biên soạn. Cách chia ba kiểu cookie và các lời bình về ví von quán cà phê là của người biên soạn. Bài viết và hình được thiết kế độc lập.

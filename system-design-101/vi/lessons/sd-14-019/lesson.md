# Session và JWT: hai cách nhớ người đã đăng nhập

**Session và JWT khác nhau ở một quyết định: ai giữ quyền nói “lần đăng nhập này còn hiệu lực”. Với session, máy chủ giữ quyền đó trong một cuốn sổ nên rút lại ngay được. Với JWT, quyền đó nằm sẵn trong tấm thẻ có chữ ký mà người dùng cầm, nên máy chủ khỏi tra sổ nhưng khó rút thẻ trước hạn.**
Bài này dựng cả hai bằng Python (sổ là một `dict`, JWT dùng PyJWT 2.14.0) để xem chỗ khác nhau lộ ra khi đăng xuất, đổi quyền và khi thẻ bị lộ. Cookie, session và token nói chung đã có ở [bài sd-14-008](../sd-14-008/lesson.md), [bài sd-14-009](../sd-14-009/lesson.md) và [bài sd-14-010](../sd-14-010/lesson.md), chuyện đăng nhập ủy quyền ở [bài sd-14-011](../sd-14-011/lesson.md); bài này không lặp lại chúng.

![Bốn khung xếp dọc. Một, hai nơi giữ quyền quyết định: session thì máy chủ giữ sổ và tra sổ mỗi yêu cầu; JWT thì thông tin nằm trong thẻ có chữ ký, máy chủ kiểm chữ ký và hạn. Hai, đăng xuất rồi: session xóa mục trong sổ nên mã cũ bị từ chối; JWT không có sổ để xóa nên bản sao của thẻ vẫn qua tới khi hết hạn. Ba, rút JWT sớm bằng sổ cấm, hạn ngắn hoặc đổi khóa ký, mỗi cách một giá. Bốn, JWT ký thông thường chỉ được ký chứ không bị che; khóa chung thì ai kiểm cũng ký được; nhiều dịch vụ dùng chung một khóa thì còn phải kiểm bên phát hành và bên nhận; OWASP khuyên cookie HttpOnly.](../../diagrams/sd-14-019-main.svg)

## Từ viết tắt

- **JWT** (JSON Web Token) — token web JSON: một chuỗi tự mang thông tin người dùng (tên, vai trò, hạn dùng); bài này nói dạng ký thông thường, có chữ ký, để máy chủ kiểm mà không phải tra sổ.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm các cặp tên và giá trị; phần thông tin của JWT được viết theo định dạng này.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.

## Đọc hình

Các lần thử chạy bằng Python 3.13 và PyJWT 2.14.0, với khóa sinh ngẫu nhiên rồi bỏ; con số là một lần đo trên máy của người biên soạn.

**1 · Hai nơi giữ quyền quyết định.** Session: máy chủ sinh một mã ngẫu nhiên, ghi vào sổ cặp “mã → người dùng, vai trò” rồi đưa mã cho trình duyệt; mỗi yêu cầu sau, máy chủ tra sổ. JWT: máy chủ ghép thông tin (ở đây ba mục: người dùng `sub`, vai trò `role`, hạn `exp`), ký, rồi đưa chuỗi kết quả cho trình duyệt; mỗi yêu cầu sau, máy chủ kiểm chữ ký và hạn rồi đọc thông tin ngay trong chuỗi. Trong các lần thử, một máy chủ vừa phát vừa kiểm thẻ, nên hai việc đó là đủ; khi một khóa phục vụ nhiều bên phát hành hoặc nhiều dịch vụ nhận, OWASP nói bên kiểm còn phải kiểm bên phát hành (`iss`) và bên nhận (`aud`) mong đợi, vì thẻ hợp lệ của dịch vụ này có thể bị đem trình cho dịch vụ khác (xem [bài sd-14-020](../sd-14-020/lesson.md)). Chuỗi đi theo từng yêu cầu nên kích thước có giá: mã session dài 22 byte, JWT ba mục dài 145 byte, gấp khoảng 6,6 lần.

**2 · Đăng xuất rồi, mã cũ còn dùng được không?** Session: xóa mục trong sổ thì mã cũ bị từ chối, y như mã chưa từng phát (đã chạy thử). OWASP cũng yêu cầu máy chủ hủy phiên khi đăng xuất, vì chỉ xóa cookie ở trình duyệt thì không hủy được bản sao của mã đã bị lấy.
JWT: máy chủ không giữ gì nên không có gì để xóa; “đăng xuất” chỉ là trình duyệt quên thẻ. Trong lần thử, một bản sao của thẻ vẫn qua kiểm tra. Quyền cũng vậy: hạ vai trò từ admin xuống member thì sổ session nói ngay member, còn thẻ cũ vẫn ghi admin tới khi hết hạn.

**3 · Rút JWT sớm: ba cách, ba giá.** Sổ cấm: ghi mã định danh `jti` của thẻ vào một tập bị cấm và kiểm ở mỗi yêu cầu; thẻ bị từ chối sau khi cấm (đã chạy thử), nhưng đó lại là một cái sổ. Hạn ngắn: thẻ có `exp` sau 2 giây bị từ chối ở giây thứ 3 (`ExpiredSignatureError`), nhưng không rút được thẻ đang còn hạn (thẻ 900 giây cùng lần chạy vẫn qua). Đổi khóa ký: thẻ cũ đều bị từ chối, của mọi người chứ không riêng ai (cách này do người biên soạn tự thử).

**4 · Cần nhớ về thẻ JWT.** Với JWT ký thông thường, dạng bài này dùng, thẻ chỉ được ký, không bị che: đọc `role` và `exp` không cần khóa, còn sửa `role` thành admin mà giữ chữ ký cũ thì kiểm thất bại (mã hóa ký tự khác mã hóa bảo mật, xem [bài sd-14-002](../sd-14-002/lesson.md)); JWT mã hóa riêng là một dạng khác, nội dung được che, và bài không bàn nó. Về khóa: với bí mật chung, bên phát và bên kiểm cầm cùng một bí mật, nên bên kiểm cũng ký được (trong lần thử, người chỉ có bí mật “để kiểm” tự ký ra thẻ admin và thẻ được nhận); với cặp khóa, chỉ bên phát giữ khóa riêng để ký, bên kiểm cầm khóa công khai (xem [bài sd-14-015](../sd-14-015/lesson.md)). Về nơi đặt thẻ, OWASP nói đừng lưu token hay JWT trong `localStorage` hoặc `sessionStorage`, vì mọi đoạn JavaScript cùng nguồn gốc đều đọc được và một lỗi chèn mã lệnh xuyên trang (cross-site scripting) làm lộ mọi token; nên dùng cookie `HttpOnly; Secure; SameSite=Strict` hoặc mô hình Backend-for-Frontend.

## Giới hạn cần nhớ

Đây là một đánh đổi, không phải bảng xếp hạng, và các lần thử rất nhỏ: một tiến trình, một máy chủ vừa phát vừa kiểm thẻ JWT dạng ký, không có nhiều máy chủ dùng chung kho session, không đo tốc độ, không có trình duyệt thật. Cái được của JWT, “không tra sổ để kiểm”, có thật ở bước kiểm; điều bài chỉ ra là nó hao đi khi phiên đăng nhập cần rút được sớm. OWASP viết rằng dùng JWT cho phiên đăng nhập thì cần một cách hủy phiên, và nếu làm bằng danh sách cấm thì phiên không còn “không lưu trạng thái” hoàn toàn; nó cũng nói JWT còn dùng ở nhiều chỗ khác, mà bài này không bàn.

## Nhìn hình trả lời

Một ứng dụng dùng JWT hạn 15 phút, ghi vai trò admin trong thẻ. Lúc 10:00 quản trị hạ người dùng đó xuống member trong cơ sở dữ liệu. Lúc 10:05 người dùng gửi yêu cầu bằng thẻ cũ. Máy chủ chỉ kiểm chữ ký sẽ làm gì? Muốn hạ quyền có hiệu lực ngay thì phải thêm gì, và với session thì sao?

<details>
<summary>Xem đáp án</summary>

Chữ ký còn đúng và thẻ chưa hết hạn, nên máy chủ chỉ kiểm chữ ký sẽ nhận thẻ và đọc vai trò admin từ chính thẻ; cơ sở dữ liệu không được hỏi (lần thử: sổ session nói member, thẻ cũ vẫn nói admin). Hạ quyền chỉ có hiệu lực khi thẻ hết hạn, tức là tới 15 phút sau.
Muốn có hiệu lực ngay, máy chủ phải giữ thêm trạng thái: cấm `jti` của thẻ (đã chạy thử), hoặc đổi khóa ký (đã chạy thử, nhưng hủy luôn thẻ của mọi người), hoặc tra lại vai trò trong cơ sở dữ liệu ở mỗi yêu cầu thay vì tin thẻ (suy luận của người biên soạn, chưa chạy thử). Với session, sửa mục trong sổ là xong, vì yêu cầu nào cũng đi qua sổ.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn và cách đã chạy thử</summary>

Bài nguồn nói JWT “được ký bằng khóa riêng” và máy chủ “kiểm bằng khóa riêng bí mật”, tức là lẫn hai mô hình. Theo OWASP, chữ ký JWT là chữ ký số bằng cặp khóa hoặc mã xác thực bằng một bí mật chung, tùy giá trị `alg` trong phần đầu của thẻ. Với cặp khóa, khóa riêng chỉ để ký và việc kiểm dùng khóa công khai (trong lần thử, đối tượng khóa công khai không có thao tác `sign`, và thẻ ký bằng một khóa riêng khác bị từ chối). Với bí mật chung thì không có “khóa riêng”, hai bên cùng giữ một bí mật, nên OWASP yêu cầu mỗi cặp (bên phát, bên kiểm) có bí mật riêng, nếu không một bên kiểm có thể giả mạo bên phát.
Bài nguồn nói thông tin trong thẻ “được mã hóa (encoded)”. Với JWT ký thông thường đó là base64url, không che gì (PyJWT cũng ghi rằng nội dung đọc mà không kiểm chữ ký thì không tin được về toàn vẹn và nguồn gốc); OWASP nhắc có dạng JWT mã hóa riêng, bài không bàn.
Bài nguồn nói với JWT “không dùng kho session”: đúng cho việc kiểm, không còn đúng khi cần rút thẻ sớm.
Bài nguồn nói máy chủ tạo session “bằng một khóa bí mật”. Trong lần thử, mã session chỉ là 16 byte ngẫu nhiên, không khóa nào dính vào; OWASP đòi ít nhất 64 bit ngẫu nhiên thật sự, sinh bằng bộ sinh số ngẫu nhiên mật mã.
Bài nguồn nói thẻ đi qua cookie hoặc thân phản hồi, “cả hai đều có ưu nhược điểm”, mà không nêu là gì; OWASP nêu ở phần 4, và ghi thêm rằng `HttpOnly` chỉ chặn việc đọc cookie: nếu lỗi chèn mã lệnh đi kèm giả mạo yêu cầu xuyên trang (cross-site request forgery), yêu cầu gửi từ trang vẫn mang cookie theo.

Cách chạy: một tệp Python, bí mật 32 byte ngẫu nhiên (`HS256`) và cặp khóa P-256 sinh tại chỗ (`ES256`); sổ session là `dict`, sổ cấm là `set`; thẻ có thêm `jti` (bốn mục) dài 179 byte. Chưa làm: đọc các văn bản đặc tả chuẩn (không truy cập được), trình duyệt thật, nhiều máy chủ, đo tốc độ. Tệp “JSON Web Token for Java Cheat Sheet” theo tên cũ không có ở commit đã ghim (trả 404), nên bài đọc “JSON Web Token Cheat Sheet”; tệp đó không nói về nơi đặt thẻ trong trình duyệt, nên phần ấy lấy từ Session Management Cheat Sheet.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what's-the-difference-between-session-based-authentication-and-jwts.md): hai luồng, session và JWT, kèm ví dụ so sánh.
- [OWASP — JSON Web Token Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/JSON_Web_Token_Cheat_Sheet.md): cấu trúc thẻ, chữ ký số và bí mật chung, thẻ ký không che nội dung, sổ cấm theo `jti`, phiên “không lưu trạng thái”. Đọc qua bản tải từ GitHub (raw).
- [OWASP — Session Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Session_Management_Cheat_Sheet.md): mã session ngẫu nhiên, hủy phiên phía máy chủ khi đăng xuất, không lưu token trong `localStorage` hay `sessionStorage`, cookie `HttpOnly`. Đọc qua bản tải từ GitHub (raw).
- [PyJWT — tài liệu sử dụng, bản 2.14.0](https://github.com/jpadilla/pyjwt/blob/c6fe464b356ff4b1ebc9ba62172d331a40aa27df/docs/usage.rst): đọc nội dung không kiểm chữ ký thì không tin được; `exp` quá hạn gây `ExpiredSignatureError`. Đọc qua bản tải từ GitHub (raw).

Đã đọc nguồn ngày 2026-10-18. Cách đặt vấn đề thành một quyết định, hình ẩn dụ “sổ” và “thẻ”, và các lần chạy thử là của người biên soạn. Bài viết và hình được thiết kế độc lập.

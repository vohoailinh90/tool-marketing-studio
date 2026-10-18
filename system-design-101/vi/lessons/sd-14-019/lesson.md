# Session và JWT: hai cách nhớ người đã đăng nhập

**Session và JWT khác nhau ở một quyết định: ai giữ quyền nói “lần đăng nhập này còn hiệu lực”. Với session, máy chủ giữ quyền đó trong một cuốn sổ nên rút lại ngay được. Với JWT, quyền đó nằm sẵn trong tấm thẻ có chữ ký mà người dùng cầm, nên máy chủ khỏi tra sổ nhưng khó rút thẻ trước hạn.**
Bài này dựng cả hai bằng Python (sổ là một `dict` trong bộ nhớ, JWT dùng PyJWT 2.14.0) để xem chỗ khác nhau lộ ra khi đăng xuất, đổi quyền và khi thẻ bị lộ. Cookie, session và token nói chung đã có ở [bài sd-14-008](../sd-14-008/lesson.md), [bài sd-14-009](../sd-14-009/lesson.md) và [bài sd-14-010](../sd-14-010/lesson.md), OAuth ở [bài sd-14-011](../sd-14-011/lesson.md); bài này không lặp lại chúng.

![Bốn khung xếp dọc. Một, hai nơi giữ quyền quyết định: session thì máy chủ giữ sổ và tra sổ mỗi yêu cầu; JWT thì thông tin nằm trong thẻ có chữ ký, máy chủ chỉ kiểm chữ ký và hạn. Hai, đăng xuất rồi: session xóa mục trong sổ nên mã cũ bị từ chối; JWT không có sổ để xóa nên bản sao của thẻ vẫn qua tới khi hết hạn. Ba, rút JWT sớm bằng sổ cấm, hạn ngắn hoặc đổi khóa ký, mỗi cách một giá. Bốn, thẻ chỉ được ký chứ không bị che; khóa chung thì ai kiểm cũng ký được; OWASP khuyên cookie HttpOnly.](../../diagrams/sd-14-019-main.svg)

## Từ viết tắt

- **JWT** (JSON Web Token) — token web JSON: một chuỗi tự mang thông tin người dùng (tên, vai trò, hạn dùng) và có chữ ký, để máy chủ kiểm mà không phải tra sổ.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm các cặp tên và giá trị; phần thông tin của JWT được viết theo định dạng này.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.

## Đọc hình

Mọi lần thử chạy bằng Python 3.13 và PyJWT 2.14.0, trong một tiến trình, với khóa sinh ngẫu nhiên rồi bỏ. Con số là một lần đo trên máy của người biên soạn.

**1 · Hai nơi giữ quyền quyết định.** Session: khi đăng nhập, máy chủ sinh một mã ngẫu nhiên (16 byte, viết ra thành 22 ký tự), ghi vào sổ cặp “mã → người dùng, vai trò” rồi đưa mã cho trình duyệt. Mỗi yêu cầu sau, máy chủ tra sổ. JWT: máy chủ ghép thông tin (ở đây ba mục: người dùng `sub`, vai trò `role`, hạn `exp`), ký, rồi đưa chuỗi kết quả cho trình duyệt. Mỗi yêu cầu sau, máy chủ chỉ kiểm chữ ký và hạn rồi đọc thông tin ngay trong chuỗi.
Chuỗi đi theo từng yêu cầu nên kích thước có giá: mã session dài 22 byte, JWT ba mục dài 145 byte, gấp khoảng 6,6 lần (một lần đo, tùy cách chọn). Đổi lại, session cần chỗ lưu và một lần tra sổ cho mỗi yêu cầu.

**2 · Đăng xuất rồi, mã cũ còn dùng được không?** Session: xóa mục trong sổ thì mã cũ bị từ chối, y như mã chưa từng phát (đã chạy thử). OWASP cũng yêu cầu máy chủ chủ động hủy phiên khi hết hạn hoặc đăng xuất, vì chỉ xóa cookie ở trình duyệt thì không hủy được bản sao của mã đã bị lấy.
JWT: máy chủ không giữ gì nên không có gì để xóa, “đăng xuất” chỉ là trình duyệt quên thẻ. Trong lần thử, một bản sao của thẻ vẫn qua kiểm tra. Quyền cũng vậy: sau khi hạ vai trò từ admin xuống member, sổ session nói ngay member, còn thẻ JWT cũ vẫn ghi admin tới khi hết hạn. OWASP viết rằng dùng JWT cho phiên đăng nhập thì phải có cách hủy phiên; làm bằng danh sách cấm thì phiên không còn “không lưu trạng thái” hoàn toàn, và nên cân nhắc hệ thống session thông thường.

**3 · Rút JWT sớm: ba cách, ba giá.**
- Sổ cấm: thêm mã định danh `jti` của thẻ vào một tập bị cấm, kiểm ở mỗi yêu cầu. Thẻ có `jti` (bốn mục, 179 byte) qua trước khi cấm và bị từ chối sau đó; nhưng đó lại là một cái sổ. OWASP cảnh báo đừng dùng chính chuỗi thẻ hay bản băm của nó làm khóa sổ cấm, vì thẻ có thể có dạng khác mà vẫn qua kiểm chữ ký; nên dùng `jti` kèm `iss` (bên phát thẻ).
- Hạn ngắn: thẻ có `exp` sau 2 giây bị từ chối khi kiểm ở giây thứ 3 (`ExpiredSignatureError`). OWASP nêu hạn ngắn để giảm việc dùng lại thẻ, nhưng nó không rút được thẻ đang còn hạn: thẻ 900 giây cùng lần chạy vẫn qua.
- Đổi khóa ký: thẻ cũ bị từ chối (`InvalidSignatureError`), và thẻ của mọi người cũng vậy. Cách này do người biên soạn tự thử, OWASP không nêu.

**4 · Cần nhớ về thẻ JWT.**
- Thẻ chỉ được ký, không bị che. Đọc `role` và `exp` không cần khóa; sửa `role` thành admin mà giữ chữ ký cũ thì kiểm thất bại (`InvalidSignatureError`). OWASP: JWT ký bảo đảm toàn vẹn và nguồn gốc, không bảo đảm bí mật; nội dung chỉ là base64url (mã hóa ký tự khác mã hóa bảo mật, xem [bài sd-14-002](../sd-14-002/lesson.md)).
- Ai giữ khóa nào. Ký bằng bí mật chung: bên phát và bên kiểm cầm cùng một bí mật, nên bên kiểm cũng ký được; trong lần thử, người chỉ có bí mật “để kiểm” tự ký ra thẻ admin và thẻ được nhận. Ký bằng cặp khóa: bên phát giữ khóa riêng để ký, bên kiểm chỉ cần khóa công khai; trong lần thử, đối tượng khóa công khai không có thao tác `sign` và thẻ ký bằng khóa riêng khác bị từ chối (xem [bài sd-14-015](../sd-14-015/lesson.md)). OWASP: với bí mật chung, mỗi cặp (bên phát, bên kiểm) phải có bí mật riêng, nếu không một bên kiểm có thể giả mạo bên phát.
- Thẻ nằm ở đâu trong trình duyệt. OWASP: đừng lưu token xác thực, mã session hay JWT trong `localStorage` hoặc `sessionStorage`, vì mọi đoạn JavaScript cùng nguồn gốc đều đọc được, nên một lỗi chèn mã lệnh xuyên trang (cross-site scripting) làm lộ mọi token; nên dùng cookie `HttpOnly; Secure; SameSite=Strict` hoặc mô hình Backend-for-Frontend. `HttpOnly` chỉ chặn việc đọc cookie: kẻ tấn công không mang cookie đi dùng nơi khác, nhưng khi mã của họ còn chạy trong trang thì trình duyệt vẫn gửi cookie kèm yêu cầu.

## Giới hạn cần nhớ

Đây là một đánh đổi, không phải bảng xếp hạng, và các lần thử rất nhỏ: một tiến trình, không có nhiều máy chủ dùng chung kho session, không đo tốc độ, không có trình duyệt thật, không có cách cấp lại thẻ. Cái được của JWT, “không tra sổ để kiểm”, có thật ở bước kiểm; điều bài chỉ ra là cái được ấy hao đi khi phiên đăng nhập của người dùng cần rút được sớm. OWASP ghi cách dùng JWT cho phiên “không lưu trạng thái” là bị không tán thành (frowned upon), và nêu JWT còn dùng ở nhiều chỗ khác, nơi lập luận này không áp dụng nguyên vẹn; bài không bàn những chỗ ấy.

## Nhìn hình trả lời

Một ứng dụng dùng JWT hạn 15 phút, ghi vai trò admin trong thẻ. Lúc 10:00 quản trị hạ người dùng đó xuống member trong cơ sở dữ liệu. Lúc 10:05 người dùng gửi yêu cầu bằng thẻ cũ. Máy chủ chỉ kiểm chữ ký sẽ làm gì? Muốn hạ quyền có hiệu lực ngay thì phải thêm gì, và với session thì sao?

<details>
<summary>Xem đáp án</summary>

Chữ ký còn đúng và thẻ chưa hết hạn, nên máy chủ chỉ kiểm chữ ký sẽ nhận thẻ và đọc vai trò admin từ chính thẻ; cơ sở dữ liệu không được hỏi (lần thử: sổ session nói member, thẻ cũ vẫn nói admin). Hạ quyền chỉ có hiệu lực khi thẻ hết hạn, tức là tới 15 phút sau.
Muốn có hiệu lực ngay, máy chủ phải giữ thêm trạng thái: cấm `jti` của thẻ (đã chạy thử), hoặc đổi khóa ký (đã chạy thử, nhưng hủy luôn thẻ của mọi người), hoặc tra lại vai trò trong cơ sở dữ liệu ở mỗi yêu cầu thay vì tin thẻ (suy luận của người biên soạn, chưa chạy thử). Với session, sửa mục trong sổ là xong, vì yêu cầu nào cũng đi qua sổ.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn và cách đã chạy thử</summary>

Bài nguồn nói JWT “được ký bằng khóa riêng” và máy chủ “kiểm bằng khóa riêng bí mật”, tức là lẫn hai mô hình. Theo OWASP, chữ ký JWT là chữ ký số bằng cặp khóa hoặc mã xác thực bằng một bí mật chung, tùy giá trị `alg` trong phần đầu của thẻ. Với cặp khóa, khóa riêng chỉ để ký và việc kiểm dùng khóa công khai; với bí mật chung thì không có “khóa riêng”, hai bên cùng giữ một bí mật. Không trường hợp nào dùng khóa riêng để kiểm.
Bài nguồn nói thông tin trong thẻ “được mã hóa (encoded)”. Với JWT ký thông thường đó là base64url, không che gì; PyJWT ghi rằng nội dung đọc mà không kiểm chữ ký thì không tin được về toàn vẹn và nguồn gốc. OWASP nhắc có dạng JWT mã hóa riêng, bài không bàn.
Bài nguồn nói với JWT “không dùng kho session”. Đúng cho việc kiểm; không còn đúng khi cần rút thẻ sớm (phần 2 và 3).
Bài nguồn nói máy chủ tạo session “bằng một khóa bí mật”. Trong lần thử, mã session chỉ là 16 byte ngẫu nhiên, không khóa nào dính vào; OWASP đòi ít nhất 64 bit ngẫu nhiên thật sự, sinh bằng bộ sinh số ngẫu nhiên mật mã.
Bài nguồn nói thẻ đi qua cookie hoặc thân phản hồi và “cả hai đều có ưu nhược điểm” mà không nêu là gì; OWASP nêu ở phần 4. Ví dụ vé máy bay của bài nguồn không được dùng lại.

Cách chạy: một tệp Python, `python3 -I`, ký bằng bí mật 32 byte ngẫu nhiên (`HS256`) và cặp khóa P-256 sinh tại chỗ (`ES256`), đều bỏ đi; sổ session là `dict`, sổ cấm là `set`. Chưa làm: đọc RFC (không truy cập được; chỉ nhắc qua OWASP), thử trên trình duyệt thật, nhiều máy chủ, đo tốc độ. Tệp “JSON Web Token for Java Cheat Sheet” theo tên cũ không có ở commit đã ghim (trả 404), nên bài đọc “JSON Web Token Cheat Sheet”. Tệp đó chỉ nhắc “browser storage” trong một câu, nên phần nơi đặt thẻ lấy từ Session Management Cheat Sheet.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what's-the-difference-between-session-based-authentication-and-jwts.md): hai luồng, session và JWT, kèm ví dụ so sánh.
- [OWASP — JSON Web Token Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/JSON_Web_Token_Cheat_Sheet.md): cấu trúc thẻ, chữ ký số và bí mật chung, thẻ ký không che nội dung, sổ cấm theo `jti`, phiên “không lưu trạng thái”. Đọc qua bản tải từ GitHub (raw).
- [OWASP — Session Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Session_Management_Cheat_Sheet.md): mã session ngẫu nhiên, hủy phiên phía máy chủ khi đăng xuất, không lưu token trong `localStorage` hay `sessionStorage`, cookie `HttpOnly`. Đọc qua bản tải từ GitHub (raw).
- [PyJWT — tài liệu sử dụng, bản 2.14.0](https://github.com/jpadilla/pyjwt/blob/c6fe464b356ff4b1ebc9ba62172d331a40aa27df/docs/usage.rst): đọc nội dung không kiểm chữ ký thì không tin được; `exp` quá hạn gây `ExpiredSignatureError`. Đọc qua bản tải từ GitHub (raw).

Đã đọc nguồn ngày 2026-10-18. Cách đặt vấn đề thành một quyết định, hình ẩn dụ “sổ” và “thẻ”, và các lần chạy thử là của người biên soạn. Bài viết và hình được thiết kế độc lập.

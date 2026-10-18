# Cookie, session, JWT và PASETO: chọn cách xác thực nào?

**PASETO bỏ đi một thứ của JWT: người gửi token không còn được tự chọn thuật toán. Nó không bỏ những việc khó của mọi token tự mang dữ liệu: thu hồi trước hạn, kiểm hạn dùng, giữ khóa và chọn chỗ cất token.** Vì vậy, chọn cách xác thực nào nên bắt đầu từ câu hỏi "tôi có cần thu hồi ngay không?", chứ không phải từ tên định dạng.

Bài này không dạy lại cookie, session và token: xem [bài sd-14-008](../sd-14-008/lesson.md), [bài sd-14-009](../sd-14-009/lesson.md) và [bài sd-14-010](../sd-14-010/lesson.md); ủy quyền và đăng nhập một lần ở [bài sd-14-011](../sd-14-011/lesson.md). Bài chỉ hỏi PASETO đổi gì so với JWT và không đổi gì, qua các lần chạy thử cục bộ với `pyseto` 1.10.0 và PyJWT 2.14.0, dùng khóa tạm.

![Ba nhóm xếp dọc. Nhóm một, ba cách xác thực: cookie với session giữ dữ liệu ở máy chủ nên xóa bản ghi là thu hồi được; JWT tự mang dữ liệu và có trường alg do người gửi viết nên người kiểm phải ghim thuật toán; PASETO không có trường alg, tiền tố phiên bản và mục đích chọn một bộ thuật toán cố định. Nhóm hai, hai loại PASETO v4: local che dữ liệu bằng khóa chung, public cho mọi người đọc dữ liệu và kiểm chữ ký bằng khóa công khai. Nhóm ba, việc bạn vẫn phải tự lo khi dùng PASETO: thu hồi và chống dùng lại, kiểm hạn dùng, giữ khóa và chọn chỗ cất token.](../../diagrams/sd-14-023-main.svg)

## Từ viết tắt

- **PASETO** (Platform-Agnostic SEcurity TOkens) — token bảo mật không phụ thuộc nền tảng: định dạng token tự mang dữ liệu, trong đó phiên bản và mục đích của token chọn sẵn bộ thuật toán.
- **JWT** (JSON Web Token) — token web JSON: định dạng token tự mang dữ liệu và chữ ký, có phần header do người gửi viết, trong đó trường `alg` nêu thuật toán.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm các cặp tên và giá trị; JWT dùng nó cho header và payload, PASETO dùng nó cho dữ liệu.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.

## Đọc hình

**Cookie và session.** Cookie chỉ mang một mã; ý nghĩa của mã nằm trong kho session ở máy chủ (OWASP). Máy chủ giữ dữ liệu nên muốn thu hồi chỉ cần xóa bản ghi. Cái giá là phải giữ kho đó, và khi có nhiều máy chủ thì chúng phải dùng chung kho (hiểu biết chung của người biên soạn, bài không đo). OWASP còn khuyên cân nhắc session thông thường thay cho JWT làm session, vì danh sách thu hồi làm session không còn "không trạng thái".

**JWT.** Header và payload của JWT chỉ là base64url: không cần khóa vẫn đọc ra `{"alg":"HS256","typ":"JWT"}` và thông tin người dùng. Header do người gửi viết, nên `alg` là lời người gửi tự khai; người kiểm phải tự khai danh sách thuật toán mình chấp nhận. PyJWT 2.14.0 buộc điều đó: gọi `decode` mà quên `algorithms` thì báo lỗi. Token `alg: none` bị từ chối trong cả bốn cách khai tôi thử, kể cả khi tự ghi `none` vào danh sách. Token `HS256` ký bằng khóa công khai của hệ `RS256` cũng bị từ chối, với cả hai cách viết khóa tôi thử. Vậy JWT dùng đúng, trên thư viện đã vá, không dính các lỗi nhầm thuật toán này. OWASP nói lỗi `none` nay đã được sửa, nhưng vẫn nêu lỗi nhầm loại khóa ở những thư viện cụ thể (có PyJWT ở bản cũ): an toàn nằm ở thư viện và cách cấu hình, không nằm ở định dạng.

**PASETO.** Token có ba đoạn ngăn bằng dấu chấm (thêm footer tùy chọn ở cuối): phiên bản (`v4`), mục đích (`local` hoặc `public`), rồi dữ liệu. Không có header JSON, không có trường thuật toán. Mỗi cặp phiên bản và mục đích là một bộ thuật toán cố định do đặc tả định sẵn; ví dụ `v4.public` dùng chữ ký `Ed25519`.

- `v4.local` mã hóa bằng khóa chung. Khi chạy thử, phần dữ liệu dài 132 byte (32 byte số dùng một lần, 68 byte dữ liệu mã hóa, 32 byte nhãn xác thực) và không tìm thấy chữ `alice` trong đó.
- `v4.public` ký bằng khóa riêng. Không cần khóa vẫn đọc ra `{"sub": "alice", "role": "user", ...}`; 64 byte cuối là chữ ký.

Sửa một ký tự (thử ở cả hai loại), sửa `role` thành `admin` mà giữ chữ ký cũ, hoặc đổi footer: cả bốn lần thử đều bị từ chối.

**Người gửi vẫn chọn được gì?** Chỉ tiền tố. Nhưng khóa trong tay người kiểm gắn với đúng một phiên bản và một mục đích. Đổi tiền tố thành `v2.public`, hoặc đưa token `local` cho bên chỉ giữ khóa công khai, đều cho lỗi "key is not found". Kẻ biết khóa công khai dùng chính các byte của nó làm khóa `local` để tạo token `v4.local` cũng bị bên giữ khóa công khai từ chối. Đặc tả gọi tính chất này là Algorithm Lucidity và yêu cầu thư viện không để khóa công khai tạo ra token `local` mà thư viện chấp nhận. Đó là quy tắc cho người viết thư viện; đặc tả cũng nói thiếu nó tự thân chưa phải lỗ hổng, nhưng có thể mở đường tấn công.

## Giới hạn cần nhớ

Bốn việc vẫn là của bạn; các lần chạy thử cho thấy chúng không tự biến mất.

- **Thu hồi.** Chữ ký không biết "đăng xuất". Một token `v4.public` còn hạn được giải mã thành công hai lần liên tiếp; thư viện chỉ có token và khóa, không có danh sách nào của ứng dụng. Tài liệu của chính PASETO nói cả JWT lẫn PASETO không được thiết kế để quản lý session không trạng thái, và PASETO không tự chống được tấn công phát lại.
- **Hạn dùng.** `exp` chỉ là một trường trong dữ liệu; có kiểm hay không là việc của thư viện và cách gọi. Với `pyseto` 1.10.0, token có `exp` cách đây một giờ vẫn được chấp nhận khi gọi `decode` không kèm `deserializer`, và bị từ chối ("Token expired.") khi kèm `deserializer=json`. PyJWT kiểm `exp` theo mặc định. Đó là hành vi của hai thư viện, không phải kết luận về hai định dạng.
- **Khóa.** Ai có khóa `local` vừa đọc vừa tạo được token (thử: token tạo bằng bản sao của khóa được chấp nhận). Đặc tả đặt mã khóa `kid` ở footer để chọn khóa khi đổi khóa. Footer không mã hóa nên đọc được không cần khóa (đã thử); đặc tả dặn không tin footer trước khi kiểm token, và không nhận khóa công khai do chính token mang theo.
- **Chỗ cất token.** Định dạng không quyết định token nằm ở đâu. OWASP dặn không cất mã session trong `localStorage` vì JavaScript đọc được, còn cookie có `HttpOnly` giảm rủi ro đó (xem [bài sd-14-009](../sd-14-009/lesson.md)); token dùng thay mã session chịu cùng rủi ro (suy luận của người biên soạn).

## Nhìn hình trả lời

Một nhóm đổi từ JWT sang `v4.public` vì nghe rằng PASETO "loại bỏ lỗ hổng thuật toán". Sau đó một nhân viên nghỉ việc và nhóm muốn chặn token của người này ngay. Việc đổi định dạng giúp được gì, và còn phải làm gì?

<details>
<summary>Xem đáp án</summary>

Không giúp gì cho việc này. Chữ ký vẫn hợp lệ cho tới khi token hết hạn, và thư viện không tra danh sách nào. Đổi định dạng chỉ bỏ trường `alg`. Muốn chặn ngay, ứng dụng phải tự thêm một thứ: danh sách thu hồi kiểm ở mỗi yêu cầu (mất một phần tính không trạng thái), hoặc đổi khóa (vô hiệu luôn mọi token ký bằng khóa đó), hoặc quay về session ở máy chủ, nơi xóa một bản ghi là xong. Hạn ngắn kèm cấp lại chỉ thu hẹp thời gian một token bị lộ còn dùng được về sau; nó không chặn token đang có.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn nói PASETO cải thiện JWT bằng mặc định mật mã mạnh hơn, loại bỏ lỗ hổng thuật toán và tránh rủi ro cấu hình sai. Bài này giữ phần đúng: đặc tả cố định bộ thuật toán theo phiên bản và token không có trường thuật toán. Phần còn lại là nói quá hoặc chưa kiểm được. "Mạnh hơn" bài không đo, và lời so sánh nằm trong tài liệu của chính nhóm viết PASETO; ba trang OWASP đã đọc không nhắc tới PASETO (tôi tìm chữ "paseto", không thấy). "Loại bỏ" quá mạnh vì an toàn còn phụ thuộc việc thư viện tách loại khóa. "Tránh cấu hình sai" không đúng với hạn dùng không được kiểm, khóa bị lộ hay footer được tin quá sớm.

So `v4.local` (che dữ liệu) với JWT đã ký (không che dữ liệu, theo OWASP) là so hai thứ khác loại; JWT có dạng mã hóa riêng, bài không bàn. Bài nguồn cũng không nói PASETO có nhiều phiên bản: `v1` và `v3` dùng thuật toán theo chuẩn của Mỹ, `v2` và `v4` thuộc họ dùng thư viện libsodium, và đặc tả ghi `v1` chỉ nên dùng cho hệ thống cũ.

README của `pyseto` ghi thư viện chưa được kiểm toán chính thức; bài này không đánh giá chất lượng thư viện nào. Mọi kết quả chạy thử là một lần chạy trên máy biên soạn, với khóa tạm sinh ngẫu nhiên.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cookies-vs-sessions-vs-jwt-vs-paseto.md).
- PASETO, đọc qua kho GitHub: [README](https://github.com/paseto-standard/paseto-spec/blob/af79f25908227555404e7462ccdd8ce106049469/README.md), [các phiên bản giao thức](https://github.com/paseto-standard/paseto-spec/blob/af79f25908227555404e7462ccdd8ce106049469/docs/01-Protocol-Versions/README.md), [Version 4](https://github.com/paseto-standard/paseto-spec/blob/af79f25908227555404e7462ccdd8ce106049469/docs/01-Protocol-Versions/Version4.md), [Payload Processing](https://github.com/paseto-standard/paseto-spec/blob/af79f25908227555404e7462ccdd8ce106049469/docs/02-Implementation-Guide/01-Payload-Processing.md), [Algorithm Lucidity](https://github.com/paseto-standard/paseto-spec/blob/af79f25908227555404e7462ccdd8ce106049469/docs/02-Implementation-Guide/03-Algorithm-Lucidity.md).
- OWASP, đọc qua kho GitHub: [JSON Web Token Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/JSON_Web_Token_Cheat_Sheet.md), [Session Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Session_Management_Cheat_Sheet.md), [HTML5 Security Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/HTML5_Security_Cheat_Sheet.md).
- [PyJWT — tài liệu sử dụng](https://github.com/jpadilla/pyjwt/blob/16231abfd1d8eab4953e8779b3017b859c88565e/docs/usage.rst): `exp` được kiểm tự động.
- [pyseto — README](https://github.com/dajiaji/pyseto/blob/a948711de5fe46375a9e004d5c0b7b93c47415cf/README.md): cách dùng ở bản 1.10.0; ghi chú chưa kiểm toán.

Đã đọc nguồn ngày 2026-10-18. Các lần chạy thử dùng `pyseto` 1.10.0 trong một môi trường ảo riêng và PyJWT 2.14.0 trên Python 3.13; không có tài liệu RFC nào được mở (trang RFC không truy cập được). Cách đặt câu hỏi "PASETO đổi gì và không đổi gì", thứ tự các mục và đoạn tóm tắt về cookie và session là của người biên soạn. Bài viết và hình được thiết kế độc lập.

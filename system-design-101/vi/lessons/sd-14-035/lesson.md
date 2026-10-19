# OAuth 2.0 bằng lời đơn giản: token làm được gì và không làm được gì

**Access token của OAuth 2.0 giống một tấm vé ghi sẵn (trong token, hoặc ở máy chủ ủy quyền): được làm việc gì (scope), dùng cho API nào (audience), đến lúc nào (exp). Nó cho ứng dụng gọi API mà không cần mật khẩu của bạn, nhưng tự nó không chứng minh bạn vừa đăng nhập, và với token loại bearer, loại bài này dùng, ai cầm nó cũng dùng được.**
Bài này nói về token đã có trong tay: máy chủ API kiểm gì, token không nói được gì. Đăng nhập khác ủy quyền thế nào xem [bài sd-14-011](../sd-14-011/lesson.md); cách xin được token không thuộc bài này.

![Ba khung dọc. Khung một, bốn phép thử của thí nghiệm trên một access token JWT: chữ ký đúng; còn hạn exp, quá hạn thì trả 401; audience, cấp cho API khác thì trả 401; scope, thiếu quyền thì trả 403. Khung hai, danh sách này chưa đủ cho mọi token: bộ kiểm JWT còn kiểm bên phát hành và loại token, còn token chuỗi mờ thì API hỏi máy chủ ủy quyền. Khung ba, token không làm được ba việc: chứng minh đăng nhập, việc đó cần ID token của OpenID Connect; cho biết ai đang cầm, vì ai có chuỗi token cũng dùng được; tự nâng quyền, vì sửa nội dung là hỏng chữ ký.](../../diagrams/sd-14-035-main.svg)

## Từ viết tắt

- **OAuth** (Open AUTHorization) — chuẩn ủy quyền mở: cho ứng dụng làm một số việc thay bạn mà không biết mật khẩu của bạn.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình gọi chức năng của chương trình khác; ở đây là máy chủ giữ hồ sơ người dùng.
- **JWT** (JSON Web Token) — token web dạng JSON: một chuỗi chữ mang vài thông tin và có chữ ký.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: văn bản gồm các cặp tên và giá trị.
- **ID** (IDentity) — danh tính: ID token mang danh tính người dùng.
- **OpenID** (Open IDentity) — chuẩn xác thực mở; OpenID Connect là lớp xác thực xây trên OAuth.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng về bảo mật ứng dụng, có các hướng dẫn bài dùng để đối chiếu.

## Đọc hình

Các lần thử chạy trên máy cục bộ, với Python 3.13 và `authlib` 1.9.1, gồm một máy chủ ủy quyền và một máy chủ API thu nhỏ. Máy chủ ủy quyền ký access token dạng JWT bằng khóa riêng; máy chủ API chỉ giữ khóa công khai (xem [bài sd-14-015](../sd-14-015/lesson.md)) và dùng bộ kiểm JWT của `authlib`. Tên API và scope do tôi đặt. Đây là một lần chạy trên máy biên soạn; hai lần chạy thêm cho cùng mã trạng thái. Thứ tự bốn câu hỏi là cách xếp của tôi: thư viện kiểm chữ ký, rồi `exp` và `aud`, rồi scope. Đây là bốn phép thử của thí nghiệm này, không phải danh sách kiểm đầy đủ: bộ kiểm JWT của `authlib` còn kiểm bên phát hành (`iss`), loại token (`typ`) và vài claim khác (đọc mã nguồn), còn token chuỗi mờ không có chữ ký để kiểm: API hỏi máy chủ ủy quyền (introspection, xem phần sau).

**1 · Chữ ký.** Sửa scope từ `read_photos` thành `read_profile` trong token nhưng giữ chữ ký cũ: bị 401, thư viện báo chữ ký sai. Token khai thuật toán `none` (không ký) cũng bị 401. Ứng dụng giữ token không tự nâng quyền được.

**2 · Hạn.** Token hạn 1 giây: gọi ngay thì được 200, sau 2,5 giây bị 401, thư viện báo hết hạn. Bản nháp OAuth 2.1 nói access token có hạn ngắn để giảm thiệt hại khi lộ.

**3 · Audience.** Token cấp cho `photos-api` đưa vào `profile-api`: bị 401, báo `aud` không khớp. Bản nháp OAuth 2.1 và OWASP nói access token nên dành cho một máy chủ API, và máy chủ API phải kiểm ở mỗi yêu cầu rằng token là của mình.

**4 · Scope.** Token chỉ có `read_photos` gọi hồ sơ: bị 403 `insufficient_scope`. Token có `read_profile`: được 200 và chỉ nhận tên; thêm `read_email` thì nhận thêm email. Scope chỉ là chữ do máy chủ ủy quyền đặt; máy chủ API đọc nó rồi quyết định trả phần nào. Theo chú thích trong `authlib`, 401 dành cho token không hợp lệ (hết hạn, bị thu hồi...), 403 cho yêu cầu cần quyền cao hơn token có.

**Mật khẩu ở đâu?** Người dùng chỉ nhập mật khẩu ở máy chủ ủy quyền. Quét mọi thông điệp của cả lần chạy: cả 9 thông điệp đăng nhập chứa chuỗi mật khẩu, 0 trên 31 thông điệp còn lại (đổi mã lấy token, gọi API, hỏi introspection) chứa nó, và 7 JWT đã cấp (kể cả ID token) cũng không có nó. Bản nháp OAuth 2.1 nói thông tin đăng nhập của chủ tài nguyên không bao giờ được chia sẻ với ứng dụng.

**Token không nói ai.** Token JWT trong thử nghiệm có `sub` (mã người dùng `u-1001`) nhưng không có tên hay email. Token chuỗi mờ (43 ký tự ngẫu nhiên) không chứa gì: máy chủ API hỏi máy chủ ủy quyền và nhận `active`, `client_id`, `scope`, `aud`, `exp`, `iat`; `sub` chỉ có khi máy chủ thu nhỏ được đặt để thêm. Bản nháp OAuth 2.1 còn nói ứng dụng không được trông đợi đọc được access token. Muốn ứng dụng biết người dùng là ai, OpenID Connect thêm một ID token cho ứng dụng tự kiểm; ID token cho biết người dùng là ai chứ chưa chứng tỏ họ vừa đăng nhập, vì nhà cung cấp có thể dùng lại phiên đăng nhập cũ: muốn kiểm độ mới của lần đăng nhập thì ứng dụng yêu cầu `max_age` và kiểm `auth_time` (mã nguồn `authlib` bắt buộc có `auth_time` khi có yêu cầu `max_age`; bài không chạy thử phần này). Với lớp `CodeIDToken` của `authlib`: đúng `nonce` (giá trị ngẫu nhiên ứng dụng gửi đi, phải nhận lại nguyên vẹn) thì hợp lệ, sai thì bị từ chối; access token đem kiểm như ID token bị từ chối vì `aud`; ID token đem gọi API bị 401 (thư viện báo `typ`).

## Giới hạn cần nhớ

Đây là token loại bearer: ai cầm chuỗi token đều dùng được. Một chương trình khác gửi đúng chuỗi ấy và nhận 200: máy chủ API không phân biệt được người gửi. Bản nháp OAuth 2.1 định nghĩa bearer đúng thế. OWASP nói nên giới hạn audience để giảm thiệt hại khi token lộ, nhắc tới token gắn với khóa của ứng dụng (bài không thử), và khuyên không để token trong `localStorage` hay `sessionStorage`, nơi mã JavaScript nào của trang cũng đọc được. `authlib` nói JWT mà máy chủ không lưu thì không thu hồi được (xem [bài sd-14-010](../sd-14-010/lesson.md)).

## Nhìn hình trả lời

Hai API dùng chung một máy chủ ủy quyền. Kẻ lấy được token `read_photos` của API ảnh đem gọi API hồ sơ thì có được không, và API hồ sơ phải kiểm gì?

<details>
<summary>Xem đáp án</summary>

Nếu API hồ sơ hỏi đủ bốn câu thì bị từ chối: audience là của API ảnh (câu 3) và scope thiếu `read_profile` (câu 4). Trong thử nghiệm, token chuỗi mờ cấp cho `photos-api` mang scope `read_profile` vẫn được API hồ sơ nhận (200) khi dùng lớp kiểm introspection mặc định của `authlib` 1.9.1, vì lớp này chỉ kiểm `active` và scope (đọc mã nguồn, chạy thử); thêm một bước kiểm `aud` thì token đó bị 401. Scope chỉ là chữ: hai API dùng cùng tên scope thì scope không phân biệt được chúng, nên mỗi API phải tự kiểm audience.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn gọi ba thực thể là User, Server và Identity Provider. OWASP, bản nháp OAuth 2.1 và `authlib` dùng bốn vai: chủ tài nguyên (thường là người dùng), ứng dụng, máy chủ ủy quyền và máy chủ API. Tài liệu `authlib` vẽ “OpenID Provider” là máy chủ ủy quyền; “Identity Provider” không phải một vai OAuth trong ba tài liệu đó.

Bài nguồn nói token đại diện cho danh tính và quyền của bạn, và làm được đăng nhập một lần. Bản nháp OAuth 2.1 nói access token đại diện cho quyền đã cấp cho ứng dụng, OAuth không phải giao thức xác thực; OWASP mô tả OpenID Connect là lớp danh tính xây trên OAuth 2.0.

Bài nguồn nói token chia sẻ quyền qua nhiều hệ thống. Một máy chủ ủy quyền có thể cấp token cho nhiều API, nhưng mỗi token nên dành cho một API (phép thử audience). Bài nguồn nói ứng dụng xem được phần hồ sơ bạn cho phép: thực tế là scope do máy chủ ủy quyền đặt và máy chủ API thực thi.

Các văn bản chuẩn gốc của OAuth và đặc tả OpenID Connect không đọc được ở đây, nên điều về chúng chỉ dựa vào bản nháp OAuth 2.1, OWASP và `authlib`.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/oauth-2-explained-with-siple-terms.md): ba thực thể và ba việc token làm được.
- [OAuth 2.1 — bản nháp](https://github.com/oauth-wg/oauth-v2-1/blob/d04b368313c8835a930a2e55a68ef547312b7b32/draft-ietf-oauth-v2-1.md): vai trò, access token, scope, bearer, audience; OAuth không phải giao thức xác thực.
- [OWASP — OAuth 2.0 Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/OAuth2_Cheat_Sheet.md) và [Session Management](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Session_Management_Cheat_Sheet.md): audience, lớp danh tính, `localStorage`.
- [authlib — tài liệu introspection](https://github.com/authlib/authlib/blob/8a308fc39c378c1090608903a09318a4267f418a/docs/oauth2/specs/rfc7662.rst), cùng `docs/oauth2/concepts.rst`, `docs/oauth2/specs/rfc9068.rst` và `authlib/oidc/core/claims.py` ở cùng commit. Các lần thử chạy với `authlib` 1.9.1 từ PyPI.

Đã đọc nguồn ngày 2026-10-18. Máy chủ ủy quyền và máy chủ API thu nhỏ, bộ thử và cách xếp bốn câu hỏi trong hình là của người biên soạn. Bài viết và hình được thiết kế độc lập.

# SSO và OAuth 2.0: đăng nhập khác ủy quyền

**OAuth 2.0 trả lời “ứng dụng này được phép làm gì thay tôi”, còn đăng nhập một lần (SSO) trả lời “tôi là ai” cho nhiều ứng dụng.**
Hai việc hay bị gộp làm một, và gộp nhầm là nguồn của nhiều lỗi thiết kế.

![Tám thẻ xếp dọc. Thẻ đầu: hai câu hỏi khác nhau, tôi là ai và ứng dụng này được làm gì thay tôi. Nhóm luồng mã ủy quyền của OAuth, năm thẻ bước nối nhau. 1 ứng dụng chuyển người dùng sang máy chủ ủy quyền, kèm mã định danh ứng dụng và địa chỉ chuyển hướng. 2 người dùng đăng nhập và đồng ý. 3 máy chủ ủy quyền trả về một mã, mà máy chủ chỉ đổi thành token một lần. 4 ứng dụng đổi mã lấy access token. 5 ứng dụng dùng access token gọi tài nguyên. Thẻ PKCE: ứng dụng tạo một chuỗi bí mật, gửi bản băm của nó ở bước 1 và chuỗi gốc ở bước 4, nên kẻ chặn mã không đổi được. Thẻ cuối: đăng nhập cần thêm một lớp nhận diện, như OpenID Connect xây trên OAuth.](../../diagrams/sd-14-011-main.svg)

## Đọc hình

**Hai câu hỏi.** Đăng nhập (xác thực) là chứng minh bạn là ai. Ủy quyền là cho một ứng dụng quyền làm một việc cụ thể, ví dụ đọc danh bạ của bạn, mà không đưa mật khẩu cho nó. Đặc tả OAuth nói thẳng OAuth là giao thức ủy quyền, không phải giao thức xác thực.

**Luồng mã ủy quyền, năm bước.** Ứng dụng chuyển bạn sang máy chủ ủy quyền (bước 1). Bạn đăng nhập và đồng ý ở đó (bước 2), nên mật khẩu không đi qua ứng dụng. Máy chủ trả về một mã (bước 3), và đặc tả yêu cầu mỗi mã chỉ được đổi thành access token một lần; ứng dụng đổi mã lấy token (bước 4) rồi dùng token để gọi tài nguyên (bước 5).

**PKCE.** Ứng dụng sinh một chuỗi ngẫu nhiên (verifier), gửi bản băm SHA-256 của nó (challenge) ở bước 1 và gửi chuỗi gốc ở bước 4. Khi chạy thử, đúng verifier thì khớp, còn verifier đoán bừa thì không. Nhờ vậy kẻ chặn được mã ở bước 3 cũng không đổi được token nếu không có verifier.

**SSO và danh tính.** SSO cho phép đăng nhập một lần rồi dùng nhiều ứng dụng. Để ứng dụng biết bạn là ai, cần một lớp xác thực đứng trên OAuth, ví dụ OpenID Connect; đặc tả OAuth chỉ nêu OpenID Connect như một ví dụ xây trên nó.

## Giới hạn cần nhớ

Access token chỉ cho biết ứng dụng được phép gì, không cho biết người dùng là ai; dùng nó như bằng chứng đăng nhập là lẫn hai việc. Và SSO gom rủi ro vào một chỗ: ai chiếm được phiên đăng nhập chung thì vào được mọi ứng dụng dùng chung nó (suy luận của người biên soạn).

## Nhìn hình trả lời

Một ứng dụng nhận access token từ Google rồi coi ai giữ token là người dùng có địa chỉ email đó. Vì sao đó là thiết kế sai, và cần thêm gì?

<details>
<summary>Xem đáp án</summary>

Access token biểu diễn quyền đã được cấp cho ứng dụng, không phải bằng chứng rằng người cầm nó vừa đăng nhập. Một token có thể được cấp cho ứng dụng khác, bị lộ hoặc dùng lại. Để biết người dùng là ai cần một giao thức xác thực xây trên OAuth, như OpenID Connect.
Đây là lập luận theo đặc tả OAuth; bài này không dựng thử kịch bản tấn công.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Phần nội dung của bài nguồn gần như chỉ là chú thích cho một sơ đồ, nên bài này được viết lại từ các tài liệu đối chiếu. Bài nguồn về token, cookie và session nói SSO “dùng CAS (dịch vụ xác thực trung tâm)”; bài này không lặp lại tên đó vì CAS chỉ là một cách cài đặt và chưa kiểm.
Tài liệu OAuth 2.1 (bản nháp của nhóm làm việc) thay thế OAuth 2.0 và bỏ luồng Implicit và luồng mật khẩu của chủ tài nguyên. Năm bước trong hình là luồng mã ủy quyền theo bản nháp đó. Bài không đi vào làm mới token, các loại token hay các luồng khác.
OWASP lưu ý máy chủ ủy quyền phải bắt buộc dùng đúng `code_verifier` ở điểm cuối cấp token khi ứng dụng gửi `code_challenge`, và nên dùng phương pháp băm chứ không gửi nguyên verifier.

Ví dụ chạy thử là phép tính challenge và so khớp bằng Python, không phải một máy chủ OAuth thật.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/explaining-sessions-tokens-jwt-sso-and-oauth-in-one-diagram.md): chủ đề session, token, JWT, SSO, OAuth (nội dung chữ rất ngắn).
- [OAuth 2.1 Authorization Framework — bản nháp](https://github.com/oauth-wg/oauth-v2-1/blob/main/draft-ietf-oauth-v2-1.md): OAuth là giao thức ủy quyền, luồng mã ủy quyền, PKCE với `S256`, bỏ Implicit và mật khẩu chủ tài nguyên. Đọc qua nguồn trên GitHub.
- [OWASP — OAuth2 Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/OAuth2_Cheat_Sheet.md): PKCE, yêu cầu dùng đúng `code_verifier`. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Đặc tả OpenID Connect không được mở; chỉ dựa vào chỗ bản nháp OAuth 2.1 nhắc tới nó. Bài viết và hình được thiết kế độc lập.

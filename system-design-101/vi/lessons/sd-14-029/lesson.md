# Các luồng OAuth 2.0: chọn luồng nào cho ứng dụng nào?

**Chọn luồng OAuth bằng hai câu hỏi: có người dùng ngồi đó để đăng nhập không, và ứng dụng có giữ kín được một bí mật không. Có người dùng thì dùng luồng mã ủy quyền kèm PKCE; không có người dùng, chỉ một dịch vụ hành động cho chính nó, thì dùng client credentials. Hai luồng còn lại, implicit và mật khẩu của chủ tài nguyên, các tài liệu tôi đọc đều không khuyên dùng.**
Bài so bốn luồng của bài nguồn bằng một máy chủ ủy quyền thu nhỏ dựng từ authlib, và sửa lỗi của nguồn: nó mô tả client credentials giống hệt implicit. OAuth khác đăng nhập thế nào xem [bài sd-14-011](../sd-14-011/lesson.md); các loại bằng chứng xác thực xem [bài sd-14-014](../sd-14-014/lesson.md).

![Hai khung. Khung một, bốn thẻ luồng OAuth: mã ủy quyền kèm PKCE là mặc định khi có người dùng; client credentials khi không có người dùng, dịch vụ tự lấy token; implicit để token nằm trên địa chỉ chuyển hướng, nên bỏ; luồng mật khẩu đưa mật khẩu người dùng cho ứng dụng, không dùng. Khung hai: ứng dụng xin mã kèm challenge và nhận mã; kẻ trộm mã thiếu verifier bị từ chối; ứng dụng gửi mã cùng verifier thì nhận token.](../../diagrams/sd-14-029-main.svg)

## Từ viết tắt

- **OAuth** (Open AUTHorization) — chuẩn ủy quyền mở: cho ứng dụng được làm một số việc, thay người dùng hoặc thay chính nó, mà không cần mật khẩu của người dùng.
- **PKCE** (Proof Key for Code Exchange) — lớp bảo vệ cho luồng mã ủy quyền: ứng dụng chứng minh chính nó là bên đã xin mã, nên mã bị trộm không đổi được token.
- **SHA** (Secure Hash Algorithm) — họ thuật toán băm: biến dữ liệu bất kỳ thành một chuỗi cố định; SHA-256 là một loại.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng về bảo mật ứng dụng; bài dùng hướng dẫn của họ để đối chiếu.
- **RFC** (Request for Comments) — “đề nghị bình luận”: loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; bài chỉ nhắc RFC 9700 theo lời OWASP.

## Đọc hình

Bốn vai: **ứng dụng** xin token; **người dùng** là chủ dữ liệu; **máy chủ ủy quyền** phát token; **máy chủ tài nguyên** nhận token rồi trả dữ liệu. Số liệu từ một lần chạy trên máy người viết, với mật khẩu và bí mật giả.

**Hai câu hỏi.** Theo bản nháp OAuth 2.1, ứng dụng lấy quyền truy cập thay chủ tài nguyên hoặc thay chính nó: đó là câu hỏi đầu. Câu sau: ứng dụng giữ kín được bí mật không. Bản nháp gọi ứng dụng có thông tin xác thực với máy chủ ủy quyền là *confidential*, không có là *public*, và coi bí mật nhúng trong ứng dụng cài trên máy người dùng là có thể bị lấy ra.

**Mã ủy quyền + PKCE: có người dùng.** Ứng dụng công khai gửi người dùng sang máy chủ ủy quyền với 7 tham số, trong đó có `code_challenge`: bản băm SHA-256 của chuỗi bí mật `code_verifier` (cả hai dài 43 ký tự). Người dùng gõ mật khẩu ở trang của máy chủ ủy quyền; trình duyệt được chuyển về ứng dụng chỉ với `code` và `state`. Nhật ký 6 dòng của ứng dụng không chứa mật khẩu. Ứng dụng tự gọi điểm cấp token với `code` và `code_verifier` rồi nhận access token: mã đi qua trình duyệt, token thì không.

Kẻ trộm có mã mà không có verifier bị từ chối: `invalid_request` khi thiếu verifier, `invalid_grant` khi đoán bừa. Trên máy chủ không có PKCE, cùng cuộc tấn công chỉ cần mã, mã định danh ứng dụng và địa chỉ chuyển hướng là nhận được token, và máy chủ tài nguyên coi kẻ trộm là người dùng alice. Ứng dụng bí mật (web có máy chủ riêng) có thêm secret: thiếu secret bị `invalid_client`; ứng dụng thật gửi mã, verifier và secret thì nhận access token cùng refresh token.

**Client credentials: không có người dùng.** Ứng dụng tự xác thực bằng mã định danh và secret trong tiêu đề `Authorization` kiểu Basic, rồi gửi `grant_type=client_credentials` kèm `scope`. Nhật ký máy chủ chỉ có một yêu cầu cấp token, không có yêu cầu nào tới trang đăng nhập. Token không kèm refresh token, và máy chủ tài nguyên thấy `user: null`: token đại diện cho chính ứng dụng. Secret sai, thiếu secret, hay ứng dụng công khai đều bị `invalid_client`; bản nháp cũng nói grant này chỉ dành cho ứng dụng bí mật, nên nó không dành cho ứng dụng một trang như bài nguồn viết.

**Implicit.** Token nằm thẳng sau dấu `#` của địa chỉ chuyển hướng: 0 yêu cầu cấp token, không có refresh token. OWASP ghi luồng này là *deprecated, do not use*: token trong địa chỉ có thể còn trong lịch sử trình duyệt và script trên trang đọc được. Bản nháp OAuth 2.1 bỏ hẳn luồng này.

**Mật khẩu của chủ tài nguyên.** Ứng dụng gửi `username` và `password` của người dùng thẳng tới điểm cấp token. Nhật ký của ứng dụng chứa mật khẩu, và không có yêu cầu nào tới trang đăng nhập của máy chủ ủy quyền. OWASP viết luồng này lộ thông tin đăng nhập cho ứng dụng và không nên dùng; bản nháp OAuth 2.1 cũng bỏ nó.

## Giới hạn cần nhớ

Chọn đúng luồng chưa làm token an toàn: OWASP nhấn mạnh PKCE chỉ bảo vệ mã, còn access token và refresh token cần gắn với người gửi (sender-constrained). Thử nghiệm chạy trên một thư viện, không phải trên dịch vụ thật; OAuth 2.1 vẫn là bản nháp; RFC 6749, 7636 và 9700 không đọc được nên bài chỉ lặp lại điều OWASP và bản nháp nói về chúng.

## Nhìn hình trả lời

Một công cụ chạy đêm trên máy chủ công ty cần đọc báo cáo từ một dịch vụ, không có người dùng nào đăng nhập. Đồng nghiệp đề nghị nhúng tên đăng nhập và mật khẩu của một nhân viên vào công cụ rồi dùng luồng mật khẩu. Nên dùng luồng nào, và vì sao?

<details>
<summary>Xem đáp án</summary>

Dùng client credentials. Công cụ là ứng dụng bí mật có danh tính riêng, và token đại diện cho chính nó (trong thử nghiệm, `user: null`) với `scope` hẹp như `reports.read`. Luồng mật khẩu bắt công cụ giữ mật khẩu thật của một người (trong thử nghiệm, nó nằm trong nhật ký của ứng dụng), và OWASP khuyên không dùng. Secret của công cụ vẫn phải giữ kín: ai có nó thì lấy được token (suy luận của người biên soạn).

</details>

<details>
<summary>Xem sâu hơn: cách thử và điều đã chỉnh so với bài nguồn</summary>

Cách thử: authlib 1.9.1, Flask 3.1.3 và requests 2.34.2 trong một venv tạm, Python 3.13.16, localhost, cổng ngẫu nhiên, trạng thái trong bộ nhớ. Máy chủ dùng đúng các lớp grant của authlib; tôi chỉ viết kho lưu trữ, trang đăng nhập và điểm gọi tài nguyên, và thêm phương thức `none` cho ứng dụng công khai vì authlib 1.9.1 mặc định không cho. Máy tính kiểm xem mật khẩu có nằm trong các chuỗi ứng dụng gửi và nhận không.

Một khác biệt: bản nháp nói máy chủ phải từ chối yêu cầu ủy quyền thiếu `code_challenge` từ ứng dụng công khai; authlib cấu hình đòi PKCE vẫn phát mã, rồi từ chối ở điểm cấp token. Mức chặt tùy cài đặt, nên hãy kiểm máy chủ thật.

Điều đã chỉnh so với bài nguồn:
1. Đoạn client credentials của nguồn là bản sao đoạn implicit (dành cho ứng dụng một trang, token trả thẳng). Đúng là: ứng dụng tự lấy token cho chính nó, không có người dùng, chỉ ứng dụng bí mật dùng được. Nguồn cũng gọi implicit là “Implicit Code Flow”, trong khi luồng này không có mã.
2. Nguồn xếp bốn luồng ngang hàng; OWASP không dùng implicit và mật khẩu chủ tài nguyên, bản nháp OAuth 2.1 bỏ cả hai.
3. Nguồn nói luồng mã ủy quyền cho cả refresh token. Refresh token là tùy chọn: trong thử nghiệm, ứng dụng công khai không được phép dùng nên không nhận, ứng dụng web được phép thì nhận.
4. Nguồn không nhắc PKCE, trong khi OWASP yêu cầu luồng mã kèm PKCE cho mọi loại ứng dụng.

Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/oauth-20-flows.md): bốn luồng, mỗi luồng một dòng.
- [OAuth 2.1 — bản nháp](https://github.com/oauth-wg/oauth-v2-1/blob/d04b368313c8835a930a2e55a68ef547312b7b32/draft-ietf-oauth-v2-1.md): loại ứng dụng, các luồng, luồng bị bỏ, PKCE.
- [OWASP — OAuth 2.0 Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/OAuth2_Cheat_Sheet.md): luồng không dùng, PKCE, giới hạn của PKCE.
- [authlib — khái niệm OAuth 2.0](https://github.com/authlib/authlib/blob/8a308fc39c378c1090608903a09318a4267f418a/docs/oauth2/concepts.rst) và [các lớp grant](https://github.com/authlib/authlib/tree/8a308fc39c378c1090608903a09318a4267f418a/authlib/oauth2/rfc6749/grants): bốn vai, bốn grant của RFC 6749. Đọc từ bản clone; thử nghiệm chạy với authlib 1.9.1.

Đã đọc nguồn ngày 2026-10-18. Cách xếp bốn luồng theo hai câu hỏi là của người biên soạn. Bài viết và hình được thiết kế độc lập.

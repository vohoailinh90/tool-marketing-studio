# SSO hoạt động thế nào? Phiên toàn cục và vé xác nhận

**Đăng nhập một lần (SSO) nghĩa là đăng nhập một lần ở một nơi rồi dùng được nhiều ứng dụng. Trong mô hình kiểu CAS mà bài này dựng thử, đó là đăng nhập ở một máy chủ định danh, rồi mỗi ứng dụng tự lập phiên riêng nhờ một vé dùng một lần.**
Trong mô hình này có hai loại phiên: phiên toàn cục ở máy chủ định danh và phiên cục bộ ở từng ứng dụng; vé nối hai loại đó. Giao thức khác (SAML là một ví dụ) có thể trả kết quả đăng nhập theo luồng khác; bài không chạy thử chúng.
Bài chỉ nói cơ chế, kiểm bằng thí nghiệm nhỏ: một máy chủ định danh, hai ứng dụng và trình duyệt Chromium thật. SSO khác ủy quyền ở đâu: [bài sd-14-011](../sd-14-011/lesson.md). Cookie, session, token: [bài sd-14-008](../sd-14-008/lesson.md), [bài sd-14-009](../sd-14-009/lesson.md), [bài sd-14-010](../sd-14-010/lesson.md).

![Ba khung. Một: lần đầu ở ứng dụng A, trình duyệt mở trang, A chuyển sang máy chủ định danh, người dùng nhập mật khẩu ở đó, máy chủ định danh đặt cookie phiên toàn cục và cấp vé, A kiểm vé qua kênh sau rồi đặt cookie phiên cục bộ. Hai: lần sau ở ứng dụng B, trình duyệt mang cookie phiên toàn cục nên vé được cấp ngay, không hỏi mật khẩu. Ba, đo trên một máy: vé dùng một lần; đăng xuất ở A thì mở lại A là vào luôn; đăng xuất ở máy chủ định danh không xóa phiên cục bộ.](../../diagrams/sd-14-031-main.svg)

## Từ viết tắt

- **SSO** (Single Sign-On) — đăng nhập một lần: đăng nhập một lần ở một nơi rồi dùng được nhiều ứng dụng.
- **CAS** (Central Authentication Service) — dịch vụ xác thực trung tâm: một giao thức SSO dựa trên vé.
- **SAML** (Security Assertion Markup Language) — ngôn ngữ đánh dấu khẳng định bảo mật: chuẩn để một nơi xác thực báo kết quả cho nơi khác.
- **MDN** (Mozilla Developer Network) — tài liệu tra cứu công nghệ web; bài dùng để đối chiếu.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng về bảo mật ứng dụng; bài dùng hướng dẫn của họ.

## Đọc hình

**Ba nơi giữ trạng thái.** Máy chủ định danh giữ phiên toàn cục, mỗi ứng dụng giữ phiên cục bộ, trình duyệt giữ ba cookie, mỗi cái chỉ gửi tới máy chủ đã đặt nó. “Toàn cục” chỉ nghĩa là “của máy chủ định danh”.

**Khung một: lần đầu ở A.** A chưa có phiên cục bộ nên chuyển trình duyệt sang máy chủ định danh, kèm địa chỉ A muốn được đưa về. Người dùng nhập mật khẩu ở máy chủ định danh; A không thấy nó. Máy chủ định danh lập phiên toàn cục, đặt cookie của nó, cấp vé và chuyển về A. A mang vé hỏi thẳng máy chủ định danh (kênh sau: máy chủ gọi máy chủ, không qua trình duyệt), nhận “hợp lệ”, rồi lập phiên cục bộ và đặt cookie của A. Từ đó A phục vụ bằng phiên cục bộ: khi chạy thử, ba lần mở A tiếp theo không gọi máy chủ định danh.

**Khung hai: lần sau ở B.** B chưa có phiên cục bộ nên cũng chuyển hướng, nhưng trình duyệt mang cookie của máy chủ định danh, nên nó cấp vé ngay, không hỏi mật khẩu. B kiểm vé và lập phiên riêng. Khi chạy thử: hai ứng dụng, một lần nhập mật khẩu; hai cookie cùng tên `sid` không đè nhau.

**Vé.** Khi chạy thử, máy chủ định danh từ chối: vé đã dùng; vé kiểm lần hai; vé cấp cho A đem trình cho B; vé quá hạn (đặt 1 giây để thử); địa chỉ quay về chưa đăng ký (mã 400, dù trình duyệt có phiên hợp lệ). Tài liệu CAS nói tương tự: vé chỉ hợp lệ cho dịch vụ được cấp, chỉ một lần kiểm (đúng hay sai đều bị vô hiệu), nên hết hạn sớm (khuyến nghị không quá năm phút).

## Giới hạn cần nhớ

Đăng xuất không tự đi qua mọi phiên. Khi chạy thử: đăng xuất ở A chỉ xóa phiên cục bộ của A; mở lại A thì máy chủ định danh còn phiên toàn cục nên cấp vé và A cho vào ngay. Đăng xuất ở máy chủ định danh xóa phiên toàn cục, nhưng A và B vẫn phục vụ bằng phiên cục bộ cũ. Chỉ khi máy chủ định danh nhớ ứng dụng nào đã nhận vé và gọi từng ứng dụng báo hủy phiên thì cả hai mới hết: đăng xuất tập trung, một việc riêng. Theo CAS việc báo này là tùy chọn và lỗi khi gọi một ứng dụng bị bỏ qua, nên có ứng dụng vẫn giữ phiên (suy luận của người biên soạn). Phiên cục bộ trong thí nghiệm không hết hạn; OWASP nói mọi phiên đều cần hạn.

## Nhìn hình trả lời

Hùng đăng xuất ở A, mở lại A và vẫn vào được mà không nhập mật khẩu. Đó có phải lỗi không, và cần gì để Hùng rời khỏi mọi ứng dụng?

<details>
<summary>Xem đáp án</summary>

Chưa chắc là lỗi. Đăng xuất ở A chỉ xóa phiên cục bộ của A; phiên toàn cục còn nên vào lại A là được cấp vé ngay (đã chạy thử). Muốn rời hẳn, phải kết thúc phiên toàn cục và để từng ứng dụng bỏ phiên cục bộ, bằng đăng xuất tập trung hoặc hạn phiên ngắn ở từng ứng dụng.

</details>

<details>
<summary>Xem sâu hơn: thí nghiệm, vì sao cookie tách nhau, chỗ bài nguồn chưa chính xác</summary>

**Thí nghiệm.** Ba máy chủ bằng thư viện chuẩn Python 3.13.16 nghe ở 127.0.0.1 trên cổng ngẫu nhiên; Playwright 1.56.0 điều khiển Chromium 141.0.7390.37; ba tên giả đuôi `.test` chỉ được ánh xạ về 127.0.0.1 trong Chromium. Đường truyền không mã hóa; mã vé và mã phiên sinh bằng `secrets.token_urlsafe(16)`. Hai lần chạy trọn vẹn cho cùng kết quả. Đây là mô hình kiểu CAS đơn giản, không phải bản cài của CAS hay SAML; mã nằm ngoài kho.

**Vì sao cookie tách nhau.** MDN: cookie không có `Domain` chỉ trả về đúng máy chủ đã đặt nó; có `Domain` thì áp dụng cho tên miền đó và các tên miền con; máy chủ chỉ đặt `Domain` là tên miền của mình hoặc tên miền cha. Khi chạy thử, nhật ký cho thấy A và B chỉ nhận cookie `sid` của mình, máy chủ định danh chỉ nhận cookie của nó. Cổng không phải ranh giới: cùng một tên máy, hai cổng, cookie do cổng này đặt được gửi tới cổng kia và bị đè khi cổng kia đặt cùng tên (quan sát ở Chromium này; tài liệu đã đọc không nói điều đó), nên thí nghiệm dùng ba tên máy. Cookie `Domain` ở tên miền cha có thể chung cho các ứng dụng con, nhưng MDN cảnh báo một ứng dụng ở tên miền con có thể đặt cookie cho mọi tên miền con khác, kẽ hở cho tấn công cố định phiên.

**Các giao thức, chỉ là tên.** OWASP: hồ sơ SAML cho trình duyệt là một trong những cách cài SSO phổ biến nhất. Tài liệu CAS: giao thức dựa trên vé; `TGT` lưu trong cookie `TGC` là phiên SSO, `ST` gửi bằng tham số GET là quyền máy chủ cấp cho ứng dụng. Đặc tả SAML không được mở.

**Chỗ bài nguồn chưa chính xác hoặc thiếu.**
- “Lược đồ xác thực” dùng “một định danh duy nhất”: thực ra một nơi kiểm tra đăng nhập; ứng dụng nhận vé, không nhận mật khẩu.
- Gọi vé là “token”: vé này khác token đi kèm mọi yêu cầu ([bài sd-14-010](../sd-14-010/lesson.md)); nó chỉ đổi lấy phiên rồi hết giá trị.
- “Phiên toàn cục” là tên của nguồn; CAS gọi là phiên SSO.
- “Máy chủ đăng ký hệ thống” khi kiểm vé: thí nghiệm không có bước đó và phần CAS đã đọc cũng không mô tả; máy chủ tra vé, đối chiếu ứng dụng, đánh dấu đã dùng. Đăng ký có thật nhưng xảy ra trước, ở danh sách ứng dụng được phép (CAS chế độ không mở; OWASP khuyên dùng danh sách cho phép).
- Nguồn bỏ qua phiên cục bộ và đăng xuất. Ví dụ Gmail và YouTube là của nguồn; bài không kiểm cách công ty nào cài đặt SSO.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/v1what-is-sso-single-sign-on.md): chuỗi mười bốn bước, hai ứng dụng và một máy chủ xác thực.
- MDN: [Set-Cookie](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/reference/headers/set-cookie/index.md), [Cookie](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/cookies/index.md): phạm vi `Domain`.
- OWASP: [Session Management](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Session_Management_Cheat_Sheet.md), [Unvalidated Redirects](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.md), [SAML](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/SAML_Security_Cheat_Sheet.md): hạn phiên, danh sách cho phép, tên giao thức.
- Apereo CAS: [tổng quan](https://github.com/apereo/cas/blob/af471c26a4316661e4f82d2c0f5e3824b60ee7ee/docs/cas-server-documentation/protocol/CAS-Protocol.md), [đặc tả 3.0.3](https://github.com/apereo/cas/blob/af471c26a4316661e4f82d2c0f5e3824b60ee7ee/docs/cas-server-documentation/protocol/CAS-Protocol-Specification.md): vé dịch vụ, cookie cấp vé, đăng xuất tập trung.

Đã đọc nguồn ngày 2026-10-18. Số liệu thử là các lần chạy trên máy biên soạn (xem phần sâu hơn); không mở trang RFC hay đặc tả SAML. Cách chia hai loại phiên và tên “vé xác nhận” là của người biên soạn. Bài viết và hình được thiết kế độc lập.

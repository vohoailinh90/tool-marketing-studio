# Bốn cơ chế xác thực: khóa SSH, token OAuth, chứng chỉ và mật khẩu

**Bốn thứ bài nguồn liệt kê cùng trả lời câu hỏi “cái gì chứng minh bạn là bạn?”, nhưng bằng bốn cách khác nhau: giữ một khóa riêng, cầm một token, có tên được một tổ chức xác nhận là gắn với một khóa, hoặc biết một bí mật.**
Bài này chạy thử từng cơ chế để thấy mỗi cái chứng minh được gì và không chứng minh được gì, rồi trả lời câu hỏi cuối bài nguồn: có nên để khóa trong một kho mã không?

![Sáu thẻ xếp dọc. Thẻ đầu là câu hỏi chung: cái gì chứng minh bạn là bạn. Khóa SSH: chứng minh bằng việc giữ khóa riêng, máy chủ chỉ giữ khóa công khai. Token OAuth: ủy quyền có giới hạn, và ai đang giữ token thì dùng được. Chứng chỉ, trong giao thức TLS trước đây gọi là SSL: gắn một tên với một khóa công khai, do tổ chức cấp chứng chỉ xác nhận; mã hóa vẫn chạy ngay cả khi không kiểm tra chứng chỉ. Mật khẩu: điều bạn biết, máy chủ nên lưu bản băm, thêm yếu tố thứ hai. Thẻ cuối: xóa một tệp chứa khóa ở commit sau không xóa nó khỏi lịch sử; phải thu hồi và đổi khóa.](../../diagrams/sd-14-014-main.svg)

## Đọc hình

**Khóa SSH.** Theo sách hướng dẫn của OpenSSH, mỗi người dùng tạo một cặp khóa; máy chủ biết khóa công khai, chỉ người dùng biết khóa riêng, và tệp `authorized_keys` liệt kê các khóa công khai được phép đăng nhập. Máy khách chứng minh mình có khóa riêng. Chạy thử với OpenSSH 10.6p1 dựng từ mã nguồn đã ghim, một máy chủ tạm trên 127.0.0.1:18022 tắt đăng nhập bằng mật khẩu: khóa nằm trong danh sách được đăng nhập (dòng “Authenticated … using "publickey"”, và lệnh ép buộc của khóa đó chạy); khóa không có trong danh sách nhận `Permission denied (publickey)`; xóa khóa đúng khỏi tệp thì chính máy khách đó bị từ chối. Nhật ký máy chủ ghi dấu vân tay của từng khóa chứ không có nội dung khóa riêng (máy chủ vốn không nhận được khóa riêng). Chiều ngược lại cũng quan trọng: ssh ghi khóa của máy chủ vào `known_hosts`. Khi ghi sẵn một khóa khác cho địa chỉ đó và đặt `StrictHostKeyChecking=yes`, ssh in `REMOTE HOST IDENTIFICATION HAS CHANGED!` và `Host key verification failed.`, thoát với mã 255, và máy chủ không ghi thêm lần đăng nhập nào. Sách hướng dẫn giải thích rằng cảnh báo này nhằm ngăn giả mạo máy chủ hay tấn công xen giữa.

**Token OAuth.** Bản nháp OAuth 2.1 định nghĩa bearer token là token mà bên nào đang giữ cũng dùng được, không cần chứng minh mình có khóa nào. Nó cũng mô tả access token gắn với khóa (sender-constrained) như một cách thu hẹp rủi ro; cách đó không được chạy thử ở đây. Điều bài nguồn gọi là “quyền truy cập có giới hạn” đúng với ý ủy quyền: token cho phép làm một số việc, không tự chứng minh người cầm vừa đăng nhập. Chi tiết xem [bài sd-14-011](../sd-14-011/lesson.md).

**Chứng chỉ (TLS, trước đây gọi là SSL).** Theo MDN, TLS là giao thức kế nhiệm SSL, cung cấp mã hóa và xác thực; máy chủ thường tự xác thực với máy khách, còn xác thực máy khách thì hiếm trên web ngoài các ứng dụng chuyên biệt. Chứng chỉ số gắn một khóa công khai với một tổ chức hoặc tên, thường do một tổ chức cấp chứng chỉ (CA) ký để xác nhận. Chạy thử bằng Python 3.13 với khóa và CA tạm: máy khách tin CA kết nối được qua TLS 1.3 tới chứng chỉ cho `localhost`; máy khách không tin CA nhận “unable to get local issuer certificate”; chứng chỉ cấp cho tên khác nhận “Hostname mismatch”; chứng chỉ hết hạn nhận “certificate has expired”; chứng chỉ tự tạo xưng là localhost nhận “self-signed certificate”. Khi tắt kiểm tra chứng chỉ ở máy khách, kết nối tới chứng chỉ tự tạo vẫn hoàn tất qua TLS 1.3 và dữ liệu vẫn đến: mã hóa chạy cả khi không biết đối phương là ai. Điều bị mất là sự chắc chắn về người ở đầu bên kia. Khi máy chủ yêu cầu chứng chỉ của máy khách (mTLS), máy khách không có chứng chỉ bị từ chối (`tlsv13 alert certificate required`) và máy khách có chứng chỉ do CA ký kết nối được; OWASP mô tả cách này là cả hai bên gửi chứng chỉ và máy chủ kiểm tra chứng chỉ của máy khách với một CA.

**Mật khẩu.** Là điều bạn biết. OWASP nói xác thực đa yếu tố là biện pháp phòng thủ tốt nhất so với phần lớn các tấn công vào mật khẩu, và mô tả credential stuffing là thử các cặp tên và mật khẩu lấy từ vụ lộ ở một trang khác. Máy chủ không nên lưu mật khẩu nguyên văn: xem [bài sd-14-003](../sd-14-003/lesson.md) về lưu mật khẩu an toàn.

**Khóa trong kho mã.** OWASP ghi nhận nhiều tổ chức có bí mật nằm thẳng trong mã nguồn dưới dạng văn bản thường, và khuyên khi lộ thì thu hồi, đổi và xóa. Thử trong một kho git tạm trên máy: commit một tệp `.env` có khóa giả rồi xóa nó ở commit sau; commit mới nhất không còn tệp ấy, nhưng `git show HEAD~1:.env` vẫn in ra khóa, `git log -S` tìm thấy cả hai commit, và sau `git gc --prune=now` khóa vẫn đọc được. Khi `.env` nằm trong `.gitignore`, `git add .env` bị từ chối trừ khi ép buộc. Đây là kho cục bộ, không phải GitHub.

## Giới hạn cần nhớ

Cách gom bốn cơ chế vào bốn kiểu bằng chứng (giữ khóa riêng, cầm token, được CA xác nhận, biết bí mật) là của người biên soạn để dễ so sánh; thực tế chúng giao nhau, ví dụ khóa riêng của SSH có thể được bảo vệ bằng một cụm mật khẩu, và một token OAuth có thể được cấp sau khi người dùng đăng nhập bằng mật khẩu (hai ví dụ này là hiểu biết chung của người biên soạn, chưa chạy thử). Các phần chưa chạy thử: thu hồi chứng chỉ (CRL, OCSP), chứng chỉ SSH, token OAuth gắn với khóa, tính năng quét bí mật của GitHub và tài liệu GitHub, nên bài không kết luận về cách GitHub xử lý khóa bị lộ.

## Nhìn hình trả lời

Bài nguồn hỏi: có nên để các khóa này trong một kho GitHub không? Một lập trình viên vừa commit nhầm tệp `.env` chứa khóa API, rồi nhận ra và xóa tệp đó ở commit kế tiếp. Khóa đã an toàn chưa, và nên làm gì?

<details>
<summary>Xem đáp án</summary>

Chưa an toàn. Xóa tệp ở commit sau chỉ làm thay đổi trạng thái mới nhất; commit cũ vẫn giữ nguyên tệp, và trong lần thử cục bộ khóa vẫn đọc được từ lịch sử kể cả sau khi dọn rác của git. Bất kỳ ai có quyền đọc kho, hoặc có bản sao của nó, đều đọc được khóa đó. Theo OWASP, việc cần làm trước tiên là thu hồi và đổi khóa, rồi mới dọn lịch sử; OWASP cũng lưu ý rằng nén (squash) lịch sử để loại bỏ commit sẽ viết lại lịch sử và làm hỏng các liên kết khác tới commit đó.
Phần công khai của một cặp khóa hoặc của một chứng chỉ vốn để chia sẻ, nên để chúng trong kho thường không phải vấn đề; khóa riêng, token và mật khẩu thì không. Kho riêng tư chỉ thu hẹp số người đọc được, không làm một khóa riêng hết nhạy cảm (suy luận của người biên soạn, chưa kiểm GitHub).
Thử nghiệm chỉ chạy trên một kho git cục bộ.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn gọi token OAuth là một cơ chế xác thực. Bài này giữ nó trong danh sách nhưng nói rõ: token ủy quyền một quyền hạn cho bất kỳ ai giữ nó; việc xác nhận người dùng là ai thuộc về lớp xác thực đứng trên OAuth (bài sd-14-011).
Bài nguồn viết “chứng chỉ SSL đảm bảo giao tiếp an toàn và được mã hóa”. Phép thử cho thấy mã hóa vẫn chạy khi chứng chỉ không được kiểm tra, nên bài này nói chứng chỉ xác thực một tên và một khóa, còn việc mã hóa đến từ giao thức TLS. Bài giữ tên SSL theo nguồn và nói TLS là giao thức hiện hành.
Câu hỏi cuối của bài nguồn (có nên để khóa trong kho GitHub không) được trả lời bằng thử nghiệm git cục bộ và hướng dẫn của OWASP thay vì một ý kiến.
Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-4-forms-of-authentication-mechanisms.md): bốn cơ chế và câu hỏi về việc quản lý khóa.
- [OpenSSH — sách hướng dẫn ssh](https://github.com/openssh/openssh-portable/blob/75ef208b8882bc8a1fb2ee3a538a4e63b05b970a/ssh.1): xác thực bằng khóa công khai, `known_hosts`, `StrictHostKeyChecking`. Đọc từ bản clone của kho; máy chủ thử dựng từ chính mã nguồn này.
- [OAuth 2.1 — bản nháp](https://github.com/oauth-wg/oauth-v2-1/blob/d04b368313c8835a930a2e55a68ef547312b7b32/draft-ietf-oauth-v2-1.md): bearer token và access token gắn với khóa. Đọc từ bản clone của kho.
- [MDN — Transport Layer Security](https://github.com/mdn/content/blob/19370346042efad9e179fbf1f55deeeadee98c40/files/en-us/web/security/defenses/transport_layer_security/index.md): TLS kế nhiệm SSL, xác thực máy chủ, chứng chỉ số và CA (kèm các mục chú giải SSL, TLS, digital certificate, certificate authority trong cùng bản clone).
- [OWASP — Authentication](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Authentication_Cheat_Sheet.md): xác thực đa yếu tố, credential stuffing, xác thực máy khách bằng TLS. [OWASP — Secrets Management](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Secrets_Management_Cheat_Sheet.md): bí mật trong mã nguồn, thu hồi, đổi, xóa. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-14. Cách gom bốn cơ chế vào bốn kiểu bằng chứng là của người biên soạn. Bài viết và hình được thiết kế độc lập.

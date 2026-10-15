# Bảng tra cứu thiết kế API

**Bản chữ của nguồn nói tới ba việc khi thiết kế API an toàn: cấp khóa cho từng client, ký mỗi yêu cầu bằng khóa bí mật, và đặt vào yêu cầu những tham số giúp chống giả mạo và gửi lại.** Mục hướng dẫn bảo mật của nguồn dừng ngay sau câu dẫn; phần còn lại, nếu có, nằm trong hình gốc và bài không đoán nội dung đó.

![Năm khung dọc: cấp khóa, mỗi client một mã ứng dụng và mỗi mức quyền như chỉ đọc hoặc đọc ghi một cặp mã truy cập với khóa bí mật; ký, thu thập tham số, dựng chuỗi cần ký, tính HMAC với SHA-256 bằng khóa bí mật rồi gửi yêu cầu kèm chữ ký, khóa bí mật không bao giờ được gửi; tham số của yêu cầu gồm thông tin xác thực, thời điểm, dữ liệu riêng của yêu cầu và nonce; máy chủ kiểm tra bằng cách tìm khóa bí mật theo mã truy cập, tính lại chữ ký, so sánh rồi kiểm tra thời điểm và nonce; chữ ký không làm thay mã hóa đường truyền, kiểm tra quyền theo tài nguyên và thu hồi khóa.](../../diagrams/sd-01-021-main.svg)

## Đọc hình

1. **Cấp khóa.** Mỗi client có một mã ứng dụng (app ID). Với mỗi mức quyền, ví dụ chỉ đọc hoặc đọc và ghi, cấp một cặp khóa riêng: mã truy cập (access key) cho máy chủ biết ai đang gọi, và khóa bí mật (secret key) dùng để ký. Nguồn gọi mã truy cập là "public key"; trong cách ký dưới đây đó chỉ là một định danh, không phải khóa công khai của mật mã bất đối xứng.
2. **Ký.** Thu thập các tham số của yêu cầu, dựng thành một chuỗi cần ký, rồi băm chuỗi đó bằng HMAC (Hash-based Message Authentication Code, mã xác thực thông điệp dựa trên hàm băm) kết hợp SHA-256 (Secure Hash Algorithm, hàm băm 256 bit), dùng khóa bí mật làm khóa. Sau đó gửi yêu cầu kèm chữ ký. Khóa bí mật không bao giờ đi qua mạng.
3. **Tham số của yêu cầu.** Nguồn nêu bốn thứ nên có: thông tin xác thực; thời điểm (timestamp) để chống tấn công phát lại; dữ liệu riêng của yêu cầu như mã người dùng, chi tiết giao dịch hay câu tìm kiếm; và nonce, một chuỗi ngẫu nhiên trong mỗi yêu cầu để mỗi yêu cầu là duy nhất, cũng nhằm chống phát lại.
4. **Máy chủ kiểm tra.** Bước này không có trong bản chữ của nguồn mà do bài bổ sung. Máy chủ tìm khóa bí mật theo mã truy cập, tự dựng lại chuỗi cần ký, tính lại chữ ký và so sánh; khác thì từ chối. Nó cũng xem thời điểm có còn trong khoảng cho phép và nonce đã dùng chưa.
5. **Chữ ký không làm thay.** Cũng do bài bổ sung: mã hóa đường truyền, kiểm tra quyền theo từng tài nguyên, và thu hồi hoặc thay khóa vẫn là việc riêng.

## Giới hạn cần nhớ

Chữ ký chứng minh người gửi giữ khóa bí mật và phần đã ký không bị sửa; nó không giữ kín nội dung (vẫn cần TLS, Transport Layer Security, giao thức mã hóa đường truyền), không cho biết người đó được phép làm việc gì, và không tự chặn việc gửi lại nếu thiếu thời điểm hoặc nonce. Theo suy luận của bài: nếu một tham số không nằm trong chuỗi cần ký thì kẻ tấn công đổi được nó mà chữ ký vẫn đúng; nonce chỉ chặn được gửi lại khi máy chủ nhớ các nonce đã thấy trong khoảng thời gian mà thời điểm còn được chấp nhận; và máy chủ nên so sánh chữ ký bằng phép so sánh thời gian không đổi. Mọi chi tiết về cách dựng chuỗi (thứ tự tham số, cách mã hóa ký tự, băm thân yêu cầu) khác nhau giữa các dịch vụ; bài không mô tả một định dạng cụ thể nào.

## Nhìn hình thử trả lời

Máy chủ nhận được một yêu cầu có chữ ký đúng, nhưng thời điểm trong yêu cầu cách hiện tại hai giờ. Có nên chấp nhận không, và nếu chấp nhận thì kẻ tấn công làm được gì?

<details>
<summary>Xem đáp án</summary>

Không nên. Chữ ký đúng chỉ chứng minh người ký có khóa bí mật vào lúc ký và nội dung không bị sửa. Nếu ai đó chụp lại được yêu cầu (từ nhật ký, từ một đoạn mạng không mã hóa) và gửi lại, chữ ký vẫn đúng, nên giao dịch có thể bị lặp. Thời điểm cho yêu cầu một hạn dùng ngắn; nonce cho phép máy chủ từ chối một yêu cầu đã thấy trong hạn đó.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **HMAC:** hàm tính một giá trị ngắn từ khóa bí mật và thông điệp; ai không có khóa thì không tính ra giá trị đúng. Hai bên dùng cùng một khóa, khác chữ ký số dùng cặp khóa công khai và riêng (RSA, ECDSA).
- **Token mang danh (bearer token):** ai cầm được token là dùng được, nên phải đi qua kênh mã hóa và dễ bị dùng lại nếu lộ. Yêu cầu có ký không gửi bí mật đi, đổi lại client phải làm phép ký cho mỗi yêu cầu.
- **Ví dụ thực tế:** AWS Signature Version 4 ký yêu cầu bằng HMAC với SHA-256, trên một dạng chuẩn hóa của yêu cầu và ngày giờ; xem tài liệu của AWS để thấy các bước chi tiết.
- **OWASP API Security Top 10:** danh sách rủi ro API phổ biến (OWASP là Open Worldwide Application Security Project, dự án cộng đồng về an toàn ứng dụng), trong đó có lỗi kiểm quyền ở cấp đối tượng; chữ ký không chữa được lỗi đó.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-cheat-sheet-for-api-designs.md): bản chữ gồm cấp khóa, ký yêu cầu và tham số của yêu cầu.
- [RFC 2104 — HMAC](https://www.rfc-editor.org/rfc/rfc2104) và [RFC 6750 — Bearer Token](https://www.rfc-editor.org/rfc/rfc6750).
- [AWS — Signature Version 4](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv.html).
- [OWASP — API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/).

Đã đọc bản nguồn ByteByteGo ngày 2026-10-15; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

# Chữ ký số: ký bằng khóa riêng, kiểm bằng khóa công khai

**Chữ ký số trả lời hai câu hỏi về một tài liệu: nó có bị sửa sau khi ký không, và có đúng người giữ khóa riêng này đã ký không. Nó không giấu nội dung, và tự nó không cho biết người giữ khóa là ai.**
Bài này đi qua sáu bước của bài nguồn, chạy thử từng bước bằng thư viện `cryptography` của Python, và chỉ ra chỗ mô tả “mã hóa bản băm bằng khóa riêng” đúng cho một kiểu chữ ký nhưng không đúng cho các kiểu khác.

![Bảy thẻ xếp dọc, sáu thẻ đầu nối bằng mũi tên. Một: người ký tạo cặp khóa, khóa riêng giữ kín, khóa công khai chia sẻ được. Hai: băm tài liệu thành một dấu vân tay ngắn cố định, đổi một byte thì dấu vân tay đổi. Ba: ký bằng khóa riêng ra chữ ký. Bốn: gửi tài liệu cùng chữ ký; tài liệu vẫn đọc được. Năm: người nhận dùng khóa công khai của người ký để kiểm chữ ký với chính tài liệu nhận được. Sáu: khớp thì đúng khóa riêng đã ký và nội dung chưa đổi kể từ lúc ký; không khớp thì từ chối. Thẻ cuối: chữ ký không giấu nội dung và không tự cho biết khóa công khai là của ai.](../../diagrams/sd-14-015-main.svg)

## Đọc hình

Các lần thử dưới đây dùng thư viện `cryptography` 50.0.1 của Python với khóa tạm; ví dụ thông điệp là `Pay Bob 100 USD`.

**1 · Cặp khóa.** Người ký tạo khóa riêng (giữ kín) và khóa công khai (chia sẻ được). Đối tượng khóa công khai trong thư viện chỉ có thao tác kiểm (`verify`); không có thao tác nào cho phép nó ký.

**2 · Băm.** Băm (hash) biến tài liệu thành một dãy ngắn có độ dài cố định, như một dấu vân tay. SHA-256 của `Pay Bob 100 USD` và của `Pay Bob 900 USD` khác nhau ở 129 trong 256 bit, dù hai câu chỉ khác một ký tự.

**3 · Ký.** Người ký dùng khóa riêng để tạo chữ ký. Với Ed25519, chữ ký luôn dài 64 byte, dù thông điệp dài 0 byte, 15 byte hay 1 MB, và ký hai lần cùng một thông điệp cho cùng một chữ ký. Bài nguồn mô tả bước này là mã hóa bản băm bằng khóa riêng; mục “Xem sâu hơn” giải thích mô tả đó đúng với kiểu nào.

**4 · Gửi.** Tài liệu đi cùng chữ ký, và tài liệu vẫn đọc được: thứ được gửi đi vẫn chứa dòng chữ `Pay Bob 100 USD` ở dạng đọc ra được. Chữ ký số không phải mã hóa nội dung.

**5 · Kiểm.** Người nhận có ba thứ: tài liệu nhận được, chữ ký và khóa công khai của người ký. Họ kiểm chữ ký với chính tài liệu họ nhận.

**6 · Kết quả.** Với Ed25519, chữ ký đúng cho kết quả hợp lệ. Đổi một byte của thông điệp (100 thành 900) hoặc kiểm bằng khóa công khai của người khác đều làm thư viện báo `InvalidSignature`. Khớp nghĩa là chữ ký do người giữ khóa riêng tương ứng tạo ra trên đúng nội dung này.

**Chưa nói được: ai là người đó.** Thử làm giả: một thông điệp giả cùng chữ ký giả do kẻ tấn công ký bằng cặp khóa riêng của họ hợp lệ khi kiểm bằng khóa công khai của chính kẻ đó, nhưng không hợp lệ khi kiểm bằng khóa công khai thật của Alice. Một chữ ký hợp lệ chỉ cho biết người giữ khóa riêng tương ứng đã ký. MDN cũng nêu điều kiện này: nếu kẻ tấn công lừa được người kiểm tin nhầm một khóa công khai thì có thể mạo danh chủ khóa, và người kiểm thường dùng chứng chỉ số để biết khóa nào là thật. Muốn biết người giữ khóa là Alice, người nhận phải biết khóa công khai nào của Alice từ một nguồn đáng tin, ví dụ chứng chỉ do tổ chức cấp chứng chỉ ký (xem [bài sd-14-014](../sd-14-014/lesson.md)).

## Giới hạn cần nhớ

Bài này kiểm chứng cơ chế kỹ thuật của chữ ký (đổi nội dung thì kiểm thất bại, khác khóa thì thất bại), chứ không bàn hiệu lực pháp lý của chữ ký, vấn đề không thể chối bỏ (non-repudiation), cách bảo quản khóa riêng hay thu hồi khóa. Các đặc tả của NIST và RFC không đọc được nên không được trích dẫn; hành vi của từng kiểu chữ ký dựa trên tài liệu của thư viện `cryptography` và các lần chạy.

## Nhìn hình trả lời

Mallory chặn một tài liệu “Pay Bob 100 USD” có chữ ký của Alice, sửa thành “900 USD” và gửi tiếp cùng chữ ký cũ. Bob sẽ thấy gì khi kiểm? Và Mallory có tự ký lại để Bob chấp nhận được không?

<details>
<summary>Xem đáp án</summary>

Bob kiểm bằng khóa công khai của Alice sẽ thấy chữ ký không hợp lệ, vì tài liệu đã đổi so với lúc Alice ký (trong lần thử, đổi một byte là đủ để thư viện báo `InvalidSignature`).
Mallory có thể ký bản sửa bằng khóa riêng của chính mình, và chữ ký ấy hợp lệ khi kiểm bằng khóa công khai của Mallory. Nó chỉ có giá trị nếu Bob tin rằng khóa công khai đó là của Alice. Vì vậy phần khó của hệ thống không nằm ở phép kiểm chữ ký mà ở chỗ người nhận biết khóa công khai nào là của ai: đó là việc của chứng chỉ và tổ chức cấp chứng chỉ, hoặc của một cách trao khóa đáng tin khác.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn nói người ký “mã hóa bản băm bằng khóa riêng” và người nhận “giải mã chữ ký bằng khóa công khai” để ra bản băm. MDN dùng cùng mô hình đơn giản đó. Chạy thử cho thấy mô tả ấy khớp với một kiểu cụ thể: RSA-2048 theo PKCS#1 v1.5 với SHA-256. Ở đó, tính `chữ ký ^ e mod n` bằng khóa công khai cho ra một giá trị 256 byte bắt đầu bằng `00 01 ff ff` và kết thúc đúng bằng SHA-256 của thông điệp, và ký hai lần cùng thông điệp cho cùng chữ ký. Với các kiểu khác thì không: RSA-PSS cho hai chữ ký khác nhau khi ký hai lần cùng thông điệp (cả hai đều hợp lệ), và giá trị `chữ ký ^ e mod n` kết thúc bằng byte `0xbc` chứ không bằng bản băm thuần; ECDSA P-256 cũng cho hai chữ ký khác nhau mà cả hai đều hợp lệ, và ký riêng bản băm SHA-256 (tùy chọn Prehashed) vẫn kiểm đúng với toàn bộ thông điệp; Ed25519 là kiểu EdDSA trên đường cong Curve25519. Tài liệu của thư viện coi PSS là lựa chọn nên dùng cho giao thức mới và chỉ dành PKCS#1 v1.5 cho giao thức cũ. Vì vậy bài này giữ sáu bước của bài nguồn nhưng nói “ký” thay cho “mã hóa bản băm”.
Bài nguồn nói người nhận “lấy bản băm gốc từ tài liệu”. Tài liệu không chứa bản băm: người nhận tự tính bản băm từ tài liệu nhận được, rồi kiểm chữ ký với nó (ở kiểu PKCS#1 v1.5, bản băm được khôi phục từ chữ ký để so với bản băm tự tính).
Bài nguồn nói chữ ký “là duy nhất cho mỗi người”. Bài này nói chữ ký gắn với một khóa riêng và một thông điệp; việc khóa đó thuộc về ai phải được xác lập riêng.
Bài nguồn không nói rõ tài liệu vẫn đọc được sau khi ký; bài này nói rõ.
Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-digital-signatures-work.md): tám bước ký và kiểm.
- [MDN — Digital signature](https://github.com/mdn/content/blob/19370346042efad9e179fbf1f55deeeadee98c40/files/en-us/glossary/digital_signature/index.md) và mục [Public-key cryptography](https://github.com/mdn/content/blob/19370346042efad9e179fbf1f55deeeadee98c40/files/en-us/glossary/public-key_cryptography/index.md): mô hình ký bằng khóa riêng, kiểm bằng khóa công khai. Đọc từ bản clone của kho.
- [pyca/cryptography — RSA](https://github.com/pyca/cryptography/blob/1fbd556897daba9479bddf82b9a1824b72ea33eb/docs/hazmat/primitives/asymmetric/rsa.rst), [Ed25519](https://github.com/pyca/cryptography/blob/1fbd556897daba9479bddf82b9a1824b72ea33eb/docs/hazmat/primitives/asymmetric/ed25519.rst), [ECDSA](https://github.com/pyca/cryptography/blob/1fbd556897daba9479bddf82b9a1824b72ea33eb/docs/hazmat/primitives/asymmetric/ec.rst): các kiểu chữ ký, PSS và PKCS#1 v1.5, Prehashed. Đọc từ bản clone của kho; các lần thử chạy với `cryptography` 50.0.1.

Đã đọc nguồn ngày 2026-10-14. Cách chia sáu bước và phần giải thích khác biệt giữa các kiểu chữ ký là của người biên soạn. Bài viết và hình được thiết kế độc lập.

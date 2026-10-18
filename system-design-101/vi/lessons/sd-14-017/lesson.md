# HTTPS và bắt tay TLS: dựng kênh mã hóa thế nào?

**HTTPS là HTTP chạy bên trong một lớp mã hóa tên là TLS. Lớp đó thêm ba thứ: giữ kín nội dung, phát hiện nội dung bị sửa trên đường, và cho trình duyệt biết máy chủ có đúng là máy chủ của tên miền nó định nối tới hay không.**
Cả ba được dựng trong một bước “bắt tay” ngay đầu kết nối. HTTPS không làm một trang web trở nên đáng tin.
Bài này đi qua bắt tay TLS ở mức nhìn được: những thông điệp nào, theo thứ tự nào, thứ nào đi nguyên văn trên đường và thứ nào đã mã hóa. Bài dựa vào tài liệu của MDN và OpenSSL, cùng một lần chạy thử cục bộ: một máy chủ và một máy khách `openssl` trên 127.0.0.1, có một chương trình nhỏ ghi lại các byte đi qua. Chứng chỉ và chữ ký không được dạy lại ở đây, xem [bài sd-14-014](../sd-14-014/lesson.md) và [bài sd-14-015](../sd-14-015/lesson.md). Bài cũng không bàn cách cấu hình máy chủ hay các tính năng TLS mới hơn.

![Ba khung xếp dọc. Khung một: HTTPS thêm ba thứ cho HTTP, gồm giữ kín nội dung, phát hiện nội dung bị sửa trên đường và xác thực máy chủ bằng chứng chỉ. Khung hai: bắt tay TLS 1.3 rút gọn giữa trình duyệt và máy chủ. Trình duyệt gửi ClientHello, máy chủ trả ServerHello, rồi từ đây mọi thứ được mã hóa: chứng chỉ, CertificateVerify, Finished của máy chủ, Finished của trình duyệt, rồi yêu cầu và phản hồi HTTP mã hóa bằng khóa phiên. Khung ba, giới hạn của HTTPS: tên máy chủ vẫn nằm trong ClientHello, chứng chỉ không làm một trang trở nên đáng tin, máy chủ vẫn đọc được mọi thứ bạn gửi và độ dài từng gói dữ liệu vẫn lộ.](../../diagrams/sd-14-017-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: ngôn ngữ trình duyệt và máy chủ web dùng để yêu cầu và trả về trang.
- **HTTPS** (HyperText Transfer Protocol Secure) — HTTP an toàn: HTTP chạy bên trong một kết nối đã được TLS mã hóa.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa đặt giữa kết nối TCP và HTTP; bài này nói về cách nó dựng kênh.
- **SSL** (Secure Sockets Layer) — lớp ổ cắm an toàn: tên của các phiên bản đầu của giao thức mà TLS thay thế; nhiều công cụ vẫn gọi theo tên cũ.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: kết nối đáng tin cậy giữa hai máy mà TLS chạy phía trên.
- **IP** (Internet Protocol) — giao thức liên mạng: địa chỉ IP là địa chỉ số của một máy trên mạng.
- **SNI** (Server Name Indication) — chỉ báo tên máy chủ: phần của ClientHello cho biết trình duyệt muốn nối tới tên nào.
- **HTML** (HyperText Markup Language) — ngôn ngữ đánh dấu siêu văn bản: ngôn ngữ mô tả cấu trúc một trang web; không liên quan tới mã hóa.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

Các số liệu dưới đây là một lần chạy trên máy biên soạn: `openssl` 3.0.13, chứng chỉ tự tạo, máy chủ và máy khách cùng nằm trên 127.0.0.1. Cách chạy ở mục “Xem sâu hơn”.

**Khung 1 · HTTPS thêm gì.** Theo MDN, TLS giữ an toàn cho kết nối theo ba cách: mã hóa (người ngoài không đọc được dữ liệu đang đi), toàn vẹn (không ai sửa lén được mà không bị phát hiện) và xác thực (một bên chứng minh mình là ai; trên web thường chỉ máy chủ chứng minh với trình duyệt). HTTPS là HTTP chạy trên TLS, nên dòng yêu cầu và phản hồi HTTP không đổi, chỉ được đặt vào các bản ghi mã hóa. Thử: khi dòng `GET / HTTP/1.0` đi qua HTTP thường, nó nằm nguyên văn trong các byte ghi được; qua TLS, nó và phản hồi đều không tìm thấy. Đổi một bit của một bản ghi trên đường thì TLS ngắt với lỗi `decryption failed or bad record mac`, còn HTTP thường nhận chữ đã bị đổi (`hello` thành `iello`) mà không biết gì.
SSL hay TLS? SSL là tên các phiên bản đầu; MDN nói TLS là tên mới và SSL đã được thay thế. Theo tài liệu OpenSSL, TLS 1.3 và TLS 1.2 là hai phiên bản phổ biến nhất, còn TLS 1.0 và 1.1 đã bị chính thức coi là lỗi thời. Hình vẽ TLS 1.3. Thói quen tên cũ vẫn còn: dòng tổng kết của chính `openssl` cho một kết nối TLS 1.3 vẫn mở đầu bằng `SSL handshake has read`.

**Khung 2 · Bắt tay.**

**ClientHello.** Trình duyệt mở đầu và gửi nguyên văn: các bộ mã (cipher suite, tức tổ hợp thuật toán hai bên có thể dùng) nó hỗ trợ, tên máy chủ muốn nối (SNI), và một “nửa khóa” (key share) cho nhóm trao đổi khóa `x25519`.

**ServerHello.** Máy chủ chọn phiên bản và bộ mã (lần chạy: `TLS_AES_256_GCM_SHA384`) rồi gửi nửa khóa của mình. Mỗi bên ghép nửa khóa nhận được với phần bí mật của riêng mình để tính ra cùng một bí mật chung, rồi từ đó ra các khóa phiên; người nghe lén chỉ có hai nửa công khai thì không tính lại được (tính chất của phép trao đổi khóa, bài không chứng minh). Trong lần chạy, các bí mật phiên không xuất hiện trong byte ghi được, và khác nhau giữa hai kết nối. Từ thông điệp kế tiếp, mọi thứ đã mã hóa.

**Chứng chỉ và chữ ký.** Máy chủ gửi chứng chỉ (có tên và khóa công khai), rồi thông điệp `CertificateVerify`: một chữ ký bằng khóa riêng, chứng minh nó giữ khóa riêng ứng với chứng chỉ. Trình duyệt kiểm: chữ ký đúng, chứng chỉ do một tổ chức nó tin ký, tên trong chứng chỉ khớp tên đã định nối. Kiểm hỏng thì một ứng dụng đúng cách dừng bắt tay: chứng chỉ tự tạo mà máy khách không tin cho `self-signed certificate`, tên không khớp cho `hostname mismatch`. Công cụ thử `openssl s_client` chỉ dừng khi có thêm `-verify_return_error`; tài liệu OpenSSL nói rõ đó là công cụ thử, không phải mẫu cho ứng dụng.

**Finished.** Mỗi bên gửi một thông điệp `Finished`. Theo tài liệu OpenSSL, bắt tay xong khi một bên đã gửi và đã nhận `Finished`; ở TLS 1.3 máy chủ gửi trước.

**Dữ liệu.** Từ đây yêu cầu và phản hồi HTTP đi trong các bản ghi mã hóa bằng khóa phiên. Đó là khóa đối xứng (một khóa cho cả mã hóa lẫn giải mã), hợp với lượng dữ liệu lớn vì chạy hiệu quả (MDN).

**Nhìn được gì trên đường dây?** Chương trình ghi byte cho thấy ClientHello và ServerHello đi nguyên văn. Sau ServerHello, các bản ghi chứa phần còn lại của bắt tay có loại ngoài là ApplicationData, và chứng chỉ không tìm thấy trong byte ghi được. Ở TLS 1.2 thì ngược lại: chứng chỉ đi nguyên văn (xem “Xem sâu hơn”).

## Giới hạn cần nhớ

HTTPS bảo vệ đoạn đường giữa trình duyệt và máy chủ, không hơn.

**Tên máy chủ vẫn lộ.** ClientHello đi nguyên văn, nên người nghe lén thấy tên (SNI): ở cả hai phiên bản TLS, chuỗi `localhost` tìm thấy trong byte máy khách gửi đi. Địa chỉ IP của máy chủ cũng không giấu được vì gói tin cần địa chỉ đích (hiểu biết chung, không thử). Tiêu đề mỗi bản ghi cho thấy cả độ dài: bản ghi chứa trang phản hồi dài 4348 byte trong lần chạy TLS 1.3.

**Trang vẫn có thể không đáng tin.** Chứng chỉ nói một tổ chức đã xác nhận khóa này thuộc về tên này; tài liệu OpenSSL không nói chủ trang trung thực hay không. Chứng chỉ cho `localhost` ở đây tạo trong vài giây; một trang lừa đảo có tên miền riêng thường vẫn xin được chứng chỉ cho tên miền đó (hiểu biết chung, không thử).

**Máy chủ vẫn thấy hết.** TLS kết thúc ở máy chủ: máy chủ thử đã giải mã được yêu cầu `GET /` và trả lời nó. Máy chủ lưu, chia sẻ hay làm lộ dữ liệu đó sau này là chuyện nằm ngoài HTTPS.

## Nhìn hình trả lời

Bạn mở một trang HTTPS ở quán cà phê, còn người ngồi cạnh ghi lại mọi gói tin trên mạng Wi-Fi. Theo khung 2 và khung 3 của hình, họ đọc được gì, không đọc được gì, và họ sửa lén một gói thì sao?

<details>
<summary>Xem đáp án</summary>

Họ đọc được ClientHello (nên biết tên máy chủ), ServerHello, địa chỉ IP của máy chủ và độ dài các bản ghi. Họ không đọc được yêu cầu và phản hồi HTTP: trong lần chạy, dòng `GET / HTTP/1.0` và đầu phản hồi không tìm thấy trong byte ghi được. Với TLS 1.3, chứng chỉ cũng đã mã hóa; với TLS 1.2 thì chứng chỉ đi nguyên văn.
Gói bị sửa dù chỉ một bit thì bên nhận ngắt kết nối (`bad record mac` trong lần thử) thay vì nhận chữ sai. Họ cũng không giả làm máy chủ chỉ bằng cách mở một máy chủ khác: trình duyệt kiểm chứng chỉ và tên, và chứng chỉ tự tạo bị từ chối (`self-signed certificate`) trừ khi chính máy khách đã chọn tin nó.

</details>

<details>
<summary>Xem sâu hơn: lần chạy thử và điều đã chỉnh so với bài nguồn</summary>

**Cách chạy.** Chứng chỉ dùng một lần: `openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" -days 1`. Máy chủ: `openssl s_server -accept 127.0.0.1:14443 -www`, tắt sau khi thử. Máy khách: `openssl s_client` với `-tls1_3` hoặc `-tls1_2`, kèm `-trace` (và `-msg`), `-CAfile` trỏ vào chính chứng chỉ tạm và `-verify_return_error`. Một chương trình Python nhỏ do người biên soạn viết đứng giữa, chuyển tiếp từng byte và ghi lại chúng; việc “tìm thấy hay không” là tìm chuỗi trong các byte ghi được. Mỗi cấu hình chạy ít lần; không có phép đo nào lặp lại đủ để gọi là thống kê.

**TLS 1.3** (`TLSv1.3`, `TLS_AES_256_GCM_SHA384`, nhóm khóa `x25519`). Thứ tự bản ghi trên đường dây: máy khách gửi ClientHello; máy chủ gửi ServerHello, một bản ghi ChangeCipherSpec 1 byte, rồi bốn bản ghi loại ApplicationData mà `s_client` giải mã và in ra là EncryptedExtensions (một thông điệp nhỏ, không có phần mở rộng nào), Certificate, CertificateVerify và Finished; máy khách gửi ChangeCipherSpec, Finished, rồi yêu cầu HTTP (35 byte); máy chủ gửi hai bản ghi 250 byte mà `s_client` in là NewSessionTicket, rồi trang phản hồi (4348 byte) và cảnh báo đóng kết nối. Trong ClientHello, `s_client` in danh sách nhóm khóa và thuật toán chữ ký như các phần mở rộng riêng; tên bộ mã của TLS 1.3 chỉ ghi phần mã hóa dữ liệu và hàm băm.

**TLS 1.2** (`TLSv1.2`, `ECDHE-ECDSA-AES256-GCM-SHA384`, khóa tạm `x25519`). Máy khách gửi ClientHello; máy chủ gửi ServerHello, Certificate, ServerKeyExchange (có khóa trao đổi và chữ ký) và ServerHelloDone; máy khách gửi ClientKeyExchange, ChangeCipherSpec và Finished; máy chủ gửi NewSessionTicket, ChangeCipherSpec và Finished; rồi mới tới dữ liệu HTTP. Chứng chỉ (413 byte) và chuỗi `localhost` tìm thấy nguyên văn trong byte máy chủ gửi đi. Finished có loại ngoài vẫn là Handshake; việc nó đã mã hóa là suy luận từ vị trí sau ChangeCipherSpec, không thử giải mã. Đọc từ thứ tự thông điệp: ở TLS 1.3 máy khách gửi yêu cầu sau một lượt trả lời của máy chủ, ở TLS 1.2 sau hai lượt.

**Các thử khác.** (1) Không chỉ định phiên bản, `s_client` và `s_server` dùng TLS 1.3. (2) Tắt kiểm chứng chỉ ở máy khách (không có `-CAfile`, không có `-verify_return_error`): `openssl` in `self-signed certificate` nhưng vẫn nối, trang vẫn trả về và `GET` không tìm thấy trên đường, tức kênh vẫn mã hóa dù không biết đối phương là ai; thêm `-verify_return_error` thì kết nối bị ngắt. Đổi tên cần khớp (`-verify_hostname`) thành một tên khác cho `hostname mismatch` và cũng bị ngắt. (3) Đổi một bit của bản ghi trang phản hồi: TLS 1.3 và TLS 1.2 đều báo `decryption failed or bad record mac`, máy khách không in trang nào. (4) Với `-keylogfile`, năm bí mật của TLS 1.3 và một bí mật của TLS 1.2 (mỗi cái 48 byte) đều không có trong byte ghi được và không trùng giữa hai kết nối.

**Điều đã chỉnh so với bài nguồn.** Phần thân bài nguồn chỉ có bốn dòng giới thiệu; bài này viết lại phần nội dung và không dùng ảnh của nguồn. Nguồn gọi là “SSL handshake”; bài này gọi là bắt tay TLS vì SSL là tên cũ và TLS 1.3 hay 1.2 là thứ đang chạy. Nguồn nói HTTPS bảo vệ dữ liệu khỏi kẻ nghe lén “và các vụ lộ dữ liệu”, và mã hóa cùng chứng chỉ tạo thành “lá chắn không thể phá”; bài này nói HTTPS chỉ bảo vệ dữ liệu đang đi, máy chủ vẫn thấy hết, tên máy chủ và độ dài vẫn lộ. Nguồn đặt chứng chỉ cạnh mã hóa như một thứ tạo lá chắn; phép thử cho thấy mã hóa đến từ việc trao đổi khóa và vẫn chạy khi không kiểm chứng chỉ, còn chứng chỉ dùng để biết đang nói chuyện với ai. Nguồn dùng hình ảnh “đường hầm mã hóa”; ở đây các bản ghi TLS đi trên chính kết nối TCP, theo tài liệu OpenSSL TLS là lớp bảo mật đặt trên giao thức tầng dưới, thường là TCP, chứ không phải một đường riêng. Nguồn dành một ý cho HTML và cái tên “hyper text”; HTML mô tả cấu trúc trang, không liên quan tới mã hóa.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/https-ssl-handshake-and-data-encryption-explained-to-kids.md): bốn dòng giới thiệu về HTTPS, bắt tay SSL, truyền dữ liệu qua “đường hầm” và HTML.
- [MDN — Transport Layer Security (TLS)](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/defenses/transport_layer_security/index.md): ba điều TLS bảo đảm, các việc bắt tay thống nhất, dữ liệu mã hóa bằng khóa chung sau bắt tay. Đọc tệp ở commit cố định.
- MDN, mục từ điển: [TLS](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/tls/index.md), [HTTPS](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/https/index.md), [SSL](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/ssl/index.md), [Cipher suite](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/cipher_suite/index.md), [Symmetric-key cryptography](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/symmetric-key_cryptography/index.md): TLS là tên mới của SSL, bộ mã, khóa đối xứng. Đọc tệp ở commit cố định.
- [OpenSSL — Giới thiệu SSL/TLS (ossl-guide-tls-introduction)](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man7/ossl-guide-tls-introduction.pod): các thông điệp ClientHello, ServerHello, Finished, vai trò chứng chỉ và chữ ký của máy chủ, các phiên bản TLS, TLS đặt trên TCP. Đọc tệp ở commit cố định.
- OpenSSL, trang lệnh: [s_client](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man1/openssl-s_client.pod.in), [s_server](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man1/openssl-s_server.pod.in), [req](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man1/openssl-req.pod.in): các tùy chọn `-msg`, `-trace`, `-servername`, `-verify_return_error`, `-keylogfile`, `-www`, `req -x509`. Đọc tệp ở commit cố định.

Đã đọc nguồn ngày 2026-10-18. Các số liệu chạy bằng `openssl` 3.0.13 và một chương trình ghi byte do người biên soạn viết, trên một máy, vài lần cho mỗi cấu hình; chúng chỉ minh họa, không phải chuẩn so sánh. Cách chia ba khung của hình, thứ tự trình bày và các phép thử là của người biên soạn. Bài viết và hình được thiết kế độc lập.

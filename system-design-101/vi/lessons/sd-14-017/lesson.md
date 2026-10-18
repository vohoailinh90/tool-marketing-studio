# HTTPS và bắt tay TLS: dựng kênh mã hóa thế nào?

**HTTPS là HTTP chạy bên trong một lớp mã hóa tên là TLS. Lớp đó thêm ba thứ: giữ kín nội dung, phát hiện nội dung bị sửa trên đường, và cho trình duyệt biết máy chủ có đúng là máy chủ của tên miền nó định nối tới hay không.**
Cả ba được dựng trong một bước “bắt tay” ngay đầu kết nối. HTTPS không làm một trang web trở nên đáng tin.
Bài này đi qua bắt tay TLS ở mức nhìn được: thông điệp nào, theo thứ tự nào, thứ nào đi nguyên văn và thứ nào đã mã hóa. Số liệu lấy từ một lần chạy thử cục bộ với `openssl` (cách chạy ở mục “Xem sâu hơn”) và từ tài liệu của MDN và OpenSSL. Chứng chỉ và chữ ký xem ở [bài sd-14-014](../sd-14-014/lesson.md) và [bài sd-14-015](../sd-14-015/lesson.md); bài không dạy lại chúng, cũng không bàn cấu hình máy chủ hay các tính năng TLS mới hơn.

![Bốn khung xếp dọc. Khung một: HTTPS thêm ba thứ cho HTTP, gồm giữ kín nội dung, phát hiện nội dung bị sửa trên đường và xác thực máy chủ bằng chứng chỉ. Khung hai và ba: bắt tay TLS 1.3 rút gọn giữa trình duyệt và máy chủ. ClientHello và ServerHello đi nguyên văn; chứng chỉ, CertificateVerify và hai thông điệp Finished sau đó được mã hóa (hình bỏ qua bản ghi ChangeCipherSpec 1 byte, không chứa nội dung bắt tay). Rồi yêu cầu HTTP và phản hồi HTTP, mỗi chiều mã hóa bằng một khóa riêng. Khung bốn, giới hạn của HTTPS: tên máy chủ vẫn nằm trong ClientHello, chứng chỉ không làm một trang trở nên đáng tin, máy chủ vẫn đọc được mọi thứ bạn gửi và độ dài từng gói dữ liệu vẫn lộ.](../../diagrams/sd-14-017-main.svg)

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

**Khung 1 · HTTPS thêm gì.** Theo MDN, TLS giữ an toàn cho kết nối theo ba cách: mã hóa (người ngoài không đọc được), toàn vẹn (không ai sửa lén được mà không bị phát hiện) và xác thực (trên web thường chỉ máy chủ chứng minh mình với trình duyệt). HTTPS là HTTP chạy trên TLS: dòng yêu cầu và phản hồi vẫn như cũ, chỉ nằm trong các bản ghi mã hóa. Thử: qua HTTP thường, dòng `GET / HTTP/1.0` nằm nguyên văn trong các byte ghi được; qua TLS thì không tìm thấy nó, cũng không thấy phản hồi. Đổi một bit của bản ghi trên đường, TLS ngắt kết nối (`bad record mac`); HTTP thường nhận chữ đã bị đổi mà không biết. SSL là tên các phiên bản đầu; MDN nói TLS đã thay thế nó. Hình vẽ TLS 1.3; theo tài liệu OpenSSL, TLS 1.3 và 1.2 là hai phiên bản phổ biến nhất.

**Khung 2 và 3 · Bắt tay.**

**ClientHello.** Trình duyệt mở đầu và gửi nguyên văn: các bộ mã (cipher suite, tức tổ hợp thuật toán hai bên có thể dùng) nó hỗ trợ, tên máy chủ muốn nối (SNI), và một “nửa khóa” (key share) cho nhóm trao đổi khóa `x25519`.

**ServerHello.** Máy chủ chọn bộ mã (lần chạy: `TLS_AES_256_GCM_SHA384`) và gửi nửa khóa của mình. Mỗi bên ghép nửa khóa nhận được với phần bí mật riêng để tính ra cùng một bí mật chung, rồi từ đó ra các khóa mã hóa (xem “Dữ liệu”); người nghe lén chỉ có hai nửa công khai thì không tính lại được (tính chất của phép trao đổi khóa, bài không chứng minh). Sau ServerHello, các thông điệp có nội dung của bắt tay (EncryptedExtensions, Certificate, CertificateVerify, Finished) đã được mã hóa: chứng chỉ không còn tìm thấy trong byte ghi được (ở TLS 1.2 nó đi nguyên văn, xem “Xem sâu hơn”). Thứ còn thấy được là một bản ghi ChangeCipherSpec dài 1 byte, không chứa nội dung bắt tay; theo tài liệu OpenSSL, đó là bản ghi giả, gửi theo mặc định để các thiết bị trung gian không hiểu TLS 1.3 không cắt kết nối.

**Chứng chỉ và chữ ký.** Máy chủ gửi chứng chỉ (có tên và khóa công khai), rồi `CertificateVerify`: chữ ký bằng khóa riêng, chứng minh nó giữ khóa riêng ứng với chứng chỉ. Trình duyệt kiểm chữ ký, kiểm chứng chỉ do một tổ chức nó tin ký, và kiểm tên trong chứng chỉ khớp tên đã định nối. Kiểm hỏng thì ứng dụng đúng cách dừng bắt tay (trong lần thử: `self-signed certificate`, `hostname mismatch`).

**Finished.** Mỗi bên gửi một thông điệp `Finished`; theo tài liệu OpenSSL, bắt tay xong khi một bên đã gửi và đã nhận `Finished`.

**Dữ liệu.** Từ bí mật chung, mỗi bên tính ra các khóa đối xứng để mã hóa dữ liệu, một khóa cho mỗi chiều: chiều từ trình duyệt tới máy chủ (yêu cầu HTTP) và chiều ngược lại (phản hồi HTTP). Bên gửi mã hóa bằng khóa của chiều đó, bên nhận giải mã bằng chính khóa ấy; “đối xứng” nghĩa là một khóa làm được cả hai việc, ở hai đầu. Khóa đối xứng hợp với lượng dữ liệu lớn vì chạy hiệu quả (MDN). Trong lần thử, nhật ký khóa của TLS 1.3 ghi hai bí mật khác nhau, một cho chiều từ máy khách và một cho chiều từ máy chủ; các khóa mã hóa cụ thể được tính ra từ chúng (hiểu biết chung, không thử).

## Giới hạn cần nhớ

HTTPS bảo vệ đoạn đường giữa trình duyệt và máy chủ, không hơn.

**Tên máy chủ và độ dài vẫn lộ.** ClientHello đi nguyên văn nên người nghe lén thấy tên (SNI): chuỗi `localhost` tìm thấy trong byte máy khách gửi ở cả hai phiên bản TLS. Tiêu đề mỗi bản ghi cho thấy độ dài (bản ghi trang phản hồi: 4348 byte). Địa chỉ IP của máy chủ cũng không giấu được (hiểu biết chung, không thử).

**Trang vẫn có thể không đáng tin.** Chứng chỉ chỉ nói một tổ chức đã xác nhận khóa này thuộc về tên này; tài liệu OpenSSL không nói chủ trang có trung thực hay không. Chứng chỉ cho `localhost` ở đây tạo trong vài giây; một trang lừa đảo có tên miền riêng thường vẫn xin được chứng chỉ cho tên đó (hiểu biết chung, không thử).

**Máy chủ vẫn thấy hết.** TLS kết thúc ở máy chủ: máy chủ thử giải mã được yêu cầu `GET /` và trả lời nó. Việc nó làm gì với dữ liệu sau đó nằm ngoài HTTPS.

## Nhìn hình trả lời

Bạn mở một trang HTTPS ở quán cà phê, còn người ngồi cạnh ghi lại mọi gói tin trên mạng Wi-Fi. Theo các khung bắt tay (2 và 3) và khung giới hạn (4) của hình, họ đọc được gì, không đọc được gì, và họ sửa lén một gói thì sao?

<details>
<summary>Xem đáp án</summary>

Họ đọc được ClientHello (nên biết tên máy chủ), ServerHello, hai bản ghi ChangeCipherSpec 1 byte (không có nội dung bắt tay), địa chỉ IP của máy chủ và độ dài các bản ghi. Họ không đọc được yêu cầu và phản hồi HTTP: trong lần chạy, dòng `GET / HTTP/1.0` và đầu phản hồi không tìm thấy trong byte ghi được. Với TLS 1.3 chứng chỉ cũng đã mã hóa; với TLS 1.2 chứng chỉ đi nguyên văn.
Gói bị sửa dù chỉ một bit thì bên nhận ngắt kết nối (`bad record mac` trong lần thử) thay vì nhận chữ sai. Họ cũng không giả làm máy chủ chỉ bằng cách mở một máy chủ khác: trình duyệt kiểm chứng chỉ và tên, và chứng chỉ tự tạo bị từ chối (`self-signed certificate`) trừ khi chính máy khách đã chọn tin nó.

</details>

<details>
<summary>Xem sâu hơn: lần chạy thử và điều đã chỉnh so với bài nguồn</summary>

**Cách chạy.** Chứng chỉ dùng một lần: `openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" -days 1`. Máy chủ: `openssl s_server -accept 127.0.0.1:14443 -www`, tắt sau khi thử. Máy khách: `openssl s_client` với `-tls1_3` hoặc `-tls1_2`, kèm `-trace`, `-CAfile` trỏ vào chứng chỉ tạm và `-verify_return_error`. Một chương trình Python nhỏ do người biên soạn viết đứng giữa và ghi lại từng byte; “tìm thấy” nghĩa là tìm một chuỗi trong các byte đó. Mỗi cấu hình chạy ít lần, chỉ để minh họa.

**TLS 1.3** (`TLSv1.3`, `TLS_AES_256_GCM_SHA384`, nhóm khóa `x25519`). Trên đường dây: ClientHello; ServerHello, một bản ghi ChangeCipherSpec 1 byte (bản ghi giả theo tài liệu OpenSSL), rồi bốn bản ghi loại ApplicationData mà `s_client` giải mã và in là EncryptedExtensions (không có phần mở rộng nào), Certificate, CertificateVerify và Finished; máy khách gửi ChangeCipherSpec (cũng 1 byte), Finished và yêu cầu HTTP; máy chủ gửi hai NewSessionTicket, trang phản hồi và cảnh báo đóng kết nối. Tên bộ mã của TLS 1.3 chỉ ghi phần mã hóa dữ liệu và hàm băm; nhóm khóa và thuật toán chữ ký nằm ở các phần mở rộng riêng của ClientHello.

**TLS 1.2** (`TLSv1.2`, `ECDHE-ECDSA-AES256-GCM-SHA384`). ClientHello; ServerHello, Certificate, ServerKeyExchange (khóa trao đổi kèm chữ ký) và ServerHelloDone; ClientKeyExchange, ChangeCipherSpec, Finished; NewSessionTicket, ChangeCipherSpec, Finished; rồi tới dữ liệu HTTP. Chứng chỉ (413 byte) và chuỗi `localhost` thấy nguyên văn trong byte máy chủ gửi. Finished có loại ngoài vẫn là Handshake; việc nó đã mã hóa là suy luận từ vị trí sau ChangeCipherSpec, không thử giải mã. Đọc từ thứ tự thông điệp: ở TLS 1.3 máy khách gửi yêu cầu sau một lượt trả lời của máy chủ, ở TLS 1.2 sau hai lượt.

**Các thử khác.** (1) Tắt kiểm chứng chỉ (không có `-CAfile`, không có `-verify_return_error`): `openssl` in `self-signed certificate` nhưng vẫn nối, trang vẫn về và `GET` không thấy trên đường, tức kênh vẫn mã hóa dù không biết đối phương là ai; thêm `-verify_return_error` thì bị ngắt, và tên cần khớp khác đi (`-verify_hostname`) cho `hostname mismatch`, cũng bị ngắt. Tài liệu OpenSSL nói `s_client` là công cụ thử, không phải mẫu cho ứng dụng. (2) Đổi một bit của bản ghi trang phản hồi: cả TLS 1.3 và 1.2 báo `decryption failed or bad record mac`, máy khách không in trang nào. (3) Với `-keylogfile`, các bí mật phiên (mỗi cái 48 byte) không có trong byte ghi được và không trùng giữa hai kết nối. (4) Nhật ký khóa của TLS 1.3 có năm dòng: `CLIENT_HANDSHAKE_TRAFFIC_SECRET`, `SERVER_HANDSHAKE_TRAFFIC_SECRET`, `CLIENT_TRAFFIC_SECRET_0`, `SERVER_TRAFFIC_SECRET_0` và `EXPORTER_SECRET`, đều 48 byte và đôi một khác nhau trong cùng một kết nối: mỗi chiều có bí mật riêng, cả cho bắt tay lẫn cho dữ liệu. Nhật ký của TLS 1.2 chỉ có một dòng `CLIENT_RANDOM` mang một bí mật 48 byte, trùng giá trị `Master-Key` mà `s_client` in ra; nó không cho thấy khóa của từng chiều. Việc TLS 1.2 cũng tách khóa theo chiều từ bí mật đó là hiểu biết chung, không thử.

**Điều đã chỉnh so với bài nguồn.** Phần thân bài nguồn chỉ có bốn dòng giới thiệu; bài này viết lại nội dung và không dùng ảnh của nguồn. Nguồn gọi là “SSL handshake”; ở đây là bắt tay TLS vì SSL là tên cũ. Nguồn nói HTTPS bảo vệ khỏi nghe lén “và các vụ lộ dữ liệu” và tạo “lá chắn không thể phá” cùng chứng chỉ; bài này nói HTTPS chỉ bảo vệ dữ liệu đang đi, máy chủ vẫn thấy hết, tên máy chủ và độ dài vẫn lộ, và phép thử cho thấy kênh vẫn mã hóa khi không kiểm chứng chỉ (chứng chỉ để biết đang nói với ai). “Đường hầm mã hóa” là hình ảnh: các bản ghi TLS đi trên chính kết nối TCP, theo OpenSSL là lớp bảo mật đặt trên giao thức tầng dưới. Ý về HTML và cái tên “hyper text” không liên quan tới mã hóa; HTML mô tả cấu trúc trang.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/https-ssl-handshake-and-data-encryption-explained-to-kids.md): bốn dòng giới thiệu về HTTPS, bắt tay SSL, “đường hầm” và HTML.
- [MDN — Transport Layer Security (TLS)](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/defenses/transport_layer_security/index.md): ba điều TLS bảo đảm, các việc bắt tay thống nhất, khóa chung mã hóa dữ liệu. Đọc tệp ở commit cố định.
- MDN, mục từ điển [TLS](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/tls/index.md), [HTTPS](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/https/index.md), [SSL](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/ssl/index.md), [Cipher suite](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/cipher_suite/index.md), [Symmetric-key cryptography](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/symmetric-key_cryptography/index.md): TLS là tên mới của SSL, bộ mã, khóa đối xứng.
- [OpenSSL — Giới thiệu SSL/TLS](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man7/ossl-guide-tls-introduction.pod): thông điệp ClientHello, ServerHello, Finished, vai trò chứng chỉ và chữ ký, các phiên bản TLS, TLS đặt trên TCP. Đọc tệp ở commit cố định.
- OpenSSL, trang lệnh [s_client](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man1/openssl-s_client.pod.in), [s_server](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man1/openssl-s_server.pod.in), [req](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man1/openssl-req.pod.in): các tùy chọn đã dùng cho lần chạy thử.

Đã đọc nguồn ngày 2026-10-18. Các số liệu chạy bằng `openssl` 3.0.13 và một chương trình ghi byte do người biên soạn viết, trên một máy, vài lần cho mỗi cấu hình; chúng chỉ minh họa, không phải chuẩn so sánh. Cách chia ba khung của hình, thứ tự trình bày và các phép thử là của người biên soạn. Bài viết và hình được thiết kế độc lập.

# HTTPS thương lượng thế nào? Bộ mã, phiên bản và khóa đối xứng

**Trước khi mã hóa một byte HTTP, hai bên phải thỏa thuận cách mã hóa: client đưa danh sách những gì nó hỗ trợ, máy chủ chọn từ danh sách đó, và nếu không có mục chung thì kết nối dừng ngay bằng một cảnh báo.** Chọn xong, hai bên cùng tính ra khóa đối xứng để mã hóa dữ liệu HTTP: từ một bí mật chung, mỗi chiều (client gửi, máy chủ gửi) có khóa riêng.

Bài chỉ nói về bước thương lượng: phiên bản TLS, bộ mã, nhóm trao đổi khóa, thuật toán chữ ký. Việc máy chủ chứng minh danh tính nằm ở [bài sd-14-014](../sd-14-014/lesson.md) (chứng chỉ) và [bài sd-14-015](../sd-14-015/lesson.md) (chữ ký số). Kết quả trong bài là một lần chạy OpenSSL 3.0.13 trên máy người viết (cục bộ, chứng chỉ tự ký dùng một lần), không phải trình duyệt hay máy chủ thật.

![Ba khung dọc. Khung một: client gửi danh sách phiên bản, bộ mã, nhóm khóa, chữ ký; máy chủ chọn mỗi loại một mục hoặc gửi cảnh báo rồi dừng. Khung hai: có điểm chung thì hai bên cùng tính ra khóa đối xứng, mỗi chiều một khóa, và HTTP đi qua bộ mã đã chọn; không có thì kết nối dừng. Khung ba: máy chủ chỉ chọn mục client đã đưa; thứ tự ưu tiên mặc định là của client; HTTP không đổi dù TLS 1.2 hay 1.3.](../../diagrams/sd-14-032-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ trả lời.
- **HTTPS** (HyperText Transfer Protocol Secure) — HTTP chạy trên TLS, nội dung được mã hóa.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa giữ kín dữ liệu giữa client và máy chủ.
- **AES** (Advanced Encryption Standard) — chuẩn mã hóa tiên tiến, thuật toán mã hóa đối xứng; 128 hay 256 là số bit bí mật của khóa.
- **GCM** (Galois/Counter Mode) — chế độ Galois/Counter: cách dùng AES để mã hóa thông điệp dài hơn một khối.
- **SHA** (Secure Hash Algorithm) — họ thuật toán băm: biến dữ liệu bất kỳ thành chuỗi cố định; SHA-256 là một loại.
- **AEAD** (Authenticated Encryption with Associated Data) — mã hóa có xác thực kèm dữ liệu liên kết: một phép vừa mã hóa vừa gắn thẻ để phát hiện dữ liệu bị sửa; GCM là một chế độ như vậy.
- **RSA** (Rivest-Shamir-Adleman) — thuật toán khóa công khai đặt theo ba tác giả, dùng để ký lẫn mã hóa.
- **ECDHE** (Elliptic Curve Diffie-Hellman Ephemeral) — cách hai bên cùng tính ra khóa chung từ các khóa tạm thời trên đường cong elliptic.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng về bảo mật ứng dụng, có hướng dẫn mà bài dùng để đối chiếu.

## Đọc hình

**Khung 1 · Client đưa danh sách.** `ClientHello`, thông điệp đầu tiên của TLS, mang bốn danh sách. Với `openssl s_client -trace` mặc định, máy thử đưa ra 2 phiên bản (TLS 1.3, TLS 1.2); 31 mục bộ mã (3 của TLS 1.3, 27 của TLS 1.2, 1 mục tín hiệu đặc biệt); 10 nhóm khóa, `x25519` đứng đầu; 20 thuật toán chữ ký. Đó là danh sách của OpenSSL, không phải của trình duyệt.

**Đọc tên bộ mã.** Theo tài liệu Mozilla, bộ mã gồm trao đổi khóa, xác thực, mã hóa dữ liệu và mã xác thực thông điệp; tài liệu đó đọc `ECDHE-RSA-AES128-GCM-SHA256` là ECDHE, RSA, AES-128 chế độ GCM và SHA-256 làm mã xác thực. Đọc kỹ hơn: GCM là kiểu mã hóa có xác thực (AEAD), tự gắn thẻ phát hiện sửa cho từng bản ghi, nên `openssl ciphers -v` in `Mac=AEAD` cho bộ này, còn `Mac=SHA256` chỉ hiện ở bộ không dùng GCM như `ECDHE-RSA-AES128-SHA256` (đã chạy). Với bộ GCM, SHA-256 không phải mã xác thực của bản ghi mà là hàm băm dùng trong bắt tay: tài liệu OpenSSL nói hàm băm của bắt tay có thể khác hàm băm tính mã xác thực bản ghi. Tên của TLS 1.3 ngắn hơn, như `TLS_AES_256_GCM_SHA384`: `openssl ciphers -v` in `Kx=any Au=any` cho chúng, và tài liệu OpenSSL dùng "any" khi bộ mã không buộc thuật toán trao đổi khóa hay xác thực nào, như ở TLS 1.3.

**Khung 1 · Máy chủ chọn.** Mỗi loại một mục:

- Phiên bản: cao nhất cả hai cùng hỗ trợ (tài liệu OpenSSL). Hai bên mặc định ra TLS 1.3; client giới hạn `-tls1_2` ra TLS 1.2.
- Bộ mã: theo tài liệu `s_server`, mặc định là mục đầu tiên trong danh sách client mà máy chủ cũng có. Máy chủ có ba bộ TLS 1.3: client xếp AES-256 đầu thì ra `TLS_AES_256_GCM_SHA384`, xếp ChaCha20 đầu thì ra `TLS_CHACHA20_POLY1305_SHA256`; bật `-serverpref` thì cả hai lần ra `TLS_AES_128_GCM_SHA256`, bộ đứng đầu danh sách máy chủ.
- `ServerHello` chỉ ghi lựa chọn: một bộ mã, TLS 1.3 trong `supported_versions`, nhóm `x25519`.

**Khung 2 · Hai kết cục.** Có điểm chung: hai bên cùng tính ra khóa đối xứng, mỗi chiều một khóa, và HTTP đi qua bộ mã đã chọn. Trong lần thử, nhật ký khóa của TLS 1.3 (`-keylogfile`) có hai bí mật lưu lượng khác nhau, `CLIENT_TRAFFIC_SECRET_0` và `SERVER_TRAFFIC_SECRET_0`; nhật ký của TLS 1.2 chỉ có một bí mật chủ (`CLIENT_RANDOM`), nên không cho thấy khóa từng chiều (TLS 1.2 cũng dẫn khóa từng chiều từ bí mật đó: hiểu biết chung, không thử). Không có: máy chủ gửi cảnh báo `fatal` kèm mã lý do rồi dừng. Bốn cách "không chung" đã thử:

- Phiên bản (máy chủ TLS 1.2, client TLS 1.3, và ngược lại): `tlsv1 alert protocol version`, mã 70; máy chủ ghi `unsupported protocol`.
- Bộ mã: `sslv3 alert handshake failure`, mã 40; máy chủ ghi `no shared cipher`.
- Nhóm khóa (máy chủ chỉ `P-256`, client chỉ `X25519`): mã 40; máy chủ ghi `no suitable key share`.
- Chữ ký (chứng chỉ khóa elliptic, client chỉ nhận chữ ký RSA): mã 40; máy chủ ghi `no suitable signature algorithm`.

Chữ `sslv3` vẫn xuất hiện dù client chỉ đưa TLS 1.3: đó là nhãn trong lời của OpenSSL, không phải phiên bản đã dùng. Câu trả lời của máy chủ chỉ là một cảnh báo dài 2 byte.

**Khung 3 · Cần nhớ.** Mọi mục chọn đều nằm trong danh sách client gửi. Thứ tự ưu tiên mặc định của OpenSSL là của client, đổi bằng `-serverpref`; phần mềm khác tùy cách cài đặt. HTTP không đổi: một yêu cầu `GET` tới máy chủ mẫu qua TLS 1.2 rồi TLS 1.3 nhận về cùng 67 byte, giống từng byte.

## Giới hạn cần nhớ

Kết nối chỉ mạnh bằng lựa chọn yếu nhất mà máy chủ còn chấp nhận. Với chứng chỉ RSA, máy chủ mặc định vẫn nhận bộ `AES128-GCM-SHA256` (`Kx=RSA`, chuyển khóa bằng RSA) ở TLS 1.2; máy chủ chỉ cho các bộ ECDHE từ chối cùng client đó (`no shared cipher`). OWASP khuyên TLS 1.3 làm mặc định, TLS 1.2 nếu cần tương thích, tắt TLS 1.0 và 1.1, và tắt các bộ `TLS_RSA_*` vì không có forward secrecy (theo cách hiểu chung: lộ khóa riêng về sau không làm lộ các phiên đã ghi lại).

## Nhìn hình trả lời

Máy chủ chỉ cho phép TLS 1.2 với đúng một bộ mã, `ECDHE-ECDSA-AES128-GCM-SHA256`. Client chỉ đưa `ECDHE-ECDSA-AES256-GCM-SHA384`. Theo hình, chuyện gì xảy ra, và client cần thêm gì để vào được?

<details>
<summary>Xem đáp án</summary>

Không có bộ mã chung nên rơi vào nhánh "Không có điểm chung": client in `sslv3 alert handshake failure` (mã 40), máy chủ ghi `no shared cipher`. Thêm `ECDHE-ECDSA-AES128-GCM-SHA256` vào danh sách của client là vào được, vì đó là mục chung duy nhất; đặt ở đầu hay cuối đều được (hai thứ tự đã thử).

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

- **Bước 3 của nguồn** (client sinh khóa phiên, mã hóa bằng khóa công khai, máy chủ giải mã bằng khóa riêng) chỉ là một họ bộ mã của TLS 1.2: chuyển khóa bằng RSA. Danh sách mặc định của client thử có 6 bộ `TLS_RSA_*`; các bộ TLS 1.3 trong tài liệu OpenSSL không có bộ nào như vậy. Với `AES128-GCM-SHA256`, `s_client` không in `Server Temp Key` và `Signature type`; với `ECDHE-RSA-AES128-GCM-SHA256` nó in `Server Temp Key: X25519, 253 bits` và `Signature type: RSA-PSS` (tài liệu OpenSSL: bộ mã dùng RSA key exchange không có chữ ký). Cách RSA chuyển khóa hoạt động là hiểu biết chung của tác giả, chưa đối chiếu văn bản tiêu chuẩn. Ở bộ ECDHE, máy chủ ký để chứng minh nó giữ khóa riêng (hướng dẫn OpenSSL).
- **Phiên bản và server hello**: nguồn nói client gửi "phiên bản mới nhất" và `ServerHello` cho biết có hỗ trợ không. Thực tế `ClientHello` gửi cả danh sách trong `supported_versions`, còn trường phiên bản cũ vẫn ghi `0x303 (TLS 1.2)`, `ServerHello` cũng vậy dù đã chọn TLS 1.3 (lý do không có trong tài liệu đã đọc). `ServerHello` nêu lựa chọn; không có thì là cảnh báo.
- **Lý do của nguồn**: "chỉ thấy mã nhị phân" không phải điểm chính; tài liệu Mozilla nêu ba việc TLS làm: mã hóa, toàn vẹn, xác thực. Về khóa đối xứng, nó nêu hai lý do: khóa công khai thường chậm hơn nhiều, và cỡ thông điệp mã hóa được tỉ lệ với cỡ khóa. Ý "chỉ một chiều" của nguồn không có trong trang nào tôi đọc nên bài không dùng.
- **Nhóm khóa lệch**: client `X25519:P-256`, máy chủ chỉ `P-256` vẫn thành công, nhưng trace cho thấy `ClientHello` được gửi hai lần; lần hai kèm khóa cho P-256.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-https-work.md)
- Tài liệu Mozilla (MDN): [Transport Layer Security](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/defenses/transport_layer_security/index.md), [Cipher suite](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/cipher_suite/index.md), [Public-key cryptography](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/public-key_cryptography/index.md).
- [OWASP — Transport Layer Security Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Transport_Layer_Security_Cheat_Sheet.md)
- [OpenSSL — hướng dẫn TLS](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man7/ossl-guide-tls-introduction.pod)
- OpenSSL 3.0.13: [s_server](https://github.com/openssl/openssl/blob/85cf92f55d9e2ac5aacf92bedd33fb890b9f8b4c/doc/man1/openssl-s_server.pod.in), [SSL_CIPHER_get_name](https://github.com/openssl/openssl/blob/85cf92f55d9e2ac5aacf92bedd33fb890b9f8b4c/doc/man3/SSL_CIPHER_get_name.pod), [SSL_get_peer_signature_nid](https://github.com/openssl/openssl/blob/85cf92f55d9e2ac5aacf92bedd33fb890b9f8b4c/doc/man3/SSL_get_peer_signature_nid.pod).

Đã đọc nguồn ngày 2026-10-18. Mọi số là một lần đo trên máy người viết; văn bản tiêu chuẩn của TLS không đọc được nên chưa đối chiếu. Cách chia khung, các thử nghiệm và phần chỉnh so với nguồn là của người viết. Bài viết và hình được thiết kế độc lập.

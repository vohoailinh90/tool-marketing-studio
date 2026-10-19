# Mã hóa đối xứng và bất đối xứng

**Mã hóa đối xứng dùng một khóa chung và rất nhanh. Mã hóa bất đối xứng dùng cặp khóa công khai và khóa riêng, chậm hơn nhiều nhưng không đòi hai bên có sẵn một bí mật chung; hai loại giải hai bài toán khác nhau nên hệ thống thật thường ghép cả hai.**
Bài này so sánh hai loại bằng các lần chạy thử với thư viện `cryptography` 50.0.1 của Python và OpenSSL 3.0.13, dùng khóa tạm trên máy cục bộ. Bài không bàn cách chọn thuật toán cho một sản phẩm hay cách bảo quản khóa. Về khác biệt giữa mã hóa, mã hóa ký tự và token hóa, xem [bài sd-14-002](../sd-14-002/lesson.md); về chữ ký số, xem [bài sd-14-015](../sd-14-015/lesson.md).

![Ba khung xếp dọc. Khung 1, hai loại khóa: đối xứng dùng một khóa chung để mã hóa và giải mã, nhanh, hợp với dữ liệu lớn, nhưng hai bên phải có chung khóa; bất đối xứng dùng cặp khóa, khóa công khai mã hóa và khóa riêng giải mã, chậm, và RSA-2048 mỗi lần mã hóa tối đa 190 byte. Khung 2, ghép lại bốn bước: người gửi tạo khóa AES ngẫu nhiên, mã hóa dữ liệu bằng AES-GCM, gói khóa AES bằng khóa công khai RSA của người nhận; người nhận mở gói bằng khóa riêng rồi giải mã dữ liệu. Khung 3, cần nhớ: không loại nào mặc định an toàn hơn, khóa công khai phải đúng của người nhận, ký số dùng vai ngược lại, một lần thử TLS 1.3 dùng X25519 và AES-256-GCM.](../../diagrams/sd-14-018-main.svg)

## Từ viết tắt

- **AES** (Advanced Encryption Standard) — chuẩn mã hóa tiên tiến: thuật toán mã hóa đối xứng, cùng một khóa để mã hóa và giải mã; AES-256 là khóa dài 256 bit.
- **GCM** (Galois/Counter Mode) — một chế độ hoạt động của mã hóa khối, vừa mã hóa vừa gắn thẻ để phát hiện dữ liệu bị sửa; AES-GCM là cặp thường dùng.
- **RSA** (Rivest-Shamir-Adleman) — tên một thuật toán mã hóa khóa công khai, đặt theo ba tác giả; RSA-2048 là khóa dài 2048 bit.
- **OAEP** (Optimal Asymmetric Encryption Padding) — một cách đệm dữ liệu trước khi mã hóa bằng RSA, có thêm giá trị ngẫu nhiên nên cùng thông điệp mã hóa hai lần cho hai kết quả khác nhau.
- **SHA** (Secure Hash Algorithm) — họ thuật toán băm: biến dữ liệu bất kỳ thành một chuỗi cố định; SHA-256 là một loại trong họ này, ở đây dùng bên trong OAEP.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: giao thức để hai bên bắt tay, thống nhất khóa rồi mã hóa dữ liệu trên đường đi.
- **HTTPS** (HyperText Transfer Protocol Secure) — cách trình duyệt và máy chủ web gửi yêu cầu, trả lời qua một kết nối được bảo vệ bằng TLS, nên nội dung được mã hóa trên đường đi.
- **MiB** (Mebibyte) — mebibyte: đơn vị dung lượng bằng 1.048.576 byte (2 mũ 20), gần bằng một triệu byte.
- **HPKE** (Hybrid Public Key Encryption) — mã hóa khóa công khai lai: một chuẩn gói sẵn việc thống nhất khóa và mã hóa dữ liệu bằng khóa chung, để khỏi tự ghép từng bước.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

Mọi con số dưới đây là một lần chạy trên máy biên soạn, không phải chuẩn so sánh.

**1 · Đối xứng: một khóa chung.** Cùng một khóa mã hóa rồi giải mã. Với AES-256-GCM, mã hóa 1 MiB mất khoảng 0,0007 giây. Cái khó nằm ở chỗ khác: hai bên phải có chung khóa từ trước mà không để lộ cho ai. Nếu n người muốn nhắn riêng từng cặp bằng khóa chung thì cần n(n−1)/2 khóa: 10 người cần 45, 100 người cần 4.950, 1.000 người cần 499.500. Với cặp khóa, mỗi người chỉ cần một cặp (10, 100, 1.000), và khóa công khai phát cho ai cũng được.

**1 · Bất đối xứng: cặp khóa.** Khóa công khai mã hóa, khóa riêng giải mã. Đối tượng khóa công khai trong thư viện có `encrypt` và không có `decrypt`. Cái giá là độ dài: RSA-2048 với OAEP và SHA-256 mã hóa tối đa 190 byte mỗi lần (tính 256 − 2 × 32 − 2; thử 190 byte thì qua, 191 byte thì thư viện báo `ValueError`). OAEP có phần ngẫu nhiên: mã hóa hai lần cùng thông điệp cho hai bản mã khác nhau, cả hai đều giải mã đúng.

**2 · Ghép lại.** Nếu bắt RSA mã hóa cả 1 MiB thì phải cắt thành 5.519 khúc 190 byte: mã hóa mất 0,14 giây, giải mã mất 2,0 giây, so với 0,0007 và 0,0006 giây của AES-256-GCM. Chênh khoảng 200 và 3.300 lần, và bản mã phình lên 1.412.864 byte. Vì vậy cặp khóa chỉ làm việc nhỏ là gói một khóa AES ngẫu nhiên: RSA-OAEP biến khóa 32 byte thành 256 byte. Gửi kèm nonce (số dùng một lần, 12 byte) và bản mã AES-GCM (1 MiB cộng 16 byte thẻ xác thực), tổng chỉ hơn 1 MiB đúng 284 byte. Người nhận mở gói bằng khóa riêng rồi giải mã ra đúng 1 MiB ban đầu. Nhờ thẻ xác thực, sửa một byte của bản mã hoặc dùng sai khóa thì giải mã báo `InvalidTag` chứ không cho ra dữ liệu sai.

## Giới hạn cần nhớ

Đây cũng là nội dung khung 3 của hình. Không loại nào an toàn hơn theo nghĩa chung. Cặp khóa bỏ nhu cầu chia sẻ trước một bí mật, nhưng thêm một nhu cầu khác: biết khóa công khai nào là của ai. Thử: gói khóa AES bằng khóa công khai của Mallory thì Mallory khôi phục đúng khóa đó. Khóa công khai không cần giấu, nhưng đưa nhầm khóa của kẻ gian là trao bí mật cho kẻ gian; chứng chỉ giải việc này (xem [bài sd-14-014](../sd-14-014/lesson.md)).

Độ mạnh của mỗi loại phụ thuộc thuật toán, độ dài khóa và cách dùng. OWASP đặt mức tối thiểu cho AES là khóa 128 bit (nên 256 bit) còn cho RSA là 2048 bit, nên không đem số bit của hai loại ra so với nhau được (cách diễn giải này là của người biên soạn). OWASP cũng nhắc rằng RSA và mật mã đường cong elliptic sẽ không an toàn trước một máy tính lượng tử đủ mạnh trong tương lai.

## Nhìn hình trả lời

Alice có khóa công khai đúng của Bob và muốn gửi một tệp 1 MiB. Vì sao không mã hóa cả tệp bằng RSA, và theo cách gói khóa thì Alice gửi những gì?

<details>
<summary>Xem đáp án</summary>

RSA-2048 với OAEP chỉ nhận tối đa 190 byte mỗi lần, nên 1 MiB thành 5.519 lần mã hóa: chậm (giải mã mất khoảng 2 giây trong lần đo, so với 0,0006 giây của AES-GCM) và bản mã to hơn.
Thay vào đó Alice tạo khóa AES ngẫu nhiên, mã hóa tệp bằng AES-GCM, rồi gói khóa AES bằng khóa công khai của Bob. Alice gửi ba thứ: khóa đã gói (256 byte), nonce (12 byte) và bản mã (1 MiB cộng 16 byte). Bob mở gói bằng khóa riêng rồi giải mã.
Điều kiện còn lại là khóa công khai Alice dùng phải thật sự là của Bob.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn và cách thử</summary>

Mọi lần thử dùng khóa tạm, chạy một lần trên máy biên soạn.

Bài nguồn nói bất đối xứng an toàn hơn vì khóa riêng không bao giờ chia sẻ. Bài này không giữ so sánh đó. MDN nói thuật toán đối xứng dùng đúng cách thì an toàn và hiệu quả. Việc khóa riêng không phải chia sẻ giải bài toán trao khóa; nó không đo độ mạnh của thuật toán.

Bài nguồn nói khóa công khai mã hóa, khóa riêng giải mã. Đó chỉ là chiều mã hóa. Với chữ ký số, vai trò đảo lại: khóa riêng ký, khóa công khai kiểm (MDN và tài liệu của `cryptography` đều nói vậy), và ký không phải là “mã hóa bản băm”, như [bài sd-14-015](../sd-14-015/lesson.md) đã thử.

Bài nguồn giải thích độ chậm bằng việc tạo khóa và tính toán phức tạp. Tạo khóa chỉ làm một lần; chi phí đo được lặp lại ở mỗi khúc 190 byte, và còn có giới hạn độ dài. Việc phép toán trên số nguyên rất lớn là nguyên nhân là hiểu biết chung của người biên soạn, chưa đối chiếu tài liệu nào. Công thức 256 − 2 × 32 − 2 cũng là hiểu biết chung; kết quả 190 qua, 191 lỗi là do chạy thử.

Bài nguồn nói HTTPS dùng mã hóa bất đối xứng để trao đổi khóa phiên, rồi chuyển sang đối xứng. Thử một kết nối TLS 1.3 cục bộ giữa `openssl s_server` và `openssl s_client -tls1_3` (127.0.0.1, chứng chỉ tự ký dùng một lần có khóa RSA-2048, cấu hình mặc định). OpenSSL in ra:

- `Server Temp Key: X25519, 253 bits`
- `Peer signature type: RSA-PSS`
- `New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384`

Đọc kết quả: khóa phiên không được gói bằng RSA rồi gửi đi. Hai bên thống nhất khóa bằng một khóa tạm trên đường cong X25519 (OWASP gọi X25519 là phép thống nhất khóa, key agreement, không phải phép mã hóa dữ liệu); khóa RSA của chứng chỉ được dùng để ký, tức chứng minh máy chủ giữ khóa riêng; dữ liệu sau đó đi bằng AES-256-GCM. Ý lớn của bài nguồn (bất đối xứng lúc bắt tay, đối xứng sau đó) vẫn đúng, nhưng “mã hóa bất đối xứng để trao đổi khóa” gợi ra một khóa được mã hóa rồi gửi, điều lần thử này không thấy. Đây là một kết nối với mặc định của OpenSSL 3.0.13, không nói gì về mọi trang web hay trình duyệt. OWASP khuyên tắt các bộ mã TLS 1.2 dùng RSA để chuyển khóa (`TLS_RSA_*`) vì chúng không có tính bí mật về trước (forward secrecy).

Cách ghép khóa AES với RSA ở trên chỉ để học. OWASP khuyên dùng một thư viện được bảo trì và cài đặt một chuẩn lai như HPKE, thay vì tự ghép. Tài liệu của `cryptography` cảnh báo dùng lại một nonce với cùng một khóa AES-GCM làm hỏng an toàn của mọi thông điệp dùng cặp đó.

Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/symmetric-encryption-vs-asymmetric-encryption.md): so sánh một khóa chung với cặp khóa.
- [MDN — Symmetric-key cryptography](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/symmetric-key_cryptography/index.md), [Public-key cryptography](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/public-key_cryptography/index.md) và [Key](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/key/index.md): hai loại khóa, vai trò khi ký và khi mã hóa, cách ghép.
- [pyca/cryptography — AEAD](https://github.com/pyca/cryptography/blob/6179e1c39ed0019cf27168420eff6b3ab1840ef9/docs/hazmat/primitives/aead.rst), [RSA](https://github.com/pyca/cryptography/blob/6179e1c39ed0019cf27168420eff6b3ab1840ef9/docs/hazmat/primitives/asymmetric/rsa.rst) và [giới thiệu khóa bất đối xứng](https://github.com/pyca/cryptography/blob/6179e1c39ed0019cf27168420eff6b3ab1840ef9/docs/hazmat/primitives/asymmetric/index.rst): AES-GCM, OAEP, vai trò của hai khóa. Tải về từ kho ở commit cố định; tài liệu ở commit đó có thể mới hơn bản 50.0.1 đã chạy.
- [OWASP — Cryptographic Storage Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Cryptographic_Storage_Cheat_Sheet.md) và [Transport Layer Security Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Transport_Layer_Security_Cheat_Sheet.md): độ dài khóa tối thiểu, chế độ có xác thực, HPKE, bộ mã TLS.

Đã đọc nguồn ngày 2026-10-18. Cách chia ba khung, phép tính số khóa, các lần đo và cách đọc kết quả của OpenSSL là của người biên soạn; các đặc tả chính thức của chuẩn không đọc được nên không được trích dẫn. Bài viết và hình được thiết kế độc lập.

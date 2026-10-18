# Quản lý dữ liệu nhạy cảm trong hệ thống

**Dữ liệu nhạy cảm được giữ an toàn bằng nhiều lớp, mỗi lớp chặn một đường lộ khác nhau: trên đường truyền, trong kho lưu, trong các bản sao, qua người có quyền và theo thời gian. Mã hóa chỉ là một lớp, và nó chỉ có tác dụng khi khóa nằm riêng khỏi dữ liệu.**
Bài này là bản đồ các lớp, không phải hướng dẫn cài đặt hay tư vấn pháp lý. Nó chạy thử những chỗ bài nguồn nói chưa đúng: tên SSL, vai trò của GCM, việc chia khóa cho ba vai trò và việc băm để “làm ẩn” dữ liệu. Mật khẩu, phân quyền và token có bài riêng: [sd-14-003](../sd-14-003/lesson.md), [sd-14-004](../sd-14-004/lesson.md), [sd-14-002](../sd-14-002/lesson.md).

![Ba khung xếp dọc, dưới tiêu đề năm đường dữ liệu có thể lọt ra; bắt đầu từ danh sách dữ liệu nhạy cảm và chỗ nó nằm. Khung 1: trên đường truyền dùng TLS, không dùng SSL 2 và 3; trong kho lưu mã hóa AES-GCM và để khóa riêng khỏi dữ liệu; trong các bản sao (log, bản xuất, môi trường thử) bỏ, che hoặc thay dữ liệu trước khi chép. Khung 2: qua người và dịch vụ thì quyền tối thiểu theo vai trò (RBAC) và ghi lại ai xem; theo thời gian thì thu hồi quyền, xoay khóa, xóa khi hết hạn lưu. Khung 3, cần nhớ: mã hóa chỉ giữ được khi khóa nằm riêng; băm một mã ngắn không làm nó ẩn; chia khóa cho nhiều người là một thiết kế, không phải luật chung; bài không đọc luật nào.](../../diagrams/sd-14-016-main.svg)

## Từ viết tắt

- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: giao thức mã hóa dữ liệu đi giữa hai máy, như giữa trình duyệt và máy chủ.
- **SSL** (Secure Sockets Layer) — tên giao thức đời trước của TLS; hai bản SSL từng được công bố đều không còn nên dùng, nhưng nhiều người vẫn gọi TLS là “SSL”.
- **AES** (Advanced Encryption Standard) — chuẩn mã hóa tiên tiến: thuật toán mã hóa dùng một khóa chung để mã hóa và giải mã.
- **GCM** (Galois Counter Mode) — chế độ đếm Galois: một cách dùng AES vừa mã hóa vừa gắn thẻ kiểm tra, nên dữ liệu bị sửa thì lúc giải mã báo lỗi.
- **CTR** (CounTeR) — chế độ đếm: một cách dùng AES chỉ mã hóa, không có thẻ kiểm tra; bài dùng nó để so với GCM.
- **DEK** (Data Encryption Key) — khóa mã hóa dữ liệu: khóa trực tiếp mã hóa dữ liệu.
- **KEK** (Key Encryption Key) — khóa mã hóa khóa: khóa dùng để mã hóa DEK, cất ở chỗ khác với dữ liệu.
- **RBAC** (Role-Based Access Control) — kiểm soát truy cập theo vai trò: quyền gắn với vai trò, người dùng được gán vai trò (xem bài sd-14-004).
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.
- **SHA** (Secure Hash Algorithm) — họ thuật toán băm: biến dữ liệu bất kỳ thành một chuỗi cố định; SHA-256 là một loại trong họ này.

## Đọc hình

Trước hết cần danh sách dữ liệu nhạy cảm cùng chỗ nó nằm, và câu hỏi bảo vệ khỏi ai: OWASP mở đầu hướng dẫn lưu trữ mã hóa bằng mô hình đe dọa, vì lớp nào là đủ tùy câu trả lời. Danh sách những thứ OWASP không muốn thấy ghi thẳng vào log cho thấy loại dữ liệu hay gặp: mật khẩu, token, khóa mã hóa, chuỗi kết nối, dữ liệu thẻ thanh toán, dữ liệu sức khỏe, giấy tờ định danh do nhà nước cấp. Cách an toàn nhất vẫn là không lưu thứ không cần.

**1 · Trên đường truyền.** Dùng TLS. OWASP cho biết hai bản SSL từng được công bố có điểm yếu mật mã nghiêm trọng, nhưng “SSL” vẫn hay được dùng lẫn cho TLS, nên chữ “SSL” trong bài nguồn là nói theo thói quen. Thứ cần cấu hình là TLS: mặc định TLS 1.3, cho phép TLS 1.2 để tương thích, tắt TLS 1.0 và 1.1.

**2 · Trong kho lưu.** OWASP khuyên AES với khóa ít nhất 128 bit (tốt nhất 256 bit) và một chế độ có xác thực như GCM: dữ liệu bị sửa thì giải mã báo lỗi thay vì trả về dữ liệu sai. Cất khóa riêng khỏi dữ liệu không phải việc của GCM mà là việc quản lý khóa, để kẻ chỉ vào được một bên (ví dụ qua lỗi cho chèn lệnh vào cơ sở dữ liệu) không có cả hai. Cách thường dùng là hai tầng khóa: DEK mã hóa dữ liệu, KEK mã hóa DEK. DEK đã mã hóa nằm cạnh dữ liệu, còn KEK ở hệ thống khác, trong một két khóa chuyên dụng chứ không trong mã nguồn. Mật khẩu là trường hợp riêng: băm chứ không mã hóa ([sd-14-003](../sd-14-003/lesson.md)).

**3 · Trong các bản sao.** Dữ liệu còn lọt ra qua log, tệp xuất và môi trường thử. OWASP kể tên các cách xử lý log như những lựa chọn khác nhau: bỏ hẳn, che (mask), làm sạch, băm, mã hóa; với dữ liệu cá nhân thì thêm xóa, xáo trộn hoặc giả danh hóa (pseudonymization). Bài nguồn gộp chúng vào một tên chung; bài này không định nghĩa chúng theo luật hay chuẩn nào vì không đọc được nguồn như vậy. Có một điều thử được ngay: băm một mã ngắn không che được nó (mục “Xem sâu hơn”). Thay dữ liệu bằng token lưu ở kho riêng là một hướng khác ([sd-14-002](../sd-14-002/lesson.md)). Áp cùng nguyên tắc cho tệp xuất và môi trường thử là hiểu biết chung của người biên soạn, không có nguồn riêng.

**4 · Qua người và dịch vụ.** Mỗi người và mỗi dịch vụ chỉ có đúng quyền cần cho việc của mình, và mặc định là từ chối (OWASP). RBAC là một cách gán quyền; [sd-14-004](../sd-14-004/lesson.md) so nó với các mô hình khác. Khóa cũng cần quyền tối thiểu: OWASP muốn tốt nhất là không người nào xem được khóa, và nếu có thì hệ thống phải ghi lại ai. Việc chia khóa cho ba vai trò mà bài nguồn nêu là một thiết kế “chia kiến thức” chứ không phải quy tắc chung: tôi không thấy hướng dẫn OWASP nào mô tả nó, tài liệu của Vault (phần mềm quản lý bí mật) mô tả một thiết kế gần: khóa chia thành nhiều phần bằng thuật toán Shamir và chỉ cần đạt một ngưỡng số phần để ghép lại, và chạy thử cho thấy đòi đủ mọi phần thì mất một phần là mất khóa.

**5 · Theo thời gian.** Quyền và khóa không nên sống mãi. Bài nguồn nói cấp cho lập trình viên đúng quyền cần lúc phát triển rồi thu hồi sau khi hệ thống chạy thật; OWASP đi cùng hướng: xem lại quyền định kỳ để bắt “quyền phình dần”, đổi mật khẩu khi nhân viên rời đi, dùng cơ sở dữ liệu và tài khoản riêng cho từng môi trường. Bí mật có vòng đời gồm tạo, xoay, thu hồi và hết hạn; với hai tầng khóa, xoay KEK chỉ là bọc lại DEK mà không phải mã hóa lại dữ liệu. Log và bản sao lưu không được hủy trước thời hạn lưu giữ bắt buộc và không nên giữ quá hạn đó; nghĩa vụ pháp lý hay hợp đồng có thể ảnh hưởng thời hạn.

## Giới hạn cần nhớ

Không lớp nào đủ một mình, và lớp nào đáng làm tùy mô hình đe dọa. Ví dụ của OWASP: mã hóa ở tầng phần cứng chống được việc mất cắp máy chủ nhưng không bảo vệ gì khi kẻ tấn công vào máy chủ từ xa. OWASP cũng yêu cầu thiết kế để hệ thống vẫn an toàn khi lớp mã hóa hỏng, nhờ kiểm soát truy cập chặt. Bài này không bàn về luật: bài nguồn nhắc luật bảo vệ dữ liệu của Liên minh châu Âu và mức phạt, nhưng tôi không đọc được văn bản luật hay hướng dẫn pháp lý nào, nên bài không nêu điều khoản, nghĩa vụ hay mức phạt nào.

## Nhìn hình trả lời

Một công ty mã hóa bảng khách hàng bằng AES-GCM, nhưng khóa nằm trong tệp cấu hình ngay trên máy chủ cơ sở dữ liệu, và kẻ tấn công đọc được toàn bộ ổ đĩa máy đó. Lớp nào của hình đã hở, và nên sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Lớp “trong kho lưu”: có mã hóa, nhưng khóa không nằm riêng khỏi dữ liệu, nên kẻ có cả ổ đĩa có cả hai. Sửa: để khóa ở hệ thống khác (két khóa chuyên dụng), dùng hai tầng DEK và KEK để DEK đã mã hóa chỉ mở được khi có KEK ở chỗ khác, và ở lớp quyền chỉ cho dịch vụ thật sự cần dùng khóa được đọc nó, có ghi lại. OWASP lưu ý rằng khi DEK và KEK không thể cất riêng thì cách hai tầng chỉ còn giá trị hạn chế, vì kẻ tấn công nhiều khả năng lấy được cả hai cùng lúc.

</details>

<details>
<summary>Xem sâu hơn: các lần chạy thử và chỗ bài nguồn chưa đúng</summary>

Các lần chạy dùng Python 3.13.16, `cryptography` 50.0.1 và OpenSSL 3.0.13 trên máy biên soạn, với khóa tạm và kết nối cục bộ. Số giây là một lần đo, một luồng, chỉ để minh họa.

**TLS thay SSL.** Máy khách Python mặc định nối được tới máy chủ TLS cục bộ (chứng chỉ tự ký tạm) bằng TLS 1.3; ép chỉ dùng TLS 1.2 vẫn nối được; ép tối đa TLS 1.1 hoặc SSL 3 thì lỗi “no protocols available”. Tài liệu CPython nói `create_default_context` loại SSL 3.0 vì bị coi là hỏng hoàn toàn. Đó là cấu hình của máy này, không nói gì về máy chủ khác.

**GCM không phải chỗ cất khóa.** Tài liệu `cryptography` mô tả AES-GCM là AES chế độ Galois Counter: khóa là tham số đưa vào và phải giữ bí mật, và không bao giờ dùng lại một nonce với cùng một khóa. Chạy thử: mã hóa 24 byte ra 40 byte (cộng thẻ 16 byte), khóa không có trong kết quả, và khóa đọc từ một tệp khác vẫn giải mã được. Đổi một bit ở từng vị trí trong 40 byte thì cả 40 lần báo `InvalidTag`; sai khóa, sai nonce hay sai dữ liệu đi kèm cũng vậy. Với CTR, chế độ không xác thực, đổi một bit của bản mã cho ra bản rõ đổi đúng một ký tự (số cuối `8` thành `9`) mà không báo lỗi. Vậy GCM phát hiện sửa đổi; còn cất khóa riêng là quyết định về nơi lưu.

**Hai tầng khóa.** DEK 32 byte mã hóa dữ liệu; KEK ở “két” riêng bọc DEK bằng `aes_key_wrap`. Bản ghi trong “cơ sở dữ liệu” gồm nonce, bản mã và DEK đã bọc, không có DEK thô. Có KEK thì mở được, một KEK ngẫu nhiên báo `InvalidUnwrap`. Xoay KEK bằng cách bọc lại DEK: bản mã giữ nguyên từng byte, KEK cũ hết mở được, KEK mới mở được. Khớp với OWASP: bọc lại không đổi DEK; muốn đổi DEK phải mã hóa lại dữ liệu.

**Chia khóa ba phần.** Hai phần ngẫu nhiên 32 byte, phần thứ ba là khóa `xor` hai phần kia. Cả bảy tổ hợp khác rỗng của ba phần được thử: một hay hai phần đều báo `InvalidTag`, chỉ đủ ba phần mới giải mã được; thiếu phần của người kiểm toán thì hai phần còn lại không mở được. Đây là mô hình đồ chơi để quan sát; hệ thống thật dùng cài đặt đã được kiểm chứng và, như tài liệu Vault cho thấy, không nhất thiết đòi đủ mọi phần. OWASP cũng nhắc dữ liệu mã hóa mà mất khóa thì không khôi phục được, nên cần cách sao lưu khóa an toàn.

**Băm một mã ngắn.** Lấy một mã thành viên 7 chữ số tự đặt (`4829175`) và lưu SHA-256 của nó như thể đã “che”. Thử lần lượt từ `0000000` thì ra sau 4.829.176 lần, mất 2,8 giây. Hàm băm nhanh không giấu được thứ có ít khả năng, cùng lý do bài [sd-14-003](../sd-14-003/lesson.md) nói về mật khẩu.

**Điều đã chỉnh so với bài nguồn.**

- SSL thành TLS; chia khóa ba vai trò thành “một thiết kế” cùng cái giá của nó; câu “GCM cất bản mã và khóa riêng nhau” thành phân biệt chế độ mã hóa với quản lý khóa.
- “Desensitization”, ẩn danh và làm sạch không còn gộp làm một; mức phạt theo luật không lặp lại vì không có nguồn pháp lý.
- Thêm từ OWASP những điều bài nguồn không nói: không lưu thứ không cần, log và bản sao, xoay khóa, vòng đời bí mật. Không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-manage-sensitive-data-in-a-system.md): các nhóm biện pháp cho dữ liệu nhạy cảm.
- [OWASP — Cryptographic Storage Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Cryptographic_Storage_Cheat_Sheet.md): mô hình đe dọa, AES và chế độ có xác thực, tách khóa khỏi dữ liệu, DEK và KEK, xoay khóa, không lưu thì không phải bảo vệ.
- [OWASP — Key Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Key_Management_Cheat_Sheet.md): quyền tối thiểu và ghi lại ai xem được khóa, bọc lại DEK khi xoay KEK, mất khóa là mất dữ liệu.
- [OWASP — Transport Layer Security Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Transport_Layer_Security_Cheat_Sheet.md): SSL và TLS, phiên bản nên bật và nên tắt.
- [OWASP — Logging Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Logging_Cheat_Sheet.md): những thứ không ghi thẳng vào log, các cách xử lý, thời hạn giữ log.
- [OWASP — Authorization Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Authorization_Cheat_Sheet.md): quyền tối thiểu, từ chối mặc định, RBAC, xem lại quyền định kỳ.
- [OWASP — Database Security Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Database_Security_Cheat_Sheet.md): tài khoản riêng cho từng môi trường, đổi mật khẩu khi nhân viên rời đi.
- [OWASP — Secrets Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/Secrets_Management_Cheat_Sheet.md): vòng đời bí mật gồm tạo, xoay, thu hồi, hết hạn.
- [pyca/cryptography — Authenticated encryption](https://github.com/pyca/cryptography/blob/6179e1c39ed0019cf27168420eff6b3ab1840ef9/docs/hazmat/primitives/aead.rst) và [Key wrapping](https://github.com/pyca/cryptography/blob/6179e1c39ed0019cf27168420eff6b3ab1840ef9/docs/hazmat/primitives/keywrap.rst): AES-GCM, `InvalidTag`, nonce không dùng lại, bọc khóa.
- [HashiCorp — Vault, Seal/Unseal](https://github.com/hashicorp/web-unified-docs/blob/34b3a09cad9357b99d52cbb50ff8034e5108a9b7/content/vault/v1.21.x/content/docs/concepts/seal.mdx): chia khóa thành các phần bằng thuật toán Shamir, ngưỡng số phần để ghép lại.
- [CPython — module ssl](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/ssl.rst): ngữ cảnh mặc định loại SSL 3.0, các hằng phiên bản đã lỗi thời.

Đã đọc nguồn ngày 2026-10-18. Tất cả tài liệu trên đọc từ bản tải về ở đúng commit đã ghi; văn bản luật và các tiêu chuẩn gốc không đọc được nên không được trích. Cách chia theo năm đường lộ, các ví dụ và các lần chạy thử là của người biên soạn. Bài viết và hình được thiết kế độc lập.

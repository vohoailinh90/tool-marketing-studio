# Encoding, encryption và tokenization

**Ba thuật ngữ nghe giống nhau, nhưng chỉ hai trong số đó nhằm bảo vệ dữ liệu.** Chọn nhầm là lỗi thiết kế hay gặp:
tưởng đã “mã hóa” trong khi dữ liệu vẫn đọc được bởi bất kỳ ai.

![Năm thẻ xếp dọc. Dữ liệu mẫu là số thẻ mẫu 4111 1111 1111 1111. Encoding, Base64, cho ra NDExMSAxMTEx…; ai cũng giải ngược được, không cần khóa. Encryption cho ra gAAAAAB…; đúng khóa mới giải được, sai khóa thì lỗi. Tokenization cho ra tok_3159c9a6…; dữ liệu thật nằm trong kho token. Thẻ cuối nêu chỗ phải bảo vệ: encoding không có gì để giữ, encryption là cái khóa, tokenization là kho token.](../../diagrams/sd-14-002-main.svg)

## Đọc hình

**Encoding.** Đổi dữ liệu sang một định dạng khác bằng một quy tắc công khai, ví dụ Base64 biến byte thành ký tự ASCII để truyền qua kênh dạng văn bản.
Không cần khóa để đổi ngược lại, nên encoding **không** bảo vệ gì.

**Encryption.** Dùng thuật toán và khóa để biến dữ liệu đọc được thành bản mã. Có thể dùng một khóa chung (đối xứng) hoặc cặp khóa công khai và riêng (bất đối xứng).
Chỉ người có khóa đúng mới đọc lại được dữ liệu gốc.

**Tokenization.** Thay dữ liệu nhạy cảm bằng một token thay thế. Ánh xạ giữa token và dữ liệu thật được giữ trong một kho token tách riêng.
Hệ thống khác chỉ cầm token, nên không phải giữ dữ liệu thật.

## Giới hạn cần nhớ

Mỗi cách đều có một chỗ bạn buộc phải bảo vệ. Encoding không có gì để giữ, nên không an toàn. Với encryption, đó là cái khóa: lộ khóa là lộ dữ liệu,
và OWASP lưu ý hệ thống quản lý khóa chuyên dụng thêm một lớp bảo vệ nhưng cũng thêm độ phức tạp và chi phí vận hành. Với tokenization, đó là kho token: ai lấy được kho thì lấy lại được dữ liệu thật.

## Nhìn hình trả lời

Một hệ thống lưu “mật khẩu” bằng Base64 và cho rằng đã mã hóa. Điều gì sai?

<details>
<summary>Xem đáp án</summary>

Base64 là encoding, không cần khóa để giải ngược, nên không bảo vệ gì. Trong gần như mọi trường hợp, mật khẩu cũng không nên được mã hóa: chúng nên được băm bằng hàm băm chậm.
Xem bài [lưu mật khẩu an toàn](../sd-14-003/lesson.md).

</details>

<details>
<summary>Xem sâu hơn: điều đã tách riêng so với bài nguồn</summary>

Băm (hash) là một thứ khác nữa: một chiều, không có khóa để giải ngược; OWASP phân biệt rõ băm và mã hóa khi nói về mật khẩu.

Bài nguồn gọi tokenization là “rất an toàn” vì token không chứa phần nào của dữ liệu gốc. Điều đó đúng với token ngẫu nhiên lấy từ kho riêng,
nhưng độ an toàn thực tế dồn vào kho token, nên bài này nêu kho đó như chỗ cần bảo vệ. Bài nguồn cũng nói token hóa hay dùng cho dữ liệu thẻ thanh toán
và tuân thủ PCI DSS; bài này chưa đối chiếu tiêu chuẩn đó.

Kết quả minh họa trong hình chạy bằng Python: `base64`, `cryptography.fernet` và một từ điển đóng vai kho token.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/encoding-vs-encryption-vs-tokenization.md): ba khái niệm.
- [OWASP — Cryptographic Storage Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Cryptographic_Storage_Cheat_Sheet.md): mã hóa đối xứng và khóa công khai; quản lý khóa. Đọc từ bản clone của kho.
- [OWASP — Password Storage Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Password_Storage_Cheat_Sheet.md): băm khác với mã hóa. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Cryptographic Storage Cheat Sheet của OWASP không nhắc tới tokenization; phần mô tả tokenization lấy từ bài nguồn và từ ví dụ chạy thử, chưa đối chiếu tiêu chuẩn nào.
Bài viết và hình được thiết kế độc lập.

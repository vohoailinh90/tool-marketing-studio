# Trình quản lý mật khẩu hoạt động thế nào?

**Trình quản lý mật khẩu không cất mật khẩu của bạn trên máy chủ; nó cất một cái kho đã khóa, còn chìa khóa được tính ra ngay trên máy bạn từ mật khẩu chủ.**
Nhờ vậy bạn chỉ nhớ một mật khẩu, và với thiết kế này máy chủ giữ dữ liệu mà bản thân nó không đọc được.

![Bảy thẻ xếp dọc. Nhóm lập tài khoản, trên máy bạn: 1 tạo khóa kho, một khóa ngẫu nhiên để mã hóa các mục; 2 khóa mở khóa, tính từ mật khẩu chủ qua hàm băm chậm có salt; 3 bọc và mã hóa, khóa mở khóa bọc khóa kho, khóa kho mã hóa từng mục. Thẻ máy chủ giữ: salt, khóa kho đã bọc, các mục đã mã hóa và một giá trị để đăng nhập, không có mật khẩu chủ. Nhóm mỗi lần mở khóa: 4 dẫn xuất lại, nhập mật khẩu chủ và tính lại khóa mở khóa; 5 mở kho, mở khóa kho và giải mã mục ngay trên máy. Thẻ cuối là giới hạn: không bảo vệ máy đang mở khóa, mất mật khẩu chủ thì nhà cung cấp không tự mở được.](../../diagrams/sd-14-005-main.svg)

## Từ viết tắt

- **MUK** (Master Unlock Key) — khóa mở khóa chủ: tên một khóa trong quy trình của một sản phẩm cụ thể mà bài nguồn nhắc, bài này không dùng tên đó.
- **MP** (Master Password) — mật khẩu chủ; "MP key" là tên khóa trong quy trình của một sản phẩm cụ thể mà bài nguồn nhắc, bài này không dùng tên đó.
- **SRP** (Secure Remote Password) — giao thức mật khẩu từ xa an toàn: cho phép chứng minh biết mật khẩu mà không gửi mật khẩu đi; bài nguồn nhắc tên SRP-X.
- **PBKDF** (Password-Based Key Derivation Function) — hàm sinh khóa từ mật khẩu: băm mật khẩu nhiều vòng để khó đoán; PBKDF2 là một phiên bản.
- **HMAC** (Hash-based Message Authentication Code) — mã xác thực thông điệp dựa trên hàm băm: giá trị tính từ một khóa bí mật và dữ liệu, để kiểm tra dữ liệu không bị sửa và do người biết khóa tạo ra.
- **HKDF** (HMAC-based Key Derivation Function) — hàm sinh thêm khóa từ một khóa gốc, dùng để mở rộng một khóa thành nhiều khóa.
- **AES** (Advanced Encryption Standard) — chuẩn mã hóa tiên tiến: thuật toán mã hóa đối xứng, cùng một khóa để mã hóa và giải mã.
- **GCM** (Galois/Counter Mode) — một chế độ hoạt động của mã hóa khối, vừa mã hóa vừa phát hiện dữ liệu bị sửa; AES-GCM là cặp thường dùng.

## Đọc hình

**1 · Tạo khóa kho.** Máy bạn sinh một khóa ngẫu nhiên dùng để mã hóa các mục (mật khẩu, ghi chú). Khóa này do máy sinh ngẫu nhiên chứ không do người đặt, nên không dễ đoán như một mật khẩu.

**2 · Khóa mở khóa.** Mật khẩu chủ được đưa qua hàm băm chậm có salt (cùng loại hàm dùng để lưu mật khẩu trên máy chủ: chậm có chủ đích và có salt) để ra một khóa mở khóa. Một số sản phẩm trộn thêm một mã bí mật do người dùng giữ, nhà cung cấp không có bản sao, ví dụ Secret Key của 1Password, để mật khẩu chủ một mình không đủ. Theo tóm tắt tìm kiếm tài liệu của họ, mã này nằm trên các thiết bị đã đăng nhập và trong Emergency Kit do người dùng tự cất, nên nó không bị khóa chặt vào một thiết bị.

**3 · Bọc và mã hóa.** Khóa mở khóa mã hóa (“bọc”) khóa kho, còn khóa kho mã hóa từng mục. Máy chủ nhận salt, khóa kho đã bọc và các mục đã mã hóa. Để đăng nhập, máy bạn còn gửi một giá trị tính từ mật khẩu chủ (ở Bitwarden là một giá trị băm của khóa chủ); giá trị này dùng để xác thực với máy chủ, và mô hình chạy thử không mô phỏng phần đăng nhập.

**4–5 · Mở khóa.** Bạn nhập mật khẩu chủ, máy tính lại khóa mở khóa, mở khóa kho rồi giải mã mục trong bộ nhớ của máy. Vì khóa mở khóa chỉ sinh ra trên máy bạn, máy chủ không giữ khóa nào để tự giải mã.

## Giới hạn cần nhớ

Cái giá của thiết kế này là nhà cung cấp cũng không tự mở được kho của bạn: mất mật khẩu chủ (và mã bí mật do người dùng giữ, nếu sản phẩm dùng) nghĩa là mất chìa, trừ khi sản phẩm có cơ chế khôi phục riêng.
Thiết kế này bảo vệ dữ liệu nằm trên máy chủ. Nó không bảo vệ một máy đang mở khóa: khi kho đã mở, các khóa nằm trong bộ nhớ của máy đó, và mật khẩu chủ yếu vẫn có thể bị đoán.

## Nhìn hình trả lời

Kẻ tấn công lấy được toàn bộ dữ liệu trên máy chủ của nhà cung cấp, nhưng không có mật khẩu chủ của bạn. Họ có đọc được các mục không, và việc đổi mật khẩu chủ ảnh hưởng gì tới các mục?

<details>
<summary>Xem đáp án</summary>

Họ có salt, khóa kho đã bọc, các mục đã mã hóa và giá trị đăng nhập, nhưng không có khóa mở khóa. Với mô hình chỉ có mật khẩu chủ, muốn đọc họ phải đoán mật khẩu chủ: hàm băm chậm làm mỗi lần đoán tốn kém, nhưng mật khẩu chủ yếu vẫn là chỗ hở.
Với biến thể có mã bí mật do người dùng giữ (như Secret Key), khóa mở khóa cần cả hai, nên họ còn phải có hoặc đoán cả mã đó; khi chạy thử, mật khẩu một mình không mở được khóa kho trong biến thể này.

Đổi mật khẩu chủ: trong mô hình chạy thử, chỉ cần bọc lại khóa kho bằng khóa mở khóa mới. Các mục đã mã hóa giữ nguyên, và mật khẩu cũ không còn mở được bản đã bọc lại. Điều đó chỉ đúng với bản đang dùng.
Kẻ đã chép dữ liệu trước khi bạn đổi mật khẩu vẫn giữ bản bọc cũ và các mục cũ, nên vẫn thử được mật khẩu cũ trên bản chép đó; khi chạy thử, bản chép cũ vẫn mở được bằng mật khẩu cũ. Đổi mật khẩu không thu hồi dữ liệu đã bị chép. Nếu nghi ngờ có người đã chép dữ liệu và mật khẩu cũ yếu, nên coi các mật khẩu bên trong kho là có thể đã lộ và đổi chúng (suy luận của người biên soạn, không có nguồn riêng).

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn mô tả quy trình riêng của một sản phẩm cụ thể bằng các tên gọi như MUK, MP key, SRP-X. Bài này dạy mô hình chung nhất và không dùng các tên đó, vì chưa đối chiếu được từng tên với tài liệu của nhà cung cấp.
Điều đối chiếu được từ tóm tắt tìm kiếm tài liệu cho nhà phát triển của 1Password: khóa mở khóa nhận từ mật khẩu tài khoản cộng Secret Key, mã hóa một bộ khóa cá nhân, và bộ khóa đó mã hóa các kho; tên cũ của khóa mở khóa là “Master Unlock Key”.
Không mở được trang tài liệu để đọc trực tiếp, nên đây chỉ là bằng chứng ở mức tóm tắt.
Tài liệu kỹ thuật của Bitwarden, đọc từ kho GitHub, mô tả một mô hình tương tự: khóa chủ tính từ mật khẩu chủ bằng PBKDF2 hoặc Argon2id (email làm salt), mở rộng bằng HKDF, rồi mã hóa khóa đối xứng của người dùng; mỗi mục có thể có khóa riêng để việc xoay khóa và chia sẻ rẻ hơn.

Bài nguồn kết luận nhà cung cấp “không có cách nào biết” mật khẩu đã mã hóa. Điều đó đúng với dữ liệu nằm trên máy chủ, nhưng bài này nêu giới hạn: máy đang mở khóa và mật khẩu chủ yếu nằm ngoài sự bảo vệ đó (suy luận của người biên soạn từ thiết kế, không có nguồn riêng).
Mô hình thử nghiệm dùng `scrypt` với tham số nhẹ và AES-GCM của thư viện `cryptography`; đây không phải cấu hình nên dùng thật.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-a-password-manager-such-as-1password-or-lastpass-work.md): ý tưởng một mật khẩu chủ, khóa kho và mã hóa từng mục.
- [Bitwarden — Cryptography guide](https://github.com/bitwarden/contributing-docs/blob/d9ef0de61d27d2a9c8e0594992f231c1d30b9761/docs/architecture/cryptography/crypto-guide.md): khóa chủ từ mật khẩu, khóa đối xứng của người dùng, khóa riêng cho từng mục, bọc khóa và giá trị băm gửi lên máy chủ để đăng nhập. Đọc từ bản clone của kho.
- [1Password Developer — Service Account security](https://developer.1password.com/docs/service-accounts/security/): khóa mở khóa từ mật khẩu cộng Secret Key, bộ khóa cá nhân mã hóa các kho. Chỉ đọc được qua tóm tắt tìm kiếm, chưa mở trang.
- [1Password Support — About your Secret Key](https://support.1password.com/secret-key-security/): nơi Secret Key được cất và việc nhà cung cấp không có bản sao. Chỉ đọc được qua tóm tắt tìm kiếm, chưa mở trang.

Đã đọc nguồn ngày 2026-10-13. Mô hình thử nghiệm chạy bằng Python, `hashlib.scrypt` và AES-GCM trong `cryptography` 50.0.1. Bài viết và hình được thiết kế độc lập.

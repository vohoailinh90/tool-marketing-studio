# Lưu mật khẩu an toàn

**Đừng lưu mật khẩu. Hãy lưu kết quả của một phép băm chậm có salt.** Kẻ lấy được cơ sở dữ liệu khi đó không đọc được mật khẩu,
và việc đoán từng mật khẩu một trở nên tốn kém.

![Hai nhóm xếp dọc và một thẻ cảnh báo. Đăng ký: 1 sinh salt ngẫu nhiên riêng cho từng mật khẩu; 2 băm chậm mật khẩu cùng salt bằng Argon2id; 3 lưu một chuỗi gồm hash, salt và tham số. Đăng nhập: 4 lấy chuỗi đã lưu của đúng người dùng; 5 băm lại mật khẩu vừa nhập với cùng salt và tham số; 6 so sánh hai hash, khớp thì hợp lệ. Thẻ cuối: đừng lưu văn bản thô, đừng chỉ dùng hàm băm nhanh như SHA-256, đừng dùng chung một salt.](../../diagrams/sd-14-003-main.svg)

## Đọc hình

**1 · Sinh salt.** Salt là một chuỗi ngẫu nhiên, duy nhất cho mỗi mật khẩu. Nhờ đó hai người đặt cùng mật khẩu vẫn có hash khác nhau.

**2 · Băm chậm.** Dùng hàm băm mật khẩu được thiết kế để chậm. OWASP khuyên Argon2id với cấu hình tối thiểu 19 MiB bộ nhớ, 2 vòng lặp, độ song song 1;
scrypt nếu không có Argon2id; bcrypt cho hệ thống cũ (hệ số công việc từ 10 trở lên, mật khẩu tối đa 72 byte);
PBKDF2 với HMAC-SHA-256 và từ 600.000 vòng nếu cần tuân thủ FIPS-140.

**3 · Lưu kết quả.** Thư viện thường trả về một chuỗi duy nhất chứa thuật toán, tham số, salt và hash,
ví dụ bắt đầu bằng `$argon2id$v=19$m=65536,t=3,p=4$`. Bạn lưu nguyên chuỗi đó.

**4–6 · Đăng nhập.** Lấy chuỗi đã lưu, băm lại mật khẩu vừa nhập với đúng salt và tham số trong đó, rồi so hai hash. Khớp thì hợp lệ.
Thư viện làm các bước này trong một lời gọi kiểm tra.

## Giới hạn cần nhớ

Salt chống tra bảng băm tính sẵn (rainbow table) và che việc hai người trùng mật khẩu, nhưng không làm việc đoán mò chậm đi.
Hàm băm nhanh như SHA-256 vẫn cho kẻ tấn công thử số lượng lớn mật khẩu mỗi giây, nên OWASP nói chúng không phù hợp để lưu mật khẩu.
Đo trên máy biên soạn bài này, một luồng, trong một giây: SHA-256 băm khoảng 1,8 triệu lần, còn Argon2id mặc định của `argon2-cffi` khoảng 16 lần.
Số đo chỉ để minh họa độ chênh, không phải chuẩn so sánh.

## Nhìn hình trả lời

Hai người dùng đặt cùng một mật khẩu và kẻ tấn công lấy được bảng hash. Vì sao hash của họ khác nhau, và điều đó giúp gì?

<details>
<summary>Xem đáp án</summary>

Mỗi mật khẩu có salt riêng nên hash khác nhau. Kẻ tấn công phải phá từng hash một thay vì tính một lần rồi so với mọi hash,
và không thể biết hai người có trùng mật khẩu hay không nếu chưa phá được hash.
Khi chạy `argon2-cffi` hai lần với cùng mật khẩu, ta nhận hai chuỗi khác nhau và cả hai đều kiểm tra thành công.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn mô tả lưu `hash(mật khẩu + salt)` mà không nói hàm băm phải chậm. Chỉ salt là chưa đủ, nên bài này thêm yêu cầu băm chậm.

Salt không phải bí mật và có thể lưu cùng hash. Khác với salt, “pepper” là một bí mật dùng chung, không nên lưu cùng hash mà để riêng trong kho bí mật;
OWASP xem pepper là lớp phòng thủ bổ sung, không thay được băm chậm. Với bcrypt, các thư viện hiện đại báo lỗi khi mật khẩu dài hơn 72 byte
(bản `bcrypt` 5.0.0 dùng để thử báo lỗi ở 73 byte).

Trong gần như mọi trường hợp, không nên mã hóa mật khẩu: OWASP khuyên băm bằng thuật toán thích nghi hiện đại thay vì mã hóa hay lưu văn bản thô.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-store-passwords-in-the-database.md): các việc không nên làm, salt, quy trình lưu và kiểm tra.
- [OWASP — Password Storage Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Password_Storage_Cheat_Sheet.md): định nghĩa salt, hàm băm chậm, cấu hình khuyến nghị, giới hạn 72 byte của bcrypt, pepper, băm khác mã hóa. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Các kết quả minh họa chạy bằng `argon2-cffi` 25.1.0, `bcrypt` 5.0.0 và `hashlib` trên Python. Các cấu hình khuyến nghị có thể đổi theo thời gian;
hãy đối chiếu bản OWASP mới nhất khi triển khai. Bài viết và hình được thiết kế độc lập.

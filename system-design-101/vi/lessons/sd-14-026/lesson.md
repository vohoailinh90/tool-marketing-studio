# Google Authenticator hoạt động thế nào? TOTP và mã sáu số

**Điện thoại và máy chủ cùng giữ một bí mật chung, rồi mỗi bên tự tính mã sáu số từ bí mật đó và giờ hiện tại; không có mã nào được gửi đi trước.** Máy chủ chỉ tính lại và so với mã bạn gõ.
Bài chạy lại phép tính bằng Python, xem mã QR chứa gì và tính xem “một triệu mã” an toàn đến đâu; không bàn mã qua tin nhắn hay lấy lại tài khoản.

![Hai khung các bước và một khung ghi nhớ. Cài đặt một lần: máy chủ tạo bí mật ngẫu nhiên; mã QR mang bí mật, tên tài khoản và nơi cấp; điện thoại quét và lưu. Mỗi lần đăng nhập: điện thoại tính mã sáu chữ số bằng HMAC của bí mật và số bước giờ; bạn gõ mã cùng mật khẩu; máy chủ tính lại và so khớp. Cần nhớ: chỉ có một triệu mã nên phải giới hạn số lần thử; lộ bí mật là lộ mã; trang giả chuyển mã được; mã dùng lại được nếu máy chủ không nhớ.](../../diagrams/sd-14-026-main.svg)

## Từ viết tắt

- **TOTP** (Time-based One-Time Password) — mật khẩu dùng một lần theo thời gian: mã ngắn tính từ bí mật chung và giờ.
- **HOTP** (HMAC-based One-Time Password) — mật khẩu dùng một lần dựa trên số đếm: cùng phép tính như TOTP nhưng lấy số đếm thay cho giờ.
- **HMAC** (Hash-based Message Authentication Code) — mã xác thực thông điệp dựa trên hàm băm: trộn khóa bí mật với một thông điệp rồi băm bằng `SHA1`, ở đây cho ra 20 byte.
- **QR** (Quick Response) — mã vạch hai chiều mà camera đọc được; ở đây chỉ là một dòng chữ vẽ thành hình.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng về bảo mật ứng dụng; bài dùng hướng dẫn của họ.
- **RFC** (Request for Comments) — loạt tài liệu đánh số của cộng đồng Internet, gồm các đặc tả của HOTP và TOTP; bài không đọc được chúng.

## Đọc hình

**Cài đặt, làm một lần.** **1 · Bí mật.** Máy chủ tạo một chuỗi ngẫu nhiên và giữ lại. Mô-đun đăng nhập của Google cho Linux sinh 160 bit. Chuỗi mẫu `JBSWY3DPEHPK3PXP` là ví dụ công khai của Google, chỉ 80 bit: đừng dùng cho tài khoản thật.

**2 · Mã QR** không mã hóa gì: nó là một dòng chữ vẽ thành ô vuông. Theo tài liệu của Google, dòng chữ đó là `otpauth://totp/NoiCap:an@example.org?secret=JBSWY3DPEHPK3PXP&issuer=NoiCap`: loại (`totp` hoặc `hotp`), nhãn gồm nơi cấp và tài khoản, rồi tham số. `secret` bắt buộc, `issuer` nên có; `algorithm`, `digits`, `period` tùy chọn.

**3 · Quét và lưu.** Từ đây ứng dụng tính mã được cả khi không có mạng (tệp `README.rst` của `pyotp`).

**Mỗi lần đăng nhập.** **1 · Điện thoại tính mã.** Giờ Unix là số giây từ 1/1/1970. Chia cho 30 lấy phần nguyên ta có số bước, đổi thành 8 byte rồi đưa vào `HMAC-SHA1` cùng bí mật, ra 20 byte. Bốn bit cuối của byte cuối cho vị trí; đọc 4 byte từ đó, bỏ bit cao nhất, chia dư cho 1.000.000, thêm số 0 đứng đầu cho đủ sáu chữ số. Đó là HOTP với số đếm lấy từ giờ. Với bí mật `JBSWY3DPEHPK3PXP`:

| Giờ Unix | Số bước | Mã |
|---|---|---|
| 1700000009 | 56666666 | 324550 |
| 1700000010 | 56666667 | 367665 |
| 1700000040 | 56666668 | 870960 |

Mã giữ nguyên từ giây 1700000010 đến 1700000039 và chỉ đổi ở mốc chia hết cho 30. Tôi viết lại phép tính bằng `hmac` và `hashlib` (khoảng mười dòng) và so với `pyotp` 2.10.0: trùng ở bảng trên, ở 2000 trên 2000 cặp bí mật và giờ ngẫu nhiên, và ở 16 giá trị mà tệp kiểm thử của `pyotp` ghi là lấy từ RFC.

**2 · Bạn gõ mã** cùng mật khẩu ([bài sd-14-003](../sd-14-003/lesson.md) nói về mật khẩu).

**3 · Máy chủ tính lại** đúng phép tính trên, với bí mật nó giữ và đồng hồ của nó. Khác mật khẩu, nó không thể chỉ giữ bản băm: HMAC cần chính bí mật làm khóa. Đồng hồ hai bên hay lệch, nên nhiều máy chủ nhận cả mã của bước trước và bước sau; mô-đun của Google mặc định nhận ba mã.

## Giới hạn cần nhớ

**Sáu chữ số chỉ có một triệu mã, nên an toàn đến từ việc giới hạn số lần thử, không phải từ việc mã đổi mỗi 30 giây.**

- **“30.000 lần mỗi giây” của bài nguồn dễ hiểu sai.** 1.000.000 chia 30 là khoảng 33.333, tốc độ để thử hết mọi mã trong một bước. Nhưng kẻ đoán không bị hạn 30 giây: mỗi bước là một ván mới, lần sai trước không để lại gì. Giả lập: đoán 100 lần mỗi giây, không giới hạn, qua 10.000 bước (khoảng 83 giờ) thì trúng ở 32 bước, kỳ vọng 30.
- **Mỗi mã được nhận làm tăng cơ hội.** Duyệt đủ 1.000.000 lần đoán: chỉ 1 lần được nhận khi máy chủ nhận một mã, 3 lần khi nhận ba.
- **Mức giới hạn do người vận hành chọn.** OWASP khuyên giới hạn số lần thử chặt và khóa tài khoản sau số lần sai, nhưng không nêu ngưỡng cho mã sáu số. Công cụ cài đặt của Google, khi bật giới hạn, nói nó giữ kẻ tấn công ở tối đa 3 lần thử mỗi 30 giây. Lấy đó làm ví dụ, không phải khuyến nghị: với ba mã được nhận, đó là 8.640 lần thử và khoảng 2,56% cơ hội trúng mỗi ngày, nếu kẻ đoán đã biết mật khẩu và tài khoản không bị khóa. Khóa sau 10 mã sai và không tự mở lại thì còn khoảng 0,003%.

TOTP **không** chống được:

- **Trang giả chuyển tiếp mã.** OWASP ghi TOTP “susceptible to phishing (although short-lived)”: trang trung gian chuyển ngay mã bạn gõ trong 30 giây. Cách chống mà OWASP nêu là bộ xác thực gắn với tên miền thật, như passkey ([bài sd-14-006](../sd-14-006/lesson.md)).
- **Bí mật bị lấy.** Ai có bí mật, từ máy chủ hay điện thoại, tính ra cùng mã như ứng dụng (thử nghiệm trên chỉ cần bí mật và giờ). `README.rst` của `pyotp` nói khóa bất đối xứng (nền của passkey) chống tốt hơn các tấn công vào máy chủ vì không có bí mật chung.
- **Dùng lại mã trong cùng một bước.** `pyotp.verify` cho cùng một mã “đúng” hai lần liên tiếp; máy chủ phải nhớ bước đã dùng. Mô-đun của Google có tùy chọn cấm dùng lại.

## Nhìn hình trả lời

Đồng hồ điện thoại nhanh hơn máy chủ 25 giây. Mã trên điện thoại còn được nhận không, và điều đó phụ thuộc vào gì ở máy chủ?

<details>
<summary>Xem đáp án</summary>

Mã tính từ số bước, nên 25 giây có thể đẩy điện thoại sang bước kế và cho mã khác mã máy chủ đang tính. Trong một lần thử (máy chủ đang ở giây thứ 5 của một bước), máy chủ chỉ nhận một mã thì từ chối, nhận mã bước trước, hiện tại và sau thì chấp nhận. Cửa sổ rộng chịu lệch giờ hơn (17 mã chịu lệch tới 4 phút, theo tài liệu của Google) nhưng làm tăng xác suất đoán trúng.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn nói chuỗi trong mã QR gồm nơi cấp, tên người dùng và bí mật; tài liệu của Google còn có loại và ba tham số tùy chọn, và ghi rằng Google Authenticator “hiện” bỏ qua `algorithm` và `period` (lời của wiki đã ghim, chưa kiểm với ứng dụng hiện hành).
Bài nguồn nói máy chủ so hai “mật khẩu”; thực tế nhiều máy chủ nhận hơn một mã (`pyotp` mặc định chỉ nhận mã hiện tại, trừ khi đặt `valid_window`).
Bài nguồn nói kẻ xấu cần 30.000 lần mỗi giây; đúng là khoảng 33.333, và không có hạn 30 giây.
Bài nguồn nói lưu bí mật đã mã hóa. `README.rst` của `pyotp` nói giữ bí mật trong cơ sở dữ liệu có kiểm soát truy cập; mô-đun của Google bắt tệp bí mật chỉ chủ sở hữu đọc được (quyền 0600 mặc định). Tôi không đọc nguồn nào bàn việc mã hóa nên không khẳng định.
Không đọc được RFC: các bước HMAC, cắt 4 byte và chia dư lấy từ mã nguồn của `pyotp` và của mô-đun Google (viết bằng C).

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-google-authenticator-or-other-types-of-2-factor-authenticators-work.md).
- [Google — Key URI Format](https://github.com/google/google-authenticator/wiki/Key-Uri-Format): chuỗi trong mã QR (kho wiki, commit 8ba6e79).
- [pyotp — `README.rst`](https://github.com/pyauth/pyotp/blob/cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1/README.rst) và [`otp.py`](https://github.com/pyauth/pyotp/blob/cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1/src/pyotp/otp.py).
- [google-authenticator-libpam — hướng dẫn](https://github.com/google/google-authenticator-libpam/blob/288db94951a9c93960a20cfd0d72359813ccc909/man/google-authenticator.1.md) và [mã C](https://github.com/google/google-authenticator-libpam/blob/288db94951a9c93960a20cfd0d72359813ccc909/src/pam_google_authenticator.c).
- [OWASP — Multifactor Authentication](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md) và [Authentication](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/Authentication_Cheat_Sheet.md).

Đã đọc nguồn ngày 2026-10-18. Số đo là một lần chạy trên máy biên soạn (Python 3.13, `pyotp` 2.10.0, bí mật ví dụ hoặc bí mật tạm). Phép tính xác suất và các giả định đi kèm là của người biên soạn. Bài viết và hình được thiết kế độc lập.

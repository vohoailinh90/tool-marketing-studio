# UPI của Ấn Độ: đăng ký, liên kết tài khoản, chuyển tiền

**UPI là hệ thống thanh toán tức thời của Ấn Độ: bạn dùng một "địa chỉ thanh toán" thay vì số tài khoản, và một tổ chức đứng giữa các ngân hàng tra địa chỉ đó ra tài khoản thật rồi điều tiền.**
Nguồn nói nó chiếm 60% giao dịch bán lẻ số ở Ấn Độ (số của nguồn, chưa kiểm tra) và còn đang tăng.

![Hai khung. Khung một, chuẩn bị: Bob cung cấp số điện thoại và xác minh bằng mật khẩu dùng một lần; đặt địa chỉ thanh toán ảo; ứng dụng tạo địa chỉ đó với ngân hàng thu; liên kết tài khoản ngân hàng qua NPCI và đặt mã PIN. Khung hai, chuyển tiền: Alice nhập địa chỉ của Bob và 100 rupee, ứng dụng của Alice gửi yêu cầu tới NPCI, NPCI nhờ ngân hàng của Bob tra chi tiết, trừ 100 ở tài khoản Alice, ra lệnh cộng 100 vào tài khoản Bob, rồi báo thành công cho các ứng dụng.](../../diagrams/sd-07-009-main.svg)

## Từ viết tắt

- **UPI** (Unified Payments Interface) — giao diện thanh toán hợp nhất: hệ thống thanh toán tức thời do tổ chức NPCI phát triển; nguồn tóm gọn là ngôn ngữ đặc tả thanh toán cộng một chuẩn để các hệ thống thanh toán dùng được với nhau.
- **NPCI** (National Payments Corporation of India) — Tập đoàn Thanh toán Quốc gia Ấn Độ: tổ chức phát triển UPI và đứng giữa các ngân hàng như một bộ chuyển mạch.
- **OTP** (One-Time Password) — mật khẩu dùng một lần: mã gửi qua điện thoại để xác minh số điện thoại.
- **VPA** (Virtual Payment Address) — địa chỉ thanh toán ảo: tên do người dùng đặt, thay cho số tài khoản khi trả tiền.
- **PIN** (Personal Identification Number) — mã định danh cá nhân: dãy số bí mật người dùng đặt để xác nhận giao dịch; nguồn nói nó dùng cho xác thực hai yếu tố.
- **2FA** (Two-Factor Authentication) — xác thực hai yếu tố: xác nhận bằng hai thứ khác loại (ở đây: điện thoại và mã PIN).

## Đọc hình

Bài gọi các ngân hàng theo vai (ngân hàng thu, ngân hàng phát hành); nguồn dùng tên cụ thể.

**Chuẩn bị của Bob.** Bob muốn mở tài khoản và đưa số điện thoại, rồi xác minh số bằng OTP. Anh đặt một địa chỉ thanh toán ảo (VPA). Ứng dụng thanh toán của anh tạo địa chỉ đó với ngân hàng thu; ngân hàng trả lại địa chỉ, và ứng dụng đưa nó cho Bob.
Tiếp theo anh liên kết tài khoản ngân hàng của mình với địa chỉ đó: yêu cầu được chuyển tới NPCI. NPCI đóng vai bộ chuyển mạch giữa các ngân hàng thu và các ngân hàng phát hành, và từ địa chỉ tra ra chi tiết tài khoản ở từng ngân hàng phát hành. Bob xác thực bằng chi tiết tài khoản và đặt mã PIN, dùng cho xác thực hai yếu tố; yêu cầu này đi thẳng tới ngân hàng phát hành.

**Alice trả Bob 100 rupee.** Alice nhập địa chỉ UPI của Bob và số tiền 100 rupee. Ứng dụng của Alice kiểm tra rồi chuyển yêu cầu tới NPCI qua một ngân hàng. NPCI nhờ ngân hàng của Bob tra chi tiết của địa chỉ đó. Rồi NPCI trừ 100 rupee ở tài khoản ngân hàng của Alice, và ra lệnh cho ngân hàng của Bob cộng 100 rupee vào tài khoản của Bob. Khi thành công, NPCI báo cho các ứng dụng thanh toán, qua các ngân hàng thu.

## Giới hạn cần nhớ

Bài nguồn là một bản tóm tắt: nó không nói điều gì xảy ra nếu một bước lỗi giữa chừng (đã trừ tiền Alice mà chưa cộng cho Bob), cũng không nói về hạn mức hay phí; bài này không bổ sung những điều đó.
Con số 60% là của nguồn, tại thời điểm nguồn viết; bài chưa kiểm tra nó. Phần giải nghĩa PIN và 2FA là kiến thức chung của người biên soạn.

## Nhìn hình trả lời

Alice chỉ biết địa chỉ UPI của Bob, không biết số tài khoản của anh. Ai là bên đổi địa chỉ đó thành tài khoản thật, và bên đó phải hỏi ai?

<details>
<summary>Xem đáp án</summary>

NPCI đứng giữa các ngân hàng và tra chi tiết tài khoản từ địa chỉ: nó nhờ ngân hàng của Bob tra chi tiết của địa chỉ, rồi mới trừ tiền ở bên Alice và ra lệnh cộng tiền ở bên Bob.
Vì Alice chỉ đưa địa chỉ và số tiền, cô không cần biết số tài khoản của Bob; nguồn không nói thêm cách NPCI lưu hay bảo vệ chi tiết đó.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có ba phần: đăng ký, liên kết tài khoản, chuyển tiền trực tiếp. Bài này gộp hai phần đầu thành bốn bước chuẩn bị, và vẽ phần chuyển tiền thành lược đồ ba bên với NPCI ở giữa. Bước trừ tiền ở ngân hàng của Alice có trong phần chữ nhưng không vẽ riêng.
Bài đổi tên ngân hàng và ứng dụng theo vai và không dùng tên thật của nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/unified-payments-interface-upi-in-india.md): UPI là gì, đăng ký, liên kết tài khoản, chuyển tiền trực tiếp và con số 60%. Phần giải nghĩa PIN, 2FA và phần giới hạn là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

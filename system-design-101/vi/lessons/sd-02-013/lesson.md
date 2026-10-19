# Hệ thống thông báo: một cổng vào, nhiều kênh ra

**Một hệ thống thông báo nhận yêu cầu từ nhiều dịch vụ nghiệp vụ qua một cổng chung, chuẩn hóa và lên lịch chúng, rồi đẩy ra từng kênh: trong ứng dụng, email, SMS, mạng xã hội.**
Bài nguồn mô tả kiến trúc theo sáu bước đánh số. Bài này gom sáu bước đó thành ba chặng: vào, xử lý, ra, cộng một vòng đo kết quả để cải thiện.

![Hai khung bước và một khung ghi nhớ. Khung một, vào và xử lý: các dịch vụ nghiệp vụ gửi thông báo tới cổng thông báo, từng cái một hoặc theo lô; dịch vụ phân phối kiểm tra, định dạng theo mẫu có sẵn và lên lịch theo kênh người dùng chọn; thông báo được đưa vào bộ định tuyến, thường là hàng đợi tin nhắn. Khung hai, ra và đo: các dịch vụ kênh gửi qua trong ứng dụng, email, SMS và mạng xã hội; dịch vụ theo dõi và phân tích ghi lại số liệu gửi để đội vận hành xem báo cáo. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-013-main.svg)

## Từ viết tắt

- **SMS** (Short Message Service) — dịch vụ tin nhắn ngắn: tin nhắn văn bản gửi tới số điện thoại.
- **OTP** (One-Time Password) — mật khẩu dùng một lần: mã ngắn gửi cho người dùng để xác nhận một lần đăng nhập hay giao dịch.

## Đọc hình

**Vào.** Bước 1.1 và 1.2: các dịch vụ nghiệp vụ gửi thông báo tới cổng thông báo. Cổng nhận theo hai kiểu: mỗi lần một thông báo, hoặc cả lô một lần.

**Xử lý.** Bước 2, 2.1 và 2.2: cổng chuyển thông báo cho dịch vụ phân phối. Ở đây thông báo được kiểm tra, định dạng và lên lịch theo cài đặt:
- Kho mẫu thông báo cho phép định nghĩa trước khuôn của tin nhắn.
- Kho kênh ưa thích cho phép người dùng chọn trước kênh nhận.

Bước 3: thông báo được đưa vào bộ định tuyến, thường là hàng đợi tin nhắn.

**Ra.** Bước 4: các dịch vụ kênh làm việc với từng kênh gửi, trong và ngoài công ty: thông báo trong ứng dụng, email, SMS và ứng dụng mạng xã hội.

**Đo.** Bước 5 và 6: số liệu gửi được dịch vụ theo dõi và phân tích ghi lại; đội vận hành xem báo cáo để cải thiện trải nghiệm người dùng.

## Giới hạn cần nhớ

Bài nguồn chỉ mô tả các khối và thứ tự. Nó không nói gửi thất bại thì thử lại thế nào, không nói cách tránh gửi trùng một thông báo, và không nói OTP (nêu trong danh sách kênh) được xử lý khác thông báo thường ra sao. Các nhận xét ở phần dưới về hàng đợi là của người biên soạn.

## Nhìn hình thử trả lời

Một người dùng tắt email và chỉ muốn nhận thông báo trong ứng dụng. Thông tin đó nằm ở đâu trong hình, và được dùng ở bước nào?

<details>
<summary>Xem đáp án</summary>

Ở kho kênh ưa thích. Dịch vụ phân phối đọc nó ở bước 2, khi lên lịch thông báo theo cài đặt, nên thông báo chỉ được đưa tới dịch vụ kênh trong ứng dụng, không tới kênh email.

</details>

<details>
<summary>Xem sâu hơn: vì sao đặt hàng đợi giữa xử lý và các kênh</summary>

- Mỗi kênh có tốc độ riêng: email có thể chậm, thông báo trong ứng dụng thì nhanh. Hàng đợi giữ việc cho kênh chậm mà không làm nghẽn kênh nhanh.
- Một kênh ngoài (nhà mạng SMS chẳng hạn) gặp sự cố thì thông báo có thể nằm chờ thay vì mất, nhưng chỉ khi hàng đợi lưu bền, chỉ xóa tin sau khi kênh gửi xong và có thử lại; bài nguồn không nói hệ thống có những điều này.
- Có thể thêm máy cho riêng kênh đang đông.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-a-typical-push-notification-system-work.md): các kênh thông báo và sáu bước của kiến trúc.

Đã đọc nguồn ngày 2026-10-19.
Bài viết và hình được thiết kế độc lập.

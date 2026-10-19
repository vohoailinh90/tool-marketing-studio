# Idempotent: sáu chỗ gửi lại cùng một yêu cầu không được làm hai lần

**Một thao tác idempotent cho cùng một kết quả dù bạn làm một lần hay nhiều lần. Mạng hay hỏng và client hay gửi lại, nên chỗ nào gửi lại có thể gây hại thì chỗ đó cần tính chất này.**
Sáu tình huống dưới đây là sáu chỗ hay gặp.

![Hai khung. Khung một, ba chỗ người dùng hoặc client gửi lại: yêu cầu REST, thanh toán, đặt đơn hàng. Khung hai, ba chỗ lặp lại bên trong hệ thống: thao tác cơ sở dữ liệu, tạo tài khoản, thông điệp giữa các dịch vụ. Mỗi ghi chú nói cách chặn việc làm hai lần.](../../diagrams/sd-11-007-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình cho chương trình khác gọi tới nó.
- **REST** (REpresentational State Transfer) — kiểu thiết kế API chạy trên HTTP, coi mỗi thứ là một tài nguyên có địa chỉ.
- **HTTP** (HyperText Transfer Protocol) — giao thức trình duyệt và máy chủ web nói chuyện với nhau.

## Đọc hình

Tên sáu tình huống giữ theo bài nguồn; phần còn lại là của người biên soạn.

**Gửi lại từ phía người dùng hoặc client**

- **Yêu cầu RESTful API.** Theo thiết kế của HTTP, `GET`, `PUT` và `DELETE` được coi là idempotent: đặt một tài nguyên về một giá trị, hay xóa nó, làm hai lần vẫn ra cùng kết quả. `POST` thì không: gửi hai lần có thể tạo hai thứ. Cách chữa quen thuộc là client gửi kèm một khóa duy nhất cho mỗi ý định, và máy chủ nhớ kết quả của khóa đó.
- **Xử lý thanh toán.** Ứng dụng gửi lệnh trả tiền, mạng báo quá hạn, ứng dụng gửi lại. Nếu máy chủ đã xử lý lần đầu thì lần sau phải trả lại đúng kết quả cũ, không trừ tiền lần nữa.
- **Hệ thống đơn hàng.** Người dùng bấm "đặt" hai lần. Mã đơn hoặc khóa duy nhất do phía gửi sinh ra giúp hệ thống nhận ra đó là một đơn.

**Lặp lại bên trong hệ thống**

- **Thao tác cơ sở dữ liệu.** "Đặt số dư bằng 100" idempotent, "cộng thêm 10" thì không. Ràng buộc khóa duy nhất và kiểu "chèn hoặc cập nhật" biến thao tác lặp thành vô hại.
- **Quản lý tài khoản.** Đăng ký gửi hai lần không được tạo hai tài khoản trùng email. Ràng buộc duy nhất trên email là chốt cuối.
- **Hệ thống phân tán và thông điệp.** Nhiều hàng đợi chỉ hứa giao *ít nhất một lần*, nên thông điệp có thể đến hai lần. Bên nhận ghi lại mã thông điệp đã xử lý để bỏ qua bản trùng.

## Giới hạn cần nhớ

Idempotent không có nghĩa là mọi lần gọi trả cùng nội dung (lần hai có thể trả "đã làm rồi"); nó chỉ nói về trạng thái cuối cùng. Chuyện `GET`, `PUT`, `DELETE` idempotent là quy ước của giao thức HTTP, còn máy chủ cụ thể có tuân theo hay không là việc của lập trình viên. Bài chưa đối chiếu với văn bản đặc tả HTTP trong phiên viết (không đọc được từ môi trường biên soạn). Khóa idempotent cũng cần hạn dùng: giữ mãi thì tốn chỗ, bỏ sớm thì gửi lại muộn lại bị làm hai lần.

## Nhìn hình trả lời

Máy chủ thanh toán trả lời chậm nên ứng dụng gửi lại. Nếu máy chủ chỉ kiểm tra "đã có khoản này chưa" rồi mới ghi, hai yêu cầu đến cùng lúc thì chuyện gì xảy ra, và sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Cả hai yêu cầu cùng thấy "chưa có" rồi cùng ghi, nên tiền bị trừ hai lần: kiểm tra rồi mới ghi là hai bước tách rời. Cách sửa là để cơ sở dữ liệu quyết định bằng một thao tác trọn vẹn, ví dụ ràng buộc khóa duy nhất trên khóa idempotent, để một yêu cầu thắng và yêu cầu kia nhận lại kết quả của yêu cầu thắng. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn đánh số sáu tình huống. Bài này giữ tên và thứ tự, chia thành hai nhóm (gửi lại từ phía client, lặp lại bên trong hệ thống) và thêm một ví dụ về lỗi kiểm tra rồi mới ghi.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-cases-to-apply-idempotency.md): chỉ lấy tên sáu tình huống. Phần giải thích là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức.

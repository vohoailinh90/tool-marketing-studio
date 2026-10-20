# Chín mẫu kiến trúc cho dòng dữ liệu và giao tiếp: mỗi mẫu trả lời một câu hỏi khác

**Chín mẫu này không cạnh tranh nhau: mỗi mẫu trả lời một câu hỏi, "các thành phần nói chuyện với nhau thế nào" hoặc "dữ liệu chảy và được xử lý ra sao", và đòi một cái giá riêng.**
Biết câu hỏi mà mỗi mẫu trả lời, bạn chọn mẫu theo bài toán, không theo tên.

![Hai khung. Khung một, năm mẫu về cách các thành phần giao tiếp và phối hợp: Peer-to-Peer, API Gateway, Request-Response, Pub-Sub, Orchestration; mỗi ghi chú nói mẫu đó giải quyết gì. Khung hai, bốn mẫu về dữ liệu: Event Sourcing, ETL, Batching, Streaming Processing.](../../diagrams/sd-11-006-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình cho chương trình khác gọi tới nó.
- **ETL** (Extract, Transform, Load) — trích xuất, biến đổi, nạp: lấy dữ liệu từ nguồn, làm sạch hoặc đổi dạng, rồi nạp vào kho đích.

## Đọc hình

Tên chín mẫu giữ theo bài nguồn. Cách chia hai nhóm và phần "giải quyết gì, giá gì" là của người biên soạn.

**Nhóm giao tiếp và phối hợp**

- **Peer-to-Peer (ngang hàng).** Mỗi nút vừa phục vụ vừa yêu cầu, không có máy chủ trung tâm. Giải quyết: không phụ thuộc một điểm duy nhất. Giá: tìm được nút nào, tin nút nào, và giữ dữ liệu khớp nhau đều khó hơn.
- **API Gateway (cổng API).** Một cửa vào cho nhiều dịch vụ phía sau, nơi đặt các việc chung như xác thực hay định tuyến. Giải quyết: người gọi chỉ cần biết một địa chỉ. Giá: cổng thành điểm cần dự phòng và thêm một chặng.
- **Request-Response (hỏi và đáp).** Bên hỏi gửi yêu cầu rồi chờ đáp. Giải quyết: đơn giản, kết quả có ngay. Giá: bên hỏi bị chặn khi bên đáp chậm.
- **Pub-Sub (đăng và đăng ký).** Bên gửi đăng sự kiện lên một chủ đề; ai đăng ký thì nhận. Giải quyết: tách bên gửi khỏi bên nhận. Giá: khó biết ai đã xử lý xong, và phải tính tới thứ tự và thông điệp trùng.
- **Orchestration (điều phối).** Một bộ điều phối gọi các bước theo thứ tự đã định. Giải quyết: quy trình nhiều bước có người chỉ huy rõ ràng. Giá: bộ điều phối thành điểm tập trung.

**Nhóm dữ liệu**

- **Event Sourcing.** Lưu chuỗi sự kiện đã xảy ra thay vì chỉ trạng thái hiện tại. Giải quyết: có lịch sử đầy đủ và phát lại được. Giá: muốn biết trạng thái hiện tại phải dựng lại từ sự kiện.
- **ETL.** Trích xuất từ nguồn, biến đổi, nạp vào kho. Giải quyết: gom dữ liệu rải rác về một chỗ để phân tích. Giá: có độ trễ, và đường ống hỏng khi nguồn đổi dạng.
- **Batching (xử lý theo lô).** Gom nhiều việc rồi xử lý một lần. Giải quyết: hiệu quả khi dữ liệu nhiều. Giá: kết quả đến muộn.
- **Streaming Processing (xử lý dòng).** Xử lý từng bản ghi ngay khi tới. Giải quyết: kết quả gần như tức thời. Giá: phức tạp hơn về thứ tự, độ trễ và trạng thái.

## Giới hạn cần nhớ

Chín mục không cùng cấp độ: Request-Response là kiểu giao tiếp, Batching là kiểu xử lý, Event Sourcing là cách lưu. Hệ thống thật thường dùng nhiều mẫu cùng lúc. Phần "giải quyết gì, giá gì" tổng hợp từ kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức nào trong phiên viết.

## Nhìn hình trả lời

Khi một đơn hàng được đặt, kho, bộ phận thông báo và bộ phận phân tích đều cần biết. Bạn gọi lần lượt từng nơi, hay dùng Pub-Sub? Khi nào vẫn nên hỏi và đáp?

<details>
<summary>Xem đáp án</summary>

Pub-Sub hợp: đơn đăng một sự kiện, mỗi bên đăng ký tự xử lý, và thêm bên mới không phải sửa phía gửi. Đổi lại, phía gửi không biết ai đã xử lý xong. Nếu đơn chỉ được nhận khi kho xác nhận còn hàng thì bước đó cần kết quả ngay, nên vẫn dùng hỏi và đáp. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê chín mẫu theo một dãy. Bài này giữ tên mẫu, chia thành hai nhóm theo câu hỏi mà chúng trả lời, và thêm cái giá của từng mẫu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-9-architectural-patterns-for-data-and-communication-flow.md): chỉ lấy tên chín mẫu. Phần giải thích là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức.

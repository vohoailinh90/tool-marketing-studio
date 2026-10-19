# Vì sao AWS Lambda phản hồi nhanh: bốn trụ cột

**Lambda nhanh không nhờ một mẹo duy nhất. Tốc độ đến từ bốn việc cùng làm: nhận lời gọi gọn, giao việc cho môi trường chạy nhanh, dựng môi trường bằng máy ảo siêu nhẹ, và đưa mã cùng dữ liệu tới nơi hiệu quả.**
Nhìn từng trụ, bạn thấy mỗi trụ cắt đúng một loại thời gian chờ.

![Hai khung. Khung một, nhận việc và giao việc: lời gọi đồng bộ hoặc bất đồng bộ, rồi dịch vụ phân công chọn môi trường chạy. Khung hai, dựng và nạp: máy ảo siêu nhẹ cách ly từng môi trường, và kho thành phần chia nhỏ mã, mã hóa chung, khởi tạo trước để bớt khởi động nguội.](../../diagrams/sd-11-012-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; Lambda là một dịch vụ trong đó.
- **CLI** (Command-Line Interface) — giao diện dòng lệnh: gọi dịch vụ bằng lệnh gõ trong cửa sổ dòng lệnh.
- **SDK** (Software Development Kit) — bộ công cụ phát triển phần mềm: thư viện giúp chương trình gọi một dịch vụ.
- **SQS** (Simple Queue Service) — dịch vụ hàng đợi của AWS: nơi xếp các thông điệp chờ được lấy ra xử lý.
- **KVM** (Kernel-based Virtual Machine) — tính năng của nhân Linux cho phép chạy máy ảo.
- **VM** (Virtual Machine) — máy ảo: một máy giả lập có hệ điều hành riêng, chạy trong máy thật.

## Đọc hình

Tên bốn trụ giữ theo bài nguồn; phần giải thích là của người biên soạn. Bài về cách Lambda chạy một hàm nằm ở một bài riêng; bài này chỉ hỏi "mỗi trụ tiết kiệm thời gian ở đâu".

**Trụ một, gọi hàm (Function Invocation).** Lời gọi đồng bộ đi thẳng từ người gọi, qua công cụ dòng lệnh, bộ công cụ phát triển hay một dịch vụ khác, tới hàm, và người gọi chờ kết quả. Lời gọi bất đồng bộ được cấp quyền rồi đặt thành một sự kiện trong hàng đợi nội bộ kiểu SQS; các bộ đọc lấy sự kiện ra và đưa đi xử lý. Chỗ tiết kiệm: người gọi không phải đợi hàm chạy xong, và hàng đợi làm đệm khi tải dồn.

**Trụ hai, dịch vụ phân công (Assignment Service).** Đây là bộ quản lý các môi trường chạy: biết môi trường nào đang rảnh để giao việc cho. Theo bài nguồn, nó viết bằng Rust để chạy nhanh, chia thành nhiều phân vùng theo kiểu một nút chính và các nút theo sau để luôn sẵn sàng, và ghi trạng thái các môi trường ra một nhật ký bên ngoài. Chỗ tiết kiệm: việc chọn môi trường nhanh, và nhờ nhật ký ngoài mà một nút hỏng không làm mất trạng thái.

**Trụ ba, máy ảo siêu nhẹ Firecracker.** Firecracker là bộ quản lý máy ảo nhẹ cho việc chạy hàm; theo bài nguồn nó dựa vào KVM của Linux để tạo ra các máy ảo siêu nhẹ, an toàn và khởi động nhanh. Chỗ tiết kiệm: vẫn cách ly được khách hàng khác nhau mà dựng nhanh hơn một máy ảo đầy đủ.

**Trụ bốn, kho thành phần (Component Storage).** Lambda phải đưa mã hàm và dữ liệu đầu vào tới đúng nơi. Bài nguồn kể ba kỹ thuật. *Chunking*: cắt ảnh container thành các mẩu để lưu và chuyển hiệu quả hơn. *Convergent encryption (mã hóa hội tụ)*: mã hóa mỗi mẩu theo cách do chính nội dung mẩu quyết định, nên hai mẩu giống hệt nhau cho ra hai bản mã giống hệt nhau; nhờ đó hệ thống nhận ra bản trùng và chỉ lưu một bản mà dữ liệu vẫn được mã hóa. Bài nguồn nói thêm là còn nối thêm dữ liệu vào mẩu trước khi tính mã băm để mã băm bền hơn. *SnapStart*: khởi tạo sẵn môi trường để giảm độ trễ khởi động nguội. Chỗ tiết kiệm: ít dữ liệu phải lưu, chuyển và khởi tạo hơn mỗi lần (mẩu trùng chỉ lưu một lần).

## Giới hạn cần nhớ

Bài nguồn chỉ liệt kê bốn trụ, không đưa số đo. Bài này không nêu con số nào về độ trễ vì chưa đối chiếu được tài liệu AWS trong phiên viết (không truy cập được ngoài GitHub). Cách các kỹ thuật ở trụ bốn hoạt động chi tiết (ví dụ cách mã hóa hội tụ giữ an toàn khi dữ liệu dùng chung) bài không giải thích sâu. "Nhanh" ở đây nghĩa là bớt thời gian chờ ở từng bước, không phải mọi lời gọi đều nhanh như nhau.

## Nhìn hình trả lời

Lần gọi đầu một hàm lớn thường chậm, các lần sau nhanh hơn. Trụ nào nhắm trực tiếp vào lần gọi đầu, và nó làm bằng cách nào?

<details>
<summary>Xem đáp án</summary>

Trụ bốn, kho thành phần, nhắm vào khởi động nguội: SnapStart khởi tạo sẵn môi trường nên lần gọi đầu bớt phải dựng và khởi tạo từ đầu; chunking và dữ liệu dùng chung bớt phần phải chuyển. Trụ ba (máy ảo siêu nhẹ) cũng góp vì dựng môi trường nhanh hơn. Đây là suy luận của người biên soạn từ mô tả của bài nguồn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn nêu bốn trụ rồi mô tả từng trụ. Bài này giữ tên và thứ tự, thêm câu hỏi "tiết kiệm thời gian ở đâu" cho mỗi trụ và không lặp lại phần mô tả đường gọi đồng bộ và bất đồng bộ đã có ở bài riêng về Lambda.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-makes-aws-lambda-so-fast.md): tên bốn trụ và các chi tiết kỹ thuật nêu ở từng trụ. Câu hỏi "tiết kiệm ở đâu" và phần giải thích là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức.

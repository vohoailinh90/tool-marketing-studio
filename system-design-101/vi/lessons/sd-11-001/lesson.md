# AWS Lambda hoạt động phía sau lời gọi hàm

Bạn tải một hàm xử lý ảnh lên Lambda. Khi có sự kiện, dịch vụ bố trí môi trường thực thi, khởi tạo runtime và chạy handler. Bạn quản lý mã, quyền IAM và cấu hình; AWS quản lý hạ tầng thực thi.

![Sự kiện: Đồng bộ: chờ kết quả: Bất đồng bộ: nhận trước; Khởi tạo nếu cần: Runtime + mã + cấu hình: Môi trường có thể tái dùng; Handler của ứng dụng: Ứng dụng ghi kho nếu cần: Lambda không tự lưu kết quả; Kết quả đồng bộ: Trả handler response/lỗi: Bên gọi chờ xử lý; Kết quả bất đồng bộ: Không trả handler response: Tra job hoặc cấu hình đích.](../../diagrams/sd-11-001-main.svg)

**Đọc hình:** Hai khung kết quả cuối đối chiếu hai chế độ gọi, không phải các bước liên tiếp. Ghi kết quả nghiệp vụ vào kho bền là trách nhiệm của mã ứng dụng khi cần, không là bước Lambda tự bảo đảm.

Với lời gọi đồng bộ, bên gọi chờ kết quả hoặc lỗi. Với lời gọi bất đồng bộ, Lambda nhận sự kiện vào hàng đợi nội bộ rồi xử lý sau; phản hồi nhận sự kiện chưa chứng minh ảnh đã được tạo. Cơ chế lấy dữ liệu từ SQS qua event source mapping là một đường vào khác.

Lambda không mặc định lưu kết quả nghiệp vụ vào kho bền. Đồng bộ trả handler response cho bên gọi; bất đồng bộ không trả response đó cho bên gọi. Muốn nhận bản ghi sau xử lý bất đồng bộ, phải cấu hình destination phù hợp; ứng dụng cũng có thể cung cấp trạng thái job riêng.

Một môi trường mới cần khởi tạo trước khi chạy. Môi trường đã dùng có thể được tái sử dụng, giúp tránh một phần chi phí khởi tạo. Tuy nhiên, dữ liệu trong RAM hoặc thư mục tạm chỉ là tối ưu phụ; trạng thái nghiệp vụ phải nằm ở nơi lưu bền.

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; bài nói Lambda là dịch vụ chạy hàm của AWS: bạn quản lý mã, quyền và cấu hình, còn AWS quản lý hạ tầng thực thi.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách để một chương trình yêu cầu dữ liệu hoặc chức năng của chương trình khác; trong ví dụ của bài, API nhận yêu cầu xử lý ảnh và báo thành công ngay, nhưng điều đó chưa chứng minh ảnh đã được tạo.
- **IAM** (Identity and Access Management) — quản lý danh tính và quyền truy cập: cho biết ai là ai và được làm gì với tài nguyên; bạn quản lý quyền IAM của hàm, còn AWS lo hạ tầng thực thi.
- **RAM** (Random Access Memory) — bộ nhớ truy cập ngẫu nhiên: bộ nhớ làm việc của máy, đọc ghi nhanh nhưng mất sạch khi tắt điện; dữ liệu trong RAM hoặc thư mục tạm chỉ là tối ưu phụ; trạng thái nghiệp vụ phải nằm ở nơi lưu bền.
- **SQS** (Simple Queue Service) — dịch vụ hàng đợi thông điệp của Amazon: nơi bên gửi đặt thông điệp để bên nhận lấy ra xử lý sau; việc lấy dữ liệu từ SQS qua event source mapping là một đường vào khác của hàm.

## Nhìn hình thử trả lời

API nhận xử lý ảnh trả thành công ngay. Ảnh đã sẵn sàng chưa?

<details>
<summary>Xem đáp án</summary>

Chưa. Cần trạng thái công việc hoặc sự kiện hoàn tất để biết handler đã xử lý thành công.

</details>

## Giới hạn cần nhớ

Không dựa vào việc Lambda luôn tái sử dụng môi trường. Chi tiết dịch vụ nội bộ có thể thay đổi; hình mô tả vòng đời công khai, không khẳng định mọi runtime có cùng đường thực thi.

<details>
<summary>Xem sâu hơn</summary>

Firecracker cung cấp cơ chế microVM nhẹ để cô lập workload. Quyền truy cập dữ liệu vẫn phải được giới hạn bằng IAM. Handler nên xử lý được sự kiện lặp và lỗi xảy ra sau khi đã ghi kết quả.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-aws-lambda-work-behind-the-scenes.md).
- [Understanding the Lambda execution environment lifecycle - AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html).
- [Invoking a Lambda Event Function asynchronously - AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html).
- [Synchronous invocation](https://docs.aws.amazon.com/lambda/latest/dg/invocation-sync.html).
- [Asynchronous invocation destinations](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-retain-records.html).
- [Firecracker](https://firecracker-microvm.github.io/).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

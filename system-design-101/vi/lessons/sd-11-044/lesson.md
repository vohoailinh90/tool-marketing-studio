# Blueprint: trình bày một thiết kế có lý do

Trong buổi thiết kế URL shortener, đừng bắt đầu bằng cache hay Kafka. Chốt thao tác tạo và đọc link, thời gian giữ, mục tiêu latency, tải và chính sách chống lạm dụng trước.

![1. Chốt bài toán: Thao tác • SLO • workload: Giả định có số và đơn vị; 2. Thiết kế tối thiểu: API + dữ liệu: Vẽ đường đọc và ghi; 3. Kiểm điểm khó: Tải đỉnh • lỗi • security: Chi phí • thay đổi • rollback.](../../diagrams/sd-11-044-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Ước lượng lưu lượng và dung lượng bằng giả định rõ. Định nghĩa API, key và dữ liệu; vẽ đường ghi và đọc tối thiểu. Sau đó giải thích từng thành phần: LB chia tải ứng dụng, DB giữ mapping bền, cache giảm đọc phổ biến, queue làm việc nền nếu có.

Đi sâu vào điểm khó thực sự, như sinh key không trùng, redirect link đã xóa, cache cũ hoặc dữ liệu khi failover. Nêu phương án thay thế và lý do chọn. Kiểm lại observability, quyền, backup và chi phí. Một blueprint tốt dẫn cuộc thảo luận từ yêu cầu đến cơ chế và giới hạn; nó không là sơ đồ phải sao chép nguyên cho mọi bài toán.

## Nhìn hình thử trả lời

Chưa biết tỷ lệ đọc/ghi nhưng đã chọn sharding theo người dùng. Vấn đề là gì?

<details>
<summary>Xem đáp án</summary>

Lựa chọn đi trước dữ kiện. Cần hiểu truy vấn và workload để xem khóa shard có tránh truy cập xuyên shard và hotspot không.

</details>

## Giới hạn cần nhớ

Không có công thức bắt buộc mọi hệ thống dùng gateway, CDN, queue và microservice. Chọn thành phần bằng trách nhiệm cụ thể.

<details>
<summary>Xem sâu hơn</summary>

Ghi cả điều chưa biết và phép đo sẽ quyết định. Với hệ đang chạy, thêm lộ trình chuyển đổi và rollback chứ không chỉ kiến trúc đích.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/system-design-blueprint-the-ultimate-guide.md).
- [AWS Well-Architected Framework - AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html).
- [Google SRE - Deployment Strategies for Product Launches](https://sre.google/sre-book/reliable-product-launches/).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

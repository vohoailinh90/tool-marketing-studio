# Mở rộng website cho hàng triệu người dùng

“Một triệu người dùng” chưa cho biết có bao nhiêu request đồng thời. Một triệu tài khoản truy cập mỗi tháng khác hẳn một triệu người cùng mở bán vé. Ước lượng QPS, kích thước dữ liệu và tỷ lệ đọc/ghi trước.

![Đo workload: Tài khoản ≠ concurrency: QPS • dữ liệu • đọc/ghi; Chia tải phục vụ: LB + app stateless: CDN cho nội dung tĩnh; Theo điểm nghẽn DB: Index → cache/replica: Queue • sharding khi cần.](../../diagrams/sd-11-013-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Một lộ trình có thể bắt đầu từ ứng dụng và DB tách riêng. Khi ứng dụng đầy, chạy nhiều bản stateless sau load balancer. Khi ảnh và tài nguyên tĩnh chiếm băng thông, dùng object storage và CDN. Khi DB đọc quá nhiều, tối ưu truy vấn rồi cân nhắc cache và read replica.

Việc gửi mail hoặc dựng báo cáo có thể chuyển sang queue và worker. Sharding chỉ nên đến khi dữ liệu hoặc tải ghi cần chia thật sự. Tách microservice theo ranh giới nghiệp vụ khi có lợi ích triển khai hoặc sở hữu rõ ràng; số tài khoản lớn không tự tạo ra yêu cầu microservice.

## Nhìn hình thử trả lời

Website nhiều tài khoản nhưng QPS thấp có cần sharding ngay không?

<details>
<summary>Xem đáp án</summary>

Không. Đo tải, dung lượng và truy vấn trước; thiết kế đơn giản có thể vẫn đáp ứng tốt.

</details>

## Giới hạn cần nhớ

Read replica chủ yếu chia tải đọc, không tự nhân năng lực ghi của primary. Session trong RAM một máy làm scale và failover khó hơn.

<details>
<summary>Xem sâu hơn</summary>

Thử tải với workload gần thực tế, có cache miss và lỗi phụ thuộc. Đo p99, pool kết nối, lag replica và tốc độ tiêu thụ queue trước khi mở thêm tầng.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-scale-a-website-to-support-millions-of-users.md).
- [AWS Well-Architected Framework - AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html).
- [Cache-Aside Pattern - Azure Architecture Center | Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside).
- [Competing Consumers Pattern - Azure Architecture Center | Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/competing-consumers).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

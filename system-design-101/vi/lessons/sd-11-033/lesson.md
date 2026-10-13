# Học AWS bằng một ứng dụng nhỏ

Thay vì học tên hàng trăm dịch vụ, hãy làm một ứng dụng lưu ảnh. Bắt đầu với IAM để hiểu danh tính và quyền, VPC để hiểu kết nối, rồi chọn EC2 hoặc Lambda cho compute. S3 giữ file; RDS hoặc DynamoDB giữ metadata theo kiểu truy vấn.

![Nền tảng: IAM + VPC: EC2 hoặc Lambda; Dữ liệu và phục vụ: S3 • RDS/DynamoDB: LB/API Gateway • DNS/CDN; Vận hành: SQS + worker khi cần: CloudWatch • CloudTrail.](../../diagrams/sd-11-033-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Tiếp theo, đưa web sau load balancer hoặc API Gateway khi phù hợp, dùng Route 53 cho tên miền và CloudFront cho nội dung phân phối. Khi cần xử lý ảnh nền, dùng SQS và worker. CloudWatch cung cấp tín hiệu vận hành; CloudTrail giúp theo dõi hoạt động API được ghi nhận.

Mỗi lượt học nên trả lời: dịch vụ giữ gì, ai có quyền gọi, khi lỗi thì sao và tính phí theo đơn vị nào? Chỉ thêm dịch vụ khi có nhu cầu. Một bài thực hành đầy đủ vòng lưu ảnh, xem ảnh và xử lý lỗi giúp hiểu liên kết giữa các thành phần hơn học riêng từng logo.

## Nhìn hình thử trả lời

Ứng dụng chỉ lưu file và thông tin chủ file. Có cần học data warehouse trước không?

<details>
<summary>Xem đáp án</summary>

Chưa cần. Ưu tiên IAM, đường mạng, compute, storage, DB và quan sát phù hợp với ứng dụng đó.

</details>

## Giới hạn cần nhớ

Không có danh sách “quan trọng nhất” áp dụng mọi đội. Lựa chọn compute và DB phải theo workload, quyền vận hành và ngân sách.

<details>
<summary>Xem sâu hơn</summary>

Dọn tài nguyên sau bài thực hành và theo dõi billing. Kiểm quyền tối thiểu, backup và retry trước khi coi bản demo là đủ cho production.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-most-important-aws-services-to-learn.md).
- [Overview of Amazon Web Services - Overview of Amazon Web Services](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/introduction.html).
- [What is IAM? - AWS Identity and Access Management](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

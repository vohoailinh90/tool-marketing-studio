# Bảng tra dịch vụ AWS theo trách nhiệm

Một bản thiết kế cần trả lời “ai làm việc gì” trước khi điền tên AWS. Với compute: EC2 cho VM, ECS/EKS cho các nhu cầu container, Lambda cho function. Với dữ liệu: S3 giữ object, EBS cung cấp block storage, EFS cung cấp file system được quản lý.

![Compute và storage: EC2 • ECS/EKS • Lambda: S3 • EBS • EFS; DB và messaging: RDS • DynamoDB • ElastiCache: SQS • SNS • EventBridge; Mạng và vận hành: VPC • DNS • CDN • LB: IAM • secrets • metrics/audit.](../../diagrams/sd-11-049-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

RDS hỗ trợ các engine quan hệ; DynamoDB là DB key-value/document được quản; ElastiCache phục vụ caching. SQS hỗ trợ queue, SNS hỗ trợ pub/sub, EventBridge định tuyến event theo tính năng và cấu hình. Route 53, VPC, CloudFront và các load balancer đảm nhận các vai trò mạng khác nhau.

IAM quản quyền; Secrets Manager phục vụ secrets; CloudWatch và CloudTrail phục vụ các nhu cầu quan sát/audit khác nhau. Sau khi map, ghi vì sao chọn, dữ liệu giữ, quyền tối thiểu, giới hạn và giá. Bài này là bảng tra khi thiết kế, khác bài lộ trình học AWS từng bước.

## Nhìn hình thử trả lời

Nhóm worker cần chia việc, mỗi việc giao cho một worker tại một thời điểm theo visibility. Nên xem dịch vụ nào trước?

<details>
<summary>Xem đáp án</summary>

SQS, rồi kiểm delivery, visibility timeout, retry và dead-letter. Consumer vẫn phải xử lý message lặp.

</details>

## Giới hạn cần nhớ

Không gọi S3 là ổ đĩa POSIX, không xem SNS và SQS là cùng mô hình tiêu thụ. Managed service vẫn cần cấu hình bảo mật, backup hoặc retention phù hợp.

<details>
<summary>Xem sâu hơn</summary>

Lưu các quyết định vào tài liệu kiến trúc. Đối chiếu quota, Region và yêu cầu mã hóa trước khi đưa bảng tra thành cấu hình production.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/aws-services-cheat-sheet.md).
- [Overview of Amazon Web Services - Overview of Amazon Web Services](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/introduction.html).
- [Amazon SQS standard queues - Amazon Simple Queue Service](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

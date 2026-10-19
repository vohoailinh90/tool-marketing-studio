# Học AWS từ đâu: nhóm dịch vụ nền tảng, dữ liệu, nhắn tin và vận hành

**AWS (Amazon Web Services) có hàng trăm dịch vụ, nhưng một người mới không cần học hết: chỉ cần biết mỗi nhóm giải việc gì, rồi chọn một hai dịch vụ tiêu biểu mỗi nhóm.** Bài nguồn là một tấm hình lộ trình liệt kê các dịch vụ quan trọng; phần văn bản của nó chỉ nói chung về quy mô. Vì thế bài này không chép tấm hình mà dựng một bản đồ nhóm dịch vụ riêng, ghi rõ chỗ nào là điều nguồn nói và chỗ nào là hiểu biết của người biên soạn.

![Hai khung dịch vụ AWS và một khung bài tập. Khung một, nền tảng: máy chủ ảo cho thuê, S3 lưu đối tượng, VPC là mạng riêng, IAM quản lý ai được làm gì. Khung hai, dữ liệu và nhắn tin: RDS cho cơ sở dữ liệu quan hệ, DynamoDB cho khóa và giá trị, SQS và SNS cho hàng đợi và thông báo. Khung ba, bài tập ứng dụng chia sẻ ảnh: mỗi nhu cầu gắn với một dịch vụ.](../../diagrams/sd-11-033-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ web của Amazon: nền tảng điện toán đám mây cho thuê máy chủ, kho lưu trữ, cơ sở dữ liệu và nhiều dịch vụ khác.
- **VPC** (Virtual Private Cloud) — đám mây riêng ảo: mạng riêng của bạn bên trong AWS.
- **IAM** (Identity and Access Management) — quản lý định danh và quyền truy cập: quyết định ai, hoặc dịch vụ nào, được làm gì.
- **RDS** (Relational Database Service) — dịch vụ cơ sở dữ liệu quan hệ: AWS lo vận hành cơ sở dữ liệu dạng bảng.
- **SQS** (Simple Queue Service) — dịch vụ hàng đợi đơn giản: nơi thông điệp xếp hàng chờ bên nhận lấy.
- **SNS** (Simple Notification Service) — dịch vụ thông báo đơn giản: gửi một thông điệp tới nhiều bên đăng ký.

## Đọc hình

**Điều nguồn nói.** AWS bắt đầu năm 2006 với những dịch vụ đơn giản như `S3` (kho lưu tệp) và `EC2` (máy chủ ảo), nay có hơn 200 dịch vụ phục vụ hàng trăm nghìn doanh nghiệp ở 190 quốc gia. Bài nguồn nói hình là điểm xuất phát và bảng tra nhanh: các dịch vụ nền tảng của điện toán đám mây, và các dịch vụ nâng cao cho nhu cầu riêng như kiến trúc không máy chủ, tự động hóa việc phát hành và vận hành, và học máy.

**Nền tảng.** Bốn thứ mà hầu như mọi hệ thống trên AWS đều chạm tới. `EC2` cho thuê máy chủ ảo. `S3` lưu tệp dạng đối tượng. VPC là mạng riêng nơi các dịch vụ của bạn nằm. IAM quyết định danh tính nào được làm gì, và là nơi nên học sớm vì sai ở đây vừa gây lỗi vừa gây lỗ hổng bảo mật.

**Dữ liệu và nhắn tin.** RDS là cơ sở dữ liệu quan hệ do AWS vận hành, hợp với dữ liệu có bảng và liên kết. DynamoDB lưu theo khóa và giá trị, hợp với truy cập đơn giản ở quy mô lớn. SQS là hàng đợi để tách bên gửi khỏi bên xử lý, SNS gửi một thông báo tới nhiều bên; hai thứ này cùng ý với các mẫu nhắn tin đã có một bài riêng.

**Vận hành và nâng cao.** Lambda chạy một đoạn mã khi có sự kiện mà không cần quản lý máy chủ. CloudWatch gom số đo và nhật ký và đặt cảnh báo. CloudFormation mô tả hạ tầng bằng mã. Các dịch vụ học máy, phân tích dữ liệu và còn nhiều nữa nằm sau các nhóm trên và nên học khi có nhu cầu thật.

Phần "vận hành và nâng cao" và các ví dụ dịch vụ ở trên là hiểu biết chung của người biên soạn, chưa đối chiếu lại với tài liệu của AWS trong phiên viết (không mở được trang từ môi trường); danh sách này không phải là nội dung của tấm hình nguồn.

## Bài tập: gắn nhu cầu với dịch vụ

Không có chương trình chạy ở bài này, vì không có điều gì tính được. Thay vào đó là một bài tập: ứng dụng chia sẻ ảnh cần những việc sau. Hãy tự gắn mỗi việc với một dịch vụ trước khi xem cột bên phải.

| Nhu cầu | Dịch vụ tiêu biểu |
|---|---|
| Lưu ảnh người dùng tải lên | `S3` |
| Đổi cỡ ảnh mỗi khi có ảnh mới | Lambda (chạy khi có sự kiện tải lên) |
| Lưu tài khoản và danh sách ảnh | RDS hoặc DynamoDB |
| Cho phép chỉ dịch vụ xử lý ảnh đọc kho ảnh | IAM |
| Báo những người đang theo dõi | SNS |
| Biết khi nào ứng dụng bắt đầu lỗi | CloudWatch |

Bảng chỉ là một cách chọn hợp lý, không phải đáp án duy nhất: có thể thay RDS bằng DynamoDB, hoặc đặt hàng đợi SQS giữa khâu tải lên và đổi cỡ ảnh.

## Giới hạn cần nhớ

Bài không chép tấm hình nguồn, và phần văn bản nguồn không nêu tên dịch vụ nào ngoài `S3` và `EC2`, nên danh sách dịch vụ ở đây là của người biên soạn; nó có thể không trùng với tấm hình. Các con số 2006, hơn 200 dịch vụ, 190 quốc gia là của nguồn tại thời điểm viết bài đó, chưa đối chiếu với AWS hôm nay. Bài không nói giá, vùng, hay cách cấu hình từng dịch vụ.

## Nhìn hình trả lời

Một nhóm nhỏ muốn đặt cả mười máy chủ vào một mạng mà ai cũng vào được cho nhanh. Trong các nhóm trên, hai nhóm nào nên học trước để làm việc này an toàn?

<details>
<summary>Xem đáp án</summary>

Mạng (VPC) và định danh (IAM): VPC để quyết định máy nào nằm trong mạng riêng, máy nào ra ngoài; IAM để quyết định ai và dịch vụ nào được làm gì. Cách đặt "ai cũng vào được" trái với cả hai.
Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một đoạn mở đầu về quy mô của AWS cùng một tấm hình lộ trình. Bài này giữ ý "bắt đầu từ các dịch vụ nền tảng rồi mới tới dịch vụ nâng cao", thêm bản đồ nhóm, bảng gắn nhu cầu với dịch vụ, và nói rõ rằng nội dung tấm hình không được chép.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-most-important-aws-services-to-learn.md): quy mô AWS và ý lộ trình. Bản đồ nhóm, bài tập và đáp án là của người biên soạn.
- [AWS — tài liệu các dịch vụ](https://docs.aws.amazon.com/): mô tả từng dịch vụ. Chưa mở lại trong phiên viết (không mở được trang từ môi trường); kiến thức chung của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

# Chi phí cloud dễ bị bỏ sót

Bạn dừng máy thử nghiệm và nghĩ hóa đơn sẽ về không. Nhưng volume, snapshot, địa chỉ IP và load balancer có thể còn tồn tại. Chi phí theo tài nguyên và mức sử dụng, không chỉ theo việc ứng dụng có khách hay không.

![Tài nguyên còn tồn tại: Volume • snapshot • IP: NAT • load balancer; Theo mức sử dụng: Request • data transfer: Log/metrics • multipart parts; Kiểm soát: Owner tag + budget alert: Đọc bảng giá hiện hành.](../../diagrams/sd-11-035-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Ngoài compute, cần nhìn storage, request, data transfer, NAT, load balancer, public IPv4 và observability. File ít nhưng `GET`/`LIST` nhiều vẫn có thể tốn phí đáng kể. Multipart upload chưa hoàn tất có thể giữ các phần đã tải. Log giữ lâu hoặc metrics có quá nhiều chuỗi cũng tăng hóa đơn.

Gắn owner và môi trường cho tài nguyên, đặt budget alert và kiểm chi phí theo nhóm hàng tuần. Với một tính năng mới, ước tính cả đường dữ liệu: đọc ở đâu, qua mạng nào và giữ bao lâu. “Free tier” có giới hạn, điều kiện tài khoản và thay đổi theo dịch vụ; phải đối chiếu bảng giá hiện hành.

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; AWS hiện có mục giá cho public IPv4.
- **EC** (Elastic Compute) — điện toán co giãn: phần chữ cái đầu của EC2, dịch vụ máy ảo của Amazon (tên đầy đủ Elastic Compute Cloud, hai chữ C thành số 2); ví dụ trong bài: máy EC2 đã dừng.
- **EBS** (Elastic Block Store) — kho khối co giãn của Amazon: ổ đĩa ảo gắn vào một máy ảo; EBS volume và snapshot còn lại có thể vẫn bị tính phí.
- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ và chuyển gói tin giữa các máy; địa chỉ IP là địa chỉ của một máy trên mạng; volume, snapshot, địa chỉ IP và load balancer có thể còn tồn tại.
- **IPv4** (Internet Protocol version 4) — phiên bản 4 của giao thức Internet: địa chỉ gồm bốn số, nguồn địa chỉ có hạn nên thường tính phí hoặc phải dùng chung; public IPv4 là một khoản chi phí cần nhìn cạnh storage, request và data transfer.
- **NAT** (Network Address Translation) — dịch địa chỉ mạng: thiết bị đổi địa chỉ nguồn hoặc đích của gói tin khi đi qua; nhờ nó nhiều máy dùng chung được một địa chỉ công cộng; NAT cũng là một khoản chi phí cần nhìn.

## Nhìn hình thử trả lời

EC2 đã dừng nhưng EBS volume và snapshot còn. Có thể vẫn bị tính phí không?

<details>
<summary>Xem đáp án</summary>

Có. Dừng compute không đồng nghĩa xóa storage hay các tài nguyên liên quan.

</details>

## Giới hạn cần nhớ

Không dùng quy tắc cũ “Elastic IP chỉ tính tiền khi vượt năm địa chỉ”. AWS hiện có mục giá public IPv4; giá và miễn giảm phụ thuộc điều kiện hiện hành.

<details>
<summary>Xem sâu hơn</summary>

Lifecycle có thể dọn incomplete multipart uploads; xóa volume không tự xóa mọi snapshot. Trước khi dọn, kiểm ownership và yêu cầu giữ dữ liệu.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/hidden-costs-of-the-cloud.md).
- [Amazon VPC Pricing](https://aws.amazon.com/vpc/pricing/).
- [S3 Pricing](https://aws.amazon.com/s3/pricing/).
- [Configuring a bucket lifecycle configuration to delete incomplete multipart uploads - Amazon Simple Storage Service](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpu-abort-incomplete-mpu-lifecycle-config.html).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

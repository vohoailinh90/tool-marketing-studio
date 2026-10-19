# Kiến trúc lõi của Reddit: đường đồng bộ và đường chạy sau

**Theo bài nguồn, Reddit phục vụ hơn 1 tỷ người dùng mỗi tháng bằng một chuỗi khá quen thuộc: CDN ở ngoài cùng, bộ cân bằng tải, các dịch vụ sau một lớp GraphQL, Postgres có memcached đứng trước, và một hàng đợi việc cho những thao tác tốn kém.**
Bài này chia kiến trúc đó thành hai đường: phần trả lời ngay cho người dùng, và phần được đẩy sang chạy sau.

![Hai dải. Đường trả lời ngay: CDN của Fastly đứng trước ứng dụng; bộ cân bằng tải chuyển yêu cầu tới đúng dịch vụ; các dịch vụ chuyển từ khối nguyên Python sang microservice viết bằng Go; lớp API dùng GraphQL, từ đầu năm 2021 chuyển sang GraphQL Federation; dữ liệu lõi trong Postgres, memcached đứng trước để giảm tải, Cassandra cho tính năng mới. Đường chạy sau: bỏ phiếu và gửi liên kết được đẩy vào hàng đợi RabbitMQ cho các worker xử lý; Kafka chuyển dữ liệu theo thời gian thực để chạy luật kiểm duyệt; Debezium bắt thay đổi dữ liệu để sao chép và giữ bộ đệm nhất quán. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-023-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy chủ đặt gần người dùng, trả nội dung thay cho máy chủ gốc.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách ứng dụng gọi dữ liệu và chức năng của hệ thống.
- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, cách ứng dụng mô tả dữ liệu mình muốn lấy.
- **DGS** (Domain Graph Service) — dịch vụ đồ thị theo miền: một API GraphQL nhỏ lo một phần dữ liệu, được ghép với các phần khác.
- **AWS** (Amazon Web Services) — dịch vụ đám mây của Amazon, nơi Reddit chạy ứng dụng.
- **CI** (Continuous Integration) — tích hợp liên tục: tự động build và kiểm thử mỗi thay đổi mã; chữ CI trong tên công cụ Drone CI.

## Đọc hình

Bài nguồn nói nó dựa trên nhiều bài blog kỹ thuật của Reddit, và vì kiến trúc luôn thay đổi nên có thể đã khác.

**Đường trả lời ngay.**
- Ngoài cùng là CDN của Fastly, đứng trước ứng dụng.
- Phía người dùng: Reddit bắt đầu dùng jQuery từ đầu năm 2009, sau dùng TypeScript, nay chuyển sang các framework Node.js hiện đại; Reddit cũng có ứng dụng Android và iOS.
- Bộ cân bằng tải đứng trước, chuyển yêu cầu tới đúng dịch vụ.
- Reddit bắt đầu là một khối nguyên viết bằng Python, rồi chuyển dần sang microservice viết bằng Go.
- Lớp API dùng GraphQL rất nhiều. Từ đầu năm 2021, Reddit chuyển sang GraphQL Federation, tức ghép nhiều API GraphQL nhỏ gọi là DGS. Năm 2022, đội GraphQL thêm nhiều subgraph viết bằng Go cho các thực thể lõi, tách dần khối GraphQL lớn.
- Dữ liệu lõi nằm trong Postgres; memcached đứng trước để giảm tải cho cơ sở dữ liệu. Cassandra được dùng nhiều cho tính năng mới vì khả năng chịu lỗi và luôn sẵn sàng.

**Đường chạy sau.**
- Thao tác tốn kém như bỏ phiếu hay gửi liên kết được đẩy vào hàng đợi việc qua RabbitMQ, rồi các worker xử lý.
- Để kiểm tra an toàn nội dung và kiểm duyệt, Kafka chuyển dữ liệu theo thời gian thực để chạy luật trên đó.
- Debezium chạy quá trình bắt thay đổi dữ liệu (change data capture) để sao chép dữ liệu và giữ bộ đệm nhất quán.

**Hạ tầng.** Ứng dụng và dịch vụ nội bộ chạy trên AWS và Kubernetes; triển khai và hạ tầng dùng Spinnaker, Drone CI và Terraform.

## Giới hạn cần nhớ

Bài nguồn liệt kê công nghệ và vai trò một dòng, không nói quy mô từng phần, không nói hàng đợi xử lý lỗi thế nào, và không nói Debezium giữ bộ đệm nhất quán ra sao. Con số 1 tỷ người dùng mỗi tháng là của bài nguồn. Cách chia "đường trả lời ngay, đường chạy sau" là của người biên soạn.

## Nhìn hình thử trả lời

Một người bấm bỏ phiếu cho một bài. Theo hình, vì sao người đó thấy nút đổi màu ngay, dù việc đếm phiếu có thể chưa xong?

<details>
<summary>Xem đáp án</summary>

Vì bỏ phiếu là thao tác tốn kém nên được đẩy vào hàng đợi RabbitMQ; hệ thống nhận yêu cầu, trả lời ngay, còn worker xử lý phần nặng sau. Người dùng không phải chờ phần việc đó.

</details>

<details>
<summary>Xem sâu hơn: cái giá của việc đẩy sang chạy sau</summary>

- Số phiếu hiển thị có thể trễ một chút so với thực tế.
- Cần theo dõi độ dài hàng đợi; nếu worker chậm, việc dồn lại.
- Cần quyết định làm gì khi một việc trong hàng đợi lỗi: thử lại, hay bỏ qua.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/reddit's-core-architecture.md): các thành phần và công nghệ của kiến trúc lõi Reddit.

Đã đọc nguồn ngày 2026-10-19. Blog kỹ thuật của Reddit chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

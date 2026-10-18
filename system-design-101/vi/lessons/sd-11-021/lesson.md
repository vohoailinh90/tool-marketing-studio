# Mạng AWS điển hình: chọn đường kết nối đúng

Trong một Region, VPC chứa các subnet gắn với từng Availability Zone. Một thiết kế web có thể đặt load balancer ở subnet public, ứng dụng và DB ở subnet private. Route table quyết định đường đi; security group giới hạn lưu lượng được phép.

![Trong VPC: Subnet thuộc một AZ: Route table + security group; Internet / AWS service: IGW • NAT cho egress IPv4: Gateway / interface endpoint; Mạng khác: VPN • Direct Connect: Peering • Transit Gateway.](../../diagrams/sd-11-021-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Internet Gateway hỗ trợ đường ra/vào internet cho tài nguyên đáp ứng điều kiện định tuyến và địa chỉ. Với IPv4, ứng dụng private có thể đi ra qua NAT Gateway mà không mở đường khởi tạo kết nối trực tiếp từ internet. Gateway endpoint phục vụ S3/DynamoDB; interface endpoint dùng PrivateLink cho dịch vụ được hỗ trợ.

Để nhân viên truy cập, cân nhắc Client VPN. Kết nối mạng công ty có Site-to-Site VPN hoặc Direct Connect. VPC peering nối các VPC theo cặp; Transit Gateway đóng vai trò hub khi có nhiều mạng. Mỗi đường cần cấu hình route, quyền và DNS thích hợp.

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; bài nói về cách chọn đường kết nối mạng trong AWS.
- **VPC** (Virtual Private Cloud) — đám mây riêng ảo: mạng riêng bạn tự chia trong cloud, gồm các subnet, bảng định tuyến và nhóm bảo mật; VPC chứa các subnet, mỗi subnet gắn với một AZ.
- **AZ** (Availability Zone) — vùng sẵn sàng: một cụm trung tâm dữ liệu tách biệt trong cùng một Region, để lỗi ở nơi này ít lan sang nơi khác; mỗi subnet thuộc một AZ.
- **DB** (DataBase) — cơ sở dữ liệu: nơi lưu dữ liệu có tổ chức để ghi và tìm lại; một thiết kế web có thể đặt load balancer ở subnet public, còn ứng dụng và DB ở subnet private.
- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" của Internet, đổi tên miền thành địa chỉ mạng để biết tìm dịch vụ ở đâu; mỗi đường kết nối cần cấu hình route, quyền và DNS thích hợp.
- **IGW** (Internet GateWay) — cổng Internet: thành phần cho mạng riêng trong cloud nói chuyện với Internet; trong hình, IGW là cổng ra Internet của mạng, đi cùng NAT cho lưu lượng đi ra.
- **NAT** (Network Address Translation) — dịch địa chỉ mạng: thiết bị đổi địa chỉ nguồn hoặc đích của gói tin khi đi qua; nhờ nó nhiều máy dùng chung được một địa chỉ công cộng; trong hình, NAT phục vụ lưu lượng đi ra qua IPv4.
- **IPv4** (Internet Protocol version 4) — phiên bản 4 của giao thức Internet: địa chỉ gồm bốn số, nguồn địa chỉ có hạn nên thường tính phí hoặc phải dùng chung; trong hình, lưu lượng đi ra qua IPv4 cần NAT.
- **VPN** (Virtual Private Network) — mạng riêng ảo: đường nối có mã hóa chạy qua Internet, làm các nơi xa nhau như cùng một mạng riêng; trong hình, VPN là một cách nối tới mạng khác, cùng Direct Connect, peering và Transit Gateway.

## Nhìn hình thử trả lời

App private cần đọc S3. Có bắt buộc qua NAT không?

<details>
<summary>Xem đáp án</summary>

Không. Có thể dùng S3 gateway endpoint với route và policy đúng, tùy nhu cầu truy cập.

</details>

## Giới hạn cần nhớ

Subnet “public” không làm mọi instance tự có internet. Peering không tự cho định tuyến bắc cầu; gateway endpoint không phải interface endpoint.

<details>
<summary>Xem sâu hơn</summary>

Triển khai nhiều AZ phải xét cả subnet, load balancer và đường egress. Đặt route qua NAT ở AZ khác có thể thêm chi phí và phụ thuộc vào AZ đó.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/typical-aws-network-architecture-in-one-diagram.md).
- [What is Amazon VPC? - Amazon Virtual Private Cloud](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html).
- [Gateway endpoints - Amazon Virtual Private Cloud](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html).
- [How VPC peering connections work - Amazon Virtual Private Cloud](https://docs.aws.amazon.com/vpc/latest/peering/invalid-peering-configurations.html).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

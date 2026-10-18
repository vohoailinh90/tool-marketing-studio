# So sánh AWS, Azure và Google Cloud theo vai trò

Đội muốn chuyển một ứng dụng giữa cloud cần map trách nhiệm trước khi map tên sản phẩm. VM có EC2, Azure Virtual Machines và Compute Engine. Object storage có S3, Blob Storage và Cloud Storage. Các tên này giúp tìm điểm bắt đầu tra tài liệu.

![Compute (VM): EC2 • Azure Virtual Machines: Google Compute Engine; Object storage: S3 • Blob • Cloud Storage: Kiểm API, quyền và giới hạn; DB quan hệ AWS / GCP: Amazon RDS • Cloud SQL: Chọn theo engine và nhu cầu; DB quan hệ trên Azure: Azure SQL Database: Azure Database for PostgreSQL; Kubernetes: EKS • AKS • GKE: Map vai trò, rồi kiểm giới hạn.](../../diagrams/sd-11-047-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Với managed relational DB, có thể xem RDS, Azure SQL hoặc Azure Database for PostgreSQL và Cloud SQL tùy engine. Với Kubernetes được quản, xem EKS, AKS và GKE. Với function, xem Lambda, Azure Functions và Cloud Run functions. Các nhóm có thể chứa nhiều lựa chọn khác nữa.

Sau ánh xạ, kiểm API, identity, network, Region, quota, SLA và chi phí. Ví dụ, chuyển object storage không chỉ thay endpoint: phải xét quyền, event notification, consistency và thư viện client. Mục tiêu multi-cloud cũng cần lợi ích rõ, vì nó thêm phần vận hành và kiểm thử tương thích.

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; bài so sánh AWS, Azure và Google Cloud theo vai trò.
- **GCP** (Google Cloud Platform) — nền tảng đám mây của Google; GCP là cách gọi nền tảng đám mây của Google trong hình.
- **VM** (Virtual Machine) — máy ảo: máy tính giả lập chạy bằng phần mềm trên một máy thật; vai trò VM có EC2, Azure Virtual Machines và Compute Engine.
- **EC** (Elastic Compute) — điện toán co giãn: phần chữ cái đầu của EC2, dịch vụ máy ảo của Amazon (tên đầy đủ Elastic Compute Cloud, hai chữ C thành số 2); EC2 là sản phẩm VM của AWS.
- **EKS** (Elastic Kubernetes Service) — dịch vụ Kubernetes được quản lý của Amazon: chạy và điều phối container; trong hình, nhóm Kubernetes có EKS.
- **AKS** (Azure Kubernetes Service) — dịch vụ Kubernetes được quản lý của Azure: chạy và điều phối container, nhà cung cấp lo phần điều khiển cụm; trong hình, nhóm Kubernetes có AKS.
- **GKE** (Google Kubernetes Engine) — dịch vụ Kubernetes được quản lý của Google: chạy và điều phối container; trong hình, nhóm Kubernetes có GKE.
- **RDS** (Relational Database Service) — dịch vụ cơ sở dữ liệu quan hệ do Amazon vận hành hộ: nhà cung cấp lo máy chủ và sao lưu; RDS là sản phẩm cơ sở dữ liệu quan hệ của AWS trong hình.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; trong hình, Cloud SQL và Azure SQL Database là cơ sở dữ liệu quan hệ.
- **DB** (DataBase) — cơ sở dữ liệu: nơi lưu dữ liệu có tổ chức để ghi và tìm lại; trong hình, DB quan hệ trên Azure và AWS cùng GCP khác tên sản phẩm.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách để một chương trình yêu cầu dữ liệu hoặc chức năng của chương trình khác; ánh xạ vai trò xong phải kiểm API, quyền và giới hạn.
- **IAM** (Identity and Access Management) — quản lý danh tính và quyền truy cập: cho biết ai là ai và được làm gì với tài nguyên; dù dùng chung engine, backup, HA và IAM vẫn khác nhau.
- **HA** (High Availability) — tính sẵn sàng cao: thiết kế để dịch vụ vẫn chạy khi một phần của hệ thống lỗi; backup, HA và IAM vẫn khác nhau giữa các nhà cung cấp.
- **SLA** (Service Level Agreement) — thỏa thuận mức dịch vụ: cam kết bằng văn bản giữa nhà cung cấp và khách hàng về mức dịch vụ và hậu quả khi không đạt; sau ánh xạ cần kiểm API, identity, network, Region, quota, SLA và chi phí.
- **URL** (Uniform Resource Locator) — địa chỉ đầy đủ của một tài nguyên trên web, ví dụ địa chỉ một trang; bài hỏi có thể chỉ đổi URL rồi coi migration xong không.

## Nhìn hình thử trả lời

S3 và Blob Storage đều lưu object. Có thể chỉ đổi URL rồi coi migration xong không?

<details>
<summary>Xem đáp án</summary>

Không. Cần kiểm API, quyền, key, metadata, sự kiện và tính đúng của dữ liệu đã chuyển.

</details>

## Giới hạn cần nhớ

Cùng vai trò không có nghĩa tương đương tính năng hay thay trực tiếp không sửa mã. Tên, gói và hỗ trợ của dịch vụ thay đổi theo thời gian.

<details>
<summary>Xem sâu hơn</summary>

Chọn engine chung có thể giảm chi phí chuyển đổi, nhưng vẫn có khác biệt ở backup, HA và IAM. Thử migration với workload và failure mode thực tế.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-comparison-cheat-sheet.md).
- [Compare AWS and Azure services to Google Cloud | Get started | Google Cloud Documentation](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison).
- [Azure for AWS Professionals - Azure Architecture Center | Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/aws-professional/services).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

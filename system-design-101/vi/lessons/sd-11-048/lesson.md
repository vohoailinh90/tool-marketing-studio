# Đường ống dữ liệu lớn trên ba đám mây: năm chặng, và kiểm bảng nguồn bằng bảng của Microsoft

**Mọi đường ống dữ liệu lớn đều đi qua năm chặng: thu thập, hồ dữ liệu, tính toán, kho dữ liệu, trình bày. Bài nguồn gán cho mỗi chặng một dịch vụ của AWS, Azure và Google Cloud. Bài này giữ năm chặng, rồi lấy hai trang so sánh của Microsoft làm thước đo: trong mười phép ghép của bảng nguồn, bảy phép được Microsoft ghép giống vậy, ba phép thì không.**
Phép kiểm chỉ đối chiếu tên dịch vụ trong các bảng, không đo hiệu năng hay chi phí.

![Ba khung. Khung một, năm chặng: thu thập, hồ dữ liệu, tính toán, kho dữ liệu, trình bày. Khung hai, các dịch vụ bài nguồn nêu: AWS dùng Kinesis, S3, EMR, Redshift, QuickSight; Azure dùng Event Hubs, Data Lake Store, Databricks, Cosmos DB, Power BI; Google Cloud dùng PubSub, Cloud Storage, DataProc và DataFlow, BigQuery, Data Studio. Khung ba, kiểm bằng hai trang của Microsoft: bảy trên mười phép ghép khớp; ba phép lệch là Cloud Storage với Data Lake Store, và hai phép kho dữ liệu với Cosmos DB.](../../diagrams/sd-11-048-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon.
- **BI** (Business Intelligence) — phân tích kinh doanh; xuất hiện trong tên `Power BI`, công cụ vẽ báo cáo của Microsoft.
- **DB** (DataBase) — cơ sở dữ liệu; xuất hiện trong tên `Cosmos DB` của Azure.
- **EMR** (Elastic MapReduce) — tên dịch vụ xử lý dữ liệu lớn của AWS.
- **GCP** (Google Cloud Platform) — tên cũ của Google Cloud; bài nguồn dùng tên này trong phần chữ.

## Đọc hình

**Năm chặng.** Bài nguồn viết rằng mỗi nền tảng có bộ dịch vụ phủ cả vòng đời của dữ liệu:

1. **Thu thập (ingestion):** gom dữ liệu từ nhiều nguồn.
2. **Hồ dữ liệu (data lake):** lưu dữ liệu thô.
3. **Tính toán (computation):** xử lý và phân tích dữ liệu.
4. **Kho dữ liệu (data warehouse):** lưu dữ liệu có cấu trúc.
5. **Trình bày (presentation):** vẽ biểu đồ và báo cáo.

Dịch vụ theo từng nền tảng, đúng như nguồn viết:

| Chặng | AWS | Azure | Google Cloud |
|---|---|---|---|
| Thu thập | `Kinesis` | `Event Hubs` | `PubSub` |
| Hồ dữ liệu | `S3` | `Data Lake Store` | `Cloud Storage` |
| Tính toán | `EMR` | `Databricks` | `DataProc`, `DataFlow` |
| Kho dữ liệu | `Redshift` | `Cosmos DB` | `BigQuery` |
| Trình bày | `QuickSight` | `Power BI` | `Data Studio` |

## Thử: kiểm bảng bằng hai trang của Microsoft

Ngày 2026-10-19, người biên soạn đọc hai trang so sánh của Microsoft (trang "Azure for AWS professionals" và trang "Google Cloud to Azure services comparison", kho `MicrosoftDocs/architecture-center` tại commit `8e2c239`) và hỏi với mỗi chặng: Microsoft có ghép dịch vụ của AWS (hoặc Google Cloud) với đúng dịch vụ Azure mà bảng nguồn ghi không? Mười phép ghép:

| Chặng | AWS với dịch vụ Azure của nguồn | Google Cloud với dịch vụ Azure của nguồn |
|---|---|---|
| Thu thập | khớp: `Kinesis Data Streams` với `Event Hubs` | khớp: `Cloud Pub/Sub` với `Event Hubs` |
| Hồ dữ liệu | khớp: `S3` với `Azure Data Lake Storage` (tên hiện nay của trang, nguồn ghi "Data Lake Store") | lệch: Microsoft ghép `Cloud Storage` với `Azure Blob Storage` |
| Tính toán | khớp: `EMR` với `Azure Databricks` | khớp: `Dataproc` và `Cloud Dataflow` đều với `Azure Databricks` |
| Kho dữ liệu | lệch: `Redshift` được ghép với `Fabric Data Warehouse` và `Azure Databricks SQL` | lệch: `BigQuery` được ghép với `Fabric Data Warehouse` và `Azure Databricks` (ở mục phân tích còn với `Azure Data Explorer`) |
| Trình bày | khớp: `QuickSight` với `Power BI` | khớp: `Looker Studio` (nguồn ghi "Data Studio") với `Power BI` |

Bảy phép khớp, ba phép lệch. Phép lệch rõ nhất là chặng kho dữ liệu: `Cosmos DB` chỉ xuất hiện trong trang Google Cloud như đối tác của `Cloud Spanner` và `Cloud Firestore` (cơ sở dữ liệu), và không có trong trang phân tích của bộ trang AWS; Microsoft không ghép nó với kho dữ liệu của bên nào. Phép lệch ở hồ dữ liệu nhẹ hơn: hai trang chọn hai dịch vụ lưu trữ Azure khác nhau cho "hồ" và cho "đối tượng". Về tên: trang Microsoft dùng `Looker Studio`, nguồn ghi `Data Studio`; bài không kiểm lịch sử đổi tên.

## Giới hạn cần nhớ

Hai trang của Microsoft là một thước đo đáng tin về cách Microsoft ghép dịch vụ, không phải sự thật khách quan, và chúng ghi ngày cập nhật năm 2026 trong khi bài nguồn viết sớm hơn; một phép "lệch" có thể chỉ phản ánh dịch vụ đã đổi. Cả hai trang tự nói chỉ ghép dịch vụ gần tương đương, không bảo đảm khớp từng tính năng. Bài không kiểm bảng nguồn với tài liệu của AWS hay Google Cloud, không so sánh tính năng, giá, hay hiệu năng.

## Nhìn hình trả lời

Một đội đang dùng `Redshift` và cần chọn dịch vụ Azure cho chặng kho dữ liệu. Bảng nguồn ghi `Cosmos DB`. Theo hai trang của Microsoft, họ nên đọc tài liệu của dịch vụ nào trước, và vì sao không nên theo bảng nguồn ở chặng này?

<details>
<summary>Xem đáp án</summary>

Nên đọc `Fabric Data Warehouse` và `Azure Databricks SQL`: trang AWS của Microsoft ghép `Redshift` với hai dịch vụ này. `Cosmos DB` không được Microsoft ghép với kho dữ liệu nào trong hai trang; nó xuất hiện như cơ sở dữ liệu cho ứng dụng. Vì vậy dòng kho dữ liệu của bảng nguồn nên được coi là cần kiểm lại. Đây là suy luận của người biên soạn từ các bảng.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một ảnh, một danh sách năm chặng và ba đoạn ngắn nêu dịch vụ của từng nền tảng. Bài này giữ năm chặng và bảng dịch vụ, bỏ ảnh, rồi thêm phép đối chiếu mười phép ghép với hai trang của Microsoft.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/big-data-pipeline-cheatsheet-for-aws-azure-and-google-cloud.md): năm chặng và dịch vụ theo từng nền tảng. Phép đối chiếu là của người biên soạn.
- [Microsoft — Azure for AWS professionals: Analytics](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/aws-professional/analytics.md) và [Google Cloud to Azure services comparison](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/gcp-professional/services.md): các bảng ghép dịch vụ tại commit `8e2c239`.

Đã đọc nguồn ngày 2026-10-19. Không đối chiếu với tài liệu của AWS hay Google Cloud (kiến thức chung của người biên soạn, chưa đối chiếu).
Bài viết và hình được thiết kế độc lập.

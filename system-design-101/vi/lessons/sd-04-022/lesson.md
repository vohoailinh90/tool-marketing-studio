# Bảng tra cơ sở dữ liệu trên đám mây: đọc một dòng thế nào cho đúng

**Bảng tra ghép dịch vụ của các nhà cung cấp đám mây theo từng loại cơ sở dữ liệu. Nó giúp bạn tìm tên, không giúp bạn biết hai cái tên trên cùng một dòng khác nhau ở đâu.**
Bài này dựng một bảng tra từ chính các trang so sánh dịch vụ của Azure Architecture Center (Azure so với AWS, Azure so với Google Cloud), rồi chỉ ra những gì các trang đó dặn thêm mà một dòng trong bảng không nói được.

![Bốn khung, theo bảng so sánh của Azure Architecture Center. Khung một, cơ sở dữ liệu quan hệ: có quản lý là Amazon RDS, Azure SQL Database và Azure Database for MySQL, PostgreSQL, Google Cloud SQL; serverless là Aurora Serverless và Azure SQL Database serverless; mở rộng ngang là Cloud Spanner. Khung hai: khóa–giá trị và tài liệu là DynamoDB và Cosmos DB for NoSQL; tài liệu kiểu MongoDB là Amazon DocumentDB và Azure DocumentDB; cột rộng kiểu Cassandra là Amazon Keyspaces và Cosmos DB for Apache Cassandra. Khung ba: đồ thị là Neptune và Cosmos DB for Apache Gremlin; bộ nhớ đệm là ElastiCache, Memorystore và Azure Managed Redis. Khung bốn, bốn điều bảng tra không nói.](../../diagrams/sd-04-022-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon.
- **RDS** (Relational Database Service) — dịch vụ cơ sở dữ liệu quan hệ có quản lý của AWS.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc của cơ sở dữ liệu quan hệ; nằm trong tên Azure SQL Database, Cloud SQL, MySQL và PostgreSQL.
- **DB** (DataBase) — cơ sở dữ liệu; nằm trong tên DynamoDB, DocumentDB, MemoryDB, MongoDB và Cosmos DB.
- **NoSQL** (Not only SQL) — tên chung cho các cơ sở dữ liệu không theo mô hình bảng quan hệ; Azure dùng nó trong tên Cosmos DB for NoSQL.
- **RDF** (Resource Description Framework) — một cách mô tả dữ liệu đồ thị bằng các bộ ba chủ thể, quan hệ, đối tượng; khác với property graph, nơi nút và cạnh mang thuộc tính.

## Đọc hình

**Khung 1 · Quan hệ.** Trang so sánh AWS với Azure ghép Amazon RDS với Azure SQL Database, Azure Database for MySQL và Azure Database for PostgreSQL, và dặn chọn theo bộ máy cơ sở dữ liệu trước, rồi mới so khả năng sẵn sàng, bản sao đọc, cách mở rộng. Trang so sánh Google Cloud với Azure ghép Cloud SQL với các dịch vụ đó. Dòng "serverless" ghép Aurora Serverless với Azure SQL Database serverless, kèm lời nhắc hai bên mở rộng và tính tiền khác nhau. Dòng "quan hệ mở rộng ngang" có Cloud Spanner ở phía Google.

**Khung 2 · Tài liệu, khóa–giá trị, cột rộng.** DynamoDB được ghép với Azure Cosmos DB for NoSQL, cùng lời dặn: cả hai chia dữ liệu theo khóa phân vùng, nhưng tính nhất quán, chỉ mục, truy vấn, giao dịch và cách tính tiền khác nhau, nên phải tính trước việc sửa ứng dụng và mô hình dữ liệu. Các dịch vụ tương thích MongoDB và Apache Cassandra được ghép theo giao diện mà chúng nói được.

**Khung 3 · Đồ thị và bộ nhớ đệm.** Amazon Neptune đi với Azure Cosmos DB for Apache Gremlin; ElastiCache (AWS) và Memorystore (Google) đi với Azure Managed Redis.

**Khung 4 · Bốn điều bảng tra không nói.**

1. **Giao diện tương thích chưa phải là giống nhau.** Trang so sánh của Azure viết thẳng: một giao diện lập trình tương thích không bảo đảm tính năng và cách vận hành ngang nhau; trước khi chuyển, hãy so cách chia phân vùng, tính nhất quán, giao dịch, chỉ mục, cách truy vấn, luồng thay đổi, phân tán toàn cầu, đơn vị thông lượng và độ tương thích của thư viện kết nối.
2. **Có dòng không có ô tương đương.** Amazon MemoryDB được thiết kế làm cơ sở dữ liệu chính, bền, nói giao thức Redis. Trang so sánh ghi phía Azure "không có tương đương trực tiếp": Azure Managed Redis là bộ nhớ đệm và kho dữ liệu tạm, không nên làm nơi giữ dữ liệu gốc.
3. **Cùng là "đồ thị", phạm vi khác nhau.** Neptune hỗ trợ cả property graph và RDF; Cosmos DB for Gremlin chỉ hỗ trợ property graph với ngôn ngữ Gremlin. Ứng dụng dùng RDF phải thiết kế khác.
4. **Người xếp khác nhau, ô khác nhau.** Ở trang so sánh với Google, Cloud Spanner nằm ở dòng "quan hệ mở rộng ngang" nhưng ô Azure lại là Cosmos DB for NoSQL, một kho phi quan hệ, kèm Azure Database for PostgreSQL với elastic clusters chia shard. Một dòng của bảng tra là ý kiến của người lập bảng, không phải sự tương đương đã được kiểm.

## Giới hạn cần nhớ

- Bảng ở đây chỉ lấy những dòng mà hai trang so sánh của Azure có; nó không đầy đủ, và tên dịch vụ đám mây đổi thường xuyên. Trang AWS với Azure ghi ngày 2026-10-05, trang Google Cloud với Azure ghi ngày 2026-04-08.
- Cả hai trang do Microsoft viết, nhìn từ phía Azure. Bài không đối chiếu được với tài liệu của AWS và Google vì không mở được từ môi trường biên soạn, và không có thử nghiệm vì cần tài khoản đám mây.
- Bài nguồn tự ghi rằng tài liệu của Google về trường hợp dùng còn ít nên vài ô có thể chưa chính xác; đó cũng là lý do bài này không lặp lại bảng của bài nguồn.

## Nhìn hình trả lời

Một nhóm đang dùng Amazon MemoryDB làm nơi lưu chính cho giỏ hàng, và định chuyển sang Azure bằng cách tìm dòng "Redis" trong bảng tra rồi chọn Azure Managed Redis. Nhìn khung 4: kế hoạch này thiếu gì?

<details>
<summary>Xem đáp án</summary>

MemoryDB là cơ sở dữ liệu chính, bền; Azure Managed Redis là bộ nhớ đệm và kho dữ liệu tạm, và trang so sánh của Azure dặn không dùng nó làm nơi giữ dữ liệu gốc. Theo trang đó, phía Azure nên có một cơ sở dữ liệu bền (ví dụ Azure Cosmos DB) giữ giỏ hàng, còn Azure Managed Redis chỉ làm lớp đệm nếu cần. Cùng nói giao thức Redis không có nghĩa cùng lời hứa về dữ liệu.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn là một hình bảng tra các dịch vụ cơ sở dữ liệu trên đám mây và lựa chọn mã nguồn mở tương ứng, kèm lời nhắc rằng vài ô về Google có thể chưa chính xác. Bài này không dùng hình đó: bảng được dựng lại từ hai trang so sánh của Azure Architecture Center, và phần chính của bài là những lời dặn đi kèm mỗi dòng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-database-cheat-sheet.md): bảng tra cơ sở dữ liệu trên đám mây.
- Azure Architecture Center, tại commit cố định, đọc từ bản clone của kho: [Database services on Azure and AWS](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/aws-professional/databases.md), [Google Cloud to Azure services comparison, mục Database](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/gcp-professional/services.md).

Đã đọc nguồn ngày 2026-10-18. Bài không có thử nghiệm riêng: các dịch vụ đám mây không dùng được từ môi trường biên soạn.
Bài viết và hình được thiết kế độc lập.

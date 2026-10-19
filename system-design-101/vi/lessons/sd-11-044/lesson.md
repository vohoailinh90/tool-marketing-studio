# Khung thảo luận thiết kế hệ thống: mười ba mục xếp thành ba loại, và hai câu hỏi khung không nêu

**Bài nguồn là một danh sách kiểm để dẫn cuộc thảo luận khi phỏng vấn thiết kế hệ thống: mười ba chủ đề rồi "và hơn thế nữa". Đọc như một danh sách phẳng thì dễ quên rằng chúng thuộc ba loại khác nhau: sáu thành phần mua được trên đám mây, hai bài toán phải tự quyết, và năm tính chất của cả hệ thống. Bài này xếp chúng theo ba loại rồi thử mỗi loại với tài liệu của Microsoft.**
Kết quả cho thấy sáu thành phần đều có dịch vụ tương ứng ở cả ba nơi, còn hai câu hỏi về chi phí và vận hành thì danh sách không hỏi.

![Ba khung. Khung một, sáu thành phần: cân bằng tải, cổng API, mạng phân phối nội dung, cơ sở dữ liệu, bộ nhớ đệm, hàng đợi thông điệp; mỗi thành phần có dịch vụ tương ứng ở cả hai trang so sánh của Microsoft. Khung hai, hai bài toán phải tự quyết: giao thức liên lạc và sinh mã định danh duy nhất; hai trang so sánh không có dòng nào nhắc mã định danh duy nhất. Khung ba, năm tính chất: khả năng mở rộng, tính sẵn sàng, hiệu năng, bảo mật, chịu lỗi và phục hồi; so với năm lăng kính của công cụ đánh giá Microsoft thì thiếu chi phí và vận hành.](../../diagrams/sd-11-044-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng; "cổng API" là điểm vào chung của một nhóm dịch vụ.
- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy chủ rải nhiều nơi giữ bản sao nội dung để trả cho người dùng gần nhất.
- **ID** (IDentifier) — mã định danh: một giá trị phân biệt một bản ghi với mọi bản ghi khác.
- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon.

## Đọc hình

**Bài nguồn nêu gì.** Phần chữ của bài nguồn nói đây là một mẫu để xử lý các bài toán thiết kế hệ thống trong phỏng vấn, và danh sách chỉ "chạm sơ" các điểm thảo luận sau: cân bằng tải, cổng API, giao thức liên lạc, mạng phân phối nội dung, cơ sở dữ liệu, bộ nhớ đệm, hàng đợi thông điệp, sinh mã định danh duy nhất, khả năng mở rộng, tính sẵn sàng, hiệu năng, bảo mật, chịu lỗi và phục hồi, "và hơn thế nữa". Phần nội dung chi tiết nằm trong ảnh, mà bài này không đọc.

**Ba loại.**

- **Sáu thành phần** (thứ ghép vào hệ thống): cân bằng tải, cổng API, mạng phân phối nội dung, cơ sở dữ liệu, bộ nhớ đệm, hàng đợi thông điệp.
- **Hai bài toán phải tự quyết:** giao thức liên lạc và sinh mã định danh duy nhất. Không ai bán sẵn câu trả lời; đó là lựa chọn thiết kế.
- **Năm tính chất của cả hệ thống:** khả năng mở rộng, tính sẵn sàng, hiệu năng, bảo mật, chịu lỗi và phục hồi. Không thêm được như một thành phần; chúng là kết quả của cách các thành phần ghép với nhau.

Cách xếp ba loại là của người biên soạn, không phải của nguồn.

## Thử: sáu thành phần có dịch vụ tương ứng không

Ngày 2026-10-19, người biên soạn đọc hai trang so sánh của Microsoft (trang "Azure for AWS professionals" và trang "Google Cloud to Azure services comparison", kho `MicrosoftDocs/architecture-center` tại commit `8e2c239`) và tìm hàng ghép dịch vụ cho từng thành phần:

| Thành phần | AWS với Azure | Google Cloud với Azure |
|---|---|---|
| Cân bằng tải | `Network Load Balancer` với `Load Balancer`; `Application Load Balancer` với `Application Gateway` | `Cloud Load Balancing` với `Azure Front Door`, `Application Gateway`, `Traffic Manager` |
| Cổng API | `Amazon API Gateway` với `Azure API Management` | `Apigee` với `Azure API Management` |
| Mạng phân phối nội dung | `CloudFront` với `Azure Front Door` | `Cloud CDN` với `Azure Content Delivery Network` |
| Cơ sở dữ liệu | `Amazon RDS` với `Azure SQL Database`; `DynamoDB` với `Azure Cosmos DB for NoSQL` | `Cloud Spanner` và `Cloud Firestore` với `Azure Cosmos DB` |
| Bộ nhớ đệm | `Amazon ElastiCache` với `Azure Managed Redis` | `Cloud Memorystore` với `Azure Managed Redis` |
| Hàng đợi thông điệp | `Amazon SQS` với `Azure Queue Storage` hoặc `Azure Service Bus queues` | `Cloud Pub/Sub` với `Azure Service Bus` (và `Event Hubs`, `Event Grid`) |

Cả sáu thành phần đều có hàng ghép ở cả hai trang: 12 trên 12 ô. Còn với hai bài toán phải tự quyết, người biên soạn tìm các chuỗi `unique id`, `uuid`, `snowflake` và `id generat` trong 12 tệp của trang AWS và 1 tệp của trang Google Cloud: 0 dòng nào chứa chúng. Điều này khớp với cách xếp loại: các trang liệt kê sản phẩm, còn sinh mã định danh là một quyết định thiết kế, không phải sản phẩm.

## Thử: năm tính chất so với năm lăng kính của Microsoft

Trang AWS của Microsoft có một hàng ghép `AWS Well-Architected Tool` với `Azure Well-Architected Review`, mô tả là "xem xét khối lượng công việc qua các lăng kính độ tin cậy, bảo mật, quản lý chi phí, xuất sắc vận hành và hiệu quả hiệu năng". Đặt cạnh năm tính chất của bài nguồn:

| Tính chất của danh sách | Lăng kính của Microsoft (theo cách ghép của người biên soạn) |
|---|---|
| Tính sẵn sàng; chịu lỗi và phục hồi | độ tin cậy |
| Hiệu năng | hiệu quả hiệu năng |
| Bảo mật | bảo mật |
| Khả năng mở rộng | không có lăng kính riêng; nằm giữa độ tin cậy và hiệu năng |
| (không có mục nào) | quản lý chi phí |
| (không có mục nào) | xuất sắc vận hành |

Danh sách của nguồn không có mục về chi phí hay vận hành. Nguồn kết bằng "và hơn thế nữa", nên đây không hẳn là thiếu sót; đây là hai câu hỏi mà danh sách thảo luận không tự nhắc, và người phỏng vấn (hay đội thật) có thể hỏi.

## Giới hạn cần nhớ

Cách xếp ba loại và cách ghép tính chất với lăng kính là suy luận của người biên soạn. Bài chỉ đọc một hàng của Microsoft cho phần lăng kính; công cụ đánh giá của AWS có tên và cách chia riêng, không được đọc ở đây. Hàng ghép dịch vụ do Microsoft viết và chỉ ghép dịch vụ gần tương đương, không bảo đảm khớp từng tính năng. Ảnh trong bài nguồn không được đọc, nên bài không bàn tới thứ tự hay mũi tên trong đó.

## Nhìn hình trả lời

Trong buổi thiết kế, bạn đã đi qua hết mười ba mục. Người phỏng vấn hỏi: "Hệ thống này tốn bao nhiêu mỗi tháng, và ai trực khi nó hỏng lúc nửa đêm?" Mục nào của danh sách giúp bạn trả lời?

<details>
<summary>Xem đáp án</summary>

Không mục nào. Hai câu hỏi này thuộc hai lăng kính mà danh sách không có: quản lý chi phí và xuất sắc vận hành. Chịu lỗi và phục hồi nói hệ thống sống sót ra sao, không nói ai phát hiện và xử lý, hay tốn bao nhiêu. Đây là suy luận của người biên soạn từ phép đối chiếu ở trên.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một ảnh và một danh sách mười ba chủ đề cộng "và hơn thế nữa". Bài này không dùng ảnh; xếp danh sách thành ba loại, thử sáu thành phần với các bảng ghép dịch vụ của Microsoft, và đặt năm tính chất cạnh năm lăng kính của công cụ đánh giá Microsoft.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/system-design-blueprint-the-ultimate-guide.md): danh sách mười ba chủ đề. Cách xếp loại và hai phép thử là của người biên soạn.
- [Microsoft — Azure for AWS professionals](https://github.com/MicrosoftDocs/architecture-center/tree/8e2c239344ee753a88856800b4210a3e27ac1036/docs/aws-professional) và [Google Cloud to Azure services comparison](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/gcp-professional/services.md): các bảng ghép dịch vụ và hàng về công cụ đánh giá, tại commit `8e2c239`.

Đã đọc nguồn ngày 2026-10-19. Không đối chiếu với tài liệu của AWS hay Google Cloud (kiến thức chung của người biên soạn, chưa đối chiếu).
Bài viết và hình được thiết kế độc lập.

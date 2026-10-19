# Elasticsearch hợp với việc gì: sáu cách dùng và cái mỗi cách dựa vào

**Elasticsearch là kho tài liệu chuyên tìm và phân tích. Sáu cách dùng quen thuộc của nó đều dựa vào vài tính năng cụ thể; biết tính năng nào gánh việc nào thì biết khi nào nên dùng và phải cấu hình gì.**
Phần thử nghiệm chạy trên Elasticsearch 9.5.5, một nút, giấy phép basic (miễn phí).

![Ba phần. Phần một, tìm và phân tích, ba thẻ: tìm kiếm toàn văn dựa vào bộ phân tích tách chữ thành từ và chỉ mục ngược; phân tích gần thời gian thực dựa vào gộp nhóm trên trường keyword, số, ngày, dữ liệu mới hiện sau lần làm mới; dữ liệu vị trí dựa vào trường geo_point, tìm trong bán kính và kết hợp với tìm chữ. Phần hai, nhật ký và an ninh, ba thẻ: nhật ký và sự kiện dựa vào data stream chỉ ghi thêm, chia chỉ mục theo thời gian, hỏi chung một tên; học máy phát hiện bất thường trên chuỗi thời gian, cần gói trả phí hoặc bản dùng thử; SIEM, một phần của Elastic Security, dựng trên Elasticsearch và Kibana để dò sự cố an ninh. Phần ba, bốn kết quả thử trên Elasticsearch 9.5.5: gõ không dấu ao khoac ra 0 kết quả, cần bộ lọc bỏ dấu; vừa ghi xong, chưa tới lần làm mới, tìm ra 0, sau lần làm mới ra 5; gộp nhóm trên trường văn bản bị từ chối; giấy phép basic không tạo được job phát hiện bất thường.](../../diagrams/sd-06-016-main.svg)

## Từ viết tắt

- **SIEM** (Security Information and Event Management) — quản lý thông tin và sự kiện an ninh: gom nhật ký an ninh từ nhiều nguồn về một chỗ để tìm, phân tích và cảnh báo sự cố.

## Đọc hình

**Tìm kiếm toàn văn.** Trường kiểu `text` đi qua bộ phân tích: tách câu thành từ, đổi về chữ thường. Mỗi từ được ghi vào chỉ mục ngược, tức danh sách "từ này nằm trong những tài liệu nào", nên tìm "áo khoác" không phải đọc lại mọi tài liệu. Kết quả được xếp theo điểm liên quan.

**Phân tích gần thời gian thực.** Gộp nhóm (aggregation) đếm, cộng, lấy trung bình theo trường `keyword`, số hay ngày. "Gần" vì tài liệu mới chỉ tìm thấy sau một lần làm mới (refresh); mặc định Elasticsearch làm mới mỗi giây, nhưng chỉ với chỉ mục có người tìm trong 30 giây qua.

**Dữ liệu vị trí.** Trường `geo_point` giữ cặp vĩ độ, kinh độ; truy vấn `geo_distance` lọc trong một bán kính và kết hợp được với tìm chữ.

**Nhật ký và sự kiện.** Data stream là một tên chung đứng trước nhiều chỉ mục ẩn chia theo thời gian, dành cho dữ liệu chỉ ghi thêm như nhật ký, số đo.

**Học máy và SIEM** là các phần dựng trên Elasticsearch: phát hiện bất thường cần gói đăng ký phù hợp hoặc bản dùng thử; Elastic Security gom SIEM và các tính năng an ninh khác, dùng Elasticsearch để tìm và Kibana để hiển thị.

**Thử nghiệm.** Năm sản phẩm, tên kiểu `text`, danh mục kiểu `keyword`, cửa hàng kiểu `geo_point`.

- Bộ phân tích chuẩn biến "Áo Khoác Gió" thành `áo`, `khoác`, `gió`. Tìm "áo khoác" ra hai áo khoác điểm 1,385 rồi áo thun 0,528 (chỉ khớp "áo"). Tìm "ao khoac" không dấu: 0 kết quả, vì dấu được giữ nguyên; thêm bộ lọc `asciifolding` thì ra `ao`, `khoac`, `gio`.
- Đếm ngay sau khi ghi, lúc chưa tới lần làm mới tự động đầu tiên: 0. Sau `_refresh`: 5. Con số 0 phụ thuộc thời điểm: đếm muộn hơn một chút thì lần làm mới tự động có thể đã chạy.
- Gộp theo danh mục: `ao` 3, `giay` 2. Gộp theo tên (`text`): lỗi "Fielddata is disabled".
- Bán kính 5 km quanh một điểm ở Hà Nội: ba sản phẩm bán ở hai cửa hàng gần đó.
- Ghi một dòng nhật ký vào `logs-checkout-default`: Elasticsearch tự tạo data stream với chỉ mục ẩn `.ds-logs-checkout-default-2026.10.18-000001`; ghi đè theo mã tài liệu thì bị từ chối, data stream chỉ nhận thêm mới.
- Tạo job phát hiện bất thường trên giấy phép basic: "current license is non-compliant for [ml]".

## Giới hạn cần nhớ

Elasticsearch tìm thấy cái nó đã được dạy để tách: chọn sai kiểu trường (tên sản phẩm là `keyword`, danh mục là `text`) thì tìm hoặc gộp nhóm hỏng, và không đổi được kiểu của một trường đã có: phải tạo chỉ mục mới với kiểu đúng rồi chép dữ liệu sang (reindex). Dữ liệu mới không hiện ngay. Số shard chính của một chỉ mục cố định từ lúc tạo. Phát hiện bất thường bằng học máy cần gói đăng ký phù hợp hoặc bản dùng thử; thử nghiệm chỉ cho thấy giấy phép basic từ chối loại job này, không nói gì về các tính năng khác.

## Nhìn hình trả lời

Một cửa hàng muốn khách gõ "giay chay bo" vẫn ra "Giày chạy bộ", và muốn biểu đồ số sản phẩm theo danh mục. Theo hình và phần thử nghiệm, cần cấu hình hai trường thế nào?

<details>
<summary>Xem đáp án</summary>

Tên sản phẩm: kiểu `text` với bộ phân tích có bộ lọc bỏ dấu (`lowercase` rồi `asciifolding`), để "Giày" và "giay" cùng ra một từ. Có thể giữ thêm một trường phụ không bỏ dấu để kết quả gõ đúng dấu được điểm cao hơn.
Danh mục: kiểu `keyword` để gộp nhóm. Nếu một trường cần cả tìm chữ lẫn gộp nhóm, tài liệu Elastic gợi ý dùng hai phiên bản của cùng trường (multi-fields): một `text`, một `keyword`.

</details>

<details>
<summary>Xem sâu hơn: vì sao trường văn bản không gộp nhóm được</summary>

- Chỉ mục ngược trả lời "từ này ở tài liệu nào". Gộp nhóm cần chiều ngược lại: "tài liệu này có giá trị gì". Trường `keyword`, số, ngày lưu thêm dữ liệu theo cột trên đĩa (doc values) cho việc đó; trường `text` thì không, và việc dựng tạm trong bộ nhớ (fielddata) mặc định bị tắt.
- Tài liệu Elastic xếp `text` cho nội dung người đọc (thân email, mô tả sản phẩm) và `keyword` cho nội dung có cấu trúc (email, tên máy, mã trạng thái, thẻ).
- Data stream hợp với dữ liệu chuỗi thời gian; nếu bạn hay ghi lại cùng một mã tài liệu và muốn bản sau thắng, tài liệu khuyên dùng alias với chỉ mục ghi thay cho data stream.
- Bài nguồn nhắc học máy "trong X-Pack"; tài liệu hiện nay gọi đây là tính năng học máy của Elastic Stack, và trang hướng dẫn cài đặt học máy ghi yêu cầu gói đăng ký phù hợp hoặc bản dùng thử. Bài chỉ thử job phát hiện bất thường.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-elasticsearch-use-cases.md): sáu cách dùng.
- Tài liệu Elastic, kho `elastic/docs-content` tại commit cố định: [Near real-time search](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/manage-data/data-store/near-real-time-search.md), [Data streams](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/manage-data/data-store/data-streams.md), [Geospatial analysis](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/explore-analyze/geospatial-analysis.md), [Setting up machine learning](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/explore-analyze/machine-learning/setting-up-machine-learning.md), [Elastic Security](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/get-started/_snippets/security-overview.md), [Clusters, nodes, and shards](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/deploy-manage/distributed-architecture/clusters-nodes-shards.md), [Explicit mapping](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/manage-data/data-store/mapping/explicit-mapping.md).
- Tài liệu tham chiếu trong kho `elastic/elasticsearch` ở thẻ v9.5.5: [kiểu `text`](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/docs/reference/elasticsearch/mapping-reference/text.md), [`doc_values`](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/docs/reference/elasticsearch/mapping-reference/doc-values.md), [bộ lọc `asciifolding`](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/docs/reference/text-analysis/analysis-asciifolding-tokenfilter.md), [truy vấn `geo_distance`](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/docs/reference/query-languages/query-dsl/query-dsl-geo-distance-query.md).

Thử nghiệm chạy ngày 2026-10-18 với ảnh Docker chính thức `elasticsearch:9.5.5` (Lucene 10.5.1), một nút, tắt bảo mật để thử trên máy riêng; dữ liệu là năm sản phẩm tự đặt. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

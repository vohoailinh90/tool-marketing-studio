# Học Elasticsearch theo đường đi của một tài liệu

**Muốn hiểu Elasticsearch, hãy theo một tài liệu (một đối tượng JSON) từ lúc được gửi vào tới lúc tìm thấy được: bộ phân tích biến chữ thành từ, chỉ mục ngược ghi từ nào ở đâu, segment giữ chỉ mục đó trên đĩa, shard chia việc cho nhiều máy.**
Bốn lớp này là của Lucene, thư viện Java mà Elasticsearch dựng lên trên, cộng với lớp phân tán của Elasticsearch. Thử nghiệm chạy trên Elasticsearch 9.5.5 (Lucene 10.5.1).

![Hai phần. Phần một, bốn bước đánh số: 1 bộ phân tích tách và chuẩn hóa chữ, Áo Khoác thành áo và khoác; 2 chỉ mục ngược, mỗi từ trỏ tới tài liệu và vị trí chứa nó; 3 segment, làm mới là ghi segment mới, không sửa segment cũ, rồi gộp dần; 4 shard và bản sao, một shard là một chỉ mục Lucene, bản sao nằm ở nút khác. Phần hai, bốn kết quả thử trên Elasticsearch 9.5.5: ba lần làm mới tạo ba segment, mỗi cái một tài liệu; sửa một tài liệu thì bản cũ bị đánh dấu xóa, bản mới vào segment mới; gộp về một segment thì thấy tệp từ điển thuật ngữ và tệp chỉ mục của nó; một nút với một bản sao thì cụm báo vàng vì bản sao chưa có chỗ.](../../diagrams/sd-06-022-main.svg)

## Từ viết tắt

- **JSON** (JavaScript Object Notation) — định dạng văn bản ghi dữ liệu thành các cặp tên và giá trị; mỗi tài liệu gửi vào Elasticsearch là một đối tượng JSON.
- **LSM** (Log-Structured Merge) — kiểu lưu trữ ghi dữ liệu mới thành các khối không sửa lại, rồi gộp dần các khối ở nền.

## Đọc hình

**1 · Bộ phân tích.** Một bộ phân tích gồm ba phần chạy nối nhau: bộ lọc ký tự (sửa chuỗi gốc), bộ tách từ, và bộ lọc từ (đổi chữ thường, bỏ dấu, bỏ từ dừng...). Tài liệu Elastic khuyên trong đa số trường hợp dùng cùng một bộ phân tích lúc ghi và lúc tìm, để từ trong câu hỏi có cùng dạng với từ trong tài liệu.

**2 · Chỉ mục ngược.** Mỗi từ dẫn tới danh sách tài liệu chứa nó, kèm số lần xuất hiện và vị trí. Tài liệu "Bộ nhớ đệm giữ dữ liệu hay dùng" cho tám từ, `bộ` ở vị trí 0, `nhớ` ở 1, `đệm` ở 2...; vị trí giúp tìm cả cụm từ.

**3 · Segment.** Lucene ghi chỉ mục thành các segment, mỗi segment là một chỉ mục độc lập. Làm mới (refresh) ghi phần đang đệm thành segment mới và mở nó để tìm, không sửa segment cũ. Xóa chỉ là đánh dấu; sửa là đánh dấu xóa bản cũ rồi ghi bản mới. Các segment nhỏ được gộp dần thành segment lớn.

**4 · Shard và bản sao.** Mỗi chỉ mục của Elasticsearch chia thành một hay nhiều shard chính, mỗi shard là một chỉ mục Lucene. Bản sao (replica) là bản chép của shard chính, giúp chịu hỏng máy và đỡ bớt việc tìm; Elasticsearch không bao giờ đặt bản sao cùng nút với shard chính.

**Thử nghiệm.** Một chỉ mục 1 shard, 1 bản sao, tắt làm mới tự động, ghi ba câu ngắn và làm mới sau mỗi câu: `_cat/segments` cho ba segment `_0`, `_1`, `_2`, mỗi cái 1 tài liệu. Sửa tài liệu 1: segment `_0` còn 0 tài liệu, 1 đã xóa, và có thêm `_3`. Gộp về một segment (`_forcemerge`): còn `_4` với 3 tài liệu. Trong thư mục của shard có các tệp `_4_Lucene104_0.tim` (từ điển thuật ngữ), `.tip` (chỉ mục vào từ điển), `.doc` (danh sách tài liệu và tần suất), `.pos` (vị trí). Cụm một nút báo trạng thái `yellow` với 1 shard chưa có chỗ: chính bản sao.

## Giới hạn cần nhớ

Gộp segment tốn đọc ghi đĩa; tài liệu đã xóa chỉ thật sự biến mất khi được gộp, và Elasticsearch còn cố ý giữ lại các lần xóa gần đây (soft deletes) để phát lại cho bản sao. Trong thử nghiệm, ngay sau khi gộp vẫn còn 1 tài liệu đã xóa; tài liệu Elastic cho biết lần xóa gần đây được giữ theo các hợp đồng giữ lịch sử, còn bài không theo dõi tới lúc nó bị bỏ hẳn. Bài nguồn nói từ điển thuật ngữ được dựng bằng cây LSM; chính xác hơn, cách ghi segment mới rồi gộp dần mới giống LSM, còn từ điển trong mỗi segment là một tệp xếp theo thứ tự với một chỉ mục riêng để nhảy tới đúng chỗ.

## Nhìn hình trả lời

Một ứng dụng sửa giá của cùng một sản phẩm hàng trăm lần mỗi phút, và đội vận hành thấy dung lượng chỉ mục tăng dù số sản phẩm không đổi. Theo hình, vì sao?

<details>
<summary>Xem đáp án</summary>

Vì segment không được sửa tại chỗ: mỗi lần sửa là đánh dấu xóa bản cũ và ghi bản mới vào segment mới. Các bản cũ còn chiếm chỗ cho tới khi segment được gộp, và Elasticsearch còn giữ các lần xóa gần đây một thời gian cho bản sao. Hướng xử lý: gom các lần sửa lại trước khi ghi, hoặc tách dữ liệu đổi liên tục (giá, tồn kho) ra khỏi phần mô tả ít đổi.

</details>

<details>
<summary>Xem sâu hơn: lộ trình học sau bốn lớp này</summary>

- **Ánh xạ (mapping):** chọn `text` cho chữ cần tìm, `keyword` cho giá trị để lọc và gộp nhóm; xem bài [Elasticsearch hợp với việc gì](../sd-06-016/lesson.md).
- **Truy vấn:** `match` đi qua bộ phân tích, `term` thì không; nhầm hai cái là nguồn lỗi phổ biến khi mới học.
- **Gần thời gian thực:** tài liệu chỉ tìm thấy sau lần làm mới; mặc định mỗi giây, với chỉ mục có người tìm trong 30 giây qua.
- **Shard:** số shard chính cố định khi tạo chỉ mục, số bản sao đổi được bất cứ lúc nào; một cụm một nút luôn `yellow` nếu chỉ mục có bản sao.
- **Lịch sử thao tác:** tài liệu Elastic giải thích soft deletes và hợp đồng giữ lịch sử (mặc định hết hạn sau 12 giờ) khiến tài liệu đã xóa còn nằm lại.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-learn-elasticsearch.md): Elasticsearch dựa trên Lucene, tính năng, cách dùng, từ điển thuật ngữ và cây LSM.
- Tài liệu Elastic, kho `elastic/docs-content` tại commit cố định: [Anatomy of an analyzer](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/manage-data/data-store/text-analysis/anatomy-of-an-analyzer.md), [Near real-time search](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/manage-data/data-store/near-real-time-search.md), [Clusters, nodes, and shards](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/deploy-manage/distributed-architecture/clusters-nodes-shards.md), [Red or yellow health status](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/troubleshoot/elasticsearch/red-yellow-cluster-status.md), [Index and search analysis](https://github.com/elastic/docs-content/blob/55f05da44f1e68caf6b83d60715f6a41bcdaa2d3/manage-data/data-store/text-analysis/index-search-analysis.md).
- Kho `elastic/elasticsearch` ở thẻ v9.5.5: [History retention](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/docs/reference/elasticsearch/index-settings/history-retention.md) (sửa là xóa rồi ghi mới, soft deletes, hạn 12 giờ), [truy vấn `term`](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/docs/reference/query-languages/query-dsl/query-dsl-term-query.md) (không dùng cho trường `text` vì giá trị đã qua phân tích).
- Lucene 10.5.1: [`codecs/lucene104/package-info.java`](https://github.com/apache/lucene/blob/64ce863a2bea79c69c19c4d56268c26710ff0ff9/lucene/core/src/java/org/apache/lucene/codecs/lucene104/package-info.java) (segment, gộp segment, bảng phần mở rộng tệp) và [`Lucene104PostingsFormat.java`](https://github.com/apache/lucene/blob/64ce863a2bea79c69c19c4d56268c26710ff0ff9/lucene/core/src/java/org/apache/lucene/codecs/lucene104/Lucene104PostingsFormat.java) (tệp `.tim` và `.tip`).

Thử nghiệm chạy ngày 2026-10-18 với ảnh Docker chính thức `elasticsearch:9.5.5`, một nút, tắt tệp gộp (`index.compound_format: false`) để thấy từng tệp của segment. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

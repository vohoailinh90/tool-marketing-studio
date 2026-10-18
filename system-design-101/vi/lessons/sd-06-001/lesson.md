# ELK Stack: thu thập, xử lý, lưu và xem log

**ELK là tên ghép của ba sản phẩm: Logstash làm sạch log, Elasticsearch lưu để tìm, Kibana vẽ ra màn hình. Thêm Beats, bên đọc log ngay ở máy nguồn, là đủ một đường ống cho log; README của Logstash gọi cả bốn là Elastic Stack.**
Beats ra đời sau nên không có trong cái tên ELK. Hiểu mỗi chặng làm gì thì cũng biết chặng nào bỏ được và chặng nào nên thêm.

![Ba khung. Khung một, bốn bước: Beats thu thập log ngay trên máy nguồn; Logstash gom, tách trường và làm sạch; Elasticsearch đánh chỉ mục và lưu; Kibana cho tìm kiếm, vẽ biểu đồ và dashboard. Khung hai, khi lượng log lớn: Beats ghi vào Kafka, Kafka giữ log theo thời hạn hoặc dung lượng, Logstash tự kéo về theo sức của mình. Khung ba, nhớ gì: Beats có thể gửi thẳng tới Elasticsearch; mỗi chặng thêm vào là một hệ thống nữa phải vận hành; tìm được log nhanh không có nghĩa là đã biết vì sao lỗi.](../../diagrams/sd-06-001-main.svg)

## Từ viết tắt

- **ELK** (Elasticsearch, Logstash, Kibana) — tên ghép từ chữ cái đầu của ba sản phẩm chính; Beats được thêm vào sau nhưng tên vẫn giữ ba chữ.

## Đọc hình

**1 · Beats thu thập.** Beats là các chương trình nhỏ cài ngay trên máy sinh ra dữ liệu. Mỗi loại lo một việc: Filebeat đọc dần các tệp log, Packetbeat bắt gói tin mạng, Winlogbeat lấy nhật ký sự kiện của Windows. Kho mã của Beats mô tả chúng là bộ gửi dữ liệu "nhẹ": cài gọn, ít tốn tài nguyên.

**2 · Logstash xử lý.** Logstash nhận dữ liệu từ nhiều nguồn cùng lúc, biến đổi nó (ví dụ tách một dòng log thành các trường như thời gian, mức lỗi, đường dẫn) rồi gửi đi. Nơi nhận thường là Elasticsearch, nhưng không bắt buộc.

**3 · Elasticsearch lưu và đánh chỉ mục.** Elasticsearch là bộ máy tìm kiếm và phân tích chạy phân tán trên nhiều máy, xây trên thư viện tìm kiếm Apache Lucene. Log được đánh chỉ mục để tìm theo chữ ("timeout") và lọc theo trường (chỉ lấy các dòng có mức lỗi là error).

**4 · Kibana hiển thị.** Kibana là giao diện để truy vấn, phân tích và vẽ biểu đồ trên dữ liệu đã nằm trong Elasticsearch. Đây là chỗ người trực sự cố nhìn vào.

**Khi log đổ về quá nhiều.** Filebeat gửi được tới Elasticsearch, Logstash, Kafka, Redis hoặc một tệp. Đặt Kafka ở giữa thì Beats chỉ việc ghi vào Kafka, còn Logstash tự *kéo* log về theo sức của nó. Tài liệu thiết kế của Kafka giải thích lợi ích của mô hình kéo: bên đọc chậm hơn bên ghi thì chỉ tụt lại phía sau rồi đuổi kịp, không bị dồn tới ngợp. Kafka giữ log theo thời hạn hoặc dung lượng đã cấu hình, nên khi Logstash chậm hay dừng một lúc, log vẫn nằm chờ trong Kafka, miễn là nó quay lại trước khi hết hạn giữ.
Việc giữ không phụ thuộc vào việc đã có ai đọc: tài liệu thiết kế của Kafka ghi rằng bản ghi không bị xóa ngay khi được đọc, và bên đọc có thể lùi về một vị trí cũ để đọc lại. Chỗ dễ hở là phần Logstash *đã lấy về* nhưng chưa gửi xong. Theo mặc định, Logstash định kỳ báo cho Kafka vị trí đã đọc (offset) của các bản ghi vừa lấy về, còn bản ghi đang xử lý thì nằm trong một hàng đợi trong bộ nhớ, và tài liệu của Logstash ghi rằng hàng đợi đó mất sạch khi Logstash bị tắt đột ngột. Khi chạy lại, Logstash đọc tiếp từ vị trí đã báo nên bỏ qua các bản ghi ấy: chúng vẫn còn trong Kafka cho tới khi hết hạn giữ, nhưng không tự được gửi lại, muốn lấy lại phải lùi vị trí đọc bằng tay. Muốn Logstash sập mà ít bỏ sót log hơn, phải bật hàng đợi lưu xuống đĩa (`queue.type: persisted`, mặc định tắt); ngay cả khi đó, tài liệu vẫn nói có thể mất phần chưa kịp ghi điểm lưu (checkpoint) nếu tắt đột ngột.

## Giới hạn cần nhớ

Logstash không bắt buộc: Beats có thể gửi thẳng tới Elasticsearch. Mỗi chặng thêm vào (Logstash, Kafka) là một hệ thống nữa phải cài, theo dõi và nâng cấp, nên chỉ thêm khi cần đúng việc nó làm: biến đổi nặng, gom từ nhiều nguồn, hay đệm khi phía sau chậm.
Và tìm được dòng log nhanh mới là bước đầu: log chỉ giúp được nếu ứng dụng ghi đủ thông tin để lần ra nguyên nhân.

## Nhìn hình trả lời

Bạn có ba máy chủ web, mỗi máy ghi log ra tệp, và chỉ cần tìm lỗi theo chữ. Đường ống tối thiểu là gì? Khi nào bạn mới cần thêm Kafka?

<details>
<summary>Xem đáp án</summary>

Tối thiểu: Filebeat trên từng máy gửi thẳng tới Elasticsearch, xem bằng Kibana; chưa cần Logstash nếu không phải biến đổi gì nhiều.
Thêm Kafka khi phía sau có lúc không theo kịp lượng log (đợt cao điểm, Logstash hay Elasticsearch bảo trì) mà bạn không muốn mất log trong lúc đó: Kafka giữ log theo hạn đã đặt để bên đọc đuổi kịp sau. Nếu cả lúc Logstash sập cũng phải hạn chế bỏ sót log, bật thêm hàng đợi lưu xuống đĩa của Logstash.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn vẽ một đường cố định Beats → Logstash → Elasticsearch → Kibana. Bài này thêm hai điều từ tài liệu của chính các dự án: Beats gửi được thẳng tới Elasticsearch (Logstash là tùy chọn), và lý do Kafka giúp được là mô hình kéo cùng thời hạn giữ log.
Bài nguồn còn nói ELK phổ biến vì "giá hợp lý"; bài này không nhắc giá vì không có nguồn để đối chiếu, và cũng không bàn giấy phép của các sản phẩm.
Bài không chạy thử ELK; mọi mô tả về các thành phần lấy từ README của từng kho mã ở các commit ghi dưới đây.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-elk-stack-and-why-is-it-so-popular-for-log-management.md): bốn bước của đường ống ELK.
- [Elastic — README của Beats, tại commit cố định](https://github.com/elastic/beats/blob/02d90c89c682160e7a336f121e0a54be480f438c/README.md): Beats là bộ gửi dữ liệu nhẹ, gửi tới Elasticsearch trực tiếp hoặc qua Logstash; bảng các Beat (Filebeat, Packetbeat, Winlogbeat…).
- [Elastic — README của Filebeat, tại commit cố định](https://github.com/elastic/beats/blob/02d90c89c682160e7a336f121e0a54be480f438c/filebeat/README.md): các đích Filebeat gửi tới, gồm Elasticsearch, Logstash, Kafka, Redis và tệp.
- [Elastic — README của Logstash, tại commit cố định](https://github.com/elastic/logstash/blob/39a297ed817a6618cc1144a8307f6622a7f369c9/README.md): đường ống xử lý phía máy chủ, nhận từ nhiều nguồn, biến đổi rồi gửi đi.
- [Elastic — README của Elasticsearch, tại commit cố định](https://github.com/elastic/elasticsearch/blob/9df53afd7c6054b65e753349ef347cf3e7ba11d1/README.asciidoc): bộ máy tìm kiếm và phân tích phân tán, dùng cho log; [tệp phiên bản phụ thuộc](https://github.com/elastic/elasticsearch/blob/9df53afd7c6054b65e753349ef347cf3e7ba11d1/build-tools-internal/version.properties) ghi Lucene.
- [Elastic — README của Kibana, tại commit cố định](https://github.com/elastic/kibana/blob/7c296350df94ecd3bd5493ce82a2a6295281f256/README.md): giao diện truy vấn, phân tích và vẽ dữ liệu trong Elasticsearch.
- [Apache Kafka — tài liệu thiết kế, tại commit cố định](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/design/design.md): mô hình kéo cho bên đọc tụt lại rồi đuổi kịp; giữ log theo thời gian hoặc dung lượng, không xóa ngay khi được đọc; bên đọc có thể lùi vị trí để đọc lại.
- [Elastic — tài liệu hàng đợi trong bộ nhớ của Logstash, tại commit cố định](https://github.com/elastic/logstash/blob/39a297ed817a6618cc1144a8307f6622a7f369c9/docs/reference/memory-queue.md): mặc định dùng hàng đợi trong bộ nhớ, mất nội dung khi bị tắt đột ngột.
- [Elastic — tài liệu hàng đợi lưu xuống đĩa của Logstash, tại commit cố định](https://github.com/elastic/logstash/blob/39a297ed817a6618cc1144a8307f6622a7f369c9/docs/reference/persistent-queues.md): `queue.type: persisted`, mặc định tắt; vẫn có thể mất dữ liệu nếu tắt đột ngột trước khi ghi điểm lưu.
- [Logstash — tài liệu đầu vào Kafka, tại commit cố định](https://github.com/logstash-plugins/logstash-integration-kafka/blob/45f52efc8714ba5db57832b40e1f178274166e80/docs/input-kafka.asciidoc): `enable_auto_commit` mặc định bật, định kỳ báo vị trí của các bản ghi đã lấy về; vị trí đã báo là chỗ đọc tiếp khi tiến trình hỏng.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho. Bài viết và hình được thiết kế độc lập.

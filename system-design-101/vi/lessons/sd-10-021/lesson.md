# Thuật toán nên biết cho phỏng vấn thiết kế hệ thống: ba mức sao

**Tác giả nguồn xếp thuật toán theo ba mức sao và nhấn mạnh rằng hiểu thuật toán được dùng thế nào trong hệ thống thật thường quan trọng hơn chi tiết cài đặt; bài giữ thang sao đó và minh họa luận điểm bằng ba thuật toán lấy từ tài liệu của hệ thống thật.**
Danh sách thuật toán của nguồn nằm trong ảnh mà bài không dùng, nên bài không gán sao cho thuật toán nào; ba ví dụ do bài tự chọn.

![Hai nhóm thẻ và một khung ghi nhớ. Ba mức sao: năm sao là rất quan trọng, cố hiểu nó chạy thế nào và vì sao; ba sao là quan trọng ở mức nào đó, có thể không cần chi tiết cài đặt; một sao là nâng cao, nên biết với ứng viên cấp cao. Ba ví dụ dùng thật: bộ lọc Bloom giúp Cassandra bỏ qua tệp dữ liệu chắc chắn không chứa khóa; băm nhất quán trên vòng token giúp Cassandra chuyển ít khóa khi đổi số nút; giao thức Raft giúp một cụm nút giữ chung một nhật ký nhân bản trong thư viện etcd-io/raft. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-021-main.svg)

## Đọc hình

**Thang sao.** Theo nguồn, năm sao dành cho thuật toán rất quan trọng, nên cố hiểu nó chạy thế nào và vì sao. Ba sao là quan trọng ở mức nào đó, và có thể không cần nắm chi tiết cài đặt. Một sao là nâng cao, tốt nếu biết khi ứng tuyển vị trí cấp cao (senior). Chính tác giả thừa nhận rất khó xếp hạng thuật toán một cách khách quan, nên thang này là ý kiến của một người, không phải chuẩn chung.

**Điều đáng nhớ nhất.** Nguồn nói trong buổi phỏng vấn thiết kế hệ thống, hiểu thuật toán được dùng thế nào trong hệ thống thật nhìn chung quan trọng hơn chi tiết cài đặt. Ba ví dụ dưới đây cho thấy "dùng thế nào" trông ra sao khi đọc tài liệu của một hệ thống.

**Ví dụ 1: bộ lọc Bloom trong đường đọc của Cassandra.** Tài liệu của Cassandra nói khi đọc, hệ thống gộp dữ liệu trong các tệp trên đĩa với dữ liệu trong bộ nhớ. Để khỏi phải kiểm tra từng tệp dữ liệu cho phân vùng đang được hỏi, nó dùng bộ lọc Bloom, cấu trúc xác suất cho một trong hai kết luận: dữ liệu chắc chắn không có trong tệp, hoặc có lẽ có. Tài liệu cũng nói bộ lọc có thể chính xác hơn nếu cho nó dùng nhiều bộ nhớ hơn, và người vận hành chỉnh điều này theo từng bảng bằng tham số `bloom_filter_fp_chance`. Cùng cấu trúc đó được giải thích kỹ ở bài về bộ lọc Bloom.

**Ví dụ 2: băm nhất quán trên vòng token.** Tài liệu Cassandra so sánh hai cách chia khóa cho các nút. Cách ngây thơ lấy băm của khóa chia lấy dư cho số nút, nhưng thêm một nút có thể làm hầu hết các ánh xạ mất hiệu lực. Cassandra thay vào đó ánh xạ mỗi nút tới một hoặc vài token trên một vòng băm liên tục, băm khóa lên vòng rồi "đi" theo một chiều để tìm nút sở hữu. Khi số nút đổi, băm nhất quán chỉ phải chuyển một phần nhỏ các khóa.

**Ví dụ 3: Raft trong thư viện etcd-io/raft.** Tài liệu của thư viện mô tả Raft là giao thức để một cụm nút duy trì một máy trạng thái được nhân bản, giữ đồng bộ bằng một nhật ký nhân bản. Thư viện cài các phần như bầu người dẫn đầu (leader election) và nhân bản nhật ký (log replication), và ghi rõ nó chỉ cài thuật toán Raft, còn việc truyền tin qua mạng và ghi đĩa để người dùng tự làm.

## Giới hạn cần nhớ

Phần chữ của nguồn không nêu tên thuật toán nào và không cho biết thuật toán nào được mấy sao; danh sách chỉ có trong ảnh nguồn, mà bài không dùng. Vì thế bài không dạy một thuật toán nào và không nên bị đọc như một danh sách cần học. Ba ví dụ là lựa chọn của bài, không gán sao, và không có nghĩa nguồn xếp chúng ở mức nào.
Thang sao không được đối chiếu với yêu cầu thật của buổi phỏng vấn nào, và nguồn không giải thích "cấp cao" nghĩa là bao nhiêu năm kinh nghiệm. Các tài liệu của Cassandra và etcd-io/raft là bản đã ghim ở mục nguồn; bài không nói hệ thống ấy hiện làm gì.

## Nhìn hình trả lời

Cassandra đọc dữ liệu từ nhiều tệp trên đĩa. Thuật toán nào giúp nó khỏi mở tệp chắc chắn không chứa khóa cần tìm, và nó có thể trả lời sai theo chiều nào? Còn khi thêm một nút vào cụm, vì sao băm nhất quán tốt hơn việc chia lấy dư?

<details>
<summary>Xem đáp án</summary>

Bộ lọc Bloom. Nó chỉ trả lời "chắc chắn không có" hoặc "có lẽ có", nên chỉ có thể báo nhầm là có, và khi đó Cassandra mở tệp rồi mới thấy không có; nó không báo nhầm là không có.
Chia lấy dư có thể làm hầu hết ánh xạ khóa sang nút mất hiệu lực khi thêm một nút; băm nhất quán chỉ phải chuyển một phần nhỏ các khóa.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh (danh sách thuật toán cùng số sao) và vài đoạn chữ: lời dẫn, lời khuyên và định nghĩa ba mức sao. Bài này giữ thang sao và lời khuyên vì đó là nội dung của nguồn, rồi thêm ba ví dụ do bài tự viết từ tài liệu của Cassandra và thư viện etcd-io/raft để minh họa lời khuyên; ba ví dụ không có trong bài nguồn. Bài không dùng ảnh nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/algorithms-you-should-know-before-taking-system-design-interviews.md): lời khuyên và thang sao; danh sách thuật toán chỉ có trong ảnh.
- [Apache Cassandra — Bloom Filters](https://github.com/apache/cassandra/blob/95b178a141824a0414c4add9b5ab87eaa1ca13bf/doc/modules/cassandra/pages/managing/operating/bloom_filters.adoc) và [Dynamo (băm nhất quán)](https://github.com/apache/cassandra/blob/95b178a141824a0414c4add9b5ab87eaa1ca13bf/doc/modules/cassandra/pages/architecture/dynamo.adoc): bộ lọc Bloom trong đường đọc; vòng token và băm nhất quán. Đọc từ kho mã.
- [etcd-io/raft — README](https://github.com/etcd-io/raft/blob/1d3216d845a72ef5a78c55772ea220a931e2c3ef/README.md): Raft, máy trạng thái nhân bản, nhật ký nhân bản. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Bài không có từ viết tắt cần giải thích.
Bài viết và hình được thiết kế độc lập.

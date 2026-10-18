# Các tầng bộ nhớ đệm, từ trình duyệt tới cơ sở dữ liệu

**Dữ liệu được giữ bản sao ở rất nhiều tầng, từ trình duyệt của người dùng tới bên trong cơ sở dữ liệu. Mỗi tầng làm một việc nhanh hơn bằng cách trả lời từ bản sao, và tầng nào cũng đặt ra cùng một câu hỏi: bản sao này được phép cũ bao lâu?**

![Ba khung. Phía người dùng: trình duyệt giữ câu trả lời riêng cho một người; CDN giữ bản sao dùng chung ở gần người dùng; proxy ngược có thể trả lời thay máy chủ. Phía máy chủ: dịch vụ giữ dữ liệu trong bộ nhớ của chính nó; Redis là bộ đệm dùng chung giữa nhiều dịch vụ; Kafka giữ nhật ký theo thời hạn để người đọc chậm đuổi kịp; chỉ mục tìm kiếm là bản sao sắp xếp lại để tìm theo chữ. Bên trong cơ sở dữ liệu: vùng đệm giữ các trang vừa đọc, lần đầu đọc ngoài, lần sau trúng vùng đệm; materialized view lưu sẵn kết quả và chỉ đúng tới lần làm mới gần nhất. Câu hỏi cho mọi tầng: bản sao được phép cũ bao lâu?](../../diagrams/sd-06-006-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt ở nhiều nơi, lưu bản sao nội dung và phát cho người dùng từ máy gần họ.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời, kèm các header như `Cache-Control`.
- **RFC** (Request for Comments) — loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; RFC 9111 là tiêu chuẩn về bộ nhớ đệm của HTTP.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ cơ sở dữ liệu dùng nó.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng cỡ một triệu byte.
- **OS** (Operating System) — hệ điều hành: phần mềm nền quản lý máy; ở đây là phần giữ dữ liệu tệp vừa đọc trong bộ nhớ (page cache).

## Đọc hình

**Phía người dùng.** RFC 9111 chia bộ nhớ đệm HTTP làm hai loại: *riêng*, phục vụ một người, thường nằm trong trình duyệt; và *dùng chung*, phục vụ nhiều người, thường nằm ở một máy trung gian như CDN hay proxy ngược (bài [sd-06-002](../sd-06-002/lesson.md) thử một proxy ngược làm việc này). Cả hai làm theo lời dặn `Cache-Control` của máy chủ.

**Phía máy chủ.** Dịch vụ có thể giữ dữ liệu ngay trong bộ nhớ của tiến trình: nhanh nhất, nhưng mỗi máy chạy dịch vụ giữ một bản riêng, nên các bản có thể lệch nhau. Một bộ đệm dùng chung như Redis cho mọi máy cùng thấy một bản. Kafka thì khác: theo tài liệu thiết kế của nó, Kafka giữ nhật ký theo thời hạn hoặc dung lượng và để người đọc tự kéo dữ liệu về, nên người đọc chậm tụt lại rồi đuổi kịp; bản thân Kafka dựa vào bộ nhớ đệm tệp của hệ điều hành (OS) thay vì tự giữ một bộ đệm riêng trong bộ nhớ. Chỉ mục tìm kiếm như Elasticsearch là một bản sao của dữ liệu được sắp xếp lại để tìm theo chữ.

**Bên trong cơ sở dữ liệu.** PostgreSQL có vùng đệm dùng chung (`shared_buffers`, mặc định thường là 128 MB theo tài liệu) giữ các trang dữ liệu vừa đọc. Materialized view lưu sẵn kết quả của một truy vấn; tài liệu PostgreSQL ghi nó đọc nhanh hơn nhiều nhưng dữ liệu "không phải lúc nào cũng mới", và được làm mới bằng `REFRESH MATERIALIZED VIEW`.

## Thử với PostgreSQL

Ngày 2026-10-18, bài chạy PostgreSQL 16.15 trên một máy, với bảng `orders` 200.000 dòng.

**Vùng đệm.** Khởi động lại máy chủ rồi chạy cùng một truy vấn hai lần với `EXPLAIN (ANALYZE, BUFFERS)`. Lần đầu: `shared read=1082`, tức 1.082 trang phải lấy từ ngoài vùng đệm (từ bộ nhớ đệm của hệ điều hành hoặc từ đĩa). Lần hai: `shared hit=1082`, cả 1.082 trang đã nằm sẵn trong vùng đệm.

**Materialized view.** Tạo view `totals` tổng hợp số đơn và tổng tiền theo khách. Khách `c7` có 2.000 đơn, tổng 14.000. Thêm một đơn 1.000 cho `c7`: bảng gốc cho 2.001 đơn, tổng 15.000, nhưng `totals` vẫn trả 2.000 và 14.000. Sau `REFRESH MATERIALIZED VIEW totals` thì view mới trả 2.001 và 15.000. Đổi lại, đọc từ view mất khoảng 0,2 ms so với khoảng 16 ms khi tính từ bảng gốc.

## Giới hạn cần nhớ

Thêm một tầng đệm là thêm một bản sao có thể cũ, và thêm một chỗ phải trả lời câu hỏi "làm sao xóa hay làm mới nó". Khi dữ liệu thay đổi, mỗi tầng chỉ đúng tới lúc nó được làm mới: hết hạn `max-age` ở trình duyệt, xóa khóa ở Redis, `REFRESH` ở materialized view. Đừng thêm tầng nếu không biết tầng đó cũ tối đa bao lâu.

## Nhìn hình trả lời

Bảng điều khiển doanh số đọc từ một materialized view được làm mới mỗi đêm. Sáng nay một đơn lớn được nhập lúc 9 giờ. Lúc 10 giờ, bảng điều khiển có thấy đơn đó không? Có cách nào biết view đang cũ tới đâu không?

<details>
<summary>Xem đáp án</summary>

Không thấy: view chỉ đúng tới lần `REFRESH` đêm qua, giống thử nghiệm ở trên, nơi view vẫn trả số cũ sau khi bảng gốc đã có đơn mới.
Cách đơn giản là ghi lại thời điểm làm mới (ví dụ trong một bảng nhỏ, cập nhật cùng lúc với `REFRESH`) và hiện nó trên bảng điều khiển, để người xem biết số liệu tính đến lúc nào.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn liệt kê tám tầng có bộ nhớ đệm. Bài này gom chúng theo vị trí, thêm câu hỏi chung "được cũ bao lâu", và thử hai cơ chế của cơ sở dữ liệu trên PostgreSQL.
Bài nguồn nói Kafka "lưu tin nhắn trên đĩa như một bộ nhớ đệm"; tài liệu thiết kế của Kafka cho thấy rõ hơn: Kafka ghi nhật ký ra tệp và dựa vào bộ nhớ đệm tệp của hệ điều hành, còn thời hạn giữ là để người đọc chậm vẫn đọc được.
Bài không thử bộ cân bằng tải hay Elasticsearch; các số đo là của một máy, một bảng thử nhỏ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cache-systems-every-developer-should-know.md): tám tầng có bộ nhớ đệm.
- [IETF HTTP Working Group — RFC 9111, bản XML tại commit cố định](https://github.com/httpwg/httpwg.github.io/blob/03f35d852e7b64668ab08fda1a8076d6d44d17ae/specs/rfc9111.xml): bộ nhớ đệm riêng và dùng chung (mục 1).
- [Apache Kafka — tài liệu thiết kế, tại commit cố định](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/design/design.md): dựa vào bộ nhớ đệm tệp của hệ điều hành; người đọc tự kéo dữ liệu; giữ nhật ký theo thời gian hoặc dung lượng.
- [PostgreSQL — tài liệu cấu hình, tại commit cố định](https://github.com/postgres/postgres/blob/45fc51fcbf4534ea2f6f85e36f8155dbd5ba9851/doc/src/sgml/config.sgml): tham số `shared_buffers`, mặc định thường là 128 MB.
- [PostgreSQL — chương về materialized view, tại commit cố định](https://github.com/postgres/postgres/blob/45fc51fcbf4534ea2f6f85e36f8155dbd5ba9851/doc/src/sgml/rules.sgml): kết quả lưu sẵn, không phải lúc nào cũng mới, làm mới bằng `REFRESH MATERIALIZED VIEW`.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày với PostgreSQL 16.15. Bài viết và hình được thiết kế độc lập.

# Thu thay đổi dữ liệu (CDC): đọc nhật ký thay vì hỏi bảng

**Muốn kho phân tích, cache hay chỉ mục tìm kiếm theo kịp một bảng đang đổi liên tục, cách dễ nghĩ là cứ vài phút hỏi bảng "có gì mới".**
Thu thay đổi dữ liệu dựa trên nhật ký đi đường khác: đọc chính nhật ký mà cơ sở dữ liệu đã ghi cho mọi thay đổi, nên thấy cả những thứ một câu truy vấn không thấy, như một dòng đã bị xóa.

![Ba khung. Khung một là bốn bước của một thay đổi: ứng dụng sửa bảng customers như bình thường; PostgreSQL ghi thay đổi vào nhật ký WAL; công cụ CDC đọc WAL qua một replication slot và giải mã thành sự kiện thêm, sửa, xóa; sự kiện được đẩy sang Kafka rồi tới kho phân tích hay cache. Khung hai so hai cách lấy thay đổi: thăm dò cột updated_at thấy dòng 1 bị sửa và dòng 3 mới thêm nhưng không thấy dòng 2 đã bị xóa; đọc WAL qua slot thấy đủ sửa dòng 1, xóa dòng 2, thêm dòng 3 theo thứ tự commit. Khung ba: slot không ai đọc giữ lại WAL, 61 MB sau một triệu dòng thêm; đọc xong và checkpoint thì chỉ còn 6.712 byte; muốn có giá trị cũ khi sửa thì đặt replica identity full cho bảng.](../../diagrams/sd-04-015-main.svg)

## Từ viết tắt

- **CDC** (Change Data Capture) — thu thay đổi dữ liệu: bắt mọi lần thêm, sửa, xóa trong một cơ sở dữ liệu và chuyển chúng thành sự kiện cho hệ thống khác dùng.
- **WAL** (Write-Ahead Log) — nhật ký ghi trước: PostgreSQL ghi mọi thay đổi vào đây trước khi sửa dữ liệu; công cụ CDC đọc chính nhật ký này.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc của cơ sở dữ liệu quan hệ; nằm trong tên PostgreSQL và MySQL.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng cỡ một triệu byte; ở đây là lượng WAL bị giữ lại.

## Đọc hình

**Khung 1 · Bốn bước.** Ứng dụng sửa bảng như mọi khi, không cần thêm cột hay đổi mã. PostgreSQL ghi thay đổi vào WAL. Logical decoding của PostgreSQL giải mã WAL thành các thay đổi theo từng hàng, đọc qua một *replication slot*. Debezium, công cụ CDC phổ biến, là một connector của Kafka Connect làm đúng việc này: lần đầu nó chụp một ảnh nhất quán của dữ liệu đang có, sau đó đọc tiếp các thay đổi qua slot (dùng plugin `pgoutput` có sẵn từ PostgreSQL 10) và đẩy chúng vào Kafka.

**Khung 2 · Thăm dò hay đọc nhật ký.** Bảng `customers` có hai dòng; sau đó sửa dòng 1, xóa dòng 2, thêm dòng 3.
Câu truy vấn `where updated_at > <lúc bắt đầu>` trả về dòng 1 và dòng 3: dòng 2 đã biến mất khỏi bảng nên không truy vấn nào thấy nó nữa. Slot trả về đủ ba thay đổi, mỗi thay đổi trong giao dịch của nó:

```text
table public.customers: UPDATE: id[integer]:1 email[text]:'an@new' ...
table public.customers: DELETE: id[integer]:2
table public.customers: INSERT: id[integer]:3 email[text]:'chi@new' ...
```

Tài liệu Debezium nêu đúng những điểm này làm lợi thế của CDC dựa trên nhật ký: bắt được mọi thay đổi kể cả xóa, không cần cột kiểu "cập nhật lần cuối", không phải hỏi liên tục.

**Khung 3 · Giá trị cũ.** Mặc định, sự kiện sửa chỉ mang giá trị mới (và khóa). Sau `ALTER TABLE customers REPLICA IDENTITY FULL`, lần sửa kế tiếp mang cả `old-key` với giá trị cũ của mọi cột lẫn `new-tuple`; tài liệu Debezium nói cũng phải làm vậy nếu muốn sự kiện sửa chứa giá trị trước khi sửa.

## Giới hạn cần nhớ

Slot giữ lại mọi đoạn WAL mà người đọc chưa nhận, kể cả khi người đọc đang tắt. Trong thử nghiệm, sau một triệu dòng thêm mà không ai đọc slot, PostgreSQL giữ 61 MB WAL cho nó; đọc hết và chạy checkpoint thì còn 6.712 byte.
Tài liệu PostgreSQL cảnh báo slot không biết gì về người đọc và vẫn ngăn dọn WAL lẫn dữ liệu danh mục hệ thống khi không có ai kết nối; trường hợp xấu có thể làm cơ sở dữ liệu tự dừng. Slot không dùng nữa phải được xóa, và slot đang dùng phải được giám sát.

## Nhìn hình trả lời

Đội dữ liệu đồng bộ bảng `orders` sang kho phân tích bằng câu `where updated_at > lần_trước` chạy mỗi 5 phút. Báo cáo cho thấy kho phân tích có nhiều đơn hơn bảng gốc. Vì sao, và CDC dựa trên nhật ký sửa được gì?

<details>
<summary>Xem đáp án</summary>

Đơn bị xóa ở bảng gốc không bao giờ khớp câu truy vấn, nên kho phân tích giữ chúng mãi (khung 2). Cách thăm dò còn có thể bỏ sót thay đổi nếu ứng dụng nào đó quên cập nhật `updated_at`.
CDC đọc WAL nên nhận được cả sự kiện xóa và mọi lần sửa, không phụ thuộc vào cột thời gian. Đổi lại, phải giám sát replication slot để WAL không đầy đĩa khi bên đọc dừng.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn mở đầu bằng con số "90% dữ liệu thế giới được tạo trong hai năm qua" không kèm nguồn; bài này không dùng nó. Bài nguồn cũng nói người dùng "chỉ cần lo bước 1, các bước khác trong suốt"; thử nghiệm cho thấy còn một việc người vận hành phải lo: replication slot giữ WAL khi bên đọc dừng.
Thử nghiệm dùng plugin `test_decoding` vì nó in thay đổi thành chữ dễ đọc; Debezium dùng `pgoutput` và gói sự kiện theo định dạng riêng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/change-data-capture-key-to-leverage-real-time-data.md): năm bước của CDC, Debezium với Kafka Connect.
- [Debezium — Features, tại commit cố định](https://github.com/debezium/debezium/blob/a058ebb7e267b4010ee0f37c68f3f9f0c01c31af/documentation/modules/ROOT/pages/features.adoc): lợi thế của CDC dựa trên nhật ký so với thăm dò. Đọc từ bản clone của kho.
- [Debezium — PostgreSQL connector, tại commit cố định](https://github.com/debezium/debezium/blob/a058ebb7e267b4010ee0f37c68f3f9f0c01c31af/documentation/modules/ROOT/pages/connectors/postgresql.adoc): ảnh chụp nhất quán ban đầu, `pgoutput`, replication slot giữ WAL khi connector dừng, `REPLICA IDENTITY FULL`.
- [PostgreSQL 16 — Logical Decoding, tại commit cố định](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/logicaldecoding.sgml): replication slot ngăn dọn WAL và dữ liệu danh mục khi không ai kết nối; slot không cần nữa thì xóa. Đọc từ bản clone, nhánh `REL_16_STABLE`.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên PostgreSQL 16.15 (`wal_level = logical`, plugin `test_decoding`); không chạy Debezium.
Bài viết và hình được thiết kế độc lập.

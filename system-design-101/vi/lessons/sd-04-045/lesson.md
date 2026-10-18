# Kafka dùng vào việc gì? Đối chiếu năm việc với danh sách của Kafka, và thử bắt thay đổi dữ liệu

**Các việc người ta giao cho Kafka có chung một điểm: một chuỗi sự kiện có thứ tự, được giữ lại, để nhiều bên đọc theo nhịp riêng của mình.** Nguồn nói Kafka sinh ra để xử lý nhật ký khối lượng lớn, giữ tin tới khi hết hạn và để người đọc tự kéo tin về, rồi kể năm việc hay dùng: xử lý nhật ký, luồng dữ liệu cho gợi ý, theo dõi và cảnh báo, bắt thay đổi dữ liệu (CDC), chuyển hệ thống. Bài này đặt năm việc đó cạnh trang "Use cases" của chính Kafka, rồi thử việc khó hình dung nhất, CDC, bằng PostgreSQL.

![Ba khung dọc. Khung một, năm việc của nguồn đặt cạnh danh sách việc của chính Kafka: xử lý nhật ký ứng với gom nhật ký; luồng dữ liệu cho gợi ý ứng với xử lý luồng; theo dõi và cảnh báo ứng với số đo vận hành; bắt thay đổi dữ liệu và chuyển hệ thống không có trong danh sách của Kafka. Khung hai, thử bắt thay đổi dữ liệu bằng PostgreSQL: mỗi lần thêm, sửa, xóa đã chốt thành một bản ghi theo đúng thứ tự, gói theo giao dịch; xem trước không lấy đi, lấy đi rồi thì không còn. Khung ba, người đọc không đọc thì nhật ký phải chờ: thêm 200.000 dòng mà chưa đọc, PostgreSQL giữ 26 MB nhật ký cho người đọc đó; đọc xong thì không còn giữ gì.](../../diagrams/sd-04-045-main.svg)

## Từ viết tắt

- **CDC** (Change Data Capture) — bắt thay đổi dữ liệu: đọc mọi lần thêm, sửa, xóa đã chốt của một cơ sở dữ liệu thành một luồng sự kiện có thứ tự, để hệ khác chép theo.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ dùng nó.
- **WAL** (Write-Ahead Log) — nhật ký ghi trước: PostgreSQL ghi mọi thay đổi vào đây trước; CDC của PostgreSQL đọc chính nhật ký này.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng; PostgreSQL in kích thước theo bội của 1.024.

## Đọc hình

1. **Năm việc, đặt cạnh danh sách của Kafka.** Trang "Use cases" trong tài liệu Kafka kể bảy việc: nhắn tin, theo dõi hoạt động trên trang web (việc đầu tiên Kafka được làm ra để làm), số đo vận hành, gom nhật ký, xử lý luồng, event sourcing và nhật ký chốt cho hệ phân tán. Ba việc của nguồn khớp: xử lý nhật ký là gom nhật ký; luồng cho gợi ý là xử lý luồng (chính tài liệu Kafka lấy ví dụ một đường ống gợi ý bài báo); theo dõi và cảnh báo là số đo vận hành. Hai việc còn lại, CDC và chuyển hệ thống, không có trong danh sách đó: chúng là cách dùng nhật ký của Kafka để chép dữ liệu từ hệ này sang hệ khác.
2. **Thử CDC trên PostgreSQL.** Phép thử chạy ngày 2026-10-18 trên PostgreSQL 16.15 với `wal_level = logical` và bộ giải mã mẫu `test_decoding` có sẵn trong bản cài; mã ở phần "Xem sâu hơn". Một khe đọc (replication slot) đóng vai người đọc. Thêm đơn 1; trong một giao dịch sửa đơn 1 và thêm đơn 2; rồi xóa đơn 2. Khe đọc trả 10 dòng: ba cặp `BEGIN`/`COMMIT` bao quanh đúng bốn thay đổi, theo đúng thứ tự đã chốt. Xem trước (`peek`) bao nhiêu lần cũng vẫn còn 10 dòng; lấy đi (`get`) một lần thì không còn. Đây là thứ mà công cụ CDC đẩy vào Kafka để các hệ khác đọc.
3. **Người đọc chưa đọc thì nhật ký phải chờ.** Thêm 200.000 dòng mà người đọc chưa đọc: PostgreSQL giữ 26 MB nhật ký cho khe đó. Đọc xong thì không còn giữ gì. Tài liệu PostgreSQL cảnh báo khe đọc không biết người đọc còn sống hay không, và vẫn giữ nhật ký kể cả khi không ai kết nối.

## Giới hạn cần nhớ

Bài không chạy Kafka; phần đối chiếu dựa trên trang "Use cases" của tài liệu Kafka, phần thử dựa trên PostgreSQL. Khác biệt đáng nhớ: Kafka giữ tin theo thời hạn rồi xóa, người đọc chậm quá sẽ mất tin; khe đọc của PostgreSQL giữ nhật ký tới khi người đọc đọc xong, nên một khe bị bỏ quên làm đầy đĩa. `test_decoding` chỉ là bộ giải mã mẫu; công cụ CDC thật dùng định dạng của riêng nó. Danh sách năm việc là của nguồn, không có số liệu kèm theo.

## Nhìn hình thử trả lời

Nhóm bạn tạo một khe CDC trên cơ sở dữ liệu đơn hàng cho một dịch vụ đồng bộ sang hệ tìm kiếm. Dịch vụ đó bị tắt khi chuyển máy và không ai bật lại. Ba tuần sau, ổ đĩa của cơ sở dữ liệu báo gần đầy dù dữ liệu không tăng bao nhiêu. Chuyện gì đã xảy ra?

<details>
<summary>Xem đáp án</summary>

Khe CDC vẫn còn và vẫn giữ toàn bộ nhật ký từ lúc người đọc dừng, như phép thử giữ 26 MB cho 200.000 dòng chưa đọc, nhưng kéo dài ba tuần. Tài liệu PostgreSQL nói khe đọc không biết người đọc còn hay không và vẫn ngăn xóa nhật ký.
Cách xử lý: bật lại dịch vụ để nó đọc hết, hoặc xóa khe (`pg_drop_replication_slot`) nếu không còn cần, rồi dựng lại bản sao cho hệ tìm kiếm từ đầu. Về lâu dài, theo dõi lượng nhật ký mỗi khe đang giữ và đặt giới hạn cho nó.

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

Cần một cụm PostgreSQL thử khởi động với `-c wal_level=logical`.

```python
import psycopg                                    # pip install "psycopg[binary]"; máy chủ cần wal_level = logical
c = psycopg.connect("host=/tmp/pglab port=5441 user=postgres", autocommit=True)
c.execute("drop table if exists orders")
if c.execute("select 1 from pg_replication_slots where slot_name = 'cdc'").fetchone():
    c.execute("select pg_drop_replication_slot('cdc')")
c.execute("create table orders(id int primary key, status text)")
c.execute("select pg_create_logical_replication_slot('cdc', 'test_decoding')")   # một 'người đọc' thay đổi

c.execute("insert into orders values (1, 'mới')")
with c.transaction():
    c.execute("update orders set status = 'đã giao' where id = 1")
    c.execute("insert into orders values (2, 'mới')")
c.execute("delete from orders where id = 2")

peek = lambda: [r[0] for r in c.execute("select data from pg_logical_slot_peek_changes('cdc', null, null)")]
print("xem trước (chưa lấy đi):"); [print("  ", line) for line in peek()]
print("xem lại lần nữa:", len(peek()), "dòng")
taken = c.execute("select count(*) from pg_logical_slot_get_changes('cdc', null, null)").fetchone()[0]
print("lấy đi:", taken, "dòng | xem lại sau khi lấy:", len(peek()), "dòng")

# Người đọc không đọc thì nhật ký phải giữ lại cho nó
c.execute("insert into orders select g, 'mới' from generate_series(10, 200009) g")
lag = lambda: c.execute("""select pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn))
                          from pg_replication_slots where slot_name = 'cdc'""").fetchone()[0]
print("nhật ký đang giữ cho người đọc chưa đọc:", lag())
c.execute("select count(*) from pg_logical_slot_get_changes('cdc', null, null)")
print("sau khi người đọc đọc xong:", lag())
c.execute("select pg_drop_replication_slot('cdc')")
```

Kết quả: mười dòng như trên (`BEGIN`, `table public.orders: INSERT: id[integer]:1 status[text]:'mới'`, `COMMIT`, rồi `UPDATE` và `INSERT` trong cùng một giao dịch, rồi `DELETE`); xem lại vẫn 10 dòng; lấy đi 10 dòng, xem lại 0; nhật ký đang giữ 26 MB, sau khi đọc xong 0 bytes.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-5-kafka-use-cases.md): Kafka sinh ra để xử lý nhật ký khối lượng lớn, giữ tin tới khi hết hạn, người đọc tự kéo tin; năm việc hay dùng.
- [Apache Kafka — Use cases, tại commit cố định](https://github.com/apache/kafka/blob/cc8baadc9f0363f2bdfe68a2f1cd8dbe4372d282/docs/getting-started/uses.md): bảy việc, trong đó theo dõi hoạt động trang web là việc đầu tiên. Đọc từ bản clone của kho.
- [PostgreSQL 16 — Logical Decoding](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/logicaldecoding.sgml), tại commit cố định của nhánh `REL_16_STABLE`: định nghĩa, khe đọc giữ tài nguyên kể cả khi không ai kết nối. Đọc từ bản clone của kho.

Phép thử chạy trên PostgreSQL 16.15, Python 3.13.16 và psycopg 3.3.6 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

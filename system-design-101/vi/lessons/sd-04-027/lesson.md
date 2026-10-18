# Một câu SQL đi qua những chặng nào? Thử từng chặng trên PostgreSQL

**Mỗi chặng mà một câu SQL đi qua để lại dấu vết riêng, và bạn tự nhìn thấy được.** Tài liệu của PostgreSQL mô tả đường đi của một truy vấn: kết nối, phân tích cú pháp, biến đổi ngữ nghĩa, viết lại, lập kế hoạch, thực thi. Hệ khác chia chặng và đặt tên khác, nhưng ý thì gần giống. Bài này gây lỗi ở từng chặng và đọc kế hoạch, bộ đệm và khóa trên PostgreSQL 16, với một bảng `orders` 200.000 dòng.

![Khung một, bốn chặng trước khi đụng dữ liệu: kết nối, câu lệnh đến qua TCP hoặc qua socket Unix trên cùng máy; phân tích cú pháp, gõ sai từ khóa thì báo lỗi cú pháp; phân tích ngữ nghĩa, tra danh mục, mở và khóa bảng, báo lỗi nếu bảng hay cột không có; viết lại, truy vấn vào một view được thay bằng bảng gốc. Khung hai, hai chặng còn lại: lập kế hoạch, chọn quét cả bảng hay dùng chỉ mục theo ước tính chi phí; thực thi, đọc các trang dữ liệu qua bộ đệm chung. Khung ba, điều thấy được: lọc một khách dùng chỉ mục còn lọc 93 phần trăm số dòng thì quét cả bảng; lần đọc đầu phải nạp 1.082 trang, lần hai cả 1.082 trang đã có sẵn; câu select cũng khóa bảng ngay từ lúc phân tích ngữ nghĩa.](../../diagrams/sd-04-027-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ cơ sở dữ liệu dùng nó.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: cách hai máy gửi dữ liệu cho nhau qua mạng, đủ và đúng thứ tự.
- **MVCC** (Multi-Version Concurrency Control) — điều khiển đồng thời bằng nhiều phiên bản: mỗi dòng có thể có vài phiên bản, nên người đọc thấy bản cũ trong khi người khác đang sửa, không phải chờ.

## Đọc hình

Mọi phép thử chạy ngày 2026-10-18 trên PostgreSQL 16.15, một cụm cục bộ; lệnh để tự chạy lại ở phần "Xem sâu hơn".

1. **Kết nối.** Câu lệnh đến máy chủ qua một kết nối. Nguồn ví dụ bằng TCP, nhưng trên cùng máy `psql` mặc định dùng socket Unix: khi đó `inet_server_addr()` trả rỗng, còn kết nối tới `localhost` trả `127.0.0.1`.
2. **Phân tích cú pháp.** Chỉ dùng luật ngữ pháp cố định, không tra bảng nào. `selec * from orders` dừng ở đây: `syntax error at or near "selec"`.
3. **Phân tích ngữ nghĩa.** Tra danh mục hệ thống để biết tên nào là bảng, cột, hàm, và mở (kèm khóa) các bảng được nhắc tới. `select * from don_hang` qua được ngữ pháp nhưng dừng ở đây: `relation "don_hang" does not exist`. Tài liệu giải thích vì sao tách hai chặng: tra danh mục phải nằm trong một giao dịch, nên lệnh như `BEGIN` hay `ROLLBACK` được nhận ra trước, chỉ bằng ngữ pháp.
4. **Viết lại.** Truy vấn vào một view được thay bằng truy vấn vào bảng gốc. Kế hoạch của `select count(*) from big_orders` chỉ nhắc tới bảng `orders`, với điều kiện của view gộp vào.
5. **Lập kế hoạch.** Bộ lập kế hoạch ước tính chi phí của các đường đi và chọn đường rẻ nhất. Cùng một chỉ mục trên cột `amount`, lọc `amount = 5` (khoảng 1% số dòng) thì dùng chỉ mục; lọc `amount < 90` (185.573 dòng, khoảng 93%) thì quét cả bảng, vì đi qua chỉ mục cho gần hết bảng còn tốn hơn.
6. **Thực thi.** Bộ thực thi đọc dữ liệu theo từng trang qua bộ đệm chung. Sau khi khởi động lại máy chủ, `EXPLAIN (ANALYZE, BUFFERS)` lần đầu báo `shared read=1082` (1.082 trang phải nạp vào bộ đệm); lần hai, `shared hit=1082`: cả 1.082 trang đã có sẵn.

Còn khóa: nguồn nói câu `SELECT` đi tới bộ đệm còn `UPDATE` và `INSERT` đi tới bộ quản lý giao dịch. Trên PostgreSQL, câu nào cũng chạy trong một giao dịch và cũng khóa bảng. Trong `pg_locks`, một `SELECT` giữ `AccessShareLock` trên bảng và các chỉ mục, xin từ lúc phân tích ngữ nghĩa và giữ tới hết giao dịch; `UPDATE` thêm `RowExclusiveLock`. Khác biệt có thật là `UPDATE` mới xin một mã giao dịch thật (`pg_current_xact_id_if_assigned()` rỗng sau `SELECT`, có giá trị sau `UPDATE`).

## Giới hạn cần nhớ

Đây là PostgreSQL. MySQL, SQL Server hay SQLite chia chặng khác và gọi tên khác; đừng mang tên chặng của hệ này sang hệ kia. Khóa ở mức nhẹ nhất của `SELECT` chỉ xung đột với khóa độc quyền (như khi `DROP TABLE`); việc đọc không chờ người đang sửa dòng là nhờ MVCC, không phải nhờ không có khóa. Số trang và thời gian chạy là của một máy; lần đọc "từ đĩa" đầu tiên có thể vẫn nằm trong bộ đệm của hệ điều hành.

## Nhìn hình thử trả lời

Ba câu lệnh gửi tới cùng một cơ sở dữ liệu đều báo lỗi: `SELEC id FROM orders`, `SELECT idd FROM orders`, và `SELECT id FROM orders` chạy mãi không xong vì một phiên khác đang `DROP TABLE orders` trong giao dịch chưa chốt. Mỗi câu dừng ở chặng nào?

<details>
<summary>Xem đáp án</summary>

Câu đầu dừng ở phân tích cú pháp: từ khóa sai, chưa cần biết có bảng nào.
Câu hai qua ngữ pháp nhưng dừng ở phân tích ngữ nghĩa: không có cột `idd`.
Câu ba cũng dừng ở phân tích ngữ nghĩa, nhưng vì phải chờ: để tra bảng `orders`, PostgreSQL mở bảng và xin `AccessShareLock` ngay ở chặng này, và khóa đó xung đột với khóa độc quyền mà `DROP TABLE` đang giữ. Thử với `lock_timeout` 1 giây, lỗi `canceling statement due to lock timeout` chỉ vào chữ `orders` của câu lệnh, tức lúc mở bảng, trước khi có kế hoạch nào. Câu `SELECT` cũng có thể bị khóa chặn.

</details>

<details>
<summary>Xem sâu hơn: lệnh tự chạy lại</summary>

Cần một cơ sở dữ liệu PostgreSQL để thử (đừng dùng cơ sở dữ liệu thật). Trong `psql`:

```sql
create table orders(id int primary key, customer text, amount int);
insert into orders select g, 'kh' || (g % 1000), g % 97 from generate_series(1, 200000) g;
create index on orders(customer);
create index on orders(amount);
analyze orders;

selec * from orders;                                  -- lỗi cú pháp
select * from don_hang;                               -- lỗi ngữ nghĩa
create view big_orders as select * from orders where amount > 90;
explain select count(*) from big_orders where customer = 'kh42';   -- chỉ thấy bảng orders
explain select * from orders where amount = 5;        -- dùng chỉ mục
explain select * from orders where amount < 90;       -- quét cả bảng
explain (analyze, buffers) select count(*) from orders;   -- chạy hai lần, so read và hit

begin;
select count(*) from orders where id < 10;
select relation::regclass, mode from pg_locks where pid = pg_backend_pid() and locktype = 'relation';
select pg_current_xact_id_if_assigned();              -- rỗng
update orders set amount = amount + 1 where id = 1;
select relation::regclass, mode from pg_locks where pid = pg_backend_pid() and locktype = 'relation';
select pg_current_xact_id_if_assigned();              -- có giá trị
rollback;
```

Muốn thấy `shared read` ở lần đầu thì khởi động lại máy chủ trước khi chạy `EXPLAIN (ANALYZE, BUFFERS)`; trong cùng một phiên, lần chạy thứ hai sẽ báo `shared hit`.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-is-a-sql-statement-executed-in-the-database.md): tám bước từ tầng vận chuyển tới bộ quản lý khóa, kèm lưu ý mỗi hệ có kiến trúc khác nhau.
- [PostgreSQL 16 — Overview of PostgreSQL Internals](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/arch-dev.sgml), tại commit cố định của nhánh `REL_16_STABLE`: đường đi của một truy vấn, lý do tách phân tích cú pháp khỏi biến đổi ngữ nghĩa, view được viết lại, chọn đường đi rẻ nhất. Đọc từ bản clone của kho.
- [PostgreSQL 16 — Concurrency Control](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/mvcc.sgml): `SELECT` giữ `ACCESS SHARE`, chỉ xung đột với `ACCESS EXCLUSIVE`. Đọc từ bản clone của kho.

Các phép thử chạy trên PostgreSQL 16.15 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

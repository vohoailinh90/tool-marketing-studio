# Học SQL bằng thử nghiệm: năm nhóm lệnh làm gì và hoàn tác được không

**Đọc cả bộ chuẩn SQL không phải cách học; chạy từng lệnh và xem dữ liệu đổi ra sao mới là cách.** Năm nhóm lệnh (DDL, DQL, DML, DCL, TCL) là nhãn dạy học quen thuộc. Điều đáng học hơn là mỗi lệnh làm gì với dữ liệu, có hoàn tác được không và có chặn người khác không. Bài này chạy thử các câu hỏi đó trên PostgreSQL và SQLite.

![Bốn khung dọc. Một: nhóm theo việc lệnh làm chứ không theo từ đầu câu; trong PostgreSQL, lệnh select into tạo ra một bảng mới và lệnh select nextval làm đổi bộ đếm. Hai: hoàn tác được không; trong PostgreSQL, thay đổi dữ liệu, tạo sửa xóa bảng, truncate và grant đều được hoàn tác bằng rollback, còn bộ đếm thì không, và SQLite cũng hoàn tác được lệnh định nghĩa bảng. Ba: một truy vấn có thể chặn người ghi; select for update làm update chờ trong khi select thường vẫn đọc được. Bốn: chỉ mục đổi cách chạy chứ không đổi đáp án; trên 200 nghìn dòng SQLite đổi từ quét toàn bảng sang tìm theo chỉ mục. Kết quả đo một lần trên một máy.](../../diagrams/sd-15-012-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ.
- **DDL** (Data Definition Language) — ngôn ngữ định nghĩa dữ liệu: nhóm lệnh tạo, sửa và xóa cấu trúc như bảng.
- **DQL** (Data Query Language) — ngôn ngữ truy vấn dữ liệu: nhóm lệnh đọc dữ liệu ra.
- **DML** (Data Manipulation Language) — ngôn ngữ thao tác dữ liệu: nhóm lệnh thêm, sửa và xóa các dòng dữ liệu.
- **DCL** (Data Control Language) — ngôn ngữ điều khiển dữ liệu: nhóm lệnh cấp và thu hồi quyền.
- **TCL** (Transaction Control Language) — ngôn ngữ điều khiển giao dịch: nhóm lệnh chốt hoặc hủy một giao dịch.
- **ISO** (International Organization for Standardization) — Tổ chức Tiêu chuẩn hóa Quốc tế: cùng IEC duy trì chuẩn SQL.
- **IEC** (International Electrotechnical Commission) — Ủy ban Kỹ thuật điện Quốc tế: cùng ISO duy trì chuẩn SQL.

## Đọc hình

Mọi phép thử chạy ngày 2026-10-16 với PostgreSQL 16.15, SQLite 3.45.1 và Python 3.13.16 trên một máy (cách tự thử ở phần "Xem sâu hơn"). Các hệ khác, hoặc phiên bản khác, có thể cho kết quả khác.

1. **Nhóm theo việc làm, không theo từ đầu câu.** Năm nhóm quen thuộc là cách gọi để dạy: sổ tay PostgreSQL tự chia thành các chương "Data Definition", "Data Manipulation" và "Queries", và không dùng nhãn DQL, DCL hay TCL ở đó. Từ đầu câu cũng không đủ để biết một lệnh làm gì. Trong PostgreSQL, `SELECT * INTO copy_of_orders FROM orders` tạo ra một bảng mới và sao chép 3 dòng vào đó (về chức năng giống `CREATE TABLE AS`). `SELECT nextval('ord_seq')` đọc ra một số nhưng làm đổi trạng thái của bộ đếm.
2. **Hoàn tác được không?** Mở giao dịch bằng `BEGIN`, làm vài việc, rồi `ROLLBACK`. Trong PostgreSQL, tạo bảng, thêm cột, xóa cả bảng (DDL), `TRUNCATE` và `GRANT` (DCL) đều được hoàn tác: sau `ROLLBACK`, bảng tạm không còn, bảng `orders` vẫn đủ 3 dòng và không có cột mới, quyền đọc vẫn chưa được cấp. Riêng bộ đếm thì không: `nextval` trả 1 trong giao dịch bị hủy, và lần gọi kế tiếp ra 2. Tài liệu của PostgreSQL cũng ghi bộ đếm không hoàn tác được. SQLite cũng hoàn tác được các lệnh DDL trong phép thử. Đừng suy ra mọi hệ làm vậy: bài chưa thử MySQL, Oracle hay SQL Server, và tài liệu của chúng chưa mở được; hãy tự thử trên hệ bạn dùng trước khi dựa vào việc "chạy thử rồi hoàn tác" cho DDL.
3. **Một truy vấn có thể chặn người ghi.** `SELECT ... FOR UPDATE` thuộc nhóm đọc nhưng khóa các dòng nó chọn. Khi một phiên giữ khóa dòng `id = 1`, phiên khác vẫn `SELECT` bình thường (thấy 10), `UPDATE` dòng `id = 2` chạy được, còn `UPDATE` dòng `id = 1` phải chờ; với `lock_timeout` đặt 500 mili giây nó bị hủy với lỗi hết thời gian chờ khóa. Phép thử chỉ có hai phiên trên một máy.
4. **Chỉ mục đổi cách chạy, không đổi đáp án.** Trên SQLite với 200.000 dòng, truy vấn `count(*)` ... `WHERE k = 1234` trả đúng 40 trước và sau khi tạo chỉ mục. Kế hoạch (`EXPLAIN QUERY PLAN`) đổi từ `SCAN t` sang `SEARCH t USING COVERING INDEX idx_k (k=?)`. Thời gian trung bình qua 20 lần chạy là khoảng 5,5 mili giây trước và khoảng 0,005 mili giây sau. Hãy xem số này là minh họa của một máy, không phải hệ số tăng tốc chung; nó phụ thuộc kích thước bảng, cách phân bố giá trị và bộ nhớ đệm.
5. **Giao dịch không chỉ là chữ trong sách.** Với thư viện `sqlite3` của Python, `INSERT` rồi đóng kết nối mà chưa gọi `commit()` thì khi mở lại bảng có 0 dòng; gọi `commit()` thì có 1 dòng. Đây là lỗi dễ gặp nhất của người mới.

## Giới hạn cần nhớ

Bài chỉ thử PostgreSQL và SQLite, một phiên bản mỗi hệ, trên bảng nhỏ và hai phiên. Kết quả về hoàn tác DDL và khóa dòng là hành vi của hai hệ đó, không phải quy tắc chung của SQL. Nhóm lệnh nào chứa lệnh nào cũng khác nhau giữa các sách và nhà cung cấp; đừng tranh luận nhãn, hãy hỏi lệnh làm gì. Phương ngữ khác nhau (PostgreSQL, MySQL, SQLite và SQL Server có cú pháp và hành vi riêng), nên luyện trên một hệ cụ thể và đối chiếu tài liệu của chính hệ đó. Thứ tự các bậc học dưới đây là gợi ý của người biên soạn, chưa thử với người học.

## Nhìn hình thử trả lời

Bạn đang đổi cấu trúc bảng `orders` trên PostgreSQL và muốn thử mà chưa chắc. Bạn bọc `ALTER TABLE ... ADD COLUMN` trong `BEGIN ... ROLLBACK`. Việc này có an toàn không, và có gì không hoàn tác được?

<details>
<summary>Xem đáp án</summary>

Trong phép thử riêng cho `ALTER TABLE ... ADD COLUMN`, PostgreSQL thấy cột mới bên trong giao dịch (1) và không còn (0) sau `ROLLBACK`. Nhưng đừng coi đó là bảo đảm chung: hệ khác có thể tự chốt giao dịch khi gặp DDL. Cũng chú ý các việc nằm ngoài giao dịch, như bộ đếm (sequence) đã tăng. Với thay đổi thật trên dữ liệu thật, hãy thử trên bản sao trước.

</details>

<details>
<summary>Xem sâu hơn: thang bài tập chạy được, và lệnh tự thử</summary>

Đoạn mã dưới đây dùng SQLite có sẵn trong Python, không cần cài gì thêm, và chạy các bậc từ 2 đến 5 của thang bên dưới trên bảng ba dòng `orders` (`an` 10, `binh` 20, `an` 30) cùng bảng `customers`.

```python
import sqlite3
c = sqlite3.connect(":memory:", isolation_level=None)
c.executescript("""
create table orders(id integer primary key, customer text, amount real);
insert into orders values (1,'an',10),(2,'binh',20),(3,'an',30);
create table customers(name text primary key, city text);
insert into customers values ('an','Hà Nội'),('binh','Huế'),('chi','Đà Nẵng');
""")
q = lambda sql: print(c.execute(sql).fetchall())
q("select customer, count(*), sum(amount) from orders group by customer order by customer")
q("select o.id, c.city from orders o join customers c on c.name = o.customer order by o.id")
q("select c.name, count(o.id) from customers c left join orders o on o.customer = c.name group by c.name order by c.name")
q("select id, amount, sum(amount) over (order by id) from orders order by id")
c.execute("begin"); c.execute("drop table orders"); c.execute("rollback")
q("select count(*) from orders")
```

Kết quả: `[('an', 2, 40.0), ('binh', 1, 20.0)]`; `[(1, 'Hà Nội'), (2, 'Huế'), (3, 'Hà Nội')]`; `[('an', 2), ('binh', 1), ('chi', 0)]` (khách `chi` chưa có đơn vẫn xuất hiện nhờ `LEFT JOIN`); `[(1, 10.0, 10.0), (2, 20.0, 30.0), (3, 30.0, 60.0)]` (tổng chạy dồn); và kết quả cuối `[(3,)]` cho biết sau `ROLLBACK` bảng `orders` vẫn còn 3 dòng.

Thang đề xuất: (1) `SELECT`, `WHERE`, `ORDER BY`; (2) `GROUP BY` và hàm tổng hợp; (3) `JOIN`, kể cả `LEFT JOIN`; (4) hàm cửa sổ; (5) `INSERT`, `UPDATE`, `DELETE` trong giao dịch với `ROLLBACK`; (6) tạo bảng, ràng buộc, chỉ mục và đọc kế hoạch. Người phân tích dữ liệu có thể dừng sâu ở bậc 1–4; người làm backend cần thêm bậc 5–6. Đây là gợi ý của người biên soạn, không phải tiêu chuẩn.

Thử lại hoàn tác trên PostgreSQL (cần một cơ sở dữ liệu thử): `begin; alter table orders add column note text; rollback;` rồi kiểm tra cột `note` không còn. Với bộ đếm: `begin; select nextval('ord_seq'); rollback; select nextval('ord_seq');` và so hai số.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-the-best-way-to-learn-sql.md): năm nhóm lệnh và lời khuyên chọn trọng tâm theo vai trò.
- [PostgreSQL — SELECT INTO](https://github.com/postgres/postgres/blob/master/doc/src/sgml/ref/select_into.sgml), [SQL Conformance](https://github.com/postgres/postgres/blob/master/doc/src/sgml/features.sgml) (ISO/IEC 9075, các bản SQL:2016, SQL:2023) và [CREATE SEQUENCE](https://github.com/postgres/postgres/blob/master/doc/src/sgml/ref/create_sequence.sgml) (bộ đếm không hoàn tác): đọc nguồn tài liệu trên GitHub ngày 2026-10-16.
- [PostgreSQL — các chương Data Definition, Data Manipulation, Queries](https://github.com/postgres/postgres/tree/master/doc/src/sgml): cách sổ tay tự chia chương, đọc ngày 2026-10-16.

Các phép thử trên PostgreSQL 16.15, SQLite 3.45.1 và Python 3.13.16 chạy trên máy biên soạn ngày 2026-10-16. Tài liệu của Oracle, MySQL, SQL Server, SQLite và trang chủ PostgreSQL chưa mở được. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

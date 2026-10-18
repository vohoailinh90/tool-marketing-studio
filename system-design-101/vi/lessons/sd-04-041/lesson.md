# Các khái niệm của sharding: chia bảng trên một máy trước khi chia ra nhiều máy

**Mọi khái niệm cốt lõi của sharding (chia ngang, chia dọc, chọn mảnh theo dải, theo băm, theo danh bạ) đều thử được trên một máy, bằng phân vùng có sẵn của PostgreSQL.** Sharding là cùng ý tưởng đó, chỉ khác mỗi mảnh nằm ở một máy riêng. Nguồn giới thiệu chia dọc và chia ngang cùng ba cách chia ngang (theo dải, theo khóa với phép chia dư cho 3, theo danh bạ). Bài này dựng từng cách và xem mỗi cách làm câu hỏi nào rẻ đi. Bài [Bốn cách chia dữ liệu vào shard](../sd-04-025/lesson.md) và [Nhập môn sharding](../sd-04-036/lesson.md) bàn chuyện dời dữ liệu và câu hỏi chạm nhiều shard.

![Ba khung dọc. Khung một, hai cách cắt một bảng: chia ngang, mỗi mảnh giữ một phần các dòng với đủ mọi cột; chia dọc, mỗi mảnh giữ một nhóm cột với đủ mọi dòng. Khung hai, ba cách chọn mảnh cho một dòng: theo dải, mỗi tháng một mảnh; theo khóa băm, băm mã khách rồi chia dư cho 3; theo danh bạ, một bảng tra ghi khách nào nằm ở mảnh nào. Khung ba, thử trên PostgreSQL 16: chia băm dư 3 cho ba mảnh 98.880, 100.500 và 100.620 dòng; hỏi một khách chỉ quét một trong ba mảnh; bỏ dữ liệu một tháng bằng cách xóa cả mảnh mất 2 đến 3 mili giây, còn xóa từng dòng mất 63 đến 236 mili giây; tách cột tiểu sử ra bảng riêng thì câu tìm theo số điện thoại đọc 768 trang thay vì 11.112.](../../diagrams/sd-04-041-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ dùng nó.

## Đọc hình

Phép thử chạy ngày 2026-10-18 trên PostgreSQL 16.15; lệnh ở phần "Xem sâu hơn". Tài liệu PostgreSQL định nghĩa phân vùng là chia một bảng lớn về mặt logic thành các mảnh vật lý nhỏ hơn.

1. **Chia ngang, theo khóa băm.** Bảng đơn hàng chia theo băm của mã khách, chia dư cho 3, thành ba mảnh: 98.880, 100.500 và 100.620 dòng. Hỏi đơn của khách 42 thì kế hoạch chỉ quét một mảnh: PostgreSQL bỏ qua hai mảnh còn lại (tài liệu gọi là cắt tỉa phân vùng). Hỏi theo số tiền, không có mã khách, thì phải quét cả ba.
2. **Chia ngang, theo dải.** Bảng đơn hàng chia theo tháng tạo đơn: tháng 7, 8, 9 mỗi tháng một mảnh. Hỏi một tuần của tháng 8 thì chỉ quét mảnh tháng 8. Bỏ dữ liệu cũ thành việc rẻ: xóa từng dòng của tháng 7 (101.090 dòng) mất từ 63 đến 236 mili giây qua hai lần chạy và để lại dòng chết chờ dọn, còn xóa cả mảnh tháng 8 mất 2,3 đến 2,7 mili giây. Tài liệu PostgreSQL cũng nói bỏ một phân vùng nhanh hơn nhiều so với xóa hàng loạt.
3. **Chia dọc.** Bảng người dùng có cột tiểu sử dài 800 ký tự. Tìm theo số điện thoại trên bảng gộp phải đọc 11.112 trang. Tách tiểu sử sang bảng riêng, bảng chính chỉ còn mã, tên và số điện thoại: cùng câu tìm đọc 768 trang, cùng đáp án 1.000 người.
4. **Theo danh bạ.** Thay vì một công thức, một bảng tra ghi từng khách (hay từng khách hàng doanh nghiệp) nằm ở mảnh nào. Chuyển một khách lớn sang mảnh riêng chỉ là sửa một dòng trong bảng tra (sau khi đã chép dữ liệu của họ). Cái giá: mỗi câu hỏi tốn thêm một lần tra, và bảng tra phải luôn đúng và luôn sẵn sàng. Bài không dựng phép thử cho cách này.

## Giới hạn cần nhớ

Phân vùng trên một máy chia việc quét và việc dọn dữ liệu, không chia sức chịu tải của máy: CPU, bộ nhớ và đĩa vẫn là của một máy. Đưa các mảnh sang máy khác là bước sharding thật, với các khó khăn của nó (giao dịch, phép nối, chia lại). PostgreSQL cho phép một phân vùng là bảng ngoài nằm ở máy khác, nhưng tài liệu cảnh báo khi đó người dùng phải tự bảo đảm dữ liệu khớp luật chia. Số đo là của một máy, bảng sinh tự động.

## Nhìn hình thử trả lời

Một ứng dụng nhật ký chỉ giữ dữ liệu 90 ngày; mỗi đêm một tác vụ xóa các dòng cũ hơn 90 ngày và chạy mất nhiều thời gian. Câu hỏi hay chạy nhất là "nhật ký của thiết bị X trong 24 giờ qua". Bạn chia bảng thế nào?

<details>
<summary>Xem đáp án</summary>

Chia ngang theo dải thời gian, mỗi ngày (hoặc mỗi tuần) một mảnh. Việc dọn hằng đêm thành bỏ một mảnh, nhanh như bỏ mảnh tháng 8 trong phép thử (vài mili giây, so với 63 đến 236 mili giây khi xóa từng dòng), và không để lại dòng chết. Câu hỏi "24 giờ qua" chỉ chạm một hai mảnh mới nhất.
Thêm chỉ mục trên mã thiết bị trong từng mảnh để lọc thiết bị X. Chia theo băm mã thiết bị thì câu hỏi theo thiết bị rẻ, nhưng việc dọn dữ liệu cũ lại phải xóa từng dòng trong mọi mảnh.

</details>

<details>
<summary>Xem sâu hơn: lệnh của phép thử</summary>

```sql
-- Chia ngang theo băm, chia dư cho 3
create table orders_h(id int, customer int, amount int) partition by hash(customer);
create table orders_h0 partition of orders_h for values with (modulus 3, remainder 0);
create table orders_h1 partition of orders_h for values with (modulus 3, remainder 1);
create table orders_h2 partition of orders_h for values with (modulus 3, remainder 2);
insert into orders_h select g, g % 5000, g % 97 from generate_series(1, 300000) g;
select tableoid::regclass, count(*) from orders_h group by 1 order by 1;
explain select * from orders_h where customer = 42;              -- chỉ một mảnh

-- Chia ngang theo dải tháng
create table orders_r(id int, created_at date, amount int) partition by range(created_at);
create table orders_2026_07 partition of orders_r for values from ('2026-07-01') to ('2026-08-01');
create table orders_2026_08 partition of orders_r for values from ('2026-08-01') to ('2026-09-01');
create table orders_2026_09 partition of orders_r for values from ('2026-09-01') to ('2026-10-01');
insert into orders_r select g, date '2026-07-01' + (g % 92), g % 97 from generate_series(1, 300000) g;
explain select sum(amount) from orders_r where created_at between '2026-08-10' and '2026-08-16';
\timing on
delete from orders_r where created_at < '2026-08-01';           -- xóa từng dòng của tháng 7
drop table orders_2026_08;                                       -- bỏ cả mảnh tháng 8

-- Chia dọc
create table users_wide(id int primary key, name text, phone text, bio text);
insert into users_wide select g, 'user' || g, '09' || lpad(g::text, 8, '0'), repeat('x', 800)
  from generate_series(1, 100000) g;
create table users_core as select id, name, phone from users_wide;
vacuum analyze users_wide; vacuum analyze users_core;
explain (analyze, buffers) select count(*) from users_wide where phone like '%99';
explain (analyze, buffers) select count(*) from users_core where phone like '%99';
```

Kết quả: ba mảnh 98.880, 100.500, 100.620 dòng; `Seq Scan on orders_h0` khi hỏi khách 42; chỉ quét `orders_2026_08` khi hỏi tuần giữa tháng 8; `DELETE 101090` từ 63 đến 236 mili giây, `DROP TABLE` từ 2,3 đến 2,7 mili giây (hai lần chạy); 11.112 và 768 trang cho hai câu tìm số điện thoại. Thời gian là của một máy.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/key-concepts-to-understand-database-sharding.md): chia dọc và chia ngang; chia theo dải, theo khóa (phép chia dư cho 3), theo danh bạ.
- [PostgreSQL 16 — Table Partitioning](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/ddl.sgml), tại commit cố định của nhánh `REL_16_STABLE`: định nghĩa phân vùng, phân vùng theo băm với modulus và remainder, cắt tỉa phân vùng, bỏ phân vùng nhanh hơn xóa hàng loạt, phân vùng là bảng ngoài. Đọc từ bản clone của kho.

Phép thử chạy trên PostgreSQL 16.15 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

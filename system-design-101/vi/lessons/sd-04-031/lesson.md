# PostgreSQL "nuốt" cả thế giới cơ sở dữ liệu? Thử phần có sẵn, đếm phần cần cài thêm

**"Phân vân thì cứ dùng PostgreSQL" có cơ sở, nhưng cần tách ba thứ: tính năng có sẵn, tiện ích cài thêm, và hệ khác chỉ nói cùng giao thức.** Nguồn kể tám mảng mà PostgreSQL vươn tới, từ chuỗi thời gian, học máy, phân tích, bản đồ, tìm kiếm tới đồ thị, phần lớn nhờ tiện ích. Bài này thử bốn việc chỉ bằng tính năng có trong PostgreSQL 16, rồi xem phần nào thật sự cần thứ khác.

![Ba khung dọc. Khung một, có sẵn trong PostgreSQL 16, đã thử: chuỗi thời gian, chỉ mục brin chỉ 24 kB trong khi chỉ mục B-tree 43 MB trên cùng 2 triệu dòng; tài liệu JSON, chỉ mục gin tìm 6.000 tài liệu có một nhãn; tìm toàn văn, tsvector với chỉ mục gin tìm ra 1 dòng trong 300.000; đồ thị đơn giản, with recursive đi hết cây cấp dưới. Khung hai, cần tiện ích ngoài: tìm vector cho học máy dùng pgvector; bản đồ dùng PostGIS; chia bảng ra nhiều máy dùng Citus. Khung ba, nói giao thức PostgreSQL chưa phải là PostgreSQL: CockroachDB nhận trình điều khiển của PostgreSQL nhưng là một hệ khác; giấy phép, cách lưu và tính năng do chính hệ đó quyết định.](../../diagrams/sd-04-031-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ cơ sở dữ liệu dùng nó.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm các cặp tên và giá trị; PostgreSQL lưu được nó trong cột kiểu `jsonb`.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng; PostgreSQL in kích thước theo bội của 1.024, nên 43 MB ở đây là 44.949.504 byte.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức để ghi và tìm lại nhanh; có trong tên CockroachDB.
- **GIS** (Geographic Information System) — hệ thống thông tin địa lý: phần mềm lưu và hỏi dữ liệu gắn với vị trí trên bản đồ; có trong tên PostGIS, tiện ích bản đồ của PostgreSQL.

## Đọc hình

Phép thử chạy ngày 2026-10-18 trên PostgreSQL 16.15, không cài tiện ích nào; lệnh ở phần "Xem sâu hơn".

1. **Chuỗi thời gian.** Bảng 2 triệu số đo, mỗi giây một dòng, ghi theo thứ tự thời gian (100 MB). Chỉ mục `brin` chỉ ghi tóm tắt giá trị nhỏ nhất và lớn nhất của từng nhóm trang liền nhau, nên nặng 24.576 byte, còn chỉ mục B-tree trên cùng cột nặng 44.949.504 byte. Hỏi một ngày (86.401 dòng), `brin` cho biết chỉ cần đọc 640 khối, rồi lọc lại 14.079 dòng thừa. Nó tốt vì dữ liệu nằm theo thứ tự thời gian; dữ liệu xáo trộn thì tóm tắt vô dụng.
2. **Tài liệu JSON.** 300.000 tài liệu `jsonb` với chỉ mục `gin`: tìm tài liệu có nhãn `t7` trả 6.000 tài liệu qua chỉ mục, không quét cả bảng.
3. **Tìm toàn văn.** `to_tsvector` cắt tiêu đề thành từ; chỉ mục `gin` trên đó tìm đúng 1 dòng chứa cả "đợi" lẫn "12344" trong 300.000 dòng. Cấu hình `simple` chỉ tách theo khoảng trắng và hạ chữ thường, không hiểu tiếng Việt: nó không biết "hàng đợi" là một cụm từ.
4. **Đồ thị đơn giản.** `with recursive` đi từ một trưởng nhóm xuống hết cấp dưới (3 người, sâu 2 tầng).

Còn lại cần tiện ích ngoài: tìm vector (pgvector), bản đồ thật (PostGIS), chia bảng ra nhiều máy (Citus) không có trong bản cài. Mảng "dẫn xuất" của nguồn lại là chuyện khác: CockroachDB ghi trong README rằng nó hỗ trợ giao thức truyền của PostgreSQL để dùng được trình điều khiển của PostgreSQL. Nó vẫn là một hệ khác, với giấy phép, cách lưu và tính năng riêng.

## Giới hạn cần nhớ

Làm được không có nghĩa là làm tốt bằng hệ chuyên dụng ở quy mô lớn: bài chỉ thử trên một máy, dữ liệu sinh tự động, không so với hệ chuyên dụng nào. Mỗi tiện ích thêm một thứ phải nâng cấp, theo dõi và kiểm giấy phép. "Hỗ trợ giao thức PostgreSQL" chỉ nói về cách kết nối, không nói hai hệ chạy giống nhau.

## Nhìn hình thử trả lời

Bảng nhật ký của bạn ghi thêm dòng mới theo thời gian, rồi một tác vụ hằng đêm cập nhật lại cột `ts` của nhiều dòng cũ theo giờ chuẩn của từng khách. Chỉ mục `brin` trên `ts` còn hữu ích không?

<details>
<summary>Xem đáp án</summary>

Kém đi. `brin` chỉ nhớ giá trị nhỏ nhất và lớn nhất của từng nhóm trang; nó hiệu quả khi thứ tự giá trị đi cùng thứ tự các dòng trên đĩa. Khi nhiều dòng cũ đổi `ts`, mỗi nhóm trang chứa cả giá trị cũ lẫn giá trị mới, khoảng tóm tắt của nó nới rộng ra, và truy vấn một ngày phải đọc thêm nhiều nhóm.
Thử trên chính bảng `events`: sửa ngẫu nhiên khoảng 5% số dòng, mỗi dòng dời `ts` tới tối đa 30 ngày, rồi `vacuum analyze`. Cùng câu hỏi một ngày phải đọc 960 khối thay vì 640, và lọc bỏ 62.414 dòng thừa thay vì 14.079 (một lần chạy; con số đổi theo phép chọn ngẫu nhiên). Chỉ mục B-tree to hơn nhưng không phụ thuộc thứ tự trên đĩa.

</details>

<details>
<summary>Xem sâu hơn: lệnh của phép thử</summary>

```sql
create table events(ts timestamptz, device int, value float8);
insert into events select timestamptz '2026-01-01' + g * interval '1 second', g % 100, g % 1000
  from generate_series(1, 2000000) g;
create index events_brin on events using brin(ts);
create index events_btree on events(ts);
select pg_relation_size('events_brin'), pg_relation_size('events_btree');   -- 24576 và 44949504
drop index events_btree;
explain (analyze) select avg(value) from events where ts between '2026-01-05' and '2026-01-06';

create table docs(id int primary key, body jsonb, title text);
insert into docs select g,
  jsonb_build_object('tags', jsonb_build_array('t' || (g % 50), 't' || (g % 7)), 'author', 'a' || (g % 300)),
  case g % 3 when 0 then 'Cơ sở dữ liệu quan hệ và chỉ mục' when 1 then 'Bộ nhớ đệm cho trang web'
             else 'Hàng đợi tin nhắn giữa các dịch vụ' end || ' số ' || g
  from generate_series(1, 300000) g;
create index on docs using gin(body jsonb_path_ops);
create index on docs using gin(to_tsvector('simple', title));
select count(*) from docs where body @> '{"tags": ["t7"]}';                  -- 6000
select id, title from docs where to_tsvector('simple', title) @@ to_tsquery('simple', 'đợi & 12344');

create table staff(id int primary key, boss int, name text);
insert into staff values (1, null, 'Giám đốc'), (2, 1, 'Trưởng nhóm A'), (3, 1, 'Trưởng nhóm B'),
  (4, 2, 'Kỹ sư 1'), (5, 2, 'Kỹ sư 2'), (6, 4, 'Thực tập sinh');
with recursive under(id, name, depth) as (
  select id, name, 0 from staff where id = 2
  union all
  select s.id, s.name, u.depth + 1 from staff s join under u on s.boss = u.id)
select * from under order by depth, id;
```

Thêm `explain (analyze)` trước hai câu tìm trong `docs` để thấy chúng đi qua chỉ mục (`Bitmap Index Scan`). Câu tìm "hàng & đợi" khớp 100.000 dòng, nên bộ lập kế hoạch bỏ chỉ mục và quét cả bảng: chỉ mục có ích khi câu hỏi chọn lọc.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/is-postgresql-eating-the-database-world.md): tám mảng (chuỗi thời gian, học máy, phân tích, hệ dẫn xuất, bản đồ, tìm kiếm, truy vấn liên hợp, đồ thị) và các tiện ích tiêu biểu.
- [PostgreSQL 16 — BRIN Indexes](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/brin.sgml), [GIN Indexes](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/gin.sgml), [JSON Types](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/json.sgml), [Full Text Search](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/textsearch.sgml), tại commit cố định của nhánh `REL_16_STABLE`. Đọc từ bản clone của kho.
- [CockroachDB — README, tại commit cố định](https://github.com/cockroachdb/cockroach/blob/d30c905fff79ef825adc96bcc647f1872a90f2ff/README.md): hỗ trợ giao thức truyền của PostgreSQL. Đọc từ bản clone của kho.

Phép thử chạy trên PostgreSQL 16.15 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

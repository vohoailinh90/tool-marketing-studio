# PostgreSQL được yêu thích vì làm được nhiều việc: thử xem việc nào có sẵn

**"Một cơ sở dữ liệu cho gần như mọi việc" đúng một nửa: phần lớn các việc đó đến từ tiện ích cài thêm, không phải từ bản cài.** Nguồn giải thích vì sao PostgreSQL được bình chọn là cơ sở dữ liệu được yêu thích nhất trong khảo sát nhà phát triển năm 2022 của Stack Overflow: nó làm được bảy việc, từ giao dịch tới bản đồ. Bài này thử từng việc trên một bản cài PostgreSQL 16 và chia chúng làm ba loại.

![Ba khung dọc, kết quả thử trên một bản cài PostgreSQL 16. Khung một, có sẵn trong bản cài: giao dịch thêm, đọc, sửa, xóa là lõi của PostgreSQL; postgres_fdw đi kèm bản cài, nối một bảng ở cơ sở dữ liệu khác như bảng thường. Khung hai, phân tích chạy được nhưng dữ liệu lưu theo dòng: cộng một cột trên 500.000 dòng đọc cả 7.744 trang, đọc cả bảy cột cũng 7.744 trang. Khung ba, cần tiện ích của bên thứ ba, không có trong bản cài: PostGIS cho dữ liệu bản đồ, TimescaleDB cho chuỗi thời gian, Citus để chia bảng ra nhiều máy, và PipelineDB không ra bản mới sau 1.0.0, chỉ hỗ trợ PostgreSQL 10 và 11.](../../diagrams/sd-04-029-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ cơ sở dữ liệu dùng nó.
- **OLTP** (OnLine Transaction Processing) — xử lý giao dịch trực tuyến: nhiều thao tác nhỏ trên ít dòng, như đặt một đơn hàng.
- **CRUD** (Create, Read, Update, Delete) — tạo, đọc, sửa, xóa: bốn thao tác cơ bản trên dữ liệu.
- **OLAP** (OnLine Analytical Processing) — xử lý phân tích trực tuyến: câu hỏi tổng hợp trên rất nhiều dòng, như doanh thu theo tháng.
- **HTAP** (Hybrid Transactional/Analytical Processing) — xử lý lai giao dịch và phân tích: một hệ được thiết kế để chạy cả hai loại việc trên cùng dữ liệu.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức để ghi và tìm lại nhanh; có trong tên TimescaleDB và PipelineDB, hai tiện ích của PostgreSQL.
- **FDW** (Foreign Data Wrapper) — bộ bọc dữ liệu ngoài: cách PostgreSQL đọc một bảng nằm ở hệ khác như thể bảng của chính nó.

## Đọc hình

Phép thử chạy ngày 2026-10-18 trên PostgreSQL 16.15, gói của Ubuntu; lệnh ở phần "Xem sâu hơn".

1. **Có sẵn.** Giao dịch OLTP với các thao tác CRUD là việc chính của PostgreSQL. `postgres_fdw` là một module đi kèm bản cài (thư mục `contrib`), cần bật bằng `create extension`: với nó, một câu `join` nối bảng `sales` ở cơ sở dữ liệu này với bảng `products` ở cơ sở dữ liệu khác, và kế hoạch ghi `Foreign Scan on products`.
2. **Chạy được, nhưng không phải HTAP.** Nguồn nói PostgreSQL dựa trên kiến trúc HTAP. Thực ra bảng thường của PostgreSQL lưu theo dòng: tài liệu gọi mỗi dòng là một mục trên trang 8 kB, và một dòng không vắt qua hai trang (giá trị quá lớn được nén hoặc cắt ra lưu riêng). Trên bảng 500.000 dòng, bảy cột, câu `sum(c1)` chỉ cần một cột vẫn phải đọc cả 7.744 trang, đúng bằng số trang khi cộng cả bảy cột. Phân tích vẫn chạy được, nhưng hệ lưu theo cột chỉ đọc cột cần dùng.
3. **Cần tiện ích bên thứ ba.** Bản cài thử có 47 tiện ích dùng được, không có PostGIS (bản đồ), TimescaleDB (chuỗi thời gian) hay Citus (chia bảng ra nhiều máy): mỗi cái là một dự án riêng, cài riêng. PipelineDB, ví dụ của nguồn cho dữ liệu dòng chảy, đã ngừng: README của nó ghi không có bản mới sau 1.0.0, chỉ hỗ trợ PostgreSQL 10 và 11, commit cuối năm 2019.

## Giới hạn cần nhớ

"Có tiện ích" chưa có nghĩa là dùng được ở chỗ bạn: dịch vụ đám mây chỉ cho bật một danh sách tiện ích nhất định, và mỗi tiện ích có phiên bản, giấy phép và đội phát triển riêng. Bài chỉ đếm tiện ích có trong gói PostgreSQL 16 của Ubuntu; gói của hệ khác có thể khác. Kết quả bình chọn năm 2022 là theo nguồn, bài chưa mở được số liệu gốc của khảo sát.

## Nhìn hình thử trả lời

Nhóm bạn định dùng PostgreSQL cho cả ứng dụng bán hàng lẫn báo cáo tồn kho theo vị trí kho trên bản đồ, chạy trên dịch vụ cơ sở dữ liệu của một nhà cung cấp đám mây. Cần kiểm hai điều gì trước khi chốt?

<details>
<summary>Xem đáp án</summary>

Thứ nhất, dịch vụ đó có cho bật PostGIS không, phiên bản nào: bản đồ không có trong bản cài mà đến từ tiện ích ngoài.
Thứ hai, báo cáo quét bao nhiêu dữ liệu: PostgreSQL lưu theo dòng, nên báo cáo trên bảng lớn đọc cả dòng dù chỉ cần vài cột; với lượng lớn có thể cần bản sao chỉ để đọc, bảng tổng hợp sẵn, hoặc một hệ phân tích riêng.

</details>

<details>
<summary>Xem sâu hơn: lệnh của phép thử</summary>

```sql
-- Có những tiện ích nào dùng được
select count(*) from pg_available_extensions;
select name from pg_available_extensions where name in ('postgres_fdw', 'postgis', 'timescaledb', 'citus');

-- Đọc bảng ở cơ sở dữ liệu khác (kho_b có bảng products)
create extension postgres_fdw;
create server kho_b foreign data wrapper postgres_fdw options (host '/tmp', port '5432', dbname 'kho_b');
create user mapping for current_user server kho_b options (user 'postgres');
create schema remote;
import foreign schema public from server kho_b into remote;
select p.name, sum(s.qty) from sales s join remote.products p on p.id = s.product_id group by p.name;

-- Lưu theo dòng: một cột hay bảy cột đều đọc cùng số trang
create table wide as select g as id, g%97 as c1, g%89 as c2, g%83 as c3, g%79 as c4, g%73 as c5,
  md5(g::text) as note1, md5((g+1)::text) as note2 from generate_series(1, 500000) g;
explain (analyze, buffers) select sum(c1) from wide;
explain (analyze, buffers) select sum(length(note1) + length(note2) + c1 + c2 + c3 + c4 + c5) from wide;
```

Kết quả: 47 tiện ích, chỉ có `postgres_fdw` trong bốn cái được hỏi; câu `join` trả 3 sản phẩm; hai câu `explain` đều chạm 7.744 trang (`hit` cộng `read`).

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/why-is-postgresql-voted-as-the-most-loved-database-by-stackoverflow-2022-developer-survey.md): bảy việc (OLTP, OLAP, FDW, dữ liệu dòng chảy, bản đồ, chuỗi thời gian, bảng phân tán) và kết quả khảo sát năm 2022.
- [PostgreSQL 16 — postgres_fdw](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/postgres-fdw.sgml) và [Additional Supplied Modules](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/contrib.sgml), tại commit cố định của nhánh `REL_16_STABLE`: module đọc dữ liệu ở máy PostgreSQL khác; các module `contrib` đi kèm bản phân phối nhưng không thuộc lõi. Đọc từ bản clone của kho.
- [PostgreSQL 16 — Database Page Layout và TOAST](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/storage.sgml): trong bảng, mỗi mục trên trang là một dòng; dòng không vắt qua nhiều trang. Đọc từ bản clone của kho.
- [PipelineDB — README, tại commit cuối](https://github.com/pipelinedb/pipelinedb/blob/5cc6ef58ab5b1c84bb7b4e932f99bf5c347f46d8/README.md): không có bản mới sau 1.0.0; hỗ trợ PostgreSQL 10 và 11. Đọc từ bản clone của kho.

Phép thử chạy trên PostgreSQL 16.15 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

# Tám cấu trúc dữ liệu sau chỉ mục: mỗi cái trả lời một kiểu câu hỏi

**Một chỉ mục chỉ nhanh với kiểu câu hỏi mà cấu trúc bên dưới nó được dựng cho.** Nguồn liệt kê tám cấu trúc hay gặp: skiplist, bảng băm, SSTable, cây LSM, B-tree, chỉ mục đảo, cây hậu tố, R-tree. Chọn cái nào tùy dữ liệu nằm trong bộ nhớ hay trên đĩa, ghi nhiều hay đọc nhiều, và câu hỏi là "đúng bằng", "trong khoảng", "chứa từ" hay "gần nhất". Bài này thử điều đó trên PostgreSQL 16 và Redis 7.0.

![Bốn khung dọc. Một, trong bộ nhớ: skiplist, danh sách nhiều tầng giữ thứ tự, dùng cho tập có thứ tự của Redis; bảng băm tìm đúng một khóa, không trả lời theo khoảng. Hai, trên đĩa: B-tree tìm đúng khóa lẫn theo khoảng; SSTable là tệp đã sắp xếp, ghi một lần không sửa; LSM gom lượt ghi trong bộ nhớ rồi xả ra SSTable, ghi nhanh nhưng phải gộp tệp ở nền. Ba, câu hỏi đặc thù: chỉ mục đảo đi từ một từ tới các tài liệu chứa nó; cây hậu tố tìm chuỗi con, PostgreSQL dùng bộ ba ký tự cho việc này; R-tree tìm điểm gần nhất, PostgreSQL dùng GiST. Bốn, đã thử: chỉ mục băm phục vụ phép bằng, phép between vẫn quét cả bảng; B-tree phục vụ cả hai; tập có thứ tự 128 phần tử là listpack, 129 là skiplist.](../../diagrams/sd-04-034-main.svg)

## Từ viết tắt

- **LSM** (Log-Structured Merge) — gộp theo kiểu nhật ký: cách lưu ghi mọi thay đổi nối tiếp vào bộ nhớ và tệp mới, rồi gộp các tệp ở nền, thay vì sửa tại chỗ.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ dùng nó.
- **WAL** (Write-Ahead Log) — nhật ký ghi trước: thay đổi được ghi vào nhật ký trước khi vào cấu trúc chính, để khôi phục được khi máy tắt đột ngột; Cassandra gọi nó là commit log.

## Đọc hình

1. **Trong bộ nhớ.** Skiplist là danh sách liên kết có thêm các tầng "đường tắt", giữ phần tử theo thứ tự nên lấy được một khoảng. Mã của Redis ghi tập có thứ tự (sorted set) dùng skiplist cùng một bảng băm từ phần tử tới điểm. Bảng băm tìm đúng một khóa rất nhanh nhưng làm mất thứ tự.
2. **Trên đĩa.** B-tree là cây cân bằng, mỗi nút một trang, phục vụ cả "đúng bằng" lẫn "trong khoảng" với số lần đọc ổn định. SSTable (Sorted String Table) là tệp khóa đã sắp xếp, ghi một lần không sửa. Cây LSM ghép hai thứ: lượt ghi vào bảng trong bộ nhớ (cùng WAL), đầy thì xả ra một SSTable mới; tài liệu của Cassandra mô tả đúng đường ghi này, và cái giá là gộp tệp ở nền khiến mỗi dòng bị ghi lại nhiều lần.
3. **Câu hỏi đặc thù.** Chỉ mục đảo đi từ một từ tới các tài liệu chứa nó (tìm toàn văn). Cây hậu tố tìm chuỗi con; PostgreSQL giải cùng bài toán bằng cách khác: tiện ích `pg_trgm` cắt chuỗi thành bộ ba ký tự và đánh chỉ mục chúng, phục vụ được `like '%abc12%'`. R-tree gom điểm theo hình chữ nhật bao để tìm "gần nhất" hay "trong vùng"; PostgreSQL làm việc này bằng khung chỉ mục GiST.

**Đã thử ngày 2026-10-18.** Trên PostgreSQL 16.15, bảng 200.000 dòng, tắt quét tuần tự (`enable_seqscan = off`) để hỏi "chỉ mục này có phục vụ được câu hỏi không": chỉ mục băm dùng được cho `code = 4242`, nhưng `code between 100 and 200` vẫn quét cả bảng; chỉ mục B-tree trên cùng cột phục vụ cả hai. Chỉ mục GiST trên cột điểm phục vụ `order by pos <-> point(500,500) limit 3`, chỉ mục bộ ba ký tự phục vụ `like '%abc12%'`. Trên Redis 7.0.15, tập có thứ tự 128 phần tử được lưu dạng `listpack` (một mảng gọn); thêm phần tử thứ 129 thì chuyển sang `skiplist`, đúng ngưỡng `zset-max-listpack-entries 128` trong cấu hình.

## Giới hạn cần nhớ

Danh sách tám cái không đầy đủ, như chính nguồn nói. Tên cấu trúc trong sách và tên trong một hệ cụ thể không trùng nhau một-một: PostgreSQL không có "cây hậu tố" hay "R-tree" theo đúng tên, mà có các khung chỉ mục (`gin`, `gist`, `spgist`) để dựng nhiều chiến lược trên đó. Bài chỉ kiểm chỉ mục nào được dùng, không đo tốc độ, và chưa thử LSM thật (như RocksDB hay Cassandra).

## Nhìn hình thử trả lời

Bảng `orders` có cột `created_at`. Hai câu hỏi hay chạy nhất là "đơn số 123 ở đâu" và "các đơn trong tuần này". Bạn đặt chỉ mục băm trên `created_at` cho nhẹ. Câu nào được lợi, câu nào không?

<details>
<summary>Xem đáp án</summary>

Không câu nào được lợi đúng chỗ. Câu "đơn số 123" tìm theo khóa chính, chỉ mục trên `created_at` không liên quan. Câu "trong tuần này" là câu hỏi theo khoảng, và chỉ mục băm chỉ phục vụ phép bằng: phép thử cho thấy `between` vẫn quét cả bảng dù đã tắt quét tuần tự.
Dùng B-tree trên `created_at`: nó phục vụ được cả "đúng bằng" lẫn "trong khoảng".

</details>

<details>
<summary>Xem sâu hơn: lệnh của phép thử</summary>

PostgreSQL:

```sql
create extension pg_trgm;
create table t_btree as select g as code, md5(g::text) as name, point(random()*1000, random()*1000) as pos
  from generate_series(1, 200000) g;
create table t_hash as select * from t_btree;
create index on t_btree(code);
create index on t_hash using hash(code);
create index on t_btree using gist(pos);
create index on t_btree using gin(name gin_trgm_ops);
analyze;
set enable_seqscan = off;
explain select * from t_hash where code = 4242;                        -- Index Scan
explain select * from t_hash where code between 100 and 200;           -- Seq Scan
explain select * from t_btree where code between 100 and 200;          -- Index Scan
explain select code from t_btree order by pos <-> point(500,500) limit 3;  -- Index Scan ... gist
explain select code from t_btree where name like '%abc12%';            -- Bitmap Index Scan ... gin
```

Redis:

```bash
for i in $(seq 1 128); do redis-cli zadd board $i u$i > /dev/null; done
redis-cli object encoding board     # listpack
redis-cli zadd board 129 u129
redis-cli object encoding board     # skiplist
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/8-data-structures-that-power-your-databases.md): tám cấu trúc và lưu ý danh sách không đầy đủ.
- [Redis — `src/t_zset.c`](https://github.com/redis/redis/blob/5e332cabd547d272783cf233a34c81dcb9ea44b3/src/t_zset.c) và [`redis.conf`](https://github.com/redis/redis/blob/5e332cabd547d272783cf233a34c81dcb9ea44b3/redis.conf), tại commit cố định: tập có thứ tự dùng skiplist cùng bảng băm; `zset-max-listpack-entries 128`. Đọc từ bản clone của kho.
- [Apache Cassandra — Storage Engine](https://github.com/apache/cassandra/blob/95b178a141824a0414c4add9b5ab87eaa1ca13bf/doc/modules/cassandra/pages/architecture/storage-engine.adoc), tại commit cố định: cây LSM, memtable, SSTable bất biến, commit log, gộp tệp và ghi lại nhiều lần. Đọc từ bản clone của kho.
- PostgreSQL 16, tại commit cố định của nhánh `REL_16_STABLE`: [Hash Indexes](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/hash.sgml) (chỉ phép `=`), [Index Types](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/indices.sgml) (GiST tìm gần nhất), [pg_trgm](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/pgtrgm.sgml) (chỉ mục cho `LIKE`). Đọc từ bản clone của kho.

Phép thử chạy trên PostgreSQL 16.15 và Redis 7.0.15 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

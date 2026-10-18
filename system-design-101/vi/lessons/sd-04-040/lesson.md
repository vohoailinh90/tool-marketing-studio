# Các loại cơ sở dữ liệu: bốn nhóm NoSQL và hai nghĩa của chữ "cột"

**Tên một loại cơ sở dữ liệu chỉ có ích khi bạn biết nó sắp dữ liệu thế nào trên đĩa; chữ "cột" là ví dụ dễ nhầm nhất.** Nguồn chia sáu loại: quan hệ, phân tích (OLAP) và NoSQL với bốn nhóm (đồ thị, khóa–giá trị, tài liệu, cột). Trong đó "cơ sở dữ liệu cột" được dùng cho hai thứ rất khác nhau: hệ lưu theo cột để phân tích, và hệ "cột rộng" như Cassandra, vốn là một kho NoSQL chia theo khóa. Bài này tách hai nghĩa đó và đo cái lợi của việc lưu theo cột.

![Bốn khung dọc. Khung một, quan hệ và phân tích: cơ sở dữ liệu quan hệ dùng bảng, khóa và giao dịch; hệ phân tích OLAP tổng hợp rất nhiều dòng và thường lưu theo cột. Khung hai, bốn nhóm NoSQL: đồ thị cho quan hệ giữa các đối tượng; khóa và giá trị để lấy đúng một khóa thật nhanh; tài liệu cho bản ghi dạng JSON, mỗi bản một kiểu; và cột, chữ này có hai nghĩa. Khung ba, hai nghĩa của chữ cột: lưu theo cột, mỗi cột một chỗ, nén tốt, dùng cho phân tích; cột rộng như Cassandra, các dòng gom theo khóa phân vùng, mỗi dòng có nhiều cột. Khung bốn, đo một triệu dòng bán hàng: SQLite lưu theo dòng nặng 25,4 MB; DuckDB lưu theo cột nặng 2,1 MB; cột năm chỉ có một giá trị nên DuckDB lưu một hằng số.](../../diagrams/sd-04-040-main.svg)

## Từ viết tắt

- **OLAP** (OnLine Analytical Processing) — xử lý phân tích trực tuyến: câu hỏi tổng hợp trên rất nhiều dòng, như tổng doanh thu theo thành phố.
- **NoSQL** (Not only SQL) — tên chung cho các cơ sở dữ liệu không theo mô hình bảng quan hệ, như kho tài liệu hay kho khóa–giá trị.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; SQLite và DuckDB đều nhận câu SQL.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm các cặp tên và giá trị, dạng mà kho tài liệu thường lưu.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng cỡ một triệu byte.

## Đọc hình

1. **Quan hệ và phân tích.** Cơ sở dữ liệu quan hệ giữ dữ liệu trong bảng nối với nhau bằng khóa và chạy giao dịch. Hệ phân tích trả lời câu hỏi tổng hợp trên rất nhiều dòng; để làm vậy nhanh, chúng thường lưu theo cột.
2. **Bốn nhóm NoSQL.** Đồ thị cho dữ liệu mà quan hệ giữa các đối tượng là điều quan trọng nhất. Khóa–giá trị để lấy đúng một thứ theo khóa. Tài liệu cho bản ghi dạng JSON, mỗi bản có thể một kiểu. Nhóm thứ tư, "cột", cần tách làm hai.
3. **Hai nghĩa của chữ "cột".** *Lưu theo cột*: mọi giá trị của một cột nằm liền nhau, nên câu hỏi chỉ cần ba cột thì chỉ đọc ba cột, và một cột nhiều giá trị lặp nén rất tốt; đây là cách của hệ phân tích như DuckDB. *Cột rộng*: tài liệu Cassandra tự mô tả là mô hình lưu trữ "cột rộng chia phân vùng" với ngữ nghĩa nhất quán sau cùng; dữ liệu được gom theo khóa phân vùng, mỗi dòng trong phân vùng có thể nhiều cột. Đó là một kho NoSQL để đọc ghi theo khóa ở quy mô lớn, không phải hệ phân tích.
4. **Đo.** Phép thử chạy ngày 2026-10-18 với SQLite 3.45.1 và DuckDB 1.5.6: cùng một triệu dòng bán hàng (mã, thành phố, cửa hàng, năm, số lượng), cùng tổng số lượng. Tệp SQLite, lưu theo dòng, nặng 25,4 MB; tệp DuckDB, lưu theo cột, nặng 2,1 MB. DuckDB cho biết nó nén từng cột một kiểu: cột thành phố bằng từ điển (năm tên, mỗi dòng chỉ giữ số thứ tự), các cột số bằng cách dồn bit, và cột năm, chỉ có một giá trị, thành một hằng số.

## Giới hạn cần nhớ

Dữ liệu sinh tự động nên lặp nhiều hơn dữ liệu thật; tỉ lệ nén thật thường thấp hơn. Kích thước tệp DuckDB còn gồm phần dành sẵn theo khối, nên với bảng nhỏ con số không nói nhiều. Lưu theo cột có cái giá: thêm hay sửa từng dòng đắt hơn, vì một dòng nằm rải ở nhiều cột. Bài không thử Cassandra, chỉ đọc tài liệu của nó; các nhóm đồ thị, khóa–giá trị và tài liệu có phép thử ở các bài khác của nhóm này.

## Nhìn hình thử trả lời

Một đồng nghiệp đề xuất: "Báo cáo doanh thu chạy chậm, ta chuyển sang một cơ sở dữ liệu cột như Cassandra." Câu này lẫn chỗ nào?

<details>
<summary>Xem đáp án</summary>

Lẫn hai nghĩa của chữ "cột". Báo cáo doanh thu là câu hỏi tổng hợp trên nhiều dòng, thứ cần *lưu theo cột* (như hệ phân tích DuckDB trong phép thử: chỉ đọc vài cột, nén tốt).
Cassandra là kho *cột rộng*: dữ liệu gom theo khóa phân vùng, mạnh ở đọc ghi theo khóa ở quy mô lớn; quét toàn bộ để tổng hợp không phải việc nó được thiết kế cho. Nên đề xuất một hệ phân tích lưu theo cột, hoặc bảng tổng hợp sẵn.

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

```python
import os, sqlite3, duckdb                           # pip install duckdb
N = 1_000_000
for f in ("rows.sqlite", "cols.duckdb"):
    if os.path.exists(f): os.remove(f)
cities = ["Hà Nội", "Huế", "Đà Nẵng", "Cần Thơ", "Hải Phòng"]

lite = sqlite3.connect("rows.sqlite")
lite.execute("create table sales(id integer primary key, city text, shop int, year int, qty int)")
lite.executemany("insert into sales values (?, ?, ?, ?, ?)",
                 ((i, cities[i % 5], i % 50, 2026, i % 7 + 1) for i in range(1, N + 1)))
lite.commit()

duck = duckdb.connect("cols.duckdb")
duck.execute("create table sales(id integer, city varchar, shop integer, year integer, qty integer)")
duck.execute(f"""insert into sales select i, ['Hà Nội','Huế','Đà Nẵng','Cần Thơ','Hải Phòng'][i % 5 + 1],
                 i % 50, 2026, i % 7 + 1 from range(1, {N + 1}) t(i)""")
duck.execute("checkpoint")
print("cùng tổng:", duck.execute("select sum(qty) from sales").fetchone() == lite.execute("select sum(qty) from sales").fetchone())
print(duck.execute("""select column_name, any_value(compression) from pragma_storage_info('sales')
                      where segment_type <> 'VALIDITY' group by column_name order by column_name""").fetchall())
duck.close(); lite.close()
print("SQLite:", round(os.path.getsize("rows.sqlite") / 1e6, 1), "MB | DuckDB:", round(os.path.getsize("cols.duckdb") / 1e6, 1), "MB")
```

Kết quả: `cùng tổng: True`; các cột nén bằng `Dictionary` (city), `BitPacking` (id, qty, shop) và `Constant` (year); SQLite 25,4 MB, DuckDB 2,1 MB.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/types-of-databases.md): quan hệ, OLAP và bốn nhóm NoSQL.
- [Apache Cassandra — Overview](https://github.com/apache/cassandra/blob/95b178a141824a0414c4add9b5ab87eaa1ca13bf/doc/modules/cassandra/pages/architecture/overview.adoc) và [Data Definition](https://github.com/apache/cassandra/blob/95b178a141824a0414c4add9b5ab87eaa1ca13bf/doc/modules/cassandra/pages/developing/cql/ddl.adoc), tại commit cố định: mô hình cột rộng chia phân vùng, nhất quán sau cùng; khóa phân vùng và cột gom nhóm. Đọc từ bản clone của kho.

Phép thử chạy bằng Python 3.13.16, SQLite 3.45.1 và DuckDB 1.5.6 ngày 2026-10-18 trên máy biên soạn. Tài liệu của DuckDB không mở được; cách nén lấy từ chính `pragma_storage_info` của nó. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

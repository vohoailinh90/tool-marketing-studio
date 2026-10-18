# Chọn cơ sở dữ liệu theo câu hỏi bạn sẽ hỏi: tám loại và hai phép đo

**Đừng chọn cơ sở dữ liệu theo tên; hãy viết ra những câu hỏi mà ứng dụng sẽ hỏi dữ liệu nhiều nhất.** Nguồn chia tám loại: giao dịch, phân tích, tìm toàn văn, kho tài liệu, kho khóa–giá trị, đồ thị, vector nhúng và dữ liệu không gian. Mỗi loại sắp xếp dữ liệu để một kiểu câu hỏi chạy nhanh. Bài này đo hai kiểu câu hỏi để thấy khoảng cách đó lớn cỡ nào.

![Khung một, câu hỏi nhỏ và ghi nhiều: giao dịch đúng từng đồng dùng cơ sở dữ liệu quan hệ cho OLTP; lấy theo khóa thật nhanh dùng kho khóa và giá trị; bản ghi dạng JSON, dùng kho tài liệu; quan hệ chằng chịt dùng cơ sở dữ liệu đồ thị. Khung hai, câu hỏi đặc thù: tổng hợp hàng triệu dòng dùng hệ OLAP lưu theo cột; tìm theo từ trong văn bản dùng tìm toàn văn; tìm thứ gần giống nhất dùng vector nhúng; gần một vị trí hay trong một vùng dùng dữ liệu không gian. Khung ba, đo trên một máy: tìm một mã trong 200.000 ghi chú, quét cả bảng mất 37 đến 49 mili giây, chỉ mục toàn văn 0,01 đến 0,02 mili giây; tổng theo cửa hàng trên 5 triệu dòng, SQLite mất 1,9 giây, DuckDB 31 đến 33 mili giây.](../../diagrams/sd-04-032-main.svg)

## Từ viết tắt

- **OLTP** (OnLine Transaction Processing) — xử lý giao dịch trực tuyến: nhiều thao tác nhỏ trên ít dòng và phải đúng tuyệt đối, như trừ tiền một tài khoản.
- **OLAP** (OnLine Analytical Processing) — xử lý phân tích trực tuyến: câu hỏi tổng hợp trên rất nhiều dòng, như doanh thu theo cửa hàng.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm các cặp tên và giá trị, hay dùng cho bản ghi mỗi cái một kiểu.
- **FTS** (Full-Text Search) — tìm toàn văn: tìm theo từ trong văn bản bằng một chỉ mục ghi sẵn mỗi từ nằm ở đâu; FTS5 là bộ tìm toàn văn có sẵn trong SQLite.
- **GB** (GigaByte) — gigabyte: đơn vị dung lượng cỡ một tỷ byte; ở đây nói lượng bộ nhớ đoạn mã cần.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi dữ liệu; SQLite và DuckDB đều nhận câu SQL.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức để ghi và tìm lại nhanh; có trong tên DuckDB.

## Đọc hình

Hai khung đầu xếp tám loại của nguồn theo kiểu câu hỏi; cách xếp là của người biên soạn. Khung ba là phép đo chạy ngày 2026-10-18 bằng Python 3.13.16 với SQLite 3.45.1 và DuckDB 1.5.6 trên một máy; mỗi số là lần nhanh nhất trong ba lần lặp, và cả đoạn mã được chạy ba lần; khoảng dao động ghi bên dưới.

1. **Tìm theo từ.** 200.000 ghi chú, tìm ghi chú chứa mã `mã123456`. Câu `like '%mã123456%'` không dùng được chỉ mục thường vì mẫu bắt đầu bằng ký tự đại diện, nên SQLite quét cả bảng (`SCAN notes`): từ 37 đến 49 mili giây. Chỉ mục toàn văn FTS5 của SQLite ghi sẵn mỗi từ nằm ở những dòng nào: từ 0,01 đến 0,02 mili giây, cùng đáp án 1 dòng. Đây là ý tưởng của mọi hệ tìm toàn văn.
2. **Tổng hợp nhiều dòng.** 5 triệu dòng bán hàng, tính tổng tiền theo 50 cửa hàng. SQLite lưu theo dòng nên đọc cả dòng, kể cả cột ghi chú dài: khoảng 1,9 giây. DuckDB, một hệ phân tích lưu theo cột, chỉ đọc ba cột cần dùng và xử lý theo lô: từ 31 đến 33 mili giây với một luồng, cùng đáp án.

Hai phép đo không có nghĩa là SQLite chậm: hỏi một đơn theo khóa, thêm một đơn trong giao dịch là việc SQLite làm tốt. Mỗi hệ nhanh ở kiểu câu hỏi nó được sắp xếp cho.

## Giới hạn cần nhớ

Số đo là của một máy, dữ liệu sinh tự động, mỗi hệ một luồng; khoảng cách giữa SQLite và DuckDB gộp hai lý do (lưu theo cột, chạy theo lô), bài không tách riêng từng lý do. Hầu hết ứng dụng có nhiều kiểu câu hỏi cùng lúc; thêm một hệ là thêm việc vận hành và việc đồng bộ dữ liệu giữa hai nơi. Bắt đầu bằng một hệ chính, và chỉ thêm hệ thứ hai khi một kiểu câu hỏi đo được là quá chậm.

## Nhìn hình thử trả lời

Một ứng dụng đặt phòng khách sạn có ba nhu cầu: giữ phòng và trừ tiền không được sai, cho khách tìm "khách sạn gần biển có hồ bơi" theo lời mô tả, và báo cáo doanh thu theo tháng cho quản lý. Mỗi nhu cầu thuộc loại nào trong hình, và bạn có cần ba hệ riêng ngay từ đầu không?

<details>
<summary>Xem đáp án</summary>

Giữ phòng và trừ tiền: giao dịch (OLTP), cơ sở dữ liệu quan hệ. Tìm theo lời mô tả: tìm toàn văn (thêm dữ liệu không gian nếu lọc theo khoảng cách tới biển). Báo cáo theo tháng: phân tích (OLAP).
Không nhất thiết cần ba hệ ngay: một cơ sở dữ liệu quan hệ có chỉ mục toàn văn và đủ nhanh cho báo cáo lúc dữ liệu còn nhỏ. Tách ra khi đo thấy một kiểu câu hỏi chậm, như phép đo tổng hợp 5 triệu dòng ở trên.

</details>

<details>
<summary>Xem sâu hơn: mã phép đo</summary>

```python
import random, sqlite3, time
import duckdb                                   # pip install duckdb

def best_ms(f, n=3):
    times = []
    for _ in range(n):
        t = time.perf_counter(); out = f(); times.append(time.perf_counter() - t)
    return out, round(min(times) * 1000, 3)

# 1. Tìm theo từ: quét LIKE so với chỉ mục toàn văn FTS5 (200.000 ghi chú)
random.seed(32)
words = ["đơn", "hàng", "giao", "chậm", "nhanh", "lỗi", "thanh", "toán", "kho", "trả", "đổi", "mới", "cũ", "giá", "rẻ"]
db = sqlite3.connect(":memory:")
db.execute("create table notes(id integer primary key, body text)")
db.executemany("insert into notes values (?, ?)",
               ((i, " ".join(random.choices(words, k=12)) + f" mã{i}") for i in range(1, 200_001)))
db.execute("create virtual table notes_fts using fts5(body, content='notes', content_rowid='id')")
db.execute("insert into notes_fts(notes_fts) values ('rebuild')")
print("like:", best_ms(lambda: db.execute("select count(*) from notes where body like '%mã123456%'").fetchone()))
print("fts5:", best_ms(lambda: db.execute("select count(*) from notes_fts where notes_fts match 'mã123456'").fetchone()))

# 2. Tổng hợp 5 triệu dòng: SQLite (lưu theo dòng) so với DuckDB (lưu theo cột), một luồng
N = 5_000_000
db.execute("create table sales(id integer primary key, shop int, product int, qty int, price int, note text)")
db.executemany("insert into sales values (?, ?, ?, ?, ?, ?)",
               ((i, i % 50, i % 1000, i % 7 + 1, i % 500 + 10, f"ghi chú dài cho đơn hàng số {i}") for i in range(1, N + 1)))
duck = duckdb.connect()
duck.execute("set threads = 1")
duck.execute(f"""create table sales as select i as id, i % 50 as shop, i % 1000 as product, i % 7 + 1 as qty,
                 i % 500 + 10 as price, 'ghi chú dài cho đơn hàng số ' || i as note from range(1, {N + 1}) t(i)""")
q = "select shop, sum(qty * price) from sales group by shop order by shop"
a, ta = best_ms(lambda: db.execute(q).fetchall())
b, tb = best_ms(lambda: duck.execute(q).fetchall())
print("cùng đáp án:", a == b, a[:2], f"SQLite {ta:.0f} ms, DuckDB {tb:.0f} ms")
```

Đoạn mã cần gần 1 GB bộ nhớ và chạy chừng 20 giây, phần lớn là để nạp 5 triệu dòng vào SQLite. Hai cửa hàng đầu có tổng 93.998.750 và 94.400.750 ở cả hai hệ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-choose-the-right-database.md): tám loại cơ sở dữ liệu và việc mỗi loại hợp với.

Phép đo chạy bằng Python 3.13.16, SQLite 3.45.1 và DuckDB 1.5.6 ngày 2026-10-18 trên máy biên soạn (4 nhân). Trang tài liệu của SQLite và DuckDB không mở được; việc FTS5 và DuckDB hoạt động thế nào được mô tả theo kiến thức chung của người biên soạn và theo kế hoạch truy vấn quan sát được. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

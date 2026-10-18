# Bảng tra hiệu năng cơ sở dữ liệu: đo ba mục trước khi tin cả mười

**Mỗi mục trong một bảng tra hiệu năng là một đánh đổi có cỡ đo được; đo vài mục trên chính máy của bạn có ích hơn học thuộc cả danh sách.** Nguồn liệt kê mười mục: chỉ mục, tối ưu truy vấn, dùng lại kết nối, bộ đệm, shard, bản sao, phần cứng, theo dõi, chuẩn hóa và phi chuẩn hóa, phân vùng. Bài này nhóm chúng theo chỗ tác động và đo ba mục dễ đo nhất trên PostgreSQL 16: giá của một kết nối mới, giá của mỗi chỉ mục khi ghi, và cái lợi của việc chỉ lấy cột cần.

![Bốn khung dọc. Khung một, mười mục của nguồn nhóm theo chỗ tác động: câu hỏi gồm chỉ mục, tối ưu truy vấn, chuẩn hóa hay phi chuẩn hóa; kết nối và bộ đệm gồm dùng lại kết nối và đệm kết quả; chia dữ liệu gồm phân vùng, shard và bản sao; máy và theo dõi gồm bộ nhớ, đĩa, CPU và đo thời gian trả lời. Khung hai, đo kết nối: mở kết nối mới cho mỗi câu mất 3,3 đến 4,1 mili giây, dùng lại một kết nối dưới 0,09 mili giây. Khung ba, chỉ mục làm chậm ghi, chèn 200.000 dòng: chỉ khóa chính 0,7 đến 0,9 giây, thêm 3 chỉ mục 1,3 đến 1,7 giây, thêm 6 chỉ mục 2,9 đến 4,2 giây. Khung bốn, chỉ lấy cột cần: select sao đọc 202 trang, chỉ hai cột có trong chỉ mục thì đọc 5 trang và không chạm bảng.](../../diagrams/sd-04-043-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần chip chạy lệnh của máy; một trong những thứ cần theo dõi khi cơ sở dữ liệu chậm.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: cách hai máy gửi dữ liệu cho nhau qua mạng; mỗi kết nối mới phải bắt tay trước khi gửi câu hỏi đầu tiên.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu; `EXPLAIN` là lệnh SQL cho xem kế hoạch chạy.

## Đọc hình

Phép đo chạy ba lần ngày 2026-10-18 trên PostgreSQL 16.15 và Python 3.13.16, kết nối qua TCP tới cùng máy; hình ghi khoảng dao động giữa ba lần. Mã ở phần "Xem sâu hơn".

1. **Mười mục, bốn nhóm.** Nhóm câu hỏi (chỉ mục, tối ưu truy vấn với `EXPLAIN`, chuẩn hóa hay phi chuẩn hóa), nhóm kết nối và bộ đệm, nhóm chia dữ liệu (phân vùng, shard, bản sao), nhóm máy và theo dõi. Nhóm đầu rẻ nhất để thử; nhóm chia dữ liệu đắt nhất để quay lại.
2. **Mở kết nối.** Mở một kết nối mới cho mỗi câu `select 1` tốn 3,3 đến 4,1 mili giây mỗi câu; dùng lại một kết nối, cùng câu đó tốn dưới 0,09 mili giây. Gần như toàn bộ thời gian là bắt tay, xác thực và dựng tiến trình phục vụ cho kết nối, không phải chạy câu hỏi. Đó là lý do có bộ gom kết nối: giữ sẵn một nhóm kết nối và cho các yêu cầu mượn.
3. **Chỉ mục làm chậm ghi.** Chèn 200.000 dòng vào bảng chỉ có khóa chính mất 0,7 đến 0,9 giây; thêm 3 chỉ mục, 1,3 đến 1,7 giây; thêm 6 chỉ mục, 2,9 đến 4,2 giây. Mỗi chỉ mục là thêm một cấu trúc phải cập nhật cho mỗi dòng ghi vào, nên chỉ mục không ai dùng là chi phí thuần.
4. **Chỉ lấy cột cần.** `select * from t where a = 42` (200 dòng) phải đọc 202 trang: tìm trong chỉ mục rồi đọc từng dòng trong bảng. `select a, f` với chỉ mục trên `a` có kèm sẵn cột `f` (`include (f)`) được PostgreSQL trả lời chỉ từ chỉ mục (`Index Only Scan`): 5 trang, không chạm bảng. Bỏ `select *` không chỉ bớt dữ liệu gửi đi mà còn mở đường cho cách chạy này.

## Giới hạn cần nhớ

Số đo là của một máy, kết nối qua TCP tới chính nó: kết nối tới máy khác qua mạng thật, có mã hóa, còn đắt hơn. Thời gian chèn phụ thuộc kiểu cột của chỉ mục (hai chỉ mục ở đây là trên chuỗi băm dài) và máy có ghi nhật ký sang bản sao hay không. Quét chỉ từ chỉ mục chỉ bỏ qua được bảng khi bản đồ hiển thị của bảng (một bit cho mỗi trang, đánh dấu trang mà mọi dòng đều đã thấy được với mọi người) còn mới; phép thử đã chạy `vacuum` trước khi đo, bảng vừa ghi nhiều thì lợi ích nhỏ hơn. Bảy mục còn lại của nguồn không được đo ở đây.

## Nhìn hình thử trả lời

Một hàm chạy trên nền tảng serverless mở kết nối mới tới PostgreSQL ở mỗi lần được gọi, và chạy đúng một câu truy vấn nhanh. Người dùng thấy mỗi lần gọi chậm hơn mong đợi khoảng vài mili giây. Theo phép đo, phần lớn thời gian đi đâu, và sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Đi vào việc mở kết nối: trong phép đo, kết nối mới cho mỗi câu tốn 3,3 đến 4,1 mili giây, còn chính câu truy vấn trên một kết nối có sẵn tốn dưới 0,09 mili giây. Qua mạng thật có mã hóa thì còn nhiều hơn.
Sửa bằng cách giữ kết nối qua các lần gọi khi nền tảng cho phép, hoặc đặt một bộ gom kết nối đứng giữa hàm và cơ sở dữ liệu để hàm mượn kết nối có sẵn thay vì tự mở.

</details>

<details>
<summary>Xem sâu hơn: mã phép đo</summary>

Cần một cơ sở dữ liệu thử `lab043` trên PostgreSQL, nhận kết nối qua `localhost`.

```python
import time, psycopg                                        # pip install "psycopg[binary]"
DSN = "host=localhost port=5433 user=postgres dbname=lab043"   # qua TCP, như ứng dụng ở máy khác
ms = lambda t: (time.perf_counter() - t) * 1000

# 1. Mở kết nối mới cho mỗi câu hỏi so với dùng lại một kết nối
t = time.perf_counter()
for _ in range(200):
    with psycopg.connect(DSN) as c:
        c.execute("select 1").fetchone()
print(f"kết nối mới mỗi lần: {ms(t) / 200:.2f} ms/câu")
with psycopg.connect(DSN) as c:
    t = time.perf_counter()
    for _ in range(200):
        c.execute("select 1").fetchone()
    print(f"dùng lại một kết nối: {ms(t) / 200:.3f} ms/câu")

# 2. Mỗi chỉ mục thêm việc cho mỗi lần ghi
with psycopg.connect(DSN, autocommit=True) as c:
    for n in (0, 3, 6):
        c.execute("drop table if exists t")
        c.execute("create table t(id int primary key, a int, b int, c int, d text, e text, f int)")
        for col in ["a", "b", "c", "d", "e", "f"][:n]:
            c.execute(f"create index on t({col})")
        t = time.perf_counter()
        c.execute("""insert into t select g, g % 1000, g % 77, g % 13, md5(g::text), md5((g * 7)::text), g % 5
                     from generate_series(1, 200000) g""")
        print(f"chèn 200.000 dòng, khóa chính + {n} chỉ mục: {ms(t):.0f} ms")

# 3. Chỉ lấy cột cần: chỉ mục 'bao phủ' trả lời mà không đọc bảng
with psycopg.connect(DSN, autocommit=True) as c:
    c.execute("create index t_a_cover on t(a) include (f)")
    c.execute("vacuum analyze t")
    for q in ("select * from t where a = 42", "select a, f from t where a = 42"):
        plan = [r[0] for r in c.execute("explain (analyze, buffers, costs off, timing off) " + q)]
        print(q, "->", plan[0].strip(), "|", next(p.strip() for p in plan if "Buffers" in p))
```

Kết quả ba lần chạy: 3,49, 3,30 và 4,08 mili giây mỗi câu với kết nối mới, 0,089, 0,075 và 0,084 với một kết nối; chèn 848, 747 và 869 mili giây (0 chỉ mục thêm), 1.677, 1.347 và 1.743 (3), 3.173, 2.892 và 4.160 (6); `Bitmap Heap Scan` đọc 202 trang, `Index Only Scan` đọc 5 trang.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-cheatsheet-on-database-performance.md): mười mục của bảng tra.
- [PostgreSQL 16 — Index-Only Scans and Covering Indexes](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/indices.sgml), tại commit cố định của nhánh `REL_16_STABLE`: chỉ mục kèm cột bằng `include`, quét chỉ mục mà không đọc bảng khi bản đồ hiển thị cho phép. Đọc từ bản clone của kho.

Phép đo chạy trên PostgreSQL 16.15, Python 3.13.16 và psycopg 3.3.6 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

# Bảy cách mở rộng cơ sở dữ liệu: thử theo thứ tự rẻ trước, đắt sau

**Bảy cách mở rộng cơ sở dữ liệu không ngang hàng: vài cách sửa được trong một buổi chiều trên chính máy đang chạy, vài cách đổi cả kiến trúc; và cách nào nhanh hơn cũng trả bằng dữ liệu cũ hơn hoặc thêm việc vận hành.** Nguồn liệt kê: chỉ mục, materialized view, phi chuẩn hóa, mở rộng theo chiều dọc (máy to hơn), bộ đệm, bản sao và shard. Bài này xếp chúng từ rẻ tới đắt, rồi đo hai cách ở giữa trên PostgreSQL 16 và Redis: materialized view và bộ đệm. Hai cách đó nhanh hơn hàng trăm lần, và cả hai đều trả về số cũ trong một khoảng thời gian.

![Khung một và hai, bảy cách xếp từ rẻ tới đắt: trên cùng một máy có chỉ mục theo đúng câu hỏi hay chạy, materialized view tính sẵn kết quả nặng, phi chuẩn hóa để bớt phép nối, bộ đệm đặt dữ liệu hay đọc ở tầng nhanh hơn; đắt hơn là máy to hơn, bản sao để chia lượt đọc, shard để chia cả lượt ghi. Khung ba, materialized view trên 2 triệu dòng: tính trực tiếp 102 đến 107 mili giây, đọc view dưới 1,3 mili giây; sau một đơn mới view vẫn nói số cũ cho tới khi làm mới, mất 98 đến 125 mili giây. Khung bốn, bộ đệm Redis hạn 2 giây: lần đầu hỏi cơ sở dữ liệu 40 đến 54 mili giây, lần hai dưới 0,3 mili giây; ngay sau đơn mới bộ đệm vẫn trả số cũ, hết hạn mới đúng.](../../diagrams/sd-04-047-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: chip chạy lệnh của máy; mở rộng theo chiều dọc là thêm CPU, bộ nhớ hay đĩa cho máy đang có.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ dùng nó.

## Đọc hình

1. **Rẻ: trên cùng một máy.** Chỉ mục đúng với câu hỏi hay chạy thường là việc đầu tiên nên thử. Materialized view lưu sẵn kết quả của một câu hỏi nặng như một bảng. Phi chuẩn hóa chấp nhận lưu lặp một ít để bớt phép nối. Bộ đệm giữ dữ liệu hay đọc ở một tầng nhanh hơn, thường là bộ nhớ của một hệ như Redis.
2. **Đắt hơn: thêm sức hoặc thêm máy.** Máy to hơn không đổi mã nhưng có trần, và tốn tiền tăng nhanh hơn sức. Bản sao chia lượt đọc nhưng đọc có thể cũ (xem bài [bản sao chỉ đọc](../sd-04-035/lesson.md)). Shard chia cả lượt ghi nhưng làm mọi câu hỏi, phép gộp và giao dịch phức tạp hơn (xem bài [nhập môn sharding](../sd-04-036/lesson.md)). Thứ tự này là của người biên soạn; nguồn đặt máy to hơn trước bộ đệm.
3. **Đo materialized view.** Phép đo chạy ba lần ngày 2026-10-18 trên PostgreSQL 16.15, bảng 2 triệu đơn của 50 cửa hàng. Tính tổng tiền theo cửa hàng trực tiếp mất 102 đến 107 mili giây; đọc view đã tính sẵn mất dưới 1,3 mili giây. Thêm một đơn 1.000 cho cửa hàng 0: bảng nói 1.920.950, view vẫn nói 1.919.950 cho tới khi làm mới bằng `refresh materialized view`, mất 98 đến 125 mili giây, gần bằng tính lại từ đầu.
4. **Đo bộ đệm.** Hàm `shop_total` kiểu "bộ đệm đặt bên cạnh": hỏi Redis trước; không có thì hỏi PostgreSQL rồi cất vào Redis với hạn 2 giây. Lần đầu mất 40 đến 54 mili giây (hỏi cơ sở dữ liệu), lần hai dưới 0,3 mili giây (từ bộ đệm). Thêm một đơn 5.000 cho cửa hàng 7: hàm vẫn trả số cũ từ bộ đệm; hết hạn 2 giây mới ra số mới, lớn hơn đúng 5.000.

## Giới hạn cần nhớ

Số đo là của một máy, bảng sinh tự động, cơ sở dữ liệu và Redis cùng chạy trên máy đó; qua mạng, mỗi lần hỏi còn cộng thêm một vòng mạng. Bài không đo phi chuẩn hóa, máy to hơn, bản sao hay shard ở đây (các bài khác của nhóm này có phép thử cho bản sao và shard). Làm mới materialized view thường gần đắt bằng tính lại từ đầu, nên chỉ có lợi khi báo cáo được đọc nhiều hơn hẳn số lần làm mới. Hạn của bộ đệm là quyết định về sản phẩm: người dùng chấp nhận số cũ bao lâu.

## Nhìn hình thử trả lời

Trang tổng quan của quản lý chạy một câu tổng hợp mất vài giây, được mở hàng trăm lần mỗi giờ, và số liệu chậm 10 phút là chấp nhận được. Nhóm định mua máy cơ sở dữ liệu to gấp đôi. Theo thứ tự trong hình, nên thử gì trước, và cái giá là gì?

<details>
<summary>Xem đáp án</summary>

Thử những cách rẻ trước: xem `EXPLAIN` có thiếu chỉ mục không, rồi tính sẵn kết quả bằng materialized view làm mới mỗi 10 phút, hoặc đặt kết quả vào bộ đệm với hạn 10 phút. Như phép đo, đọc kết quả tính sẵn nhanh hơn hàng trăm lần so với tính lại, và mỗi giờ chỉ phải tính lại 6 lần thay vì hàng trăm.
Cái giá: số liệu trên trang có thể cũ tới 10 phút, đúng như view và bộ đệm trong phép đo trả số cũ cho tới khi làm mới hoặc hết hạn; và phải có tác vụ làm mới chạy đều. Máy to hơn chỉ cần khi những cách này không đủ.

</details>

<details>
<summary>Xem sâu hơn: mã phép đo</summary>

Cần một cơ sở dữ liệu thử `lab047` trên PostgreSQL và một Redis ở cổng 6393.

```python
import json, time, psycopg, redis              # pip install "psycopg[binary]" redis; cần PostgreSQL và Redis
db = psycopg.connect("host=/tmp/pglab port=5433 user=postgres dbname=lab047", autocommit=True)
cache = redis.Redis(port=6393, decode_responses=True)
ms = lambda t: (time.perf_counter() - t) * 1000
db.execute("drop materialized view if exists sales_by_shop"); db.execute("drop table if exists sales")
db.execute("create table sales(id serial primary key, shop int, amount int)")
db.execute("insert into sales(shop, amount) select g % 50, g % 97 from generate_series(1, 2000000) g")
db.execute("analyze sales")
REPORT = "select shop, sum(amount) from sales group by shop order by shop"

# 1. Materialized view: tính sẵn báo cáo, đọc ngay, nhưng cũ cho tới lần làm mới
t = time.perf_counter(); live = db.execute(REPORT).fetchall(); print(f"báo cáo tính trực tiếp: {ms(t):.0f} ms")
db.execute("create materialized view sales_by_shop as " + REPORT)
t = time.perf_counter(); db.execute("select * from sales_by_shop").fetchall(); print(f"đọc materialized view: {ms(t):.2f} ms")
db.execute("insert into sales(shop, amount) values (0, 1000)")
old = db.execute("select sum from sales_by_shop where shop = 0").fetchone()[0]
new = db.execute("select sum(amount) from sales where shop = 0").fetchone()[0]
print("sau một đơn mới của cửa hàng 0: view nói", old, "| bảng nói", new)
t = time.perf_counter(); db.execute("refresh materialized view sales_by_shop"); print(f"làm mới view: {ms(t):.0f} ms")

# 2. Bộ đệm đặt bên cạnh (cache-aside) với hạn 2 giây
def shop_total(shop):
    key = f"total:{shop}"
    if (hit := cache.get(key)) is not None:
        return int(hit), "bộ đệm"
    value = db.execute("select sum(amount) from sales where shop = %s", (shop,)).fetchone()[0]
    cache.set(key, value, ex=2)                                     # hết hạn sau 2 giây
    return value, "cơ sở dữ liệu"
cache.delete("total:7")
for label in ("lần 1", "lần 2"):
    t = time.perf_counter(); v, src = shop_total(7); print(f"{label}: {v} từ {src}, {ms(t):.2f} ms")
db.execute("insert into sales(shop, amount) values (7, 5000)")
print("ngay sau đơn mới:", shop_total(7))
time.sleep(2.1)
print("sau khi hết hạn:", shop_total(7))
```

Kết quả ba lần chạy: 107, 102 và 106 mili giây tính trực tiếp, 1,23, 0,70 và 0,47 mili giây đọc view; view nói 1.919.950 khi bảng nói 1.920.950; làm mới 99, 125 và 98 mili giây; bộ đệm: 43,46, 53,54 và 40,03 mili giây lần đầu, 0,22, 0,17 và 0,15 mili giây lần hai; ngay sau đơn mới vẫn 1.919.954 từ bộ đệm, hết hạn thì 1.924.954 từ cơ sở dữ liệu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/7-must-know-strategies-to-scale-your-database.md): bảy cách mở rộng cơ sở dữ liệu.
- [PostgreSQL 16 — Materialized Views](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/rules.sgml), tại commit cố định của nhánh `REL_16_STABLE`: view lưu kết quả như một bảng, không tự cập nhật, làm mới bằng `REFRESH MATERIALIZED VIEW`. Đọc từ bản clone của kho.

Phép đo chạy trên PostgreSQL 16.15, Redis 7.0.15, Python 3.13.16, psycopg 3.3.6 và redis-py 8.1.0 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

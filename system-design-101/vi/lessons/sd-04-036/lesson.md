# Nhập môn sharding: chia xong rồi, câu hỏi nào đổi?

**Chia shard là chia một bảng lớn ra nhiều máy; cái giá thật không nằm ở lúc chia mà ở mọi câu hỏi sau đó.** Nguồn giải thích vì sao chia (quá nhiều dữ liệu, quá nhiều yêu cầu cho một máy), khóa shard, ba thuật toán (theo dải, theo băm, tra bảng), ba chỗ đặt logic (ứng dụng, lớp trung gian, cơ sở dữ liệu) và bốn khó khăn. Bài này mô phỏng 4 shard để thấy cụ thể ba khó khăn: câu hỏi không có khóa shard, gộp kết quả, và giao dịch qua hai shard. Cách các thuật toán dời dữ liệu khi thêm shard có ở bài [Bốn cách chia dữ liệu vào shard](../sd-04-025/lesson.md).

![Ba khung dọc. Khung một, ba chỗ đặt logic chia shard: ứng dụng tự chọn shard cho từng câu lệnh; một lớp trung gian đứng giữa ứng dụng và các shard; hoặc chính cơ sở dữ liệu tự chia. Khung hai, đo trên 4 shard với 10.000 đơn, khóa shard là mã khách: hỏi đơn của một khách chỉ cần 1 shard; hỏi đơn có một sản phẩm phải hỏi cả 4 shard rồi gộp; một khách mua rất nhiều làm một shard giữ 3.994 đơn, gần gấp đôi các shard khác. Khung ba, hai cái bẫy: lấy trung bình của 4 giá trị trung bình được 43,74 trong khi trung bình đúng là 40,54; chuyển tiền giữa hai shard mà tiến trình chết giữa chừng thì tổng tiền hụt 30.](../../diagrams/sd-04-036-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu; mỗi shard trong phép thử là một cơ sở dữ liệu SQLite riêng.

## Đọc hình

Phép thử chạy bằng Python 3.13.16 với SQLite 3.45.1 ngày 2026-10-18: 4 shard, mỗi shard một cơ sở dữ liệu trong bộ nhớ, 10.000 đơn của 1.000 khách, khóa shard là mã khách (shard = mã khách chia lấy dư cho 4). Một khách (số 7) đặt một phần năm số đơn, toàn món nhỏ. Mã ở phần "Xem sâu hơn".

1. **Ba chỗ đặt logic.** Ứng dụng tự biết shard nào giữ khách nào; hoặc một lớp trung gian đứng giữa làm việc đó; hoặc chính cơ sở dữ liệu tự chia và ứng dụng chỉ thấy một bảng. Phép thử đặt logic trong ứng dụng: hàm `run` nhận mã khách thì hỏi đúng một shard, không có thì hỏi cả bốn rồi gộp.
2. **Câu hỏi có khóa shard và không có.** "Đơn của khách 42" chạm 1 shard. "Đơn có sản phẩm `sp9`" chạm cả 4: không có cách nào biết trước shard nào có. Chọn khóa shard là chọn câu hỏi nào sẽ rẻ.
3. **Shard lệch.** Khách số 7 đặt 2.000 đơn, nên shard của nó giữ 3.994 đơn, các shard khác khoảng 2.000. Băm đều mã khách không cứu được khi một khách lớn hơn hẳn.
4. **Gộp kết quả.** Mỗi shard tính được trung bình của mình, nhưng trung bình của bốn trung bình là 43,74, còn trung bình đúng của mọi đơn là 40,54: shard đông đơn món nhỏ bị tính ngang với shard khác. Phải gộp tổng và số đếm của từng shard rồi mới chia.
5. **Giao dịch qua hai shard.** Chuyển 30 từ khách 1 (shard 1) sang khách 2 (shard 2) là hai lần ghi ở hai cơ sở dữ liệu. Tiến trình chết sau lần ghi thứ nhất: tổng tiền của hệ từ 100.000 còn 99.970. Muốn hai lần ghi cùng xong hoặc cùng không, cần một giao dịch phân tán, chẳng hạn cam kết hai pha; PostgreSQL có lệnh `PREPARE TRANSACTION` cho việc này, dành cho một bộ quản lý giao dịch bên ngoài chứ không cho ứng dụng gọi thẳng.

## Giới hạn cần nhớ

Mô phỏng chạy trong một tiến trình, không có mạng, nên không thấy độ trễ của việc hỏi bốn máy hay máy chậm nhất quyết định thời gian trả lời. Ví dụ "chết giữa chừng" được dựng bằng cách dừng sau lần ghi đầu, không phải sự cố thật. Chia lại shard sau khi đã chạy (nguồn gọi là resharding) không được thử ở đây. Trước khi chia, hãy hỏi đã thử bản sao chỉ đọc, chỉ mục và bộ đệm chưa: chia shard thêm cả ba khó khăn trên vào mọi tính năng về sau.

## Nhìn hình thử trả lời

Một ứng dụng nhắn tin chia bảng `messages` theo mã người gửi. Câu hỏi hay chạy nhất là "mở một cuộc trò chuyện giữa An và Bình, xem 50 tin gần nhất". Câu đó chạm mấy shard, và nên chọn khóa shard khác không?

<details>
<summary>Xem đáp án</summary>

Tin của An nằm ở shard của An, tin của Bình ở shard của Bình. Câu hỏi chạm 1 shard nếu hai người tình cờ cùng shard, 2 shard nếu khác (với nhiều shard, khác là chuyện thường); khi chạm 2 thì phải gộp và sắp xếp lại theo thời gian để lấy 50 tin mới nhất (mỗi shard phải trả đủ 50 tin của mình, không phải 25).
Chia theo mã cuộc trò chuyện thì mọi tin của một cuộc nằm chung một shard: câu hỏi hay chạy nhất chỉ chạm 1 shard. Đổi lại, "mọi tin An đã gửi" sẽ phải hỏi nhiều shard.

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

```python
import random, sqlite3
random.seed(36)
N = 4
shards = [sqlite3.connect(":memory:") for _ in range(N)]
for db in shards:
    db.execute("create table orders(id integer primary key, customer int, product text, amount int)")
    db.execute("create table wallets(customer int primary key, balance int)")
shard_of = lambda customer: customer % N                     # khóa shard: mã khách
touched = []
def run(sql, args=(), customer=None):
    """Có khóa shard thì hỏi đúng một shard; không có thì hỏi mọi shard rồi gộp."""
    targets = [shard_of(customer)] if customer is not None else range(N)
    touched.append(len(targets))
    return [row for s in targets for row in shards[s].execute(sql, args).fetchall()]

# 10.000 đơn, khách 1..1.000; khách số 7 mua rất nhiều món nhỏ, nên shard của nó lệch hẳn
for i in range(1, 10_001):
    c = 7 if i % 5 == 0 else random.randint(1, 1000)
    shards[shard_of(c)].execute("insert into orders values (?, ?, ?, ?)",
        (i, c, f"sp{random.randint(1, 50)}", random.randint(1, 10) if c == 7 else random.randint(1, 100)))
for c in range(1, 1001):
    shards[shard_of(c)].execute("insert into wallets values (?, 100)", (c,))

run("select count(*) from orders where customer = ?", (42,), customer=42)
run("select count(*) from orders where product = ?", ("sp9",))
print("số shard phải hỏi: theo khách", touched[0], "| theo sản phẩm", touched[1])

# Gộp kết quả: trung bình của các trung bình không phải trung bình
per_shard = run("select count(*), sum(amount), avg(amount) from orders")
true_avg = sum(s for _, s, _ in per_shard) / sum(c for c, _, _ in per_shard)
naive = sum(a for _, _, a in per_shard) / N
print("số đơn mỗi shard", [c for c, _, _ in per_shard], "| trung bình đúng", round(true_avg, 3),
      "| trung bình các trung bình", round(naive, 3))

# Chuyển 30 từ khách 1 (shard 1) sang khách 2 (shard 2): hai lần ghi ở hai shard, không có giao dịch chung
total = lambda: sum(b for (b,) in run("select sum(balance) from wallets"))
print("tổng tiền trước", total())
shards[shard_of(1)].execute("update wallets set balance = balance - 30 where customer = 1"); shards[shard_of(1)].commit()
# ... tiến trình chết ở đây, trước khi kịp ghi vào shard của khách 2
print("tổng tiền nếu chết giữa chừng", total())
```

Kết quả: hỏi 1 shard và 4 shard; số đơn mỗi shard `[2051, 2023, 1932, 3994]`; trung bình đúng 40,536, trung bình các trung bình 43,738; tổng tiền 100.000 rồi 99.970.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-crash-course-in-database-sharding.md): định nghĩa, lý do chia, khóa và thuật toán chia, ba cách đặt logic, bốn khó khăn (phức tạp hơn, phân bố dữ liệu, phép nối và giao dịch qua shard, chia lại).
- [PostgreSQL 16 — PREPARE TRANSACTION](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/ref/prepare_transaction.sgml), tại commit cố định của nhánh `REL_16_STABLE`: chuẩn bị giao dịch cho cam kết hai pha, dành cho bộ quản lý giao dịch bên ngoài. Đọc từ bản clone của kho.

Phép thử chạy bằng Python 3.13.16 và SQLite 3.45.1 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

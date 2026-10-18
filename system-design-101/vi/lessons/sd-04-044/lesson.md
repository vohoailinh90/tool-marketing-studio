# ACID là gì? Thử từng chữ trên PostgreSQL

**Mỗi chữ của ACID là một lời hứa có điều kiện, và cách chắc nhất để hiểu nó là thử phá nó.** Nguồn định nghĩa bốn chữ: nguyên tử (làm trọn hoặc không làm), nhất quán (giữ đúng các luật của dữ liệu, khác chữ "nhất quán" của CAP), cô lập (giao dịch chạy cùng lúc không lẫn vào nhau, chặt nhất là tuần tự hóa) và bền vững (đã chốt thì không mất dù máy hỏng). Bài này dựng hai tài khoản 100 đồng trên PostgreSQL 16 và thử từng lời hứa, kể cả lúc nó không được giữ.

![Bốn khung dọc. Khung A, nguyên tử: chuyển 150 khi tài khoản chỉ có 100, lệnh cộng đã chạy nhưng lệnh trừ lỗi, cả giao dịch bị hủy và hai tài khoản vẫn 100 và 100. Khung C, nhất quán: ràng buộc số dư không âm chặn lệnh trừ quá tay; nhất quán ở đây là giữ đúng luật của dữ liệu, khác chữ C của CAP. Khung I, cô lập: ở read committed đọc lại thấy 100 rồi 50; ở repeatable read đọc lại vẫn 100; rút 10 và rút 20 cùng lúc từ 100, read committed còn 80, mất một lượt rút; repeatable read hủy lượt sau, phải chạy lại. Khung D, bền vững: chốt 2.000 dòng rồi tắt máy chủ đột ngột, còn đủ 2.000; nếu tắt việc chờ ghi đĩa khi chốt thì chỉ còn từ 1.928 đến 1.974 dòng qua ba lần thử.](../../diagrams/sd-04-044-main.svg)

## Từ viết tắt

- **ACID** (Atomicity, Consistency, Isolation, Durability) — nguyên tử, nhất quán, cô lập, bền vững: bốn tính chất của một giao dịch đáng tin cậy.
- **CAP** (Consistency, Availability, Partition) — nhất quán, sẵn sàng, phân vùng: định lý về hệ phân tán; chữ C của nó nghĩa là mọi lượt đọc thấy lần ghi mới nhất, khác chữ C của ACID.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ dùng nó.
- **WAL** (Write-Ahead Log) — nhật ký ghi trước: PostgreSQL ghi thay đổi vào nhật ký này và đẩy xuống đĩa trước khi báo đã chốt; khi khởi động lại sau sự cố, nó đọc nhật ký để dựng lại dữ liệu.

## Đọc hình

Phép thử chạy ngày 2026-10-18 trên PostgreSQL 16.15; mã ở phần "Xem sâu hơn". Bảng `accounts` có ràng buộc `check (balance >= 0)`.

1. **A, nguyên tử.** Chuyển 150 từ tài khoản 1 (có 100) sang tài khoản 2 trong một giao dịch: lệnh cộng 150 vào tài khoản 2 chạy xong, lệnh trừ tài khoản 1 bị từ chối. Cả giao dịch bị hủy, kể cả lệnh cộng đã chạy: hai tài khoản vẫn 100 và 100.
2. **C, nhất quán.** Điều chặn lệnh trừ là ràng buộc `check`: `new row for relation "accounts" violates check constraint`. Cơ sở dữ liệu chỉ giữ được những luật bạn khai báo cho nó; luật nằm trong mã ứng dụng thì nó không biết.
3. **I, cô lập.** Ở mức mặc định `read committed`, giao dịch A đọc số dư 100, B sửa thành 50 và chốt, A đọc lại thấy 50: hai lần đọc trong cùng giao dịch khác nhau. Ở `repeatable read`, A đọc lại vẫn 100. Nguy hiểm hơn là mất cập nhật: A và B cùng đọc 100, A ghi 100 trừ 10, B ghi 100 trừ 20. Ở `read committed` cả hai ghi được và số dư thành 80, lượt rút 10 biến mất. Ở `repeatable read`, B bị hủy với `could not serialize access due to concurrent update`, số dư 90, và ứng dụng phải chạy lại lượt rút của B.
4. **D, bền vững.** Một cụm thử khác chốt 2.000 giao dịch, mỗi giao dịch một dòng, rồi bị tắt đột ngột (`pg_ctl stop -m immediate`, tài liệu nói chế độ này dừng mọi tiến trình mà không tắt sạch, nên lần khởi động sau phải phục hồi). Khởi động lại: đủ 2.000 dòng, nhờ WAL. Đặt `synchronous_commit = off` (chốt mà không chờ WAL xuống đĩa) rồi làm lại: ba lần thử còn 1.928, 1.974 và 1.946 dòng. Các giao dịch đã được báo là chốt vẫn mất: tài liệu PostgreSQL gọi đây là chốt không đồng bộ, nhanh hơn nhưng có thể mất các giao dịch gần nhất khi máy hỏng.

## Giới hạn cần nhớ

Mức cô lập mặc định của PostgreSQL là `read committed`, không phải mức chặt nhất; mỗi hệ có mặc định riêng. Mức chặt hơn đổi lỗi âm thầm lấy lỗi phải xử lý: ứng dụng phải chạy lại giao dịch bị hủy. "Bền vững" ở đây là trên một máy và một đĩa; như nguồn nói, trong hệ phân tán bền vững còn cần chép dữ liệu sang máy khác, vì đĩa của một máy cũng có thể hỏng. Phép thử dùng hai phiên và một kiểu tắt đột ngột, không phải mất điện thật.

## Nhìn hình thử trả lời

Một ứng dụng ví điện tử rút tiền bằng hai bước: `select balance` để kiểm, rồi `update accounts set balance = <số vừa đọc trừ số rút>`. Nó chạy ở mức mặc định của PostgreSQL. Khi một người bấm rút hai lần thật nhanh, chuyện gì có thể xảy ra, và có những cách sửa nào?

<details>
<summary>Xem đáp án</summary>

Mất cập nhật, như phép thử ở `read committed`: hai lượt cùng đọc 100, mỗi lượt ghi số của mình, lượt ghi sau đè lượt trước. Người dùng rút hai lần mà số dư chỉ giảm một lần (hoặc ngược lại, tùy con số), và ràng buộc không âm cũng không bắt được vì mỗi lượt ghi đều hợp lệ.
Cách sửa: để cơ sở dữ liệu tự trừ (`update ... set balance = balance - 20 where id = 1 and balance >= 20`), hoặc khóa dòng khi đọc (`select ... for update`), hoặc chạy ở `repeatable read` và chạy lại giao dịch khi bị hủy với lỗi tuần tự hóa.

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

Nguyên tử, nhất quán và cô lập, trên một cơ sở dữ liệu thử `lab044`:

```python
import psycopg                                    # pip install "psycopg[binary]"
DSN = "host=/tmp/pglab port=5433 user=postgres dbname=lab044"
admin = psycopg.connect(DSN, autocommit=True)
def reset():
    admin.execute("drop table if exists accounts")
    admin.execute("create table accounts(id int primary key, balance int check (balance >= 0))")
    admin.execute("insert into accounts values (1, 100), (2, 100)")
balances = lambda: admin.execute("select id, balance from accounts order by id").fetchall()

# A + C: chuyển 150 từ tài khoản 1 sang 2; lệnh trừ vi phạm ràng buộc, cả giao dịch bị hủy
reset()
with psycopg.connect(DSN) as c:
    try:
        with c.transaction():
            c.execute("update accounts set balance = balance + 150 where id = 2")
            c.execute("update accounts set balance = balance - 150 where id = 1")
    except psycopg.Error as e:
        print("bị từ chối:", e.diag.message_primary)
print("sau giao dịch hỏng:", balances())

# I: đọc lại trong cùng giao dịch, ở hai mức cô lập
for level in ("read committed", "repeatable read"):
    reset()
    a, b = psycopg.connect(DSN), psycopg.connect(DSN, autocommit=True)
    a.execute(f"set transaction isolation level {level}")
    first = a.execute("select balance from accounts where id = 1").fetchone()[0]
    b.execute("update accounts set balance = 50 where id = 1")             # người khác sửa và chốt
    second = a.execute("select balance from accounts where id = 1").fetchone()[0]
    a.rollback(); print(f"{level}: đọc lần một {first}, lần hai {second}")

# I: mất cập nhật khi đọc rồi tự tính ở ứng dụng
for level in ("read committed", "repeatable read"):
    reset()
    a, b = psycopg.connect(DSN), psycopg.connect(DSN)
    for c in (a, b):
        c.execute(f"set transaction isolation level {level}")
    seen_a = a.execute("select balance from accounts where id = 1").fetchone()[0]
    seen_b = b.execute("select balance from accounts where id = 1").fetchone()[0]
    a.execute("update accounts set balance = %s where id = 1", (seen_a - 10,)); a.commit()
    try:
        b.execute("update accounts set balance = %s where id = 1", (seen_b - 20,)); b.commit(); note = "B ghi được"
    except psycopg.Error as e:
        b.rollback(); note = "B bị hủy: " + e.diag.message_primary
    print(f"{level}: rút 10 và rút 20 từ 100 -> {balances()[0][1]} ({note})")
```

Bền vững, trên một cụm thử riêng ở cổng 5441 có bảng `durable(id int, note text)` (lệnh `pg_ctl` chạy với quyền của người dùng `postgres`):

```bash
for mode in on off; do
  psql -h /tmp/pglab -p 5441 -U postgres -qc "truncate durable"
  python3 -c "
import psycopg
c = psycopg.connect('host=/tmp/pglab port=5441 user=postgres', autocommit=True)
c.execute('set synchronous_commit = $mode')
for i in range(1, 2001):
    c.execute('insert into durable values (%s, %s)', (i, 'đã chốt'))   # mỗi lệnh là một giao dịch đã chốt
"
  pg_ctl -D /tmp/pglab/s028 stop -m immediate                         # tắt đột ngột, không tắt sạch
  pg_ctl -D /tmp/pglab/s028 -o '-p 5441 -k /tmp/pglab' -l /tmp/s028.log start -w
  echo "$mode: $(psql -h /tmp/pglab -p 5441 -U postgres -Atc 'select count(*) from durable') dòng"
done
```

Kết quả: `bị từ chối: new row for relation "accounts" violates check constraint "accounts_balance_check"` và `[(1, 100), (2, 100)]`; `read committed` đọc 100 rồi 50, `repeatable read` đọc 100 rồi 100; rút cùng lúc còn 80 ở `read committed`, còn 90 với B bị hủy ở `repeatable read`; bền vững: `on` 2.000 dòng cả ba lần, `off` 1.928, 1.974 và 1.946 dòng qua ba lần.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-does-acid-mean.md): định nghĩa bốn chữ, nhất quán khác với chữ C của CAP, bền vững trong hệ phân tán là chép sang máy khác.
- Tài liệu PostgreSQL 16, tại commit cố định của nhánh `REL_16_STABLE`, đọc từ bản clone của kho: [Concurrency Control](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/mvcc.sgml) (mức cô lập, lỗi tuần tự hóa ở `repeatable read`), [Reliability and the Write-Ahead Log](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/wal.sgml) (chốt không đồng bộ có thể mất giao dịch gần nhất), [pg_ctl](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/ref/pg_ctl-ref.sgml) (chế độ dừng `immediate`).

Phép thử chạy trên PostgreSQL 16.15, Python 3.13.16 và psycopg 3.3.6 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

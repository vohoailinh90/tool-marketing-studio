# Khóa trong cơ sở dữ liệu: thử từng loại trên PostgreSQL bằng hai phiên

**Hiểu khóa là hiểu ai chặn ai; tên của từng loại khóa thì mỗi hệ một khác.** Nguồn liệt kê chín loại: khóa chia sẻ, khóa độc quyền, khóa cập nhật, khóa cấu trúc, khóa nạp hàng loạt, khóa theo khoảng khóa, và khóa theo dòng, theo trang, theo bảng. Vài cái tên trong đó (khóa cập nhật, khóa nạp hàng loạt, khóa theo khoảng khóa) không có trong tài liệu PostgreSQL; PostgreSQL giải cùng các bài toán bằng cơ chế khác. Bài này mở hai phiên trên PostgreSQL 16 và xem từng tình huống: ai được, ai phải chờ, ai bị hủy.

![Bốn khung dọc, thử trên PostgreSQL 16 bằng hai phiên. Khung một, khóa trên một dòng: hai khóa chia sẻ cùng lúc được; khóa chia sẻ và khóa độc quyền thì bên sau phải chờ; đọc thường không bị khóa dòng chặn; khóa dòng 1 không chặn dòng 2. Khung hai, deadlock: A giữ dòng 1 rồi xin dòng 2, B giữ dòng 2 rồi xin dòng 1; PostgreSQL hủy một bên với lỗi deadlock detected và bên kia chạy tiếp. Khung ba, lệch ghi khi hai bác sĩ cùng xin nghỉ trực: ở mức repeatable read cả hai chốt được và không còn ai trực; ở mức serializable bên sau bị hủy và còn một người trực. Khung bốn, khóa bảng: đang đổi cấu trúc bảng mà chưa chốt thì cả câu đọc thường cũng phải chờ, vì khóa này xung đột với mọi khóa khác.](../../diagrams/sd-04-042-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ dùng nó.
- **MVCC** (Multi-Version Concurrency Control) — điều khiển đồng thời bằng nhiều phiên bản: mỗi dòng có thể có vài phiên bản, nên người đọc thấy bản đã chốt trong khi người khác đang sửa, không phải chờ.

## Đọc hình

Phép thử chạy ngày 2026-10-18 trên PostgreSQL 16.15. Phiên chờ khóa quá 500 mili giây thì bị hủy (`lock_timeout`), để thấy "phải chờ" thành một thông báo thay vì treo. Mã ở phần "Xem sâu hơn".

1. **Khóa trên một dòng.** A giữ khóa chia sẻ dòng 1 (`for share`). B xin khóa chia sẻ cùng dòng: được. B xin khóa độc quyền (`for update`) dòng đó: phải chờ, rồi bị hủy vì quá giờ. B đọc thường dòng đó: được ngay, vì nhờ MVCC, tài liệu PostgreSQL nói khóa dòng không ảnh hưởng việc đọc mà chỉ chặn người ghi và người khóa cùng dòng. B khóa độc quyền dòng 2: được, vì khóa chỉ nằm trên dòng 1.
2. **Deadlock.** A sửa dòng 1, B sửa dòng 2, rồi A xin dòng 2 và B xin dòng 1: mỗi bên chờ bên kia mãi mãi. PostgreSQL tự phát hiện và hủy một giao dịch (ở đây là A, với lỗi `deadlock detected`), bên kia chạy tiếp.
3. **Hai bác sĩ cùng xin nghỉ trực.** Luật: phải còn ít nhất một người trực. Mỗi bác sĩ đếm thấy còn 2 người trực, rồi tự đặt mình là nghỉ. Ở mức cô lập `repeatable read`, cả hai đều chốt được và không còn ai trực: hai lượt ghi chạm hai dòng khác nhau nên khóa dòng không ngăn được. Ở mức `serializable`, PostgreSQL giữ các khóa vị từ (4 khóa `SIReadLock` trong `pg_locks`) để biết lượt ghi nào làm sai kết quả đọc của giao dịch kia; bên chốt sau bị hủy với `could not serialize access due to read/write dependencies among transactions`, còn 1 người trực. Đây là cách PostgreSQL chặn loại lỗi mà nguồn gán cho khóa theo khoảng khóa; khóa vị từ của nó không chặn ai, chỉ hủy giao dịch khi cần.
4. **Khóa bảng.** A đang thêm cột vào bảng mà chưa chốt: B chỉ đọc thường cũng phải chờ. Đổi cấu trúc bảng xin khóa `ACCESS EXCLUSIVE`, loại xung đột với mọi khóa khác trên bảng.

## Giới hạn cần nhớ

Phép thử chỉ có hai phiên, bảng hai dòng; nó cho thấy ai chặn ai, không đo hiệu năng. Hệ khác chia và đặt tên khóa khác (khóa theo trang, khóa cập nhật, khóa nạp hàng loạt có ở những hệ nguồn mô tả, PostgreSQL không có dưới các tên đó); đọc tài liệu của chính hệ bạn dùng. Mức `serializable` không làm giao dịch chờ nhau nhưng có thể hủy giao dịch, nên ứng dụng phải sẵn sàng chạy lại giao dịch bị hủy.

## Nhìn hình thử trả lời

Hai yêu cầu chuyển tiền chạy cùng lúc: một từ tài khoản 1 sang 2, một từ 2 sang 1. Mỗi yêu cầu khóa tài khoản nguồn trước, rồi mới khóa tài khoản đích. Đôi khi một yêu cầu báo `deadlock detected`. Vì sao, và sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Yêu cầu thứ nhất giữ tài khoản 1 và chờ tài khoản 2; yêu cầu thứ hai giữ tài khoản 2 và chờ tài khoản 1: đúng tình huống deadlock trong phép thử, và PostgreSQL hủy một bên.
Sửa bằng cách khóa theo một thứ tự cố định cho mọi yêu cầu, chẳng hạn luôn khóa tài khoản có mã nhỏ hơn trước: khi đó cả hai yêu cầu cùng xin tài khoản 1 trước, một bên chờ bên kia xong rồi mới chạy, không ai giữ thứ người kia cần. Ứng dụng vẫn nên chạy lại giao dịch khi gặp lỗi deadlock.

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

Cần một cơ sở dữ liệu thử `lab042` trên PostgreSQL; đoạn mã tạo lại hai bảng `accounts` và `doctors`.

```python
import threading, time, psycopg                  # pip install "psycopg[binary]"
DSN = "host=/tmp/pglab port=5433 user=postgres dbname=lab042"
setup = psycopg.connect(DSN, autocommit=True)
setup.execute("drop table if exists accounts, doctors")
setup.execute("create table accounts(id int primary key, balance int)")
setup.execute("insert into accounts values (1, 100), (2, 100)")
setup.execute("create table doctors(name text primary key, on_call bool)")
setup.execute("insert into doctors values ('An', true), ('Bình', true)")

def session():
    c = psycopg.connect(DSN, options="-c lock_timeout=500ms"); return c
def attempt(conn, sql):
    try:
        conn.execute(sql); return "được"
    except psycopg.Error as e:
        conn.rollback(); return "bị chặn: " + e.diag.message_primary

# 1. Khóa chia sẻ và khóa độc quyền trên một dòng
a, b = session(), session()
a.execute("select * from accounts where id = 1 for share")
print("A giữ khóa chia sẻ dòng 1 | B xin chia sẻ:", attempt(b, "select * from accounts where id = 1 for share"))
b.rollback()
print("A giữ khóa chia sẻ dòng 1 | B xin độc quyền:", attempt(b, "select * from accounts where id = 1 for update"))
print("A giữ khóa chia sẻ dòng 1 | B đọc thường:", attempt(b, "select balance from accounts where id = 1"))
print("A giữ khóa chia sẻ dòng 1 | B xin độc quyền dòng 2:", attempt(b, "select * from accounts where id = 2 for update"))
a.rollback(); b.rollback()

# 2. Deadlock: mỗi bên giữ một dòng rồi xin dòng của bên kia
a, b = psycopg.connect(DSN), psycopg.connect(DSN)
a.execute("update accounts set balance = balance - 10 where id = 1")
b.execute("update accounts set balance = balance - 10 where id = 2")
result = {}
def a_then():
    result["A"] = attempt(a, "update accounts set balance = balance + 10 where id = 2")
t = threading.Thread(target=a_then); t.start(); time.sleep(0.3)
result["B"] = attempt(b, "update accounts set balance = balance + 10 where id = 1")
t.join(); print("deadlock:", result); a.rollback(); b.rollback()

# 3. Lệch ghi (write skew): hai bác sĩ cùng xin nghỉ trực, mỗi người thấy còn người kia
for level in ("repeatable read", "serializable"):
    a, b = psycopg.connect(DSN), psycopg.connect(DSN)
    for c in (a, b):
        c.execute(f"set transaction isolation level {level}")
        c.execute("select count(*) from doctors where on_call")            # mỗi bên thấy 2 người trực
    a.execute("update doctors set on_call = false where name = 'An'")
    b.execute("update doctors set on_call = false where name = 'Bình'")
    if level == "serializable":
        print("khóa vị từ đang giữ:", setup.execute("select count(*) from pg_locks where mode = 'SIReadLock'").fetchone()[0])
    a.commit()
    try:
        b.commit(); outcome = "B chốt được"
    except psycopg.Error as e:
        outcome = "B bị hủy: " + e.diag.message_primary
    left = setup.execute("select count(*) from doctors where on_call").fetchone()[0]
    print(f"{level}: {outcome} | còn {left} người trực")
    setup.execute("update doctors set on_call = true")

# 4. Đổi cấu trúc bảng chặn cả người đọc
a, b = psycopg.connect(DSN), session()
a.execute("alter table accounts add column note text")                      # chưa chốt
print("A đang alter table | B đọc thường:", attempt(b, "select * from accounts"))
a.rollback(); b.rollback()
```

Kết quả: chia sẻ cùng chia sẻ được; độc quyền bị chặn (`canceling statement due to lock timeout`); đọc thường và khóa dòng 2 được; deadlock hủy A, B được; `repeatable read` còn 0 người trực, `serializable` hủy B và còn 1 người trực, với 4 khóa `SIReadLock` lúc đó; đọc thường bị chặn khi A đang `alter table`.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-differences-among-database-locks.md): chín loại khóa thường gặp.
- [PostgreSQL 16 — Concurrency Control](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/mvcc.sgml), tại commit cố định của nhánh `REL_16_STABLE`: khóa dòng không ảnh hưởng việc đọc; tự phát hiện và hủy deadlock; khóa vị từ của mức `serializable` không chặn ai; `ACCESS EXCLUSIVE` xung đột với mọi khóa. Đọc từ bản clone của kho.

Phép thử chạy trên PostgreSQL 16.15, Python 3.13.16 và psycopg 3.3.6 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

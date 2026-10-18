# Bản sao chỉ đọc qua lớp trung gian: vừa đặt đơn mà không thấy đơn

**Lớp trung gian giấu được cấu trúc của cụm máy khỏi ứng dụng, nhưng không giấu được việc bản sao luôn chậm hơn bản chính một chút.** Mẫu bản sao chỉ đọc chia việc: mọi lượt ghi về một bản chính, các lượt đọc chia cho bản sao. Nguồn so hai cách đặt logic định tuyến (trong mã ứng dụng, hoặc trong một lớp trung gian nói giao thức MySQL) và bàn ưu nhược của lớp trung gian. Bài này dựng một bản chính và một bản sao PostgreSQL thật, viết một lớp định tuyến tối giản, và đo chuyện xảy ra khi người dùng đọc ngay sau khi ghi.

![Khung một, bốn mảnh: ứng dụng gửi mọi câu lệnh tới một địa chỉ và không biết có mấy máy; lớp trung gian đưa câu ghi tới bản chính, câu đọc tới bản sao; bản chính nhận mọi lượt ghi và gửi nhật ký sang bản sao; bản sao chỉ đọc và áp dụng nhật ký chậm hơn một chút. Khung hai, trình tự: Alice đặt đơn, bản chính trả lời đã lưu; Alice xem đơn của mình, câu đọc đi tới bản sao, bản sao trả 0 đơn vì chưa nhận kịp. Khung ba, đo trên một máy: bản sao chậm trung vị dưới nửa mili giây, nhưng đọc ngay sau khi ghi thì 45 đến 48 trên 50 lần không thấy; cho người vừa ghi đọc ở bản chính trong 5 giây thì Alice thấy đơn; bật remote_apply thì thấy ngay 50 trên 50, đổi lại mỗi lần ghi phải chờ bản sao.](../../diagrams/sd-04-035-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; MySQL và PostgreSQL là hai hệ dùng nó.
- **WAL** (Write-Ahead Log) — nhật ký ghi trước: PostgreSQL ghi mọi thay đổi vào nhật ký này; bản sao nhận nhật ký từ bản chính rồi áp dụng lại.

## Đọc hình

Phép thử chạy ngày 2026-10-18 trên PostgreSQL 16.15: bản chính và một bản sao tạo bằng `pg_basebackup`, nhận WAL theo kiểu không đồng bộ, cùng một máy. Lớp trung gian là một lớp Python vài chục dòng (phần "Xem sâu hơn"), không phải phần mềm trung gian thật.

1. **Bốn mảnh.** Ứng dụng chỉ biết một chỗ để gửi câu lệnh. Lớp trung gian nhìn câu lệnh: `select` đi tới bản sao, còn lại tới bản chính. Bản sao từ chối ghi: `cannot execute INSERT in a read-only transaction`.
2. **Alice đặt đơn rồi xem ngay.** Tài liệu PostgreSQL nói rõ dữ liệu trên bản sao đến sau, nên cùng một câu hỏi gửi gần như cùng lúc tới hai máy có thể cho hai kết quả; bản sao chỉ "nhất quán sau cùng". Để thấy rõ, bài tạm dừng việc áp dụng WAL trên bản sao (`pg_wal_replay_pause()`): Alice ghi một đơn, lớp định tuyến đưa câu đọc tới bản sao, và nó trả 0 đơn.
3. **Không cần chờ lâu mới gặp.** Không tạm dừng gì, trên cùng một máy, bản sao thấy dòng mới sau trung vị dưới 0,5 mili giây. Vậy mà đọc ngay một lần sau khi ghi, 45 đến 48 trên 50 lần bản sao chưa có dòng đó (hai lần chạy).
4. **Hai cách sửa.** Cách một nằm ở lớp trung gian: sau khi một người ghi, cho các câu đọc của chính người đó đi tới bản chính một lúc (ở đây 5 giây); Alice thấy đơn của mình. Cách hai nằm ở cơ sở dữ liệu: đặt bản sao là đồng bộ và `synchronous_commit = remote_apply`, lệnh ghi chỉ báo xong khi bản sao đã áp dụng; đọc ngay thấy 50 trên 50 lần.

## Giới hạn cần nhớ

Cách một chỉ giúp người vừa ghi; người khác vẫn có thể đọc dữ liệu cũ, và lớp trung gian phải nhớ ai vừa ghi, khó khi có nhiều bản của nó. Cách hai làm mỗi lần ghi chậm thêm một vòng tới bản sao, và tài liệu PostgreSQL cảnh báo lệnh ghi có thể không bao giờ xong nếu bản sao đồng bộ bị sập. Lớp trung gian còn là thêm một chặng mạng và một điểm phải chạy dự phòng, như nguồn đã nêu. Số đo ở đây là của hai tiến trình trên cùng một máy; bản sao ở máy khác, vùng khác thì chậm hơn nhiều.

## Nhìn hình thử trả lời

Trang "Hồ sơ của tôi" cho người dùng đổi ảnh đại diện. Sau khi bấm lưu, trang tải lại và hiện ảnh cũ, vài giây sau mới đúng. Điều gì đang xảy ra, và bạn sửa ở đâu nếu không muốn mọi lượt ghi của cả hệ chậm đi?

<details>
<summary>Xem đáp án</summary>

Câu ghi đi tới bản chính, còn trang tải lại đọc từ bản sao chưa kịp áp dụng thay đổi: đúng tình huống của Alice.
Không muốn mọi lượt ghi chậm đi thì đừng bật `remote_apply` cho cả hệ; sửa ở chỗ định tuyến: các câu đọc của chính người vừa ghi đi tới bản chính trong một khoảng ngắn (hoặc tới khi bản sao báo đã áp dụng tới vị trí WAL của lượt ghi đó). PostgreSQL cũng cho đặt `synchronous_commit` riêng cho từng giao dịch: khi đã có bản sao đồng bộ, để mặc định là `local` và chỉ lượt ghi cần thấy ngay mới dùng `remote_apply`.

</details>

<details>
<summary>Xem sâu hơn: lớp định tuyến tối giản</summary>

Cần một bản chính (cổng 5433) và một bản sao (cổng 5434) đã chạy, tạo bằng `pg_basebackup -R -X stream`, có cơ sở dữ liệu `shop` với bảng `orders(id serial primary key, customer text, item text)`.

```python
import time
import psycopg                                  # pip install "psycopg[binary]"

primary = psycopg.connect("host=/tmp/pglab port=5433 user=postgres dbname=shop", autocommit=True)
replica = psycopg.connect("host=/tmp/pglab port=5434 user=postgres dbname=shop", autocommit=True)

class Router:
    """Ghi tới bản chính, đọc tới bản sao; tùy chọn 'dính' bản chính một lúc sau khi ghi."""
    def __init__(self, sticky_seconds=0):
        self.sticky_seconds, self.last_write = sticky_seconds, {}
    def run(self, user, sql, *args):
        is_read = sql.lstrip().lower().startswith("select")
        recent = time.monotonic() - self.last_write.get(user, -1e9) < self.sticky_seconds
        conn = replica if is_read and not recent else primary
        rows = conn.execute(sql, args).fetchall() if is_read else conn.execute(sql, args)
        if not is_read:
            self.last_write[user] = time.monotonic()
        return ("bản sao" if conn is replica else "bản chính"), rows

primary.execute("truncate orders"); time.sleep(1)       # bắt đầu từ bảng trống, chờ bản sao nhận kịp
replica.execute("select pg_wal_replay_pause()")           # giả lập bản sao chậm
for name, router in [("theo loại câu lệnh", Router()), ("dính 5 giây sau khi ghi", Router(sticky_seconds=5))]:
    router.run("alice", "insert into orders(customer, item) values (%s, %s)", "alice", name)
    print(name, router.run("alice", "select count(*) from orders where customer = %s", "alice"))
replica.execute("select pg_wal_replay_resume()")
```

Kết quả: `theo loại câu lệnh ('bản sao', [(0,)])` rồi `dính 5 giây sau khi ghi ('bản chính', [(2,)])`. Phép đo "đọc ngay sau khi ghi" lặp 50 lần: ghi một dòng ở bản chính, đọc dòng đó một lần ở bản sao, rồi đọc lại liên tục tới khi thấy để tính độ trễ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-implement-read-replica-pattern.md): hai cách định tuyến, lớp trung gian nói giao thức MySQL, ưu điểm (mã ứng dụng gọn, tương thích) và nhược điểm (thêm phức tạp, cần chạy dự phòng, thêm độ trễ mạng).
- [PostgreSQL 16 — High Availability, Load Balancing, and Replication](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/high-availability.sgml), tại commit cố định của nhánh `REL_16_STABLE`: bản sao chỉ đọc, nhất quán sau cùng; `remote_apply` cho cân bằng tải với nhất quán nhân quả; lệnh ghi có thể không bao giờ xong nếu bản sao đồng bộ sập. Đọc từ bản clone của kho.

Phép thử chạy trên PostgreSQL 16.15, Python 3.13.16 và psycopg 3.3.6 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

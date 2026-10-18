# Định lý CAP: thử cắt mạng giữa hai máy PostgreSQL

**CAP không bảo bạn "chọn hai trong ba"; nó nói lúc mạng giữa các máy bị cắt, hệ phải chọn giữa trả lời ngay (có thể thiếu dữ liệu mới) và chờ cho đúng (có thể không trả lời).** Nguồn định nghĩa ba chữ C, A, P, rồi lưu ý cách nói "hai trong ba" dễ gây hiểu lầm: chọn cơ sở dữ liệu không thể chỉ dựa vào CAP, định lý nói về sẵn sàng và nhất quán trọn vẹn, và khi không có phân vùng thì câu hỏi thật là độ trễ đổi lấy nhất quán (định lý PACELC). Bài này dựng một phân vùng thật giữa bản chính và bản sao PostgreSQL để thấy hai lựa chọn đó.

![Khung một, ba chữ của CAP: C, nhất quán, mọi lượt đọc thấy cùng dữ liệu mới nhất; A, sẵn sàng, mọi yêu cầu tới máy còn sống đều được trả lời; P, chịu phân vùng, hệ vẫn chạy khi mạng giữa các máy bị cắt. Khung hai, PostgreSQL sao chép không đồng bộ, cắt đường sao chép rồi ghi ở bản chính: lệnh ghi xong ngay, bản sao vẫn trả lời nhưng thiếu dòng mới; nối lại mạng thì bản sao nhận đủ. Khung ba, sao chép đồng bộ: lệnh ghi treo, statement_timeout 3 giây không cắt được; hủy tay sau 10 giây chỉ ra một cảnh báo, dòng đã ghi ở bản chính nhưng bản sao chưa có. Khung bốn, khi không có phân vùng, cái giá là độ trễ: mỗi lần ghi 0,40 mili giây khi không đồng bộ và 0,88 mili giây khi đồng bộ.](../../diagrams/sd-04-038-main.svg)

## Từ viết tắt

- **CAP** (Consistency, Availability, Partition) — nhất quán, sẵn sàng, phân vùng: chữ P viết tắt cho "chịu được phân vùng" (partition tolerance); định lý CAP nói một hệ phân tán không giữ trọn cả nhất quán lẫn sẵn sàng khi mạng bị chia cắt.
- **ACID** (Atomicity, Consistency, Isolation, Durability) — bốn tính chất của một giao dịch đáng tin: làm trọn hoặc không làm, giữ dữ liệu hợp lệ, các giao dịch không lẫn vào nhau, đã ghi thì không mất.
- **PACELC** (Partition, Availability, Consistency, Else, Latency, Consistency) — mở rộng của CAP: khi có phân vùng thì chọn giữa sẵn sàng và nhất quán; còn lại (else) thì chọn giữa độ trễ và nhất quán.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ dùng nó.
- **WAL** (Write-Ahead Log) — nhật ký ghi trước: PostgreSQL ghi mọi thay đổi vào nhật ký này; bản sao nhận nhật ký từ bản chính để chép theo.

## Đọc hình

Phép thử chạy ngày 2026-10-18 trên PostgreSQL 16.15: một bản chính và một bản sao trên cùng máy. "Cắt mạng" là cho bản sao trỏ tới một cổng không có ai nghe (đổi `primary_conninfo` rồi nạp lại cấu hình): cả hai máy vẫn chạy, chỉ không nói chuyện được với nhau. Mã ở phần "Xem sâu hơn".

1. **Sao chép không đồng bộ: chọn trả lời.** Lệnh ghi ở bản chính xong ngay. Bản sao vẫn trả lời mọi câu đọc, nhưng không có dòng vừa ghi. Nối lại mạng thì bản sao nhận đủ. Hệ giữ được sẵn sàng, đổi lại người đọc ở bản sao thấy dữ liệu cũ trong lúc phân vùng.
2. **Sao chép đồng bộ: chọn nhất quán.** Đặt bản sao là đồng bộ (`synchronous_standby_names = '*'`): lệnh ghi chỉ báo xong khi bản sao xác nhận. Khi mạng bị cắt, lệnh ghi treo (chờ ở sự kiện `SyncRep`); đặt `statement_timeout` 3 giây cũng không cắt được lúc chờ này. Hủy tay sau 10 giây, máy khách không nhận lỗi mà nhận một cảnh báo: `canceling wait for synchronous replication due to user request`, kèm lời giải thích giao dịch đã được ghi ở bản chính nhưng có thể chưa sang bản sao. Đúng vậy: bản chính thấy dòng đó, bản sao không. Mã nguồn PostgreSQL ghi lý do: lúc này không thể báo lỗi (vì giao dịch đã ghi xong ở bản chính), cũng không thể báo thành công như bình thường (vì chưa sao chép), nên chỉ còn cảnh báo.
3. **Không phân vùng: trả bằng độ trễ.** Ghi 200 dòng liên tiếp: trung bình 0,40 mili giây mỗi lần khi không đồng bộ, 0,88 mili giây khi chờ bản sao áp dụng (`remote_apply`). Hai tiến trình trên cùng một máy đã gấp đôi; bản sao ở vùng khác thì mỗi lần ghi cộng thêm cả một vòng mạng.

## Giới hạn cần nhớ

Phép thử là hai tiến trình trên một máy và một kiểu phân vùng (bản sao không tới được bản chính); hệ thật còn có phân vùng một chiều, máy chậm mà không chết, và phải chọn máy nào lên làm bản chính. "Nhất quán" của CAP (mọi lượt đọc thấy lần ghi mới nhất) khác chữ "nhất quán" trong ACID (giữ đúng các ràng buộc của dữ liệu). Như nguồn nói, đừng chọn cơ sở dữ liệu chỉ vì nó được xếp nhãn "chọn sẵn sàng" hay "chọn nhất quán": phần lớn thời gian không có phân vùng, và lúc đó độ trễ, mô hình dữ liệu và cách vận hành mới là điều quyết định.

## Nhìn hình thử trả lời

Bạn chạy PostgreSQL với một bản sao đồng bộ ở trung tâm dữ liệu khác. Đường truyền giữa hai nơi đứt. Người dùng báo "bấm đặt hàng thì quay mãi", rồi kỹ sư trực hủy các lệnh đang treo. Sau đó đơn của những người dùng đó có hay không, và ứng dụng nên làm gì?

<details>
<summary>Xem đáp án</summary>

Có, ở bản chính: như phép thử, hủy lúc đang chờ bản sao không hoàn tác giao dịch, nó đã được ghi ở bản chính, chỉ chưa chắc đã sang bản sao. Ứng dụng nhận một cảnh báo chứ không phải lỗi, nên nếu nó coi "không có lỗi là thành công" thì báo thành công, còn nếu nó coi "quá giờ là thất bại" và cho người dùng đặt lại thì sinh đơn trùng.
Ứng dụng nên đọc lại trạng thái đơn trước khi cho đặt lại, và gắn mỗi lượt đặt một mã không trùng để lần thử lại không tạo đơn thứ hai. Còn chọn giữ bản sao đồng bộ (đúng nhưng có thể treo) hay chuyển sang không đồng bộ (trả lời được nhưng có thể mất dữ liệu nếu bản chính hỏng) là quyết định của người làm sản phẩm.

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

Cần một bản chính (cổng 5433) và một bản sao (cổng 5434) đã chạy, có bảng `orders(id serial primary key, customer text, item text)` trong cơ sở dữ liệu `shop`. Chỉ thử trên cụm thử.

```python
import threading, time, psycopg                    # pip install "psycopg[binary]"
P = "host=/tmp/pglab port=5433 user=postgres dbname=shop"
R = "host=/tmp/pglab port=5434 user=postgres dbname=shop"
primary, admin, replica = (psycopg.connect(P, autocommit=True), psycopg.connect(P, autocommit=True),
                           psycopg.connect(R, autocommit=True))
GOOD = replica.execute("show primary_conninfo").fetchone()[0]
notices = []
primary.add_notice_handler(lambda d: notices.append((d.severity, d.message_primary, d.message_detail)))

def partition(on):                                  # cắt hoặc nối lại đường sao chép
    target = "'host=/tmp/pglab port=5999 user=postgres'" if on else psycopg.sql.Literal(GOOD).as_string(replica)
    replica.execute(f"alter system set primary_conninfo = {target}")
    replica.execute("select pg_reload_conf()"); time.sleep(3)

seen = lambda c, item: c.execute("select count(*) from orders where item = %s", (item,)).fetchone()[0]
for names in ("''", "'*'"):                         # '' là không đồng bộ, '*' là đồng bộ
    admin.execute(f"alter system set synchronous_standby_names = {names}"); admin.execute("select pg_reload_conf()")
    time.sleep(1); partition(True)
    pid = primary.execute("select pg_backend_pid()").fetchone()[0]
    primary.execute("set statement_timeout = '3s'")
    cancel = threading.Timer(10, lambda: admin.execute("select pg_cancel_backend(%s)", (pid,))); cancel.start()
    t = time.perf_counter()
    primary.execute("insert into orders(customer, item) values ('cap', %s)", (names,))
    cancel.cancel()
    print(names, f"ghi trả về sau {time.perf_counter() - t:.1f} s", notices[-1:],
          "| bản chính", seen(primary, names), "| bản sao", seen(replica, names))
    partition(False)
    print(names, "nối lại, bản sao", seen(replica, names))
admin.execute("alter system reset synchronous_standby_names"); admin.execute("select pg_reload_conf()")
```

Kết quả: với `''`, lệnh ghi trả về ngay, bản chính 1, bản sao 0, nối lại thì bản sao 1. Với `'*'`, lệnh ghi trả về sau 10 giây kèm cảnh báo `canceling wait for synchronous replication due to user request`, bản chính 1, bản sao 0; nối lại thì bản sao 1. Phép đo độ trễ ghi 200 dòng liên tiếp ở hai chế độ khi mạng thông suốt.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cap-theorem-one-of-the-most-misunderstood-terms.md): định nghĩa C, A, P; ba lưu ý về cách hiểu "hai trong ba"; câu trích bài "CAP Twelve Years Later" và PACELC.
- [PostgreSQL 16 — High Availability, Load Balancing, and Replication](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/high-availability.sgml), tại commit cố định của nhánh `REL_16_STABLE`: sao chép đồng bộ, lệnh ghi có thể không bao giờ xong nếu bản sao đồng bộ hỏng. Đọc từ bản clone của kho.
- [PostgreSQL 16 — mã nguồn `syncrep.c`, thư mục sao chép của máy chủ](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/src/backend/replication/syncrep.c), cùng commit: lời giải thích vì sao hủy lúc chờ sao chép chỉ cho ra cảnh báo. Đọc từ bản clone của kho.

Phép thử chạy trên PostgreSQL 16.15, Python 3.13.16 và psycopg 3.3.6 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

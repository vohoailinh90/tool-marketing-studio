# Redis giữ dữ liệu qua lần sập thế nào: RDB và AOF

**Redis giữ toàn bộ dữ liệu trong bộ nhớ. Muốn dữ liệu còn sau khi tiến trình chết, phải bật một cách ghi xuống đĩa: chụp ảnh định kỳ (RDB) hoặc ghi lại từng lệnh (AOF).**
Hai cách khác nhau ở chỗ mất bao nhiêu khi sập và khởi động lại nhanh hay chậm. Bài này thử cả hai trên Redis 7.0.15.

![Ba phần xếp dọc. Phần một, bốn bước của một lệnh ghi khi bật AOF: sửa dữ liệu trong RAM, nối lệnh vào bộ đệm AOF, gọi write() đưa bộ đệm vào tệp, thường xong trước khi trả lời, fsync theo chính sách (everysec mỗi giây ở nền, always trước khi trả lời). Phần hai, kết quả thử ghi 1500 khóa rồi kill -9: không lưu còn 0 khóa; chỉ RDB với ảnh chụp lúc có 1000 khóa còn 1000, mất 500; AOF everysec còn đủ 1500. Phần ba, bốn điều cần nhớ: RDB gọn và nạp nhanh nhưng mất phần ghi sau ảnh chụp cuối; AOF mất ít hơn nhưng tệp lớn hơn và được viết lại ở nền; kill -9 khác mất điện vì fsync mới quyết định phần nào chắc chắn nằm trên đĩa; bật cả hai thì tệp gốc dạng RDB, các lệnh sau nối dạng AOF.](../../diagrams/sd-06-019-main.svg)

## Từ viết tắt

- **RDB** (Redis DataBase) — tệp ảnh chụp của Redis: toàn bộ dữ liệu tại một thời điểm, ghi gọn vào một tệp nhị phân.
- **AOF** (Append Only File) — tệp chỉ ghi nối thêm: nhật ký các lệnh làm đổi dữ liệu, được chạy lại khi khởi động để dựng lại dữ liệu.
- **RAM** (Random Access Memory) — bộ nhớ trong của máy: nơi Redis giữ dữ liệu khi chạy; mất sạch khi tiến trình hay máy tắt.

## Đọc hình

**Một lệnh ghi khi bật AOF.** Redis chạy lệnh trên dữ liệu trong bộ nhớ trước, rồi mới nối lệnh vào bộ đệm AOF. Nhật ký này ghi *sau* khi thực hiện, ngược với nhật ký ghi trước của nhiều cơ sở dữ liệu. Bình thường, mỗi vòng xử lý ghi bộ đệm vào tệp bằng một lần `write()` rồi mới gửi các câu trả lời. Ngoại lệ là `everysec` (mặc định) khi lần `fsync` nền trước chưa xong: Redis có thể hoãn `write()` tới khoảng hai giây, và trong lúc đó các câu trả lời vẫn được gửi. Việc ép dữ liệu xuống đĩa thật (`fsync`) tùy chính sách: `everysec` để một luồng nền làm mỗi giây; chỉ `always` bảo đảm đã ghi và `fsync` xong rồi mới trả lời.

**Thử nghiệm.** Ghi 1500 khóa, giết tiến trình bằng `kill -9`, khởi động lại và đếm khóa:

- tắt cả hai cách: còn 0 khóa;
- chỉ RDB, ảnh chụp lấy lúc có 1000 khóa: còn 1000, mất 500 khóa ghi sau ảnh chụp;
- AOF với `everysec`: còn đủ 1500.

**RDB chụp thế nào.** Redis gọi `fork()`. Tiến trình con ghi ảnh chụp ra tệp tạm rồi thay tệp cũ; tiến trình cha vẫn phục vụ. Nhờ cơ chế sao chép khi ghi của hệ điều hành, hai tiến trình dùng chung bộ nhớ, chỉ trang nào bị sửa trong lúc chụp mới phải chép riêng. Nhật ký của lần thử ghi đủ các bước: bắt đầu lưu nền với số tiến trình con, lưu xong, và lượng bộ nhớ phải chép riêng (bằng 0 với 1000 khóa nhỏ).

## Giới hạn cần nhớ

`kill -9` chỉ giết tiến trình; phần đã `write()` vẫn nằm trong bộ đệm của hệ điều hành nên không mất (trong lần thử, đĩa rảnh nên không có lần ghi nào bị hoãn). Mất điện hay sập cả máy mới là lúc `fsync` quyết định: với `everysec`, tài liệu Redis nói có thể mất khoảng một giây ghi cuối. Lần thử trên không giả lập mất điện.

Câu "lưu xuống đĩa không chặn việc ghi" cũng không đúng tuyệt đối: `fork()` với dữ liệu lớn có thể làm Redis ngừng phục vụ từ vài mili giây tới cả giây, và `always` bắt mỗi đợt trả lời chờ `fsync`.

## Nhìn hình trả lời

Bạn dùng Redis làm bộ nhớ đệm trước một cơ sở dữ liệu chính, chấp nhận mất dữ liệu đệm của vài phút. Còn một Redis khác giữ giỏ hàng, thứ không lưu ở đâu khác. Mỗi cái nên bật cách nào?

<details>
<summary>Xem đáp án</summary>

Redis làm bộ nhớ đệm: RDB là đủ, thậm chí không lưu cũng được, vì dữ liệu đệm dựng lại được từ cơ sở dữ liệu chính; RDB cho tệp gọn để sao lưu và khởi động lại nhanh hơn AOF khi dữ liệu lớn.
Redis giữ giỏ hàng: bật AOF để chỉ mất tối đa khoảng một giây khi sập máy, và giữ cả RDB. Tài liệu Redis khuyên dùng cả hai khi rất cần an toàn dữ liệu, và không khuyến khích chỉ dùng AOF vì ảnh chụp RDB tiện cho sao lưu và khởi động lại.

</details>

<details>
<summary>Xem sâu hơn: bật cả hai thì tệp trông thế nào</summary>

- Từ Redis 7.0, AOF chia thành một tệp gốc và các tệp tăng, có tệp kê khai (manifest) theo dõi. Trong lần thử, thư mục `appendonlydir` có `appendonly.aof.1.base.rdb`, `appendonly.aof.1.incr.aof` và `appendonly.aof.manifest`; tệp tăng chứa lệnh ở đúng dạng giao thức Redis (`SELECT 0`, rồi `SET k1 v1`...).
- Khi viết lại AOF bằng `BGREWRITEAOF`, với `aof-use-rdb-preamble yes` (mặc định), tệp gốc mới ở dạng RDB: tệp `appendonly.aof.2.base.rdb` mở đầu bằng chữ `REDIS`, các lệnh ghi sau đó nối vào `appendonly.aof.2.incr.aof`. Đây là cách "ảnh chụp làm nền, nhật ký ghi phần sau" mà bài nguồn gọi là kết hợp.
- Viết lại AOF để làm gì: tăng một bộ đếm 100 lần thì nhật ký có 100 lệnh nhưng chỉ cần một để dựng lại. Redis viết lại ở nền, cũng bằng `fork()`.
- Có cả AOF lẫn RDB khi khởi động thì Redis nạp từ AOF, vì nó đầy đủ hơn.
- Lệnh cuối trong AOF bị ghi dở (đầy đĩa, sập giữa chừng): mặc định (`aof-load-truncated yes`) Redis vẫn nạp và bỏ lệnh dở dang.
- Với `everysec`, khi `fsync` nền chưa xong, mã nguồn cho phép hoãn lần `write()` tiếp theo tối đa khoảng hai giây trước khi ghi bất chấp.
- RDB mặc định trong `redis.conf` của 7.0: lưu sau 3600 giây nếu có ít nhất 1 thay đổi, sau 300 giây nếu có 100, sau 60 giây nếu có 10000. AOF mặc định tắt (`appendonly no`).

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-redis-persist-data.md): AOF, RDB, quy trình `bgsave` và cách kết hợp.
- [Redis — Persistence, tại commit cố định của kho tài liệu](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/persistence.md): ưu nhược của RDB và AOF, ba chính sách `fsync`, AOF nhiều phần từ 7.0, viết lại AOF, lời khuyên dùng cả hai, AOF được ưu tiên khi khởi động.
- [Redis 7.0.15 — `aof.c`](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/src/aof.c) và [`server.c`](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/src/server.c): ghi bộ đệm AOF trước khi gửi trả lời trong vòng xử lý, trừ khi `everysec` hoãn lần ghi (tối đa khoảng hai giây) vì `fsync` nền chưa xong; khi đó trả lời vẫn được gửi.
- [Redis — Diagnosing latency issues, tại commit cố định của kho tài liệu](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/optimization/latency.md): với `everysec`, Redis dùng bộ đệm để hoãn `write(2)` tới hai giây khi `fsync` còn chạy.
- [Redis 7.0.15 — `redis.conf`](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/redis.conf): mốc lưu RDB mặc định, `appendonly no`, `appendfsync everysec`, `aof-use-rdb-preamble yes`, `aof-load-truncated yes`.

Thử nghiệm chạy ngày 2026-10-18 trên Linux với gói Redis 7.0.15 của Ubuntu, mỗi trường hợp một thư mục dữ liệu riêng; không thử mất điện và không đo độ trễ. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

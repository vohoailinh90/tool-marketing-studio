# Redis 101: chạy thử từng điều cơ bản

**Redis là một máy chủ giữ các cấu trúc dữ liệu trong bộ nhớ; nhiều chương trình gửi lệnh qua mạng để cùng đọc và sửa chúng.** Vì dữ liệu nằm trong bộ nhớ nên đọc ghi rất nhanh, và Redis có thể chép xuống đĩa theo cấu hình.
Bài này không liệt kê tính năng mà chạy thử từng điều trên Redis 7.0.15, để thấy cả những chỗ người mới hay nhầm.

![Ba khung. Khung một, Redis là gì: một máy chủ giữ cấu trúc dữ liệu trong bộ nhớ, các chương trình gửi lệnh qua mạng để đọc và sửa chung một dữ liệu. Khung hai, năm kiểu dữ liệu đã thử: chuỗi dùng làm bộ đếm, hash giữ các trường của một đối tượng, list làm hàng đợi, set giữ phần tử không trùng, sorted set xếp hạng theo điểm. Khung ba, bốn điều dễ nhầm: lệnh xóa là DEL, gõ DELETE thì bị báo lệnh không tồn tại; JSON không có sẵn trong bản 7.0.15 mà cần module; mặc định Redis chỉ chụp ảnh dữ liệu theo chu kỳ nên có thể mất các lần ghi sau ảnh cuối; tin pub/sub gửi lúc không ai nghe thì mất.](../../diagrams/sd-06-005-main.svg)

## Từ viết tắt

- **DEL** (DELete) — lệnh xóa khóa của Redis; tên lệnh là `DEL`, không phải `DELETE`.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm các cặp tên và giá trị, dùng rộng rãi để chương trình trao đổi dữ liệu.
- **RDB** (Redis DataBase) — tệp ảnh chụp toàn bộ dữ liệu của Redis tại một thời điểm, tên mặc định `dump.rdb`.
- **AOF** (Append Only File) — tệp chỉ ghi thêm: nhật ký nối từng lệnh ghi vào cuối, để dựng lại dữ liệu khi khởi động lại.

## Thử từng điều

Mọi lệnh dưới đây chạy ngày 2026-10-18 bằng `redis-cli` với Redis 7.0.15 trên một máy.

**1 · Năm kiểu dữ liệu.** README của Redis gọi nó là máy chủ *cấu trúc dữ liệu*: mỗi khóa trỏ tới một kiểu, và lệnh `TYPE` cho biết kiểu đó.

| Lệnh đã chạy | Kết quả | `TYPE` |
|---|---|---|
| `INCR page:views` hai lần | 1, rồi 2 | `string` |
| `HSET user:1 name An city Hue` | 2 trường | `hash` |
| `LPUSH queue a b` rồi `RPOP queue` | lấy ra `a`, phần tử vào trước | `list` |
| `SADD tags redis cache redis` rồi `SCARD tags` | 2: phần tử trùng chỉ giữ một | `set` |
| `ZADD board 10 an 30 binh 20 chi` rồi `ZREVRANGE board 0 1 WITHSCORES` | `binh` 30, `chi` 20 | `zset` (sorted set) |

**2 · Khóa có hạn dùng.** `SET otp 1234 EX 1` đặt một mã sống 1 giây: `TTL otp` trả 1, sau 1,2 giây `GET otp` trả rỗng. Đây là cách Redis hay được dùng làm bộ nhớ đệm hoặc giữ phiên đăng nhập.

**3 · Lệnh xóa là `DEL`.** Đặt `SET user:1:name An` trước. Gõ `DELETE user:1:name` thì Redis báo `ERR unknown command 'DELETE'`; `DEL user:1:name` trả 1 (đã xóa một khóa).

**4 · JSON chưa có sẵn trong bản này.** `JSON.SET doc $ '{"a":1}'` báo lệnh không tồn tại, và `MODULE LIST` rỗng: kiểu JSON đến từ một module phải cài thêm vào Redis 7.0.15.

**5 · Pub/sub không giữ tin.** `PUBLISH news hello` khi chưa ai đăng ký trả 0 (không ai nhận). Mở một client chạy `SUBSCRIBE news` rồi gửi lại thì lệnh trả 1 và client kia nhận được. Tài liệu của Redis gọi đây là giao nhận *nhiều nhất một lần*: người nghe bị ngắt kết nối thì tin đó mất hẳn. Cần giữ tin thì dùng Redis Streams.

**6 · Lưu xuống đĩa: mặc định là ảnh chụp.** Khởi động không kèm tệp cấu hình, `CONFIG GET save` trả `3600 1 300 100 60 10000` và `CONFIG GET appendonly` trả `no`. Theo chú thích trong `redis.conf`, nghĩa là chụp ảnh RDB sau một giờ nếu có ít nhất 1 thay đổi, sau 5 phút nếu có 100, sau 60 giây nếu có 10.000. Mã nguồn bản 7.0.15 cho thấy cả hai vế đều tính từ lần chụp trước: số thay đổi là cộng dồn kể từ ảnh cuối, không đếm riêng trong từng khoảng 5 phút. Máy sập giữa hai lần chụp thì mất các lần ghi kể từ ảnh cuối. Khoảng đó tùy lượng ghi: nhiều ghi thì ảnh được chụp mỗi phút; hệ thống ghi rất ít, dưới 100 thay đổi kể từ ảnh trước, có thể chờ gần một giờ tới mốc `3600 1`, tức có thể mất gần một giờ ghi. Muốn bền hơn thì bật AOF; với chế độ fsync mặc định là mỗi giây, tệp cấu hình ghi rằng khi mất điện có thể mất khoảng một giây ghi. Một giây là mức thường gặp, không phải giới hạn: tài liệu về độ trễ của Redis nói khi lần fsync trước chưa xong, Redis hoãn `write(2)` tới hai giây, nên mất điện lúc đĩa chậm có thể mất cả những lần ghi cũ hơn một giây đã được trả lời (bài về khóa lớn và AOF trong nhóm này nói kỹ hơn).

## Giới hạn cần nhớ

"Redis là cơ sở dữ liệu đầy đủ" chỉ đúng khi bạn cấu hình cho nó như vậy. Mặc định của bản đã thử chấp nhận mất các lần ghi kể từ ảnh chụp cuối khi sập, có thể tới gần một giờ với hệ thống ít ghi, pub/sub không giữ tin, và mọi dữ liệu phải vừa bộ nhớ. Hãy chọn cấu hình lưu trữ theo việc bạn dùng Redis: làm bộ nhớ đệm thì mất dữ liệu chỉ là phải nạp lại, làm kho chính thì không.

## Nhìn hình trả lời

Bạn dùng Redis với cấu hình mặc định của bản 7.0.15 để giữ giỏ hàng. Máy chủ mất điện 2 phút sau lần chụp ảnh gần nhất, trong 2 phút đó có 50 lần ghi. Sau khi khởi động lại, 50 lần ghi đó còn không? Muốn giữ được thì đổi gì?

<details>
<summary>Xem đáp án</summary>

Không còn. Với `save 3600 1 300 100 60 10000`, sau 2 phút và 50 thay đổi kể từ ảnh trước thì chưa mốc nào đủ: mốc 60 giây cần 10.000 thay đổi, mốc 5 phút và mốc một giờ chưa tới thời gian; nên chưa có ảnh mới, Redis khởi động lại từ ảnh cũ.
Bật AOF (`appendonly yes`): với chế độ mặc định `everysec`, khi mất điện thường chỉ mất khoảng một giây ghi cuối; lúc đĩa chậm có thể mất hơn, vì Redis có thể hoãn việc ghi tới hai giây.

</details>

<details>
<summary>Xem sâu hơn: điều đã sửa và bỏ so với bài nguồn</summary>

Bài nguồn liệt kê tám bước: Redis là gì, ai dùng, cách lưu, kiểu dữ liệu, lệnh cơ bản, module, pub/sub, trường hợp dùng. Bài này chạy thử thay vì liệt kê, và sửa ba chỗ: lệnh xóa là `DEL` chứ không phải `DELETE`; JSON là module chứ không có sẵn trong bản đã thử; "vừa lưu bền vừa đọc từ bộ nhớ" chỉ đúng tới mức cấu hình lưu trữ cho phép.
Bài bỏ danh sách công ty dùng Redis và danh sách module vì không có nguồn để đối chiếu; bài cũng không kiểm tra các bản Redis mới hơn 7.0.15, nơi danh sách tính năng có sẵn có thể khác.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-ultimate-redis-101.md): tám bước làm quen với Redis.
- [Redis 7.0.15 — README, tại commit của bản phát hành](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/README.md): Redis là máy chủ cấu trúc dữ liệu, dữ liệu phục vụ từ bộ nhớ và được lưu xuống đĩa, mức bền chỉnh được.
- [Redis 7.0.15 — tệp cấu hình mẫu, tại commit của bản phát hành](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/redis.conf): các mốc `save` mặc định; `appendonly no`; mức mất dữ liệu với AOF.
- [Redis 7.0.15 — mã nguồn vòng chụp ảnh, tại commit của bản phát hành](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/src/server.c): `serverCron` chụp ảnh khi số thay đổi cộng dồn từ ảnh cuối (`server.dirty`) đạt ngưỡng và thời gian từ ảnh cuối vượt số giây của mốc.
- [Redis — tài liệu về độ trễ, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/optimization/latency.md): ở chế độ `everysec`, nếu lần fsync trước chưa xong thì Redis hoãn `write(2)` tới hai giây.
- [Redis — tài liệu pub/sub, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/pubsub/_index.md): giao nhận nhiều nhất một lần; cần giữ tin thì dùng Streams.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; các lệnh chạy cùng ngày với Redis 7.0.15. Bài viết và hình được thiết kế độc lập.

# Memcached và Redis khác nhau thế nào

**Cả memcached và Redis đều giữ dữ liệu trong bộ nhớ và đọc ghi theo khóa. Khác biệt nằm ở chỗ memcached chỉ là bộ nhớ đệm khóa và chuỗi, còn Redis là máy chủ cấu trúc dữ liệu có thể lưu xuống đĩa.**
README của Redis tự mô tả nó như "một memcached phức tạp hơn", với thao tác trên list, set và các cấu trúc có thứ tự thay vì chỉ đặt và lấy. Bài này chạy hai phần mềm cạnh nhau để thấy khác biệt đó cụ thể.

![Ba khung. Khung một, giống nhau: cả hai giữ dữ liệu trong bộ nhớ và đọc ghi theo khóa; đầy thì đẩy khóa cũ ra. Khung hai, khác nhau đã thử: memcached chỉ lưu chuỗi, Redis có thêm hash, list, set, sorted set và bitmap; giá trị 2 MiB bị memcached từ chối vì mặc định tối đa 1 MiB, Redis nhận; khởi động lại thì memcached mất hết, Redis đọc lại ảnh chụp; memcached chạy 4 luồng xử lý, Redis xử lý lệnh trên một luồng chính. Khung ba, bitmap của Redis: một triệu người dùng mỗi người một bit, đánh dấu 300 nghìn người đăng nhập, chiếm 125 nghìn byte.](../../diagrams/sd-06-011-main.svg)

## Từ viết tắt

- **MiB** (Mebibyte) — mebibyte: đơn vị dung lượng bằng 1.048.576 byte (2 mũ 20), gần bằng một triệu byte.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng cỡ một triệu byte; ở đây là giới hạn bộ nhớ đặt cho memcached.
- **RDB** (Redis DataBase) — tệp ảnh chụp toàn bộ dữ liệu của Redis tại một thời điểm, dùng để nạp lại sau khi khởi động.

## Thử cạnh nhau

Ngày 2026-10-18, trên một máy, với memcached 1.6.24 và Redis 7.0.15, cấu hình mặc định.

| Điều thử | memcached | Redis |
|---|---|---|
| Lưu và đọc một chuỗi | được | được |
| Tăng một bộ đếm (`incr` trên giá trị "1") | được, ra 2 | được (`INCR`) |
| Một lệnh kiểu hash (`hset`) | `ERROR`: không có lệnh này | được (`HSET`) |
| Giá trị 2 MiB | `SERVER_ERROR object too large for cache` (giới hạn mặc định 1 MiB, `item_size_max` 1048576) | được |
| Khởi động lại máy chủ | khóa mất hết | đọc lại tệp RDB, khóa còn |
| Số luồng xử lý | 4 (mặc định của `-t`) | một luồng chính xử lý lệnh |

**Cả hai đều đẩy khóa ra khi đầy.** Cho memcached giới hạn 2 MB rồi ghi 5.000 giá trị 1.000 byte: cả 5.000 lần ghi đều thành công, 3.230 khóa cũ bị đẩy ra, còn lại 1.770. Bật cờ `-M` (tắt đẩy ra): chỉ 1.770 lần ghi thành công, 3.230 lần còn lại báo `SERVER_ERROR out of memory storing object`. Redis có lựa chọn tương tự qua `maxmemory-policy`.

**Bitmap: một bit cho mỗi người dùng.** Bài nguồn gợi ý dùng bitmap của Redis để lưu trạng thái có hoặc không của rất nhiều người. Thử với 1 triệu mã người dùng, đánh dấu ngẫu nhiên 300.000 người đăng nhập bằng `SETBIT`: `BITCOUNT` trả 300.000, chuỗi dài 125.000 byte (1 triệu bit chia 8), và `MEMORY USAGE` báo 163.912 byte kể cả phần quản lý của Redis. memcached không có thao tác trên từng bit.

## Chọn cái nào

- Chỉ cần bộ nhớ đệm chuỗi đơn giản, giá trị nhỏ, mất khi khởi động lại cũng không sao: memcached đủ, và nó chạy nhiều luồng ngay từ mặc định.
- Cần cấu trúc dữ liệu (đếm theo trường, xếp hạng, tập không trùng, bitmap), giá trị lớn hơn 1 MiB, hoặc giữ dữ liệu qua khởi động lại: Redis.

## Giới hạn cần nhớ

Bài chỉ thử cấu hình mặc định trên một máy, không đo tốc độ. Phần lớn khác biệt chỉnh được: giới hạn kích thước của memcached đổi bằng `-I`, Redis có thể tắt lưu xuống đĩa, và Redis có tùy chọn thêm luồng cho phần đọc ghi mạng (`io-threads`, mặc định 1 trong bản đã thử). Đừng chọn theo bảng so sánh mà không thử với dữ liệu và tải của mình.

## Nhìn hình trả lời

Bạn cần đếm lượt thích của mỗi bài viết và lấy ra 10 bài nhiều lượt thích nhất trong ngày. Làm trên memcached thì phải làm gì, còn trên Redis thì sao?

<details>
<summary>Xem đáp án</summary>

Trên memcached, `incr` đếm được từng bài, nhưng nó không biết sắp xếp: muốn lấy 10 bài cao nhất, ứng dụng phải tự đọc hết các bộ đếm rồi tự sắp xếp, hoặc giữ một danh sách riêng ở nơi khác.
Trên Redis, một sorted set làm cả hai việc: tăng điểm của bài khi có lượt thích (`ZINCRBY`) và lấy 10 bài cao nhất (`ZREVRANGE ... 0 9`).

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn là một hình so sánh và bốn ví dụ dùng cấu trúc dữ liệu của Redis (hash, zset, bitmap). Bài này kiểm từng khác biệt bằng cách chạy cả hai phần mềm, và đo thử ví dụ bitmap.
Bài không so tốc độ vì một phép đo trên một máy dễ gây hiểu lầm; cũng không bàn sao chép dữ liệu hay chạy cụm, hai chủ đề mà một bài so sánh đầy đủ cần có.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/memcached-vs-redis.md): khác biệt giữa Redis và memcached, bốn ví dụ dùng cấu trúc dữ liệu của Redis.
- [Redis 7.0.15 — README, tại commit của bản phát hành](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/README.md): máy chủ cấu trúc dữ liệu, lưu xuống đĩa; "một memcached phức tạp hơn".
- [memcached 1.6.24 — README, tại commit của bản phát hành](https://github.com/memcached/memcached/blob/1b3b8555734f9b7b8d979924c7f8d6cf82194ba8/README.md): kho khóa và giá trị chạy nhiều luồng, hướng sự kiện, dùng làm bộ nhớ đệm; vào ra mạng không chặn, không làm vào ra đĩa.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày. Bài viết và hình được thiết kế độc lập.

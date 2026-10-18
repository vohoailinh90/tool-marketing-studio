# Kiến trúc Redis lớn dần thế nào: mỗi bước vá một giới hạn

**Redis bắt đầu là một tiến trình trên một máy, giữ dữ liệu trong bộ nhớ. Mỗi lớp thêm vào về sau vá một giới hạn của lớp trước, và mang theo một giới hạn mới.**
Học theo thứ tự "giới hạn nào, vá bằng gì" dễ nhớ hơn học danh sách tính năng. Phần thử nghiệm chạy trên Redis 7.0.15, cả cụm nằm trên một máy.

![Hai phần xếp dọc. Phần một, bốn bước đánh số nối nhau: 1 lưu xuống đĩa bằng RDB và AOF vì khởi động lại là mất hết; 2 nhân bản, bản sao chép bất đồng bộ, vì một máy chết là ngừng phục vụ; 3 Sentinel bỏ phiếu và nâng bản sao lên vì đổi chủ bằng tay chậm; 4 cluster chia 16384 khe cho nhiều máy chủ vì dữ liệu vượt một máy. Phần hai, bốn kết quả thử trên Redis 7.0.15: tắt bản sao thì máy chủ vẫn trả lời thành công nhưng lệnh chờ báo 0 bản sao nhận; tắt máy chủ thì ba Sentinel nâng bản sao lên sau 3,3 giây; gửi khóa tới nhầm nút thì lỗi trả về chỉ sang nút giữ khe đó; một lệnh ghi hai khóa ở hai khe bị từ chối, còn hai khóa cùng thẻ băm thì được.](../../diagrams/sd-06-018-main.svg)

## Từ viết tắt

- **RDB** (Redis DataBase) — tệp ảnh chụp của Redis: toàn bộ dữ liệu tại một thời điểm, ghi gọn vào một tệp.
- **AOF** (Append Only File) — tệp chỉ ghi nối thêm: nhật ký các lệnh làm đổi dữ liệu, chạy lại khi khởi động để dựng lại dữ liệu.

## Đọc hình

**1 · Lưu xuống đĩa.** Redis chỉ giữ dữ liệu trong bộ nhớ thì khởi động lại là mất hết, và cơ sở dữ liệu phía sau phải đón toàn bộ truy vấn. RDB chụp ảnh định kỳ, AOF ghi lại từng lệnh; chi tiết ở bài [Redis giữ dữ liệu qua lần sập thế nào](../sd-06-019/lesson.md).

**2 · Nhân bản.** Đĩa giữ được dữ liệu, nhưng máy chết thì vẫn ngừng phục vụ. Bản sao (replica) chép dữ liệu từ máy chủ (master) và mặc định chỉ cho đọc. Việc chép là bất đồng bộ: máy chủ trả lời "thành công" mà không chờ bản sao. Lệnh `WAIT` cho biết bao nhiêu bản sao đã nhận một lần ghi.

**3 · Sentinel.** Có bản sao rồi, ai nâng nó lên khi máy chủ chết? Sentinel là các tiến trình riêng làm bốn việc: theo dõi, báo động, tự chuyển đổi dự phòng, và cho máy khách biết địa chỉ máy chủ hiện tại. Đủ số Sentinel đồng ý (quorum) thì máy chủ bị coi là đã chết; muốn chuyển đổi thật, một Sentinel còn phải được đa số các Sentinel bầu làm người dẫn.

**4 · Cluster.** Nhân bản chỉ thêm bản chép: mọi lệnh ghi vẫn dồn về một máy chủ, và dữ liệu vẫn phải vừa bộ nhớ một máy. Redis Cluster chia không gian khóa thành 16384 khe, khe của một khóa là `CRC16(key) mod 16384`, trừ khi khóa có thẻ băm: nếu tên khóa chứa một đoạn `{...}` không rỗng thì chỉ phần trong ngoặc được băm (vì vậy `{user:1}:cart` và `{user:1}:orders` rơi vào cùng khe), và mỗi máy chủ giữ một phần các khe (mỗi máy chủ có thể có bản sao riêng).

**Thử nghiệm.** Tắt bản sao rồi ghi: máy chủ vẫn trả `OK`, còn `WAIT 1 500` trả 0. Ba Sentinel với quorum 2, ngưỡng 2 giây không trả lời: tắt máy chủ (`SHUTDOWN NOSAVE`) thì sau 3,3 giây bản sao thành máy chủ mới và vẫn còn khóa đã ghi. Cụm ba nút chia 0–5460, 5461–10922, 10923–16383; ghi `user:2` vào nút đầu thì nhận `MOVED 6777 127.0.0.1:7202`; `MSET user:1 a user:2 b` bị lỗi `CROSSSLOT`; `{user:1}:cart` và `{user:1}:orders` cùng khe 10778 nên `MSET` chạy được.

## Giới hạn cần nhớ

Không bước nào giữ được mọi lần ghi đã báo thành công. Sentinel và Cluster đều dựa trên chép bất đồng bộ, nên một lần ghi máy chủ đã trả lời vẫn có thể mất nếu máy chủ chết trước khi bản sao nhận. Tài liệu Redis nói `WAIT` giảm mạnh khả năng đó nhưng không biến Redis thành hệ nhất quán mạnh. Cluster còn đổi cách viết ứng dụng: lệnh nhiều khóa chỉ chạy khi mọi khóa nằm cùng khe, và máy khách phải biết đi theo lỗi chuyển hướng.

## Nhìn hình trả lời

Một cửa hàng dùng một Redis duy nhất, đã bật AOF, để giữ giỏ hàng. Ổ đĩa của máy hỏng, cả trang ngừng cho tới khi dựng xong máy mới. Bước nào trong hình nhắm vào sự cố này, và nó vẫn chưa bảo đảm điều gì?

<details>
<summary>Xem đáp án</summary>

Bước 2 và 3: một bản sao trên máy khác để có sẵn máy thay, và Sentinel để nâng bản sao lên mà không chờ người. AOF (bước 1) không giúp vì đĩa chứa nó hỏng theo máy.
Điều chưa bảo đảm: vì chép bất đồng bộ, vài lần ghi cuối trước sự cố có thể chưa tới bản sao và mất khi nó được nâng lên. Bước 4 không cần cho sự cố này: nó giải bài toán dữ liệu hay lượng ghi vượt một máy, không phải bài toán máy hỏng.

</details>

<details>
<summary>Xem sâu hơn: mốc phiên bản, đối chiếu với bài nguồn</summary>

- Kho mã Redis có commit đầu tiên ngày 22/3/2009. Ở thẻ 1.3.6 (3/2010), `redis.conf` đã có mốc lưu RDB (`save`), `appendonly`, `appendfsync` và `slaveof`; tài liệu Redis ghi AOF có từ bản 1.1. Bài nguồn xếp lưu xuống đĩa và nhân bản vào bản 2.8 năm 2013, không khớp các tệp này.
- 2.6.0 (10/2012) đã có tệp `sentinel.conf`. 2.8.0 (22/11/2013) mang Sentinel viết lại (tài liệu gọi là Sentinel 2, bản ổn định từ 2.8) và cho bản sao đồng bộ lại một phần sau khi mất kết nối ngắn, thay vì chép lại toàn bộ.
- 3.0.0 (1/4/2015): Redis Cluster, cùng lệnh `WAIT`.
- 5.0.0 (17/10/2018): kiểu dữ liệu stream (bài nguồn ghi 2017).
- 6.0.0 (30/4/2020): có thể giao việc đọc và ghi socket của máy khách cho các luồng I/O phụ, mặc định tắt; `redis.conf` của bản này vẫn mô tả Redis "phần lớn là đơn luồng". Bài [Vì sao Redis nhanh](../sd-06-021/lesson.md) nói tiếp chuyện này.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-redis-architecture-evolve.md): các mốc độc lập, lưu xuống đĩa, nhân bản, Sentinel, cluster và luồng I/O.
- Tài liệu Redis tại commit cố định của kho tài liệu: [Replication](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/replication.md) (bất đồng bộ, `WAIT`, bản sao chỉ đọc), [Sentinel](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/sentinel.md) (bốn việc, quorum và đa số, Sentinel 2 ổn định từ 2.8), [Cluster specification](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/reference/cluster-spec.md) (16384 khe, `CRC16`, thẻ băm, lỗi `MOVED`, khoảng có thể mất lần ghi), [Persistence](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/persistence.md) (AOF từ bản 1.1).
- Kho mã Redis: `redis.conf` ở [thẻ 1.3.6](https://github.com/redis/redis/blob/7b7f987e9184645f64f766b7f8f7eb02a9a69552/redis.conf) và [thẻ 6.0.0](https://github.com/redis/redis/blob/17dfd7cabbf7954f92b7a1243d4bb27fee5d4500/redis.conf); ghi chú phát hành ở [2.8.0](https://github.com/redis/redis/blob/4e6d34bd2ccd8998335baefb6be08e1704a839d2/00-RELEASENOTES), [3.0.0](https://github.com/redis/redis/blob/1fab07e078f35e175b8b09db3955dd654ced82c2/00-RELEASENOTES), [5.0.0](https://github.com/redis/redis/blob/882ca6962f4ca32683b0e8db831de1b425c27d3c/00-RELEASENOTES), [6.0.0](https://github.com/redis/redis/blob/17dfd7cabbf7954f92b7a1243d4bb27fee5d4500/00-RELEASENOTES); tệp `sentinel.conf` ở [thẻ 2.6.0](https://github.com/redis/redis/blob/5eec376c2f56dbf617cc8bc19476fd5431cd664d/sentinel.conf).

Thử nghiệm chạy ngày 2026-10-18 với gói Redis 7.0.15 của Ubuntu: mọi tiến trình trên một máy, không có độ trễ mạng thật, nên 3,3 giây chỉ phản ánh cấu hình ngưỡng 2 giây của lần thử, không phải con số chung. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

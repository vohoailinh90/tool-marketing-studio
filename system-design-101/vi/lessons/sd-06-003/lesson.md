# Khóa lớn ảnh hưởng thế nào tới việc lưu AOF của Redis

**Khi bật AOF, mỗi lệnh ghi của Redis được chép thêm vào một tệp nhật ký. Khóa càng lớn thì bản ghi càng lớn, và phần chép đó chạy trên chính luồng đang phục vụ mọi client.**
Câu hỏi hay gặp là: chọn chế độ `everysec` hay `no` thì khóa lớn có còn làm Redis khựng lại không? Tài liệu của Redis và một phép đo nhỏ cho câu trả lời là *có*.

![Ba khung. Khung một, bốn bước của một lệnh ghi khi bật AOF: Redis đổi dữ liệu trong bộ nhớ; luồng chính gọi write để chép bản ghi vào bộ đệm của hệ điều hành; fsync đẩy xuống đĩa, ở always thì luồng chính làm trước khi trả lời, ở everysec thì luồng nền làm mỗi giây, ở no thì hệ điều hành tự quyết; rồi Redis trả lời. Khung hai, ba chế độ: always an toàn và chậm nhất; everysec là mặc định, có thể mất khoảng một giây dữ liệu; no để hệ điều hành quyết. Khung ba, đo với giá trị 5 MiB trên một máy ảo: tắt AOF, lệnh ghi mất khoảng 6 mili giây; bật AOF ở cả ba chế độ, riêng bước write trên luồng chính mất hàng chục mili giây; chỉ always có thêm fsync; client khác chờ theo.](../../diagrams/sd-06-003-main.svg)

## Từ viết tắt

- **AOF** (Append Only File) — tệp chỉ ghi thêm: nhật ký mà Redis nối từng lệnh ghi vào cuối, để khi khởi động lại thì đọc lại và dựng lại dữ liệu.
- **MiB** (Mebibyte) — mebibyte: đơn vị dung lượng bằng 1.048.576 byte (2 mũ 20), gần bằng một triệu byte.

## Đọc hình

**Khóa lớn** là một khóa giữ nhiều dữ liệu, ví dụ một chuỗi 5 MiB. Redis xử lý lệnh trên một luồng chính, nên lệnh nào chiếm luồng lâu thì mọi client khác phải chờ.

Tài liệu về độ trễ của Redis nói AOF dùng hai lời gọi hệ thống. `write(2)` chép bản ghi vào bộ đệm của hệ điều hành; `fdatasync(2)` (một dạng fsync) ép bộ đệm đó xuống đĩa. **Cả hai đều có thể gây trễ.** Ba chế độ `appendfsync` chỉ khác nhau ở bước fsync:

- `always`: fsync sau mỗi lần ghi, *trước khi* trả lời client. An toàn nhất, chậm nhất.
- `everysec` (mặc định): một luồng nền fsync mỗi giây. Nếu lần fsync trước chưa xong, Redis hoãn `write(2)` tối đa hai giây rồi vẫn ghi, và lúc đó luồng chính có thể bị chặn.
- `no`: không gọi fsync, để hệ điều hành tự quyết; theo tài liệu persistence, Linux thường đẩy xuống đĩa khoảng 30 giây một lần. Nguồn trễ còn lại là `write(2)`.

Điểm chung dễ bị bỏ qua: **ở cả ba chế độ, `write(2)` chạy trên luồng chính.** Khóa 5 MiB nghĩa là mỗi lần ghi phải chép 5 MiB vào tệp nhật ký.

## Đo thử

Ngày 2026-10-18, bài chạy Redis 7.0.15 trên một máy ảo (ổ đĩa ext4), tắt việc tự viết lại AOF để không lẫn với việc khác. Một client ghi đè lặp lại các giá trị 5 MiB; một tiến trình khác gửi lệnh `PING` mỗi mili giây để đo xem nó phải chờ bao lâu. Bộ theo dõi độ trễ có sẵn của Redis (`latency-monitor-threshold 1`) ghi lại việc nào trong Redis vượt 1 mili giây.

| Cấu hình | Một lệnh ghi 5 MiB (trung vị) | `PING` của client khác (p99) | Redis tự ghi nhận |
|---|---|---|---|
| Tắt AOF | khoảng 6 ms | dưới 0,6 ms | không có sự kiện nào |
| AOF `always` | 34–36 ms | 29–32 ms | `aof-write` tới 31–69 ms; `aof-fsync-always` 9–19 ms |
| AOF `everysec` | 27–34 ms | 22–29 ms | `aof-write` tới 29–60 ms |
| AOF `no` | 28–31 ms | 22–26 ms | `aof-write` tới 30–46 ms |

Mỗi khoảng là ba lần chạy, mỗi lần 40 lệnh ghi cách nhau 50 ms. Chạy lại với một lệnh ghi mỗi nửa giây (ít áp lực lên đĩa hơn), `aof-write` vẫn tới 28–31 ms ở cả ba chế độ.
Sự kiện `aof-write` là thời gian của chính lời gọi `write(2)` trên luồng chính; `aof-fsync-always` chỉ xuất hiện ở chế độ `always`. Đọc 5 MiB bằng `GET` (không ghi AOF) chỉ mất khoảng 3,5 ms.

Kết luận cho máy này: chế độ fsync quyết định Redis có chờ đĩa trước khi trả lời hay không, còn cái giá của việc chép một khóa lớn vào nhật ký thì cả ba chế độ đều phải trả. Đây là số đo trên một máy, ổ đĩa ảo, một phiên bản; máy khác sẽ ra số khác, nhưng hướng thì tài liệu của Redis cũng nói.

## Giới hạn cần nhớ

Đổi `always` sang `everysec` giúp các lệnh ghi *nhỏ* nhanh hơn rõ rệt, nhưng không làm khóa lớn hết hại. Cách chữa tận gốc là đừng tạo khóa lớn: chia một giá trị lớn thành nhiều khóa nhỏ, hoặc đặt dữ liệu lớn ở nơi khác và chỉ giữ tham chiếu trong Redis.

## Nhìn hình trả lời

Một dịch vụ dùng `appendfsync everysec` và mỗi phút ghi đè một khóa 20 MiB chứa toàn bộ danh mục sản phẩm. Người dùng thấy cứ khoảng một phút lại có một nhịp chậm. Đổi sang `appendfsync no` có hết không?

<details>
<summary>Xem đáp án</summary>

Nhiều khả năng là không hết. Ở cả hai chế độ, luồng chính vẫn phải `write(2)` một bản ghi 20 MiB vào AOF, và trong lúc đó mọi client khác phải chờ. `no` chỉ bỏ phần fsync vốn đã chạy ở luồng nền.
Nên chia danh mục thành nhiều khóa nhỏ (mỗi sản phẩm một khóa, hoặc theo trang) để mỗi lần ghi chỉ chép phần thay đổi.

</details>

<details>
<summary>Xem sâu hơn: điều đã sửa so với bài nguồn, và cách đo</summary>

Bài nguồn nói ở chế độ `everysec` và `no` khóa lớn "không ảnh hưởng tới luồng chính". Tài liệu về độ trễ của Redis và phép đo ở trên đều không ủng hộ câu đó: phần fsync rời khỏi luồng chính, nhưng phần `write(2)` thì không.
Khi để Redis tự viết lại AOF như mặc định, phép đo còn thấy sự kiện `fork` và `aof-write-active-child`: khóa lớn làm tệp nhật ký phình nhanh nên việc viết lại chạy thường hơn. Bài không đo riêng hiệu ứng này.

Cách đo, để tự thử: chạy `redis-server --appendonly yes --appendfsync everysec`, đặt `CONFIG SET latency-monitor-threshold 1`, ghi vài lần một giá trị cỡ 5 MiB, rồi xem `LATENCY LATEST`. Trong lúc ghi, `redis-cli --latency` ở một cửa sổ khác cho thấy client khác phải chờ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-big-keys-impact-redis-persistence.md): ba chế độ AOF và nhận định về khóa lớn.
- [Redis — tài liệu về độ trễ, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/optimization/latency.md): mục "Latency due to AOF and disk I/O", hai lời gọi `write(2)` và `fdatasync(2)`, cách mỗi chế độ fsync gây trễ.
- [Redis — tài liệu persistence, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/persistence.md): ba chế độ `appendfsync`, mặc định `everysec`, mức mất dữ liệu.
- [Redis 7.0.15 — tệp cấu hình mẫu, tại commit của bản phát hành](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/redis.conf): `appendfsync everysec` là mặc định; chú thích về `no-appendfsync-on-rewrite`.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày với Redis 7.0.15. Bài viết và hình được thiết kế độc lập.

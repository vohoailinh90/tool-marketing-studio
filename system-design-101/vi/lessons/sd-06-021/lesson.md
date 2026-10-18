# Vì sao Redis nhanh, và khi nào nó chậm

**Redis nhanh vì ba điều đi cùng nhau: dữ liệu nằm trong bộ nhớ, một luồng chạy lần lượt mọi lệnh, và giá trị nhỏ được lưu ở dạng gọn. Chính điều thứ hai cũng là lý do một lệnh chậm làm mọi máy khách chờ.**
Các con số dưới đây đo trên một máy Linux 4 nhân với Redis 7.0.15; chúng cho thấy hướng thay đổi, không phải tốc độ Redis sẽ đạt trên máy của bạn.

![Hai phần. Phần một, ba lý do Redis nhanh, mỗi lý do một thẻ có biểu tượng: dữ liệu trong RAM nên đọc ghi không chờ đĩa, đĩa chỉ để lưu bản sao; một luồng chạy lệnh, một vòng lặp sự kiện nghe mọi kết nối và chạy lần lượt từng lệnh; dạng lưu gọn, giá trị nhỏ nằm liền một khối như listpack và intset. Phần hai, ba kết quả đo trên máy thử: gửi 16 lệnh mỗi lượt thì số lệnh mỗi giây tăng khoảng 9 lần; quét 2 triệu khóa mất 1,6 giây và lệnh khác phải xếp hàng chờ; bảng băm 512 trường chiếm 6192 byte, thêm 1 trường thì chiếm 28816 byte.](../../diagrams/sd-06-021-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần chạy lệnh của máy; một máy có nhiều nhân CPU chạy song song được.
- **RAM** (Random Access Memory) — bộ nhớ trong của máy: nơi Redis giữ toàn bộ dữ liệu khi chạy, truy cập nhanh hơn đĩa nhiều nhưng ít và đắt hơn.

## Đọc hình

**Dữ liệu trong bộ nhớ.** Mọi lệnh đọc ghi chạm vào dữ liệu trong RAM; đĩa chỉ dùng để lưu bản sao (xem [Redis giữ dữ liệu qua lần sập thế nào](../sd-06-019/lesson.md)). Cái giá là dữ liệu phải vừa bộ nhớ.

**Một luồng chạy lệnh.** Một tiến trình phục vụ mọi kết nối bằng kỹ thuật dồn kênh (multiplexing): một vòng lặp sự kiện hỏi hệ điều hành kết nối nào đã có dữ liệu (trên Linux là `epoll`), đọc lệnh, chạy, rồi trả lời. Tại mỗi thời điểm chỉ một lệnh chạy, nên không cần khóa để giữ dữ liệu đúng. Tài liệu Redis nói thêm điều quan trọng: Redis nhanh chủ yếu vì không đứng chờ các lời gọi hệ thống như đọc hay ghi socket, và vì mỗi lệnh thông thường như `GET`, `SET` chạy trong thời gian rất ngắn.

**Dạng lưu gọn.** Bảng băm, tập hợp hay danh sách nhỏ được lưu liền một khối (`listpack`; tập hợp chỉ có số nguyên thì `intset`) thay vì bảng băm thật với con trỏ cho từng phần tử. Quá ngưỡng (`hash-max-listpack-entries`, mặc định 512) thì Redis đổi sang dạng thường.

**Đo.** Với 50 kết nối, `redis-benchmark` cho khoảng 66 nghìn lệnh `SET` mỗi giây khi mỗi lượt gửi một lệnh, và khoảng 593 nghìn khi gom 16 lệnh mỗi lượt (pipelining). Tài liệu Redis giải thích: mỗi lượt đi về tốn thời gian chờ mạng và tốn lời gọi hệ thống `read()`, `write()` để đọc ghi socket, nên gom lệnh giảm cả hai; phần chạy lệnh thì không đổi. Với 2 triệu khóa, `KEYS *` chạy 1,57 giây (theo nhật ký lệnh chậm), và một `PING` gửi ngay sau đó phải chờ 1,54 giây. Bảng băm 512 trường còn ở dạng `listpack`, chiếm 6192 byte; trường thứ 513 đổi nó sang `hashtable`, 28816 byte.

## Giới hạn cần nhớ

Một luồng nghĩa là một lệnh chậm chặn tất cả. Tài liệu Redis chỉ ra nguồn chậm hay gặp nhất là `KEYS` trên hệ thống thật, và khuyên kiểm độ phức tạp của lệnh, dùng `SCAN` để duyệt dần, theo dõi bằng nhật ký lệnh chậm (`SLOWLOG`). Một luồng cũng có nghĩa là một tiến trình chỉ dùng một nhân để chạy lệnh; muốn dùng nhiều nhân thì chạy nhiều tiến trình hoặc chia dữ liệu.

## Nhìn hình trả lời

Một dịch vụ dùng Redis báo "thỉnh thoảng mọi yêu cầu cùng chậm khoảng một giây rồi lại bình thường", dù lưu lượng không tăng. Theo hình, bạn nghi gì trước và kiểm bằng cách nào?

<details>
<summary>Xem đáp án</summary>

Nghi một lệnh chậm chạy trên luồng duy nhất: mọi lệnh khác phải xếp hàng sau nó, nên tất cả cùng chậm một lúc. Kiểm bằng `SLOWLOG GET` để xem lệnh nào chạy lâu, và độ phức tạp của lệnh đó; ứng viên quen thuộc là `KEYS *` hay một lệnh trên tập rất lớn. Cách chữa: đổi sang `SCAN` hoặc chia nhỏ dữ liệu, và chuyển truy vấn nặng sang bản sao.

</details>

<details>
<summary>Xem sâu hơn: "đơn luồng" chính xác đến đâu</summary>

- Redis là "phần lớn đơn luồng": từ 2.4 đã có luồng phụ cho vài việc đĩa chậm, từ 4.0 có xóa đối tượng ở nền (`UNLINK`). Việc chạy lệnh vẫn nằm trên một luồng.
- Từ 6.0 có thể giao việc đọc và ghi socket cho các luồng I/O phụ (`io-threads`, mặc định 1, tức là tắt). `redis.conf` khuyên chỉ bật khi máy có từ 4 nhân và Redis thật sự thiếu CPU.
- Vòng lặp sự kiện chọn cơ chế dồn kênh tốt nhất hệ điều hành có: `evport`, rồi `epoll`, rồi `kqueue`, cuối cùng là `select`.
- Bài nguồn so tốc độ bộ nhớ với ổ đĩa bằng một con số cố định; bài này không lặp lại con số đó vì chưa đo. Bài về các con số độ trễ cùng nhóm bàn chuyện này.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/why-is-redis-so-fast.md): ba lý do, bộ nhớ, dồn kênh và đơn luồng, cấu trúc dữ liệu.
- Tài liệu Redis tại commit cố định của kho tài liệu: [Diagnosing latency issues](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/optimization/latency.md) (đơn luồng, dồn kênh, lệnh chậm, `KEYS`), [FAQ](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/get-started/faq.md) (dùng nhiều nhân, luồng từ 4.0), [Pipelining](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/using-commands/pipelining.md) (thời gian đi về và lời gọi hệ thống đọc ghi socket), [Memory optimization](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/optimization/memory-optimization.md) (mã hóa đặc biệt cho tập hợp nhỏ, ngưỡng 512).
- Redis 7.0.15: [`src/ae.c`](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/src/ae.c) (chọn cơ chế dồn kênh) và [`redis.conf`](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/redis.conf) (mục `THREADED I/O`, ngưỡng `listpack`).

Thử nghiệm chạy ngày 2026-10-18: gói Redis 7.0.15 của Ubuntu, `redis-benchmark` và `redis-cli` chạy cùng máy qua giao diện mạng nội bộ, 4 nhân, `io-threads` 1; thời gian `PING` đo từ phía `redis-cli` nên gồm cả lúc khởi động chương trình (khoảng 10 ms khi Redis rảnh). Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

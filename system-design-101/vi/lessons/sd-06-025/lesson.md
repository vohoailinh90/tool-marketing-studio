# Các con số độ trễ nên biết: nhớ bậc, rồi tự đo

**Bảng "con số độ trễ ai cũng nên biết" hữu ích ở chỗ nó cho thấy các bậc: bộ nhớ đệm của CPU tính bằng nano giây, mạng và đĩa tính bằng micro giây, ghi bền vào cơ sở dữ liệu cỡ mili giây, đi xuyên lục địa cỡ trăm mili giây. Con số cụ thể thì khác theo từng máy, nên bài này đo lại trên một máy chủ đám mây.**
Chính bài nguồn cũng ghi các con số của nó không chính xác, chỉ lấy từ vài bài đo trên mạng.

![Ba phần. Phần một, bốn bậc đo trên máy thử, nối nhau từ nhanh tới chậm: bộ nhớ đệm của CPU, vùng 16 KB 1,5 nano giây, vùng 256 KB 3,9 nano giây; RAM, đọc ngẫu nhiên vùng 512 MB khoảng 315 nano giây; mạng nội bộ máy, gửi 1 KB rồi nhận lại khoảng 60 micro giây; đĩa ảo, đọc ngẫu nhiên 4 KB 60 micro giây, ghi kèm fsync 440 micro giây. Phần hai, chậm hơn nữa: ghi bền một dòng vào SQLite kèm commit khoảng 1,3 mili giây; xuyên lục địa, bài nguồn ước 100 mili giây một vòng California, Hà Lan, không đo ở đây. Phần ba, ba điều cần nhớ: nhớ bậc nano, micro, mili giây và giây, mỗi bậc gấp nghìn lần bậc trước; bước chậm nằm trong vòng lặp thì nhân lên theo số vòng; máy của bạn sẽ ra số khác, hãy đo.](../../diagrams/sd-06-025-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm; bên trong có các tầng bộ nhớ đệm nhỏ và rất nhanh (L1, L2, L3).
- **RAM** (Random Access Memory) — bộ nhớ trong của máy, lớn hơn và chậm hơn bộ nhớ đệm của CPU.
- **KB** (KiloByte) — kilobyte: khoảng một nghìn byte.
- **MB** (MegaByte) — megabyte: khoảng một triệu byte.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc dùng với cơ sở dữ liệu quan hệ; SQLite là một cơ sở dữ liệu SQL nằm gọn trong một tệp.
- **SSD** (Solid-State Drive) — ổ đĩa thể rắn: lưu dữ liệu trên chip nhớ thay vì đĩa quay, đọc ngẫu nhiên nhanh hơn ổ cứng cơ.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền tải: cách hai chương trình gửi dữ liệu cho nhau tin cậy qua mạng.

## Đọc hình

**Đơn vị.** 1 ns (nano giây) là một phần tỷ giây; 1 µs (micro giây) bằng 1000 ns; 1 ms (mili giây) bằng 1000 µs. Mỗi bậc chậm hơn bậc trước một nghìn lần.

**Thử nghiệm**, ngày 2026-10-18, trên một máy ảo Linux có 4 nhân Xeon, đĩa ảo:

- **Bộ nhớ:** một chương trình C đi theo chuỗi con trỏ xáo trộn, mỗi bước phải chờ bước trước. Vùng 16 KB (vừa bộ nhớ đệm L1): 1,5 ns mỗi lần đọc; 256 KB (vừa L2): 3,9 ns; 4 MB: khoảng 99 ns; 512 MB: khoảng 315 ns. Con số cuối cao hơn mức "100 ns cho RAM" của bài nguồn; một lý do có thể là đọc ngẫu nhiên vùng lớn còn tốn thêm việc tra bảng trang, và trên máy ảo việc đó đắt hơn (bài không đo riêng phần này).
- **Mạng trong cùng máy:** gửi 1 KB qua TCP trên giao diện nội bộ (loopback) rồi nhận lại: trung vị 58,5 µs (chương trình Python). Lệnh `GET` một giá trị 1 KB của Redis qua cùng đường: p50 63 µs.
- **Đĩa:** đọc ngẫu nhiên 4 KB, bỏ qua bộ đệm của hệ điều hành (`O_DIRECT`): trung vị 60 µs. Ghi 4 KB rồi `fsync` để chắc dữ liệu đã xuống đĩa: trung vị 443 µs.
- **Ghi bền vào cơ sở dữ liệu:** SQLite, `synchronous=FULL`, chế độ nhật ký mặc định `journal_mode=DELETE`, mỗi lần một `INSERT` rồi `COMMIT`: trung vị 1,31 ms. Theo dõi bằng `strace`, một lần commit gọi `fdatasync` bốn lần, nên nó tốn cỡ vài lần bậc "ghi rồi ép xuống đĩa" ở trên.

## Giới hạn cần nhớ

Các con số trên chỉ đúng cho máy đã đo, và máy đám mây cho kết quả khác máy để bàn có ổ SSD gắn trực tiếp, hay mạng thật giữa hai máy. Bài không đo được đường xuyên lục địa; con số 100 ms là ước lượng của bài nguồn. Con số cũng không cộng thẳng được: hệ thống thật chạy nhiều việc song song và có bộ đệm ở nhiều tầng. Điều đáng nhớ là bậc, để biết bước nào là nút thắt.

## Nhìn hình trả lời

Một trang hiển thị danh sách 50 đơn hàng. Mã nguồn lấy danh sách bằng một truy vấn, rồi với mỗi đơn lại gọi một truy vấn riêng tới cơ sở dữ liệu ở máy khác trong cùng trung tâm dữ liệu để lấy tên khách. Theo thang độ trễ, chỗ nào đáng sửa trước?

<details>
<summary>Xem đáp án</summary>

Năm mươi lượt đi về tới máy khác nằm trong vòng lặp. Mỗi lượt ít nhất là bậc micro giây tới mili giây (mạng giữa hai máy chậm hơn loopback đo ở trên), nhân lên 50 lần, trong khi vài phép xử lý trong bộ nhớ chỉ ở bậc nano giây. Gộp thành một truy vấn lấy tên khách cho cả 50 đơn (một lượt đi về) thường lợi hơn nhiều so với tối ưu phần tính toán.

</details>

<details>
<summary>Xem sâu hơn: đối chiếu với bảng của bài nguồn</summary>

- Bài nguồn: bộ nhớ đệm L1, L2 1 ns, 10 ns; RAM 100 ns; gửi 1 KB qua mạng 1 Gbps (gigabit mỗi giây) 10 µs; đọc từ SSD 100 µs; ghi vào cơ sở dữ liệu 1 ms; gói tin California – Hà Lan – California 100 ms; chu kỳ làm mới của hệ thống giám sát 1–10 giây.
- Đo ở đây cùng bậc với bảng ở bộ nhớ đệm, đĩa và ghi bền; RAM chậm hơn vì cách đo (đọc ngẫu nhiên vùng lớn).
- 10 µs cho 1 KB trên mạng 1 Gbps là thời gian đẩy 8000 bit lên đường truyền (8000 / 10⁹ giây = 8 µs), chưa tính thời gian đi đường và xử lý; con số loopback đo ở trên chủ yếu là chi phí phần mềm.
- Bài nguồn nói Grafana mặc định làm mới 5–10 giây. Tệp cấu hình mặc định của Grafana có `min_refresh_interval = 5s`, tức là mức làm mới *nhanh nhất được phép* cho một bảng điều khiển, không phải mức mặc định.
- Tài liệu Redis về pipelining cũng nhắc: dù qua loopback, thời gian đi về dưới một mili giây vẫn cộng dồn thành nhiều khi gửi nhiều lệnh nối nhau.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/which-latency-numbers-should-you-know.md): bảng độ trễ và lời lưu ý rằng các con số không chính xác.
- [Grafana — `conf/defaults.ini`, tại commit cố định](https://github.com/grafana/grafana/blob/3920186ffd305507ae78ea7f035d0197e71d929f/conf/defaults.ini): `min_refresh_interval = 5s`.
- [Redis — Pipelining, tại commit cố định của kho tài liệu](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/using-commands/pipelining.md): thời gian đi về qua loopback và chi phí cộng dồn.

Thử nghiệm chạy ngày 2026-10-18: chương trình C biên dịch bằng gcc `-O2` cho bộ nhớ và đĩa, Python 3.13 cho TCP và SQLite 3.45.1, `redis-benchmark` của Redis 7.0.15; mỗi phép đo lặp hàng trăm tới hàng triệu lần, báo trung vị (hoặc trung bình với phép đo bộ nhớ). Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

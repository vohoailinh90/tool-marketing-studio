# Chọn hệ thống tin nhắn: tin bị lấy đi, phát đi hay giữ lại

**Trước khi so tốc độ hay số sao trên GitHub, hãy hỏi hệ thống tin nhắn làm gì với một tin sau khi giao.**
Có ba câu trả lời quen thuộc: lấy tin ra khỏi hàng đợi, phát cho ai đang nghe, hoặc giữ tin trong một nhật ký để mỗi bên tự đọc theo vị trí của mình. Nhiều tiêu chí chọn lựa được trả lời luôn từ đó.

![Hai khung. Khung một là ba thẻ, mỗi thẻ một cách giao tin, kèm kết quả thử trên Redis 7. Hàng đợi công việc: mỗi tin tới đúng một worker rồi biến mất; worker 1 nhận m1 và m2, worker 2 nhận m3. Phát và nhận (Pub/Sub): chỉ ai đang nghe mới nhận, tin không được lưu; B vào sau khi m1 được gửi nên chỉ nhận m2. Nhật ký: tin được giữ lại, mỗi nhóm đọc có vị trí riêng; nhóm tạo sau vẫn đọc lại đủ m1 đến m3. Khung hai là bốn câu hỏi trước khi chọn: một tin cho một worker hay cho mọi bên; bên nhận đang tắt thì tin chờ hay mất; có cần đọc lại tin cũ không; báo nhận trước hay sau khi xử lý xong.](../../diagrams/sd-04-004-main.svg)

## Đọc hình

Ba cách trong hình đều chạy được trên cùng một máy chủ Redis 7, mỗi cách một kiểu dữ liệu:

| Cách | Trong Redis | Tin sau khi giao | Ai nhận |
|---|---|---|---|
| Hàng đợi công việc | list, đẩy bằng `LPUSH`, lấy bằng `BRPOP` | bị lấy ra khỏi list | đúng một worker |
| Phát và nhận | Pub/Sub, `PUBLISH` và `SUBSCRIBE` | không được lưu ở đâu | mọi người đang đăng ký lúc đó |
| Nhật ký | stream, `XADD` và `XREADGROUP` | ở lại trong stream | mỗi nhóm đọc nhận đủ, tự giữ vị trí |

**Thử nghiệm.** Gửi ba tin `m1`, `m2`, `m3` vào mỗi kiểu, trên Redis 7.0.15:

- **List:** worker 1 lấy được `m1` và `m2`, worker 2 lấy `m3`; một worker chờ thêm 1 giây không nhận được gì, list còn 0 phần tử.
- **Pub/Sub:** lệnh `PUBLISH` trả về số người nhận. Lúc gửi `m1` chỉ có A đăng ký, lệnh trả về 1; B đăng ký sau đó, lúc gửi `m2` lệnh trả về 2. A nhận cả hai tin, B chỉ nhận `m2`.
- **Stream:** nhóm `billing` đọc đủ ba tin. Nhóm `email` được tạo *sau* khi ba tin đã ghi, bắt đầu từ vị trí 0, vẫn đọc đủ ba tin. Stream vẫn dài 3; ba tin của `billing` nằm trong danh sách đang chờ báo nhận cho tới khi nhóm đó gọi `XACK`.

Kafka thuộc kiểu thứ ba: tài liệu của Kafka nói tin không bị xóa sau khi được đọc mà được giữ theo cấu hình thời hạn của từng topic, và mỗi bên đọc có thể lùi vị trí để đọc lại.

## Giới hạn cần nhớ

- **Hàng đợi:** lấy tin ra rồi mới xử lý thì worker sập giữa chừng là mất tin. Tài liệu Redis gọi cách dùng list đơn giản này là không tin cậy và gợi ý `LMOVE`: chuyển tin sang một list "đang xử lý" thay vì lấy hẳn ra.
- **Pub/Sub của Redis:** tài liệu ghi rõ là giao nhiều nhất một lần; bên nhận lỗi hay rớt mạng thì tin mất hẳn.
- **Nhật ký:** dữ liệu lớn dần, phải đặt thời hạn hoặc độ dài tối đa. Bên đọc phải tự quản vị trí và tự chịu việc đọc lại tin đã xử lý.

## Nhìn hình trả lời

Hệ thống đặt hàng phát một tin "đơn mới". Bên tính tiền phải xử lý mọi đơn; tuần sau sẽ thêm bên gửi thư, cũng cần cả những đơn cũ. Cách nào trong hình hợp, và vì sao không chọn hai cách kia?

<details>
<summary>Xem đáp án</summary>

Nhật ký. Mỗi bên là một nhóm đọc với vị trí riêng, nên cả hai nhận đủ mọi đơn; nhóm gửi thư tạo tuần sau vẫn đọc lại được từ đầu, như nhóm `email` trong thử nghiệm.
Hàng đợi công việc chia mỗi tin cho đúng một bên, nên bên tính tiền và bên gửi thư sẽ giành tin của nhau. Pub/Sub không giữ gì, nên đơn phát lúc bên gửi thư chưa có thì mất.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn nêu tám tiêu chí: tốc độ, khả năng mở rộng, độ tin cậy, độ bền, dễ dùng, hệ sinh thái, khả năng tích hợp và giao thức hỗ trợ. Bài này không chấm điểm sản phẩm theo từng tiêu chí; nó chỉ ra rằng độ tin cậy và độ bền phụ thuộc trước hết vào cách giao tin, nên cùng một Redis có thể mất tin (Pub/Sub) hoặc giữ tin (stream).
Thử nghiệm không đo tốc độ và không so Redis với Kafka hay sản phẩm nào khác; máy chủ Redis chạy không lưu xuống đĩa.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/types-of-message-queue.md): tám tiêu chí chọn hàng đợi tin nhắn.
- [Redis docs — Lists, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/data-types/lists.md): dùng list làm hàng đợi, `BRPOP` giao mỗi phần tử cho một client. Đọc từ bản clone của kho.
- [Redis docs — LMOVE, mục Pattern: reliable queue](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/commands/lmove.md): hàng đợi bằng `BRPOP` có thể mất tin khi bên nhận sập.
- [Redis docs — Pub/Sub, mục Delivery semantics](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/pubsub/_index.md): giao nhiều nhất một lần, tin của stream thì được lưu.
- [Redis docs — Streams](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/data-types/streams/_index.md): nhật ký chỉ ghi nối, nhóm đọc, vị trí bắt đầu `0` hay `$`, `XACK` và danh sách đang chờ.
- [Apache Kafka — Introduction, tại commit cố định](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/getting-started/introduction.md) và [Design, mục Consumer Position](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/design/design.md): tin không bị xóa sau khi đọc, giữ theo thời hạn của topic, bên đọc lùi vị trí để đọc lại. Đọc từ bản clone của kho.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên Redis 7.0.15 (một máy, không bật lưu xuống đĩa) bằng thư viện redis cho Python.
Bài viết và hình được thiết kế độc lập.

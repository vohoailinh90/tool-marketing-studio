# Kafka có làm mất tin không? Có, ở ba chỗ, và đây là cách thấy tận mắt

**Kafka có thể không mất tin nào, nhưng chỉ khi bên gửi, broker và bên nhận cùng được cấu hình để không mất.**
Tài liệu Kafka nói rõ: một tin đã *commit* thì không mất miễn còn một bản sao đồng bộ sống. Thử nghiệm dưới đây cho thấy một tin được xác nhận với bên gửi vẫn có thể chưa từng được commit.

![Ba khung. Khung một, bốn bước thử: đủ ba broker, gửi 100 tin chờ mọi bản đồng bộ, 100 tin được xác nhận; dừng broker 2 và 3, gửi 100 tin chờ mọi bản thì không tin nào được nhận vì broker báo thiếu bản sao; gửi 100 tin chỉ chờ leader thì được xác nhận nhưng bên đọc không thấy; giết leader, cho broker 2 và 3 trở lại, broker 3 làm leader và 100 tin chỉ chờ leader biến mất. Khung hai, ba chỗ có thể mất tin: bên gửi chỉ chờ leader hoặc không thử lại; broker cho bản sao không đồng bộ làm leader; bên nhận lưu vị trí trước khi xử lý xong. Khung ba, cấu hình giữ tin: chờ mọi bản đồng bộ và bật idempotence; ba bản sao, tối thiểu hai bản đồng bộ; tắt unclean leader election; lưu vị trí sau khi xử lý.](../../diagrams/sd-04-016-main.svg)

## Từ viết tắt

- **ISR** (In-Sync Replicas) — tập bản sao đồng bộ: các bản sao của một partition đang theo kịp leader; chỉ chúng được chọn làm leader mới.
- **ELR** (Eligible Leader Replicas) — tập bản sao đủ tư cách làm leader: các bản sao đã rời ISR nhưng Kafka biết chắc chúng có mọi tin đã commit, nên vẫn được chọn làm leader.

## Đọc hình

**Tin "đã commit".** Theo tài liệu thiết kế của Kafka, một tin chỉ được coi là commit khi mọi bản sao trong ISR đã nhận nó. Bên gửi chọn chờ 0, 1 hay mọi bản sao xác nhận (`acks=0`, `1`, `all`). `min.insync.replicas` buộc partition từ chối ghi khi ISR nhỏ hơn số đó, nhưng chỉ có tác dụng với bên gửi dùng `acks=all`.

**Thử nghiệm (khung 1).** Cụm Kafka 4.4.0: một controller và ba broker; topic `orders` một partition, ba bản sao trên broker 1, 2, 3, leader là broker 1, `min.insync.replicas=2`.

| Bước | Kết quả |
|---|---|
| Gửi 100 tin `first` với `acks=all` | 100 tin được xác nhận |
| Dừng broker 2 và 3; ISR còn `[1]` | |
| Gửi 100 tin `second` với `acks=all` | 0 tin được nhận; broker ghi `NotEnoughReplicasException`, bên gửi hết hạn chờ |
| Gửi 100 tin `third` với `acks=1` | 100 tin được xác nhận |
| Đọc từ đầu ở broker 1 | chỉ thấy 100 tin `first` |
| Giết broker 1 (`kill -9`), bật lại broker 2 và 3 | broker 3 làm leader, ISR `[2, 3]` |
| Bật lại broker 1, đọc từ đầu | chỉ còn 100 tin `first`: 100 tin `third` đã mất |

Vì sao `third` được xác nhận mà không đọc được? Trang ELR của tài liệu Kafka (tính năng có từ bản 4.0) mô tả luật "min ISR chặt": mốc high watermark (vị trí cuối cùng bên đọc được thấy) không tiến lên khi ISR nhỏ hơn `min.insync.replicas`. Nên `third` nằm trên đĩa broker 1 mà chưa bao giờ commit. Với ELR (bật mặc định cho cụm mới từ 4.1), controller biết broker 2 và 3 có đủ mọi tin đã commit nên chọn chúng làm leader một cách "sạch", và broker 1 khi quay lại phải bỏ phần đuôi không có ở leader.

**Ba chỗ mất tin (khung 2).** Bên gửi: `acks=1` hay `acks=0` như bước `third`, hoặc gặp lỗi mà không gửi lại. Broker: nếu mọi bản sao trong ISR đều chết và `unclean.leader.election.enable` được bật, Kafka cho một bản sao không đồng bộ lên làm leader, và nhật ký của nó thành bản chuẩn dù thiếu tin. Bên nhận: lưu vị trí đọc trước khi xử lý xong.

## Giới hạn cần nhớ

Cấu hình giữ tin (khung 3) đổi tính sẵn sàng lấy độ bền: ở bước `second`, partition từ chối mọi lệnh ghi `acks=all` chừng nào còn dưới hai bản đồng bộ. Tài liệu Kafka gọi đây là đánh đổi giữa nhất quán và sẵn sàng.
Tài liệu cũng nói Kafka không gọi `fsync` sau mỗi lần ghi mà dựa vào bản sao: broker sập có thể mất phần chưa ghi xuống đĩa, và phải đồng bộ lại hoàn toàn trước khi được vào ISR lại. Một broker một bản sao thì không có lớp bảo vệ đó.

## Nhìn hình trả lời

Một đội đặt `acks=1` cho producer "để nhanh hơn", topic ba bản sao, `min.insync.replicas=2`. Họ tin rằng `min.insync.replicas` sẽ bảo vệ tin của mình. Đúng không?

<details>
<summary>Xem đáp án</summary>

Không. Tài liệu Kafka nói `min.insync.replicas` chỉ có tác dụng khi bên gửi dùng `acks=all`. Với `acks=1`, leader xác nhận ngay khi tự mình ghi xong, như bước `third`: tin được xác nhận rồi mất khi leader chết trước lúc bản sao kịp nhận.
Muốn tin được bảo vệ phải dùng `acks=all` cùng `min.insync.replicas=2`, và chấp nhận rằng ghi sẽ bị từ chối khi chỉ còn một bản đồng bộ.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn nói broker có thể mất tin vì tin được ghi xuống đĩa bất đồng bộ, sập trước khi ghi là mất. Tài liệu Kafka đặt vấn đề khác: độ bền đến từ bản sao chứ không từ `fsync`, nên một broker sập không mất tin đã commit khi còn bản sao đồng bộ khác.
Bài nguồn nhắc các luồng bên trong producer (luồng ứng dụng, bộ gom tin, luồng gửi); bài này không đi vào chúng. Thử nghiệm chạy trên Kafka 4.4.0, nơi ELR đã bật; trên bản cũ hơn hay cụm nâng cấp chưa bật ELR, diễn biến bước cuối có thể khác.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/can-kafka-lose-messages.md): mất tin ở bên gửi, broker và bên nhận.
- [Apache Kafka — Design, các mục Replication, Unclean leader election, Availability and Durability Guarantees, tại commit cố định](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/design/design.md): định nghĩa tin đã commit qua ISR, `acks` 0, 1, `all`, `min.insync.replicas` chỉ tác dụng với `acks=all`, bầu leader không sạch tắt mặc định từ 0.11.0.0, không cần `fsync` mỗi lần ghi. Đọc từ bản clone của kho.
- [Apache Kafka — Eligible Leader Replicas, tại commit cố định](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/operations/eligible-leader-replicas.md): luật min ISR chặt, high watermark không tiến khi ISR nhỏ hơn min ISR, thứ tự chọn leader, ELR bật mặc định cho cụm mới từ 4.1.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên Kafka 4.4.0 (một controller và ba broker trên một máy), thư viện confluent-kafka 2.16.0.
Bài viết và hình được thiết kế độc lập.

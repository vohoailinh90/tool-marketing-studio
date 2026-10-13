# Distributed lock: khóa chưa đủ nếu chủ cũ vẫn ghi

Hai worker cùng muốn tạo báo cáo tháng cho một khách hàng. Distributed lock có thể cho một worker giữ quyền làm tại một thời điểm theo giao thức đã chọn. Nhưng worker giữ khóa có thể bị pause lâu rồi tiếp tục sau khi lease hết hạn.

![Cấp lease: A giữ quyền tạm thời: Token 41; Lease hết • chủ mới: B được cấp token 42: A có thể chưa dừng; Tài nguyên đích: Đã thấy 42 → từ chối 41: Khóa + fencing khi cần.](../../diagrams/sd-11-031-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Trong lúc đó, worker khác đã lấy khóa và ghi bản mới. Nếu worker cũ ghi muộn, dữ liệu mới có thể bị ghi đè. Fencing token tăng theo lần cấp quyền giúp tài nguyên đích từ chối chủ cũ; việc này chỉ hiệu quả khi đích thực sự kiểm token.

Khóa có thể dùng cho phối hợp leader, scheduler, phân bổ tài nguyên, cập nhật inventory hoặc session. Trước khi dùng, xem transaction, unique constraint hoặc conditional write có giải quyết trực tiếp quy tắc dữ liệu không. Khóa nên có timeout và cách giải phóng xác định; thao tác vẫn cần khả năng phục hồi khi tiến trình chết.

## Nhìn hình thử trả lời

Worker A hết lease nhưng vẫn chạy; B lấy khóa mới. Vì sao chỉ có khóa là chưa đủ?

<details>
<summary>Xem đáp án</summary>

A có thể ghi sau B. Cần đích kiểm fencing token hoặc cơ chế điều kiện khác để chặn quyền ghi cũ.

</details>

## Giới hạn cần nhớ

Distributed lock không tự biến cập nhật ở nhiều DB thành transaction nguyên tử, cũng không bảo đảm một job chỉ thực thi đúng một lần.

<details>
<summary>Xem sâu hơn</summary>

Nếu khóa chỉ nhằm tránh tính trùng, lỗi có thể chấp nhận được. Nếu khóa bảo vệ tính đúng, phân tích mất lease, partition, restart và khả năng bảo vệ tại nơi ghi.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/why-do-we-need-to-use-a-distributed-lock.md).
- [How to do distributed locking — Martin Kleppmann’s blog](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html).
- [Distributed Locks with Redis | Docs](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

# Tám mẫu hạn chế sự cố lan rộng

Một dịch vụ thanh toán phản hồi chậm có thể giữ hết thread của ứng dụng bán hàng. Khách gửi lại, tải tăng, rồi cả hệ thống ngừng phục vụ. Resiliency bắt đầu bằng giới hạn tài nguyên bị một lỗi chiếm giữ.

![Giới hạn chờ: Timeout • retry có ngân sách: Circuit breaker; Giới hạn tài nguyên: Rate limit • load shedding: Bulkhead • backpressure; Phục hồi có kiểm soát: Supervisor khởi động lại: Giữ trạng thái nghiệp vụ bền.](../../diagrams/sd-11-014-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Timeout giới hạn chờ; retry có backoff và jitter thử lại lỗi tạm thời; circuit breaker tạm ngừng gọi phụ thuộc đang hỏng. Rate limiting giới hạn nhịp vào, load shedding từ chối bớt khi hệ thống thiếu năng lực. Bulkhead tách pool tài nguyên để lỗi ở một nhóm không giữ hết nhóm khác.

Backpressure báo bên gửi giảm tốc khi bên nhận chậm. “Let it crash” cho phép tiến trình lỗi được supervisor khởi động lại, khi đã có lưu trạng thái và cách phục hồi an toàn. Kết hợp các mẫu theo tình huống: timeout không thay retry, retry không thay dự phòng và khởi động lại không sửa dữ liệu đã sai.

## Nhìn hình thử trả lời

Phụ thuộc đang quá tải. Retry ngay hàng nghìn request có giúp phục hồi không?

<details>
<summary>Xem đáp án</summary>

Thường làm tải tăng thêm. Cần giới hạn retry, chờ có jitter, từ chối bớt hoặc mở circuit breaker.

</details>

## Giới hạn cần nhớ

Retry vô hạn có thể khuếch đại sự cố. Fallback phải nói rõ tính năng hoặc dữ liệu nào bị giảm chất lượng, đặc biệt ở thao tác ghi.

<details>
<summary>Xem sâu hơn</summary>

Gán deadline đầu cuối và truyền ngân sách chờ qua các tầng. Tránh để mỗi tầng retry riêng khiến một request tạo hàng chục lời gọi phía dưới.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/resiliency-patterns.md).
- [Timeouts, retries, and backoff with jitter | AWS Builder Center](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/).
- [Circuit Breaker Pattern - Azure Architecture Center | Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker).
- [Bulkhead Pattern - Azure Architecture Center | Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

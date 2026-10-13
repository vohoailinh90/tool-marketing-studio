# Nhập môn khả năng mở rộng kiến trúc

Một worker xử lý mỗi đơn trong 100 ms. Mười worker chưa chắc cho gấp mười throughput: nếu mọi worker cùng giữ một khóa DB, phần tuần tự vẫn giới hạn cả hệ thống.

![Ba điểm nghẽn: Tập trung • thao tác chậm: Coupling buộc cùng co giãn; Cơ chế cải thiện: Stateless • cache • queue: Chia workload khi phù hợp; Chứng minh bằng đo: Throughput + p99: Chi phí cho mỗi thao tác.](../../diagrams/sd-11-016-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Ba dấu hiệu cần xem là điểm tập trung, thao tác chậm và coupling chặt. Điểm tập trung có thể là một DB hoặc bộ điều phối. Thao tác chậm có thể là I/O tới bên ngoài. Coupling chặt khiến các phần buộc phải cùng tăng số bản dù chỉ một phần bận.

Để cải thiện, đo đường xử lý và thời gian chờ trước. Stateless giúp thêm bản sao; cache giảm việc lặp; queue tách việc dài; partitioning chia workload. Một chiến lược mở rộng tốt còn có chi phí chấp nhận được khi lặp lại. Nếu mỗi người dùng mới tạo thêm quá nhiều lời gọi xuyên dịch vụ, thêm máy chỉ che vấn đề trong thời gian ngắn.

## Nhìn hình thử trả lời

Gấp đôi worker nhưng throughput giữ nguyên, thời gian chờ khóa tăng. Nên xem gì?

<details>
<summary>Xem đáp án</summary>

Phần được bảo vệ bởi khóa và thiết kế truy cập tài nguyên chung; thêm worker chưa xử lý được điểm nghẽn tuần tự.

</details>

## Giới hạn cần nhớ

Không suy ra khả năng mở rộng từ sơ đồ có nhiều hộp. Đo với tải và mức dữ liệu tăng, kể cả phần tuần tự và dịch vụ phụ thuộc.

<details>
<summary>Xem sâu hơn</summary>

Batching có thể giảm overhead nhưng tăng thời gian chờ. Theo dõi latency đuôi và chi phí trên một thao tác, không chỉ tổng throughput.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-crash-course-on-architectural-scalability.md).
- [AWS Well-Architected Framework - AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html).
- [Google SRE: Load Balancing with Client Side Throttling](https://sre.google/sre-book/handling-overload/).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

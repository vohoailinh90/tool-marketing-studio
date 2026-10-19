# McDonald's: chuẩn hóa sự kiện trước, mở rộng sau

**Kiến trúc hướng sự kiện chỉ chạy tốt ở quy mô lớn khi mọi đội cùng hiểu một sự kiện trông thế nào.** Theo bài nguồn, McDonald's dựng bốn thành phần để chuẩn hóa sự kiện, rồi mới lo mở rộng phần xử lý theo vùng và theo miền nghiệp vụ.
Bài này tách hai lớp đó: lớp giữ cho sự kiện đúng khuôn, và lớp giữ cho hệ thống chịu được tải.

![Ba khung xếp dọc. Chuẩn hóa sự kiện: sổ đăng ký sự kiện định nghĩa schema chuẩn; SDK riêng xử lý sự kiện và lỗi theo cách chung; cổng sự kiện xác thực danh tính và phân quyền; tiện ích và công cụ sửa sự kiện hỏng, giữ cụm khỏe và làm việc quản trị. Mở rộng trong một vùng: bên phát chia sự kiện theo miền nghiệp vụ, mỗi miền được một cụm MSK riêng xử lý, cụm tự mở rộng theo chỉ số như mức dùng CPU. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-007-main.svg)

## Từ viết tắt

- **SDK** (Software Development Kit) — bộ công cụ phát triển: thư viện và công cụ mà các đội dùng chung để gửi và nhận sự kiện theo cùng một cách.
- **MSK** (Managed Streaming for Kafka) — dịch vụ Kafka được quản lý của Amazon, tên đầy đủ là Amazon Managed Streaming for Apache Kafka: nhà cung cấp lo vận hành cụm Kafka, nơi sự kiện được ghi và đọc ra theo thứ tự.
- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon, nơi McDonald's đặt kiến trúc này theo bài nguồn.
- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần chạy lệnh của máy; mức dùng của nó là một chỉ số để quyết định khi nào thêm tài nguyên.

## Đọc hình

**Chuẩn hóa.** Theo nguồn, McDonald's chuẩn hóa sự kiện bằng bốn thành phần:
- Sổ đăng ký sự kiện: nơi định nghĩa schema chuẩn, tức khuôn dữ liệu mà mỗi loại sự kiện phải theo.
- SDK riêng: để các đội xử lý sự kiện và xử lý lỗi theo cùng một cách.
- Cổng sự kiện: xác thực danh tính và phân quyền. Bài nguồn không nói những sự kiện nào phải đi qua cổng này, nên đừng hiểu là mọi sự kiện đều qua đây.
- Tiện ích và công cụ: sửa sự kiện hỏng, giữ cụm khỏe, làm các việc quản trị.

**Mở rộng.** McDonald's dùng kiến trúc theo vùng trên AWS để có tính sẵn sàng toàn cầu. Trong một vùng, bên phát chia sự kiện theo miền nghiệp vụ, và mỗi miền được một cụm MSK xử lý. Cụm tự mở rộng dựa trên chỉ số của MSK, như mức dùng CPU; quy trình mở rộng dựa trên Step Functions và các tác vụ phân bổ lại. Nguồn không nói cụm có tự bớt máy khi tải giảm hay không.

## Giới hạn cần nhớ

Chia theo miền nghĩa là có nhiều cụm hơn để vận hành, và bên phát phải biết mỗi sự kiện thuộc miền nào để gửi tới đúng cụm. Đây là đánh đổi chung của người biên soạn, bài nguồn không bàn. Bài nguồn cũng không nói vì sao sổ đăng ký và cổng được tách riêng; cách đọc "lớp đúng khuôn, lớp chịu tải" là của bài này.
Mọi mô tả là theo bài nguồn, tóm tắt một bài trên blog kỹ thuật của McDonald's; bài blog đó chưa được mở để đối chiếu.

## Nhìn hình thử trả lời

Đội thanh toán đổi tên một trường trong sự kiện "đơn đã trả tiền" mà không báo ai. Thành phần nào trong hình được dựng ra để chặn chuyện này, và chặn bằng cách nào?

<details>
<summary>Xem đáp án</summary>

Sổ đăng ký sự kiện. Nó giữ schema chuẩn của từng loại sự kiện, nên một sự kiện không theo schema đã đăng ký có thể bị phát hiện thay vì âm thầm làm hỏng các đội đang đọc nó. SDK dùng chung giúp mọi bên xử lý lỗi đó theo cùng một cách.

</details>

<details>
<summary>Xem sâu hơn: vì sao chia theo miền thay vì một cụm lớn</summary>

- Một miền tăng tải đột ngột (khuyến mãi lớn, chẳng hạn) không làm chậm các miền khác.
- Mỗi cụm tự mở rộng theo tải của riêng nó.
- Sự cố ở một cụm chỉ ảnh hưởng một miền.

Đây là lợi ích chung của việc chia theo miền, do người biên soạn nêu; bài nguồn chỉ mô tả cách chia.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/mcdonald's-event-driven-architecture.md): bốn thành phần chuẩn hóa sự kiện, kiến trúc theo vùng, chia theo miền và cụm tự mở rộng.

Đã đọc nguồn ngày 2026-10-19. Bài blog gốc của McDonald's mà nguồn dẫn chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

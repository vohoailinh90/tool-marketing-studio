# Nhiều nhất một lần, ít nhất một lần, đúng một lần: quyết định nằm ở chỗ lưu vị trí

**Hệ thống tin nhắn hứa giao "ít nhất một lần" hay "nhiều nhất một lần" thật ra là hứa về chuyện gì xảy ra khi một bên chết giữa chừng.**
Ở phía nhận, câu trả lời phụ thuộc vào một quyết định rất nhỏ: lưu vị trí đã đọc tới đâu trước, hay xử lý tin trước. Bài này cho bên nhận chết thật ở cùng một chỗ và đếm kết quả.

![Ba khung. Khung một, thứ tự lưu vị trí đọc: lưu vị trí trước rồi xử lý thì bên nhận chết sau khi lưu làm khoản 6 bị bỏ qua, sổ còn 9 dòng, nhiều nhất một lần; xử lý trước rồi lưu vị trí thì chết trước khi lưu làm khoản 6 được giao lại, sổ 11 dòng, ít nhất một lần. Khung hai, hai cách cho kết quả như đúng một lần: xử lý rồi bỏ bản trùng theo mã thanh toán, sổ 10 dòng; lưu vị trí cùng giao dịch với kết quả, chết trước commit thì cả hai cùng mất và làm lại từ khoản 6, sổ 10 dòng. Khung ba: số đo giám sát chịu mất vài điểm thì nhiều nhất một lần; có khóa để bỏ trùng thì ít nhất một lần là đủ; với tiền, lưu vị trí cùng giao dịch với kết quả; đích là topic Kafka thì dùng giao dịch của Kafka.](../../diagrams/sd-04-014-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc của cơ sở dữ liệu quan hệ; nằm trong tên PostgreSQL, nơi giữ sổ thanh toán trong thử nghiệm.

## Đọc hình

Tài liệu Kafka định nghĩa ba mức: *nhiều nhất một lần* (tin có thể mất nhưng không bao giờ giao lại), *ít nhất một lần* (không mất nhưng có thể giao lại) và *đúng một lần* (mỗi tin được xử lý đúng một lần). Tài liệu cũng chia vấn đề làm hai nửa: bên gửi có chắc tin đã vào nhật ký không, và bên nhận lưu vị trí đọc thế nào.

**Khung 1 · Bên nhận.** Theo tài liệu Kafka, bên nhận tự giữ vị trí (offset) của mình. Lưu vị trí rồi mới xử lý thì chết ở giữa làm tin bị bỏ qua; xử lý rồi mới lưu vị trí thì chết ở giữa làm tin bị giao lại.

**Khung 2 · Đúng một lần.** Không có phép màu: hoặc làm cho việc xử lý lặp lại không đổi kết quả (bỏ bản trùng theo khóa), hoặc lưu vị trí ở *cùng chỗ* và *cùng giao dịch* với kết quả, để chúng cùng thành hoặc cùng mất. Tài liệu Kafka gợi ý đúng cách thứ hai cho đích ngoài Kafka, thay vì commit hai pha.

**Bên gửi.** Gửi lại sau lỗi mạng có thể ghi một tin hai lần. Từ bản 0.11.0.0, producer có chế độ idempotent: broker gán cho mỗi producer một mã và bỏ bản trùng nhờ số thứ tự gửi kèm từng tin; producer còn có giao dịch để ghi nhiều partition cùng thành hoặc cùng mất.

## Thử nghiệm: chết ở khoản thứ 6

Kafka 4.4.0 (ba broker), topic `payments` có 10 khoản, producer bật `enable.idempotence`. Bên nhận ghi mỗi khoản vào bảng `ledger` của PostgreSQL 16 và tắt tự lưu vị trí. Lần chạy đầu chết ngay tại khoản 6; lần chạy hai, cùng nhóm, tiếp quản.

| Cách làm của bên nhận | Bảng `ledger` sau lần hai |
|---|---|
| Lưu vị trí, rồi ghi sổ | 9 dòng, thiếu khoản 6 |
| Ghi sổ, rồi lưu vị trí | 11 dòng, khoản 6 hai lần |
| Ghi sổ nếu chưa có mã đó, rồi lưu vị trí | 10 dòng |
| Ghi sổ và ghi vị trí vào một bảng khác của cùng cơ sở dữ liệu, trong một giao dịch; khi khởi động, đọc vị trí từ bảng đó | 10 dòng |

## Giới hạn cần nhớ

- "Đúng một lần" trong Kafka (producer giao dịch cùng bên nhận đọc mức `read_committed`) chỉ phủ chuỗi đọc, xử lý, ghi *trong* Kafka. Tài liệu Kafka nói đích bên ngoài thì cần đích đó hợp tác.
- Tài liệu Kafka cũng cảnh báo nhiều hệ thống tự nhận "đúng một lần" nhưng lời hứa không còn đúng khi bên gửi hay bên nhận chết, khi có nhiều bên nhận, hay khi dữ liệu trên đĩa mất. Đọc kỹ điều kiện đi kèm.
- Mặc định Kafka là ít nhất một lần, nên bên nhận phải chịu được tin trùng.

## Nhìn hình trả lời

Một dịch vụ gửi thư xác nhận đơn hàng đọc tin từ Kafka rồi gọi một nhà cung cấp gửi thư bên ngoài, không hỗ trợ bỏ trùng. Gửi trùng một thư thì phiền, mất một thư thì khách khiếu nại. Chọn thứ tự nào, và giảm bản trùng ra sao?

<details>
<summary>Xem đáp án</summary>

Xử lý rồi mới lưu vị trí (ít nhất một lần): mất thư tệ hơn gửi trùng. Để giảm bản trùng, dịch vụ tự ghi lại mã đơn đã gửi thư (ví dụ trong cơ sở dữ liệu của mình) và kiểm trước khi gọi nhà cung cấp.
Vẫn còn một khe hở: chết sau khi gọi nhà cung cấp nhưng trước khi ghi mã thì lần sau vẫn gửi lại. Khi đích ngoài không hợp tác, "đúng một lần" chỉ đến gần chứ không đạt hẳn.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn gắn mỗi mức với một nhóm ứng dụng (số đo giám sát cho nhiều nhất một lần, thanh toán cho đúng một lần). Bài này giữ ý đó ở khung 3 nhưng chỉ ra cơ chế: mức nào là do *thứ tự* lưu vị trí và xử lý, và "đúng một lần" với đích ngoài là việc của chính ứng dụng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/delivery-semantics.md): ba mức giao tin và trường hợp dùng.
- [Apache Kafka — Design, mục Message Delivery Semantics, tại commit cố định](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/design/design.md): định nghĩa ba mức, producer idempotent và giao dịch từ 0.11.0.0, hai thứ tự lưu vị trí của bên nhận, lưu vị trí cùng chỗ với kết quả, mặc định ít nhất một lần. Đọc từ bản clone của kho.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên Kafka 4.4.0 (ba broker trên một máy), PostgreSQL 16.15, thư viện confluent-kafka 2.16.0; "chết" là dừng bên nhận ngay tại khoản 6 mà không lưu gì thêm.
Bài viết và hình được thiết kế độc lập.

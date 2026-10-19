# Stack Overflow: chín máy chủ web và một khối nguyên

**Đề bài "thiết kế Stack Overflow" thường được trả lời bằng microservice, sharding và hàng đợi; theo bài nguồn, hệ thống thật chạy trên chín máy chủ web tại chỗ và là một khối nguyên.**
Bài này đặt hai bức tranh cạnh nhau: điều người ta nghĩ một trang lớn phải có, và điều bài nguồn nói Stack Overflow thật sự dùng. Mục đích không phải chê bên nào, mà để thấy một thiết kế được chọn theo nhu cầu, không theo danh sách kỹ thuật.

![Hai cột thẻ và một khung ghi nhớ. Cột một, điều thường được chờ trong buổi phỏng vấn: tách thành nhiều microservice; mỗi dịch vụ một cơ sở dữ liệu riêng, dùng bộ đệm nhiều; chia dữ liệu thành nhiều mảnh; các dịch vụ nói chuyện bất đồng bộ qua hàng đợi tin nhắn. Cột hai, theo bài nguồn: chín máy chủ web phục vụ toàn bộ lưu lượng; một ứng dụng khối nguyên; máy chủ riêng đặt tại chỗ, không chạy trên đám mây. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-009-main.svg)

## Từ viết tắt

- **CQRS** (Command Query Responsibility Segregation) — tách trách nhiệm ghi và đọc: phần nhận lệnh thay đổi dữ liệu và phần trả lời truy vấn được làm thành hai mô hình riêng.
- **CAP** (Consistency, Availability, Partition) — nhất quán, sẵn sàng, chịu được phân vùng (partition tolerance); định lý CAP: khi mạng giữa các máy bị chia cắt, một hệ phân tán phải chọn giữ nhất quán hay giữ sẵn sàng.

## Đọc hình

**Điều thường được chờ.** Bài nguồn liệt kê câu trả lời mà người phỏng vấn có lẽ đang chờ:
- Tách hệ thống thành nhiều microservice nhỏ.
- Mỗi dịch vụ có cơ sở dữ liệu riêng, dùng bộ đệm (cache) nhiều.
- Dịch vụ được chia mảnh (sharding).
- Các dịch vụ nói chuyện bất đồng bộ qua hàng đợi tin nhắn.
- Làm theo Event Sourcing với CQRS.
- Khoe hiểu biết về hệ phân tán: nhất quán cuối cùng, định lý CAP...

**Theo bài nguồn.** Stack Overflow phục vụ toàn bộ lưu lượng chỉ bằng 9 máy chủ web đặt tại chỗ (on-premise), và là một khối nguyên (monolith). Họ có máy chủ riêng, không chạy trên đám mây. Bài nguồn gọi điều này là ngược với nhiều niềm tin phổ biến hiện nay.

## Giới hạn cần nhớ

Bài nguồn không nói con số này thuộc năm nào, cũng không nói lưu lượng là bao nhiêu hay còn những máy nào khác ngoài máy chủ web (cơ sở dữ liệu, bộ đệm, tìm kiếm). "Chín máy chủ web" vì vậy không có nghĩa là cả hệ thống chỉ có chín máy. Bài nguồn cũng không giải thích vì sao cách làm này chạy được; các lý do ở phần dưới là của người biên soạn.

## Nhìn hình thử trả lời

Bạn được hỏi thiết kế một trang hỏi đáp mới, ít người dùng, đội ba người. Bạn có nên mở đầu bằng sharding và hàng đợi tin nhắn không? Hình gợi ý gì?

<details>
<summary>Xem đáp án</summary>

Không nhất thiết. Hình cho thấy một trang rất lớn như Stack Overflow vẫn chạy được trên một khối nguyên với ít máy chủ web. Nên bắt đầu từ thiết kế đơn giản nhất đáp ứng được tải dự kiến, rồi nói rõ khi nào và vì sao mới cần tách dịch vụ hay chia mảnh dữ liệu.

</details>

<details>
<summary>Xem sâu hơn: khi nào một khối nguyên vẫn đủ</summary>

- Phần lớn yêu cầu là đọc, nên bộ đệm và máy mạnh gánh được nhiều.
- Một đội không quá lớn làm chung một mã nguồn thì ít cần ranh giới dịch vụ.
- Mỗi microservice thêm vào là thêm mạng, thêm lỗi từng phần, thêm việc vận hành.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-will-you-design-the-stack-overflow-website.md): câu trả lời phỏng vấn thường gặp so với chín máy chủ web tại chỗ và một khối nguyên.

Đã đọc nguồn ngày 2026-10-19. Bài nguồn không dẫn tài liệu gốc của Stack Overflow; con số chưa được đối chiếu.
Bài viết và hình được thiết kế độc lập.

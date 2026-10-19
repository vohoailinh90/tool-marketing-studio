# Netflix và EVCache: một bộ đệm, bốn cách dùng

**Theo bài nguồn, Netflix dùng EVCache, một kho khóa–giá trị phân tán, để giảm độ trễ, và dùng nó theo bốn cách khác nhau: bộ đệm bên cạnh, kho dữ liệu tạm, kho chính và dữ liệu đọc rất nhiều.**
Bài nguồn mở đầu bằng con số: sự chú ý của một người dùng thường chỉ kéo dài khoảng 90 giây. Bài này đi qua bốn cách dùng và hỏi, ở mỗi cách, dữ liệu gốc nằm ở đâu.

![Hai khung thẻ và một khung ghi nhớ. Khung một, bộ đệm theo nghĩa quen: bộ đệm bên cạnh, ứng dụng hỏi EVCache trước, thiếu thì lấy từ dịch vụ phía sau và Cassandra rồi cập nhật bộ đệm; kho dữ liệu tạm, giữ thông tin phiên phát video mà nhiều dịch vụ lần lượt mở, cập nhật và đóng. Khung hai, khi bộ đệm là nơi đọc chính: kho chính, mỗi đêm hệ thống tính trước trang chủ cho từng hồ sơ và ghi vào EVCache để dịch vụ trực tuyến đọc; dữ liệu đọc rất nhiều, như chuỗi chữ giao diện và bản dịch, được một tiến trình riêng đẩy vào EVCache. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-014-main.svg)

## Từ viết tắt

- **UI** (User Interface) — giao diện người dùng: phần chữ, nút và hình mà người dùng nhìn thấy trên trang Netflix.

## Đọc hình

**Bộ đệm theo nghĩa quen.**
- Bộ đệm bên cạnh (lookaside cache): ứng dụng hỏi EVCache trước; nếu không có, nó lấy từ dịch vụ phía sau và cơ sở dữ liệu Cassandra. Dịch vụ cũng cập nhật bộ đệm cho các lần hỏi sau.
- Kho dữ liệu tạm (transient data store): EVCache giữ dữ liệu ngắn hạn như thông tin phiên phát video. Một dịch vụ có thể mở phiên, dịch vụ khác cập nhật, cuối cùng phiên được đóng.

**Khi bộ đệm là nơi đọc chính.**
- Kho chính (primary store): mỗi đêm Netflix chạy các hệ thống tính trước quy mô lớn, dựng trang chủ mới cho từng hồ sơ của từng người dùng dựa trên lịch sử xem và gợi ý. Toàn bộ dữ liệu đó được ghi vào cụm EVCache, nơi các dịch vụ trực tuyến đọc ra để dựng trang chủ.
- Dữ liệu đọc rất nhiều (high volume data): có dữ liệu được đọc rất nhiều và cần luôn sẵn sàng, ví dụ chuỗi chữ UI và bản dịch trên trang chủ. Một tiến trình riêng tính và đẩy chúng vào EVCache một cách bất đồng bộ; ứng dụng đọc ra với độ trễ thấp.

## Giới hạn cần nhớ

Bài nguồn không nói EVCache giữ dữ liệu bao lâu, cũng không nói chuyện gì xảy ra khi cụm EVCache mất dữ liệu ở cách dùng "kho chính". Nó cũng không đưa số liệu độ trễ. Con số 90 giây là về sự chú ý của người xem, không phải thời gian tải trang. Nhận xét về "dữ liệu gốc nằm ở đâu" là cách đọc của bài này.

## Nhìn hình thử trả lời

Ở cách dùng "kho chính", nếu sáng nay cụm EVCache mất sạch dữ liệu trang chủ, dịch vụ có thể lấy lại từ đâu?

<details>
<summary>Xem đáp án</summary>

Từ hệ thống tính trước chạy hằng đêm: trang chủ được tính ở đó rồi mới ghi vào EVCache, nên có thể chạy lại để ghi lại. Khác với bộ đệm bên cạnh, ở đây không có một cơ sở dữ liệu nào đứng sau để mỗi lần thiếu thì hỏi. Bài nguồn không mô tả cách Netflix xử lý trường hợp này; đây là suy luận từ hình.

</details>

<details>
<summary>Xem sâu hơn: dữ liệu gốc nằm ở đâu</summary>

- Bộ đệm bên cạnh: gốc ở Cassandra và dịch vụ phía sau; bộ đệm chỉ là bản sao.
- Kho dữ liệu tạm: dữ liệu chỉ sống trong một phiên, không cần gốc lâu dài.
- Kho chính và dữ liệu đọc nhiều: gốc là tiến trình tính ra nó; EVCache là nơi đọc.

Đây là cách xếp của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/4-ways-netflix-uses-caching-to-hold-user-attention.md): EVCache và bốn cách Netflix dùng nó.

Đã đọc nguồn ngày 2026-10-19. Tài liệu của Netflix về EVCache chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

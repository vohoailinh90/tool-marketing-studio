# Telegram có an toàn không? Còn tùy ai giữ chìa khóa

**"Có mã hóa" chưa đủ để gọi là an toàn; câu hỏi thật là ai có thể giải mã tin nhắn.** Bài nguồn so sánh hai loại chat của Telegram: chat thường và chat nhóm không mã hóa đầu cuối, còn "secret chat" thì có.
Bài này đọc hai loại đó theo cùng một câu hỏi: ngoài người gửi và người nhận, còn ai đọc được tin?

![Hai nhóm thẻ so sánh. Chat thường và chat nhóm: máy người gửi mã hóa tin trên đường tới máy chủ; máy chủ Telegram giải mã được và lưu tin đã mã hóa, chia nhỏ ở nhiều nước; chìa khóa giải mã cũng chia nhỏ ở nhiều nước. Secret chat: máy người gửi mã hóa bằng chìa khóa chỉ hai máy biết; máy chủ chỉ chuyển tiếp dữ liệu đã mã hóa; chỉ máy người nhận giải mã được. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-004-main.svg)

## Từ viết tắt

- **E2EE** (End-to-End Encryption) — mã hóa đầu cuối: tin được mã hóa ngay trên máy người gửi và chỉ máy người nhận giải mã được; máy chủ ở giữa chỉ chuyển tiếp dữ liệu nó không đọc được.

## Đọc hình

**Định nghĩa trước.** Theo bài nguồn, một cuộc chat "an toàn" thường nghĩa là tin được mã hóa ở phía người gửi và chỉ giải mã được ở phía người nhận, tức là E2EE.

**Chat thường và chat nhóm.** Đây là hai loại chat mặc định, và theo nguồn chúng không mã hóa đầu cuối: bên thứ ba về nguyên tắc có thể chặn và đọc tin. Cách Telegram bảo vệ chúng:
- Tin đã mã hóa được lưu trên máy chủ Telegram, chia thành nhiều mảnh, cất ở các nước khác nhau.
- Chìa khóa giải mã cũng được chia nhỏ và cất ở nhiều nước.

Kẻ tấn công vì vậy phải lấy được mọi mảnh tin và mọi mảnh chìa khóa. Nguồn nói việc đó có thể làm được nhưng cực kỳ khó.

**Secret chat.** Chọn "secret chat" thì tin được mã hóa đầu cuối. Theo nguồn, cái giá là: không dùng được cho chat nhóm hay chat một-một thông thường, và chỉ bật được trên thiết bị di động.

## Giới hạn cần nhớ

Điểm khác cốt lõi là ai giữ chìa khóa. Ở chat thường, hệ thống của Telegram có cách giải mã tin (nó phải làm thế để đồng bộ lịch sử lên nhiều máy), nên mức an toàn dựa vào việc tin tưởng Telegram và cách họ cất chìa khóa. Ở secret chat, máy chủ không có chìa khóa. Câu giải thích này là suy luận của người biên soạn từ định nghĩa E2EE, không phải câu của bài nguồn.
Các giới hạn của secret chat là theo bài nguồn viết đầu năm 2024; tính năng của ứng dụng có thể đã đổi, nên xem lại tài liệu hiện hành của Telegram trước khi dựa vào.

## Nhìn hình thử trả lời

Một người lấy được toàn bộ dữ liệu của một máy chủ Telegram ở một nước. Với chat thường và với secret chat, người đó đọc được tin chưa?

<details>
<summary>Xem đáp án</summary>

Chat thường: chưa, vì theo nguồn tin và chìa khóa đều bị chia nhỏ ra nhiều nước, nên họ còn phải lấy các mảnh ở nơi khác. Khó, nhưng không phải không thể.
Secret chat: không, vì máy chủ chỉ giữ dữ liệu đã mã hóa và không có chìa khóa; chìa khóa chỉ nằm trên hai máy của người gửi và người nhận.

</details>

<details>
<summary>Xem sâu hơn: mã hóa trên đường đi khác mã hóa đầu cuối</summary>

- **Mã hóa giữa máy khách và máy chủ:** kẻ nghe lén trên mạng không đọc được, nhưng máy chủ giải mã được. Đa số dịch vụ web hoạt động như vậy.
- **Mã hóa đầu cuối:** cả máy chủ cũng không đọc được. Đổi lại, những việc cần máy chủ đọc tin (tìm kiếm phía máy chủ, đồng bộ lịch sử lên máy mới) khó làm hơn.

Đây là kiến thức chung của người biên soạn, giúp hiểu vì sao secret chat có ít tính năng hơn; bài nguồn không giải thích lý do của các giới hạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/is-telegram-secure.md): định nghĩa chat an toàn, cách Telegram lưu chat thường và giới hạn của secret chat.

Đã đọc nguồn ngày 2026-10-19. Tài liệu chính thức của Telegram chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

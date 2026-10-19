# Telegram có an toàn không? Còn tùy ai giữ chìa khóa

**"Có mã hóa" chưa đủ để gọi là an toàn; câu hỏi thật là ai có thể giải mã tin nhắn.** Bài nguồn so sánh hai loại chat của Telegram: chat thường và chat nhóm không mã hóa đầu cuối, còn "secret chat" thì có.
Bài này đọc hai loại đó theo cùng một câu hỏi: ngoài người gửi và người nhận, còn ai đọc được tin?

![Hai nhóm thẻ so sánh. Chat thường và chat nhóm: máy người gửi mã hóa tin trên đường tới máy chủ; máy chủ Telegram giải mã được và lưu tin đã mã hóa ở nhiều trung tâm dữ liệu; chìa khóa giải mã được chia thành nhiều phần cất ở nhiều nơi. Secret chat: máy người gửi mã hóa bằng chìa khóa chỉ hai máy biết; máy chủ chỉ chuyển tiếp dữ liệu đã mã hóa; chỉ hai máy ở hai đầu cuộc chat giải mã được. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-004-main.svg)

## Từ viết tắt

- **E2EE** (End-to-End Encryption) — mã hóa đầu cuối: tin được mã hóa ngay trên máy người gửi và chỉ hai máy ở hai đầu cuộc chat (người gửi và người nhận) giải mã được; máy chủ ở giữa chỉ chuyển tiếp dữ liệu nó không đọc được.

## Đọc hình

**Định nghĩa trước.** Theo bài nguồn, một cuộc chat "an toàn" thường nghĩa là tin được mã hóa ở phía người gửi và chỉ giải mã được ở hai đầu cuộc chat, tức là E2EE. Vì chat có hai chiều, cả hai máy đều giữ chìa khóa và đều giải mã được tin mình nhận.

**Chat thường và chat nhóm.** Đây là hai loại chat mặc định, và theo nguồn chúng không mã hóa đầu cuối. Bài nguồn diễn giải điều này là bên thứ ba có thể chặn và đọc tin; nói chính xác hơn, tin vẫn được mã hóa giữa máy khách và máy chủ, nên kẻ nghe lén trên mạng không đọc được, nhưng phía máy chủ của Telegram giải mã được. Rủi ro vì vậy nằm ở việc tin Telegram và cách họ giữ chìa khóa. Cách Telegram bảo vệ chúng, theo nguồn:
- Tin đã mã hóa được lưu trên máy chủ Telegram, ở nhiều trung tâm dữ liệu.
- Chìa khóa giải mã được chia thành nhiều phần và cất ở nhiều nơi khác nhau.

Bài nguồn nói cả tin cũng bị chia thành nhiều mảnh; tài liệu của Telegram chỉ nói chìa khóa giải mã được chia phần, còn dữ liệu chat thì được lưu ở nhiều trung tâm dữ liệu.

Kẻ tấn công lấy được dữ liệu ở một trung tâm dữ liệu vẫn chưa đọc được tin, vì còn phải gom đủ các phần của chìa khóa cất ở nơi khác. Nguồn nói việc đó có thể làm được nhưng cực kỳ khó; cách cất chìa khóa này là mô tả của chính Telegram.

**Secret chat.** Chọn "secret chat" thì tin được mã hóa đầu cuối. Secret chat là một cuộc chat một-một riêng, mở thêm bên cạnh chat một-một thường với cùng người đó. Theo nguồn, cái giá là: không dùng được cho chat nhóm, không thay cho chat một-một thường, và chỉ bật được trên thiết bị di động.

## Giới hạn cần nhớ

Điểm khác cốt lõi là ai giữ chìa khóa. Ở chat thường, hệ thống của Telegram có cách giải mã tin (Telegram chọn cách lưu tin trên đám mây mà máy chủ đọc được, một phần để việc đồng bộ lịch sử lên nhiều máy đơn giản hơn; đồng bộ nhiều máy vẫn làm được mà máy chủ không cần đọc tin, chỉ là khó hơn), nên mức an toàn dựa vào việc tin tưởng Telegram và cách họ cất chìa khóa. Ở secret chat, máy chủ không có chìa khóa. Câu giải thích này là suy luận của người biên soạn từ định nghĩa E2EE, không phải câu của bài nguồn.
Các giới hạn của secret chat là theo bài nguồn viết đầu năm 2024; tính năng của ứng dụng có thể đã đổi, nên xem lại tài liệu hiện hành của Telegram trước khi dựa vào.

## Nhìn hình thử trả lời

Một người lấy được toàn bộ dữ liệu của một máy chủ Telegram ở một nước. Với chat thường và với secret chat, người đó đọc được tin chưa?

<details>
<summary>Xem đáp án</summary>

Chat thường: chưa, vì chìa khóa giải mã được chia thành nhiều phần cất ở nơi khác, nên họ còn phải lấy các phần đó. Khó, nhưng không phải không thể.
Secret chat: không, vì máy chủ chỉ chuyển tiếp dữ liệu đã mã hóa và không có chìa khóa; chìa khóa chỉ nằm trên hai máy của người gửi và người nhận.

</details>

<details>
<summary>Xem sâu hơn: mã hóa trên đường đi khác mã hóa đầu cuối</summary>

- **Mã hóa giữa máy khách và máy chủ:** kẻ nghe lén trên mạng không đọc được, nhưng máy chủ giải mã được. Đa số dịch vụ web hoạt động như vậy.
- **Mã hóa đầu cuối:** cả máy chủ cũng không đọc được. Đổi lại, những việc cần máy chủ đọc tin (tìm kiếm phía máy chủ, đồng bộ lịch sử lên máy mới) khó làm hơn.

Đây là kiến thức chung của người biên soạn, giúp hiểu vì sao secret chat có ít tính năng hơn; bài nguồn không giải thích lý do của các giới hạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/is-telegram-secure.md): định nghĩa chat an toàn, cách Telegram lưu chat thường và giới hạn của secret chat.

- [Telegram — FAQ, mục "Do you process data requests?"](https://telegram.org/faq#q-do-you-process-data-requests): dữ liệu của chat thường được lưu ở nhiều trung tâm dữ liệu, chìa khóa giải mã được chia thành nhiều phần và không cất cùng dữ liệu. Trang này không mở trực tiếp được lúc biên soạn; ý trên được đối chiếu qua bản dẫn lại của [Belkasoft](https://belkasoft.com/how-to-investigate-telegram-crime).

Đã đọc nguồn ngày 2026-10-19. Ngoài mục FAQ trên, tài liệu chính thức của Telegram chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

# Bốn thước đo của một hệ thống: mở rộng, sẵn sàng, tin cậy và hiệu năng

**Mở rộng, sẵn sàng, tin cậy và hiệu năng là bốn câu hỏi khác nhau về cùng một hệ thống. Một hệ thống có thể trả lời tốt câu này mà dở câu kia.**
Phân biệt được bốn câu hỏi, bạn biết khi nào "hệ thống chậm", "hệ thống sập" và "hệ thống trả sai" là ba vấn đề khác nhau.

![Hai khung. Khung một, bốn câu hỏi: chịu thêm tải được không, có luôn sẵn sàng phục vụ không, có cho kết quả đúng không, có đủ nhanh dưới tải đỉnh không. Khung hai, ví dụ tính được: hệ thống sẵn sàng 99,9 phần trăm thì có thể ngừng khoảng 8,76 giờ mỗi năm, và hai dịch vụ nối tiếp, mỗi dịch vụ 99,9 phần trăm, chỉ còn khoảng 99,8 phần trăm.](../../diagrams/sd-11-011-main.svg)

## Đọc hình

Tên bốn thước đo giữ theo bài nguồn; lời giải thích và các phép tính là của người biên soạn.

**Scalability (khả năng mở rộng).** Khi tải tăng gấp đôi, hệ thống có chịu được nếu thêm tài nguyên, mà không phải viết lại? Ví dụ: thêm máy phía sau bộ chia tải. Nó trả lời câu hỏi về *tương lai*: tải tăng thì sao.

**Availability (độ sẵn sàng).** Tỷ lệ thời gian hệ thống sẵn sàng phục vụ. Hay nói bằng số "chín": 99% là hai chín, 99,9% là ba chín. Nó trả lời câu hỏi "lúc người dùng cần, hệ thống có đó không".

**Reliability (độ tin cậy).** Hệ thống có cho kết quả *đúng* một cách nhất quán không. Một dịch vụ có thể luôn trả lời (sẵn sàng cao) nhưng đôi lúc trả số dư sai (tin cậy thấp). Ngược lại, hệ thống thà dừng còn hơn trả sai thì tin cậy tốt nhưng không phải lúc nào cũng sẵn sàng.

**Performance (hiệu năng).** Hệ thống làm việc với tốc độ mong đợi, nhất là lúc tải đỉnh, bằng tài nguyên sẵn có. Nó trả lời câu hỏi "nhanh bao nhiêu khi đông nhất".

**Ví dụ tính được về độ sẵn sàng.** Một năm có 8 760 giờ (365 ngày). Với 99% sẵn sàng, được phép ngừng tối đa 1% là 87,6 giờ mỗi năm; với 99,9% là 8,76 giờ; với 99,99% là khoảng 52,6 phút; với 99,999% là khoảng 5,3 phút. Mỗi thêm một chữ số chín thì thời gian được ngừng giảm mười lần, nên mỗi chữ số chín thường đắt hơn chữ số trước.

**Nối tiếp thì nhân.** Nếu một yêu cầu phải đi qua hai dịch vụ, mỗi dịch vụ sẵn sàng 99,9% và hỏng độc lập, thì cả đường chỉ sẵn sàng khi cả hai cùng sẵn sàng: 0,999 × 0,999 ≈ 0,998, tức khoảng 99,8%. Càng nhiều dịch vụ nối tiếp, độ sẵn sàng tổng càng thấp hơn từng dịch vụ.

## Giới hạn cần nhớ

Bốn thước đo này kéo nhau theo cả hai chiều: thêm bản sao giúp sẵn sàng và mở rộng, nhưng làm việc giữ kết quả đúng giữa các bản sao khó hơn. Phép nhân ở trên giả định các dịch vụ hỏng độc lập; trong thực tế nhiều dịch vụ hỏng cùng lúc vì cùng một nguyên nhân, nên con số thật khác. Cách hiểu "chín" và cách đo thời gian ngừng (ngừng một phần có tính không) khác nhau giữa các tổ chức; bài này dùng cách tính đơn giản nhất. Bài chưa đối chiếu được tài liệu chính thức nào trong phiên viết.

## Nhìn hình trả lời

Một cửa hàng trực tuyến luôn mở được trang, nhưng thỉnh thoảng hiển thị tồn kho sai làm khách đặt hàng không còn hàng. Thước đo nào đang kém, và thêm máy chủ có sửa được không?

<details>
<summary>Xem đáp án</summary>

Độ tin cậy đang kém: hệ thống vẫn sẵn sàng (trang mở được) nhưng trả kết quả sai. Thêm máy chủ không tự sửa được, vì lỗi nằm ở việc giữ dữ liệu tồn kho đúng và nhất quán, không ở sức chứa; thậm chí nhiều bản sao dữ liệu còn làm việc đó khó hơn. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn chỉ nêu bốn tên và một câu cho mỗi tên. Bài này giữ tên, đổi mỗi câu thành một câu hỏi mà người xây hệ thống tự hỏi, và thêm hai phép tính (số giờ được ngừng, độ sẵn sàng của chuỗi nối tiếp) để thấy các con số này nặng đến đâu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/who-are-the-fantastic-four-of-system-design.md): chỉ lấy tên bốn thước đo. Lời giải thích và các phép tính là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức; các phép tính là số học thuần túy.

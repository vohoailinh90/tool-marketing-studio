# Event sourcing: lưu sự kiện thay vì trạng thái

**Thay vì ghi đè trạng thái mới nhất của một thứ (giỏ hàng, tài khoản), event sourcing ghi lại từng sự kiện đã làm nên nó, và lấy trạng thái hiện tại bằng cách phát lại các sự kiện.** Kho sự kiện là nguồn sự thật; mọi cái khác (bảng tra cứu, chỉ mục tìm kiếm) là bản suy ra từ nó. Bài này dựng ý đó trên một giỏ hàng nhỏ, thử cái giá của việc phát lại, và nói những chỗ khó.

![Hai khung. Khung một, sơ đồ trình tự giữa dịch vụ giỏ hàng, kho sự kiện và dịch vụ thanh toán: giỏ hàng ghi sự kiện thêm món và bỏ món vào kho, kho phát sự kiện mới cho dịch vụ thanh toán, dịch vụ thanh toán đọc lại từ đầu và nhận các sự kiện. Khung hai, thử nghiệm: dựng lại giỏ hàng từ 100500 sự kiện cần áp dụng 100500 sự kiện, từ ảnh chụp mỗi 1000 sự kiện chỉ cần 500; hai bên cùng ghi vào phiên bản 0 thì bên thứ hai bị từ chối.](../../diagrams/sd-11-026-main.svg)

## Từ viết tắt

- **CRUD** (Create, Read, Update, Delete) — tạo, đọc, sửa, xóa: kiểu làm việc quen thuộc với dữ liệu, chỉ giữ giá trị mới nhất và ghi đè lên giá trị cũ.
- **CQRS** (Command Query Responsibility Segregation) — tách trách nhiệm lệnh và truy vấn: ghi và đọc đi qua hai mô hình riêng, thường kèm một kho chỉ để đọc.

## Đọc hình

**Dòng sự kiện của một thực thể.** Mỗi thực thể (một giỏ hàng) có dòng sự kiện riêng: dãy có thứ tự các điều đã xảy ra, như "thêm món A", "bỏ món A". Sự kiện chỉ được thêm vào cuối, không sửa, không xóa. Muốn biết giỏ hàng bây giờ có gì thì phát lại dòng đó từ đầu (việc này có tên là rehydration, tạm dịch "làm đầy lại").

**Ai nghe.** Mỗi khi một sự kiện được ghi, các bên quan tâm có thể nghe và làm việc của mình: dịch vụ thanh toán, dịch vụ chống gian lận, dịch vụ gửi thư. Mỗi bên tự quyết định nó giữ mô hình dữ liệu nào, vì sự thật nằm ở sự kiện chứ không ở bảng của ai. Trong hình, dịch vụ thanh toán cũng có thể đọc lại dòng sự kiện từ đầu để dựng mô hình của riêng nó.

**Ba hình thức dùng thường gặp.** Một trang báo lưu mọi bài viết dưới dạng sự kiện rồi suy ra các chỉ mục tìm kiếm; một bộ thu thập thay đổi dữ liệu biến thay đổi của bảng thành sự kiện cho các bên khác tiêu thụ; hay các dịch vụ trao đổi nhau bằng sự kiện (ví dụ dịch vụ giỏ hàng phát ra sự kiện cho thanh toán, chống gian lận, gửi thư). Đây là các ví dụ của bài nguồn.

## Thử: cái giá của việc phát lại

Ngày 2026-10-19, một chương trình Python nhỏ, không có cơ sở dữ liệu. Một giỏ hàng nhận 100500 sự kiện thêm và bỏ món (50 loại món).

| Phép thử | Kết quả |
|---|---|
| Dựng trạng thái từ đầu | áp dụng 100500 sự kiện |
| Dựng từ ảnh chụp tại sự kiện 100000 (chụp mỗi 1000 sự kiện) | áp dụng 500 sự kiện, ra trạng thái y hệt |
| Hai bên cùng đọc phiên bản 0 rồi cùng ghi | bên thứ nhất được, bên thứ hai bị từ chối |

Ảnh chụp là một tối ưu hóa, không thay cho dòng sự kiện: bỏ nó đi thì dựng lại từ đầu vẫn ra cùng kết quả. Dòng cuối là kiểm soát đồng thời kiểu lạc quan: khi ghi phải nói "tôi đã đọc tới phiên bản nào"; nếu dòng đã đổi, lần ghi bị từ chối và bên ghi đọc lại rồi thử lại.

## Giới hạn cần nhớ

Mô hình đếm số lần áp dụng, không đo thời gian thật. Các chỗ khó của event sourcing, theo hướng dẫn kiến trúc của Microsoft, nằm ngoài mô hình: trạng thái chỉ nhất quán sau một lúc (bản suy ra trễ hơn kho sự kiện); sự kiện đã ghi không sửa được nên sai thì phải thêm sự kiện bù, và đổi dạng sự kiện cần chiến lược (chấp nhận trường lạ, đánh phiên bản, chuyển dạng cũ sang mới khi đọc); bên tiêu thụ có thể nhận một sự kiện hai lần nên phải xử lý lặp lại không đổi kết quả; quy định xóa dữ liệu cá nhân mâu thuẫn với kho chỉ thêm, nên thường để dữ liệu cá nhân ngoài sự kiện hoặc mã hóa bằng khóa riêng rồi hủy khóa. Một hệ truyền thông điệp như Kafka phân phối sự kiện tốt nhưng thường không thay được kho sự kiện, vì thiếu đọc theo thực thể và kiểm soát đồng thời.

## Nhìn hình trả lời

Một cửa hàng cần biết "khách đã bỏ món A bao nhiêu lần trước khi mua". Với CRUD ghi đè giỏ hàng thì dữ liệu này còn không, và với event sourcing thì sao?

<details>
<summary>Xem đáp án</summary>

Với CRUD ghi đè, giỏ hàng chỉ còn trạng thái cuối, trừ khi có thêm cơ chế ghi lịch sử riêng, nên câu hỏi đó không trả lời được. Với event sourcing, mọi lần bỏ món đã nằm trong dòng sự kiện, nên đếm lại là được, kể cả cho câu hỏi chưa ai nghĩ ra lúc thiết kế.
Đây là suy luận của người biên soạn, khớp với điểm mạnh về lịch sử mà tài liệu của Microsoft nêu.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn đưa ba ví dụ dùng event sourcing và nói ngắn gọn về kho sự kiện. Bài này giữ ba ví dụ, thêm cách dựng lại trạng thái, ảnh chụp, kiểm soát đồng thời kiểu lạc quan bằng một thử nghiệm riêng, cùng các giới hạn lấy từ tài liệu kiến trúc của Microsoft (đã đọc).

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-incorporate-event-sourcing-into-the-systems.md): ba ví dụ dùng. Thử nghiệm và đáp án là của người biên soạn.
- [Microsoft — Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing): dòng sự kiện, ảnh chụp, kiểm soát đồng thời, giới hạn. Đã đọc bản trên kho GitHub MicrosoftDocs/architecture-center.
- [Martin Fowler — Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html): mô tả gốc của mẫu. Kiến thức chung, chưa mở lại trong phiên viết.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

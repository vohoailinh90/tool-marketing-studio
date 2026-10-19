# Phát hiện nút hỏng trong hệ thống phân tán: sáu biến thể của nhịp tim

**Muốn biết một nút còn sống, hệ thống nhờ nó "đập nhịp" đều đặn. Sáu biến thể dưới đây khác nhau ở chỗ ai chủ động, nhịp tim mang theo gì, và ai được quyền kết luận một nút đã hỏng.**
Điều khó nhất không nằm ở việc nghe nhịp, mà ở việc đặt ngưỡng chờ.

![Hai khung. Khung một, ai chủ động: nút tự gửi nhịp, bên giám sát chủ động hỏi, hoặc nhịp kèm kiểm tra sức khỏe. Khung hai, làm cho đáng tin hơn: nhịp kèm mốc thời gian, nhịp có xác nhận, và nhiều nút cùng đồng ý trước khi kết luận.](../../diagrams/sd-11-009-main.svg)

## Đọc hình

Tên sáu biến thể giữ theo bài nguồn; phần giải thích và thử nghiệm là của người biên soạn.

**Ai chủ động**

- **Push-Based Heartbeat (nút tự đẩy nhịp).** Mỗi nút gửi một tín hiệu cho bên giám sát theo chu kỳ. Quá một ngưỡng thời gian không thấy tín hiệu thì nghi nút hỏng. Gọn và rẻ; nhưng bên giám sát chỉ biết "không nghe thấy", không biết vì nút hỏng hay vì đường truyền.
- **Pull-Based Heartbeat (bên giám sát chủ động hỏi).** Bên giám sát gửi câu hỏi theo chu kỳ và chờ trả lời. Bên giám sát nắm nhịp độ, nhưng tải hỏi tăng theo số nút.
- **Heartbeat with Health Check (nhịp kèm kiểm tra sức khỏe).** Nút trả lời không chỉ "tôi còn chạy" mà còn "tôi còn làm được việc": kiểm tra nội bộ như kết nối tới cơ sở dữ liệu. Một tiến trình còn chạy nhưng đã kẹt vẫn bị phát hiện.

**Làm cho đáng tin hơn**

- **Heartbeat with Timestamps (nhịp kèm mốc thời gian).** Mỗi nhịp ghi thời điểm gửi, giúp phát hiện nhịp đến muộn hoặc đến lộn xộn. Mốc thời gian chỉ đáng tin khi đồng hồ các nút không lệch nhau nhiều.
- **Heartbeat with Acknowledgement (nhịp có xác nhận).** Bên nhận phản hồi để bên gửi biết nhịp đã tới nơi.
- **Heartbeat with Quorum (nhịp theo đa số).** Nhiều nút giám sát cùng quan sát; nút chỉ bị coi là hỏng khi đủ đa số đồng ý. Một nút giám sát nghe lỗi vì đường truyền riêng của nó không còn kéo cả hệ thống đi theo.

**Thử nghiệm: ngưỡng chờ bao lâu?** Giả định (đây là mô hình tự đặt, không phải số đo thật): một nhịp mỗi giây; độ trễ mạng là 20 ms cộng một khoảng ngẫu nhiên trung bình 80 ms; 1% số nhịp bị chậm thêm từ 0,5 đến 2 giây. Mỗi lần khoảng cách giữa hai nhịp liên tiếp tới nơi vượt ngưỡng được tính là một lần nghi nhầm. Mô phỏng 2 000 000 nhịp (khoảng 556 giờ, hạt giống ngẫu nhiên 1) cho thấy: ngưỡng 1,5 giây khoảng 38 lần mỗi giờ, 2 giây khoảng 24 lần mỗi giờ, 3 giây khoảng 492 lần trong cả 556 giờ (chưa tới một lần mỗi giờ), 5 giây không lần nào. Ngưỡng càng cao càng ít báo nhầm, nhưng nút hỏng thật cũng bị phát hiện chậm đúng bằng ngưỡng đó.

## Giới hạn cần nhớ

Nhịp tim không cho biết chắc nút đã hỏng: trong mạng không bảo đảm thời gian, nút chậm và nút hỏng nhìn từ ngoài giống hệt nhau (kết quả quen thuộc trong lý thuyết hệ thống phân tán; bài chưa đối chiếu lại với tài liệu gốc). Bởi vậy "nghi" là từ chính xác hơn "biết". Các con số của thử nghiệm phụ thuộc hoàn toàn vào mô hình giả định ở trên; chúng minh họa chiều của đánh đổi, không dự đoán mạng của bạn.

## Nhìn hình trả lời

Một nút báo nhịp đều, nhưng người dùng thấy dịch vụ không phản hồi. Biến thể nào trong hình bắt được trường hợp này, và vì sao nhịp thường không bắt được?

<details>
<summary>Xem đáp án</summary>

Nhịp kèm kiểm tra sức khỏe: tiến trình có thể còn chạy và còn đập nhịp trong khi phần xử lý đã kẹt, nên nhịp thường nói "còn chạy" chứ không nói "còn làm được việc". Kiểm tra sức khỏe hỏi thẳng vào khả năng làm việc. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê sáu biến thể. Bài này giữ tên và thứ tự, chia thành hai nhóm (ai chủ động, làm cho đáng tin hơn) và thêm một thử nghiệm mô phỏng về việc chọn ngưỡng chờ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-detect-node-failures-in-distributed-systems.md): chỉ lấy tên sáu biến thể. Phần giải thích và thử nghiệm là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức; thử nghiệm là mô phỏng với mô hình giả định ghi trong bài.

# Ngôn ngữ lập trình nào "xanh" nhất?

**Một nghiên cứu đã đo cả thời gian chạy, bộ nhớ và năng lượng của nhiều ngôn ngữ trên cùng mười bài toán, để người viết phần mềm có thêm căn cứ khi năng lượng là mối quan tâm.**
Bài nguồn chỉ có một đoạn trích tóm tắt nghiên cứu và một tấm ảnh bảng so sánh. Bài này không dùng ảnh nên không chép bảng xếp hạng; nó đọc cách làm và cách dùng kết quả cho thận trọng.

![Ba nhóm thẻ xếp dọc. Cách làm của nghiên cứu, ba bước: chọn mười bài toán chuẩn; viết mỗi bài bằng từng ngôn ngữ; đo ba thứ là thời gian chạy, bộ nhớ và năng lượng. Điều tóm tắt nêu, ba ý: có trường hợp ngôn ngữ chạy chậm hơn lại tốn ít năng lượng hơn và ngược lại; mức dùng bộ nhớ ảnh hưởng tới năng lượng tiêu thụ; kết quả giúp kỹ sư quyết định ngôn ngữ khi quan tâm hiệu quả năng lượng. Đọc thận trọng, ba ý: mười bài toán chuẩn không phải ứng dụng của bạn; bài nguồn tự nói cách nhìn này có thể gây tranh cãi; số ngôn ngữ nguồn ghi hai lần khác nhau nên cần kiểm bản gốc.](../../diagrams/sd-10-004-main.svg)

## Đọc hình

**Cách làm.** Nghiên cứu chạy mười bài toán chuẩn (benchmark), mỗi bài được viết bằng từng ngôn ngữ trong nhóm gần ba mươi ngôn ngữ. Với mỗi ngôn ngữ, nó đo ba thứ: thời gian chạy, bộ nhớ dùng và năng lượng tiêu thụ.

**Điều tóm tắt nêu.** Đoạn tóm tắt kể những phát hiện thú vị: có trường hợp ngôn ngữ chạy chậm hơn lại tốn ít năng lượng hơn và ngược lại, và mức dùng bộ nhớ ảnh hưởng tới năng lượng tiêu thụ. Các tác giả muốn kết quả giúp kỹ sư phần mềm quyết định dùng ngôn ngữ nào khi hiệu quả năng lượng là mối quan tâm.

**Đọc thận trọng.** Chính bài nguồn nói cách nhìn này có thể gây tranh cãi. Mười bài toán chuẩn chỉ là mười bài toán, không đại diện cho chương trình của bạn.

## Giới hạn cần nhớ

Bài nguồn ghi hai con số khác nhau cho số ngôn ngữ: "28 ngôn ngữ" ở câu mở đầu, còn đoạn tóm tắt được trích nguyên văn ghi "hai mươi bảy". Bài này vì vậy chỉ nói "gần ba mươi"; nếu cần trích số chính xác, hãy mở bài báo gốc.
Bảng xếp hạng nằm trong ảnh của bài nguồn, bài này không dùng và cũng chưa đối chiếu được, nên không nêu ngôn ngữ nào "xanh nhất". Câu hỏi trong tiêu đề vì thế được trả lời bằng cách đọc nghiên cứu, không bằng một cái tên.
Kết luận rằng ngôn ngữ nhanh hơn hay chậm hơn thì tốn ít hay nhiều năng lượng chỉ đúng trong khuôn khổ các bài toán đã đo; đây là cảnh báo chung của người biên soạn, không phải câu của nguồn.

## Nhìn hình trả lời

Đội bạn chọn ngôn ngữ cho một dịch vụ chạy liên tục và muốn tiết kiệm điện. Dựa trên bài này, hai việc nên làm trước khi tin một bảng xếp hạng ngôn ngữ "xanh" là gì?

<details>
<summary>Xem đáp án</summary>

Thứ nhất, nhìn đủ cả ba số đo, không riêng thời gian chạy, vì tóm tắt nói ngôn ngữ nhanh hơn hay chậm hơn không đương nhiên tốn ít hay nhiều năng lượng hơn, và bộ nhớ cũng ảnh hưởng.
Thứ hai, kiểm tra mười bài toán đã đo có giống việc của dịch vụ mình không, và mở bài báo gốc để kiểm các chi tiết như số ngôn ngữ, vì nguồn tự ghi hai con số.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một đoạn dẫn ngắn kèm trích nguyên văn phần tóm tắt của nghiên cứu. Hình này tách ba phần: cách làm, điều tóm tắt nêu và các lưu ý khi đọc.
Mọi câu về kết quả đều lấy từ phần tóm tắt trích trong nguồn; bài không đọc bài báo gốc và không biết bảng số liệu của nó.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-greenest-programming-languages.md): đoạn dẫn và phần tóm tắt nghiên cứu về thời gian chạy, bộ nhớ và năng lượng.

Đã đọc nguồn ngày 2026-10-18. Chưa đọc bài báo gốc của nghiên cứu; lưu ý về phạm vi kết quả là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

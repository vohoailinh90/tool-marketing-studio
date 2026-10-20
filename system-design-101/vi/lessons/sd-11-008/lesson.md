# Năm cặp đánh đổi trong thiết kế hệ thống: được cái này, trả bằng cái kia

**Mỗi cặp đánh đổi nói rằng hai điều tốt không đạt cực đại cùng lúc. Việc của người thiết kế là chọn nghiêng về phía nào, ở chỗ nào, vì lý do gì.**
Nhìn cặp nào đang kéo nhau, bạn thấy quyết định thật sự nằm ở đâu.

![Năm ghi chú, mỗi ghi chú là một cặp đánh đổi: chi phí và hiệu năng, độ tin cậy và khả năng mở rộng, hiệu năng và tính nhất quán, bảo mật và tính linh hoạt, tốc độ phát triển và chất lượng. Mỗi ghi chú nói điều gì kéo hai phía ra xa nhau.](../../diagrams/sd-11-008-main.svg)

## Đọc hình

Tên năm cặp giữ theo bài nguồn; phần giải thích và ví dụ là của người biên soạn.

**Cost vs. Performance (chi phí và hiệu năng).** Máy mạnh hơn, nhiều bản sao hơn thì nhanh hơn nhưng đắt hơn. Câu hỏi: nhanh thêm một chút có đáng tiền thêm không, và người dùng có nhận ra không?

**Reliability vs. Scalability (độ tin cậy và khả năng mở rộng).** Thêm máy giúp chịu tải, nhưng càng nhiều máy thì càng nhiều chỗ có thể hỏng và càng nhiều mối nối phải đúng. Giữ hệ thống đáng tin khi lớn lên là việc riêng, không tự đến cùng với việc mở rộng.

**Performance vs. Consistency (hiệu năng và tính nhất quán).** Bắt mọi bản sao khớp nhau trước khi trả lời thì chậm hơn; trả lời ngay thì có thể trả dữ liệu cũ. Chọn theo việc đang làm: số dư tài khoản khác với số lượt xem.

**Security vs. Flexibility (bảo mật và tính linh hoạt).** Kiểm soát chặt hơn thì ít cách đi lạc hơn nhưng khó thay đổi và khó dùng hơn. Mỗi quyền nới ra là một bề mặt tấn công mới.

**Development Speed vs. Quality (tốc độ phát triển và chất lượng).** Ra nhanh thì bỏ bớt kiểm thử và thiết kế; khoản nợ đó thường trả lãi bằng lỗi và công sửa về sau. Có lúc ra nhanh là lựa chọn đúng, miễn là biết mình đang vay.

## Giới hạn cần nhớ

Năm cặp lấy từ bài nguồn, không phải danh sách đầy đủ: còn nhiều cặp khác (như độ trễ và thông lượng). "Đánh đổi" cũng không phải lúc nào cũng là chọn một bỏ một: có khi một cách làm tốt hơn khiến hai phía cùng khá hơn. Ví dụ và cách diễn đạt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức.

## Nhìn hình trả lời

Hệ thống ghi sổ chuyển khoản và hệ thống đếm lượt xem video. Với cặp hiệu năng và nhất quán, mỗi hệ thống nên nghiêng về phía nào?

<details>
<summary>Xem đáp án</summary>

Sổ chuyển khoản nghiêng về nhất quán: chậm hơn một chút còn hơn hiển thị sai số tiền. Lượt xem nghiêng về hiệu năng: chậm cập nhật vài giây hay lệch một ít không ai bị thiệt. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê năm cặp. Bài này giữ tên và thứ tự, thêm câu hỏi cần trả lời ở mỗi cặp và lưu ý rằng không phải đánh đổi nào cũng là chọn một bỏ một.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-5-trade-offs-in-system-designs.md): chỉ lấy tên năm cặp. Phần giải thích là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức.

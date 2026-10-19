# Mười cuốn sách cho người phát triển phần mềm

**Mười cuốn sách chia thành năm nhóm, mỗi nhóm hai cuốn: lời khuyên chung, viết mã, kiến trúc phần mềm, mẫu thiết kế, và cấu trúc dữ liệu cùng thuật toán.**
Bài giữ tên nhóm, tên sách và tác giả của danh sách gợi ý trong bài nguồn; phần nói mỗi cuốn dạy gì là lời của người biên soạn, viết từ hiểu biết chung về các cuốn này.

![Năm nhóm xếp dọc, mỗi nhóm hai cuốn. Lời khuyên chung: The Pragmatic Programmer của Hunt và Thomas, Code Complete của McConnell. Viết mã: Clean Code của Martin, Refactoring của Fowler. Kiến trúc phần mềm: Designing Data-Intensive Applications của Kleppmann, System Design Interview của Alex Xu. Mẫu thiết kế: Design Patterns của Gamma cùng ba đồng tác giả, Domain-Driven Design của Evans. Cấu trúc dữ liệu và thuật toán: Introduction to Algorithms của Cormen, Leiserson, Rivest và Stein, Cracking the Coding Interview của McDowell. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-013-main.svg)

## Đọc hình

**Lời khuyên chung.** *The Pragmatic Programmer* của Andrew Hunt và David Thomas bàn về thói quen làm nghề: cách suy nghĩ, cách làm việc hằng ngày của một người viết phần mềm, hơn là một công nghệ cụ thể. *Code Complete* của Steve McConnell đi theo hướng khác: một cuốn sổ tay dày về việc xây dựng phần mềm, từ đặt tên, tổ chức hàm và lớp tới kiểm thử và gỡ lỗi.

**Viết mã.** *Clean Code* của Robert C. Martin tập trung vào mã dễ đọc: đặt tên rõ nghĩa, hàm ngắn làm một việc, chú thích đúng chỗ. *Refactoring* của Martin Fowler dạy cách sửa cấu trúc bên trong của mã bằng những bước nhỏ mà hành vi nhìn từ ngoài không đổi, kèm danh mục các thủ thuật sửa thường gặp.

**Kiến trúc phần mềm.** *Designing Data-Intensive Applications* của Martin Kleppmann nói về các hệ thống chủ yếu xoay quanh dữ liệu: cách lưu trữ, sao chép, chia nhỏ dữ liệu, giao dịch và xử lý theo lô hay theo dòng. *System Design Interview* của Alex Xu đi qua từng bài thiết kế hệ thống mẫu theo kiểu một buổi phỏng vấn; đây là sách của chính nhóm ByteByteGo, người viết bài nguồn.

**Mẫu thiết kế.** *Design Patterns* của Erich Gamma, Richard Helm, Ralph Johnson và John Vlissides là danh mục các mẫu thiết kế hướng đối tượng, mỗi mẫu gồm vấn đề, cách giải và lúc nên dùng. *Domain-Driven Design* của Eric Evans bàn về cách dựng mô hình phần mềm bám sát lĩnh vực nghiệp vụ phức tạp, với một ngôn ngữ chung giữa người làm nghiệp vụ và người viết mã.

**Cấu trúc dữ liệu và thuật toán.** *Introduction to Algorithms* của Thomas Cormen, Charles Leiserson, Ronald Rivest và Clifford Stein là giáo trình đại học về thuật toán và cách chứng minh chúng đúng, chạy nhanh. *Cracking the Coding Interview* của Gayle Laakmann McDowell tập hợp câu hỏi lập trình hay gặp trong phỏng vấn kèm lời giải và cách luyện.

## Giới hạn cần nhớ

Các lời nói về nội dung từng cuốn ở trên là hiểu biết chung của người biên soạn, chưa đối chiếu với trang của nhà xuất bản hay tác giả (môi trường soạn bài không mở được các trang đó). Bài không nói năm xuất bản hay lần in, không đánh giá chất lượng và không khuyên đọc cuốn nào trước.
Bài nguồn không có thứ tự đọc, trình độ hay lý do chọn đúng mười cuốn này. Một cuốn trong danh sách là sách của chính nhóm viết bài nguồn, nên đây là danh sách gợi ý của một bên có liên quan, không phải bảng xếp hạng độc lập.
Bài nguồn ghi tác giả đầu của *Design Patterns* là "Eric Gamma"; tên thường được dùng cho người này là Erich Gamma, và bài viết theo tên đó mà chưa đối chiếu với trang sách.

## Nhìn hình trả lời

Bạn muốn học cách sửa mã bằng những bước nhỏ mà không làm hỏng chương trình: cuốn nào, thuộc nhóm nào? Cuốn nào trong danh sách là sách của chính nhóm viết bài nguồn?

<details>
<summary>Xem đáp án</summary>

*Refactoring* của Martin Fowler, thuộc nhóm viết mã.
*System Design Interview*, thuộc nhóm kiến trúc phần mềm.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và danh sách mười cuốn theo năm nhóm. Bài này giữ tên nhóm, tên sách và tên tác giả, vì đó là dữ kiện. Phần nói mỗi cuốn bàn về gì là phần bài tự viết; nguồn chỉ mô tả riêng một cuốn nên bài không bám theo câu chữ nào của nguồn. Hình tự vẽ lại thành các thẻ, bài không dùng ảnh nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/10-books-for-software-developers.md): chỉ lấy tên nhóm, tên sách và tên tác giả.

Đã đọc nguồn ngày 2026-10-19. Phần mô tả từng cuốn là hiểu biết chung của người biên soạn, chưa đối chiếu với trang nhà xuất bản hay tác giả; chuyện tên Erich Gamma cũng vậy.
Bài viết và hình được thiết kế độc lập.

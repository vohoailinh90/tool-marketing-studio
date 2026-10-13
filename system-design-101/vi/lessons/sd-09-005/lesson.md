# Merge và rebase: ghép lịch sử khác nhau

Nhánh tính năng của bạn bắt đầu từ A. Trong lúc bạn tạo F, nhánh main có thêm B. Muốn đưa thay đổi mới vào nhánh tính năng, bạn có thể giữ hai đường lịch sử bằng merge hoặc phát lại thay đổi bằng rebase.

![Trước khi ghép: main: A → B | feature: A → F; Merge khi đã phân nhánh: M có hai cha: B và F; Rebase feature lên main: A → B → F′; Điểm khác nhau: F′ thường có ID khác F.](../../diagrams/sd-09-005-main.svg)

**Đọc hình:** Các thẻ là các bước hoặc góc nhìn của ví dụ; đọc từ trên xuống. Mũi tên chỉ thứ tự đọc, không biểu diễn luồng mạng hoặc sự phụ thuộc bắt buộc.

Merge trong tình huống đã phân nhánh tạo commit M nối hai lịch sử. Các commit cũ vẫn giữ ID; con trỏ của nhánh nhận merge di chuyển tới kết quả. Khi nhánh nhận chỉ cần đi tiến tới commit đã có, Git có thể fast-forward và không tạo merge commit.

Rebase phát lại thay đổi của F trên nền B, thường tạo F′ với parent mới và ID mới. Lịch sử nhìn thẳng hơn, nhưng người đã dựa trên F cần biết lịch sử đã thay đổi. Cả merge và rebase đều có thể gặp xung đột; hình đang giả định giải quyết thành công.

## Nhìn hình thử trả lời

Có thể kết luận mọi lần git merge đều sinh commit có hai parent không?

<details>
<summary>Xem đáp án</summary>

Không. Một merge có thể fast-forward nếu lịch sử cho phép; tùy chọn cũng ảnh hưởng cách tích hợp.

</details>

## Giới hạn cần nhớ

Tránh rebase lịch sử người khác đã sử dụng nếu chưa thống nhất cách phối hợp. Rebase không phải cách an toàn mặc định để sửa nhánh chung.

<details>
<summary>Xem sâu hơn</summary>

Sơ đồ nói về ancestry, không đo chất lượng code. Sau tích hợp, chạy lại kiểm tra trên nội dung cuối cùng. Lịch sử tuyến tính không bảo đảm các thay đổi kết hợp đúng.

</details>

## Nguồn đối chiếu

- [Chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/git-merge-vs-git-rebate.md). Bài viết và hình này được thiết kế độc lập; không dịch thân bài hoặc sử dụng ảnh nguồn.
- [Git merge](https://git-scm.com/docs/git-merge).
- [Git rebase](https://git-scm.com/docs/git-rebase).

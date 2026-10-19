# Dòng "For You" của Twitter: từ 500 triệu tweet xuống một trang

**Theo bài nguồn, Twitter chọn dòng "For You" qua năm chặng trong khoảng 1,5 giây: gom ứng viên, lọc chung, chấm điểm, lọc cho đa dạng, rồi trộn với quảng cáo và gợi ý theo dõi.**
Bài nguồn dựa trên thuật toán Twitter đã công bố mã nguồn. Bài này đi qua năm chặng như một cái phễu: mỗi chặng làm gì, và vì sao chặng tốn kém nhất được đặt sau khi số ứng viên đã nhỏ.

![Hai khung bước và một khung ghi nhớ. Khung một, thu hẹp: gom ứng viên, bắt đầu từ khoảng 500 triệu tweet; lọc chung, còn 1.500 ứng viên; chấm điểm và xếp hạng bằng một mạng nơ-ron 48 triệu tham số, có cộng điểm cho Twitter Blue. Khung hai, hoàn thiện trang: lọc để đa dạng tác giả và nội dung; trộn với quảng cáo và gợi ý nên theo dõi ai. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-011-main.svg)

## Đọc hình

**Thu hẹp.**
- Gom ứng viên (candidate sourcing): bắt đầu từ khoảng 500 triệu tweet.
- Lọc chung (global filtering): còn 1.500 ứng viên.
- Chấm điểm và xếp hạng (scoring & ranking): một mạng nơ-ron 48 triệu tham số chấm điểm từng ứng viên; tài khoản Twitter Blue được cộng điểm.

**Hoàn thiện trang.**
- Lọc (filtering): để các tweet trên trang đa dạng về tác giả và nội dung.
- Trộn (mixing): ghép với quảng cáo được gợi ý và mục "nên theo dõi ai" (Who to Follow).

Toàn bộ chặng đường được nêu trong tiêu đề bài nguồn là khoảng 1,5 giây.

## Giới hạn cần nhớ

Bài nguồn chỉ có năm dòng; nó không nói mỗi chặng tốn bao lâu, không nói 500 triệu là số tweet trong khoảng thời gian nào, và không nói lọc chung dựa trên tiêu chí gì. Các con số là của bài nguồn, đọc từ mã đã công bố tại thời điểm đó; hệ thống thật có thể đã khác. Nhận xét về cái phễu ở dưới là của người biên soạn.

## Nhìn hình thử trả lời

Mạng nơ-ron 48 triệu tham số chấm điểm 1.500 ứng viên. Nếu nó phải chấm thẳng 500 triệu tweet thì sao, và thiết kế trong hình tránh điều đó bằng cách nào?

<details>
<summary>Xem đáp án</summary>

Chấm 500 triệu tweet bằng một mô hình lớn cho mỗi lần mở trang thì quá chậm và quá tốn, không thể xong trong khoảng 1,5 giây. Thiết kế đặt các chặng rẻ (gom và lọc chung) lên trước để thu hẹp còn 1.500 ứng viên, rồi mới dùng mô hình đắt trên số nhỏ đó.

</details>

<details>
<summary>Xem sâu hơn: vì sao còn lọc sau khi đã xếp hạng</summary>

- Xếp hạng chấm từng tweet riêng lẻ, nên có thể đẩy lên nhiều tweet của cùng một người hay cùng một chủ đề.
- Chặng lọc sau nhìn cả trang, sửa sự lặp đó.
- Chặng trộn cuối cùng ghép các thứ không phải tweet của người khác (quảng cáo, gợi ý theo dõi) vào đúng chỗ.

Đây là cách đọc của người biên soạn; bài nguồn chỉ nêu mục đích "đa dạng tác giả và nội dung".

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-twitter-recommend-tweets.md): năm chặng chọn dòng "For You" và các con số ở từng chặng.

Đã đọc nguồn ngày 2026-10-19. Mã thuật toán Twitter đã công bố, nơi bài nguồn dựa vào, chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

# Levels.fyi: bảng tính làm backend cho hàng triệu người dùng

**Một trang web có hàng triệu người dùng mỗi tháng vẫn có thể chạy trên Google Forms và Google Sheets, nếu nhóm làm sản phẩm chọn bắt đầu đơn giản.** Theo bài nguồn, Levels.fyi (trang so sánh lương trong ngành công nghệ) đã làm đúng như vậy trước khi chuyển sang một backend thật.
Bài này không cổ vũ dùng bảng tính làm cơ sở dữ liệu; nó hỏi cách đó cho gì, và dấu hiệu nào cho biết đã tới lúc đổi.

![Ba khung xếp dọc. Lúc đầu không có backend riêng: người dùng gửi số liệu qua Google Forms, dữ liệu vào Google Sheets đóng vai cơ sở dữ liệu, có dùng hàm serverless, nhưng nguồn không nói hàm đó làm gì. Cách này cho gì: ra mắt nhanh, không phải vận hành máy chủ cơ sở dữ liệu, thời gian dồn vào sản phẩm. Khi nào nên đổi: cần ràng buộc dữ liệu hay giao dịch, chạm hạn mức của bảng tính, truy vấn mới khó viết.](../../diagrams/sd-02-006-main.svg)

## Đọc hình

**Lúc đầu.** Theo nguồn, Levels.fyi bắt đầu với Google Forms để nhận dữ liệu và Google Sheets để lưu, và nhờ đó đạt tới hàng triệu người dùng hoạt động mỗi tháng trước khi đổi sang backend riêng. Họ có dùng điện toán serverless, tức là chạy các hàm nhỏ trên hạ tầng của nhà cung cấp mà không tự quản máy chủ, nhưng phần lưu dữ liệu là bảng tính. Bài nguồn không nói các hàm serverless đó làm gì, cũng không nói trang web đọc dữ liệu qua đường nào.

**Lý do của họ.** Bài nguồn trích lời nhóm Levels.fyi: nghe thì ngược đời khi một trang có lượng truy cập như họ không có backend hay hạ tầng cầu kỳ, nhưng triết lý làm sản phẩm của họ luôn là bắt đầu đơn giản rồi cải tiến dần, để đi nhanh và tập trung vào điều quan trọng.

**Cách này cho gì.** Không phải dựng, sao lưu, nâng cấp một máy chủ cơ sở dữ liệu. Người không viết mã cũng xem và sửa được dữ liệu. Nhóm thử ý tưởng ngay, trước khi biết ý tưởng có người dùng hay không.

## Giới hạn cần nhớ

Bảng tính thiếu nhiều thứ một cơ sở dữ liệu có sẵn: ràng buộc kiểu dữ liệu, giao dịch khi nhiều người ghi cùng lúc, chỉ mục cho truy vấn phức tạp. Dịch vụ bảng tính trực tuyến cũng có hạn mức số lần gọi và kích thước. Những giới hạn này là kiến thức chung của người biên soạn, không phải từ bài nguồn, và bài nguồn không nói Levels.fyi chuyển đi vì giới hạn nào.
Một lưu ý nữa: trang của Levels.fyi chủ yếu là đọc, người dùng gửi số liệu ít hơn nhiều so với lượt xem. Lý do này là suy luận của người biên soạn; nó giải thích phần nào vì sao bảng tính chịu được lâu, và cũng là lý do đừng chép nguyên cách này cho một ứng dụng ghi nhiều.

## Nhìn hình thử trả lời

Bạn làm một ứng dụng đặt chỗ, nhiều người có thể bấm đặt cùng một ghế trong cùng một giây. Bảng tính có hợp làm nơi lưu đơn đặt chỗ không? Khung nào của hình trả lời?

<details>
<summary>Xem đáp án</summary>

Không hợp. Khung "Khi nào nên đổi" đã nêu: ứng dụng này cần giao dịch thật để hai người không cùng giữ một ghế, và đó là thứ bảng tính không bảo đảm. Levels.fyi chịu được lâu một phần vì phần lớn lượt truy cập chỉ đọc số liệu.

</details>

<details>
<summary>Xem sâu hơn: "bắt đầu đơn giản" không có nghĩa là không có kế hoạch</summary>

Bắt đầu đơn giản hiệu quả khi nhóm biết trước đường rút: dữ liệu nằm ở một chỗ dễ xuất ra, phần đọc dữ liệu được gói trong vài hàm để sau này chỉ thay bên trong. Khi đó việc chuyển sang cơ sở dữ liệu thật là một dự án có giới hạn, không phải viết lại từ đầu.
Đây là gợi ý của người biên soạn; bài nguồn không mô tả cách Levels.fyi chuyển đổi.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-levelsfyi-scaled-to-millions-of-users-with-google-sheets.md): Google Forms và Sheets làm backend, serverless, lời trích về triết lý bắt đầu đơn giản.

Đã đọc nguồn ngày 2026-10-19. Bài viết gốc của Levels.fyi chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

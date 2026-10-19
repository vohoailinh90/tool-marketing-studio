# Khả năng mở rộng của kiến trúc: ba nút thắt, ba nguyên tắc, bốn kỹ thuật

**Một hệ thống mở rộng được khi tăng tải mà vẫn giữ hiệu năng, và khi cách mở rộng còn đủ rẻ để lặp lại. Có ba kiểu thành phần hay chặn đường, và ba nguyên tắc để tránh chúng.**
Biết nút thắt nào đang chặn, bạn chọn đúng kỹ thuật thay vì thêm máy một cách mù quáng.

![Hai khung. Khung một, ba nút thắt: thành phần tập trung, thành phần chậm, và các thành phần gắn chặt với nhau. Khung hai, bốn kỹ thuật gỡ chúng: chia tải, bộ nhớ đệm, xử lý theo sự kiện, chia nhỏ dữ liệu.](../../diagrams/sd-11-016-main.svg)

## Đọc hình

Các mục giữ theo bài nguồn; lời giải thích và phép tính là của người biên soạn.

**Hai cách hiểu "mở rộng được".** Cách một: xử lý được khối lượng lớn hơn mà không mất hiệu năng. Cách hai: xử lý được khối lượng lớn hơn bằng cách lặp lại một chiến lược tiết kiệm chi phí. Cách hai nhắc rằng một hệ thống có thể về kỹ thuật vẫn mở rộng được nhưng về tiền thì không: nếu mỗi lần nhân đôi tải phải nhân hơn đôi chi phí, tới một điểm nào đó việc mở rộng ngừng khả thi.

**Ba nút thắt.**

- **Thành phần tập trung (centralized).** Mọi yêu cầu phải đi qua một chỗ, nên chỗ đó vừa là trần công suất vừa là điểm hỏng duy nhất.
- **Thành phần chậm (high latency).** Những bước làm mất nhiều thời gian giữ tài nguyên lâu, nên cùng tài nguyên phục vụ được ít yêu cầu hơn.
- **Gắn chặt (tight coupling).** Các phần phụ thuộc nhau chặt nên không thể mở rộng riêng từng phần: muốn thêm một phần phải thêm cả những phần khác.

**Ba nguyên tắc.** *Không giữ trạng thái* (yêu cầu tới bản sao nào cũng được), *gắn lỏng* (các phần nói chuyện qua giao diện hẹp) và *xử lý bất đồng bộ* (việc lâu không giữ người gọi chờ).

**Bốn kỹ thuật.** *Chia tải* trải yêu cầu ra nhiều máy để không máy nào thành nút cổ chai. *Bộ nhớ đệm* giữ những thứ được hỏi nhiều ở nơi nhanh. *Xử lý theo sự kiện* đưa việc lâu vào hàng đợi để làm sau. *Chia nhỏ dữ liệu (sharding)* cắt một tập dữ liệu lớn thành nhiều mảnh nhỏ để mở rộng theo chiều ngang.

**Phép tính: một phần tập trung giới hạn lợi ích của việc thêm máy.** Giả sử 5% công việc của mỗi yêu cầu bắt buộc chạy nối tiếp qua một thành phần tập trung, 95% còn lại chia được cho nhiều máy. Theo công thức tăng tốc quen thuộc (định luật Amdahl): tăng tốc = 1 ÷ (0,05 + 0,95 ÷ n). Với n = 10 máy được khoảng 6,9 lần, n = 100 máy khoảng 16,8 lần, n = 1 000 máy khoảng 19,6 lần, và dù thêm vô hạn máy cũng không quá 1 ÷ 0,05 = 20 lần. Thêm máy tới mấy cũng không vượt qua phần tập trung.

## Giới hạn cần nhớ

Công thức ở trên mô hình hóa một tải cố định và giả định phần chia được chia đều không tốn chi phí phối hợp; hệ thống thật có thêm chi phí liên lạc nên lợi ích còn thấp hơn. Công thức là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu gốc. Bài không nêu số liệu thực của một hệ thống nào. Mỗi kỹ thuật cũng có giá: bộ nhớ đệm có thể trả dữ liệu cũ, xử lý bất đồng bộ làm kết quả đến muộn, và chia nhỏ dữ liệu làm truy vấn qua nhiều mảnh khó hơn.

## Nhìn hình trả lời

Trang báo cáo cuối tháng làm máy chủ chậm cả hệ thống, vì mỗi báo cáo chạy 30 giây ngay trong yêu cầu của người dùng. Thuộc nút thắt nào, và kỹ thuật nào hợp nhất?

<details>
<summary>Xem đáp án</summary>

Nút thắt thành phần chậm: việc lâu giữ tài nguyên của yêu cầu. Kỹ thuật hợp nhất là xử lý theo sự kiện: nhận yêu cầu, đưa việc làm báo cáo vào hàng đợi, trả lời ngay "đang xử lý", rồi báo khi xong. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn nêu hai cách hiểu, ba nút thắt, ba nguyên tắc và bốn kỹ thuật. Bài này giữ đủ các mục đó, chia thành hai khung (nút thắt, kỹ thuật) và thêm một phép tính cho thấy vì sao phần tập trung đặt trần cho việc thêm máy.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-crash-course-on-architectural-scalability.md): các mục chính. Lời giải thích và phép tính là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức; phép tính là số học thuần túy theo công thức nêu trong bài.

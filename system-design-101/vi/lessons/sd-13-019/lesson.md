# Bốn nút thắt giữa các nhóm khi đưa phần mềm lên chạy

Khi nhiều nhóm cùng đưa một sản phẩm lên chạy, thời gian thường mất ở các chỗ chuyển giao chứ không ở lúc viết mã. Bài này nêu bốn nút thắt hay gặp, dấu hiệu nhận ra chúng, và việc nhỏ đáng thử trước.

![Bốn nút thắt giữa các nhóm và việc nên thử trước: chờ môi trường và quyền thì làm mẫu môi trường tự phục vụ, phát hành thủ công thì viết các bước thành pipeline, sự cố lặp lại thì đặt SLO và quy tắc khi hết ngân sách lỗi, và hiểu biết dồn vào vài người thì viết runbook và luân phiên trực ca.](../../diagrams/sd-13-019-main.svg)

**Đọc hình:** mỗi thẻ là một nút thắt độc lập; nút nào đang chậm nhất ở tổ chức của bạn nên được xử lý trước.

## Nhìn hình thử trả lời

Nhóm đã dùng hết "ngân sách lỗi" của tháng nhưng còn ba tính năng phải ra. Theo quy tắc đã thỏa thuận từ trước thì nên làm gì?

<details>
<summary>Xem đáp án</summary>

Giảm tốc độ phát hành tính năng mới và ưu tiên việc tăng độ tin cậy, cho tới khi lại nằm trong mục tiêu mức dịch vụ (SLO). Quy tắc này phải được các bên thống nhất trước khi ngân sách cạn, không đặt ra giữa lúc căng thẳng.

</details>

## Giới hạn cần nhớ

Bốn nút thắt này là cách nhìn của bài, không phải danh mục đầy đủ; tổ chức nhỏ có thể chưa cần tách nhóm nền tảng hay đặt SLO chính thức. Các tên gọi như DevOps, SRE hay Platform Engineering thường gắn với những cách xử lý trên nhưng không có ranh giới cứng, và chức danh ở mỗi công ty khác nhau, nên hãy hỏi công việc cụ thể thay vì dựa vào tên.

<details>
<summary>Xem sâu hơn</summary>

- **Đo chỗ chờ trước:** ghi lại thời gian chờ ở từng chuyển giao (cấp môi trường, duyệt, phát hành) trước khi chọn cách giảm; chỗ chậm nhất không phải lúc nào cũng là chỗ gây phiền nhất.
- **Tự phục vụ:** cung cấp "đường đi mẫu" (mẫu kho mã, mẫu pipeline, mẫu hạ tầng) để nhóm sản phẩm dùng mà không cần hiểu hết lớp bên dưới; coi nhóm sản phẩm là khách hàng nội bộ của nhóm làm nền tảng.
- **Tự động hóa phát hành:** tự động các bước lặp lại và giữ thay đổi nhỏ; xem thêm bài về vòng đời một tính năng có cờ và bài về rủi ro khi triển khai.
- **Mục tiêu độ tin cậy:** SLO là mục tiêu đo được về trải nghiệm người dùng (ví dụ tỉ lệ request thành công); ngân sách lỗi là phần sai lệch còn được phép so với SLO.
- **Chia sẻ hiểu biết:** cập nhật runbook sau mỗi sự cố, viết đánh giá sau sự cố tập trung vào hệ thống và quy trình thay vì quy lỗi cho cá nhân, và cho người viết mã cùng tham gia trực để thấy hậu quả của quyết định.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/devops-vs-sre-vs-paltform-engg.md).
- Google: [mục tiêu mức dịch vụ](https://sre.google/sre-book/service-level-objectives/), [chính sách ngân sách lỗi](https://sre.google/workbook/error-budget-policy/), [văn hóa đánh giá sau sự cố](https://sre.google/sre-book/postmortem-culture/).
- Platform Engineering: [định nghĩa](https://platformengineering.org/blog/what-is-platform-engineering).

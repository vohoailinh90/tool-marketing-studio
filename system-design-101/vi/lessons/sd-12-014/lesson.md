# Thiết kế sàn giao dịch chứng khoán

**Sàn giao dịch xử lý lệnh trên một đường chính cực kỳ nhạy về độ trễ.** Những việc không nằm trên đường đó, như báo giá cho người xem hay báo cáo, được tách ra để không làm chậm việc khớp lệnh.

![Bảy thẻ dọc: khách đặt lệnh qua ứng dụng của môi giới; môi giới gửi lệnh tới sàn; cổng khách hàng kiểm tra hợp lệ, giới hạn tần suất và xác thực; quản lý lệnh kiểm tra rủi ro theo quy tắc; kiểm tra vốn của khách (đơn giản hóa: số dư trong ví); động cơ khớp lệnh khớp mua với bán và sinh hai bản ghi khớp; kết quả trả về khách qua các thành phần ngược lại. Chú thích: lệnh và kết quả khớp được đánh số thứ tự để phát lại ra cùng kết quả.](../../diagrams/sd-12-014-main.svg)

## Đọc hình

**Đường chính (từ lệnh tới kết quả).** Khách đặt lệnh trong ứng dụng của **môi giới**, môi giới chuyển tới sàn. Tại sàn, **cổng khách hàng** kiểm tra đầu vào, giới hạn tần suất và xác thực; **quản lý lệnh** kiểm tra rủi ro theo quy tắc của bộ phận rủi ro và, trong thiết kế đơn giản hóa này, kiểm tra vốn của khách qua một ví; lệnh đạt thì vào **động cơ khớp lệnh**.

Động cơ ghép lệnh mua với lệnh bán. Khi khớp, nó sinh **hai bản ghi khớp**, một cho bên mua và một cho bên bán, rồi kết quả đi ngược về khách. Cả lệnh lẫn kết quả được **đánh số thứ tự** để phát lại cùng một chuỗi sẽ cho đúng cùng kết quả.

**Ngoài đường chính** còn luồng dữ liệu thị trường và luồng báo cáo, yêu cầu độ trễ khác nên được tách riêng.

## Giới hạn cần nhớ

Bài mô tả luồng đã đơn giản hóa; sàn thật còn nhiều loại lệnh, phiên giao dịch, quy tắc tạm dừng và giám sát. Ranh giới trách nhiệm cũng đơn giản hóa: trên thực tế hạn mức mua của khách thường do **môi giới** kiểm tra trước khi gửi lệnh, còn sàn áp dụng kiểm soát rủi ro theo thành viên hoặc công ty thanh toán bù trừ. Bài đặt kiểm tra vốn trong quản lý lệnh của sàn chỉ để theo sát luồng nguồn. Đường chính phải nhanh nhưng cũng phải đúng: các kiểm tra rủi ro và vốn, dù do sàn hay do môi giới thực hiện, là bắt buộc trước khi khớp và không thể bỏ để nhanh hơn.

## Nhìn hình trả lời

Vì sao việc gửi báo giá cho người xem không nên đi cùng đường với việc khớp lệnh?

<details>
<summary>Xem đáp án</summary>

Hai việc có yêu cầu độ trễ và tải khác nhau. Nếu chung một đường, nhiều người xem giá có thể làm chậm việc khớp lệnh. Tách ra để mỗi phần được tối ưu riêng.

</details>

<details>
<summary>Xem sâu hơn: sổ lệnh và tính tất định</summary>

- **Sổ lệnh (order book):** hai danh sách, lệnh mua xếp giá cao trước và lệnh bán xếp giá thấp trước. Hai lệnh khớp khi giá mua không thấp hơn giá bán. Quy tắc phổ biến: giá tốt hơn được ưu tiên, cùng giá thì lệnh đến trước khớp trước.
- **Tính tất định:** nếu kết quả khớp chỉ phụ thuộc chuỗi lệnh đã đánh số thì phát lại chuỗi đó cho cùng kết quả. Nhờ vậy máy dự phòng chạy cùng chuỗi lệnh có thể thay thế khi sự cố, và việc kiểm toán dựng lại được lịch sử.
- **Ba luồng:** giao dịch (đường chính), dữ liệu thị trường và báo cáo.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/design-stock-exchange.md): luồng lệnh qua cổng, quản lý lệnh và động cơ khớp lệnh.
- [Wikipedia — Order book](https://en.wikipedia.org/wiki/Order_book): sổ lệnh và quy tắc ưu tiên.
- [Wikipedia — Matching engine](https://en.wikipedia.org/wiki/Matching_engine): động cơ khớp lệnh.
- [Martin Fowler — Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html): lưu chuỗi sự kiện để dựng lại trạng thái.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-014.json).

# Sáu mẫu nhắn tin trên đám mây, và điều mỗi mẫu giải

**Dịch vụ nói chuyện với nhau không chỉ bằng "gọi rồi chờ". Có sáu mẫu quen thuộc, mỗi mẫu giải một nỗi đau cụ thể: việc chạy lâu, người gửi bị chặn, thông điệp quá to, việc gấp, nhất quán dữ liệu, và nhiều người nhận cùng lúc.** Bài này giữ tên sáu mẫu của bài nguồn, nói mỗi mẫu giải gì, và thử vài hành vi nhỏ bằng chương trình thay vì chỉ mô tả.

![Ba khung. Hai khung đầu, mỗi khung ba trong sáu mẫu nhắn tin trên đám mây, mỗi mẫu một thẻ: yêu cầu bất đồng bộ rồi trả lời sau, đăng và đăng ký, thẻ nhận hàng cho thông điệp lớn, hàng đợi ưu tiên, saga, nhiều bên cùng tranh nhau nhận. Khung ba, thử nhỏ: ba người nhận thông điệp có thời gian xử lý khác nhau nên xong không theo thứ tự gửi; hàng đợi ưu tiên không bao giờ phục vụ thông điệp thấp khi tải cao liên tục; saga hỏng ở bước ba thì bù ngược hai bước đã xong.](../../diagrams/sd-11-032-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: giao thức web; mã 202 của nó nghĩa là "đã chấp nhận để xử lý nhưng chưa xong": máy chủ nhận yêu cầu, chưa hứa kết quả.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cổng mà một chương trình mở ra để chương trình khác gọi.

## Đọc hình

**Asynchronous Request-Reply (yêu cầu bất đồng bộ, trả lời sau).** Cho việc chạy lâu ở phía sau. Máy khách gọi API, việc dài được giao cho phía sau, và API trả ngay mã HTTP 202 (Accepted) để báo "đã chấp nhận để xử lý, chưa xong". Mã này không hứa việc đã bắt đầu hay sẽ thành công, nên máy khách cần một cách hỏi lại kết quả. Phía trước và phía sau được tách ra, máy khách không phải giữ kết nối suốt thời gian xử lý.

**Publisher-Subscriber (đăng và đăng ký).** Tách người gửi khỏi người nhận, và không bắt người gửi chờ phản hồi. Người gửi đăng thông điệp lên kênh; những ai đăng ký sẽ nhận.

**Claim Check (thẻ nhận hàng).** Cho thông điệp lớn. Cả nội dung được lưu vào một kho, thông điệp chỉ mang tham chiếu; người nhận dùng tham chiếu lấy nội dung từ kho khi cần.

**Priority Queue (hàng đợi ưu tiên).** Việc có ưu tiên cao được nhận và xử lý sớm hơn việc ưu tiên thấp.

**Saga.** Giữ dữ liệu nhất quán qua nhiều dịch vụ, đặc biệt trong vi dịch vụ nơi mỗi dịch vụ có cơ sở dữ liệu riêng, mà không dùng giao dịch phân tán vốn khó mở rộng và làm hệ thống chậm.

**Competing Consumers (nhiều bên tranh nhau nhận).** Nhiều bên nhận cùng xử lý thông điệp từ một kênh, không cần cấu hình phối hợp phức tạp. Nhưng mẫu này không bảo đảm thứ tự thông điệp.

## Thử: ba hành vi mà tên mẫu không nói

Ngày 2026-10-19, các chương trình Python nhỏ, không có hàng đợi thật.

**Tranh nhau nhận làm đảo thứ tự.** 12 thông điệp đánh số 0 đến 11 vào một hàng, ba bên nhận; mỗi thông điệp tốn từ 1 đến 9 bước. Thứ tự hoàn thành là 0, 1, 3, 2, 5, 6, 8, 7, 4, 9, 11, 10. Thông điệp 4 xong sau 7 và 8, dù được gửi trước. Hệ quả: nếu thứ tự quan trọng (ví dụ cập nhật rồi xóa cùng một mục) thì cần cách khác, như chia theo khóa để cùng khóa luôn vào một bên.

**Hàng đợi ưu tiên có thể bỏ đói việc thấp.** Mỗi bước xử lý 1 việc; việc ưu tiên cao đến 1,34 việc mỗi bước trong 100 bước (134 việc), 10 việc thấp đến ở 10 bước đầu. Sau 100 bước đã xử lý 100 việc cao, 0 việc thấp, và 44 việc còn tồn. Hệ quả: hàng đợi ưu tiên cần thêm thứ gì đó (hạn mức cho việc cao, hay tăng ưu tiên theo thời gian chờ) khi tải cao có thể kéo dài.

**Saga bù theo thứ tự ngược.** Ba bước: đặt chỗ, trừ tiền, giữ hàng. Giữ hàng hỏng. Các bước đã xong được bù theo thứ tự ngược: hoàn tiền rồi hủy chỗ. Mỗi bước phải có sẵn thao tác bù của nó.

**Thẻ nhận hàng nhỏ hơn rất nhiều.** Một khối 5 megabyte so với tham chiếu 60 byte: nhỏ hơn khoảng 87000 lần. (Con số 60 byte là giả định của thử nghiệm; kích thước tham chiếu thật tùy kho.)

## Giới hạn cần nhớ

Ba mô phỏng đều tối giản: thời gian xử lý ngẫu nhiên đều, tải cố định, một saga thẳng không phân nhánh. Không mô phỏng nào thay cho việc đọc tài liệu của một sản phẩm hàng đợi cụ thể, nơi các hành vi trên có thể được xử lý khác (ví dụ hàng đợi có thứ tự theo nhóm hay theo khóa). Bài nguồn chỉ dựa vào bản tóm tắt ngắn; chi tiết từng mẫu chưa được đối chiếu với catalogue mẫu của Microsoft trong phiên viết.

## Nhìn hình trả lời

Một dịch vụ nhận ảnh người dùng tải lên, ảnh tới 8 megabyte, rồi nhiều dịch vụ khác cần xử lý ảnh. Mẫu nào giảm kích thước thông điệp, và nó làm phát sinh thêm trách nhiệm gì?

<details>
<summary>Xem đáp án</summary>

Thẻ nhận hàng (Claim Check): lưu ảnh vào kho đối tượng, gửi tham chiếu. Phát sinh thêm: ai dọn ảnh khi không còn ai cần, và việc người nhận phải có quyền đọc kho. Đây là suy luận của người biên soạn từ mô tả mẫu.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn tóm tắt sáu mẫu mỗi mẫu một vài câu. Bài này giữ sáu mẫu và thứ tự đó, thêm ba mô phỏng nhỏ và một phép so kích thước, và ghi rõ những gì chúng không chứng minh.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-cloud-messaging-patterns.md): sáu mẫu nhắn tin. Mô phỏng và đáp án là của người biên soạn.
- [Microsoft — Cloud design patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/): catalogue chứa các mẫu này (Asynchronous Request-Reply, Publisher/Subscriber, Claim-Check, Priority Queue, Saga, Competing Consumers). Chưa mở lại trong phiên viết; kiến thức chung của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

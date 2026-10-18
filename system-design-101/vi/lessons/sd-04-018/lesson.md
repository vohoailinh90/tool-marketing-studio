# Sáu cách dùng kho đối tượng, và tính năng nào làm cho mỗi cách chạy được

**"Dùng kho đối tượng để lưu trữ dài hạn" hay "để làm hồ dữ liệu" chỉ đúng khi bạn bật đúng tính năng cho việc đó.**
Bài này đặt sáu cách dùng quen thuộc cạnh tính năng gánh chúng, lấy Amazon S3 làm ví dụ, kèm cái giá phải tính trước.

![Ba khung. Khung một, giữ lâu và an toàn: lưu trữ dài hạn nhờ quy tắc vòng đời chuyển đối tượng sang lớp rẻ hơn theo tuổi; sao lưu và phục hồi nhờ versioning giữ mọi phiên bản, xóa chỉ thêm dấu xóa nên lấy lại được; không cho sửa xóa nhờ Object Lock, ghi một lần đọc nhiều lần. Khung hai, kho chung cho nhiều chương trình: ảnh, video, tài liệu lớn tải theo nhiều phần và ghi cả đối tượng một lần; hồ dữ liệu dựa vào việc ghi xong là đọc và liệt kê thấy ngay; dữ liệu từ thiết bị dùng thông báo sự kiện báo có đối tượng mới, giao ít nhất một lần. Khung ba, cái giá: mỗi phiên bản là một đối tượng đầy đủ bị tính đủ tiền; chuyển lớp lưu trữ tốn phí; thông báo có thể đến hai lần.](../../diagrams/sd-04-018-main.svg)

## Từ viết tắt

- **WORM** (Write Once, Read Many) — ghi một lần, đọc nhiều lần: kiểu lưu trữ trong đó dữ liệu đã ghi không sửa hay xóa được trong một thời hạn; S3 Object Lock cài kiểu này.
- **ETL** (Extract, Transform, Load) — trích xuất, biến đổi, nạp: chuỗi bước đọc dữ liệu thô, đổi dạng rồi nạp vào kho phân tích.
- **IA** (Infrequent Access) — truy cập không thường xuyên: phần đuôi trong tên lớp lưu trữ Standard-IA của S3, dành cho dữ liệu ít khi đọc lại.
- **IoT** (Internet of Things) — Internet vạn vật: các thiết bị nhỏ như cảm biến tự nối mạng và gửi dữ liệu; bài nguồn tính đây là một trường hợp dùng kho đối tượng.

## Đọc hình

**Khung 1 · Giữ lâu, giữ an toàn.**

- **Lưu trữ dài hạn.** Hướng dẫn S3 mô tả quy tắc vòng đời: chuyển đối tượng sang lớp lưu trữ khác theo tuổi (ví dụ sang Standard-IA sau 30 ngày, sang Glacier Flexible Retrieval sau một năm) và xóa khi hết hạn.
- **Sao lưu và phục hồi.** Khi bật versioning, ghi đè tạo phiên bản mới, còn xóa chỉ chèn một dấu xóa (delete marker) làm phiên bản hiện hành; phiên bản cũ vẫn lấy lại được. Versioning tắt theo mặc định, phải bật.
- **Không cho sửa, xóa.** S3 Object Lock lưu đối tượng theo kiểu WORM: trong thời hạn giữ, đối tượng không bị ghi đè hay xóa. Hướng dẫn S3 nêu nó để đáp ứng quy định cần lưu trữ WORM, hoặc thêm một lớp bảo vệ. Bật Object Lock thì bucket tự bật versioning, vì khóa áp lên từng phiên bản.

**Khung 2 · Kho chung cho nhiều chương trình.**

- **Ảnh, video, tài liệu.** Đối tượng được ghi trọn mỗi lần: ghi đè là thay cả đối tượng, còn khi đọc thì lấy được riêng một khoảng byte. Tệp lớn thì tải lên theo nhiều phần rồi ghép.
- **Hồ dữ liệu.** Hướng dẫn S3 ghi S3 có nhất quán mạnh kiểu đọc sau ghi: một lệnh ghi đã thành công thì lệnh đọc hay liệt kê bắt đầu sau đó thấy ngay dữ liệu mới, và cập nhật một khóa là nguyên tử (người đọc nhận bản cũ hoặc bản mới, không bao giờ nửa vời). Nhờ vậy các bước ETL nối tiếp nhau đọc được đầu ra của bước trước.
- **Dữ liệu từ thiết bị.** Thông báo sự kiện của S3 báo khi có đối tượng mới để khởi động bước xử lý. Hướng dẫn S3 ghi các thông báo này được thiết kế để giao ít nhất một lần, thường trong vài giây nhưng có khi một phút hay lâu hơn.

## Giới hạn cần nhớ

Mỗi tính năng có giá riêng. Với versioning, mỗi phiên bản là một đối tượng đầy đủ chứ không phải phần khác biệt: ba phiên bản là trả tiền cho ba đối tượng. Chuyển lớp lưu trữ bằng vòng đời cũng tốn phí yêu cầu. Thông báo sự kiện có thể đến hai lần hoặc đến trễ, nên bước xử lý phải chịu được trùng (xem bài về các mức giao tin).

## Nhìn hình trả lời

Một công ty lưu bản sao lưu cơ sở dữ liệu hằng đêm lên kho đối tượng. Một hôm có kẻ lấy được khóa truy cập và xóa sạch các bản sao lưu. Tính năng nào trong khung 1 lẽ ra giữ được dữ liệu, và vì sao versioning một mình chưa đủ?

<details>
<summary>Xem đáp án</summary>

Object Lock ở chế độ compliance: trong thời hạn giữ, không người dùng nào xóa hay ghi đè được phiên bản đã khóa, kể cả tài khoản gốc. Chế độ governance yếu hơn: người có quyền vượt khóa vẫn xóa được, nên nếu khóa truy cập bị lộ có quyền đó thì bản sao lưu vẫn mất.
Versioning giúp lấy lại khi lệnh xóa thường chỉ chèn dấu xóa, nhưng lệnh xóa kèm mã phiên bản thì xóa hẳn phiên bản đó; nó chống được xóa nhầm, chưa chống được người cố ý xóa.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn nêu sáu trường hợp: lưu trữ dài hạn, dữ liệu phi cấu trúc, ứng dụng cloud-native, hồ dữ liệu, IoT, sao lưu và phục hồi. Bài này gom chúng thành hai nhóm theo việc kho đối tượng làm (giữ lâu và an toàn, làm kho chung) và gắn mỗi trường hợp với tính năng của S3 làm nó chạy được; "ứng dụng cloud-native" được nhập vào hồ dữ liệu và kho chung, còn chỗ trống được dùng cho Object Lock.
Đáp án câu hỏi về Object Lock và versioning là suy luận của người biên soạn từ mô tả trong hướng dẫn S3, chưa thử trên S3 thật. Mọi chi tiết lấy từ hướng dẫn S3 bản 2023; tính năng và giá có thể đã đổi.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/explain-the-top-6-use-cases-of-object-stores.md): sáu trường hợp dùng kho đối tượng.
- Amazon S3 User Guide, bản 2023, đọc từ bản clone của kho: [quản lý vòng đời](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/object-lifecycle-mgmt.md), [versioning](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/Versioning.md), [xóa phiên bản](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/DeletingObjectVersions.md), [Object Lock](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/object-lock.md) và [hai chế độ của nó](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/object-lock-overview.md), [mô hình nhất quán](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/Welcome.md), [thông báo sự kiện](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/EventNotifications.md), [tải nhiều phần](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/mpuoverview.md), [đọc một khoảng byte](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/download-objects.md).

Đã đọc nguồn ngày 2026-10-18. Bài không có thử nghiệm riêng: kho đối tượng thật không dùng được từ môi trường biên soạn.
Bài viết và hình được thiết kế độc lập.

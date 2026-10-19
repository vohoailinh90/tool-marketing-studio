# Netflix dùng sáu loại cơ sở dữ liệu, mỗi loại một việc

**Theo bài nguồn, Netflix không chọn một cơ sở dữ liệu cho tất cả, mà chọn theo loại dữ liệu: quan hệ cho tiền, cột cho phân tích, khóa–giá trị cho bộ đệm, cột rộng cho hầu hết dữ liệu, chuỗi thời gian cho số đo, và kho đối tượng cho tệp.**
Bài này xếp sáu loại theo câu hỏi mà mỗi loại trả lời tốt, để người mới thấy vì sao một công ty lớn dùng nhiều cơ sở dữ liệu cùng lúc.

![Hai khung thẻ và một khung ghi nhớ. Khung một, dữ liệu nghiệp vụ: cơ sở dữ liệu quan hệ MySQL cho thanh toán, gói đăng ký, thuế và doanh thu, CockroachDB cho kiến trúc nhiều vùng cùng hoạt động; cột rộng Cassandra cho gần như mọi thứ như thông tin phim, người dùng, thiết bị, lịch sử xem; khóa–giá trị EVCache dựng trên Memcached làm bộ đệm. Khung hai, phân tích và tệp: cơ sở dữ liệu cột Redshift và Druid cho phân tích; chuỗi thời gian Atlas cho số đo; kho đối tượng S3 cho ảnh, video, số đo và nhật ký, cùng Apache Iceberg. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-015-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: cách hỏi và sửa dữ liệu trong cơ sở dữ liệu dạng bảng; chữ SQL nằm trong tên MySQL.

## Đọc hình

**Dữ liệu nghiệp vụ.**
- Quan hệ: MySQL cho giao dịch thanh toán, gói đăng ký, thuế và doanh thu. CockroachDB cho kiến trúc nhiều vùng cùng hoạt động (active-active), giao dịch toàn cầu và quy trình đường ống dữ liệu.
- Cột rộng (wide-column): Cassandra thường là lựa chọn mặc định, dùng cho gần như mọi thứ: thông tin phim và diễn viên, dữ liệu người dùng, thông tin thiết bị, lịch sử xem.
- Khóa–giá trị: chủ yếu EVCache, dựng trên Memcached. EVCache đã ở Netflix hơn 10 năm, dùng cho hầu hết dịch vụ, đệm các dữ liệu như trang chủ và gợi ý cá nhân.

**Phân tích, số đo và tệp.**
- Cột (columnar): chủ yếu cho phân tích. Redshift và Druid lưu dữ liệu có cấu trúc; Spark và đường ống dữ liệu để xử lý; Tableau để vẽ biểu đồ.
- Chuỗi thời gian: Netflix làm Atlas, một cơ sở dữ liệu trong bộ nhớ mã nguồn mở, để lưu và gộp số đo.
- Dữ liệu phi cấu trúc: S3 là lựa chọn mặc định, chứa gần như mọi thứ liên quan tới ảnh, video, số đo và tệp nhật ký. Apache Iceberg cũng được dùng cùng S3 cho dữ liệu lớn.

## Giới hạn cần nhớ

Bài nguồn chỉ liệt kê loại và tên, không nói năm, không nói quy mô, cũng không nói dữ liệu đi từ cơ sở dữ liệu này sang cái khác thế nào. Spark và Tableau được nêu cùng nhóm cột nhưng là công cụ xử lý và vẽ biểu đồ, không phải cơ sở dữ liệu. Câu hỏi "mỗi loại trả lời tốt câu gì" ở dưới là của người biên soạn.

## Nhìn hình thử trả lời

Bạn cần lưu số tiền mỗi khách trả hằng tháng, và tuyệt đối không được ghi sai hay ghi đôi. Theo hình, Netflix đặt loại dữ liệu này ở đâu?

<details>
<summary>Xem đáp án</summary>

Ở cơ sở dữ liệu quan hệ MySQL, nơi bài nguồn nói Netflix để giao dịch thanh toán, gói đăng ký, thuế và doanh thu. Cơ sở dữ liệu quan hệ có giao dịch (transaction), giúp một lần ghi tiền hoặc thành công trọn vẹn hoặc không xảy ra.

</details>

<details>
<summary>Xem sâu hơn: mỗi loại trả lời tốt câu hỏi gì</summary>

- Quan hệ: "ghi số tiền này cho đúng, một lần".
- Cột rộng: "ghi rất nhiều, đọc theo khóa, ở nhiều máy".
- Khóa–giá trị trong bộ nhớ: "trả lời thật nhanh khi đã biết khóa".
- Cột: "cộng, đếm trên hàng triệu dòng".
- Chuỗi thời gian: "số đo này thay đổi thế nào theo phút".
- Kho đối tượng: "giữ tệp lớn, rẻ, lâu dài".

Đây là gợi ý chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/netflix-tech-stack-databases.md): sáu loại cơ sở dữ liệu Netflix dùng và việc của từng loại.

Đã đọc nguồn ngày 2026-10-19. Tài liệu kỹ thuật của Netflix chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

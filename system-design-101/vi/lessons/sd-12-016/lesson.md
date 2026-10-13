# Điều gì xảy ra khi tải tệp lên kho đối tượng kiểu S3?

**Kho đối tượng lưu tệp không như ổ đĩa có thư mục.** Mỗi tệp là một “đối tượng” nằm trong một “thùng”; nội dung và thông tin mô tả được lưu ở hai nơi khác nhau.

![Sáu thẻ dọc: client tạo thùng bằng yêu cầu HTTP PUT tới dịch vụ API; dịch vụ API hỏi dịch vụ định danh và quyền xem có quyền ghi không; dịch vụ lưu mục thùng vào kho siêu dữ liệu; client gửi PUT tạo đối tượng; dữ liệu của đối tượng được lưu ở kho dữ liệu và trả về một mã đối tượng; dịch vụ API ghi vào kho siêu dữ liệu mã đối tượng, thùng chứa và tên. Chú thích: dữ liệu nằm ở một nơi, thông tin mô tả nằm ở nơi khác.](../../diagrams/sd-12-016-main.svg)

## Đọc hình

**Thuật ngữ.** **Thùng** (bucket) là vật chứa có tên duy nhất, tạo trước khi tải lên. **Đối tượng** (object) gồm **dữ liệu** (dãy byte bất kỳ) và **siêu dữ liệu** (các cặp tên–giá trị mô tả nó). Thùng chỉ có siêu dữ liệu.

**Tạo thùng (1–3).** Client gửi PUT tới dịch vụ API. API hỏi dịch vụ định danh và phân quyền (IAM) xem người dùng có quyền ghi không, rồi tạo mục thùng trong kho siêu dữ liệu và báo thành công.

**Tải tệp lên (4–6).** Client gửi PUT tạo đối tượng. API kiểm tra quyền như trước rồi đẩy dữ liệu sang **kho dữ liệu**, nơi lưu và trả về một mã duy nhất. Cuối cùng API ghi vào kho siêu dữ liệu một mục gồm mã đối tượng, thùng chứa và tên đối tượng.

## Giới hạn cần nhớ

Đây là mô hình thiết kế một hệ lưu trữ đối tượng kiểu S3, không phải mô tả cách S3 thật vận hành bên trong. Dữ liệu và siêu dữ liệu nằm ở hai nơi nên phải quyết định điều gì xảy ra nếu một nơi ghi xong còn nơi kia lỗi: nếu dữ liệu đã ghi mà chưa có mục siêu dữ liệu thì tệp chưa thể được tìm thấy, và dữ liệu mồ côi cần được dọn.

## Nhìn hình trả lời

Dữ liệu đã ghi vào kho dữ liệu nhưng bước ghi siêu dữ liệu bị lỗi. Người dùng có tải được tệp không? Vì sao?

<details>
<summary>Xem đáp án</summary>

Không: tên đối tượng chỉ được tra ra nhờ mục siêu dữ liệu, nên chưa có mục thì chưa tìm thấy tệp. Dữ liệu đã ghi trở thành dữ liệu mồ côi và cần được dọn hoặc ghi lại.

</details>

<details>
<summary>Xem sâu hơn: đối tượng không sửa tại chỗ, tải lên nhiều phần</summary>

- **Dữ liệu đối tượng không được sửa tại chỗ:** đổi nội dung nghĩa là ghi một đối tượng mới thay cho đối tượng cũ. Siêu dữ liệu thì cập nhật được.
- **Tải lên nhiều phần:** tệp lớn thường được cắt thành các phần gửi song song và ghép lại, để khi lỗi chỉ gửi lại phần hỏng.
- **Tính nhất quán:** sau khi ghi thành công, đọc lại phải thấy đúng dữ liệu mới là yêu cầu mà người dùng thường kỳ vọng; mỗi hệ thống tự nêu cam kết của mình.
- **Tên thùng duy nhất** trong toàn dịch vụ để địa chỉ truy cập không trùng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-happens-when-you-upload-a-file-to-amazon-s3.md): thùng, đối tượng và các bước tạo thùng rồi tải tệp lên.
- [AWS — Amazon S3 giới thiệu](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html): thùng, đối tượng và mô hình nhất quán.
- [AWS — Tải lên nhiều phần](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html): cắt tệp lớn thành các phần.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-016.json).

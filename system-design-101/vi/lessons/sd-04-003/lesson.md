# Tải tệp lớn lên S3: chia phần, chọn cỡ phần, dọn phần bỏ dở

**Gửi một tệp vài chục GiB lên S3 (dịch vụ lưu trữ đối tượng của Amazon) trong một lệnh thì đứt mạng giữa chừng là phải gửi lại từ đầu.**
Tải nhiều phần (multipart upload) cắt tệp thành các phần gửi riêng: phần nào hỏng thì gửi lại phần đó, các phần có thể đi song song, và kho chỉ ghép thành một đối tượng khi được báo hoàn tất.

![Ba khung. Khung một là trình tự giữa máy khách và kho đối tượng: máy khách xin bắt đầu một lượt tải nhiều phần và nhận upload ID; gửi từng phần, có thể song song, kèm số phần và upload ID, mỗi phần nhận về một ETag; cuối cùng gửi lệnh hoàn tất kèm danh sách số phần và ETag, kho ghép các phần theo số phần. Khung hai là cách chọn cỡ phần: mỗi phần ít nhất 5 MiB trừ phần cuối và tối đa 10.000 phần; tệp 100 GiB với phần 5 MiB cần 20.480 phần nên phải dùng phần từ 10,24 MiB trở lên. Khung ba: lượt tải bỏ dở vẫn bị tính tiền lưu trữ cho tới khi hủy, và ETag của đối tượng tải nhiều phần không phải MD5 của cả tệp.](../../diagrams/sd-04-003-main.svg)

## Từ viết tắt

- **ID** (IDentifier) — mã định danh: ở đây là upload ID, mã của một lượt tải nhiều phần mà mọi lệnh gửi phần, hoàn tất hay hủy đều phải mang theo.
- **ETag** (Entity Tag) — thẻ thực thể: mã kho trả về sau mỗi phần (và sau cả đối tượng) để nhận diện đúng nội dung đã nhận.
- **MD** (Message Digest) — tóm lược thông điệp: MD5 là một hàm băm cho ra chuỗi 128 bit từ dữ liệu bất kỳ; S3 dùng nó để tính ETag và kiểm dữ liệu không bị hỏng trên đường truyền.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: tập lệnh mà chương trình gọi để làm việc với S3, như lệnh bắt đầu, gửi phần và hoàn tất.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng cỡ một triệu byte; tài liệu API của S3 ghi giới hạn cỡ phần bằng đơn vị này.
- **MiB** (Mebibyte) — mebibyte: đơn vị dung lượng bằng 1.048.576 byte (2 mũ 20).
- **GiB** (Gibibyte) — gibibyte: đơn vị dung lượng bằng 1.024 MiB.

## Đọc hình

**Khung 1 · Ba bước.** Bắt đầu một lượt tải để nhận upload ID; gửi từng phần kèm số phần (từ 1 tới 10.000) và giữ lại ETag kho trả về cho mỗi phần; gửi lệnh hoàn tất kèm danh sách số phần và ETag.
Các phần gửi theo thứ tự nào cũng được; gửi lại một số phần đã có thì phần mới đè lên phần cũ. Hướng dẫn S3 cho phép số phần không liên tiếp, trừ khi lượt tải dùng checksum bổ sung: khi đó số phần phải liên tiếp, không thì lệnh hoàn tất báo lỗi. Đánh số 1, 2, 3… cho mọi lượt tải là cách an toàn.
Khi hoàn tất, S3 nối các phần theo số phần tăng dần, và các phần riêng lẻ không còn nữa. Hướng dẫn S3 dặn tự ghi lại số phần và ETag thay vì dựa vào lệnh liệt kê phần để lập danh sách hoàn tất.

**Khung 2 · Cỡ phần.** Lệnh hoàn tất bị từ chối với lỗi `EntityTooSmall` nếu một phần không phải phần cuối nhỏ hơn 5 MB.
Giới hạn 10.000 phần mới là thứ buộc người ta chọn cỡ phần: tệp 100 GiB cắt phần 5 MiB ra 20.480 phần, nên phần phải từ 10,24 MiB trở lên. Hướng dẫn S3 bản 2023 cũng ghi một phần lớn nhất 5 GiB.

**Khung 3 · Hai điều hay quên.** Mục “Giới hạn cần nhớ” nói kỹ hơn.

## Thử nghiệm: tính ETag như S3 mô tả

Hướng dẫn S3 mô tả ETag của đối tượng tải nhiều phần: lấy MD5 của từng phần, nối các giá trị đó lại, lấy MD5 của chuỗi nối, rồi thêm dấu gạch và số phần.
Làm theo đúng mô tả ấy trên máy (không gọi S3) với một tệp ngẫu nhiên 21 MiB, phần 5 MiB:

| Thứ được tính | Kết quả |
|---|---|
| Các phần | 5, 5, 5, 5 và 1 MiB |
| ETag của đối tượng | `4f79d0f27854976ba9c74084e2ea3aee-5` |
| MD5 của cả tệp | `9cd7fe8ee2fb0c02de53bc4f59b9c0e4` |

Hai giá trị khác nhau: muốn kiểm tệp tải về đúng thì không so ETag với MD5 của cả tệp. Cắt cùng tệp theo cỡ phần khác cũng ra ETag khác, vì giá trị phụ thuộc vào cách chia.
Cách tính này là của bucket thường (general purpose) trong hướng dẫn S3 bản 2023. Với directory bucket, một loại bucket khác của S3, tài liệu API trong botocore (bản 2026) ghi ETag không phải MD5 của đối tượng và MD5 không được hỗ trợ, nên đừng viết công cụ kiểm tra dựa vào công thức trên; dùng các checksum mà S3 trả về thay vào đó.

## Giới hạn cần nhớ

- **Phần bỏ dở vẫn tốn tiền.** Một lượt tải đã bắt đầu không tự hết hạn; S3 giữ và tính tiền lưu các phần đã gửi cho tới khi lượt tải được hoàn tất hoặc hủy. Hướng dẫn S3 khuyên đặt quy tắc vòng đời `AbortIncompleteMultipartUpload` để tự hủy những lượt tải chưa xong sau một số ngày.
- **ETag không phải MD5 của tệp.** Với đối tượng tải nhiều phần, ETag không bao giờ là MD5 của cả dữ liệu, dù mã hóa kiểu gì. Muốn kiểm toàn vẹn, dùng các thuật toán checksum bổ sung mà S3 hỗ trợ; `Content-MD5` cho từng phần chỉ dùng được với bucket thường, không với directory bucket.

## Nhìn hình trả lời

Ứng dụng tải video lên S3 bằng nhiều phần. Mạng rớt sau khi phần 37 trên 60 đã gửi xong. Lúc mạng có lại, ứng dụng cần những gì để đi tiếp mà không gửi lại từ đầu?

<details>
<summary>Xem đáp án</summary>

Cần upload ID của lượt tải đang dở, và danh sách số phần cùng ETag đã nhận cho 37 phần đầu. Ứng dụng gửi tiếp phần 38 tới 60 với cùng upload ID, rồi gửi lệnh hoàn tất kèm đủ 60 cặp số phần và ETag.
Nếu ứng dụng bỏ cuộc thay vì đi tiếp, nó nên hủy lượt tải; không thì 37 phần đã gửi vẫn bị tính tiền lưu trữ tới khi quy tắc vòng đời (nếu có) dọn chúng.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn nói ETag của một phần "về cơ bản là MD5 của phần đó". Hướng dẫn S3 nói rõ hơn: ETag có là MD5 hay không còn tùy cách mã hóa phía máy chủ, và ETag của cả đối tượng tải nhiều phần thì không phải MD5 của dữ liệu.
Bài này cũng thêm giới hạn 10.000 phần (thứ quyết định cỡ phần) và việc dọn lượt tải bỏ dở, hai chỗ bài nguồn không nhắc.

Hướng dẫn S3 dùng làm nguồn là bản 2023, lần cuối trước khi Amazon gỡ nội dung khỏi kho trên GitHub; tài liệu tham chiếu API trong botocore (bản 2026) vẫn ghi phần tối thiểu 5 MB và số phần từ 1 tới 10.000. Giới hạn của dịch vụ có thể đổi, nên kiểm lại tài liệu hiện hành trước khi dựa vào con số.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-upload-a-large-file-to-s3.md): sáu bước của tải nhiều phần, ví dụ tệp 1,6 GB chia 8 phần.
- [Amazon S3 User Guide — Uploading and copying objects using multipart upload, bản 2023](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/mpuoverview.md): ba bước, số phần 1 tới 10.000, phần gửi lại đè phần cũ, tự ghi ETag, tiền lưu trữ cho tới khi hoàn tất hoặc hủy. Đọc từ bản clone của kho tại commit trước khi nội dung bị gỡ.
- [Amazon S3 User Guide — multipart upload limits, bản 2023](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/qfacts.md): phần từ 5 MiB tới 5 GiB, phần cuối không có cỡ tối thiểu, tối đa 10.000 phần.
- [Amazon S3 User Guide — Checking object integrity, bản 2023](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/checking-object-integrity.md): khi nào ETag là MD5, cách tính ETag của đối tượng tải nhiều phần.
- [Amazon S3 User Guide — xóa lượt tải chưa xong bằng vòng đời, bản 2023](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/mpu-abort-incomplete-mpu-lifecycle-config.md): quy tắc `AbortIncompleteMultipartUpload`.
- [botocore — mô tả API của S3, tại commit cố định](https://github.com/boto/botocore/blob/4de93abe62cc263980414f7a66be5226bd541b77/botocore/data/s3/2006-03-01/service-2.json): lỗi `EntityTooSmall` (mỗi phần ít nhất 5 MB trừ phần cuối), phải hoàn tất hoặc hủy để thôi bị tính tiền các phần, ETag của đối tượng trong directory bucket không phải MD5 và MD5 không được hỗ trợ ở đó. Đọc từ bản clone của kho.

Đã đọc nguồn và chạy phép tính ngày 2026-10-18; phép tính ETag chạy trên máy theo mô tả của tài liệu, không gửi gì lên S3.
Bài viết và hình được thiết kế độc lập.

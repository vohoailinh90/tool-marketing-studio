# Lưu trữ khối, tệp và đối tượng: khác nhau ở thứ chương trình nhìn thấy

**Ba kiểu lưu trữ có thể nằm trên cùng loại ổ đĩa; khác nhau là chương trình được đưa cho cái gì để đọc ghi.**
Với lưu trữ khối, chương trình thấy một dãy khối đánh số. Với lưu trữ tệp, nó thấy tên và thư mục. Với lưu trữ đối tượng, nó thấy từng đối tượng có khóa, đọc ghi trọn qua một giao diện lập trình.

![Ba khung. Khung một là ba thẻ: lưu trữ khối là một dãy khối đánh số, máy chủ đọc ghi khối 2066 mà không biết đó là tệp gì; lưu trữ tệp ghép tên và thư mục với các khối, tệp /docs/note.txt là inode 13 nằm ở khối 2066; lưu trữ đối tượng là không gian phẳng, khóa photos/2017/a.jpg chỉ là một cái tên, thư mục chỉ là tiền tố, đọc ghi qua API. Khung hai là bốn bước thử: tạo một đĩa ảo 64 MiB định dạng ext4 với khối 4 KiB; ghi tệp /docs/note.txt dài 28 byte; hệ tệp cho biết tệp là inode 13, dữ liệu ở khối 2066; đọc thẳng khối 2066 ra đúng nội dung mà không cần tên. Khung ba: Ceph cho cả ba giao diện trên cùng một cụm: thiết bị khối, hệ tệp và kho đối tượng tương thích S3.](../../diagrams/sd-04-017-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: tập lệnh mà chương trình gọi qua mạng để đọc ghi đối tượng, như lệnh đặt và lấy một đối tượng theo khóa.
- **MiB** (Mebibyte) — mebibyte: đơn vị dung lượng bằng 1.048.576 byte; đĩa ảo trong thử nghiệm có cỡ 64 MiB.
- **KiB** (Kibibyte) — kibibyte: đơn vị dung lượng bằng 1.024 byte; mỗi khối của đĩa ảo là 4 KiB.

## Đọc hình

**Khối.** Ổ đĩa (hay một ổ đĩa mạng) chỉ biết "đọc khối số n, ghi khối số n". Ai dùng nó phải tự biết khối nào chứa gì: một hệ tệp, hoặc một cơ sở dữ liệu tự quản khối.

**Tệp.** Hệ tệp dựng trên các khối: nó giữ bảng ghép tên, thư mục với inode, và inode với danh sách khối chứa dữ liệu. Nhờ vậy nhiều chương trình dùng chung được bằng tên, kể cả qua mạng.

**Đối tượng.** Hướng dẫn Amazon S3 viết rằng mô hình dữ liệu của S3 là một cấu trúc phẳng: bucket chứa đối tượng, không có bucket con hay thư mục con. "Thư mục" trên bảng điều khiển chỉ là tiền tố của khóa: đối tượng `photos/2017/example.jpg` hiện ra như thư mục `photos` chứa thư mục `2017`.

## Thử nghiệm: một tệp nằm ở khối nào

Không cần quyền quản trị hay gắn đĩa: tạo một tệp 64 MiB, định dạng ext4 với khối 4 KiB bằng `mkfs.ext4`, rồi dùng `debugfs` để ghi và hỏi hệ tệp.

| Bước | Kết quả |
|---|---|
| Ghi tệp `/docs/note.txt` (28 byte) vào đĩa ảo | hệ tệp cấp inode 13 |
| `debugfs -R "stat /docs/note.txt"` | dữ liệu nằm ở một đoạn bắt đầu tại khối 2066 |
| Đọc thẳng khối 2066 của tệp đĩa bằng `dd`, không qua hệ tệp | ra đúng 28 byte nội dung của tệp |

Bước cuối là góc nhìn của lưu trữ khối: cùng những byte đó, nhưng chỉ có số khối, không có tên. Tên `/docs/note.txt` chỉ tồn tại trong cấu trúc của hệ tệp.

Ceph cho thấy ba kiểu là ba *giao diện*: trên cùng một cụm lưu trữ, nó cung cấp thiết bị khối (có thể chụp ảnh và nhân bản, khối được chia ra khắp cụm), hệ tệp gắn được bằng `mount`, và kho đối tượng với giao diện tương thích Amazon S3.

## Giới hạn cần nhớ

Chọn kiểu nào là chọn những thao tác có sẵn. Thiết bị khối thường chỉ một máy gắn vào dùng; bài nguồn nói nó thuộc trọn một máy chủ, không phải tài nguyên dùng chung. Hệ tệp cho nhiều máy dùng chung tên và thư mục. Kho đối tượng không có thư mục thật, nên "đổi tên một thư mục" nghĩa là chép rồi xóa từng đối tượng mang tiền tố đó; hướng dẫn S3 ghi rõ thư mục trên bảng điều khiển không đổi tên được.

## Nhìn hình trả lời

Một cơ sở dữ liệu cần ghi đè vài khối 8 KiB ở giữa một tệp dữ liệu lớn hàng nghìn lần mỗi giây. Đặt tệp đó trên kho đối tượng có ổn không?

<details>
<summary>Xem đáp án</summary>

Không. Kho đối tượng đọc ghi theo từng đối tượng qua giao diện lập trình; sửa vài khối ở giữa nghĩa là phải ghi lại cả đối tượng. Cơ sở dữ liệu cần ghi đè khối tại chỗ, nên nó hợp với lưu trữ khối (hoặc một hệ tệp trên lưu trữ khối).
Kho đối tượng hợp với bản sao lưu của cơ sở dữ liệu đó: tệp lớn, ghi một lần, đọc lại khi cần.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn kể ví dụ kho đối tượng gồm S3 của Amazon, "Google block storage" và Azure blob storage; dịch vụ đối tượng của Google là Google Cloud Storage, không phải lưu trữ khối. Bài nguồn cũng nói kho đối tượng "chủ yếu cho lưu trữ và sao lưu" dữ liệu lạnh; bài này không lặp lại vì các trường hợp dùng kho đối tượng rộng hơn thế.
Thử nghiệm dùng một tệp làm đĩa ảo nên không đo tốc độ; thứ nó chứng minh là cách hệ tệp ghép tên với khối.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/storage-systems-overview.md): ba loại lưu trữ khối, tệp, đối tượng.
- [Amazon S3 User Guide — Creating object key names, bản 2023](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/object-keys.md): mô hình dữ liệu phẳng, phân cấp suy ra từ tiền tố và dấu phân cách. Đọc từ bản clone của kho.
- [Amazon S3 User Guide — Organizing objects using folders, bản 2023](https://github.com/awsdocs/amazon-s3-userguide/blob/cc53dd6a44d3aa1d654e6d3705a0a7550f20fd2a/doc_source/using-folders.md): thư mục là tiền tố của khóa, không đổi tên được.
- [Ceph — Ceph Clients, tại commit cố định](https://github.com/ceph/ceph/blob/c0b32d47115c516baef9eb0111b4dc1c21c91ff4/doc/architecture/ceph-clients.rst): thiết bị khối, kho đối tượng tương thích S3, hệ tệp trên cùng một cụm. Đọc từ bản clone của kho.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 với e2fsprogs 1.47.0 (`mkfs.ext4`, `debugfs`) trên một tệp đĩa ảo.
Bài viết và hình được thiết kế độc lập.

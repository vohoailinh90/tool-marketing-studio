# Cây thư mục Linux và vai trò từng nơi

Trên Linux, đường dẫn tuyệt đối bắt đầu từ `/`. Các filesystem có thể được mount vào vị trí trong cùng cây đường dẫn. Bạn đọc cây theo vai trò thư mục để biết cấu hình, dữ liệu thay đổi và dữ liệu người dùng thường ở đâu.

![Gốc cây: /; Cấu hình hệ thống: /etc; Dữ liệu biến đổi: /var · ví dụ log; Người dùng và phần mềm: /home · /usr.](../../diagrams/sd-09-017-main.svg)

**Đọc hình:** Các thẻ là các bước hoặc góc nhìn của ví dụ; đọc từ trên xuống. Mũi tên chỉ thứ tự đọc, không biểu diễn luồng mạng hoặc sự phụ thuộc bắt buộc.

`/etc` thường giữ cấu hình riêng của máy. `/var` chứa dữ liệu thay đổi trong quá trình vận hành, chẳng hạn log trong `/var/log`. `/home` thường chứa thư mục người dùng; `/usr` giữ phần lớn chương trình và dữ liệu dùng chung của hệ thống, không phải home của từng user.

`/tmp` dành cho dữ liệu tạm, không nên dùng làm nơi duy nhất giữ dữ liệu cần lâu dài. `/dev` chứa node thiết bị. `/proc` và `/sys` thường là các filesystem ảo để quan sát trạng thái và giao tiếp với kernel. Chúng không đơn giản là các thư mục file thường lưu trên cùng một ổ đĩa.

## Nhìn hình thử trả lời

Một file cấu hình của dịch vụ thường tìm ở /etc hay /home chỉ vì tên usr giống user?

<details>
<summary>Xem đáp án</summary>

Thường tìm ở /etc theo quy ước hệ thống. /usr không phải thư mục home của user.

</details>

## Giới hạn cần nhớ

FHS là quy ước phổ biến, không bảo đảm mọi distro/container có bố cục giống nhau. Nhiều hệ thống dùng merged-/usr, với /bin là liên kết tới /usr/bin.

<details>
<summary>Xem sâu hơn</summary>

Dùng `pwd`, `ls` và `findmnt` để quan sát trước khi sửa. Tên đường dẫn không cho biết thiết bị vật lý: một mount mới có thể đưa filesystem khác vào một nhánh của cây.

</details>

## Nguồn đối chiếu

- [Chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/linux-file-system-explained.md). Bài viết và hình này được thiết kế độc lập; không dịch thân bài hoặc sử dụng ảnh nguồn.
- [Filesystem Hierarchy Standard 3.0](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html).
- [hier](https://man7.org/linux/man-pages/man7/hier.7.html).
- [proc](https://man7.org/linux/man-pages/man5/proc.5.html).

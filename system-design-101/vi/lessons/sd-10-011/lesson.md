# Big endian và little endian: thứ tự byte trong bộ nhớ

**Một số nguyên nhiều byte có thể nằm trong bộ nhớ theo hai thứ tự: byte nhỏ nhất trước (little endian) hoặc byte lớn nhất trước (big endian).**
Hai kiểu này không sai hay đúng; chúng chỉ gây rắc rối khi dữ liệu đi giữa hai hệ thống dùng kiểu khác nhau.

![Bốn nhóm xếp dọc. Big endian với số 1023 hay 0x3ff: byte lớn nhất 03 nằm ở địa chỉ thấp nhất, byte nhỏ nhất ff ở địa chỉ kế tiếp. Little endian với số 1023: byte nhỏ nhất ff nằm ở địa chỉ thấp nhất, byte lớn nhất 03 ở địa chỉ kế tiếp. Dùng ở đâu: little endian ở bộ xử lý Intel x86; big endian ở PowerPC và Motorola 68k đời cũ, trong truyền thông mạng và lưu tệp. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-011-main.svg)

## Đọc hình

**Ví dụ: số 1023.** Số 1023 viết thập lục phân là `0x3ff`, nên cần hai byte: byte lớn nhất là `03`, byte nhỏ nhất là `ff`. Big endian ghi `03 ff`, nghĩa là byte lớn nhất ở địa chỉ thấp nhất. Little endian ghi `ff 03`, nghĩa là byte nhỏ nhất ở địa chỉ thấp nhất. Ví dụ này lấy từ tài liệu mô-đun `struct` của Python.

**Little endian.** Bộ xử lý Intel x86 lưu số nguyên hai byte với byte nhỏ nhất (least significant byte) trước, rồi tới byte lớn nhất (most significant byte). Đó là thứ tự little endian.

**Big endian.** Với thứ tự big endian, byte lớn nhất nằm ở địa chỉ bộ nhớ thấp nhất và byte nhỏ nhất ở địa chỉ cao nhất. Các kiến trúc PowerPC và Motorola 68k đời cũ thường dùng big endian. Trong truyền thông mạng và lưu tệp, big endian cũng được dùng.

**Vì sao quan trọng.** Thứ tự byte trở nên quan trọng khi dữ liệu được chuyển giữa các hệ thống, hoặc được xử lý bởi các hệ thống có thứ tự khác nhau. Cần xử lý đúng thứ tự byte để đọc dữ liệu nhất quán.

## Giới hạn cần nhớ

Thứ tự byte nói về cách xếp **byte** của một số trong bộ nhớ, không phải về thứ tự các bit trong một byte.
Nguồn nêu Intel x86 cho little endian, PowerPC và Motorola 68k đời cũ cho big endian, và nói mạng dùng big endian; bài không nói máy nào "nhanh hơn". Tài liệu `struct` của Python ghi thêm rằng thứ tự gốc của máy phụ thuộc máy, và dùng `sys.byteorder` để biết máy mình dùng kiểu nào.

## Nhìn hình trả lời

Một chương trình trên máy little endian ghi số 1023 thành hai byte rồi gửi nguyên hai byte đó cho một máy big endian. Máy nhận đọc hai byte theo thứ tự của chính nó. Chuyện gì xảy ra?

<details>
<summary>Xem đáp án</summary>

Máy little endian gửi `ff 03`. Máy big endian coi byte đầu tiên là byte lớn nhất nên đọc thành `0xff03`, tức 65283 nếu hiểu là số nguyên không dấu hai byte (phép tính của người biên soạn), thay vì 1023.
Vì thế cần thống nhất thứ tự khi truyền dữ liệu, và mạng dùng big endian làm thứ tự chung.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và ba phần ngắn: little endian, big endian, vì sao quan trọng. Bài này không dùng ảnh; ví dụ 1023 lấy từ tài liệu Python thay cho một ví dụ tự nghĩ ra, và có thêm câu hỏi kiểm tra.
Việc `struct` coi thứ tự mạng là big endian, và nêu Intel x86 là little endian còn nhiều kiến trúc cũ là big endian, đã được đối chiếu với tài liệu Python tại commit cố định ở mục nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/big-endian-vs-little-endian.md): hai thứ tự byte, nơi dùng, vì sao quan trọng.
- [Python — tài liệu mô-đun struct](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/struct.rst): ví dụ 1023, thứ tự mạng là big endian, thứ tự gốc phụ thuộc máy. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Phép đổi `ff03` thành 65283 là phép tính của người biên soạn.
Bài viết và hình được thiết kế độc lập.

# Bốn trụ cột của lập trình hướng đối tượng

**Trừu tượng, đóng gói, kế thừa và đa hình là bốn ý tưởng nền của lập trình hướng đối tượng; mỗi ý tưởng trả lời một câu hỏi khác nhau về cách tổ chức mã.**
Bài nguồn nêu bốn trụ cột bằng bốn đoạn ngắn kèm ví dụ; bài này giữ nguyên chúng rồi đối chiếu với cách Python làm.

![Hai nhóm thẻ và một khung ghi nhớ. Che bớt chi tiết, hai thẻ: trừu tượng ẩn chi tiết cài đặt, ví dụ Vehicle có phương thức stop trừu tượng; đóng gói gói dữ liệu và phương thức vào một lớp, ví dụ trường private cùng getter và setter. Dùng lại và thay đổi, hai thẻ: kế thừa cho lớp con thừa hưởng từ lớp cha, ví dụ Car kế thừa Vehicle; đa hình cho cùng một phương thức chạy khác nhau theo đối tượng gọi nó. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-019-main.svg)

## Đọc hình

**Trừu tượng (abstraction).** Là việc ẩn chi tiết cài đặt và chỉ cho thấy những đặc điểm thiết yếu của một đối tượng. Ví dụ của nguồn: lớp `Vehicle` có phương thức `stop` trừu tượng.

**Đóng gói (encapsulation).** Gói dữ liệu (trường) và phương thức vào một đơn vị duy nhất là lớp, rồi hạn chế truy cập trực tiếp bằng các từ khóa quyền truy cập (access modifier). Ví dụ của nguồn: các trường `private` kèm hàm đọc (getter) và hàm ghi (setter) `public`.

**Kế thừa (inheritance).** Tạo một lớp mới (lớp con) thừa hưởng thuộc tính và phương thức từ một lớp đã có (lớp cha), nhờ đó dùng lại mã. Ví dụ của nguồn: lớp `Car` kế thừa lớp `Vehicle`.

**Đa hình (polymorphism).** Cho phép phương thức chạy khác nhau tùy đối tượng được gọi. Theo nguồn, khi hai kiểu cùng một chuỗi kế thừa thì có thể dùng thay cho nhau mà không gây lỗi.

**Gặp lại trong Python.** Tài liệu hướng dẫn của Python nói lớp con (derived class) có thể ghi đè (override) phương thức của lớp cha, và mọi phương thức Python đều có thể bị ghi đè theo kiểu "ảo" của C++. Với đóng gói, Python khác Java: tài liệu nói biến thể hiện "riêng tư" mà chỉ truy cập được từ bên trong đối tượng thì không tồn tại trong Python; thay vào đó có quy ước đặt dấu gạch dưới ở đầu tên để báo "phần không công khai". Python còn có mô-đun `abc` để định nghĩa lớp cơ sở trừu tượng.

## Giới hạn cần nhớ

Nguồn chỉ định nghĩa từng trụ cột bằng một hai câu và một ví dụ nhỏ; không có mã, không nói trụ cột nào quan trọng hơn và không nói ngôn ngữ nào thực hiện thế nào. Ví dụ `Vehicle` và `Car` là minh họa, không phải mã thật.
Từ khóa quyền truy cập như `private` và `public` là chuyện của một số ngôn ngữ; Python dựa vào quy ước. Bài chỉ nêu điều tài liệu Python nói, không so sánh các ngôn ngữ khác. Câu về đa hình của nguồn ("dùng thay cho nhau mà không gây lỗi") bài chưa kiểm chứng ở mọi ngôn ngữ.

## Nhìn hình trả lời

Lớp `Car` dùng lại thuộc tính của lớp `Vehicle` mà không viết lại. Trụ cột nào mô tả điều đó? Còn việc mỗi loại phương tiện dừng theo cách riêng của nó khi gọi `stop` thì thuộc trụ cột nào?

<details>
<summary>Xem đáp án</summary>

Kế thừa: `Car` thừa hưởng thuộc tính và phương thức của `Vehicle`, nên dùng lại mã.
Đa hình: cùng một phương thức `stop` chạy khác nhau tùy đối tượng được gọi. Việc chỉ nêu `stop` mà không nêu cách làm là trừu tượng.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh, một câu hỏi mở đầu và bốn đoạn (trừu tượng, đóng gói, kế thừa, đa hình). Hình ở đây giữ bốn trụ cột theo thứ tự đó và không dùng ảnh nguồn.
Mục "Gặp lại trong Python" lấy từ hướng dẫn lớp của Python và tài liệu mô-đun `abc` tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-fundamental-pillars-of-object-oriented-programming.md): bốn trụ cột và ví dụ.
- [Python — hướng dẫn về lớp](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/tutorial/classes.rst) và [mô-đun abc](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/abc.rst): ghi đè phương thức, biến "riêng tư" bằng quy ước, lớp cơ sở trừu tượng. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Bài này không dùng từ viết tắt cần giải nghĩa.
Bài viết và hình được thiết kế độc lập.

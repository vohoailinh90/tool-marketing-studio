# Bốn trụ cột của lập trình hướng đối tượng

**Trừu tượng, đóng gói, kế thừa và đa hình là bốn ý tưởng nền của lập trình hướng đối tượng; mỗi ý tưởng trả lời một câu hỏi khác nhau về cách tổ chức mã.**
Bài giữ tên bốn trụ cột của bài nguồn, giải thích từng trụ cột bằng bảng thuật ngữ MDN và tài liệu của Python, và dùng một ví dụ tự nghĩ: các hình `Shape`, `Circle` và `Square`.

![Hai nhóm thẻ và một khung ghi nhớ. Che bớt chi tiết: trừu tượng cho người dùng chỉ thấy giao diện đơn giản, ví dụ gọi area của một Shape mà không cần biết công thức; đóng gói gói dữ liệu và hàm vào một lớp rồi kiểm soát truy cập, ví dụ Circle giữ bán kính bên trong. Dùng lại và thay đổi: kế thừa cho lớp con giữ hoặc thêm thuộc tính và phương thức của lớp cha, ví dụ Circle và Square kế thừa Shape; đa hình cho mỗi lớp có hàm riêng, ví dụ area chạy theo từng hình. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-019-main.svg)

## Từ viết tắt

- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

Ví dụ chung: một lớp `Shape` (hình) có hàm `area` (diện tích); `Circle` (hình tròn) và `Square` (hình vuông) là hai lớp con. Ví dụ này do bài tự nghĩ để minh họa, không phải mã thật và không lấy từ nguồn.

**Trừu tượng (abstraction).** Theo MDN, trừu tượng là cách giảm độ phức tạp: giấu sự phức tạp kỹ thuật của một hệ thống sau một giao diện đơn giản hơn. Lợi ích MDN nêu gồm tránh phải viết mã mức thấp, tránh lặp mã, và đổi được cách cài đặt bên trong mà không ảnh hưởng người dùng. Trong ví dụ, người dùng chỉ cần biết gọi `area` của một `Shape`, không cần biết công thức tính nằm ở đâu.

**Đóng gói (encapsulation).** MDN mô tả đóng gói là gói dữ liệu và hàm vào một thành phần, ví dụ một lớp, rồi kiểm soát truy cập vào nó để biến đối tượng thành một "hộp đen": người dùng lớp chỉ cần biết giao diện lộ ra ngoài, không cần biết phần cài đặt bị giấu. Trong ví dụ, `Circle` giữ bán kính bên trong lớp và chỉ cho đọc hoặc đổi qua các hàm của nó. Cách kiểm soát truy cập khác nhau giữa các ngôn ngữ: tài liệu Python nói biến thể hiện "riêng tư" mà chỉ truy cập được từ bên trong đối tượng thì không tồn tại trong Python; thay vào đó có quy ước đặt dấu gạch dưới ở đầu tên để báo "phần không công khai".

**Kế thừa (inheritance).** Theo MDN, đây là một tính năng chính của lập trình hướng đối tượng: các lớp có thể có lớp cha và lớp con, và người viết chọn giữ phần nào của lớp cha rồi thêm phần của riêng mình; một số ngôn ngữ cho một lớp kế thừa nhiều lớp cha. Trong ví dụ, `Circle` và `Square` kế thừa `Shape` nên dùng lại những gì `Shape` đã có. Tài liệu Python nói thêm lớp con có thể ghi đè (override) phương thức của lớp cha, và mọi phương thức trong Python đều có thể bị ghi đè theo kiểu "ảo" của C++.

**Đa hình (polymorphism).** MDN định nghĩa đa hình là đưa ra một giao diện cho nhiều kiểu dữ liệu. Với hướng đối tượng, mỗi lớp chịu trách nhiệm về mã và dữ liệu của chính nó, nên mỗi lớp có hàm riêng và hàm đó chạy đúng với từng đối tượng được gọi. Trong ví dụ, gọi `area` trên `Circle` hay trên `Square` đều được, và mỗi hình tính theo cách của nó.

**Trừu tượng trong Python.** Python có mô-đun `abc` để định nghĩa lớp cơ sở trừu tượng, tức lớp chỉ nêu giao diện chung để lớp con cài đặt.

## Giới hạn cần nhớ

Bài nguồn chỉ định nghĩa từng trụ cột bằng một hai câu và một ví dụ nhỏ; không có mã, không nói trụ cột nào quan trọng hơn và không nói ngôn ngữ nào thực hiện thế nào. Bài này bỏ ví dụ của nguồn và dùng ví dụ `Shape` tự nghĩ; ví dụ đó chỉ để minh họa.
Từ khóa quyền truy cập như `private` và `public` là chuyện của một số ngôn ngữ; Python dựa vào quy ước. Bài chỉ nêu điều MDN và tài liệu Python nói, không so sánh các ngôn ngữ khác, và không kiểm chứng điều nguồn nói về việc hai kiểu cùng một chuỗi kế thừa dùng thay cho nhau được ở mọi ngôn ngữ.

## Nhìn hình trả lời

Trong ví dụ `Shape`, `Circle` dùng lại những gì `Shape` đã có mà không viết lại. Trụ cột nào mô tả điều đó? Còn việc gọi `area` trên mỗi hình cho kết quả riêng của hình đó thì thuộc trụ cột nào?

<details>
<summary>Xem đáp án</summary>

Kế thừa: `Circle` kế thừa `Shape` nên giữ lại và thêm phần của riêng mình.
Đa hình: mỗi lớp có hàm `area` riêng, chạy đúng với đối tượng được gọi. Việc người dùng chỉ cần biết gọi `area` mà không cần biết công thức bên trong là trừu tượng.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh, một câu hỏi mở đầu và bốn đoạn (trừu tượng, đóng gói, kế thừa, đa hình) kèm ví dụ. Bài này giữ tên và thứ tự bốn trụ cột, nhưng viết lại phần giải thích từ bảng thuật ngữ MDN và tài liệu Python tại commit cố định ở mục nguồn, và thay ví dụ của nguồn bằng ví dụ `Shape` tự nghĩ, nên không lặp câu chữ của nguồn. Hình giữ bốn trụ cột theo hai nhóm và không dùng ảnh nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-fundamental-pillars-of-object-oriented-programming.md): chỉ lấy tên bốn trụ cột.
- MDN, bảng thuật ngữ: [Abstraction](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/abstraction/index.md), [Encapsulation](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/encapsulation/index.md), [Inheritance](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/inheritance/index.md) và [Polymorphism](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/polymorphism/index.md). Đọc từ kho mã.
- [Python — hướng dẫn về lớp](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/tutorial/classes.rst) và [mô-đun abc](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/abc.rst): ghi đè phương thức, biến "riêng tư" và quy ước dấu gạch dưới, lớp cơ sở trừu tượng. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Câu giải nghĩa MDN trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

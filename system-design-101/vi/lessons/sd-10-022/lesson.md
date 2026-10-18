# Mệnh lệnh, hàm và hướng đối tượng: ba mô hình lập trình chính

**Ba mô hình chính để tổ chức mã: mô hình mệnh lệnh đổi trạng thái bằng chuỗi lệnh, mô hình hàm tính toán không tác dụng phụ, mô hình hướng đối tượng dựng chương trình từ các đối tượng.**
Bài nguồn so ba mô hình bằng ba danh sách bốn ý; bài này giữ nguyên các ý đó rồi đối chiếu chúng với tài liệu hướng dẫn của Python.

![Ba nhóm thẻ, mỗi nhóm bốn thẻ, và một khung ghi nhớ. Mệnh lệnh: đổi trạng thái bằng chuỗi lệnh; dùng vòng lặp và câu lệnh điều kiện; nhấn mạnh dữ liệu thay đổi được và các bước tường minh; ví dụ C và Python. Hàm: hàm thuần không tác dụng phụ; bất biến; hàm bậc cao, đệ quy và lập trình khai báo; ví dụ Haskell, Lisp, Scala. Hướng đối tượng: mô hình thực thể thành đối tượng chứa dữ liệu và phương thức; kế thừa, đóng gói, đa hình; dùng lớp, đối tượng và giao diện; ví dụ Java, C++, Python, Ruby. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-022-main.svg)

## Đọc hình

**Mệnh lệnh (imperative).**
- Làm việc bằng cách thay đổi trạng thái chương trình qua một chuỗi lệnh.
- Dùng cấu trúc điều khiển như vòng lặp và câu lệnh điều kiện để điều khiển luồng chạy.
- Nhấn mạnh dữ liệu thay đổi được (mutable) và các bước tường minh để hoàn thành việc.
- Ví dụ theo nguồn: C, Python và hầu hết ngôn ngữ thủ tục.

**Hàm (functional).**
- Dựa trên hàm thuần (pure function): tính toán không có tác dụng phụ (side effect).
- Khuyến khích bất biến (immutability) và tránh trạng thái thay đổi được.
- Hỗ trợ hàm bậc cao (higher-order function), đệ quy và lập trình khai báo.
- Ví dụ theo nguồn: Haskell, Lisp, Scala và các tính năng hàm trong những ngôn ngữ như JavaScript.

**Hướng đối tượng (object-oriented).**
- Tập trung mô hình hóa thực thể thực tế thành các đối tượng chứa dữ liệu và phương thức.
- Khuyến khích kế thừa, đóng gói và đa hình.
- Dùng lớp, đối tượng và giao diện (interface) để dựng mã.
- Ví dụ theo nguồn: Java, C++, Python và Ruby.

**Gặp lại trong tài liệu Python.** Hướng dẫn lập trình hàm của Python chia cách giải bài toán thành bốn lối. Thủ tục: chương trình là danh sách lệnh bảo máy làm gì với đầu vào; đa số ngôn ngữ thuộc lối này. Hướng đối tượng: chương trình thao tác trên tập các đối tượng có trạng thái nội bộ và các phương thức để hỏi hoặc sửa trạng thái đó; Smalltalk và Java là ngôn ngữ hướng đối tượng, còn C++ và Python hỗ trợ nhưng không ép dùng. Hàm: bài toán được chia thành các hàm, lý tưởng là hàm chỉ nhận đầu vào và trả đầu ra, không có trạng thái nội bộ ảnh hưởng kết quả; phong cách này không khuyến khích hàm có tác dụng phụ, và hàm không có tác dụng phụ nào gọi là "hàm thuần" (purely functional). Hàm bậc cao là hàm nhận một hay nhiều hàm làm đầu vào hoặc trả về một hàm. Tài liệu cũng nói Lisp, C++ và Python là ngôn ngữ đa mô hình, nên có thể viết chương trình theo nhiều lối.

## Giới hạn cần nhớ

Nguồn chỉ liệt kê đặc điểm, không nói mô hình nào tốt hơn hay khi nào chọn mô hình nào, không có mã và không có ví dụ chạy được. Danh sách ngôn ngữ chỉ là ví dụ của nguồn.
Các mô hình không loại trừ nhau. Nguồn đặt Python vào cả danh sách mệnh lệnh lẫn hướng đối tượng, và tài liệu Python giải thích điều này: đó là ngôn ngữ đa mô hình. Phần đối chiếu chỉ nói điều tài liệu Python nói, không so sánh các ngôn ngữ khác.

## Nhìn hình trả lời

Một hàm chỉ nhận đầu vào, trả đầu ra và không sửa biến nào bên ngoài. Nó thuộc mô hình nào, và tài liệu Python gọi hàm không có tác dụng phụ nào là gì? Python có mặt ở cả danh sách mệnh lệnh và danh sách hướng đối tượng: vì sao điều đó không mâu thuẫn?

<details>
<summary>Xem đáp án</summary>

Mô hình hàm; hàm không có tác dụng phụ nào gọi là hàm thuần (purely functional).
Không mâu thuẫn vì Python là ngôn ngữ đa mô hình: tài liệu của nó nói có thể viết chương trình theo lối thủ tục, hướng đối tượng hoặc hàm.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh, một đoạn dẫn và ba mục, mỗi mục bốn gạch đầu dòng theo thứ tự mệnh lệnh, hàm, hướng đối tượng. Hình ở đây giữ nguyên ba mô hình và bốn ý của mỗi mô hình, không dùng ảnh nguồn.
Mục "Gặp lại trong tài liệu Python" lấy từ hướng dẫn lập trình hàm của Python tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/imperative-vs-functional-vs-object-oriented-programming.md): ba mô hình, mỗi mô hình bốn ý.
- [Python — hướng dẫn lập trình hàm](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/howto/functional.rst): bốn lối thủ tục, khai báo, hướng đối tượng, hàm; hàm thuần; hàm bậc cao; ngôn ngữ đa mô hình. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Bài này không dùng từ viết tắt cần giải nghĩa.
Bài viết và hình được thiết kế độc lập.

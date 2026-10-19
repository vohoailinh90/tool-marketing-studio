# Đọc một sơ đồ lớp UML

**Sơ đồ lớp UML vẽ các lớp của một chương trình và các đường nối giữa chúng, để người đọc hiểu thiết kế mà chưa cần đọc mã. Muốn đọc được chỉ cần biết ba thứ: hộp một lớp có ba ngăn, vài dấu trước tên thành viên, và năm kiểu đường nối.**
Bài này giải thích từng thứ, rồi thử xem mã nguồn có đủ để vẽ lại sơ đồ hay không.

![Ba khung. Khung một, một lớp là hộp ba ngăn: tên lớp, thuộc tính, phương thức; dấu cộng, trừ, thăng, ngã trước tên chỉ quyền truy cập. Khung hai, năm kiểu đường nối: kết hợp, tập hợp, hợp thành, kế thừa, hiện thực. Khung ba, quét thư viện chuẩn Python: 288 lớp có 214 đường kế thừa nhưng chỉ 12 chỗ lớp tự tạo một đối tượng của lớp khác; mã cho thấy ai tạo ra đối tượng chứ không cho thấy ai làm nó mất đi, nên chỉ nhìn mã không phân biệt được tập hợp với hợp thành.](../../diagrams/sd-08-003-main.svg)

## Từ viết tắt

- **UML** (Unified Modeling Language) — ngôn ngữ mô hình hóa thống nhất: bộ ký hiệu chuẩn để vẽ thiết kế phần mềm, trong đó sơ đồ lớp là một loại sơ đồ.

## Đọc hình

**Hộp ba ngăn.** Ngăn trên là tên lớp. Ngăn giữa liệt kê thuộc tính (dữ liệu lớp giữ), ngăn dưới liệt kê phương thức (việc lớp làm được). Trước tên mỗi thành viên có thể có một dấu chỉ ai được dùng nó: `+` công khai, `-` riêng tư, `#` được bảo vệ (lớp con dùng được), `~` trong gói. Một giao diện (interface, bộ phương thức mà lớp nào hiện thực nó cũng phải có) được đánh dấu `<<interface>>` phía trên tên; một kiểu liệt kê (enumeration, tập tên giá trị cố định như loại sản phẩm hay tháng trong năm) được đánh dấu `<<enumeration>>` và liệt kê giá trị.

**Năm kiểu đường nối.** Bảng dưới cho tên, cách đọc và cách viết trong Mermaid (một ngôn ngữ vẽ sơ đồ bằng chữ).

| Đường nối | Đọc là | Mermaid |
|---|---|---|
| Kết hợp (association) | A biết và dùng B lâu dài | `A --> B` |
| Tập hợp (aggregation) | A có các B, B sống riêng được | `A o-- B` |
| Hợp thành (composition) | A có các B, A mất thì B mất | `A *-- B` |
| Kế thừa (inheritance) | A là một loại của B | `B <\|-- A` |
| Hiện thực (realization) | A thực hiện giao diện B | `A ..\|> B` |

Ở hai đầu một đường kết hợp có thể ghi bội số (multiplicity), cho biết mỗi bên có bao nhiêu đối tượng: `1` đúng một, `0..1` không hoặc một, `1..*` một trở lên, `*` nhiều. Ví dụ: một khách hàng `1` có `*` đơn hàng. Cũng có kiểu thứ sáu nhẹ hơn, phụ thuộc (dependency, `A ..> B`: A dùng B thoáng qua), mà bài nguồn không liệt kê.

Điểm dễ lẫn nhất là tập hợp và hợp thành: cả hai đều là "có các phần", khác nhau ở **thời gian sống**. Một chiếc xe và động cơ của nó là hợp thành nếu động cơ không còn ý nghĩa khi xe bị hủy; một nhóm và các thành viên là tập hợp nếu giải tán nhóm thì thành viên vẫn còn.

## Thử: mã nguồn có nói được ai làm mất ai không

Ngày 2026-10-19, một đoạn chương trình Python đọc mã (ast) của ba gói trong thư viện chuẩn Python 3.13: asyncio, email và unittest. Nó đếm hai việc nhìn thấy được trong mã: lớp nào kế thừa lớp nào trong cùng gói, và chỗ nào hàm khởi tạo `__init__` tự tạo một đối tượng của một lớp khác trong gói (`self.x = LopKhac(...)`), dấu hiệu gần nhất của hợp thành mà mã cho thấy.

| Gói | Số lớp | Đường kế thừa | Chỗ lớp tự tạo đối tượng lớp khác |
|---|---|---|---|
| asyncio | 106 | 85 | 8 |
| email | 128 | 98 | 3 |
| unittest | 54 | 31 | 1 |
| Cộng | 288 | 214 | 12 |

Hai điều đọc được. Một, trong ba gói này, đường kế thừa (214) nhiều hơn hẳn chỗ lớp tự tạo đối tượng lớp khác (12), và đọc được thẳng từ danh sách lớp cha; đó là so sánh hai mẫu hẹp mà phép quét đếm được, không phải kết luận rằng kế thừa là quan hệ phổ biến nhất trong mã thật (kết hợp, phụ thuộc, đối tượng truyền vào, hàm tạo riêng không được đếm). Hai, thứ "ai tạo ra đối tượng" mã cho thấy (12 chỗ) cũng chưa đủ để kết luận hợp thành: để biết nó có hủy đi khi lớp chứa bị hủy, phải biết ai còn giữ tham chiếu tới nó, mà việc đó không nằm ở kiểu khai báo. Nên tập hợp và hợp thành là **lời tuyên bố của người thiết kế**, không suy ra được tự động từ mã.

## Giới hạn cần nhớ

Phép quét chỉ đếm hai mẫu đơn giản: tên lớp cha viết thẳng trong danh sách lớp cha, và phép gán `self.x = LopKhac(...)` ngay trong `__init__`, và chỉ tính các lớp cùng gói; nó bỏ sót các cách tạo đối tượng khác (hàm tạo riêng, tạo ở nơi khác rồi truyền vào) và cả mã Python ngoài ba gói. Con số 12 vì thế chỉ là cận dưới của "chỗ lớp tự tạo", không phải số hợp thành thật. Bài cũng không kiểm cách các công cụ vẽ hiển thị hay sinh mã: Mermaid chỉ được đọc ở phần tài liệu cú pháp của nó, chưa vẽ ra ở đây. Cách đọc "tập hợp khác hợp thành ở thời gian sống" là kiến thức chung của người biên soạn về UML, chưa đối chiếu với đặc tả UML của tổ chức chuẩn hóa.

## Nhìn hình trả lời

Trong một cửa hàng, `DonHang` có nhiều `DongHang`, và một dòng hàng không có nghĩa nếu đơn hàng bị hủy. `KhachHang` có thể có nhiều `DonHang` nhưng vẫn tồn tại khi đơn bị hủy. `ThanhToan` là một giao diện mà `TheTinDung` và `ChuyenKhoan` cùng hiện thực. Vẽ các đường nối nào?

<details>
<summary>Xem đáp án</summary>

`DonHang *-- DongHang`: hợp thành, vì dòng hàng mất theo đơn hàng. `KhachHang "1" --> "*" DonHang`: kết hợp (hoặc tập hợp nếu muốn nhấn "khách có đơn"), vì khách vẫn tồn tại khi đơn bị hủy, và bội số 1 và nhiều. `TheTinDung ..|> ThanhToan` và `ChuyenKhoan ..|> ThanhToan`: hiện thực, ở trên `ThanhToan` đặt `<<interface>>`. Không có đường kế thừa nào, vì không lớp nào "là một loại của" lớp khác.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một danh sách các thành phần của sơ đồ lớp (lớp, thuộc tính, phương thức, giao diện, kiểu liệt kê, quan hệ) và liệt kê năm quan hệ không giải thích. Bài này giữ danh sách đó, thêm cách đọc dấu quyền truy cập và bội số, nói rõ tập hợp khác hợp thành ở thời gian sống, và thêm phép thử xem mã nguồn có đủ để suy ra các quan hệ này hay không.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-cheatsheet-for-uml-class-diagrams.md): các thành phần của sơ đồ lớp và năm quan hệ.
- [Mermaid — cú pháp sơ đồ lớp](https://github.com/mermaid-js/mermaid/blob/e28fbd9ded0a07ba9569e51be4764c1ad4daa8f6/packages/mermaid/src/docs/syntax/classDiagram.md): dấu quyền truy cập, kiểu đường nối, bội số, chú thích giao diện và kiểu liệt kê. Đọc từ bản clone của kho.
- [Thư viện chuẩn Python 3.13 — asyncio, email, unittest](https://docs.python.org/3.13/library/index.html): ba gói được quét, đọc từ bản cài đặt trên máy thử.

Đã đọc nguồn ngày 2026-10-19. Cách đọc tập hợp và hợp thành, và phép quét, là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

# Tám mô hình lập trình

**Mô hình lập trình là một cách nghĩ về chương trình; bài nguồn nêu tám cách: mệnh lệnh, khai báo, hướng đối tượng, hướng khía cạnh, hàm, phản ứng, tổng quát và đồng thời.**
Bài này giữ các định nghĩa của nguồn, gom chúng thành ba nhóm, rồi đối chiếu bốn mô hình với tài liệu của Python, Java và Go.

![Ba nhóm thẻ và một khung ghi nhớ. Cách mô tả chương trình: mệnh lệnh mô tả chuỗi bước đổi trạng thái; khai báo nêu logic không nêu luồng điều khiển; hàm xem tính toán là tính giá trị hàm toán học. Cách tổ chức mã: hướng đối tượng xoay quanh đối tượng; hướng khía cạnh tách mối quan tâm cắt ngang; tổng quát viết mã không gắn với kiểu dữ liệu. Nhiều việc và dữ liệu thay đổi: phản ứng xử lý luồng dữ liệu bất đồng bộ; đồng thời chạy nhiều tác vụ cùng lúc. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-020-main.svg)

## Từ viết tắt

- **FP** (Functional Programming) — lập trình hàm: mô hình xem tính toán là việc tính giá trị của các hàm.
- **OOP** (Object-Oriented Programming) — lập trình hướng đối tượng: mô hình xoay quanh các đối tượng gói dữ liệu và hành vi.
- **AOP** (Aspect-Oriented Programming) — lập trình hướng khía cạnh: mô hình tách các mối quan tâm cắt ngang nhiều phần của hệ thống.
- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; bài trích mã nguồn của nó để đối chiếu.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để hỏi và ghi dữ liệu; tài liệu Python lấy nó làm ví dụ về ngôn ngữ khai báo.

## Đọc hình

**Cách mô tả chương trình.**
- Mệnh lệnh (imperative): mô tả một chuỗi bước làm thay đổi trạng thái của chương trình. Nguồn nêu C, C++, Java, Python (ở một mức nào đó) và nhiều ngôn ngữ khác hỗ trợ lối này.
- Khai báo (declarative): nhấn mạnh việc nêu logic và chức năng mà không mô tả luồng điều khiển một cách tường minh. Nguồn nói lập trình hàm là một dạng phổ biến của lập trình khai báo.
- Hàm (functional, FP): xem tính toán như việc tính các hàm toán học, nhấn mạnh dữ liệu bất biến (immutable) và biểu thức khai báo. Nguồn nêu Haskell, Lisp, Erlang, và một số tính năng trong JavaScript, Python, Scala.

**Cách tổ chức mã.**
- Hướng đối tượng (OOP): xoay quanh đối tượng, mỗi đối tượng gói dữ liệu (thuộc tính) và hành vi (phương thức). Nguồn nêu Java, C++, Python, Ruby, C#.
- Hướng khía cạnh (AOP): tách các mối quan tâm cắt ngang nhiều phần của một hệ thống phần mềm. Nguồn nêu AspectJ là một trong những khung AOP nổi tiếng nhất, mở rộng Java.
- Tổng quát (generic): viết mã dùng lại, linh hoạt, không phụ thuộc kiểu, cho phép viết thuật toán và cấu trúc dữ liệu mà không nêu kiểu chúng làm việc. Nguồn nói nó được dùng nhiều trong thư viện và khung để tạo danh sách, ngăn xếp, hàng đợi và các thuật toán như sắp xếp, tìm kiếm.

**Nhiều việc và dữ liệu thay đổi.**
- Phản ứng (reactive): xử lý các luồng dữ liệu bất đồng bộ và lan truyền thay đổi. Nguồn nói ứng dụng hướng sự kiện và ứng dụng xử lý dữ liệu luồng hưởng lợi từ mô hình này.
- Đồng thời (concurrent): chạy nhiều tác vụ hoặc tiến trình cùng lúc để cải thiện hiệu năng và tận dụng tài nguyên. Nguồn nêu máy chủ đa luồng, xử lý song song, máy chủ web đồng thời và tính toán hiệu năng cao.

**Gặp lại trong tài liệu gốc.**
- Hướng dẫn lập trình hàm của Python chia ngôn ngữ thành bốn lối: thủ tục (chuỗi lệnh), khai báo (như SQL, mô tả dữ liệu cần lấy chứ không nêu cách lấy), hướng đối tượng và hàm. Tài liệu cũng nói Lisp, C++ và Python là ngôn ngữ đa mô hình, có thể viết chương trình theo nhiều lối khác nhau.
- Mã JDK có `Flow`, một bộ giao diện cho các thành phần có điều khiển lưu lượng, trong đó nhà xuất bản (Publisher) tạo ra các phần tử mà một hoặc nhiều người đăng ký (Subscriber) tiêu thụ. Đó là cách Java hiện thực ý tưởng luồng phản ứng.
- Thư viện chuẩn của Java khai báo kiểu phần tử như một tham số: lớp `List` ghi "the type of elements in this list" cho tham số kiểu `E`. Đó là dạng lập trình tổng quát mà nguồn nói tới.
- Tài liệu Effective Go phân biệt đồng thời (concurrency, chia chương trình thành các thành phần chạy độc lập) với song song (parallelism, chạy các phép tính song song trên nhiều bộ xử lý để tăng hiệu quả), và nói Go là ngôn ngữ đồng thời chứ không phải ngôn ngữ song song.

## Giới hạn cần nhớ

Nguồn định nghĩa mỗi mô hình bằng một hai câu và vài tên ngôn ngữ; không nói mô hình nào tốt hơn, và các mô hình không loại trừ nhau (một chương trình có thể pha nhiều mô hình, như tài liệu Python nói). Danh sách ngôn ngữ cho mỗi mô hình là ví dụ của nguồn, bài chưa kiểm tra từng cái.
Nguồn dùng từ "đồng thời" kèm "xử lý song song" như cùng một ý; theo Effective Go hai khái niệm này khác nhau, nên đừng dùng hai từ thay cho nhau. Phần đối chiếu chỉ là vài trường hợp, không phải danh sách đầy đủ.

## Nhìn hình trả lời

Một câu lệnh SQL chỉ nêu bạn muốn lấy những dòng nào và để hệ cơ sở dữ liệu tự quyết cách lấy. Theo tài liệu Python, đó là lối lập trình nào? Và lối nào xem tính toán là chuỗi tính giá trị của hàm, ưu tiên dữ liệu bất biến?

<details>
<summary>Xem đáp án</summary>

Lối khai báo: nêu cái cần có chứ không nêu luồng điều khiển.
Lối hàm (lập trình hàm): xem tính toán như việc tính giá trị các hàm toán học và nhấn mạnh dữ liệu bất biến.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và tám đoạn theo thứ tự mệnh lệnh, khai báo, hướng đối tượng, hướng khía cạnh, hàm, phản ứng, tổng quát, đồng thời. Hình ở đây giữ cả tám mô hình và chia chúng thành ba nhóm theo việc mô hình lo; cách chia nhóm là của bài, không phải của nguồn. Bài không dùng ảnh nguồn.
Mục "Gặp lại trong tài liệu gốc" lấy từ tài liệu của Python, mã JDK và Effective Go tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-8-programming-paradigms.md): tám mô hình và ví dụ ngôn ngữ.
- [Python — hướng dẫn lập trình hàm](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/howto/functional.rst): bốn lối thủ tục, khai báo, hướng đối tượng, hàm; ngôn ngữ đa mô hình. Đọc từ kho mã.
- [OpenJDK — Flow](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/Flow.java) và [List](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/List.java): luồng phản ứng, kiểu phần tử là tham số. Đọc từ kho mã.
- [Go — Effective Go](https://github.com/golang/website/blob/d1edce5b8ec957935895f507f3253d6e02447a6c/_content/doc/effective_go.html): đồng thời khác song song. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa FP, OOP, AOP và SQL trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

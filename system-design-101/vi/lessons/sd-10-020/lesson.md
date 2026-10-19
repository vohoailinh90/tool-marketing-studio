# Tám mô hình lập trình

**Mô hình lập trình là một cách nghĩ về chương trình; bài nguồn nêu tám cách: mệnh lệnh, khai báo, hướng đối tượng, hướng khía cạnh, hàm, phản ứng, tổng quát và đồng thời.**
Bài giữ tên tám mô hình của nguồn, gom chúng thành ba nhóm theo việc mô hình lo, và giải thích các mô hình bằng tài liệu của Python, MDN, Spring, AspectJ, Reactive Streams, JDK và Go; riêng định nghĩa chung của mô hình phản ứng là kiến thức của người biên soạn, chưa đối chiếu, và Reactive Streams chỉ làm ví dụ.

![Ba nhóm thẻ và một khung ghi nhớ. Cách mô tả chương trình: mệnh lệnh là danh sách lệnh bảo máy làm gì; khai báo nêu bài toán và để cài đặt tự chọn cách giải; hàm chia việc thành các hàm nhận vào rồi trả ra. Cách tổ chức mã: hướng đối tượng xoay quanh đối tượng có trạng thái và phương thức; hướng khía cạnh tách mối quan tâm cắt ngang nhiều kiểu; tổng quát dùng kiểu như một tham số. Nhiều việc và dữ liệu thay đổi: phản ứng là phản ứng với dữ liệu đến theo thời gian, ví dụ Reactive Streams; đồng thời chia chương trình thành các phần chạy độc lập. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-020-main.svg)

## Từ viết tắt

- **FP** (Functional Programming) — lập trình hàm: mô hình chia việc thành các hàm.
- **OOP** (Object-Oriented Programming) — lập trình hướng đối tượng: mô hình xoay quanh các đối tượng gói dữ liệu và hành vi.
- **AOP** (Aspect-Oriented Programming) — lập trình hướng khía cạnh: mô hình tách các mối quan tâm cắt ngang nhiều phần của hệ thống.
- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; bài trích mã nguồn của nó để đối chiếu.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để hỏi và ghi dữ liệu; tài liệu Python lấy nó làm ví dụ về ngôn ngữ khai báo.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

**Cách mô tả chương trình.**
- Mệnh lệnh (imperative): tài liệu lập trình hàm của Python gọi lối này là "thủ tục" (procedural): chương trình là một danh sách lệnh bảo máy làm gì với dữ liệu vào; C, Pascal và cả các shell của Unix là ngôn ngữ thủ tục. Bài hiểu "thủ tục" của Python gần với "mệnh lệnh" của nguồn, đó là cách đọc của người biên soạn.
- Khai báo (declarative): theo tài liệu Python, người viết đưa ra một bản đặc tả mô tả bài toán cần giải, còn phần cài đặt của ngôn ngữ tự tìm cách tính hiệu quả. Ví dụ quen nhất là SQL: một câu truy vấn mô tả tập dữ liệu cần lấy, còn động cơ SQL quyết định quét bảng hay dùng chỉ mục, mệnh đề nào chạy trước.
- Hàm (functional, FP): cũng theo tài liệu Python, lập trình hàm chia bài toán thành một tập hàm. Lý tưởng là hàm chỉ nhận đầu vào và trả đầu ra, không có trạng thái bên trong ảnh hưởng đến kết quả của một đầu vào đã cho. Lối này không khuyến khích hàm có tác dụng phụ; hàm không có tác dụng phụ nào gọi là hàm thuần túy. Các ngôn ngữ hàm nổi tiếng gồm họ `ML` và Haskell, còn chương trình Python viết theo lối hàm thường chỉ dựng giao diện trông như hàm và vẫn dùng tính năng không thuần túy ở bên trong.

**Cách tổ chức mã.**
- Hướng đối tượng (OOP): MDN mô tả đây là cách tiếp cận trong đó dữ liệu được đóng gói trong các đối tượng và người ta thao tác trên chính đối tượng, thay vì trên từng phần của nó. Tài liệu Python bổ sung rằng đối tượng có trạng thái bên trong và các phương thức để hỏi hoặc đổi trạng thái đó; Smalltalk và Java là ngôn ngữ hướng đối tượng, còn C++ và Python hỗ trợ nhưng không bắt buộc dùng. Bốn ý nền của mô hình này có trong bài riêng về bốn trụ cột.
- Hướng khía cạnh (AOP): tài liệu của Spring nói AOP bổ sung cho OOP một cách nghĩ khác về cấu trúc chương trình: đơn vị chia nhỏ chính của OOP là lớp, còn của AOP là "khía cạnh" (aspect). Khía cạnh cho phép tách riêng những mối quan tâm cắt ngang nhiều kiểu và đối tượng, ví dụ quản lý giao dịch. README của AspectJ tự giới thiệu là phần mở rộng hướng khía cạnh liền mạch cho ngôn ngữ Java, giúp tách riêng gọn gàng các mối quan tâm cắt ngang như xử lý lỗi, đồng bộ hóa, ghi nhật ký và giám sát.
- Tổng quát (generic): viết mã không nêu sẵn kiểu mà nó làm việc. Trong thư viện chuẩn của Java, giao diện (interface) `List` khai báo kiểu phần tử như một tham số kiểu `E` và ghi chú đó là "the type of elements in this list"; nhờ vậy cùng một giao diện dùng được cho danh sách các kiểu khác nhau.

**Nhiều việc và dữ liệu thay đổi.**
- Phản ứng (reactive): cách viết chương trình sao cho nó phản ứng với dữ liệu hoặc sự kiện đến theo thời gian (cách hiểu chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn). Reactive Streams chỉ là một ví dụ cụ thể, không phải định nghĩa của cả mô hình: README của nó nói mục đích là đưa ra một chuẩn cho xử lý luồng bất đồng bộ với áp lực ngược không chặn (non-blocking backpressure). Mã JDK có `Flow`, một bộ giao diện cho các thành phần có điều khiển lưu lượng, trong đó nhà xuất bản (Publisher) tạo ra các phần tử mà một hoặc nhiều người đăng ký (Subscriber) tiêu thụ, và tài liệu của nó nói các giao diện này tương ứng với đặc tả reactive-streams.
- Đồng thời (concurrent): tài liệu Effective Go của Go phân biệt đồng thời (concurrency: chia chương trình thành các thành phần chạy độc lập) với song song (parallelism: chạy các phép tính song song trên nhiều bộ xử lý để tăng hiệu quả), và nói Go là ngôn ngữ đồng thời chứ không phải ngôn ngữ song song.

**Pha trộn mô hình.** Tài liệu Python nói một số ngôn ngữ nhấn mạnh một cách tiếp cận và khiến cách khác khó viết hơn, còn những ngôn ngữ đa mô hình như Lisp, C++ và Python cho phép viết phần lớn theo lối thủ tục, hướng đối tượng hay hàm; trong một chương trình lớn, mỗi phần có thể viết theo một lối.

## Giới hạn cần nhớ

Bài nguồn định nghĩa mỗi mô hình bằng một hai câu và vài tên ngôn ngữ; không nói mô hình nào tốt hơn. Bài này chỉ dùng tên tám mô hình của nguồn, còn danh sách ngôn ngữ nguồn gắn với từng mô hình không được lặp lại hay kiểm tra.
Mỗi mô hình ở trên chỉ được giải thích qua một hai tài liệu, không phải định nghĩa duy nhất; các tài liệu khác có thể chia và đặt tên khác. Hai từ "đồng thời" và "song song" khác nhau theo Effective Go, nên đừng dùng thay cho nhau. Cách đọc "thủ tục" của Python như "mệnh lệnh" là của người biên soạn.

## Nhìn hình trả lời

Một câu truy vấn SQL mô tả tập dữ liệu cần lấy và để động cơ chọn cách lấy: nó thuộc mô hình nào, theo tài liệu Python? Còn một chương trình được chia thành các thành phần chạy độc lập nhưng không nhất thiết trên nhiều bộ xử lý: Effective Go gọi đó là gì?

<details>
<summary>Xem đáp án</summary>

Khai báo: người viết mô tả điều cần có, phần cài đặt quyết định cách tính.
Đồng thời (concurrency): cấu trúc chương trình thành các thành phần chạy độc lập; chạy song song trên nhiều bộ xử lý để tăng hiệu quả là một khái niệm khác.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và tám đoạn, mỗi đoạn định nghĩa một mô hình kèm vài tên ngôn ngữ. Bài này giữ tên tám mô hình, gom chúng thành ba nhóm của riêng bài, và viết lại phần giải thích từ tài liệu Python, bảng thuật ngữ MDN, tài liệu Spring, README của AspectJ và Reactive Streams, mã nguồn JDK và Effective Go tại commit cố định ở mục nguồn nên không lặp câu chữ của nguồn; riêng định nghĩa chung của mô hình phản ứng là kiến thức của người biên soạn, chưa đối chiếu, và Reactive Streams chỉ làm ví dụ. Hình không dùng ảnh nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-8-programming-paradigms.md): chỉ lấy tên tám mô hình.
- [Python — hướng dẫn lập trình hàm](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/howto/functional.rst): thủ tục, khai báo, hướng đối tượng, hàm; ngôn ngữ đa mô hình. Đọc từ kho mã.
- [MDN — thuật ngữ OOP](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/oop/index.md): lập trình hướng đối tượng. Đọc từ kho mã.
- [Spring Framework — AOP](https://github.com/spring-projects/spring-framework/blob/a859427c11e1d6e69f09e7e17970f6b928cadd7e/framework-docs/modules/ROOT/pages/core/aop.adoc) và [AspectJ — README](https://github.com/eclipse-aspectj/aspectj/blob/36e31738da5853953a657565db8fa79ba47aa2a1/README.md): khía cạnh và mối quan tâm cắt ngang. Đọc từ kho mã.
- [Reactive Streams — README](https://github.com/reactive-streams/reactive-streams-jvm/blob/a625d3aba756e9842ad1291a5b73f5db280b6168/README.md), [OpenJDK — Flow](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/Flow.java) và [List](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/List.java): luồng bất đồng bộ, nhà xuất bản và người đăng ký, tham số kiểu. Đọc từ kho mã.
- [Go — Effective Go](https://github.com/golang/website/blob/d1edce5b8ec957935895f507f3253d6e02447a6c/_content/doc/effective_go.html): đồng thời khác song song. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Cách hiểu chung về mô hình phản ứng và các câu giải nghĩa FP, OOP, AOP, SQL và MDN trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

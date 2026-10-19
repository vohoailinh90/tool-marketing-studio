# Dọn rác bộ nhớ hoạt động thế nào?

**Chương trình xin bộ nhớ liên tục, còn bộ dọn rác tự thu hồi phần không còn dùng; mỗi ngôn ngữ chọn một cách dọn khác nhau.**
Bài nguồn chỉ nêu tên ba ngôn ngữ Java, Python và Go; bài này giữ ba ngôn ngữ đó và đọc từng cách theo cùng một câu hỏi: dọn bằng cơ chế nào, và chương trình bị chậm lại ra sao, dựa vào tài liệu của chính JDK, Python và Go.

![Bốn nhóm thẻ xếp dọc. Java, nhóm đơn giản hoặc đề cao thông lượng: Serial dành cho ứng dụng nhỏ và đơn giản, Parallel dùng nhiều bộ xử lý và còn gọi là bộ dọn thông lượng. Java, nhóm quan tâm thời gian dừng: G1 hợp vùng nhớ lớn và là bộ dọn mặc định trong tài liệu JDK được đọc; ZGC và Shenandoah nhắm thời gian dừng rất thấp, không tăng theo kích thước vùng nhớ. CPython và Go chuẩn: CPython đếm tham chiếu và giải phóng khi bộ đếm về không, thêm bộ dọn vòng tham chiếu cho các đối tượng trỏ vòng quanh nhau; Go chuẩn dùng bộ dọn đánh dấu và quét chạy đồng thời với ứng dụng. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-10-002-main.svg)

## Từ viết tắt

- **GC** (Garbage Collection) — dọn rác bộ nhớ: cơ chế tự động thu hồi vùng nhớ mà chương trình không còn dùng; bài cũng gọi bộ dọn rác thực hiện việc đó là GC.
- **ZGC** (Z Garbage Collector) — bộ dọn rác Z: một bộ dọn rác của Java nhắm tới thời gian dừng rất thấp.
- **CMS** (Concurrent Mark-Sweep) — đánh dấu rồi quét đồng thời: tên một bộ dọn rác cũ của Java, mà tài liệu JDK được đọc không còn mô tả.
- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn, trình chạy `java` và tài liệu đi kèm; bài trích tài liệu của nó để đối chiếu.

## Đọc hình

**Điều chung.** Mọi bộ dọn rác phải biết vùng nhớ nào còn được dùng và thu hồi phần còn lại. Chúng khác nhau ở cách biết điều đó và ở việc có buộc chương trình dừng hẳn hay không. Kiểu dừng hẳn trong lúc dọn gọi là "stop-the-world".
Hai thước đo hay gặp: **thông lượng** là tổng lượng việc làm được trong một khoảng thời gian, còn **độ trễ** là thời gian chờ của từng việc, kể cả lúc chương trình bị dừng để dọn.

**Java.** Tài liệu của trình chạy `java` trong JDK mô tả năm bộ dọn rác mà người dùng có thể chọn bằng các tùy chọn dòng lệnh:
- Serial: theo tài liệu, thường là lựa chọn tốt nhất cho ứng dụng nhỏ và đơn giản, không cần tính năng đặc biệt nào từ bộ dọn rác.
- Parallel: còn gọi là bộ dọn thông lượng (throughput collector); dùng nhiều bộ xử lý để cải thiện hiệu năng của ứng dụng.
- G1 (Garbage-First): bộ dọn kiểu máy chủ, hướng tới máy nhiều bộ xử lý và nhiều bộ nhớ; theo tài liệu, nó đạt mục tiêu thời gian dừng với xác suất cao mà vẫn giữ thông lượng tốt, và là bộ dọn mặc định trong bản tài liệu đã đọc.
- ZGC: bộ dọn có độ trễ thấp, thời gian dừng tối đa cỡ vài mili giây, đổi lại một phần thông lượng; thời gian dừng không phụ thuộc kích thước vùng nhớ.
- Shenandoah: bộ dọn đồng thời với thời gian dừng thấp, cũng không tăng theo kích thước vùng nhớ.
Bài nguồn có nhắc thêm CMS, nhưng tài liệu JDK được đọc không có tùy chọn nào cho CMS, nên bài này không mô tả nó. Bộ nào có sẵn và bộ nào là mặc định tùy phiên bản JDK.

**Python (CPython).** Hai lớp. Theo tài liệu mô hình dữ liệu của Python, CPython hiện dùng đếm tham chiếu kèm việc phát hiện chậm (tùy chọn) các vòng tham chiếu: hầu hết đối tượng được thu hồi ngay khi không còn ai trỏ tới, nhưng rác chứa vòng tham chiếu thì không được bảo đảm. Từ điển thuật ngữ nói số tham chiếu là số chỗ đang trỏ tới một đối tượng, và về không thì đối tượng được giải phóng. Lớp thứ hai là bộ dọn vòng tham chiếu, xử lý những đối tượng trỏ vòng quanh nhau mà bộ đếm không giải quyết được; tài liệu mô-đun `gc` nói nó bổ sung cho đếm tham chiếu và có thể tắt nếu chắc chương trình không tạo vòng. Tài liệu đánh dấu đây là chi tiết cài đặt của CPython, các bản cài đặt khác hoạt động khác và CPython có thể đổi, nên đừng coi đếm tham chiếu là bảo đảm của chính ngôn ngữ Python (PyPy là một bản như vậy, theo kiến thức chung của người biên soạn).

**Go (bộ công cụ chuẩn).** Bộ dọn kiểu đánh dấu rồi quét (mark-and-sweep) chạy đồng thời với ứng dụng để giảm các lần dừng. Tài liệu của Go nói nó không hoàn toàn dừng toàn bộ: phần lớn việc dọn chạy đồng thời với ứng dụng, nhưng không phải toàn bộ, nên vẫn có lúc ứng dụng phải dừng. Cũng theo tài liệu đó, đặc tả ngôn ngữ Go không đòi phải có bộ dọn rác, và phần mô tả này áp dụng cho bộ công cụ chuẩn của Go (trình biên dịch `gc` và các công cụ đi kèm), nên bản cài đặt Go khác có thể làm khác.

## Giới hạn cần nhớ

Dọn đồng thời không miễn phí. Tài liệu của Go nói thực tế nó thường dẫn tới thiết kế có thông lượng thấp hơn một bộ dọn dừng toàn bộ tương đương, và cũng nói rõ độ trễ thấp không đương nhiên kéo theo thông lượng thấp. Vì vậy chọn bộ dọn là chọn cái cần nhất: tổng việc làm hay thời gian chờ từng việc.
Mô tả các bộ dọn của Java lấy từ một bản tài liệu JDK cố định; bộ nào có sẵn và bộ nào là mặc định tùy phiên bản, nên hãy xem tài liệu của phiên bản đang dùng.
Bài này so sánh cách làm, không đo tốc độ, nên không có con số nào ở đây.

## Nhìn hình trả lời

Trong CPython, hai đối tượng trỏ vào nhau và không còn biến nào khác trỏ tới chúng. Bộ đếm tham chiếu của từng đối tượng có về không không? Phần nào của hình xử lý trường hợp này?

<details>
<summary>Xem đáp án</summary>

Không. Mỗi đối tượng vẫn được đối tượng kia trỏ tới nên bộ đếm không về không, và đếm tham chiếu một mình không giải phóng được chúng.
Đây chính là việc của bộ dọn vòng tham chiếu, lớp thứ hai trong cách dọn của CPython.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn chia theo ngôn ngữ và chỉ ghi mỗi bộ dọn của Java một dòng. Bài này chỉ giữ tên ba ngôn ngữ và ý "mỗi ngôn ngữ chọn một cách dọn"; không dịch hay diễn đạt lại các dòng mô tả đó mà dựng phần Java từ tài liệu trình chạy `java` của JDK (nên có Shenandoah, không có CMS), phần Python từ tài liệu mô-đun `gc` và phần Go từ hướng dẫn về bộ dọn rác của Go.
Hình đặt Serial và Parallel thành một nhóm, G1, ZGC và Shenandoah thành nhóm quan tâm thời gian dừng, và đặt Python cạnh Go vì cả hai chỉ có một cơ chế chính. Những câu về chi phí của dọn đồng thời, về việc tắt bộ dọn vòng và về "stop-the-world" lấy từ tài liệu của Go và Python.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-garbage-collection-work.md): tên ba ngôn ngữ.
- [OpenJDK — tài liệu trình chạy java](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/man/java.md): các tùy chọn chọn bộ dọn rác Serial, Parallel, G1, ZGC và Shenandoah. Đọc từ kho mã.
- [Python — tài liệu mô hình dữ liệu](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/reference/datamodel.rst) và [từ điển thuật ngữ](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/glossary.rst): CPython dùng đếm tham chiếu, về không thì giải phóng, đây là chi tiết cài đặt. Đọc từ kho mã.
- [Python — tài liệu mô-đun gc](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/gc.rst): bộ dọn bổ sung cho đếm tham chiếu, có thể tắt nếu không tạo vòng tham chiếu. Đọc từ kho mã.
- [Go — hướng dẫn về bộ dọn rác](https://github.com/golang/website/blob/d1edce5b8ec957935895f507f3253d6e02447a6c/_content/doc/gc-guide.html): mark-sweep, chạy đồng thời, thông lượng và độ trễ. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Câu giải nghĩa GC trong mục từ viết tắt và việc nêu PyPy làm ví dụ cho bản cài đặt khác là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

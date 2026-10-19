# Dọn rác bộ nhớ hoạt động thế nào?

**Chương trình xin bộ nhớ liên tục, còn bộ dọn rác tự thu hồi phần không còn dùng; mỗi ngôn ngữ chọn một cách dọn khác nhau.**
Bài nguồn nêu cách làm của Java, Python và Go; bài này đọc ba cách đó theo cùng một câu hỏi: dọn bằng cơ chế nào, và chương trình bị chậm lại ra sao.

![Bốn nhóm thẻ xếp dọc. Java, nhóm nhỏ gọn hoặc đề cao thông lượng: bộ dọn Serial hợp môi trường một luồng hoặc ứng dụng nhỏ; bộ dọn Parallel còn gọi là Throughput Collector. Java, nhóm quan tâm thời gian dừng: CMS nhắm độ trễ thấp, G1 cân bằng thông lượng và độ trễ, ZGC dành cho vùng nhớ lớn và thời gian dừng tối thiểu. CPython và Go chuẩn: CPython đếm tham chiếu và giải phóng khi bộ đếm về không, thêm bộ dọn vòng tham chiếu cho các đối tượng trỏ vòng quanh nhau; Go chuẩn dùng bộ dọn đánh dấu và quét chạy đồng thời với ứng dụng. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-10-002-main.svg)

## Từ viết tắt

- **GC** (Garbage Collection) — dọn rác bộ nhớ: cơ chế tự động thu hồi vùng nhớ mà chương trình không còn dùng; bài cũng gọi bộ dọn rác thực hiện việc đó là GC.
- **CMS** (Concurrent Mark-Sweep) — đánh dấu rồi quét đồng thời: tên một bộ dọn rác của Java, nhắm tới việc giảm thời gian dừng.
- **ZGC** (Z Garbage Collector) — bộ dọn rác Z: một bộ dọn rác của Java dành cho vùng nhớ lớn và thời gian dừng tối thiểu.

## Đọc hình

**Điều chung.** Mọi bộ dọn rác phải biết vùng nhớ nào còn được dùng và thu hồi phần còn lại. Chúng khác nhau ở cách biết điều đó và ở việc có buộc chương trình dừng hẳn hay không. Kiểu dừng hẳn trong lúc dọn gọi là "stop-the-world".
Hai thước đo hay gặp: **thông lượng** là tổng lượng việc làm được trong một khoảng thời gian, còn **độ trễ** là thời gian chờ của từng việc, kể cả lúc chương trình bị dừng để dọn.

**Java.** Bài nguồn nêu năm bộ dọn rác, mỗi bộ hợp một hoàn cảnh:
- Serial: hợp môi trường một luồng hoặc ứng dụng nhỏ.
- Parallel: còn gọi là "Throughput Collector", đề cao thông lượng.
- CMS: nhắm độ trễ thấp, giảm thời gian dừng.
- G1 (Garbage-First): cân bằng giữa thông lượng và độ trễ.
- ZGC: dành cho ứng dụng cần vùng nhớ lớn và thời gian dừng tối thiểu.

**Python (CPython).** Hai lớp. Lớp đầu là đếm tham chiếu: mỗi đối tượng có một bộ đếm, về không thì vùng nhớ được giải phóng. Lớp thứ hai là bộ dọn vòng tham chiếu, xử lý những đối tượng trỏ vòng quanh nhau mà bộ đếm không giải quyết được. Tài liệu của Python nói bộ dọn này bổ sung cho đếm tham chiếu và có thể tắt nếu chắc chương trình không tạo vòng. Đây là cách của CPython, bản cài đặt Python phổ biến nhất; các bản cài đặt khác, như PyPy, không nhất thiết đếm tham chiếu từng đối tượng, nên đừng coi đếm tham chiếu là bảo đảm của chính ngôn ngữ Python.

**Go (bộ công cụ chuẩn).** Bộ dọn kiểu đánh dấu rồi quét (mark-and-sweep) chạy đồng thời với ứng dụng để giảm các lần dừng. Tài liệu của Go nói nó không hoàn toàn dừng toàn bộ: phần lớn việc dọn chạy đồng thời với ứng dụng, nhưng không phải toàn bộ, nên vẫn có lúc ứng dụng phải dừng. Cũng theo tài liệu đó, đặc tả ngôn ngữ Go không đòi phải có bộ dọn rác, và phần mô tả này áp dụng cho bộ công cụ chuẩn của Go (trình biên dịch `gc` và các công cụ đi kèm), nên bản cài đặt Go khác có thể làm khác.

## Giới hạn cần nhớ

Dọn đồng thời không miễn phí. Tài liệu của Go nói thực tế nó thường dẫn tới thiết kế có thông lượng thấp hơn một bộ dọn dừng toàn bộ tương đương, và cũng nói rõ độ trễ thấp không đương nhiên kéo theo thông lượng thấp. Vì vậy chọn bộ dọn là chọn cái cần nhất: tổng việc làm hay thời gian chờ từng việc.
Bài nguồn không nói phiên bản Java. Bộ dọn nào có sẵn và bộ nào là mặc định tùy phiên bản, nên xem tài liệu của phiên bản đang dùng; đây là kiến thức chung của người biên soạn.
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

Bài nguồn chia theo ngôn ngữ và chỉ ghi mỗi bộ dọn một dòng. Hình này gộp năm bộ của Java thành hai nhóm theo điều mỗi bộ nhắm tới trong chính mô tả của nguồn, và đặt Python cạnh Go vì cả hai chỉ có một cơ chế chính.
Những câu về chi phí của dọn đồng thời, về việc tắt bộ dọn vòng và về "stop-the-world" lấy từ tài liệu của Go và Python, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-garbage-collection-work.md): ba ngôn ngữ và các bộ dọn rác.
- [Python — tài liệu mô-đun gc](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/gc.rst): bộ dọn bổ sung cho đếm tham chiếu, có thể tắt nếu không tạo vòng tham chiếu. Đọc từ kho mã.
- [Go — hướng dẫn về bộ dọn rác](https://github.com/golang/website/blob/d1edce5b8ec957935895f507f3253d6e02447a6c/_content/doc/gc-guide.html): mark-sweep, chạy đồng thời, thông lượng và độ trễ. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Mô tả các bộ dọn của Java là của bài nguồn, chưa đối chiếu với tài liệu Java.
Bài viết và hình được thiết kế độc lập.

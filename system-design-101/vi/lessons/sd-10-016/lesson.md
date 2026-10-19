# Mười một cấu trúc dữ liệu dùng hằng ngày

**Mỗi cấu trúc dữ liệu thường đi với một việc quen thuộc: ngăn xếp với hoàn tác, hàng đợi với lệnh in, bảng băm với bộ nhớ đệm, đồ thị với quan hệ bạn bè.**
Tiêu đề bài nguồn nói "10 cấu trúc" nhưng danh sách có mười một; bài giữ tên và ví dụ trong danh sách đó, đếm lại, rồi giải thích từng cấu trúc bằng tài liệu của Java, của MDN và của WebGL.

![Ba nhóm thẻ và một khung ghi nhớ. Danh sách và thứ tự: danh sách là dãy có thứ tự, ví dụ dòng tin; mảng là các giá trị có chỉ số, ví dụ tính toán số; ngăn xếp vào sau ra trước, ví dụ hoàn tác; hàng đợi chờ xử lý, ví dụ lệnh in. Tra cứu và sắp việc: bảng băm tra cứu nhanh nhờ hàm băm, ví dụ bộ nhớ đệm; đống lấy phần tử ưu tiên nhất trước, ví dụ lập lịch; cây nối các nút, ví dụ tài liệu HTML; cây hậu tố, ví dụ tìm chuỗi trong tài liệu. Quan hệ, không gian và đồ họa: đồ thị cho quan hệ bạn bè hoặc tìm đường; R-tree tìm hàng xóm gần nhất; vertex buffer là bộ đệm điểm đỉnh để vẽ. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-016-main.svg)

## Từ viết tắt

- **HTML** (HyperText Markup Language) — ngôn ngữ đánh dấu siêu văn bản: văn bản dùng thẻ để mô tả cấu trúc của một trang web; trang đó được giữ trong bộ nhớ dưới dạng cây.
- **DOM** (Document Object Model) — mô hình đối tượng tài liệu: cách trình duyệt giữ một trang HTML trong bộ nhớ, dưới dạng một cây các nút.
- **AI** (Artificial Intelligence) — trí tuệ nhân tạo: các hệ thống máy tính làm những việc thường cần trí thông minh của con người; ở đây là chương trình ra quyết định.
- **GPU** (Graphics Processing Unit) — bộ xử lý đồ họa: chip chuyên vẽ hình; vertex buffer là cách đưa dữ liệu điểm vẽ tới chip này.
- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; bài trích mã nguồn của nó để đối chiếu.
- **LIFO** (Last In, First Out) — vào sau, ra trước: phần tử thêm vào sau cùng là phần tử lấy ra đầu tiên, đúng kiểu của ngăn xếp.
- **FIFO** (First In, First Out) — vào trước, ra trước: phần tử thêm vào sớm nhất được lấy ra đầu tiên, đúng kiểu hàng đợi thông thường.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

**Danh sách và thứ tự.**
- Danh sách (List): dãy phần tử có thứ tự, trong đó người dùng kiểm soát được từng phần tử nằm ở vị trí nào và lấy ra theo chỉ số nguyên; khác với tập hợp, danh sách thường cho phép phần tử trùng nhau (tài liệu `List` của JDK). Bài nguồn gắn nó với dòng tin trên mạng xã hội, ví dụ là Twitter.
- Mảng (Array): theo MDN, một tập dữ liệu có thứ tự, lưu nhiều giá trị dưới một tên; mỗi phần tử có một số gọi là chỉ số, và trong JavaScript chỉ số bắt đầu từ 0. Bài nguồn gắn nó với các phép toán số học.
- Ngăn xếp (Stack): tài liệu `Deque` của JDK nói hàng đợi hai đầu có thể dùng như ngăn xếp LIFO, thêm và lấy phần tử ở một đầu, và nên dùng thay lớp `Stack` cũ. Bài nguồn gắn ngăn xếp với hoàn tác và làm lại (undo/redo) trong trình soạn văn bản: thao tác vừa làm là thao tác được hoàn tác trước.
- Hàng đợi (Queue): tài liệu `Queue` mô tả đây là tập hợp để giữ phần tử trước khi xử lý, thường, nhưng không nhất thiết, sắp theo FIFO. Bài nguồn gắn nó với lệnh in, hoặc với việc gửi các thao tác của người chơi trong game.

**Tra cứu và sắp việc.**
- Bảng băm (Hash table): tài liệu `HashSet` nói lớp này dựa trên một bảng băm và cho thời gian hằng số với các thao tác cơ bản (thêm, xóa, kiểm tra có không) nếu hàm băm rải phần tử đều vào các ngăn. Bài nguồn gắn bảng băm với hệ thống bộ nhớ đệm (cache).
- Đống (Heap): tài liệu `PriorityQueue` mô tả hàng đợi ưu tiên dựa trên một đống ưu tiên (priority heap); phần tử ở đầu là phần tử nhỏ nhất theo thứ tự đã chọn. Bài nguồn gắn đống với việc lập lịch tác vụ.
- Cây (Tree): theo MDN, trình duyệt giữ một trang HTML dưới dạng cây nút gọi là cây DOM, mỗi nút là một phần của tài liệu. Bài nguồn gắn cây với việc giữ tài liệu HTML, và với quyết định của AI.
- Cây hậu tố (Suffix tree): bài nguồn gắn nó với việc tìm một chuỗi trong tài liệu. Bài không có tài liệu gốc cho cấu trúc này.

**Quan hệ, không gian và đồ họa.**
- Đồ thị (Graph): bài nguồn gắn nó với theo dõi quan hệ bạn bè, hoặc tìm đường. Bài không có tài liệu gốc cho cấu trúc này.
- R-tree: bài nguồn gắn nó với việc tìm hàng xóm gần nhất. Bài không có tài liệu gốc cho cấu trúc này.
- Vertex buffer: tài liệu MDN về `WebGLBuffer` nói đây là một vùng đệm lưu dữ liệu như các đỉnh (vertex) hoặc màu; MDN giải thích GPU là thành phần chuyên vẽ đồ họa 2D và 3D lên màn hình. Bài nguồn gắn nó với việc gửi dữ liệu tới GPU để vẽ.

## Giới hạn cần nhớ

Mỗi cấu trúc ở trên chỉ có một việc đi kèm trong bài nguồn; ví dụ chỉ là minh họa, không phải mô tả cách các ứng dụng đó thật sự được xây, và bài không nói khi nào nên chọn cấu trúc nào.
Tiêu đề nguồn nói mười cấu trúc nhưng danh sách có mười một mục (List, Stack, Queue, Hash Table, Array, Heap, Tree, Suffix Tree, Graph, R-Tree, Vertex Buffer); bài theo danh sách. Ví dụ thư viện Java chỉ là vài trường hợp đã đối chiếu, không phải danh sách đầy đủ, và các ngôn ngữ khác có thể đặt tên khác. Cây hậu tố, đồ thị và R-tree chưa đối chiếu với tài liệu gốc nào.

## Nhìn hình trả lời

Bạn gõ chữ trong một trình soạn văn bản, bấm hoàn tác ba lần rồi làm lại một lần. Nguồn gắn việc này với cấu trúc nào, và vì sao kiểu "vào sau, ra trước" hợp với nó? Còn nhiều lệnh in gửi tới một máy in thì nguồn gắn với cấu trúc nào, và tài liệu `Queue` nói thứ tự thông thường của nó là gì?

<details>
<summary>Xem đáp án</summary>

Ngăn xếp (stack): thao tác vừa làm xong là thao tác được hoàn tác đầu tiên, nên kiểu LIFO hợp với hoàn tác và làm lại.
Các lệnh in được nguồn gắn với hàng đợi (queue), thường theo thứ tự FIFO: lệnh gửi trước được xử lý trước.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và danh sách mười một mục theo một thứ tự phẳng, mỗi mục một ví dụ. Bài này giữ tên cấu trúc và ví dụ, vì đó là dữ kiện của danh sách, nhưng phần giải thích mỗi cấu trúc là gì được viết lại từ tài liệu JDK, MDN và WebGL nên không lặp câu chữ của nguồn. Hình giữ cả mười một mục, chia thành ba nhóm theo họ hàng; cách chia nhóm là của bài. Bài không dùng ảnh nguồn.
Các mô tả lấy từ mã nguồn JDK (`List`, `Deque`, `Queue`, `PriorityQueue`, `HashSet`) và bảng thuật ngữ cùng trang `WebGLBuffer` của MDN tại commit cố định ở mục nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/10-key-data-structures-we-use-every-day.md): chỉ lấy tên mười một cấu trúc và ví dụ đi kèm.
- OpenJDK: [List](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/List.java), [Deque](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Deque.java), [Queue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Queue.java), [PriorityQueue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/PriorityQueue.java) và [HashSet](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/HashSet.java): danh sách, ngăn xếp, hàng đợi, đống ưu tiên, bảng băm. Đọc từ kho mã.
- MDN: [Array](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/array/index.md), [DOM](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/dom/index.md), [GPU](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/gpu/index.md) và [WebGLBuffer](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/api/webglbuffer/index.md): mảng, cây DOM, GPU, vertex buffer. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Cây hậu tố, đồ thị, R-tree và các câu giải nghĩa viết tắt trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

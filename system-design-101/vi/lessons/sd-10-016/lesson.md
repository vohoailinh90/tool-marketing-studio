# Mười một cấu trúc dữ liệu dùng hằng ngày

**Mỗi cấu trúc dữ liệu thường gắn với một việc quen thuộc: ngăn xếp cho hoàn tác, hàng đợi cho lệnh in, bảng băm cho bộ nhớ đệm, đồ thị cho quan hệ bạn bè.**
Tiêu đề nguồn nói "10 cấu trúc" nhưng danh sách có mười một; bài này đếm lại và theo danh sách, rồi đối chiếu bốn cấu trúc đầu với thư viện chuẩn của Java.

![Ba nhóm thẻ và một khung ghi nhớ. Danh sách và thứ tự: danh sách giữ dòng tin, mảng cho phép toán số học, ngăn xếp cho hoàn tác và làm lại, hàng đợi cho lệnh in hoặc thao tác trong game. Tra cứu và sắp việc: bảng băm cho bộ nhớ đệm, đống cho lập lịch tác vụ, cây giữ tài liệu HTML hoặc quyết định của AI, cây hậu tố để tìm chuỗi trong tài liệu. Quan hệ, không gian và đồ họa: đồ thị cho quan hệ bạn bè hoặc tìm đường, R-tree tìm hàng xóm gần nhất, vertex buffer gửi dữ liệu tới GPU để vẽ. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-016-main.svg)

## Từ viết tắt

- **HTML** (HyperText Markup Language) — ngôn ngữ đánh dấu siêu văn bản: văn bản dùng thẻ để mô tả cấu trúc của một trang web; trang đó được giữ trong bộ nhớ dưới dạng cây.
- **AI** (Artificial Intelligence) — trí tuệ nhân tạo: các hệ thống máy tính làm những việc thường cần trí thông minh của con người; ở đây là chương trình ra quyết định.
- **GPU** (Graphics Processing Unit) — bộ xử lý đồ họa: chip chuyên vẽ hình; vertex buffer là cách đưa dữ liệu điểm vẽ tới chip này.
- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; bài trích mã nguồn của nó để đối chiếu.
- **LIFO** (Last In, First Out) — vào sau, ra trước: phần tử thêm vào sau cùng là phần tử lấy ra đầu tiên, đúng kiểu của ngăn xếp.

## Đọc hình

**Danh sách và thứ tự.**
- Danh sách (List): giữ dòng tin trên mạng xã hội; nguồn lấy ví dụ Twitter.
- Mảng (Array): dùng cho các phép toán số học.
- Ngăn xếp (Stack): hỗ trợ hoàn tác và làm lại (undo/redo) trong trình soạn văn bản.
- Hàng đợi (Queue): giữ các lệnh in, hoặc gửi các thao tác người chơi trong game.

**Tra cứu và sắp việc.**
- Bảng băm (Hash table): dùng trong các hệ thống bộ nhớ đệm (cache).
- Đống (Heap): dùng để lập lịch tác vụ.
- Cây (Tree): giữ tài liệu HTML, hoặc dùng cho quyết định của AI.
- Cây hậu tố (Suffix tree): để tìm một chuỗi trong tài liệu.

**Quan hệ, không gian và đồ họa.**
- Đồ thị (Graph): theo dõi quan hệ bạn bè, hoặc tìm đường.
- R-tree: để tìm hàng xóm gần nhất.
- Vertex buffer: để gửi dữ liệu tới GPU nhằm vẽ.

**Gặp lại trong thư viện Java.** Tài liệu của JDK nói `Deque` có thể dùng như ngăn xếp LIFO và nên dùng thay lớp `Stack` cũ; `Queue` thường xếp phần tử theo thứ tự vào trước ra trước; `PriorityQueue` là hàng đợi ưu tiên dựa trên một đống ưu tiên (priority heap); `HashSet` dựa trên một bảng băm. Như vậy bốn cấu trúc ngăn xếp, hàng đợi, đống và bảng băm đều có sẵn trong thư viện chuẩn.

## Giới hạn cần nhớ

Nguồn chỉ nêu một việc mỗi cấu trúc, không giải thích chúng hoạt động ra sao và không nói khi nào dùng cấu trúc nào; ví dụ chỉ là minh họa, không phải mô tả cách các ứng dụng đó thật sự được xây.
Tiêu đề nguồn nói mười cấu trúc nhưng danh sách có mười một mục (List, Stack, Queue, Hash Table, Array, Heap, Tree, Suffix Tree, Graph, R-Tree, Vertex Buffer); bài theo danh sách. Ví dụ thư viện Java chỉ là vài trường hợp đã đối chiếu, không phải danh sách đầy đủ, và các ngôn ngữ khác có thể đặt tên khác.

## Nhìn hình trả lời

Bạn gõ chữ trong một trình soạn văn bản, bấm hoàn tác ba lần rồi làm lại một lần. Nguồn gắn việc này với cấu trúc nào, và vì sao kiểu "vào sau, ra trước" hợp với nó? Còn nhiều lệnh in gửi tới một máy in thì nguồn gắn với cấu trúc nào?

<details>
<summary>Xem đáp án</summary>

Ngăn xếp (stack): thao tác vừa làm xong là thao tác được hoàn tác đầu tiên, nên kiểu LIFO hợp với hoàn tác và làm lại.
Các lệnh in được nguồn gắn với hàng đợi (queue).

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và danh sách mười một mục theo một thứ tự phẳng, mỗi mục một ví dụ. Hình ở đây giữ cả mười một mục và chia chúng thành ba nhóm theo họ hàng; cách chia nhóm là của bài, không phải của nguồn. Bài không dùng ảnh nguồn.
Mục "Gặp lại trong thư viện Java" lấy từ mã nguồn JDK tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/10-key-data-structures-we-use-every-day.md): danh sách cấu trúc và việc gắn với từng cấu trúc.
- [OpenJDK — Deque](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Deque.java), [Queue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Queue.java), [PriorityQueue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/PriorityQueue.java) và [HashSet](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/HashSet.java): ngăn xếp, hàng đợi, đống ưu tiên, bảng băm. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa viết tắt trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

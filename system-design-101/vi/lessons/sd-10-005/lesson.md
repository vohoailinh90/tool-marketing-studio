# Cây phân cấp Java Collection

**Đọc cây Collection như một bộ hợp đồng: mỗi interface hứa một điều khác nhau về vị trí, về trùng lặp và về thứ tự lấy phần tử ra.**
Nắm ba lời hứa đó giúp chọn đúng kiểu trước khi nghĩ tới tên lớp cụ thể.

![Ba nhóm thẻ xếp dọc. Phần gốc: Iterable hứa duyệt lần lượt từng phần tử, nên dùng được trong vòng lặp for nâng cao, và Collection là hợp đồng chung cho một nhóm phần tử, kế thừa Iterable. Ba hợp đồng con của Collection: List cho phần tử một vị trí và đọc theo chỉ số, ví dụ ArrayList và LinkedList; Set cấm hai phần tử bằng nhau theo equals, ví dụ HashSet và TreeSet; Queue giữ phần tử chờ xử lý và mỗi thao tác có hai dạng, ví dụ PriorityQueue và ArrayDeque. Khung cuối nhắc rằng Map là hợp đồng riêng ngoài cây, thứ tự lấy ra do từng lớp quy định, và hình là bản rút gọn.](../../diagrams/sd-10-005-main.svg)

## Từ viết tắt

- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; thư viện tập hợp nằm trong gói này.

## Đọc hình

**Gốc chung.** `Iterable` chỉ hứa một điều: có thể đi qua từng phần tử, nên đối tượng nào cài đặt nó thì dùng được trong vòng lặp `for` nâng cao. `Collection` đứng trên đó và là hợp đồng chung cho "một nhóm đối tượng". Tài liệu JDK nói thẳng rằng nhóm này có thể có hoặc không có phần tử trùng, có hoặc không có thứ tự. Tài liệu cũng nói JDK không cung cấp cài đặt trực tiếp nào của `Collection`, chỉ cài đặt của các interface con cụ thể hơn như `Set` và `List`; ý này nói về các lớp cụ thể, vì lớp khung trừu tượng `AbstractCollection` vẫn khai báo cài đặt `Collection` để các lớp khác kế thừa. Vì vậy `Collection` hay xuất hiện ở tham số hoặc kiểu trả về khi hàm chỉ cần "một nhóm phần tử nào đó" và không quan tâm hình dạng.

**Ba hợp đồng con.**
- `List` hứa cho mỗi phần tử một vị trí. Người dùng quyết định chèn ở đâu và đọc lại bằng chỉ số tính từ 0. Tài liệu viết rằng danh sách thường cho phép phần tử trùng. Lớp hay gặp: `ArrayList`, `LinkedList`.
- `Set` mô hình hóa tập hợp trong toán học: không có hai phần tử `e1`, `e2` nào mà `e1.equals(e2)` đúng. "Trùng" ở đây nghĩa là bằng nhau theo `equals`, không phải cùng một đối tượng. Lớp hay gặp: `HashSet`, `TreeSet`.
- `Queue` hứa giữ phần tử trong lúc chờ được xử lý. Mỗi việc chèn, lấy ra và xem phần tử ở đầu đều có hai dạng: một dạng ném ngoại lệ khi không làm được, dạng kia trả giá trị đặc biệt (`false` hoặc `null`). Với việc chèn, dạng thứ hai sinh ra cho hàng đợi có giới hạn sức chứa, nơi "đầy" là chuyện bình thường. Lớp hay gặp: `PriorityQueue`, `ArrayDeque`.

**Ngoài cây.** `Map` là hợp đồng riêng: ánh xạ khóa sang giá trị, mỗi khóa trỏ tới nhiều nhất một giá trị và không có khóa trùng. Nó không kế thừa `Collection`, nhưng cho nhìn nội dung của mình dưới ba dạng tập hợp: tập khóa, nhóm giá trị và tập cặp khóa–giá trị.

**Từ hợp đồng đến lớp cụ thể.** Chọn xong interface mới đến chọn lớp, và tài liệu của từng lớp nói điều mà interface bỏ ngỏ:
- `ArrayList` lưu bằng mảng co giãn, đọc theo chỉ số tốn thời gian hằng số. `LinkedList` là danh sách liên kết đôi, cài đặt cả `List` lẫn `Deque`; truy cập theo chỉ số phải đi từ đầu hoặc từ cuối tới vị trí cần.
- `HashSet` dựa trên bảng băm, không đảm bảo thứ tự lặp và thứ tự đó có thể đổi theo thời gian. `TreeSet` giữ phần tử theo thứ tự tự nhiên hoặc theo `Comparator` đưa vào lúc tạo.
- `PriorityQueue` không lấy theo thứ tự vào: phần tử ở đầu là phần tử nhỏ nhất theo thứ tự đã chọn. `ArrayDeque` là hàng đợi hai đầu bằng mảng co giãn; tài liệu nói nó nhiều khả năng nhanh hơn `LinkedList` khi dùng làm hàng đợi.

## Giới hạn cần nhớ

- Thứ tự lấy ra do từng lớp quyết định. `Queue` thường, nhưng không nhất thiết, lấy theo thứ tự vào trước ra trước: `PriorityQueue` lấy theo ưu tiên, còn kiểu ngăn xếp lấy phần tử vào sau cùng trước. Tài liệu yêu cầu mỗi cài đặt phải nêu rõ thứ tự của mình, nên cần đọc tài liệu của lớp, không chỉ tên interface.
- Đọc theo chỉ số trên một `List` không rõ cài đặt có thể tốn thời gian tỷ lệ với chỉ số. Nếu chỉ cần đi qua mọi phần tử thì nên lặp thay vì lấy từng chỉ số.
- Với `Set`, đừng sửa một phần tử theo cách làm đổi kết quả `equals` khi nó đang nằm trong tập: tài liệu nói hành vi khi đó không được xác định.
- Thêm và xóa là thao tác tùy chọn của `Collection`. Danh sách không sửa được, như kết quả của `List.of(...)`, ném `UnsupportedOperationException` khi bị thêm hoặc xóa.
- Hình là bản rút gọn. Trong mã nguồn JDK này, `List` kế thừa `Collection` qua một interface trung gian tên `SequencedCollection`, và `Deque` nằm giữa `Queue` và `ArrayDeque`; hình bỏ những tầng đó để thấy ba hợp đồng chính.

## Nhìn hình trả lời

Một dịch vụ cần ba thứ: (1) danh sách mã khách đã xử lý, không mã nào xuất hiện hai lần; (2) các việc đang chờ, mỗi lần lấy ra việc gấp nhất; (3) bảng tra "mã khách → số lần đã xử lý". Mỗi thứ nên nằm ở nhánh nào của cây?

<details>
<summary>Xem đáp án</summary>

(1) Nhánh `Set`, vì hợp đồng của nó là không có hai phần tử bằng nhau theo `equals`; `HashSet` là lớp hay gặp.
(2) Nhánh `Queue`, cụ thể `PriorityQueue`, vì đầu hàng là phần tử nhỏ nhất theo thứ tự ưu tiên chứ không phải phần tử vào trước.
(3) `Map`, vì đây là quan hệ khóa trỏ tới giá trị, và `Map` nằm ngoài cây `Collection`.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn chỉ có vài câu mô tả khung tập hợp và một ảnh cây phân cấp; bài này không dùng ảnh và không theo cách trình bày đó. Từ bài nguồn chỉ giữ tên các interface và lớp.
Lời giải thích viết lại từ phần chú thích của các tệp JDK ở commit cố định: `Collection` nói gì về trùng lặp, thứ tự và thao tác tùy chọn; `List` về vị trí và chỉ số; `Set` về `equals`; `Queue` về hai dạng thao tác; `Map` về khóa. Phần "Từ hợp đồng đến lớp cụ thể" lấy từ chú thích của chính các lớp `ArrayList`, `LinkedList`, `HashSet`, `TreeSet`, `PriorityQueue`, `ArrayDeque`.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/java-collection-hierarchy.md): chỉ dùng để lấy tên các interface và lớp.
- [OpenJDK — interface Collection](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Collection.java), [List](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/List.java), [Set](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Set.java), [Queue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Queue.java) và [Map](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Map.java): lời hứa của từng interface. Đọc từ kho mã.
- [OpenJDK — ArrayList](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/ArrayList.java), [LinkedList](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/LinkedList.java), [HashSet](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/HashSet.java), [TreeSet](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/TreeSet.java), [PriorityQueue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/PriorityQueue.java) và [ArrayDeque](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/ArrayDeque.java): đặc điểm của lớp cụ thể.

Đã đọc nguồn ngày 2026-10-19. Mọi mô tả hợp đồng và đặc điểm lớp lấy từ phần chú thích của các tệp JDK nêu trên; câu hỏi cuối bài là ví dụ tự đặt.
Bài viết và hình được thiết kế độc lập.

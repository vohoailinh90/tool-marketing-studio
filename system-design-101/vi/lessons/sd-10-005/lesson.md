# Cây phân cấp Java Collection

**Các kiểu tập hợp trong Java cùng xuất phát từ interface `Collection`, rồi tách thành ba nhánh chính: List, Set và Queue.**
Nắm cây này giúp chọn đúng cấu trúc dữ liệu cho từng bài toán thay vì dùng một kiểu cho mọi việc.

![Ba nhóm thẻ xếp dọc. Phần gốc: Iterable cho phép duyệt từng phần tử, kể cả bằng vòng lặp for nâng cao, và Collection kế thừa nó, khai báo các thao tác cơ bản thêm, xóa và hỏi phần tử, trong đó thêm và xóa là thao tác tùy chọn. Ba nhánh chính của Collection: List có thứ tự theo vị trí và cho phép trùng, ví dụ ArrayList và LinkedList; Set không chứa phần tử trùng, ví dụ HashSet và TreeSet; Queue giữ phần tử chờ xử lý, ví dụ PriorityQueue và ArrayDeque. Khung cuối nhắc rằng Map nằm ngoài cây Collection.](../../diagrams/sd-10-005-main.svg)

## Từ viết tắt

- **JCF** (Java Collections Framework) — khung tập hợp của Java: bộ interface và lớp có sẵn để lưu và xử lý nhóm phần tử.
- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java.

## Đọc hình

**Gốc.** JCF dựng trên một tập interface, mỗi interface định nghĩa các thao tác cơ bản của một kiểu cấu trúc dữ liệu phổ biến như danh sách, tập hợp và ánh xạ. Mỗi cấu trúc có một số lớp cụ thể cài đặt nó, với tính năng riêng.
`Collection` là interface gốc của các tập hợp: nó khai báo các thao tác cơ bản như thêm, xóa và hỏi phần tử. Với thêm và xóa, tài liệu của JDK gọi đó là thao tác tùy chọn (optional): một lớp không hỗ trợ thì ném `UnsupportedOperationException`, như các tập hợp không sửa được. Nó kế thừa `Iterable`, nên có thể duyệt từng phần tử bằng vòng lặp for nâng cao hoặc bằng iterator.

**Ba nhánh.** `Collection` có ba interface con chính, mỗi interface có đặc điểm và cách dùng riêng:
- `List`: có thứ tự theo vị trí và cho phép phần tử trùng. Lớp cài đặt thường gặp: `ArrayList`, `LinkedList`.
- `Set`: không chứa phần tử trùng. Lớp cài đặt thường gặp: `HashSet`, `TreeSet`.
- `Queue`: giữ phần tử chờ xử lý. Lớp cài đặt thường gặp: `PriorityQueue`, `ArrayDeque`.

**Ngoài cây.** `Map` cũng thuộc JCF nhưng không kế thừa `Collection`; nó là một họ interface riêng.

## Giới hạn cần nhớ

`Queue` thường, nhưng không nhất thiết, lấy phần tử theo thứ tự vào trước ra trước; `PriorityQueue` lấy theo thứ tự ưu tiên. Vì vậy phải đọc tài liệu của lớp cụ thể chứ không chỉ nhìn tên interface.
Tương tự, thêm và xóa phần tử là thao tác tùy chọn của `Collection`: một tập hợp không sửa được, như kết quả của `List.of(...)`, sẽ ném `UnsupportedOperationException` khi bị thêm hoặc xóa.
Hình là bản rút gọn. Trong mã nguồn của JDK hiện tại, `List` không kế thừa trực tiếp `Collection` mà qua một interface trung gian tên `SequencedCollection`, và các lớp cụ thể có thêm nhiều interface khác; hình bỏ những tầng đó để thấy ba nhánh chính của bài nguồn.

## Nhìn hình trả lời

Bạn cần lưu danh sách mã đơn hàng đã xử lý và không bao giờ muốn một mã xuất hiện hai lần. Bạn chọn nhánh nào của cây, và một kiểu dữ liệu tên `Map` có phải lựa chọn tự nhiên không?

<details>
<summary>Xem đáp án</summary>

Nhánh `Set`, vì nó không chứa phần tử trùng; `HashSet` là một lớp cài đặt thường gặp.
`Map` lưu cặp khóa và giá trị chứ không phải một nhóm phần tử đơn, và nó nằm ngoài cây `Collection`; với bài toán chỉ cần biết một mã đã có hay chưa, `Set` khớp hơn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn chỉ có văn bản mô tả JCF và một ảnh cây phân cấp. Bài này không dùng ảnh; hình được vẽ lại từ các câu của nguồn.
Tên các lớp cài đặt, quan hệ kế thừa của `Collection`, `List`, `Set`, `Queue`, `Map` và các lớp đã nêu được đối chiếu với mã nguồn của JDK tại commit cố định ở mục nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/java-collection-hierarchy.md): JCF, interface `Collection`, ba interface con chính.
- [OpenJDK — interface Collection](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Collection.java), [List](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/List.java), [Set](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Set.java), [Queue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Queue.java) và [Map](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Map.java): khai báo và mô tả. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các lớp cài đặt thường gặp được kiểm trên khai báo trong mã nguồn JDK; mô tả thứ tự và trùng lặp của `List`, `Set`, `Queue` lấy từ phần chú thích của chính các tệp đó.
Bài viết và hình được thiết kế độc lập.

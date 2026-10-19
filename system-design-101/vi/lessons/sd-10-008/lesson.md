# Sáu mẫu thiết kế đa luồng cần biết

**Nhiều luồng chạy cùng lúc dùng chung bộ nhớ nên sinh ra nhu cầu đồng bộ và giao tiếp; sáu mẫu thiết kế dưới đây là cách làm quen thuộc cho từng nhu cầu.**
Bài nguồn chỉ nêu tên sáu mẫu; bài này giữ đúng sáu tên đó, chia thành hai nhóm (chia việc và lấy kết quả, bảo vệ và đồng bộ) và giải thích từng mẫu từ tài liệu của Python và của JDK.

![Ba nhóm thẻ xếp dọc. Chia việc và lấy kết quả: Producer-Consumer là một bên tạo việc, một bên nhận việc, qua một hàng đợi có khóa sẵn; Thread pool là một nhóm luồng lập sẵn nhận việc thay vì mỗi việc một luồng mới; Futures và Promises, trong đó future đại diện cho kết quả của việc đang chạy và được hỏi lấy sau. Bảo vệ và đồng bộ: Monitor object cho mỗi lúc chỉ một luồng sở hữu monitor của đối tượng; Barrier cho một số luồng cố định chờ nhau rồi thả cùng lúc; Read-write lock cho nhiều luồng đọc cùng lúc nếu không có luồng ghi, còn ghi là độc quyền. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-008-main.svg)

## Từ viết tắt

- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; bài trích mã nguồn của nó để đối chiếu.

## Đọc hình

Hình chia sáu mẫu thành hai nhóm; cả cách chia lẫn lời giải thích dưới đây là của người biên soạn, dựa vào tài liệu của Python và của JDK. Chỉ có tên sáu mẫu là của bài nguồn.

**Nền.** Các luồng (thread) trong cùng một tiến trình dùng chung vùng nhớ, nên hai luồng có thể đụng vào cùng một dữ liệu cùng lúc. Khi đó kết quả có thể phụ thuộc vào thứ tự các luồng chạy, gọi là race condition (kiến thức chung của người biên soạn). Sáu mẫu dưới đây là sáu cách tổ chức công việc để tránh hoặc kiểm soát tình trạng đó.

**Nhóm 1 · Chia việc và lấy kết quả.**
- Producer-Consumer: một bên tạo việc, một bên nhận việc, hai bên nói chuyện qua một hàng đợi. Tài liệu mô-đun `queue` của Python gọi đó là hàng đợi nhiều producer, nhiều consumer, nói nó đặc biệt hữu ích khi thông tin phải được trao đổi an toàn giữa nhiều luồng, và cho biết lớp `Queue` đã làm sẵn mọi ngữ nghĩa khóa cần thiết, nên người dùng không phải tự viết khóa.
- Thread pool: thay vì mỗi việc một luồng mới, một nhóm luồng lập sẵn nhận việc. Tài liệu `concurrent.futures` mô tả `ThreadPoolExecutor` là bộ thực thi dùng một nhóm tối đa `max_workers` luồng để chạy các lời gọi bất đồng bộ, thường dùng để chồng thời gian chờ đọc ghi dữ liệu lên nhau thay vì để làm việc nặng tính toán, và khuyên không dùng nó cho việc chạy rất lâu.
- Futures và Promises: future là đối tượng đại diện cho kết quả của một việc đang chạy bất đồng bộ. Theo tài liệu `concurrent.futures`, lớp `Future` gói việc thực thi bất đồng bộ của một lời gọi và do `Executor.submit` tạo ra; người gọi nhận future ngay rồi hỏi kết quả sau. Phần "promise", bên hứa giao kết quả, là cách gọi ở ngôn ngữ khác (kiến thức chung của người biên soạn).

**Nhóm 2 · Bảo vệ và đồng bộ.**
- Monitor object: mỗi đối tượng Java có một monitor, và theo tài liệu của lớp `Object`, mỗi lúc chỉ một luồng sở hữu monitor của một đối tượng. Luồng có quyền đó khi chạy một phương thức `synchronized` của đối tượng, khi chạy thân một câu lệnh `synchronized` trên đối tượng, hoặc, với đối tượng kiểu `Class`, khi chạy một phương thức tĩnh `synchronized`.
- Barrier: lớp `threading.Barrier` của Python là một cơ chế đồng bộ cho một số luồng cố định cần chờ nhau. Mỗi luồng gọi `wait` và bị chặn cho tới khi mọi luồng đã gọi `wait`, rồi các luồng được thả cùng lúc; rào dùng lại được nhiều lần cho cùng số luồng.
- Read-write lock: theo tài liệu của `ReadWriteLock` trong JDK, nó giữ một cặp khóa liên kết, một cho thao tác chỉ đọc và một cho ghi. Khóa đọc có thể được nhiều luồng đọc giữ cùng lúc miễn không có luồng ghi; khóa ghi là độc quyền. Mọi cài đặt phải bảo đảm luồng lấy được khóa đọc thấy các cập nhật trước khi khóa ghi được nhả.

## Giới hạn cần nhớ

Phần giải thích mô tả cách các thư viện của Python và JDK làm, không phải định nghĩa chung của từng mẫu; một ngôn ngữ khác có thể làm khác, và tên lớp ở mỗi ngôn ngữ cũng khác nhau.
Bài không so sánh chi phí giữa các mẫu, không nói khi nào mẫu này hơn mẫu kia và không có mã.

## Nhìn hình trả lời

Một dịch vụ nhận rất nhiều yêu cầu ngắn. Tạo một luồng mới cho từng yêu cầu rồi hủy đi tốn kém. Mẫu nào trong sáu mẫu giải quyết việc này, và nó làm thế nào?

<details>
<summary>Xem đáp án</summary>

Thread pool. Một nhóm luồng được lập sẵn và nhận việc, nên không phải tạo một luồng mới cho từng yêu cầu rồi hủy đi. Tài liệu Python nói bộ thực thi này hợp để chồng các việc có thời gian chờ lên nhau, và khuyên không dùng cho việc chạy rất lâu, nên nó khớp với nhiều yêu cầu ngắn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn nêu sáu mẫu theo thứ tự Producer-Consumer, Thread pool, Futures và Promises, Monitor object, Barrier, Read-write lock, mỗi mẫu một câu mô tả ngắn. Bài này chỉ giữ tên sáu mẫu; không dịch hay diễn đạt lại các câu mô tả đó mà giải thích từng mẫu từ tài liệu mô-đun `queue`, `concurrent.futures` và `threading` của Python, lớp `Object` và `ReadWriteLock` của JDK (tại các commit cố định ở mục nguồn), còn phần nền và phần nói về "promise" là kiến thức chung của người biên soạn.
Hình chia sáu mẫu thành hai nhóm theo việc chúng làm. Bài không dùng ảnh của nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-multithreading-design-patterns-you-must-know.md): tên sáu mẫu thiết kế.
- [Python — mô-đun queue](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/queue.rst), [concurrent.futures](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/concurrent.futures.rst) và [threading](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/threading.rst): hàng đợi nhiều producer và consumer, nhóm luồng, Future, Barrier. Đọc từ kho mã.
- [OpenJDK — lớp Object](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/lang/Object.java): monitor của đối tượng. Đọc từ kho mã.
- [OpenJDK — ReadWriteLock](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/locks/ReadWriteLock.java): khóa đọc dùng chung, khóa ghi độc quyền. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Phần nền về race condition và về "promise" là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

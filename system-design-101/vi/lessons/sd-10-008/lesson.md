# Sáu mẫu thiết kế đa luồng cần biết

**Nhiều luồng chạy cùng lúc dùng chung bộ nhớ nên sinh ra nhu cầu đồng bộ và giao tiếp; sáu mẫu thiết kế dưới đây là cách làm quen thuộc cho từng nhu cầu.**
Bài nguồn nêu sáu mẫu; bài này chia chúng thành hai nhóm: chia việc và lấy kết quả, bảo vệ và đồng bộ.

![Ba nhóm thẻ xếp dọc. Chia việc và lấy kết quả: Producer-Consumer có luồng sản xuất dữ liệu và luồng xử lý, đệm bằng hàng đợi chặn; Thread pool giữ một nhóm luồng làm việc tái sử dụng để khỏi tạo và hủy luồng; Futures và Promises, promise giữ kết quả sẽ có và future cho phép lấy kết quả, không chặn luồng chính. Bảo vệ và đồng bộ: Monitor object cho mỗi lúc chỉ một luồng truy cập tài nguyên chia sẻ; Barrier bắt một nhóm luồng chờ nhau tới cùng một điểm; Read-write lock cho nhiều luồng đọc nhưng chỉ một luồng ghi. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-008-main.svg)

## Từ viết tắt

- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; bài trích mã nguồn của nó để đối chiếu.

## Đọc hình

**Nền.** Đa luồng cho một chương trình làm nhiều việc đồng thời: mỗi việc là một luồng (thread), một đơn vị thực thi nhẹ chia sẻ tài nguyên của tiến trình như vùng nhớ. Cái giá là sự phức tạp: đồng bộ, giao tiếp giữa các luồng và nguy cơ race condition (kết quả phụ thuộc vào thứ tự các luồng chạy). Các mẫu thiết kế sinh ra để xử lý những việc đó.

**Nhóm 1 · Chia việc và lấy kết quả.**
- Producer-Consumer: có hai loại luồng, luồng sản xuất tạo dữ liệu và luồng tiêu thụ xử lý dữ liệu; một hàng đợi chặn làm bộ đệm giữa hai bên.
- Thread pool: một nhóm luồng làm việc được tái sử dụng để chạy tác vụ, nên khỏi tốn chi phí tạo và hủy luồng. Hợp với nhiều tác vụ ngắn.
- Futures và Promises: promise là đối tượng giữ kết quả sẽ có, future là cách truy cập kết quả đó. Hợp để chạy việc dài đồng thời mà không chặn luồng chính.

**Nhóm 2 · Bảo vệ và đồng bộ.**
- Monitor object: bảo đảm mỗi lúc chỉ một luồng được truy cập hoặc sửa tài nguyên chia sẻ trong một đối tượng, để tránh race condition. Cần khi phải bảo vệ dữ liệu khỏi truy cập đồng thời.
- Barrier: đồng bộ một nhóm luồng. Mỗi luồng chạy tới điểm rào rồi chặn cho tới khi mọi luồng cùng tới. Hợp cho các tác vụ song song phải tới một giai đoạn trước khi sang giai đoạn kế.
- Read-write lock: cho nhiều luồng cùng đọc một tài nguyên chia sẻ nhưng chỉ cho một luồng ghi tại một thời điểm. Hợp khi việc đọc nhiều hơn việc ghi.

**Gặp lại trong thư viện chuẩn.** Một số mẫu có sẵn thành lớp: `queue.Queue` của Python là hàng đợi nhiều producer, nhiều consumer với khóa đã làm sẵn; `ThreadPoolExecutor` dùng một nhóm luồng để chạy lời gọi bất đồng bộ; `Future` đóng gói việc thực thi bất đồng bộ; `threading.Barrier` chặn các luồng cho tới khi đủ số luồng cùng gọi `wait`, rồi thả cùng lúc. `ReadWriteLock` của Java cho phép nhiều luồng đọc giữ khóa đọc cùng lúc khi không có luồng ghi, còn khóa ghi là độc quyền.

## Giới hạn cần nhớ

Bài nguồn chỉ mô tả ý tưởng của sáu mẫu; không có mã, không so sánh chi phí và không nói khi nào mẫu này hơn mẫu kia.
Ví dụ thư viện chuẩn ở trên chỉ là vài trường hợp đã đối chiếu, không phải danh sách đầy đủ; tên lớp ở mỗi ngôn ngữ cũng khác nhau, và bài không nói ngôn ngữ nào có sẵn mẫu nào ngoài các ví dụ đó.

## Nhìn hình trả lời

Một dịch vụ nhận rất nhiều yêu cầu ngắn. Tạo một luồng mới cho từng yêu cầu rồi hủy đi tốn kém. Mẫu nào trong sáu mẫu giải quyết việc này, và nó làm thế nào?

<details>
<summary>Xem đáp án</summary>

Thread pool. Nó giữ một nhóm luồng làm việc để tái sử dụng chạy tác vụ, nên không phải tạo và hủy luồng liên tục. Nguồn nói mẫu này hợp với việc chạy nhiều tác vụ ngắn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn nêu sáu mẫu theo thứ tự Producer-Consumer, Thread pool, Futures và Promises, Monitor object, Barrier, Read-write lock, kèm một đoạn dẫn vào về đa luồng. Hình giữ cả sáu mẫu và chia chúng thành hai nhóm theo việc chúng làm.
Phần "Gặp lại trong thư viện chuẩn" lấy từ tài liệu Python và mã nguồn JDK tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-multithreading-design-patterns-you-must-know.md): đa luồng và sáu mẫu thiết kế.
- [Python — mô-đun queue](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/queue.rst), [concurrent.futures](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/concurrent.futures.rst) và [threading](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/threading.rst): hàng đợi nhiều producer và consumer, nhóm luồng, Future, Barrier. Đọc từ kho mã.
- [OpenJDK — ReadWriteLock](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/locks/ReadWriteLock.java): khóa đọc dùng chung, khóa ghi độc quyền. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Mô tả sáu mẫu là của bài nguồn; các ví dụ thư viện chuẩn đã đối chiếu với tài liệu và mã nguồn ở trên.
Bài viết và hình được thiết kế độc lập.

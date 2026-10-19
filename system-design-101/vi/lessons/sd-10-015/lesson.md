# C++, Java và Python chạy như thế nào?

**Ba cách chạy một chương trình: biên dịch ra mã máy rồi bộ xử lý chạy thẳng; biên dịch ra bytecode rồi máy ảo chạy; hoặc để trình thông dịch chạy chương trình từ mã nguồn.**
Bài giữ ba nhóm và các ngôn ngữ ví dụ của bài nguồn, rồi giải thích từng nhóm bằng tài liệu của Python, của OpenJDK (bộ phát triển Java) và của MDN, kèm chỗ ranh giới giữa các nhóm mờ đi.

![Ba nhóm xếp dọc. Ngôn ngữ biên dịch như C, C++, Go, hai bước: biên dịch trước, chương trình thành mã máy trước khi chạy; bộ xử lý thực thi thẳng mã máy. Ngôn ngữ bytecode như Java, C#, ba bước: biên dịch mã nguồn thành bytecode, dạng trung gian; máy ảo JVM nạp và chạy bytecode; tùy chọn, trình JIT biến đoạn chạy nhiều thành mã máy lúc chạy. Ngôn ngữ thông dịch như Python, JavaScript, Ruby, hai bước: chạy thẳng mã nguồn, không tạo tệp chạy được riêng; trình thông dịch đọc và chạy chương trình khi cần. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-015-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần cứng chạy mã máy, tức các lệnh ở dạng máy hiểu được.
- **JVM** (Java Virtual Machine) — máy ảo Java: chương trình chạy bytecode của Java.
- **JIT** (Just-In-Time) — biên dịch đúng lúc: dịch đoạn mã sang mã máy ngay trong lúc chương trình đang chạy, thay vì trước khi chạy.
- **AOT** (Ahead-Of-Time) — biên dịch trước: dịch cả chương trình sang mã máy trước khi chạy; ngược với JIT.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

**Biên dịch (C, C++, Go).** Theo MDN, biên dịch là biến một chương trình viết bằng ngôn ngữ này thành các lệnh ở một dạng hoặc ngôn ngữ khác; chương trình làm việc đó là trình biên dịch. Thường thì đích là mã máy, tức mã chạy được. Phần lớn trình biên dịch làm theo kiểu biên dịch trước (AOT) hoặc kiểu đúng lúc (JIT); `gcc` là ví dụ quen thuộc của kiểu biên dịch trước, và người dùng gọi nó từ dòng lệnh hay từ môi trường phát triển. Mã máy sinh ra được bộ xử lý thực thi trực tiếp, không cần chương trình trung gian nào nữa.

**Bytecode (Java, C#).** Với Java, tài liệu lệnh `java` của OpenJDK nói lệnh này chạy một ứng dụng bằng cách khởi động máy ảo Java (JVM), nạp lớp chính của ứng dụng rồi gọi phương thức `main()` của lớp đó. Thứ máy ảo nạp là tệp lớp, tức mã đã biên dịch ra một dạng trung gian chứ chưa phải mã máy của một máy cụ thể. MDN mô tả trình JIT là bước dịch dạng trung gian như bytecode của Java sang mã máy ngay lúc chương trình chạy: trình JIT theo dõi những đoạn được chạy nhiều ("điểm nóng") và chỉ biên dịch chúng khi lợi ích nhanh hơn lớn hơn chi phí biên dịch. C# được giữ trong nhóm này theo danh sách của bài nguồn; bài không mô tả cách C# chạy.

**Thông dịch (Python, JavaScript, Ruby).** Tài liệu của Python gọi Python là ngôn ngữ thông dịch, đối lập với ngôn ngữ biên dịch: có thể chạy thẳng tệp mã nguồn mà không phải tự tạo trước một tệp thực thi. Cách này thường rút ngắn vòng viết, chạy, sửa lỗi, đổi lại chương trình nhìn chung chạy chậm hơn. JavaScript trong trình duyệt là ví dụ cho thấy ranh giới có thể mờ: MDN nói các trình duyệt lớn đều có bộ máy JavaScript với trình JIT tích hợp để tăng tốc.

**Chỗ ranh giới mờ.** Cũng theo tài liệu của Python, mã nguồn Python thực ra được biên dịch thành bytecode, một dạng nội bộ của trình thông dịch CPython, và bytecode được lưu tạm trong tệp `.pyc` để lần chạy sau nhanh hơn. Theo hiểu biết chung của người biên soạn (chưa đối chiếu), việc lưu này thường áp dụng cho các module được nạp bằng `import`, không áp dụng cho script chạy trực tiếp bằng `python tên_tệp.py`, và có thể bị tắt hoặc bị chặn vì quyền ghi tệp. Bytecode này chạy trên một máy ảo của Python. Chính tài liệu đó thừa nhận sự phân biệt biên dịch và thông dịch có thể mờ vì có bước biên dịch ra bytecode.

## Giới hạn cần nhớ

Ba nhóm là cách chia của bài nguồn, một sự đơn giản hóa. Cách chạy là chuyện của từng bản cài đặt cụ thể chứ không phải của ngôn ngữ; bài chỉ nói điều tài liệu Python, OpenJDK và MDN nói và không so sánh các bản cài đặt.
Bài không có số đo tốc độ, nên "chạy chậm hơn" chỉ là nhận định chung trong tài liệu Python. Tài liệu lệnh `java` mô tả cách khởi chạy và không bàn về JIT; phần JIT lấy từ MDN. Bài cũng không nói gì thêm về cách C# hay Ruby chạy.

## Nhìn hình trả lời

Một chương trình viết bằng Java được biên dịch thành bytecode. Ai nạp và chạy bytecode đó, và chuyện gì có thể xảy ra thêm để chạy nhanh hơn? Còn một chương trình Python thì sao: tài liệu Python nói nó chạy bằng cách nào, và vì sao ranh giới biên dịch và thông dịch mờ?

<details>
<summary>Xem đáp án</summary>

Máy ảo Java (JVM) nạp và chạy; trình JIT có thể dịch những đoạn chạy nhiều sang mã máy ngay lúc chạy để nhanh hơn.
Python chạy thẳng từ mã nguồn qua trình thông dịch, nhưng bên trong mã nguồn được biên dịch thành bytecode (có thể được lưu trong tệp `.pyc` khi là module được nạp) rồi chạy trên máy ảo của Python, nên ranh giới mờ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và ba đoạn về ba nhóm, kèm ví dụ ngôn ngữ và một câu so sánh tốc độ. Bài này giữ ba nhóm và các ví dụ, vì đó là danh sách; phần giải thích từng nhóm được viết lại từ bảng thuật ngữ của Python, tài liệu lệnh `java` của OpenJDK và hai trang thuật ngữ MDN (biên dịch, JIT) tại commit cố định ở mục nguồn, nên không lặp câu chữ của nguồn. Hình vẽ ba nhóm thành ba chuỗi bước và không dùng ảnh nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-c++-java-python-work.md): chỉ lấy ba nhóm và các ngôn ngữ ví dụ.
- [Python — bảng thuật ngữ](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/glossary.rst): mục bytecode (tệp `.pyc`), mục interpreted và mục virtual machine. Đọc từ kho mã.
- [OpenJDK — tài liệu lệnh java](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/man/java.md): lệnh `java` khởi động JVM, nạp lớp chính, gọi `main()`. Đọc từ kho mã.
- MDN: [Compile](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/compile/index.md) và [Just-In-Time Compilation](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/just_in_time_compilation/index.md): biên dịch trước và JIT, điểm nóng, trình duyệt. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Việc tệp lớp mà JVM nạp chứa bytecode và các câu giải nghĩa CPU, JVM và AOT trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

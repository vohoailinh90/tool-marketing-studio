# C++, Java và Python chạy như thế nào?

**Ba cách chạy một chương trình: biên dịch ra mã máy rồi CPU chạy thẳng; biên dịch ra bytecode rồi máy ảo chạy; hoặc để trình thông dịch chạy ngay lúc chạy.**
Bài nguồn phân ngôn ngữ thành ba nhóm theo cách chạy; bài này đọc từng nhóm rồi nói rõ ranh giới giữa các nhóm mờ ở đâu, đối chiếu với tài liệu của Python và MDN.

![Ba nhóm xếp dọc. Ngôn ngữ biên dịch như C, C++, Go, hai bước: trình biên dịch dịch mã nguồn thành mã máy; CPU chạy mã máy trực tiếp. Ngôn ngữ bytecode như Java, C#, ba bước: biên dịch mã nguồn thành bytecode; máy ảo JVM chạy chương trình từ bytecode; đôi khi trình JIT dịch ra mã máy để chạy nhanh hơn. Ngôn ngữ thông dịch như Python, JavaScript, Ruby, hai bước: không biên dịch trước, chương trình giữ nguyên mã nguồn; trình thông dịch chạy chương trình ngay lúc chạy. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-015-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần cứng chạy mã máy, tức các lệnh ở dạng máy hiểu được.
- **JVM** (Java Virtual Machine) — máy ảo Java: chương trình chạy bytecode của Java.
- **JIT** (Just-In-Time) — biên dịch đúng lúc: dịch đoạn mã sang mã máy ngay trong lúc chương trình đang chạy, thay vì trước khi chạy.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

**Biên dịch.** Ngôn ngữ biên dịch (compiled language) được trình biên dịch (compiler) dịch thành mã máy (machine code); sau đó CPU chạy mã máy trực tiếp. Ví dụ trong nguồn: C, C++, Go.

**Bytecode.** Ngôn ngữ như Java dịch mã nguồn thành bytecode trước, rồi JVM chạy chương trình. Đôi khi trình biên dịch JIT dịch sang mã máy để chạy nhanh hơn. Ví dụ trong nguồn: Java, C#.

**Thông dịch.** Ngôn ngữ thông dịch (interpreted language) không được biên dịch trước; trình thông dịch (interpreter) chạy chương trình ngay lúc chạy. Ví dụ trong nguồn: Python, JavaScript, Ruby.

**So sánh.** Nguồn kết luận: nhìn chung ngôn ngữ biên dịch chạy nhanh hơn ngôn ngữ thông dịch.

**Chỗ ranh giới mờ.** Tài liệu của Python nói mã nguồn Python được biên dịch thành bytecode, và bytecode được lưu tạm trong tệp `.pyc` để lần chạy sau nhanh hơn; cũng chính tài liệu đó gọi Python là ngôn ngữ thông dịch nhưng thừa nhận ranh giới có thể mờ vì có bước biên dịch ra bytecode. Tài liệu MDN nói JIT dịch mã (ví dụ JavaScript hoặc bytecode của Java) sang mã máy ngay lúc chạy, và thường được dùng trong trình duyệt hiện đại để làm JavaScript chạy nhanh hơn.

## Giới hạn cần nhớ

Ba nhóm là cách chia của nguồn, một sự đơn giản hóa. Một ngôn ngữ không tự nó "biên dịch" hay "thông dịch": cách chạy là chuyện của từng bản cài đặt cụ thể; bài này chỉ nói điều tài liệu Python và MDN nói, không so sánh các bản cài đặt.
Nguồn viết JIT biên dịch "mã nguồn" thành mã máy; theo MDN, JIT dịch từ dạng trung gian như bytecode hoặc từ ngôn ngữ cấp cao hơn. Nguồn gom Java và C# vào cùng nhóm bytecode và nhắc JVM; bài không nói gì thêm về cách C# chạy. Nguồn không cho số đo tốc độ, nên "nhanh hơn" chỉ là nhận định chung.

## Nhìn hình trả lời

Một chương trình viết bằng Java được biên dịch thành bytecode. Ai chạy bytecode đó, và chuyện gì có thể xảy ra thêm để chạy nhanh hơn? Còn một chương trình Python thì có gì khác trong nguồn, và tài liệu Python bổ sung điều gì?

<details>
<summary>Xem đáp án</summary>

JVM chạy bytecode; đôi khi trình JIT dịch sang mã máy ngay lúc chạy để nhanh hơn.
Nguồn xếp Python vào nhóm thông dịch: không biên dịch trước, trình thông dịch chạy lúc chạy. Tài liệu Python bổ sung rằng mã nguồn thực ra được biên dịch thành bytecode (lưu trong tệp `.pyc`), nên ranh giới giữa biên dịch và thông dịch có thể mờ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và ba đoạn về ba nhóm, kèm một câu so sánh tốc độ. Hình ở đây vẽ ba nhóm thành ba chuỗi bước và không dùng ảnh nguồn.
Mục "Chỗ ranh giới mờ" và hai điều chỉnh trong phần giới hạn lấy từ bảng thuật ngữ của Python và trang thuật ngữ JIT của MDN tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-c++-java-python-work.md): ba nhóm ngôn ngữ và cách chạy.
- [Python — bảng thuật ngữ](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/glossary.rst): mục bytecode (tệp `.pyc`) và mục interpreted. Đọc từ kho mã.
- [MDN — Just-In-Time Compilation](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/just_in_time_compilation/index.md): JIT dịch sang mã máy lúc chạy, thường dùng trong trình duyệt. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa CPU và JVM trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

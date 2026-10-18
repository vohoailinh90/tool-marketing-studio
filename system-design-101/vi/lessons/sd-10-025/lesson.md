# Đồng thời và song song: khác nhau ở đâu?

**Đồng thời (concurrency) là cách thiết kế chương trình để xử lý nhiều việc; song song (parallelism) là cách thực thi nhiều phép tính cùng một lúc. Cái đầu nói về cấu trúc, cái sau nói về phần cứng.**
Bài nguồn dựng quanh một câu nói và hai đoạn định nghĩa; bài này đọc từng ý rồi đối chiếu với tài liệu của Go và Python.

![Hai nhóm thẻ và một khung ghi nhớ. Đồng thời, nghĩa là dealing with nhiều việc cùng lúc, ba thẻ: chuyện thiết kế chương trình; các việc chạy chồng thời gian nhau, không nhất thiết cùng một khoảnh khắc, một lõi vẫn làm được; hợp với việc chờ như tệp, mạng, người dùng. Song song, nghĩa là doing nhiều việc cùng lúc, ba thẻ: chuyện thực thi, chạy nhiều phép tính cùng một lúc; cần nhiều bộ xử lý hoặc nhiều lõi; hợp với việc nặng tính toán. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-025-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần cứng chạy chương trình; việc "bị chặn bởi CPU" là việc mà tốc độ tính toán của nó quyết định thời gian chạy.
- **GIL** (Global Interpreter Lock) — khóa phiên dịch toàn cục: cơ chế của CPython khiến một thời điểm chỉ một luồng chạy mã Python.

## Đọc hình

**Câu nói mở đầu.** Nguồn trích lời Rob Pike (nguồn viết là "Rob Pyke", một trong những người tạo ra Go): "Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once." Nói gọn: đồng thời là *xử lý* nhiều việc cùng lúc, song song là *làm* nhiều việc cùng lúc. Theo nguồn, đồng thời nghiêng về *thiết kế* chương trình, song song nghiêng về *thực thi*.

**Đồng thời.** Là cấu trúc một chương trình để xử lý nhiều việc: các việc có thể bắt đầu, chạy và kết thúc trong những khoảng thời gian chồng lên nhau, nhưng không nhất thiết ở cùng một khoảnh khắc. Nguồn mô tả nó là sự kết hợp của các tiến trình chạy độc lập, và là khả năng của chương trình xử lý nhiều việc bằng cách làm cho từng việc tiến triển, mà không cần xong việc này mới bắt đầu việc kia. Trên thực tế, đồng thời giúp chương trình vẫn phản hồi đầu vào, làm việc nền và xử lý nhiều thao tác như thể cùng lúc, kể cả trên bộ xử lý một lõi. Nó đặc biệt hữu ích với các việc bị chặn bởi vào ra (I/O, input/output) và có độ trễ cao: chờ tệp, mạng hoặc thao tác của người dùng.

**Song song.** Là việc thực thi nhiều phép tính cùng một lúc: chạy hai hay nhiều tác vụ cùng lúc, dùng nhiều bộ xử lý hoặc nhiều lõi trong một máy. Song song cần phần cứng có nhiều đơn vị xử lý, và mục tiêu chính là tăng thông lượng (throughput) và tốc độ tính toán của hệ thống. Nó quan trọng với các việc bị chặn bởi CPU, nơi tốc độ tính toán là nút thắt: tính toán toán học nặng, phân tích dữ liệu, xử lý ảnh, xử lý thời gian thực.

**Gặp lại trong tài liệu gốc.**
- Tài liệu Effective Go của Go định nghĩa hai khái niệm gần như vậy: đồng thời là cấu trúc một chương trình thành các thành phần chạy độc lập; song song là thực hiện các phép tính song song trên nhiều bộ xử lý để tăng hiệu quả. Tài liệu nói Go là ngôn ngữ đồng thời chứ không phải ngôn ngữ song song, và các tính năng đồng thời của Go có thể giúp một số bài toán dễ được cấu trúc thành tính toán song song.
- Tài liệu `asyncio` của Python mô tả nó là thư viện viết mã đồng thời bằng cú pháp async/await, và "thường rất hợp" với mã mạng có cấu trúc, bị chặn bởi vào ra.
- Tài liệu `threading` của Python nói: trong CPython, do GIL, một thời điểm chỉ một luồng chạy mã Python; muốn tận dụng tài nguyên tính toán của máy nhiều lõi thì nên dùng `multiprocessing` hoặc `ProcessPoolExecutor`; nhưng luồng vẫn là mô hình thích hợp để chạy nhiều việc bị chặn bởi vào ra cùng lúc.

## Giới hạn cần nhớ

Nguồn không có mã, số đo hay ví dụ chạy được; nó cũng không nói khi nào chọn bên nào ngoài hai nhóm việc (chờ đợi và tính toán nặng). Việc lời trích là của Rob Pike, một trong những người tạo ra Go, là lời của nguồn (nguồn viết tên là "Rob Pyke"); bài chỉ đối chiếu các định nghĩa với Effective Go, không kiểm tra lời trích.
Nguồn dùng chữ "đồng thời" trong câu "xử lý nhiều việc cùng lúc" nhưng cũng nói rõ các việc không nhất thiết chạy tại cùng một khoảnh khắc; đọc kỹ chỗ đó để khỏi lẫn với song song. Ví dụ Go và Python chỉ là vài trường hợp đã đối chiếu, không phải danh sách đầy đủ.

## Nhìn hình trả lời

Một chương trình dành phần lớn thời gian chờ phản hồi từ mạng và tệp. Một chương trình khác xử lý ảnh bằng những phép tính nặng. Theo nguồn, mỗi chương trình hợp với đồng thời hay song song? Và đồng thời có đòi hỏi máy nhiều lõi không?

<details>
<summary>Xem đáp án</summary>

Chương trình chờ mạng và tệp (bị chặn bởi vào ra, độ trễ cao) hợp với đồng thời.
Chương trình xử lý ảnh nặng tính toán (bị chặn bởi CPU) hợp với song song, vì cần tốc độ và thông lượng tính toán.
Đồng thời không đòi hỏi nhiều lõi: nguồn nói nó chạy được trên bộ xử lý một lõi. Song song thì cần phần cứng có nhiều đơn vị xử lý.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh, một câu mở đầu, lời trích và năm đoạn: đồng thời (hai đoạn), song song, ứng dụng của đồng thời, ứng dụng của song song. Hình ở đây gộp thành hai nhóm thẻ, một nhóm cho mỗi khái niệm, và không dùng ảnh nguồn.
Mục "Gặp lại trong tài liệu gốc" lấy từ Effective Go và tài liệu Python tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/concurrency-is-not-parallelism.md): định nghĩa đồng thời và song song, nơi mỗi bên hợp.
- [Go — Effective Go](https://github.com/golang/website/blob/d1edce5b8ec957935895f507f3253d6e02447a6c/_content/doc/effective_go.html): đồng thời khác song song; Go là ngôn ngữ đồng thời. Đọc từ kho mã.
- [Python — asyncio](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/asyncio.rst) và [threading](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/threading.rst): mã đồng thời, việc bị chặn bởi vào ra, khóa phiên dịch toàn cục, `multiprocessing`. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa CPU và GIL trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

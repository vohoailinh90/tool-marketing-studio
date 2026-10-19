# Đồng thời và song song: khác nhau ở đâu?

**Cùng một máy bốn lõi, bốn việc chờ và bốn việc tính toán chạy theo ba cách. Số đo cho thấy khi nào chỉ cần đồng thời, khi nào phải có song song.**
Bài tự chạy một thí nghiệm nhỏ bằng Python rồi đọc kết quả cùng tài liệu của Go và Python; số đo là của một lần thử trên một máy, không phải con số chung.

![Hai nhóm thẻ số đo và một khung ghi nhớ. Bốn việc chờ, mỗi việc 0,5 giây: lần lượt hết 2,00 giây; đồng thời bằng asyncio hết 0,50 giây; đồng thời bằng bốn luồng hết 0,50 giây. Bốn việc tính toán: lần lượt hết khoảng 0,6 giây; bốn luồng khoảng 0,7 giây; bốn tiến trình khoảng 0,2 đến 0,3 giây. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-025-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần cứng chạy chương trình; việc "nặng tính toán" là việc mà tốc độ của nó quyết định thời gian chạy.
- **GIL** (Global Interpreter Lock) — khóa phiên dịch toàn cục: cơ chế của CPython (bản Python phổ biến nhất) khiến một thời điểm chỉ một luồng chạy mã Python.

## Đọc hình

**Bốn việc chờ.** Mỗi việc chỉ chờ nửa giây, như khi đợi một máy chủ khác trả lời. Làm lần lượt thì hết 2,00 giây vì phải chờ nối đuôi nhau. Cho cả bốn việc cùng đang chờ thì hết 0,50 giây, dù bằng asyncio (chạy trong một luồng, nên không cần nhiều lõi) hay bằng bốn luồng. Đây là đồng thời: nhiều việc cùng tiến triển trong những khoảng thời gian chồng nhau, và thời gian chờ của việc này được dùng cho việc kia.

**Bốn việc tính toán.** Mỗi việc là một vòng lặp cộng ba triệu số, không có gì để chờ. Lần lượt hết khoảng 0,6 giây. Bốn luồng không nhanh hơn, còn chậm hơn một chút, khoảng 0,7 giây. Bốn tiến trình thì hết khoảng 0,2 đến 0,3 giây, vì mỗi tiến trình dùng một lõi riêng. Đây là song song: nhiều phép tính chạy đúng cùng một lúc trên nhiều lõi.

**Vì sao luồng không giúp việc tính toán.** Tài liệu `threading` của Python nói: trong CPython, do GIL, một thời điểm chỉ một luồng chạy mã Python. Muốn dùng nhiều lõi thì nên dùng `multiprocessing` hoặc `ProcessPoolExecutor`; còn luồng vẫn phù hợp khi chạy nhiều việc bị chặn bởi chờ vào ra. Cũng tài liệu đó ghi từ Python 3.13 có bản "free-threaded" tắt được GIL; thí nghiệm ở đây chạy trên bản có GIL.

**Hai khái niệm theo tài liệu Go.** Effective Go dặn đừng nhầm hai ý: đồng thời là dựng chương trình thành các thành phần chạy độc lập; song song là tính toán song song để hiệu quả hơn trên nhiều CPU. Go là ngôn ngữ đồng thời, không phải ngôn ngữ song song, và không phải bài toán song song nào cũng khớp với mô hình của Go. Tài liệu `asyncio` thì nói thư viện này viết mã đồng thời bằng cú pháp async/await và "thường rất hợp" với mã mạng có cấu trúc, bị chặn bởi vào ra.

## Giới hạn cần nhớ

Số đo là của hai lần chạy trên một container bốn lõi với Python 3.13.16; máy khác, bản khác hay tải khác sẽ cho số khác, nên hãy đọc tỉ lệ (2,00 xuống 0,50; 0,6 xuống 0,2 đến 0,3) hơn là từng con số. Việc chờ được giả bằng `time.sleep`, không phải mạng thật. Mỗi tiến trình có chi phí khởi động, nên việc quá nhỏ không đáng chia thành tiến trình. Bài không đo Go, và không nói chọn công cụ nào cho chương trình thật: chỉ đo hai loại việc đơn giản.

## Nhìn hình trả lời

Một chương trình gọi hai mươi dịch vụ ngoài, mỗi lần gọi chủ yếu là chờ. Một chương trình khác nén ảnh, việc nào cũng đốt hết một lõi. Mỗi chương trình hợp với cách nào trong hình, và vì sao bốn luồng không giúp chương trình thứ hai?

<details>
<summary>Xem đáp án</summary>

Chương trình gọi dịch vụ hợp với đồng thời (asyncio hoặc luồng): thời gian chờ chồng nhau, như bốn việc chờ từ 2,00 giây xuống 0,50 giây.
Chương trình nén ảnh hợp với song song (nhiều tiến trình, mỗi tiến trình một lõi). Bốn luồng không giúp vì trong CPython có GIL, một thời điểm chỉ một luồng chạy mã Python, nên bốn việc tính toán vẫn chạy nối đuôi nhau.

</details>

<details>
<summary>Xem sâu hơn: cách đo</summary>

Mỗi phép đo dùng `time.perf_counter` quanh toàn bộ bốn việc. Việc chờ là `time.sleep(0,5)` (trong bản asyncio là `await asyncio.sleep(0,5)`); việc tính toán là vòng `for i in range(3_000_000): s += i * i`. Ba cách chạy là: gọi lần lượt trong một vòng lặp; `asyncio.gather` hoặc `ThreadPoolExecutor(4)` cho việc chờ; `ThreadPoolExecutor(4)` và `ProcessPoolExecutor(4)` cho việc tính toán. Chạy lại hai lần cho kết quả sát nhau (việc tính toán lần lượt 0,60 và 0,63 giây, bốn luồng 0,70 và 0,72, bốn tiến trình 0,21 và 0,30).

Đồng thời và song song cũng đi cùng nhau được: một chương trình đồng thời cho việc chờ có thể đồng thời giao việc nặng cho nhiều tiến trình. Hình chỉ tách hai loại việc để thấy mỗi cách hợp chỗ nào.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/concurrency-is-not-parallelism.md): chỉ lấy chủ đề; ý, ví dụ và số đo trong bài là của bài này.
- [Go — Effective Go](https://github.com/golang/website/blob/d1edce5b8ec957935895f507f3253d6e02447a6c/_content/doc/effective_go.html): đồng thời khác song song; Go là ngôn ngữ đồng thời. Đọc từ kho mã.
- [Python — asyncio](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/asyncio.rst) và [threading](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/threading.rst): mã đồng thời bằng async/await, khóa phiên dịch toàn cục, `multiprocessing`, bản free-threaded. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Số đo do người biên soạn chạy ngày 2026-10-19; các câu giải nghĩa CPU và GIL trong mục từ viết tắt là kiến thức chung của người biên soạn (phần GIL khớp với tài liệu `threading`).
Bài viết và hình được thiết kế độc lập.

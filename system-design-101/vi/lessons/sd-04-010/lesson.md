# Bốn kiểu hàng đợi trong chương trình: FIFO, bộ đệm vòng, ưu tiên, deque

**Bốn cấu trúc này cùng giữ các việc đang chờ, nhưng khác nhau ở câu hỏi "lấy cái nào ra trước, và đầy thì sao".**
Bài này chạy thử cả bốn bằng Python để thấy mỗi câu trả lời, kể cả một cái bẫy hiệu năng khi dùng sai cấu trúc.

![Hai khung. Khung một là bốn thẻ. Hàng đợi FIFO: vào cuối, ra đầu; lấy hết 100.000 phần tử từ đầu một list Python mất khoảng 14 giây, từ đầu một deque mất 0,009 giây. Bộ đệm vòng: 8 ô cố định dùng xoay vòng; khi đầy, người ghi phải chờ người đọc. Hàng đợi ưu tiên: lấy ra phần tử ưu tiên nhất trước; Binh và Dung cùng mức 1 ra trước, rồi Chi, rồi An. Deque: thêm và lấy ở cả hai đầu; chỉ dùng một đầu thì thành ngăn xếp. Khung hai chọn theo câu hỏi: giữ đúng thứ tự đến thì FIFO; bộ nhớ cố định thì bộ đệm vòng; việc gấp đi trước thì hàng đợi ưu tiên; cần cả hai đầu thì deque.](../../diagrams/sd-04-010-main.svg)

## Từ viết tắt

- **FIFO** (First In, First Out) — vào trước ra trước: phần tử đến trước được lấy ra trước, như hàng người xếp ở quầy.
- **LIFO** (Last In, First Out) — vào sau ra trước: phần tử đến sau cùng được lấy ra trước, như chồng đĩa; đó là cách một ngăn xếp làm việc.

## Đọc hình

**FIFO.** Thêm vào cuối, lấy ra ở đầu. Tài liệu Python nói `list` được tối ưu cho thao tác ở cuối, còn `pop(0)` phải dời mọi phần tử còn lại, tốn O(n) mỗi lần; `collections.deque` thêm và lấy ở hai đầu với chi phí xấp xỉ O(1).

**Bộ đệm vòng (ring buffer).** Một mảng cố định, người ghi và người đọc mỗi bên giữ một số thứ tự tăng mãi; ô được dùng là số thứ tự lấy phần dư cho kích thước mảng. Tài liệu của Disruptor, một thư viện trao đổi dữ liệu giữa các luồng, chọn kích thước là lũy thừa của 2 để phép lấy dư thành một phép AND bit, cấp phát sẵn mọi ô từ đầu để không sinh rác cho bộ thu gom, và cho người ghi theo dõi người đọc chậm nhất để không ghi đè lên dữ liệu chưa đọc.

**Hàng đợi ưu tiên.** Lấy ra phần tử có mức ưu tiên cao nhất trước, thường cài bằng heap. Mô-đun `heapq` của Python lấy ra phần tử nhỏ nhất, nên mức 1 nghĩa là gấp nhất.

**Deque (double-ended queue, hàng đợi hai đầu).** Thêm và lấy được ở cả hai đầu. Dùng một đầu để thêm, đầu kia để lấy thì thành FIFO; chỉ dùng một đầu thì thành ngăn xếp LIFO.

## Thử nghiệm

Python 3.13 trên một máy:

| Việc | Kết quả |
|---|---|
| Lấy hết 100.000 phần tử từ đầu, bằng `list.pop(0)` | khoảng 14 giây (hai lần chạy: 14,5 và 14,0) |
| Cùng việc, bằng `deque.popleft()` | 0,009 giây |
| Bộ đệm vòng 8 ô, người đọc đứng yên, ghi `e0` tới `e9` | nhận 8, từ chối từ `e8`; đọc 3 phần tử thì ghi tiếp được, `e10` nằm ở ô 2 (10 lấy dư cho 8) |
| `deque(maxlen=3)` thêm `e0` tới `e4` | còn `e2`, `e3`, `e4`: phần tử cũ nhất bị bỏ |
| Heap với bộ ba (mức, số thứ tự đến, tên) | ra Binh, Dung, Chi, An |

Bộ đệm vòng và `deque(maxlen=3)` cho thấy hai cách xử lý khi đầy: bắt người ghi chờ, hoặc bỏ phần tử cũ nhất. Tài liệu Python gợi ý kiểu thứ hai cho việc chỉ quan tâm các mục mới nhất, như lệnh `tail` của Unix.

## Giới hạn cần nhớ

Hàng đợi ưu tiên không giữ thứ tự đến cho các phần tử cùng mức nếu không làm gì thêm. Tài liệu `heapq` khuyên thêm một số đếm tăng dần vào giữa mức ưu tiên và dữ liệu, như thử nghiệm làm, để Binh và Dung cùng mức 1 ra theo thứ tự đến. Việc mức thấp có thể chờ mãi khi việc mức cao đến liên tục là một rủi ro riêng mà cấu trúc này không tự giải.

## Nhìn hình trả lời

Một máy chủ ghi lại 1.000 yêu cầu gần nhất để xem khi có sự cố, và không được dùng thêm bộ nhớ theo thời gian. Kiểu nào hợp, và đầy thì nên chờ hay bỏ?

<details>
<summary>Xem đáp án</summary>

Bộ đệm có kích thước cố định, ví dụ `deque(maxlen=1000)` hay một bộ đệm vòng 1.024 ô. Đầy thì bỏ cái cũ nhất: thứ cần xem là các yêu cầu gần nhất, và bắt máy chủ chờ chỉ để ghi nhật ký thì làm chậm chính việc phục vụ người dùng.
Nếu dữ liệu không được phép mất, như lệnh giao dịch trong Disruptor, thì ngược lại: người ghi phải chờ người đọc.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn nói ở hàng đợi vòng "việc thêm diễn ra ở đầu và việc xóa ở cuối hàng". Cách bài này và tài liệu Disruptor mô tả thì khác: người ghi và người đọc cùng đi một chiều quanh vòng, người đọc theo sau người ghi.
Bài nguồn dùng hàng đợi ưu tiên để xếp bệnh nhân cấp cứu; bài này giữ ví dụ đó nhưng thêm số thứ tự đến để giải chuyện cùng mức.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/explaining-the-4-most-commonly-used-types-of-queues-in-a-single-diagram.md): bốn kiểu hàng đợi và ví dụ dùng.
- [Python — tài liệu `collections`, mục deque, tại commit cố định](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/collections.rst): thêm và lấy ở hai đầu xấp xỉ O(1), `list.pop(0)` tốn O(n), `maxlen` bỏ phần tử ở đầu kia. Đọc từ bản clone của kho.
- [Python — tài liệu `heapq`, mục Priority Queue Implementation Notes](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/heapq.rst): số đếm làm khóa phụ để giữ thứ tự đến.
- [Disruptor — bài viết kỹ thuật, tại commit cố định](https://github.com/LMAX-Exchange/disruptor/blob/c871ca49826a6be7ada6957f6fbafcfecf7b1f87/src/docs/asciidoc/en/disruptor.adoc): bộ đệm vòng cấp phát sẵn, kích thước lũy thừa của 2 và mặt nạ bit, người ghi không vượt vòng người đọc. Đọc từ bản clone của kho.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 bằng Python 3.13.
Bài viết và hình được thiết kế độc lập.

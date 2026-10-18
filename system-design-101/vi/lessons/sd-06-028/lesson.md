# Năm cách làm API nhanh hơn, và cái giá của mỗi cách

**Một lời gọi API chậm thường vì hai lý do: nó trả quá nhiều dữ liệu, hoặc nó đứng chờ một việc chậm (mở kết nối, ghi đĩa, hỏi cơ sở dữ liệu). Năm cách quen thuộc chia đúng theo hai lý do đó: phân trang và nén để trả ít hơn; ghi log qua hàng đợi, bộ đệm và tái dùng kết nối để chờ ít hơn. Cách nào cũng đổi một thứ lấy một thứ.**
Các con số dưới đây đo trên một máy với PostgreSQL 16 và Python 3.13.

![Ba phần. Trả ít hơn, hai thẻ: phân trang, trả từng trang nhỏ, trang sâu thì đi theo khóa; nén phản hồi, gzip và brotli cho văn bản lớn, tốn thêm thời gian xử lý. Chờ ít hơn, ba thẻ: ghi log qua hàng đợi để luồng khác ghi xuống đĩa, sập thì mất phần chưa ghi; bộ đệm dữ liệu, đọc bản đã giữ thay vì hỏi cơ sở dữ liệu; tái dùng kết nối, giữ sẵn kết nối thay vì mở mới mỗi lần. Đo với PostgreSQL 16 và Python: kết nối mới mỗi truy vấn 3,9 ms, tái dùng 0,1 ms; trang sâu bỏ qua 290 000 dòng 27,7 ms, theo khóa 0,23 ms; cả 300 000 dòng là 25 MB JSON, một trang 4,2 KB, nén còn 580 byte; log qua hàng đợi 9 µs mỗi dòng thay vì 273 µs, nhưng chết ngay thì mất 1998 trên 2000 dòng.](../../diagrams/sd-06-028-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình gọi chức năng hoặc lấy dữ liệu của chương trình khác.
- **JSON** (JavaScript Object Notation) — định dạng văn bản ghi dữ liệu thành các cặp tên và giá trị; nhiều API trả kết quả ở dạng này.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn cơ sở dữ liệu quan hệ; PostgreSQL là một cơ sở dữ liệu SQL.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền dữ liệu web mà phần lớn API dùng.
- **TCP** (Transmission Control Protocol) — giao thức mở kết nối tin cậy giữa hai máy; mỗi kết nối mới cần một lần bắt tay.
- **TLS** (Transport Layer Security) — lớp mã hóa kết nối; bật nó thì mở kết nối tốn thêm một lần bắt tay.
- **KB** (KiloByte) — kilobyte: một nghìn byte.
- **MB** (MegaByte) — megabyte: một triệu byte.

## Đọc hình

**Phân trang.** Thay vì trả mọi dòng, API trả từng trang và một cách để lấy trang sau. Cách đơn giản là bỏ qua *n* dòng (`OFFSET`); tài liệu PostgreSQL nói các dòng bị bỏ qua vẫn phải được tính trong máy chủ, nên `OFFSET` lớn có thể chậm. Cách theo khóa (keyset) nhớ khóa của dòng cuối trang trước và hỏi "các dòng sau khóa này", nên dùng được chỉ mục để nhảy thẳng tới chỗ cần.

**Nén phản hồi.** Văn bản như JSON nén rất tốt; trình duyệt và thư viện HTTP giải nén tự động. Cái giá là thời gian nén ở máy chủ.

**Ghi log qua hàng đợi.** Thay vì ghi và ép từng dòng log xuống đĩa trong lúc xử lý yêu cầu, mã đẩy dòng log vào một hàng đợi trong bộ nhớ rồi trả lời ngay; một luồng khác ghi xuống đĩa. Thư viện chuẩn của Python có sẵn `QueueHandler` và `QueueListener` cho việc này. Cái giá: dòng còn trong hàng đợi mất khi tiến trình chết.

**Bộ đệm dữ liệu.** Dữ liệu đọc nhiều được giữ ở chỗ nhanh hơn (như Redis) và đọc từ đó trước; chi tiết các chiến lược ở bài [Năm chiến lược bộ đệm](../sd-06-026/lesson.md).

**Tái dùng kết nối.** Mở một kết nối tới cơ sở dữ liệu tốn bắt tay mạng, xác thực, dựng tiến trình phục vụ. Một bể kết nối (connection pool) giữ sẵn vài kết nối và cho mượn; tài liệu psycopg nói thời gian mở kết nối mới có thể khá dài nên giữ kết nối mở giảm độ trễ.

**Đo thử.** Bảng 300 000 đơn hàng trong PostgreSQL 16, truy cập qua TCP trên cùng máy bằng psycopg 3.3, trung vị nhiều lần chạy:

- Mở kết nối mới cho mỗi truy vấn `SELECT 1`: 3,88 ms. Dùng lại một kết nối: 0,106 ms.
- Trang 50 dòng sau 290 000 dòng: `OFFSET 290000` 27,7 ms; theo khóa (`WHERE id > 290000`) 0,231 ms, cùng 50 dòng. `EXPLAIN ANALYZE` cho thấy cách `OFFSET` quét chỉ mục qua 290 050 dòng.
- Trả cả bảng: 25 175 741 byte JSON, gzip còn 3 295 327 byte nhưng nén mất 332 ms. Một trang 50 dòng: 4 191 byte, gzip còn 580 byte.
- Ghi log (mỗi dòng ghi rồi `fsync`): người gọi chờ 273 µs mỗi dòng. Qua hàng đợi: 9,4 µs. Một tiến trình đẩy 2000 dòng qua hàng đợi rồi thoát ngay: tệp log chỉ có 2 dòng.

## Giới hạn cần nhớ

Phân trang theo khóa nhanh nhưng không nhảy thẳng tới "trang 37" được, và cần một thứ tự ổn định theo cột có chỉ mục. Nén tốn thời gian xử lý và gần như vô ích với phản hồi nhỏ hay dữ liệu đã nén. Log qua hàng đợi có thể mất đúng những dòng cần nhất khi tiến trình sập. Bể kết nối cần giới hạn kích thước, vì mỗi kết nối chiếm tài nguyên ở máy chủ cơ sở dữ liệu. Thử nghiệm chạy trên một máy, không có độ trễ mạng thật, nên khoảng cách thật giữa các con số còn lớn hơn khi cơ sở dữ liệu ở máy khác.

## Nhìn hình trả lời

Một API `GET /orders?page=N` trả 50 đơn mỗi trang bằng `OFFSET (N-1)*50`. Trang đầu trả trong vài mili giây, nhưng một công cụ đồng bộ đọc lần lượt mọi trang thì càng về cuối càng chậm. Vì sao, và sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Vì mỗi trang sâu, máy chủ vẫn phải đọc qua mọi dòng bị bỏ qua: trong thử nghiệm, trang sau 290 000 dòng mất 27,7 ms so với vài phần mười mili giây khi đi theo khóa, và chi phí tăng theo số trang. Sửa: cho API trả kèm khóa của dòng cuối (ví dụ `next_after=290050`) và trang sau hỏi `WHERE id > :khóa ORDER BY id LIMIT 50`. Công cụ đồng bộ chỉ cần đi tuần tự nên không cần nhảy tới số trang bất kỳ.

</details>

<details>
<summary>Xem sâu hơn: đo cái gì trước khi chọn cách</summary>

- Bài nguồn nói phân trang "truyền" kết quả lớn về máy khách; ở đây chỉ bàn phân trang theo trang và theo khóa, vì đó là điều đo được.
- Thư viện chuẩn của Python mô tả `QueueHandler` trong mục "Dealing with handlers that block" của logging cookbook: dùng khi trình ghi log có thể làm chậm luồng đang xử lý.
- Thử nghiệm dùng xác thực `trust` cho đơn giản; khi có xác thực bằng mật khẩu và mã hóa TLS, mở kết nối mới còn tốn hơn.
- Tìm chỗ chậm trước khi sửa: đo thời gian từng bước của một yêu cầu (truy vấn, mở kết nối, ghi log, tuần tự hóa JSON), rồi sửa bước lớn nhất.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-5-common-ways-to-improve-api-performance.md): năm cách tăng tốc API.
- [PostgreSQL 16 — `queries.sgml`, tại commit cố định của nhánh REL_16_STABLE](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/queries.sgml): mục `LIMIT` và `OFFSET`, các dòng bị bỏ qua vẫn phải được tính.
- [psycopg — Connection pools, tại commit cố định](https://github.com/psycopg/psycopg/blob/99356800e90aa0e7b604f652d714ef0f33422b47/docs/advanced/pool.rst): thời gian mở kết nối mới, giữ kết nối mở giảm độ trễ.
- [Python 3.13 — Logging Cookbook, tại commit cố định](https://github.com/python/cpython/blob/24d048d3601c2f1d41fa357897c1c91bb0a0bc13/Doc/howto/logging-cookbook.rst): mục "Dealing with handlers that block", `QueueHandler` và `QueueListener`.
- [MDN — Compression in HTTP, tại commit cố định](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/compression/index.md): nén phản hồi văn bản.

Thử nghiệm chạy ngày 2026-10-18: PostgreSQL 16.15 (gói Ubuntu) trên cùng máy, psycopg 3.3.6, Python 3.13, gzip mức 6; ghi log mỗi dòng có `fsync` để mô phỏng log được ép xuống đĩa. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

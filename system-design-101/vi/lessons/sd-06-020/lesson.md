# Redis dùng vào việc gì: mười cách dùng, năm nhóm kiểu dữ liệu

**Redis không chỉ là bộ nhớ đệm. Nó có nhiều kiểu dữ liệu, và mỗi cách dùng quen thuộc thực chất là chọn đúng kiểu dữ liệu rồi dùng các lệnh nguyên tử của nó.**
Bài xếp mười cách dùng hay gặp vào năm nhóm kiểu dữ liệu (bitmap thực ra là chuỗi đọc theo bit; danh sách và stream chung một nhóm), rồi chạy thử để thấy chỗ mỗi cách dễ sai.

![Ba phần. Phần một, ba thẻ: chuỗi dùng cho bộ đệm, khóa phân tán, bộ đếm, giới hạn tần suất và sinh số tăng dần; bảng băm dùng cho phiên đăng nhập và giỏ hàng, nhiều trường trong một khóa; bitmap cho mỗi người dùng một bit mỗi ngày, giao hai ngày để đếm người quay lại. Phần hai, hai thẻ: danh sách và stream làm hàng đợi việc, stream giữ tin tới khi được xác nhận; tập có thứ tự làm bảng xếp hạng, mỗi phần tử một điểm. Phần ba, bốn điều thấy khi chạy thử: khóa phải gắn mã riêng và chỉ xóa khi mã còn đúng của mình; giới hạn tần suất phải tăng đếm và đặt hết hạn trong cùng một bước; lấy việc khỏi danh sách rồi sập thì việc đó mất; stream để tin chưa xác nhận chờ cho người khác nhận lại.](../../diagrams/sd-06-020-main.svg)

## Từ viết tắt

- **MB** (MegaByte) — megabyte: khoảng một triệu byte, đơn vị đo dung lượng bộ nhớ.
- **IP** (Internet Protocol) — giao thức Internet; "địa chỉ IP" là địa chỉ của một máy trên mạng, ở đây dùng để đếm số yêu cầu của từng máy khách.

## Đọc hình

**Chuỗi.** Một khóa giữ một giá trị. Bộ đệm là `SET` kèm thời gian hết hạn. Bộ đếm lượt xem, lượt thích và số đơn tăng dần đều là `INCR`: lệnh tăng chạy nguyên tử nên hai máy khách cùng tăng không mất lượt nào. Khóa phân tán là `SET` với `NX` (chỉ đặt khi chưa có) và `PX` (tự hết hạn).

**Bảng băm.** Một khóa chứa nhiều trường: phiên đăng nhập (`HSET session:… user_id 42`, thêm hết hạn 30 phút) hay giỏ hàng (mỗi mặt hàng một trường, `HINCRBY` để cộng số lượng).

**Bitmap.** Một chuỗi được đọc theo từng bit. Mỗi ngày một bitmap, bit thứ *n* bật khi người dùng số *n* đăng nhập; `BITOP AND` hai ngày rồi `BITCOUNT` cho số người quay lại.

**Danh sách và stream.** `LPUSH` thêm việc, người xử lý lấy ra từ đầu kia. Stream là nhật ký chỉ nối thêm, có nhóm người đọc và lệnh xác nhận (`XACK`).

**Tập có thứ tự.** Mỗi phần tử kèm một điểm; `ZINCRBY` cộng điểm, `ZREVRANGE` lấy những phần tử điểm cao nhất.

**Chạy thử (Redis 7.0.15).**

- A lấy khóa với hạn 1 giây; B thử lấy, bị từ chối. Qua hạn, B lấy được. A xử lý chậm xong mới gọi `DEL`: khóa của B bị xóa mất. Làm lại với một script chỉ xóa khi giá trị đúng mã của A: script trả 0, khóa của B còn nguyên.
- Giới hạn 10 yêu cầu một phút cho một địa chỉ IP: yêu cầu thứ 11 và 12 đếm ra 11, 12 nên bị từ chối.
- Ngày 1 có 6 người, ngày 2 có 4 người, quay lại cả hai ngày: 3. Bitmap có bit thứ 10 000 000 dài 1 250 001 byte, vì Redis cấp bộ nhớ tới bit cao nhất được bật.
- Danh sách: người xử lý lấy `j1` rồi "chết", `j1` không còn ở đâu. `LMOVE` sang danh sách đang xử lý thì việc còn nằm đó. Stream: người đọc A nhận 2 tin rồi chết trước khi xác nhận; 2 tin vẫn ở trạng thái chờ, B nhận lại bằng `XAUTOCLAIM`, xác nhận một tin thì còn 1 tin chờ.
- Bảng xếp hạng: `post:c` từ 90 điểm, cộng 300, lên đầu với 390.

## Giới hạn cần nhớ

Khóa trên một máy Redis chỉ an toàn khi máy đó luôn sống; tài liệu Redis nói cách này dùng được khi thỉnh thoảng có xung đột cũng chấp nhận được, còn khóa qua nhiều máy là thuật toán Redlock, phức tạp hơn. Hạn của khóa là thời gian bạn có để làm xong việc; quá hạn mà việc chưa xong thì người khác đã vào. Hàng đợi bằng danh sách đơn giản nhưng không tự giữ việc khi người xử lý chết.

## Nhìn hình trả lời

Bạn cần một hàng đợi gửi email xác nhận đơn hàng, và không được bỏ sót email nào khi một máy xử lý khởi động lại giữa chừng. Dùng kiểu dữ liệu nào, và bước nào bảo đảm điều đó?

<details>
<summary>Xem đáp án</summary>

Stream với nhóm người đọc. Tin được đọc nhưng chưa `XACK` vẫn nằm trong danh sách chờ của nhóm; khi máy kia chết, máy khác xem danh sách chờ (`XPENDING`) và nhận lại tin bằng `XAUTOCLAIM` hoặc `XCLAIM`. Bước bảo đảm là chỉ `XACK` sau khi đã gửi email xong. Danh sách với `LMOVE` sang danh sách đang xử lý cũng làm được, nhưng bạn phải tự viết phần theo dõi và trả việc lại.
Lưu ý: vì tin có thể được nhận lại, một email có thể bị gửi hai lần; phần gửi cần chịu được việc chạy lặp.

</details>

<details>
<summary>Xem sâu hơn: chi tiết của từng mẫu</summary>

- **Khóa:** tài liệu Redis cho mẫu `SET resource_name my_random_value NX PX 30000`; giá trị phải là duy nhất giữa mọi máy khách và mọi lần lấy khóa. Nhả khóa bằng script so giá trị rồi mới xóa (hoặc lệnh `DELEX ... IFEQ` từ Redis 8.4).
- **Giới hạn tần suất:** nếu máy khách chạy `INCR` rồi chết trước `EXPIRE`, khóa đếm sống mãi; tài liệu sửa bằng `MULTI`/`EXEC` (mỗi giây một khóa) hoặc một script Lua gộp hai bước. Đây là cửa sổ cố định: sát ranh giới hai cửa sổ có thể lọt gần gấp đôi giới hạn trong thời gian ngắn.
- **Bitmap:** tài liệu Redis ghi một chuỗi tối đa 512 MB, đủ cho khoảng 4 tỷ bit, nên mã người dùng phải là số nguyên tăng dần và không quá thưa.
- **Danh sách:** `RPOPLPUSH` (cũ) và `LMOVE` là mẫu "hàng đợi tin cậy" trong tài liệu; một máy khách khác theo dõi danh sách đang xử lý để trả những việc nằm quá lâu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-can-redis-be-used.md): mười cách dùng và kiểu dữ liệu gợi ý cho mỗi cách.
- Tài liệu Redis tại commit cố định của kho tài liệu: [Distributed locks](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/clients/patterns/distributed-locks.md) (khóa trên một máy, giá trị ngẫu nhiên, script nhả khóa), [`INCR`](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/commands/incr.md) (mẫu bộ đếm và giới hạn tần suất), [`LMOVE`](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/commands/lmove.md) (hàng đợi tin cậy), [Streams](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/data-types/streams/_index.md) (nhóm người đọc, tin chờ, nhận lại), [Bitmaps](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/data-types/strings/bitmaps.md) (`BITOP`, `BITCOUNT`, giới hạn 512 MB), [Sorted sets](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/data-types/sorted-sets.md), [Hashes](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/data-types/hashes.md).

Thử nghiệm chạy ngày 2026-10-18 với gói Redis 7.0.15 của Ubuntu, một máy khách `redis-cli`; "A chết" là dừng gọi lệnh, không phải giết tiến trình thật. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

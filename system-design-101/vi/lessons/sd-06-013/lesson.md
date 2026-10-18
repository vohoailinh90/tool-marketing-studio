# Truy vấn khóa không tồn tại: khi bộ nhớ đệm bị xuyên qua

**Bộ nhớ đệm chỉ giữ được thứ có thật. Một yêu cầu xin mã không tồn tại sẽ trượt bộ nhớ đệm, rồi hỏi tới cơ sở dữ liệu, rồi không có gì để cất, và lần sau lại y như vậy.** Kẻ xấu gửi thật nhiều yêu cầu như thế thì bộ nhớ đệm coi như không có, mọi tải dồn thẳng xuống cơ sở dữ liệu.
Hai cách chữa hay được nhắc là cất cả giá trị rỗng và dùng bộ lọc Bloom. Bài này thử cả hai và thấy cách thứ nhất chỉ chặn được một kiểu tấn công.

![Ba khung. Khung một, trình tự: kẻ tấn công xin một mã không tồn tại; bộ đệm không có nên hỏi cơ sở dữ liệu; cơ sở dữ liệu trả không có; bộ đệm không cất gì và trả không có; kẻ tấn công xin một mã khác và mọi thứ lặp lại. Khung hai, cất giá trị rỗng: cùng một mã lặp lại 20 nghìn lần chỉ còn 1 lần hỏi cơ sở dữ liệu; 20 nghìn mã khác nhau vẫn là 20 nghìn lần hỏi, kèm 20 nghìn khóa rác. Khung ba, bộ lọc Bloom: trả lời chắc chắn không có thì chặn ngay, có thể có thì mới hỏi tiếp; thử với tỷ lệ lọt 1 phần trăm, 0,87 phần trăm mã giả lọt qua, bộ lọc tốn khoảng 120 nghìn byte cho 100 nghìn mã.](../../diagrams/sd-06-013-main.svg)

## Từ viết tắt

- **TTL** (Time To Live) — thời gian sống: số giây một khóa được giữ trước khi tự hết hạn; giá trị rỗng thường được cất với hạn ngắn.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; SQLite là một cơ sở dữ liệu nhỏ dùng nó.
- **KB** (KiloByte) — kilôbyte: đơn vị dung lượng, khoảng một nghìn byte.
- **SHA** (Secure Hash Algorithm) — thuật toán băm an toàn: biến một chuỗi bất kỳ thành một dãy số cố định; SHA-256 cho ra 256 bit, ở đây dùng để chọn vị trí bit trong bộ lọc.

## Đọc hình

**Cất giá trị rỗng.** Khi cơ sở dữ liệu trả "không có", vẫn cất một giá trị đánh dấu rỗng vào bộ nhớ đệm, với hạn sống (TTL) ngắn. Lần sau hỏi đúng mã đó thì bộ nhớ đệm trả "không có" luôn.

**Bộ lọc Bloom** là một cấu trúc dữ liệu nhỏ trả lời câu hỏi "mã này có trong tập không?" với hai đáp án: *chắc chắn không có*, hoặc *có thể có*. Tài liệu của Redis về bộ lọc Bloom nói rõ luôn có khả năng dương tính giả (báo có thể có dù chưa từng thêm), nhưng không có âm tính giả. Đặt bộ lọc trước bộ nhớ đệm: mã nào bị báo "chắc chắn không có" thì từ chối ngay, không hỏi tiếp.

Tài liệu của Redis cũng cho công thức chọn kích thước: với tỷ lệ dương tính giả mong muốn *p*, cần khoảng −ln(*p*)/ln(2)² bit cho mỗi phần tử và ⌈−ln(*p*)/ln(2)⌉ hàm băm. Với 1% là khoảng 9,6 bit và 7 hàm băm; với 0,1% là khoảng 14,4 bit và 10 hàm băm.

## Thử với Redis và SQLite

Ngày 2026-10-18, trên một máy: bảng sản phẩm 100.000 dòng trong SQLite, bộ nhớ đệm là Redis 7.0.15, đọc theo kiểu cache-aside. Đếm số lần phải hỏi cơ sở dữ liệu với hai kiểu tấn công, mỗi kiểu 20.000 yêu cầu:

| Cách làm | 20.000 mã không có, **khác nhau** | 1 mã không có, **lặp lại** 20.000 lần |
|---|---|---|
| Cache-aside thường | 20.000 lần hỏi | 20.000 lần hỏi |
| Cất giá trị rỗng (hạn 60 giây) | 20.000 lần hỏi, và 20.000 khóa rỗng nằm trong Redis | 1 lần hỏi |

Cất giá trị rỗng chỉ chặn được kẻ hỏi lặp lại một mã. Kẻ đổi mã mỗi lần vẫn đi xuyên qua, và còn làm đầy bộ nhớ đệm bằng khóa rác.

Thêm một bộ lọc Bloom (tự viết bằng Python, băm SHA-256) chứa đủ 100.000 mã có thật, rồi cho 20.000 mã giả đi qua:

| Tỷ lệ chọn | Kích thước bộ lọc | Mã giả lọt qua | Lần hỏi cơ sở dữ liệu | Mã thật bị chặn nhầm |
|---|---|---|---|---|
| 1% | 958.506 bit (khoảng 120 KB), 7 hàm băm | 174 (0,87%) | 174 | 0 |
| 0,1% | 1.437.759 bit (khoảng 180 KB), 10 hàm băm | 24 (0,12%) | 24 | 0 |

Tỷ lệ đo được gần với tỷ lệ đã chọn, và không mã thật nào bị chặn.

## Giới hạn cần nhớ

Bộ lọc phải được cập nhật mỗi khi thêm dữ liệu mới, nếu không mã thật vừa thêm sẽ bị báo "không có". Bộ lọc Bloom cơ bản không xóa được phần tử, nên dữ liệu bị xóa vẫn lọt qua bộ lọc (chỉ là dương tính giả, cơ sở dữ liệu vẫn trả đúng). Theo tài liệu của Redis, thêm quá sức chứa đã chọn thì tỷ lệ sai tăng dần. Và bộ lọc chỉ chặn được mã không tồn tại; kẻ tấn công hỏi mã có thật thì vẫn cần giới hạn tần suất ở phía trước.

## Nhìn hình trả lời

Một trang sản phẩm bị dò bằng các mã ngẫu nhiên không tồn tại, mỗi giây vài nghìn mã khác nhau. Nhóm đã bật cất giá trị rỗng nhưng cơ sở dữ liệu vẫn quá tải và bộ nhớ Redis tăng đều. Vì sao, và nên làm gì?

<details>
<summary>Xem đáp án</summary>

Mỗi mã chỉ được hỏi một lần nên giá trị rỗng không bao giờ được dùng lại: lần nào cũng phải hỏi cơ sở dữ liệu (cột trái của bảng thứ nhất), và mỗi lần lại để lại một khóa rỗng trong Redis.
Nên đặt một bộ lọc Bloom chứa các mã có thật trước bộ nhớ đệm, để mã giả bị chặn trước khi chạm tới cơ sở dữ liệu (chỉ khoảng tỷ lệ đã chọn lọt qua), và giới hạn tần suất theo nguồn gửi yêu cầu.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn mô tả hiện tượng và hai cách chữa. Bài này thử cả hai và cho thấy điều bài nguồn không nói: cất giá trị rỗng không chặn được mã thay đổi liên tục. Công thức kích thước của bộ lọc lấy từ tài liệu của Redis.
Bộ lọc trong thử nghiệm là bản tự viết để thấy cơ chế; Redis có kiểu dữ liệu Bloom riêng, nhưng bản Redis 7.0.15 đã thử không có sẵn nó (các kiểu xác suất là module). Thử nghiệm chạy trên một máy, với mã giả sinh ngẫu nhiên.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cache-miss-attack.md): hiện tượng truy vấn khóa không tồn tại, cất giá trị rỗng với hạn ngắn, và bộ lọc Bloom.
- [Redis — tài liệu bộ lọc Bloom, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/data-types/probabilistic/bloom-filter.md): luôn có khả năng dương tính giả; tỷ lệ sai và sức chứa; công thức số bit mỗi phần tử và số hàm băm; tỷ lệ sai tăng khi vượt sức chứa.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của kho; thử nghiệm chạy cùng ngày với Redis 7.0.15, SQLite và Python 3.13. Bài viết và hình được thiết kế độc lập.

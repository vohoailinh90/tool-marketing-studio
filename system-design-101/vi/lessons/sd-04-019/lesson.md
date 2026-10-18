# Bốn mẫu nhất quán cuối cùng: bản đọc đi sau bao lâu, và ai sửa khi một bước hỏng

**"Nhất quán cuối cùng" nghĩa là có một khoảng thời gian các bản dữ liệu nói khác nhau. Chọn mẫu là chọn khoảng đó dài bao nhiêu và ai lo khi có bước thất bại.**
Bài này đo khoảng lệch của hai cách lan thay đổi trên PostgreSQL, rồi chạy một saga hỏng giữa chừng để xem giao dịch bù làm gì.

![Bốn khung. Khung một, bốn mẫu: theo sự kiện, bên nghe tự sửa bản của mình; đồng bộ nền, tác vụ theo lịch chép phần đã đổi; saga, giao dịch cục bộ nối nhau, hỏng thì bù; CQRS, ghi một kho, đọc kho khác đi sau. Khung hai, thử trên PostgreSQL 16 với 200 lần sửa 20 đơn hàng: theo sự kiện, trigger gửi thông báo, bản đọc trễ trung vị 2,3 ms, lâu nhất 23,8 ms; đồng bộ mỗi 2 giây trễ trung vị 640 ms, chỉ 117 trong 200 phiên bản tới nơi; đọc ngay sau khi ghi ra bản cũ 194/200 lần với sự kiện, 200/200 lần với đồng bộ. Khung ba, saga: trừ 300, giữ hàng bị chặn vì hết hàng, bù bằng một dòng hoàn 300 rồi hủy đơn. Khung bốn, bốn câu hỏi trước khi chọn mẫu.](../../diagrams/sd-04-019-main.svg)

## Từ viết tắt

- **CQRS** (Command Query Responsibility Segregation) — tách trách nhiệm lệnh và truy vấn: phần nhận lệnh ghi và phần phục vụ truy vấn đọc dùng hai mô hình, thường là hai kho dữ liệu khác nhau.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc của cơ sở dữ liệu quan hệ; nằm trong tên PostgreSQL, nơi chạy thử nghiệm.

## Đọc hình

**Khung 1 · Bốn cách cho thay đổi lan đi.**

- **Theo sự kiện.** Dịch vụ ghi dữ liệu xong thì phát một sự kiện; dịch vụ khác nghe và tự sửa bản của mình. Hai bên không gọi nhau trực tiếp, đổi lại bản của bên nghe đi sau một chút.
- **Đồng bộ nền.** Một tác vụ chạy theo lịch, tìm phần đã đổi từ lần trước và chép sang. Lịch thưa bao nhiêu thì bản chép có thể cũ bấy nhiêu.
- **Saga.** Một việc lớn chia thành nhiều giao dịch cục bộ, mỗi giao dịch nằm gọn trong một dịch vụ. Hướng dẫn kiến trúc của Azure mô tả: nếu một bước hỏng, saga chạy các *giao dịch bù* để gỡ tác động của những bước đã xong.
- **CQRS.** Ghi vào một kho, đọc từ một kho khác được dựng cho việc đọc. Theo tài liệu CQRS của Azure, khi hai kho tách rời, kho đọc có thể chưa thấy thay đổi mới nhất.

**Khung 2 · Thử: bản đọc đi sau bao lâu.** Một bảng `orders` có 20 đơn hàng; chương trình sửa trạng thái 200 lần, mỗi lần cách nhau 50 ms. Hai bản đọc nằm ở một cơ sở dữ liệu khác:

| Cách lan thay đổi | Trễ trung vị | Trễ lâu nhất | Phiên bản tới được bản đọc | Đọc ngay sau khi ghi ra bản cũ |
|---|---|---|---|---|
| Theo sự kiện: trigger gọi `pg_notify`, một tiến trình `LISTEN` áp vào bản đọc | 2,3 ms | 23,8 ms | 200/200 | 194/200 lần |
| Đồng bộ nền: mỗi 2 giây chép các dòng đổi từ lần trước | 640 ms | 1,99 s | 117/200 | 200/200 lần |

Hai điều đáng để ý. Thứ nhất, trễ vài mili giây vẫn là trễ: đọc bản đọc ngay sau khi ghi, gần như lần nào cũng ra giá trị cũ. Thứ hai, đồng bộ nền chỉ chép trạng thái lúc nó chạy; một đơn bị sửa hai lần giữa hai lượt chạy thì bản đọc không bao giờ thấy lần sửa đầu. Nếu bên đọc cần từng thay đổi (ví dụ để gửi thông báo), cách này không đủ.

**Khung 3 · Saga hỏng ở bước giữ hàng.** Ba cơ sở dữ liệu riêng cho đơn hàng, thanh toán và kho; kho còn 0 cuốn sách, có ràng buộc số lượng không âm. Chương trình đóng vai bên điều phối:

| Bước | Đơn hàng | Thanh toán | Kho |
|---|---|---|---|
| 1. Tạo đơn (giao dịch cục bộ) | `PENDING` | | 0 |
| 2. Trừ tiền (giao dịch cục bộ) | `PENDING` | trừ 300 | 0 |
| 3. Giữ hàng | | | ràng buộc chặn: hết hàng |
| 4. Bù: hoàn tiền bằng một dòng mới | `PENDING` | trừ 300, hoàn 300 | 0 |
| 5. Bù: hủy đơn | `CANCELLED` | trừ 300, hoàn 300 | 0 |

Giao dịch bù không xóa dòng "trừ 300": tiền đã trừ là chuyện đã xảy ra và đã được ghi hẳn. Nó thêm một hành động ngược lại. Giữa bước 2 và bước 4, ai đọc cả hai cơ sở dữ liệu sẽ thấy tiền đã trừ mà đơn chưa xong; giữa các dịch vụ không có sự cô lập như trong một giao dịch.

## Giới hạn cần nhớ

- Thông báo của PostgreSQL chỉ được gửi khi giao dịch ghi đã commit, và chỉ tới các phiên đang `LISTEN`; đăng ký nghe mất khi phiên kết thúc. Bên nghe tắt lúc đó là lỡ sự kiện. Muốn không lỡ, cần một hàng đợi bền hoặc đọc nhật ký thay đổi của cơ sở dữ liệu (xem bài về bắt thay đổi dữ liệu).
- Tài liệu Compensating Transaction của Azure nhắc: không nên khôi phục nguyên trạng cũ, vì có thể đè lên thay đổi của người khác; bước bù không nhất thiết chạy theo đúng thứ tự ngược; và luật nghiệp vụ có thể quyết định khác (hủy chuyến bay chưa chắc được hoàn đủ tiền).
- Bước bù cũng có thể hỏng; hướng dẫn về saga ghi rõ điều đó. Hướng dẫn cũng yêu cầu các bước sau điểm không quay lại được phải thử lại được và lũy đẳng: chạy hai lần cũng như một lần.
- Số đo là của một máy, hai cơ sở dữ liệu cùng một máy chủ PostgreSQL; qua mạng thật, trễ của cách theo sự kiện sẽ lớn hơn.

## Nhìn hình trả lời

Một trang hồ sơ cho người dùng đổi tên rồi tải lại trang ngay. Hệ thống ghi vào kho ghi và đọc từ kho đọc theo kiểu CQRS, bản đọc trễ vài mili giây. Nhìn khung 2: người dùng có thấy tên cũ không, và sửa thế nào mà không bỏ kho đọc?

<details>
<summary>Xem đáp án</summary>

Có thể, nếu lần đọc tới trước khi bản đọc kịp cập nhật. Trong thử nghiệm, lần đọc gửi ngay sau lệnh ghi (chưa tới 1 ms sau) ra bản cũ 194 trên 200 lần; bản đọc trễ trung vị 2,3 ms, lâu nhất 23,8 ms. Một lần tải lại trang thường đến muộn hơn thế, nhưng khi bản đọc bị chậm (mạng, tải nặng) thì người dùng vẫn có thể gặp.
Một cách sửa là đọc từ kho ghi cho chính người vừa ghi trong một khoảng ngắn (chỉ cho trang của họ), còn mọi người khác vẫn đọc từ kho đọc. Đây là suy luận của người biên soạn từ số đo, không phải một mẫu được nêu trong tài liệu đã dẫn.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn nêu bốn mẫu: theo sự kiện, đồng bộ nền, saga và CQRS, mỗi mẫu một hai câu. Bài này đo khoảng lệch thật của hai cách lan thay đổi và chạy một saga có giao dịch bù.
Bài nguồn nói đồng bộ nền làm nhất quán "chậm hơn" vì chạy theo lịch; thử nghiệm cho thấy thêm một điều: nó bỏ qua các phiên bản trung gian.
Tài liệu Azure liệt kê thêm các bất thường của saga (mất cập nhật, đọc bẩn, đọc không lặp lại được) và cách giảm chúng như khóa ngữ nghĩa ở mức ứng dụng; bài này chỉ nêu cái thấy được trong thử nghiệm.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-eventual-consistency-patterns-you-must-know.md): bốn mẫu nhất quán cuối cùng.
- Azure Architecture Center, tại commit cố định, đọc từ bản clone của kho: [Saga](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/saga-content.md), [Compensating Transaction](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/compensating-transaction.md), [CQRS](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/cqrs.md).
- PostgreSQL 16, tại commit cố định: [`NOTIFY`](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/ref/notify.sgml) (giao khi commit, tới các phiên đã `LISTEN`) và [`LISTEN`](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/ref/listen.sgml) (đăng ký mất khi phiên kết thúc).

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 với PostgreSQL 16.15 và psycopg 3.3.6 trên một máy.
Bài viết và hình được thiết kế độc lập.

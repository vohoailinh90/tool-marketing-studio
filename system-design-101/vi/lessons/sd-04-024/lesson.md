# Các loại cơ sở dữ liệu khác nhau ở lời hứa: giao dịch, lược đồ và cách mở rộng

**Tên loại (quan hệ, khóa–giá trị, tài liệu...) cho biết dữ liệu được xếp thế nào. Điều quyết định khi có sự cố là loại đó hứa gì: lỗi giữa chừng thì có gỡ lại được không, dữ liệu sai kiểu bị chặn ở đâu.**
Bài này đặt ba câu hỏi về lời hứa, rồi thử hai câu trên PostgreSQL và Redis bằng cùng một tình huống.

![Bốn khung. Khung một, ba câu hỏi về lời hứa: phạm vi nguyên tử là nhiều dòng hay một khóa; lược đồ được kiểm khi ghi hay khi đọc; mở rộng bằng thêm máy hay phải tự chia shard. Khung hai, chuyển 100 từ a sang b, bước hai hỏng: PostgreSQL hủy cả giao dịch, a vẫn 500, b vẫn 0; Redis vẫn chạy bước một, a còn 400, b không đổi, 100 biến mất. Khung ba, số lượng ghi bằng chữ hai: cột kiểu số từ chối ngay khi ghi; cột tài liệu JSON nhận cả ba dòng, lỗi hiện ra khi đọc để cộng tổng; Redis nhận mà không hỏi. Khung bốn, đọc kết quả.](../../diagrams/sd-04-024-main.svg)

## Từ viết tắt

- **ACID** (Atomicity, Consistency, Isolation, Durability) — nguyên tử, nhất quán, cô lập, bền vững: bốn tính chất của giao dịch trong cơ sở dữ liệu quan hệ; "nguyên tử" nghĩa là hoặc mọi bước cùng có hiệu lực, hoặc không bước nào.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc của cơ sở dữ liệu quan hệ; nằm trong tên PostgreSQL.
- **JSON** (JavaScript Object Notation) — định dạng dữ liệu dạng chữ gồm các cặp tên và giá trị; cột `jsonb` của PostgreSQL lưu tài liệu theo định dạng này.

## Đọc hình

**Khung 1 · Ba câu hỏi về lời hứa.** Hướng dẫn "Understand data models" của Azure Architecture Center so các loại theo đúng những điểm này:

- **Phạm vi nguyên tử.** Cơ sở dữ liệu quan hệ hỗ trợ giao dịch ACID trên nhiều dòng. Kho tài liệu hứa nguyên tử trong một tài liệu, kho khóa–giá trị trong một khóa.
- **Lược đồ.** Cơ sở dữ liệu quan hệ kiểm lược đồ khi ghi (schema on write). Kho tài liệu và kho khóa–giá trị để chương trình đọc tự hiểu dữ liệu (schema on read).
- **Mở rộng.** Muốn mở rộng ngang, cơ sở dữ liệu quan hệ thường phải chia shard hoặc chia partition; hướng dẫn ghi kho khóa–giá trị có điểm mạnh là mở rộng tuyến tính.

**Khung 2 · Thử: chuyển 100 từ a sang b, bước hai hỏng.** Bước một trừ 100 của a (a có 500); bước hai cộng 100 vào b nhưng hỏng. Với PostgreSQL, b có 0 và số tiền ở bước hai được truyền là chữ "một trăm". Với Redis, b đang giữ chuỗi "không phải số", nên lệnh cộng 100 vào b hỏng khi `EXEC` chạy.

| | PostgreSQL 16, một giao dịch | Redis 7, gói lệnh `MULTI` … `EXEC` |
|---|---|---|
| Bước hai | lỗi `invalid input syntax for type integer` | lỗi `value is not an integer or out of range` |
| Bước một | bị hủy cùng cả giao dịch | vẫn có hiệu lực |
| Sau cùng | a = 500, b = 0 | a = 400, b không đổi |

Với PostgreSQL, tài liệu hướng dẫn gọi giao dịch là thao tác "tất cả hoặc không gì": lỗi ở bất kỳ bước nào làm cả giao dịch không có hiệu lực. Với Redis, tài liệu về giao dịch viết rõ: lỗi xảy ra khi `EXEC` đang chạy không được xử lý đặc biệt, các lệnh khác vẫn chạy, và Redis không hỗ trợ rollback, để giữ sự đơn giản và tốc độ. 100 đồng đã rời a mà không tới b.

**Khung 3 · Thử: số lượng ghi là chữ "hai".**

- **Cột kiểu số** (`qty int`): lệnh ghi bị từ chối ngay, cùng lỗi `invalid input syntax for type integer`.
- **Cột tài liệu** (`doc jsonb`): ba dòng đều được ghi, gồm một dòng `"qty": "hai"` và một dòng dùng tên trường khác (`so_luong`). Lỗi chỉ hiện ra lúc đọc, khi truy vấn cộng tổng `qty` ép chữ "hai" thành số; dòng thiếu trường `qty` thì lặng lẽ không được cộng.
- **Redis**: một hash `line:2` nhận `qty = hai` mà không hỏi gì.

Lược đồ khi ghi bắt lỗi ở chỗ nó sinh ra; lược đồ khi đọc đẩy việc kiểm tra sang mọi chương trình đọc dữ liệu đó.

## Giới hạn cần nhớ

- Đây là lời hứa mặc định của hai sản phẩm cụ thể. Redis có `WATCH` để hủy cả giao dịch khi khóa đang theo dõi bị đổi trước `EXEC`; PostgreSQL có thể chứa tài liệu `jsonb` như thử nghiệm cho thấy. Tên loại không thay được việc đọc tài liệu của sản phẩm bạn chọn.
- Thử nghiệm không đo câu hỏi thứ ba (mở rộng); phần đó lấy từ hướng dẫn Azure.

## Nhìn hình trả lời

Một ứng dụng ví điện tử lưu số dư của mọi người trong Redis và chuyển tiền bằng một gói lệnh `MULTI` … `EXEC` gồm "trừ người gửi, cộng người nhận". Nhìn khung 2: điều gì có thể xảy ra, và loại nào hợp với phần số dư?

<details>
<summary>Xem đáp án</summary>

Nếu lệnh cộng cho người nhận hỏng khi đang chạy, lệnh trừ người gửi vẫn có hiệu lực và tiền biến mất, như a mất 100 trong thử nghiệm. Số dư cần giao dịch nhiều dòng, tất cả hoặc không gì: đó là lời hứa của cơ sở dữ liệu quan hệ (hướng dẫn Azure xếp "giao dịch nhiều thực thể chặt chẽ" vào loại này). Redis vẫn hợp để đệm phần đọc nhiều như số dư hiển thị, miễn là bản gốc nằm ở nơi có giao dịch.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn chỉ có một câu dẫn: cần hiểu đặc điểm, lựa chọn phổ biến và trường hợp dùng của từng loại; phần còn lại nằm trong hình, và bài này không dùng hình đó. Thay vì liệt kê lại các loại, bài chọn hai đặc điểm thử được ngay (phạm vi nguyên tử, nơi kiểm lược đồ) và một đặc điểm lấy từ tài liệu (cách mở rộng).

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/understanding-database-types.md): các loại cơ sở dữ liệu, đặc điểm và trường hợp dùng.
- [Azure Architecture Center — Understand data models, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/data-guide/technology-choices/understand-data-store-models.md): giao dịch nhiều dòng của cơ sở dữ liệu quan hệ, phạm vi nguyên tử và cách kiểm lược đồ của từng loại, cách mở rộng. Đọc từ bản clone của kho.
- [PostgreSQL 16 — Transactions, tại commit cố định](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/advanced.sgml): giao dịch là thao tác tất cả hoặc không gì.
- [Redis — Transactions, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/using-commands/transactions.md): lỗi sau `EXEC` không dừng các lệnh khác, không có rollback, `WATCH`.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 với PostgreSQL 16.15, Redis 7.0.15, psycopg 3.3.6 và redis-py 8.1.0 trên một máy.
Bài viết và hình được thiết kế độc lập.

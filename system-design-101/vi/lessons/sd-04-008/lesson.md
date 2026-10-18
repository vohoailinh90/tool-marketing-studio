# Sáu mẫu quản lý dữ liệu: bản nào là gốc, bản nào là dẫn xuất

**Cache-aside, materialized view, index table, CQRS, event sourcing và sharding giải sáu bài toán khác nhau.**
Cách đọc nhanh nhất là hỏi mỗi mẫu làm gì với dữ liệu gốc. Cache, materialized view và index table thêm một bản dẫn xuất; CQRS dùng hai kho và event sourcing dựng projection để đọc cũng vậy. Với mọi bản dẫn xuất, câu hỏi là nó được làm mới khi nào và cũ được bao lâu. Sharding thì khác: nó không tạo bản sao nào mà chia chính bản gốc, nên câu hỏi của nó là chia theo khóa nào.

![Ba khung. Khung một, ba mẫu đọc nhanh nhờ một bản dữ liệu thứ hai: cache-aside đọc cache trước, trượt thì đọc kho rồi nạp vào cache, cũ tới khi hết hạn hoặc bị xóa; materialized view lưu sẵn kết quả một truy vấn nặng và cũ tới lần làm mới, thử nghiệm thấy 70 khi bảng gốc đã là 100; index table là bảng phụ sắp theo khóa khác, phải cập nhật cùng bảng gốc. Khung hai, ba mẫu đổi cách lưu: CQRS tách mô hình ghi và đọc, ở hai kho thì mô hình đọc theo sau; event sourcing lấy chuỗi sự kiện làm bản gốc, view dựng từ đó có thể cũ; sharding chia chính bản gốc theo khóa shard, lo ngại là shard nóng. Khung ba, với mọi bản dẫn xuất: làm mới khi nào, cũ được bao lâu, ai sửa khi lệch.](../../diagrams/sd-04-008-main.svg)

## Từ viết tắt

- **CQRS** (Command Query Responsibility Segregation) — tách trách nhiệm lệnh và truy vấn: mô hình xử lý lệnh ghi tách khỏi mô hình phục vụ truy vấn đọc.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc của cơ sở dữ liệu quan hệ; nằm trong tên PostgreSQL, nơi chạy thử nghiệm.

## Đọc hình

**Khung 1 · Đọc nhanh nhờ bản thứ hai.**

- **Cache-aside:** ứng dụng hỏi cache trước; không có thì đọc kho gốc, đưa vào cache rồi trả về. Khi ghi, ứng dụng sửa kho gốc rồi xóa mục trong cache. Theo Azure Architecture Center, mẫu này không bảo đảm cache khớp kho: một tiến trình khác sửa kho thì cache không biết cho tới lần nạp sau.
- **Materialized view:** lưu sẵn kết quả một truy vấn tốn kém, như tổng doanh thu theo ngày. Truy vấn nhanh, nhưng dữ liệu chỉ mới bằng lần làm mới gần nhất.
- **Index table:** thêm bảng sắp theo một khóa khác (ví dụ theo thành phố thay vì theo mã khách) để tra nhanh trên kho không có chỉ mục phụ. Bảng gốc và bảng phụ không cập nhật được trong cùng giao dịch thì phải thiết kế theo nhất quán sau cùng.

**Khung 2 · Đổi cách lưu.**

- **CQRS:** mô hình ghi lo kiểm tra nghiệp vụ, mô hình đọc trả dữ liệu dựng sẵn cho màn hình. Hai mô hình có thể dùng chung một kho; chỉ khi chúng ở hai kho thì mô hình đọc mới là bản dẫn xuất và theo sau mô hình ghi.
- **Event sourcing:** không ghi đè trạng thái mà nối sự kiện vào một kho chỉ ghi thêm; chuỗi sự kiện là bản gốc, trạng thái hiện tại có được bằng cách phát lại. Phát lại tốn kém nên thường đi kèm materialized view, và chính view đó mới là bản dẫn xuất có thể cũ.
- **Sharding:** chia chính bản gốc ra nhiều kho theo khóa shard, không tạo bản dẫn xuất. Theo Azure Architecture Center, khóa tốt không đổi theo thời gian, có nhiều giá trị khác nhau, chia đều tải, và khớp với truy vấn chính để phần lớn yêu cầu chỉ chạm một shard. Lo ngại của nó là shard nóng (một shard gánh phần tải lớn bất thường) và việc dời dữ liệu khi cân bằng lại.

## Thử nghiệm: materialized view cũ tới lần làm mới

Trên PostgreSQL 16.15, bảng `sales` có ba dòng; view `sales_by_day` cộng doanh thu theo ngày.

| Bước | Bảng gốc, ngày 18 | View, ngày 18 |
|---|---|---|
| Tạo view | 70 | 70 |
| Thêm một đơn 30 vào ngày 18 | 100 | 70 |
| `REFRESH MATERIALIZED VIEW sales_by_day` | 100 | 100 |

Tài liệu PostgreSQL nói thẳng: đọc materialized view thường nhanh hơn nhiều, nhưng dữ liệu không phải lúc nào cũng mới.

## Giới hạn cần nhớ

Mỗi bản dẫn xuất cần một cơ chế làm mới, và cơ chế đó có thể hỏng âm thầm: Azure Architecture Center cảnh báo nếu tín hiệu làm mới view bị mất hay trễ, view cứ thế trả kết quả cũ. Nên theo dõi tuổi của bản dẫn xuất và báo động khi nó cũ quá mức cho phép.

## Nhìn hình trả lời

Trang chủ của một cửa hàng hiện "Top 10 sản phẩm bán chạy hôm nay", truy vấn nặng, chạy mỗi lần có người mở trang. Chọn mẫu nào trong khung 1, và phải trả lời câu hỏi gì trước khi làm?

<details>
<summary>Xem đáp án</summary>

Materialized view (hoặc cache-aside cho kết quả truy vấn). Trước khi làm phải quyết định danh sách được phép cũ bao lâu, ví dụ vài phút, rồi chọn cách làm mới theo đó: theo lịch, hay theo sự kiện bán hàng.
Danh sách bán chạy cũ vài phút thường chấp nhận được; số tồn kho khi thanh toán thì không, nên đừng đọc tồn kho từ cùng bản dẫn xuất.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn định nghĩa sáu mẫu, mỗi mẫu một đoạn, theo cùng thứ tự trong hình. Bài này gom chúng theo việc chúng làm với dữ liệu (thêm bản dẫn xuất hay đổi cách lưu), thêm câu hỏi chung về độ cũ, và chạy thử một mẫu.
Phần định nghĩa và cân nhắc của từng mẫu lấy từ các trang mẫu của Azure Architecture Center, không lấy từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-manage-data.md): sáu mẫu quản lý dữ liệu.
- Azure Architecture Center, tại commit cố định, đọc từ bản clone của kho: [Cache-Aside](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/cache-aside-content.md), [Materialized View](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/materialized-view.md), [Index Table](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/index-table.md), [CQRS](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/cqrs.md), [Event Sourcing](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/event-sourcing.md), [Sharding](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/sharding.md).
- [PostgreSQL 16 — chương The Rule System, mục Materialized Views, tại commit cố định](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/rules.sgml): kết quả lưu dạng bảng, dữ liệu không phải lúc nào cũng mới.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên PostgreSQL 16.15.
Bài viết và hình được thiết kế độc lập.

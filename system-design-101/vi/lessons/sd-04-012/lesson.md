# Event sourcing khác thiết kế CRUD ở đâu: lưu trạng thái hay lưu chuyện đã xảy ra

**Thiết kế CRUD giữ trạng thái mới nhất và ghi đè mỗi khi có thay đổi; event sourcing giữ chuỗi sự kiện và tính trạng thái từ chuỗi đó.**
Cùng một đơn hàng đi qua đặt, trả tiền, hoàn tiền và hủy, hai cách lưu trả lời rất khác nhau câu hỏi "lúc 10:05 đơn này thế nào".

![Ba khung. Khung một, thiết kế CRUD: một hàng của đơn hàng bị ghi đè qua các bước đặt hàng, thanh toán, hoàn tiền và hủy; cuối cùng hàng ghi cancelled, số tiền 500, cập nhật lúc 10:21, không còn dấu vết đơn từng được trả tiền. Khung hai, event sourcing: bốn sự kiện được nối vào luồng của đơn, OrderPlaced lúc 10:00, OrderPaid lúc 10:03, PaymentRefunded lúc 10:20, OrderCancelled lúc 10:21; không sự kiện nào bị sửa. Khung ba, điều đo được: phát lại tới 10:05 thì đơn ở trạng thái paid, đã trả 500; phát lại tới 10:30 thì cancelled, còn 0; hai bên cùng nối sự kiện số 5 thì bên sau bị khóa chính chặn.](../../diagrams/sd-04-012-main.svg)

## Từ viết tắt

- **CRUD** (Create, Read, Update, Delete) — tạo, đọc, sửa, xóa: kiểu thiết kế phổ biến trong đó mỗi bản ghi giữ trạng thái hiện tại và được sửa tại chỗ.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc của cơ sở dữ liệu quan hệ; nằm trong tên PostgreSQL, nơi chạy thử nghiệm.

## Đọc hình

**Khung 1 · CRUD.** Một hàng `orders_crud` được thêm khi đặt hàng rồi bị sửa ba lần. Cuối cùng hàng ghi `cancelled`, số tiền 500, cập nhật lúc 10:21. Hàng đó không cho biết đơn từng được trả tiền và đã hoàn tiền, cũng không trả lời được đơn ở trạng thái nào lúc 10:05.

**Khung 2 · Event sourcing.** Bảng `order_events` chỉ được thêm, không bao giờ sửa: bốn sự kiện, mỗi sự kiện mang số thứ tự trong luồng của đơn. Theo Azure Architecture Center, muốn hủy tác dụng một sự kiện thì thêm một sự kiện bù trừ (ở đây là `PaymentRefunded`), không sửa hay xóa sự kiện cũ.

**Khung 3 · Đo được.** Trạng thái là kết quả phát lại các sự kiện theo thứ tự. Phát lại các sự kiện tới 10:05 cho `paid`, đã trả 500; tới 10:30 cho `cancelled`, còn 0.
Khóa chính `(order_id, seq)` làm luôn việc kiểm soát ghi đồng thời: hai bên cùng nghĩ luồng đang ở sự kiện 4 và cùng nối sự kiện 5, bên sau bị từ chối với lỗi "duplicate key value violates unique constraint". Đây là khóa lạc quan, chỉ là trên số thứ tự sự kiện thay vì cột phiên bản.

## Giới hạn cần nhớ

Azure Architecture Center gọi event sourcing là một mẫu phức tạp, tốn kém khi chuyển sang hoặc bỏ đi. Những cái giá chính:

- **Đọc phải dựng lại.** Phát lại cả luồng mỗi lần đọc thì đắt, nên thường kèm ảnh chụp trạng thái (snapshot) định kỳ và materialized view cho truy vấn; các bản dẫn xuất đó chỉ nhất quán sau cùng.
- **Sự kiện sai thì nằm đó mãi.** Sửa lỗi trong mã không sửa được sự kiện đã ghi; phải thêm sự kiện bù trừ hoặc chuyển đổi khi phát lại.
- **Lược đồ sự kiện phải tiến hóa được.** Sự kiện cũ vẫn phải đọc được khi định dạng đổi, nên cần đánh phiên bản cho sự kiện.

## Nhìn hình trả lời

Kế toán hỏi: "Tháng trước có bao nhiêu đơn đã thu tiền rồi mới bị hoàn?" Thiết kế nào trả lời được ngay, và vì sao thiết kế kia không?

<details>
<summary>Xem đáp án</summary>

Event sourcing: đếm các đơn có cả `OrderPaid` và `PaymentRefunded` trong tháng. Thiết kế CRUD chỉ còn trạng thái cuối `cancelled`, không phân biệt được đơn bị hủy trước khi trả tiền với đơn đã trả rồi được hoàn, trừ khi đã có sẵn một bảng lịch sử riêng ghi lại từng thay đổi.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Thân bài nguồn chỉ có ba đoạn ngắn: nêu câu hỏi, nói hình so sánh CRUD với event sourcing bằng một hệ thống thương mại điện tử đặt và trả tiền đơn hàng, và nói event sourcing giúp thiết kế hệ thống có tính tất định. Nội dung so sánh nằm trong hình của nguồn, bài này không dùng hình đó.
Toàn bộ ví dụ, thử nghiệm và phần giới hạn là của bài này, dựa trên trang Event Sourcing của Azure Architecture Center.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/differences-in-event-sourcing-system-design.md): so sánh thiết kế CRUD với event sourcing qua đơn hàng và thanh toán.
- [Azure Architecture Center — Event Sourcing pattern, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/event-sourcing.md): kho chỉ thêm, trạng thái từ phát lại, sự kiện bù trừ, nhất quán sau cùng của các bản dẫn xuất, đánh phiên bản sự kiện, ảnh chụp trạng thái, khi nào không nên dùng. Đọc từ bản clone của kho.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên PostgreSQL 16.15; hai bảng là ví dụ tối giản, không phải một kho sự kiện chuyên dụng.
Bài viết và hình được thiết kế độc lập.

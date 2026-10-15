# 8 gợi ý thiết kế API hiệu quả

**Một API tốt là API mà người khác đoán được cách dùng.** Tám gợi ý dưới đây là các quy ước hay gặp khi thiết kế API REST; hình minh họa bằng một API đơn hàng.

![Tám khung dọc, mỗi khung một gợi ý kèm ví dụ trên API đơn hàng: đường dẫn theo nghiệp vụ như /orders; ít phương thức HTTP và dùng đúng nghĩa, PATCH cần thống nhất cách vá; gọi lại không gây trùng, POST kèm Idempotency-Key; một tập nhỏ mã trạng thái ghi trong tài liệu; đánh phiên bản từ đầu như /v1/orders; đường dẫn là danh từ số nhiều nhất quán; xử lý hàng loạt qua /orders/batch trả kết quả từng mục; truy vấn thống nhất để lọc, sắp xếp và phân trang. Đây là quy ước, không phải chuẩn.](../../diagrams/sd-01-015-main.svg)

## Đọc hình

1. **Đường dẫn theo miền nghiệp vụ.** Đặt tên theo khái niệm của nghiệp vụ (`/orders`, `/orders/42/items`), không theo tên hàm hay bảng nội bộ.
2. **Ít phương thức HTTP, dùng đúng nghĩa.** GET đọc, POST tạo, PUT thay cả đối tượng, DELETE xóa. PATCH sửa một phần nên đội phải thống nhất cách mô tả phần sửa; chưa thống nhất thì đừng dùng.
3. **Gọi lại không gây trùng.** GET, PUT và DELETE vốn idempotent: lặp lại cho cùng hiệu ứng trên máy chủ. POST thì không, nên cần thiết kế thêm, thường bằng khóa gửi kèm.
4. **Ít mã trạng thái, dùng nhất quán.** Chọn một tập nhỏ, đúng nghĩa, và ghi trong tài liệu.
5. **Phiên bản từ đầu.** Đưa phiên bản vào API ngay từ bản đầu (`/v1/orders`) để sau này đổi mà không làm vỡ client cũ.
6. **Đường dẫn dễ đoán.** Danh từ, số nhiều, cách đặt tên nhất quán, để người dùng tìm đúng API trong tài liệu.
7. **Xử lý hàng loạt.** Gom nhiều thao tác vào một lời gọi bằng từ khóa `batch` hoặc `bulk` ở cuối đường dẫn, và trả kết quả của từng mục.
8. **Truy vấn thống nhất.** Mọi danh sách dùng chung quy tắc lọc, sắp xếp và phân trang (`?status=paid&limit=20`).

## Giới hạn cần nhớ

Đây là quy ước của người viết, không phải chuẩn; nhiều điểm còn tranh luận, như việc dùng PATCH hay có động từ trong đường dẫn. Chọn cách nào cũng được, miễn dùng đồng nhất và ghi rõ. Một vài điểm có cái giá: phân trang theo `offset` bị lệch khi dữ liệu thay đổi giữa hai lần gọi (con trỏ `cursor` ổn định hơn); một lời gọi hàng loạt có thể thành công một phần nên phải định nghĩa kết quả từng mục; phiên bản không cần tăng cho thay đổi chỉ thêm trường.

## Nhìn hình thử trả lời

Ứng dụng gọi `POST /orders` để đặt hàng, quá hạn chờ và gọi lại. Điều gì có thể xảy ra, và thiết kế nào tránh được?

<details>
<summary>Xem đáp án</summary>

Lần gọi đầu có thể đã tạo đơn nhưng phản hồi bị mất, nên lần gọi lại tạo thêm một đơn trùng. Cách tránh: client gửi kèm một khóa duy nhất (như header `Idempotency-Key`); máy chủ nhớ khóa và trả lại kết quả cũ khi gặp lại, thay vì tạo đơn mới.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Idempotent là về hiệu ứng, không phải phản hồi:** DELETE lần hai có thể trả 404 mà vẫn idempotent. Chuẩn HTTP coi PUT, DELETE và các phương thức an toàn là idempotent; POST và PATCH thì không mặc định như vậy.
- **`Idempotency-Key`:** hiện là bản nháp của nhóm làm việc HTTPAPI tại IETF, chưa phải RFC; nhiều nhà cung cấp dùng một cơ chế tương tự theo cách riêng. Nếu cùng khóa nhưng nội dung khác, bản nháp gợi ý trả 422; nếu lần đầu còn đang xử lý, trả 409.
- **PATCH:** có hai định dạng vá phổ biến, JSON Merge Patch và JSON Patch; chọn một và ghi rõ.
- **Lỗi có cấu trúc:** nên có định dạng thân lỗi thống nhất, như problem details của IETF.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/8-tips-for-efficient-api-design.md).
- [RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#name-idempotent-methods): phương thức idempotent; [§15.5.10 (409)](https://www.rfc-editor.org/rfc/rfc9110.html#name-409-conflict) và [§15.5.21 (422)](https://www.rfc-editor.org/rfc/rfc9110.html#name-422-unprocessable-content).
- [Bản nháp Idempotency-Key](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/) của nhóm HTTPAPI.
- [RFC 5789](https://www.rfc-editor.org/rfc/rfc5789) (PATCH), [RFC 7396](https://www.rfc-editor.org/rfc/rfc7396) (JSON Merge Patch), [RFC 6902](https://www.rfc-editor.org/rfc/rfc6902) (JSON Patch) và [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) (problem details).

Đã đọc nguồn ngày 2026-10-15. Định nghĩa idempotent, mô tả 409 và 422 được đối chiếu với bản RFC 9110 và bản nháp Idempotency-Key; các RFC về PATCH và problem details chưa được mở để đối chiếu trực tiếp. Bài viết và hình được thiết kế độc lập.

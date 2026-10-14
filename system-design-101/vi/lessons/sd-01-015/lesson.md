# 8 gợi ý thiết kế API hiệu quả

**API là hợp đồng giữa người viết và người dùng.** Hợp đồng càng nhất quán thì người dùng càng đoán được hành vi mà không phải hỏi. Tám gợi ý dưới đây theo kiểu REST/HTTP; mỗi cái là một quyết định nên chốt sớm.

![Tám khung dọc, mỗi khung một gợi ý: đường dẫn theo miền dùng danh từ như /orders/42/items; phương thức đúng như GET đọc, POST tạo, PUT thay; idempotent nghĩa là gửi lại có cùng tác động lên máy chủ như gửi một lần, đúng với GET, PUT, DELETE còn POST dùng Idempotency-Key; mã trạng thái ít và nhất quán, 201 nên kèm Location khi tạo mới; phiên bản như /v1/orders hoặc header; tên dễ hiểu dạng danh từ số nhiều; thao tác hàng loạt như POST /orders/batch trả kết quả từng phần tử; truy vấn với lọc, sắp xếp và phân trang.](../../diagrams/sd-01-015-main.svg)

## Đọc hình

1. **Đường dẫn theo miền.** Cấu trúc đường dẫn phản ánh mô hình nghiệp vụ: `/orders/42/items` là các mục của đơn 42. Hành động nằm ở phương thức HTTP, không nằm trong đường dẫn.
2. **Phương thức đúng.** `GET` đọc (client không yêu cầu thay đổi trạng thái; máy chủ vẫn có thể có tác dụng phụ như ghi nhật ký), `POST` tạo hoặc thực hiện thao tác, `PUT` thay toàn bộ, `DELETE` xóa. `PATCH` sửa một phần, nhưng cần quy ước rõ vì cách dùng khác nhau giữa các nhóm.
3. **Idempotent.** Gửi lại cùng yêu cầu thì tác động dự kiến lên máy chủ vẫn như gửi một lần (RFC 9110); phản hồi có thể khác, ví dụ `DELETE` lần đầu trả 204 còn lần sau trả 404. `GET`, `PUT`, `DELETE` theo định nghĩa là idempotent; `POST` thì không. Để client thử lại an toàn, cho `POST` nhận một khóa và nhớ kết quả. Ví dụ là header `Idempotency-Key`: nó chưa phải chuẩn, từng được mô tả trong một Internet-Draft của IETF (bản thảo có thể đã hết hạn hoặc đổi), nên cách dùng cụ thể lấy theo tài liệu của dịch vụ như Stripe.
4. **Mã trạng thái.** Dùng một tập nhỏ, nhất quán: 200, 201 (nên kèm `Location` trỏ tới tài nguyên mới), 204, 400, 401, 403, 404, 409, 429, 500; kèm thân lỗi cùng một định dạng.
5. **Phiên bản.** Quyết sớm: trong đường dẫn (`/v1/...`) hoặc trong header. Thay đổi làm vỡ client thì ra phiên bản mới và giữ bản cũ một thời gian.
6. **Tên dễ hiểu.** Danh từ số nhiều, nhất quán, để tìm trong tài liệu và đoán được tên của API chưa gặp.
7. **Hàng loạt.** Nhiều thao tác trong một yêu cầu, ví dụ `POST /orders/batch`; cần định nghĩa rõ trường hợp thành công một phần và kích thước tối đa.
8. **Truy vấn.** Quy tắc lọc, sắp xếp, phân trang thống nhất: `?status=paid&sort=-created_at&limit=20`. Phân trang bằng con trỏ thường ổn định hơn offset khi dữ liệu đang thay đổi.

## Giới hạn cần nhớ

Không có "cách đúng duy nhất": REST là một phong cách, và nhiều hệ thống chọn RPC hay GraphQL vì lý do riêng. Điều quan trọng là nhất quán và có tài liệu. Các gợi ý này cũng không thay cho xác thực, phân quyền và giới hạn tốc độ.

## Nhìn hình thử trả lời

Client gọi `POST /payments`, hết thời gian chờ và gửi lại. Rủi ro là gì, và gợi ý nào giải quyết?

<details>
<summary>Xem đáp án</summary>

Máy chủ có thể đã xử lý lần đầu nên lần gửi lại tạo thanh toán trùng. Gợi ý 3: client gửi kèm một `Idempotency-Key` cố định cho cả hai lần; máy chủ nhận ra yêu cầu lặp và trả lại kết quả cũ thay vì tạo mới.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Lỗi có cấu trúc:** có chuẩn định dạng thân lỗi chung (problem details) để client xử lý thống nhất.
- **429:** khi vượt giới hạn tốc độ, trả 429 và nói khi nào được thử lại (`Retry-After`).
- **PATCH:** không mặc định idempotent; thiết kế cách dùng cụ thể trước khi cho client thử lại.
- **Đường dẫn và hành động:** khi một thao tác không khớp động từ HTTP nào, có thể coi nó là một tài nguyên con (ví dụ `POST /orders/42/cancellation`).

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/8-tips-for-efficient-api-design.md).
- [RFC 9110 — Ngữ nghĩa HTTP](https://www.rfc-editor.org/rfc/rfc9110) (phương thức, idempotent, mã trạng thái), [RFC 5789 — PATCH](https://www.rfc-editor.org/rfc/rfc5789), [RFC 6585 — 429](https://www.rfc-editor.org/rfc/rfc6585) và [RFC 9457 — Problem Details](https://www.rfc-editor.org/rfc/rfc9457).
- [Stripe — Idempotent requests](https://docs.stripe.com/api/idempotent_requests) và [IETF — Idempotency-Key header](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/).
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines) và [Google API Design Guide](https://cloud.google.com/apis/design).

Đã đọc bản nguồn ByteByteGo ngày 2026-10-13; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

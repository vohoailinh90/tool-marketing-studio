# REST API hoạt động thế nào?

**REST coi mọi thứ là tài nguyên có địa chỉ, và hai bên chỉ trao đổi "bản trình bày" của tài nguyên đó.** Bài này đi theo một yêu cầu từ client tới máy chủ, rồi nêu các ràng buộc khiến kiểu API này dễ mở rộng.

![Năm khung dọc: tài nguyên có địa chỉ riêng như /orders/42; yêu cầu gồm phương thức, đường dẫn và header; máy chủ không nhớ yêu cầu trước nên mỗi yêu cầu tự đủ thông tin; phản hồi gồm mã trạng thái, header và bản trình bày JSON, có thể kèm chỉ dẫn cache; các ràng buộc gồm client và máy chủ tách biệt, phi trạng thái, cache được, giao diện thống nhất và phân tầng. REST là phong cách chứ không phải chuẩn.](../../diagrams/sd-01-017-main.svg)

## Đọc hình

1. **Tài nguyên và địa chỉ.** Một đơn hàng, một người dùng hay một danh sách đều là tài nguyên, mỗi cái có URL riêng, ví dụ `/orders/42`. Địa chỉ nói *cái gì*; *làm gì* nằm ở phương thức HTTP.
2. **Yêu cầu.** Gồm phương thức và đường dẫn (`GET /orders/42`), các header (như `Accept` cho biết client muốn định dạng nào, `Authorization` mang thông tin xác thực) và thân nếu có, như với `POST` hay `PUT`.
3. **Máy chủ không nhớ phiên.** Mỗi yêu cầu mang đủ thông tin để hiểu và xử lý, nên bản sao máy chủ nào nhận cũng làm được. Vì thế API kiểu REST dễ đặt sau bộ cân bằng tải.
4. **Phản hồi.** Gồm mã trạng thái (`200`, `404`...), header (như `Content-Type`, `Cache-Control`, `ETag`) và thân là bản trình bày của tài nguyên, thường là JSON.
5. **Các ràng buộc.** Client và máy chủ tách việc giao diện khỏi lưu trữ; không giữ trạng thái phiên; phản hồi nói rõ có cache được không; mọi tài nguyên dùng chung một giao diện; giữa hai đầu có thể có nhiều tầng trung gian (proxy, gateway, CDN) mà client không cần biết.

## Giới hạn cần nhớ

REST là một phong cách kiến trúc do Roy Fielding mô tả, không phải giao thức hay chuẩn có chứng nhận. Nhiều API tự nhận là REST nhưng bỏ bớt ràng buộc, chẳng hạn không dùng siêu liên kết để dẫn client đi tiếp. "Phi trạng thái" không có nghĩa hệ thống không lưu dữ liệu: dữ liệu vẫn nằm trong cơ sở dữ liệu; chỉ trạng thái *của cuộc trao đổi* không nằm lại ở máy chủ. Mỗi yêu cầu phải mang thêm thông tin (như token) nên tốn thêm byte. REST cũng không quy định cách xác thực hay cách chia tài nguyên: thiết kế vẫn là việc của bạn.

## Nhìn hình thử trả lời

Trình duyệt và CDN lưu `GET /products/9` trong một giờ. Chủ shop đổi giá lúc 10:05 nhưng đến 10:30 khách vẫn thấy giá cũ. Ràng buộc nào của REST tạo ra tình huống này, và có những cách nào giảm tác hại?

<details>
<summary>Xem đáp án</summary>

Ràng buộc cache: phản hồi được phép dùng lại trong thời hạn mà `Cache-Control` cho phép (như `max-age`), nên bản cũ vẫn hợp lệ cho tới khi hết hạn. Cách giảm tác hại: đặt thời hạn ngắn cho dữ liệu hay đổi; dùng `ETag` để lần sau client hỏi lại bằng `If-None-Match` và nhận `304` nếu chưa đổi; dùng `no-cache` (phải hỏi lại máy chủ trước khi dùng) hoặc `no-store` (không lưu) cho dữ liệu không được cũ; xóa bản trong cache của CDN khi đổi giá.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Sáu ràng buộc của Fielding:** client–server, phi trạng thái, cache được, giao diện thống nhất, hệ thống phân tầng, và mã theo yêu cầu (tùy chọn, ví dụ máy chủ gửi script cho client chạy).
- **Giao diện thống nhất** gồm bốn ý: định danh tài nguyên, thao tác qua bản trình bày, thông điệp tự mô tả, và siêu phương tiện dẫn dắt trạng thái ứng dụng (HATEOAS).
- **Mô hình trưởng thành của Richardson:** cách xếp API HTTP theo mức, từ "một điểm vào cho mọi thứ", qua dùng tài nguyên, dùng đúng phương thức HTTP, đến dùng siêu liên kết. Nhiều API dừng ở mức giữa mà vẫn hữu ích.
- **Xác thực:** REST không quy định. Cách phổ biến là khóa API (nhận diện ứng dụng), HTTP Basic (tên và mật khẩu, chỉ nên dùng qua TLS) và token mang danh (Bearer) cấp theo OAuth 2.0; JWT chỉ là một định dạng token. Xác thực (bạn là ai) khác phân quyền (bạn được làm gì).

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-rest-api-work.md): bản nguồn chỉ có một hình và một câu hỏi; bài này viết từ mô tả REST của Fielding và các RFC về HTTP.
- [Fielding — Kiểu kiến trúc REST (chương 5 luận án)](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm).
- [RFC 9110 — Ngữ nghĩa HTTP](https://www.rfc-editor.org/rfc/rfc9110) và [RFC 9111 — HTTP caching](https://www.rfc-editor.org/rfc/rfc9111).
- [RFC 7617 — HTTP Basic](https://www.rfc-editor.org/rfc/rfc7617), [RFC 6749 — OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749), [RFC 6750 — Bearer token](https://www.rfc-editor.org/rfc/rfc6750) và [RFC 7519 — JWT](https://www.rfc-editor.org/rfc/rfc7519).
- [Martin Fowler — Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html).

Đã đọc bản nguồn ByteByteGo ngày 2026-10-13; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

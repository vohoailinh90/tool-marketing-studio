# Vì sao HTTP/2 nhanh hơn HTTP/1?

HTTP/2 giữ nguyên ý nghĩa của yêu cầu và phản hồi; thứ thay đổi là cách đóng gói và gửi chúng qua mạng. Nhờ vậy nhiều tài nguyên có thể dùng chung một kết nối thay vì xếp hàng chờ nhau.

![HTTP/1.1 xử lý lần lượt từng yêu cầu trên mỗi kết nối nên trình duyệt phải mở thêm kết nối; HTTP/2 chia thông điệp thành khung nhị phân, đan xen khung của nhiều luồng trên một kết nối. Năm đặc điểm: khung nhị phân, dồn luồng, ưu tiên luồng, server push, nén header HPACK. Giới hạn: một gói TCP mất làm mọi luồng trên kết nối cùng chờ.](../../diagrams/sd-01-009-main.svg)

- **Khung nhị phân:** HTTP/1.1 gửi thông điệp dạng văn bản; HTTP/2 cắt thông điệp thành các khung nhị phân nhỏ, mỗi khung gắn với một luồng.
- **Dồn luồng (multiplexing):** khung của nhiều yêu cầu và phản hồi đan xen trên một kết nối TCP, rồi được ráp lại ở phía nhận. Một phản hồi chậm không chặn các phản hồi khác ở tầng HTTP.
- **Ưu tiên luồng:** client có thể gợi ý luồng nào quan trọng hơn để server cân nhắc khi gửi. Đây chỉ là gợi ý, server không bắt buộc làm theo.
- **Server push:** server có thể gửi trước tài nguyên mà client chưa yêu cầu. Trong thực tế tính năng này ít được dùng và một số trình duyệt đã bỏ hỗ trợ.
- **Nén header (HPACK):** header lặp lại giữa các yêu cầu được gửi dưới dạng gọn, nhờ bảng mà hai bên cùng giữ, nên tốn ít băng thông hơn.

**Đọc hình:** hai thẻ đầu so sánh cách gửi: mỗi ô là một đoạn dữ liệu của một tài nguyên (A, B, C). Năm thẻ sau là các đặc điểm của HTTP/2. Thẻ cuối là giới hạn: HTTP/2 nhanh hơn trong nhiều trường hợp, không phải mọi trường hợp.

## Nhìn hình thử trả lời

Một trang cần tải 30 tệp nhỏ. Trình duyệt dùng HTTP/1.1 thường phải mở nhiều kết nối song song; HTTP/2 xử lý việc này khác đi thế nào? Và nếu một gói TCP bị mất giữa chừng, các luồng còn lại trên kết nối đó bị ảnh hưởng ra sao?

<details>
<summary>Xem đáp án</summary>

HTTP/2 gửi cả 30 yêu cầu thành 30 luồng trên một kết nối, khung của chúng đan xen nhau, nên cần ít kết nối hơn và không phải xếp hàng từng yêu cầu. Nhưng TCP giao dữ liệu theo đúng thứ tự: khi một gói bị mất, mọi luồng trên kết nối đó phải chờ gói được gửi lại mới đi tiếp. Đây là tắc nghẽn đầu hàng ở tầng TCP; HTTP/3 chạy trên QUIC để tránh điều này.

</details>

## Giới hạn cần nhớ

HTTP/2 không tự làm trang nhanh. Lợi ích phụ thuộc vào mạng, số lượng và kích thước tài nguyên, cách server và CDN cấu hình. Muốn biết có nhanh hơn thật không, hãy đo trên đúng kịch bản của mình thay vì suy từ hình.

<details>
<summary>Xem sâu hơn</summary>

- **Ngữ nghĩa không đổi:** phương thức, mã trạng thái, header và URL vẫn như HTTP/1.1. Vì thế ứng dụng thường không phải sửa mã khi server hoặc CDN bật HTTP/2; thay đổi nằm ở cách đóng gói trên đường truyền.
- **Vì sao HTTP/1.1 phải mở nhiều kết nối:** mỗi kết nối xử lý lần lượt từng yêu cầu. Chuẩn có pipelining nhưng trình duyệt hầu như không dùng, nên trình duyệt thường mở vài kết nối song song tới mỗi máy chủ (con số thường gặp là khoảng sáu). Mỗi kết nối thêm là một lần bắt tay, và nếu có TLS thì thêm một lần thương lượng.
- **Thủ thuật cũ có thể hết tác dụng:** chia nhỏ tài nguyên ra nhiều tên miền để tăng số kết nối song song (domain sharding) hay gộp mọi thứ thành tệp lớn là cách giảm cú chạm mạng của HTTP/1.1. Với HTTP/2, chia tên miền thường phản tác dụng vì làm mất lợi thế dùng chung một kết nối; gộp tệp vẫn có thể hợp lý nhưng cần cân nhắc với bộ nhớ đệm.
- **Ưu tiên luồng đã đổi cách làm:** cơ chế ưu tiên ban đầu của HTTP/2 (cây phụ thuộc và trọng số) bị phiên bản chuẩn mới hơn coi là lỗi thời; có một cách ưu tiên mới, đơn giản hơn, dùng chung cho HTTP/2 và HTTP/3. Hỗ trợ giữa các server và trình duyệt không đồng đều.
- **HPACK nén thế nào:** hai bên giữ một bảng các header đã thấy. Header lặp lại như cookie hay user-agent chỉ cần gửi chỉ số trỏ vào bảng, phần mới được mã hóa gọn.
- **Trên trình duyệt thường đi kèm TLS:** các trình duyệt chỉ dùng HTTP/2 qua kết nối TLS, được thương lượng bằng ALPN. Bản HTTP/2 không mã hóa có trong chuẩn nhưng ít được trình duyệt hỗ trợ.

HTTP/3 thay TCP bằng QUIC để giải quyết tắc nghẽn đầu hàng ở tầng vận chuyển; chi tiết của nó nằm ngoài bài nhập môn này.

</details>

## Nguồn đối chiếu

Thân bài nguồn đã được đọc ở snapshot cố định để xác định phạm vi; phần diễn đạt, ví dụ, hình và các lưu ý về giới hạn là viết mới. Các claim dựa vào tiêu chuẩn và tài liệu công khai dưới đây, chưa kiểm được trong phiên này.

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-makes-http2-faster-than-http1.md) (chủ đề của mục này).
- IETF: [RFC 9113 (HTTP/2)](https://www.rfc-editor.org/rfc/rfc9113.html), [RFC 7541 (HPACK)](https://www.rfc-editor.org/rfc/rfc7541.html), [RFC 9218 (ưu tiên mở rộng)](https://www.rfc-editor.org/rfc/rfc9218.html), [RFC 9114 (HTTP/3)](https://www.rfc-editor.org/rfc/rfc9114.html).
- Tài liệu: [MDN: Evolution of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Evolution_of_HTTP), [Chrome: removing HTTP/2 Server Push](https://developer.chrome.com/blog/removing-push).

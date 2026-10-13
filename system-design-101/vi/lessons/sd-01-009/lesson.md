# Vì sao HTTP/2 nhanh hơn HTTP/1?

**HTTP/2 giữ nguyên ý nghĩa của HTTP (phương thức, mã trạng thái, header) và chỉ đổi cách đóng gói, gửi dữ liệu qua mạng.** Nhờ đó nhiều yêu cầu dùng chung một kết nối thay vì xếp hàng chờ nhau. Nhanh hơn ở đâu, và khi nào thì không, là nội dung bài này.

![Năm thẻ dọc. Thẻ một, HTTP/1.1: một kết nối xử lý một yêu cầu một lúc nên trình duyệt phải mở thêm kết nối. Thẻ hai, khung nhị phân: mỗi thông điệp cắt thành khung gắn số hiệu luồng. Thẻ ba, ghép kênh: một kết nối chở nhiều luồng, vẽ sáu khung A1, B1, A2, C1, B2, A3 của ba luồng A, B, C xen kẽ nhau. Thẻ bốn, nén header bằng HPACK: header lặp lại chỉ gửi dạng rút gọn. Thẻ năm, ưu tiên luồng và server push: đều có lưu ý khi dùng thực tế. Chú thích: mất một gói TCP vẫn làm mọi luồng chờ, HTTP/3 sửa điều này.](../../diagrams/sd-01-009-main.svg)

## Đọc hình

**1. HTTP/1.1.** Dòng đầu và các header của thông điệp là văn bản; phần thân có thể là bất kỳ dữ liệu nào, như ảnh hay video. Trên một kết nối, mỗi lúc thực tế chỉ có một yêu cầu đang chờ phản hồi (HTTP/1.1 có “pipelining” nhưng trình duyệt gần như không dùng). Một phản hồi chậm ở đầu hàng làm các yêu cầu sau phải chờ, gọi là **head-of-line blocking** ở tầng HTTP. Trình duyệt bù bằng cách mở nhiều kết nối song song tới cùng một máy chủ (thường khoảng sáu), còn nhà phát triển gộp file, ghép ảnh hay chia tên miền để lách giới hạn đó.

**2. Khung nhị phân.** HTTP/2 cắt thông điệp thành các **khung (frame)** nhị phân thay vì gửi nguyên khối chữ: header đi trong khung HEADERS, thân đi trong khung DATA. Mỗi khung mang số hiệu của **luồng (stream)** mà nó thuộc về (một số khung điều khiển dùng luồng số 0, tức cả kết nối); một luồng ứng với một cặp yêu cầu–phản hồi. Riêng việc dùng dạng nhị phân chỉ giúp máy đọc gọn và ít nhập nhằng hơn; lợi ích lớn đến từ việc khung cho phép bước tiếp theo.

**3. Ghép kênh (multiplexing).** Khung của nhiều luồng được gửi xen kẽ trên cùng một kết nối TCP rồi ráp lại ở đầu bên kia. Một phản hồi lớn hay chậm không còn chặn các phản hồi khác ở tầng HTTP (dù băng thông vẫn là chung), và trình duyệt thường chỉ cần một kết nối cho mỗi nguồn gốc.

**4. Nén header (HPACK).** Header của các yêu cầu liên tiếp thường lặp lại (cookie, user-agent…). HPACK giữ ở hai đầu một bảng các header đã gặp và gửi phần lặp bằng chỉ số ngắn, nên tiết kiệm băng thông, nhất là khi có nhiều yêu cầu nhỏ.

**5. Ưu tiên luồng và server push.** Nguồn liệt kê hai tính năng này là lý do HTTP/2 nhanh; trong thực tế cả hai đều có lưu ý, xem phần dưới.

## Giới hạn cần nhớ

HTTP/2 không nhanh hơn trong mọi tình huống; nguồn cũng nhắc phải đo và tối ưu. **Mất gói:** mọi luồng dùng chung một kết nối TCP, nên một gói bị mất làm TCP chờ gửi lại và cả các luồng cùng dừng; trên mạng hay mất gói, một kết nối HTTP/2 có thể không hơn nhiều kết nối HTTP/1.1. HTTP/3 chạy trên QUIC để các luồng không chặn nhau ở tầng vận chuyển. **Ưu tiên luồng:** cơ chế ban đầu (trọng số và phụ thuộc giữa các luồng) đã bị RFC 9113 đánh dấu lỗi thời; một cơ chế ưu tiên khác được mô tả trong RFC 9218, và mức hỗ trợ khác nhau giữa trình duyệt và máy chủ. **Server push:** máy chủ gửi trước tài nguyên mà nó đoán là sắp cần, nhưng khó đoán đúng (dễ gửi thứ trình duyệt đã có trong bộ nhớ đệm), và một số trình duyệt lớn như Chrome đã ngừng hỗ trợ, nên đừng dựa vào nó.

## Nhìn hình trả lời

Một trang tải 40 file nhỏ. Với HTTP/1.1 người ta hay gộp chúng thành vài file lớn. Vì sao với HTTP/2 việc gộp thường quan trọng ít hơn, và vì sao vẫn không nên bỏ gộp hàng loạt mà không đo?

<details>
<summary>Xem đáp án</summary>

Ghép kênh cho phép gửi nhiều yêu cầu nhỏ cùng lúc trên một kết nối, và HPACK làm mỗi yêu cầu tốn ít header hơn, nên cái giá của nhiều file nhỏ giảm đi. Nhưng mạng mất gói, kích thước file và bộ nhớ đệm vẫn ảnh hưởng kết quả, nên cần đo trước khi đổi.

</details>

<details>
<summary>Xem sâu hơn: khung, luồng, HPACK, TLS và HTTP/3</summary>

- **Khung và luồng:** khung có nhiều loại; ví dụ khung HEADERS mang header và khung DATA mang thân thông điệp. Mỗi luồng có số hiệu riêng, các luồng chạy đồng thời trên một kết nối.
- **Kiểm soát lưu lượng:** HTTP/2 có kiểm soát lưu lượng (flow control) riêng cho từng luồng và cho cả kết nối, để một luồng không chiếm hết bộ đệm của bên nhận.
- **HPACK:** dùng một bảng tĩnh các header phổ biến, một bảng động theo từng kết nối và mã hóa Huffman cho chuỗi. Nó được thiết kế riêng thay vì dùng nén tổng quát như DEFLATE, vì cách nén đó từng bị khai thác trong các tấn công kiểu CRIME.
- **TLS:** chuẩn cho phép HTTP/2 không mã hóa, nhưng trên web các trình duyệt thường chỉ dùng HTTP/2 qua TLS (HTTPS), và hai bên thương lượng giao thức khi bắt tay TLS.
- **HTTP/3:** giữ nguyên ngữ nghĩa HTTP nhưng chạy trên QUIC (qua UDP); mất gói chỉ làm chậm luồng bị ảnh hưởng chứ không dừng cả kết nối.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-makes-http2-faster-than-http1.md): năm tính năng của HTTP/2 và lưu ý rằng cần đo trong từng tình huống.
- [RFC 9113 — HTTP/2](https://www.rfc-editor.org/rfc/rfc9113.html): khung, luồng, ghép kênh, kiểm soát lưu lượng; ưu tiên cũ bị đánh dấu lỗi thời.
- [RFC 7541 — HPACK](https://www.rfc-editor.org/rfc/rfc7541.html): nén header của HTTP/2.
- [RFC 9218 — Ưu tiên mở rộng cho HTTP](https://www.rfc-editor.org/rfc/rfc9218.html): cơ chế ưu tiên thay thế.
- [RFC 9112 — HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112.html): pipelining và mô hình yêu cầu–phản hồi của HTTP/1.1.
- [MDN — Quản lý kết nối trong HTTP/1.x](https://developer.mozilla.org/en-US/docs/Web/HTTP/Connection_management_in_HTTP_1.x): nhiều kết nối song song và pipelining ít được dùng.
- [Chrome — Gỡ HTTP/2 server push](https://developer.chrome.com/blog/removing-push): lý do và thời điểm Chrome ngừng hỗ trợ push.
- [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114.html): HTTP trên QUIC.
- [RFC 9000 — QUIC](https://www.rfc-editor.org/rfc/rfc9000.html): luồng độc lập khi mất gói.
- [Can I use — HTTP/2](https://caniuse.com/http2): mức hỗ trợ HTTP/2 của trình duyệt.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-01-009.json).

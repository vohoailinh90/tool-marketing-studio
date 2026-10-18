# HTTP/1.1, HTTP/2, HTTP/3: dữ liệu chờ nhau ở đâu?

**Giữ ý nghĩa yêu cầu–phản hồi, đổi cách truyền.** Trang thư viện tải ảnh bìa và danh mục cùng lúc. Ba phiên bản tổ chức việc truyền khác nhau; số phiên bản không phải cam kết trang luôn nhanh hơn.

![Ba thẻ so sánh trong một kết nối: HTTP/1.1 trên TCP có phản hồi theo thứ tự; HTTP/2 trên TCP xen kẽ nhiều luồng nhưng mất gói có thể làm các luồng cùng chờ; HTTP/3 trên QUIC chạy trên UDP tách việc giao dữ liệu giữa các luồng nhưng từng luồng vẫn có thể chờ.](../../diagrams/sd-01-037-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức trao đổi yêu cầu và phản hồi trên web.
- **TCP** (Transmission Control Protocol) — giao thức truyền tải cung cấp dòng byte tin cậy, đúng thứ tự; HTTP/1.1 và HTTP/2 dùng nó.
- **UDP** (User Datagram Protocol) — giao thức gửi gói, tự nó không bảo đảm giao đủ hoặc đúng thứ tự; giao thức phía trên có thể bổ sung các khả năng đó.
- **QUIC** (Quick UDP Internet Connections) — tên khai triển lịch sử; ở đây là tên giao thức truyền tải chuẩn mà HTTP/3 dùng, có giao dữ liệu tin cậy theo từng luồng trên UDP.

## Đọc hình

- **HTTP/1.1:** tái sử dụng kết nối TCP. Có thể gửi nhiều yêu cầu trước khi chờ phản hồi bằng pipelining, nhưng phản hồi trên kết nối đó phải theo thứ tự yêu cầu. Một phản hồi dài có thể giữ các phản hồi sau chờ.
- **HTTP/2:** chia thông điệp thành khung để xen kẽ nhiều luồng trên một kết nối TCP. Tuy vậy, mất dữ liệu trong dòng TCP có thể giữ dữ liệu của nhiều luồng cùng chờ truyền lại.
- **HTTP/3:** dùng QUIC trên UDP. Dữ liệu thiếu của một luồng không buộc luồng khác đợi vì thứ tự giao dữ liệu ở tầng truyền tải. Trong chính luồng bị thiếu, dữ liệu vẫn phải được phục hồi và giao đúng thứ tự.

## Nhìn hình thử trả lời

Ảnh bìa mất một gói, còn danh mục nằm trên luồng khác của cùng kết nối HTTP/3. Danh mục có bắt buộc đợi ảnh bìa chỉ vì thứ tự giao dữ liệu truyền tải không?

<details>
<summary>Xem đáp án</summary>

Không. QUIC tách việc giao dữ liệu theo luồng. Nhưng danh mục vẫn có thể chậm vì máy chủ, nghẽn mạng hoặc phụ thuộc ở tầng ứng dụng; hình không bảo đảm nó hoàn tất ngay.

</details>

<details>
<summary>Giới hạn trước khi chọn phiên bản</summary>

Hình so sánh một kết nối, không nói HTTP/1.1 chỉ mở được một kết nối. Máy khách có thể dùng nhiều kết nối để giảm việc chờ nhau, đổi lại thêm tài nguyên.

HTTP/3 không bỏ qua gói bị mất chỉ vì dùng UDP: QUIC bổ sung độ tin cậy. Nhiều luồng vẫn dùng chung đường mạng và tài nguyên; không suy thành độc lập hiệu năng hoàn toàn. Khi mạng chặn UDP, kết nối QUIC có thể thất bại; máy khách nên thử phiên bản HTTP trên TCP. Cần đo trên tải và mạng thật, không áp một bảng tốc độ chung.

</details>

## Nguồn đối chiếu

- [ByteByteGo — body ghim](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/http1-http2-http3.md): chủ đề ba phiên bản; không dùng ảnh nguồn hoặc lấy năm trong bài làm mốc chuẩn hóa.
- [HTTP/1.1 §9.3.2–9.4](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3.2): pipelining và nhiều kết nối.
- [HTTP/2 §1](https://www.rfc-editor.org/rfc/rfc9113.html#section-1): khung, ghép luồng và giới hạn chặn ở TCP.
- [HTTP/3 §1–3](https://www.rfc-editor.org/rfc/rfc9114.html#section-1): luồng QUIC, giao dữ liệu tin cậy và khả năng mạng chặn UDP.
- [Chromium — QUIC hiện hành](https://www.chromium.org/quic/) và [tên khai triển lịch sử năm 2013](https://blog.chromium.org/2013/06/experimenting-with-quic.html): không đồng nhất bản thử nghiệm ban đầu với giao thức chuẩn hiện nay.

Đã đọc body ghim và các mục chuẩn cho claim ngày 2026-10-16. Ví dụ thư viện và hình tự thiết kế; chưa đo ba phiên bản trên dịch vụ thật hoặc thử với người học.

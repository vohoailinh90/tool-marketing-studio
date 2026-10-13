# Vì sao HTTP/2 nhanh hơn HTTP/1?

**HTTP/2 nhanh hơn nhờ đổi cách đóng gói và gửi thông điệp, không nhờ một mẹo riêng lẻ.**
Nhưng vài tính năng hay được nêu đã thay đổi, và “nhanh hơn” còn tùy tình huống.

![Ba nhóm xếp dọc. Cải tiến so với HTTP/1.1: khung nhị phân chia thông điệp thành khung; ghép luồng cho nhiều yêu cầu song song trên một kết nối; nén header bằng HPACK. Cần cập nhật: cơ chế ưu tiên luồng gốc đã bị bỏ và có chuẩn thay thế; Server Push bị Chrome tắt mặc định từ bản 106. Giới hạn: vẫn một kết nối TCP, mất gói có thể làm mọi luồng cùng chờ.](../../diagrams/sd-01-009-main.svg)

## Đọc hình

**Khung nhị phân.** Thông điệp được chia thành các khung (frame) mã hóa nhị phân thay vì văn bản.
Máy xử lý hiệu quả hơn, nhưng người không đọc trực tiếp được.

**Ghép luồng.** Nhiều cặp yêu cầu–phản hồi chạy song song trên một kết nối, các khung xen kẽ nhau.
Một luồng chậm không chặn luồng khác. HTTP/1.x phải mở nhiều kết nối để làm việc song song.

**Nén header.** HPACK giảm phần header lặp lại giữa các yêu cầu.

**Ưu tiên luồng.** Cơ chế báo mức ưu tiên của bản đầu đã bị bỏ trong bản HTTP/2 mới. Chuẩn thay thế là RFC 9218.

**Server Push.** Server gửi trước tài nguyên mà client chưa hỏi. Thực tế ít được dùng: Chrome tắt nó mặc định
từ bản 106 và đề nghị dùng 103 Early Hints hoặc preload.

## Giới hạn cần nhớ

HTTP/2 vẫn chạy trên một kết nối TCP. Khi mất gói tin, TCP cho cả kết nối chờ truyền lại, nên mọi luồng cùng chậm.
Đặc tả HTTP/2 tự ghi rằng nó không giải quyết chuyện này; HTTP/3 chạy trên QUIC để tránh nó.
Vì vậy hãy đo trên tình huống thật thay vì mặc định HTTP/2 luôn nhanh hơn.

## Nhìn hình trả lời

Một trang tải 30 tài nguyên nhỏ qua mạng hay mất gói. Ghép luồng giúp được gì, và còn giới hạn nào?

<details>
<summary>Xem đáp án</summary>

Ghép luồng cho phép gửi các yêu cầu song song trên một kết nối, không cần mở nhiều kết nối.
Giới hạn: mất gói ở tầng TCP vẫn có thể làm mọi luồng cùng chờ.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn liệt kê ưu tiên luồng và Server Push như hai tính năng làm HTTP/2 nhanh. Bản HTTP/2 mới (RFC 9113)
tuyên bố bỏ cơ chế báo ưu tiên của bản đầu, và Chrome đã tắt Server Push mặc định.

HTTP/1.1 có pipelining, nhưng đặc tả HTTP/2 nói nó chỉ giải quyết một phần việc gửi song song
và vẫn bị chặn đầu hàng ở tầng ứng dụng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-makes-http2-faster-than-http1.md): năm tính năng.
- [Đặc tả HTTP/2 (RFC 9113) — bản nguồn của nhóm HTTP](https://github.com/httpwg/http2-spec/blob/main/draft-ietf-httpbis-http2bis.xml): khung nhị phân, ghép luồng, bỏ cơ chế ưu tiên cũ, Server Push, chặn đầu hàng TCP.
- [HPACK (RFC 7541) — bản nguồn](https://github.com/httpwg/http2-spec/blob/main/draft-ietf-httpbis-header-compression.xml): nén header cho HTTP/2.
- [MDN — Evolution of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Evolution_of_HTTP): nhị phân, ghép luồng, nén header; HTTP/3 và QUIC.
- [Chrome — removing push](https://developer.chrome.com/blog/removing-push) và [RFC 9218](https://www.rfc-editor.org/rfc/rfc9218): tắt Server Push; chuẩn ưu tiên thay thế. Hai trang này không mở được; nội dung đối chiếu qua trích đoạn tìm kiếm.

Đã đọc nguồn ngày 2026-10-13. Đặc tả HTTP/2 và HPACK được đọc từ bản clone của kho httpwg/http2-spec,
MDN từ kho mdn/content. Bài viết và hình được thiết kế độc lập.

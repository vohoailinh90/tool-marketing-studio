# Vì sao HTTP/2 nhanh hơn HTTP/1?

**Một trang web cần hàng chục tệp.** Cách gửi chúng qua kết nối quyết định trang hiện nhanh hay chậm. HTTP/2 đổi chính cách đó, nên thường nhanh hơn HTTP/1.1.

![Ba khung dọc: HTTP/1.1 mỗi kết nối chỉ xử lý một yêu cầu một lúc nên muốn song song phải mở thêm kết nối, trình duyệt thường giới hạn khoảng sáu; HTTP/2 dùng một kết nối với nhiều luồng được chia thành khung xen kẽ và nén header bằng HPACK; vẫn còn giới hạn vì cùng chạy trên một kết nối TCP, mất gói thì mọi luồng chờ, và HTTP/3 chạy trên QUIC để giảm điều đó.](../../diagrams/sd-01-009-main.svg)

## Đọc hình

**HTTP/1.1.** Trên một kết nối, một yêu cầu phải xong thì yêu cầu kế mới đi (cơ chế gửi nối tiếp pipelining có, nhưng thực tế gần như không dùng). Muốn tải song song, trình duyệt mở nhiều kết nối tới cùng máy chủ, thường giới hạn khoảng sáu, và mỗi kết nối tốn thời gian thiết lập.

**HTTP/2.** Dùng *một* kết nối. Mỗi yêu cầu và phản hồi là một *luồng*, chia thành các *khung* nhị phân. Khung của nhiều luồng xen kẽ trên cùng kết nối, nên một tệp chậm không chặn các tệp khác ở tầng HTTP. Trong hình, mỗi ô là một khung; cùng màu và cùng chữ cái là cùng một luồng (A1 và A2 thuộc luồng A). Header lặp lại được nén bằng *HPACK*, tiết kiệm băng thông khi có nhiều yêu cầu nhỏ.

**Ưu tiên luồng** cho phép ưu tiên tệp quan trọng (như CSS) trước ảnh.

## Giới hạn cần nhớ

HTTP/2 không luôn nhanh hơn rõ rệt. Nó giúp nhiều khi trang gồm nhiều tệp nhỏ; một tệp lớn duy nhất ít khác biệt. Vì mọi luồng dùng chung một kết nối TCP, mất một gói TCP làm *mọi* luồng phải chờ gửi lại; trên mạng hay mất gói, đôi khi HTTP/2 chậm hơn HTTP/1.1. Đó là lý do HTTP/3 chuyển sang QUIC. Số luồng chạy đồng thời cũng có giới hạn: mỗi bên công bố một mức qua `SETTINGS_MAX_CONCURRENT_STREAMS`, và mức đó giới hạn số luồng do bên kia mở, nên không phải mọi yêu cầu chạy cùng một lúc. Cần đo trên trang thật thay vì mặc định.

## Nhìn hình thử trả lời

Một trang tải 40 tệp nhỏ qua HTTP/1.1 với sáu kết nối. HTTP/2 giúp gì, và còn điểm yếu nào?

<details>
<summary>Xem đáp án</summary>

Giúp: gửi các yêu cầu trên một kết nối, xen kẽ (trong giới hạn số luồng đồng thời), không phải xếp hàng sau sáu kết nối, và header được nén. Điểm yếu: cùng một kết nối TCP, nên mất gói làm mọi luồng chậm lại.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Nhị phân và văn bản:** HTTP/1.1 là văn bản; HTTP/2 mã hóa thành khung nhị phân, dễ máy xử lý hơn. Ý nghĩa của yêu cầu và phản hồi (phương thức, mã trạng thái) giữ nguyên.
- **Server push:** ý tưởng gửi trước tài nguyên chưa được hỏi. Thực tế khó dùng đúng và ít hiệu quả; một số trình duyệt lớn đã gỡ hỗ trợ.
- **Ưu tiên:** cách đặt ưu tiên theo trọng số của bản đầu tiên về sau được thay bằng cách mới; hành vi thật tùy trình duyệt và máy chủ.
- **Trình duyệt và TLS:** trình duyệt chỉ dùng HTTP/2 qua TLS (thương lượng bằng ALPN); chuẩn vẫn cho phép chạy không mã hóa (h2c) nhưng trình duyệt không dùng.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-makes-http2-faster-than-http1.md).
- [RFC 9113 — HTTP/2](https://www.rfc-editor.org/rfc/rfc9113) và [RFC 7541 — HPACK](https://www.rfc-editor.org/rfc/rfc7541).
- [RFC 7301 — ALPN](https://www.rfc-editor.org/rfc/rfc7301), [RFC 9112 — HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112) và [RFC 9218 — Ưu tiên mở rộng](https://www.rfc-editor.org/rfc/rfc9218).
- [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114) và [RFC 9000 — QUIC](https://www.rfc-editor.org/rfc/rfc9000).

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

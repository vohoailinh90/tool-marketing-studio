# Làm cho một request chậm truy vết được

Muốn tìm vì sao một request chậm, bạn cần dữ liệu nối được với nhau. Bài này đi qua năm việc nhỏ khi gắn thiết bị đo cho dịch vụ, mỗi việc làm cho dữ liệu hữu ích hơn khi sự cố xảy ra.

![Năm việc khi làm cho một request chậm truy vết được: truyền header traceparent giữa các dịch vụ, ghi nhật ký có cấu trúc kèm trace_id, đo độ trễ bằng histogram thay cho trung bình, giữ nhãn số đo có giới hạn, và lấy mẫu vết có chủ đích.](../../diagrams/sd-13-021-main.svg)

**Đọc hình:** năm việc độc lập; cùng nhau chúng cho phép đi từ một con số bất thường tới đúng request và đúng dòng nhật ký.

## Từ viết tắt

- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản biểu diễn dữ liệu bằng các cặp tên và giá trị, dễ đọc với cả người và máy.
- **ID** (IDentifier) — mã định danh: chuỗi hoặc số dùng để phân biệt một đối tượng với các đối tượng khác, ví dụ một người dùng, một thông điệp hay một lượt xử lý.

## Nhìn hình thử trả lời

Độ trễ trung bình là 120 ms (mili giây, 1 ms bằng một phần nghìn giây) nhưng người dùng than chậm. Vì sao con số trung bình không phản ánh điều đó, và nên xem gì?

<details>
<summary>Xem đáp án</summary>

Trung bình bị kéo xuống bởi số đông request nhanh, che mất một phần nhỏ rất chậm. Hãy xem phân vị cao như p95 hoặc p99, tính từ histogram thay vì từ giá trị trung bình.

</details>

## Giới hạn cần nhớ

Không có bộ thiết bị đo đúng cho mọi hệ thống: truyền ngữ cảnh vết cần mọi dịch vụ trên đường đi cùng hợp tác, lấy mẫu làm mất một số vết, và nhật ký chi tiết tốn chi phí lưu trữ. Bắt đầu từ đường đi quan trọng nhất rồi mở rộng.

<details>
<summary>Xem sâu hơn</summary>

- **Trace Context:** chuẩn W3C (World Wide Web Consortium — tổ chức xây dựng chuẩn web) định nghĩa header `traceparent` có dạng `00-<trace-id>-<parent-id>-<cờ>`. Dịch vụ có thu thập vết (ví dụ qua thư viện đo lường như OpenTelemetry khi được bật) giữ nguyên `trace-id` và đặt `parent-id` của header gửi đi thành mã của hoạt động hiện tại của chính nó; chuẩn coi đây là cách đổi thường gặp nhất và nên là mặc định. Chuyển nguyên header đã nhận là việc điển hình của dịch vụ chuyển tiếp thuần như proxy, hoặc của dịch vụ chưa thu thập vết.
- **Nhật ký có cấu trúc:** mỗi dòng là một đối tượng (ví dụ JSON, tức JavaScript Object Notation — định dạng dữ liệu văn bản dạng khóa và giá trị) có trường như `trace_id`, `service`, `level`, để tìm kiếm chính xác thay vì đoán chuỗi.
- **Histogram:** chia độ trễ vào các khoảng; phân vị tính xấp xỉ từ các khoảng, nên chọn ranh giới khoảng quanh mục tiêu mức dịch vụ.
- **Nhãn:** mỗi tổ hợp giá trị nhãn là một chuỗi riêng, nên nhãn có vô hạn giá trị làm số chuỗi bùng nổ.
- **Lấy mẫu:** lấy mẫu theo đầu vết (quyết định ngay từ đầu) đơn giản nhưng có thể bỏ lỡ vết lỗi; lấy mẫu theo đuôi (quyết định sau khi vết hoàn tất) giữ được vết lỗi và chậm nhưng tốn tài nguyên hơn.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/logging-tracing-metrics.md).
- W3C: [Trace Context](https://www.w3.org/TR/trace-context/), riêng việc đổi trường traceparent ở [mục này](https://www.w3.org/TR/trace-context/#mutating-the-traceparent-field). OpenTelemetry: [context propagation](https://opentelemetry.io/docs/concepts/context-propagation/), [sampling](https://opentelemetry.io/docs/concepts/sampling/).
- Prometheus: [histograms và summaries](https://prometheus.io/docs/practices/histograms/), [đặt tên và nhãn](https://prometheus.io/docs/practices/naming/).

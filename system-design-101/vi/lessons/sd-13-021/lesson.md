# Gỡ lỗi bằng số đo, vết và nhật ký

Ba loại tín hiệu trả lời ba câu hỏi nối tiếp khi hệ thống có vấn đề: có vấn đề không, ở đâu, và vì sao.

![Quy trình gỡ lỗi ba bước: số đo cho biết có vấn đề không, vết cho biết chậm hoặc lỗi ở đoạn nào của chuỗi gọi, nhật ký cho biết chi tiết vì sao.](../../diagrams/sd-13-021-main.svg)

**Đọc hình:** thứ tự là thói quen gỡ lỗi, không phải bắt buộc; nhiều khi bạn bắt đầu từ nhật ký của một lỗi cụ thể.

## Nhìn hình thử trả lời

Bạn cần biết "độ trễ p99 của tuần trước tăng hay giảm". Dùng tín hiệu nào?

<details>
<summary>Xem đáp án</summary>

Số đo, vì đó là dữ liệu đã tổng hợp theo thời gian. Muốn biết một request cụ thể chậm ở đâu thì xem vết; muốn biết lỗi gì xảy ra thì đọc nhật ký.

</details>

## Giới hạn cần nhớ

Ba tín hiệu là cách phân loại, không phải ba hệ thống phải xây riêng. Giá trị lớn nhất đến khi chúng liên kết với nhau (cùng trace ID, cùng nhãn dịch vụ), và mỗi loại có chi phí lưu trữ khác nhau: nhật ký thường tốn nhất.

<details>
<summary>Xem sâu hơn</summary>

- **Số đo** gọn, rẻ để giữ lâu, hợp để phát hiện và cảnh báo.
- **Vết** cho thấy đường đi một request qua nhiều dịch vụ; cần mỗi dịch vụ truyền ngữ cảnh vết.
- **Nhật ký** chi tiết nhất; nên có định dạng chung để tìm kiếm.
- **OpenTelemetry** cung cấp API, SDK và giao thức chung cho cả ba loại tín hiệu.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/logging-tracing-metrics.md).
- OpenTelemetry: [signals](https://opentelemetry.io/docs/concepts/signals/), [observability primer](https://opentelemetry.io/docs/concepts/observability-primer/).

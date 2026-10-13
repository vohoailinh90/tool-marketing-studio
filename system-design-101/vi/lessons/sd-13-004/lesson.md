# Thu thập số đo: kéo hay đẩy

Số đo có thể được bộ thu thập kéo về hoặc được dịch vụ đẩy tới. Cách nào hợp tùy dịch vụ của bạn sống thế nào và nằm ở đâu.

![Ba tình huống và lựa chọn tương ứng: dịch vụ chạy lâu trong cụm thì kéo, tác vụ batch cấp dịch vụ thì đẩy qua Pushgateway, đích nằm sau tường lửa thì đặt agent trong mạng đó, kéo cục bộ rồi chuyển tiếp mẫu về bằng remote write.](../../diagrams/sd-13-004-main.svg)

**Đọc hình:** không có cách đúng cho mọi trường hợp; một hệ thống thật thường dùng cả hai.

## Nhìn hình thử trả lời

Một tác vụ batch chạy trên một máy cụ thể và chỉ có ý nghĩa với máy đó. Pushgateway có hợp không?

<details>
<summary>Xem đáp án</summary>

Không phải lựa chọn mặc định. Tài liệu Prometheus khuyên Pushgateway cho tác vụ cấp dịch vụ, không gắn với một máy hay instance; với tác vụ gắn với máy thì dùng textfile collector của Node Exporter. Textfile collector đọc mọi tệp `.prom` còn trong thư mục ở mỗi lần kéo, nên tác vụ hoặc một bước dọn dẹp phải xóa hoặc ghi đè tệp, nếu không số đo cũ vẫn được xuất mãi.

</details>

## Giới hạn cần nhớ

Với kéo, đích phải bật sẵn một địa chỉ phơi số đo và collector phải tới được nó. Với đẩy trực tiếp qua Pushgateway, Prometheus không tự sinh số đo `up` cho từng nguồn đẩy, nên bạn mất tín hiệu tự động "đích có còn sống không" (một hệ thống đẩy khác có thể gửi tín hiệu còn sống riêng, và agent kéo cục bộ rồi chuyển tiếp bằng remote write vẫn giữ `up`). Với mọi cách đẩy, bạn phải tự chặn việc đẩy quá nhiều làm quá tải kho. Pushgateway giữ số đo cho tới khi bị xóa, nên số đo cũ có thể ở lại nếu không dọn.

<details>
<summary>Xem sâu hơn</summary>

- **Kéo trong Prometheus:** cấu hình `scrape_configs`; đích thường tìm bằng service discovery (ví dụ `kubernetes_sd_config`) thay vì tệp ghi cứng, để danh sách theo kịp khi máy chủ thêm bớt.
- **Tín hiệu sẵn có:** mỗi lần kéo Prometheus ghi số đo `up` cho biết kéo có thành công không.
- **Pushgateway:** nhận số đo đẩy lên từ tác vụ ngắn rồi để Prometheus kéo từ chính nó; không phải cách đẩy chung cho mọi dịch vụ.
- **Agent và remote write:** agent vẫn kéo (scrape) đích trong mạng của nó rồi chuyển tiếp các mẫu đã thu; vì còn kéo cục bộ nên vẫn thấy tín hiệu `up`. Remote write không dành cho ứng dụng đẩy thẳng số đo của chính nó.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/push-vs-pull-in-metrics-collecting-systems.md).
- Prometheus: [tổng quan](https://prometheus.io/docs/introduction/overview/), [khi nào dùng Pushgateway](https://prometheus.io/docs/practices/pushing/), [cấu hình scrape](https://prometheus.io/docs/prometheus/latest/configuration/configuration/), [Agent mode](https://prometheus.io/docs/prometheus/latest/prometheus_agent/), [đặc tả Remote Write](https://prometheus.io/docs/specs/prw/remote_write_spec/).

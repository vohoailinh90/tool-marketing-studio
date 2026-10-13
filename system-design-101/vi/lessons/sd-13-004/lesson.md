# Thu thập số đo: kéo hay đẩy

Số đo có thể được bộ thu thập kéo về hoặc được dịch vụ đẩy tới. Cách nào hợp tùy dịch vụ của bạn sống thế nào và nằm ở đâu.

![Ba tình huống và lựa chọn tương ứng: dịch vụ chạy lâu trong cụm thì kéo, tác vụ batch cấp dịch vụ thì đẩy qua Pushgateway, đích nằm sau tường lửa thì đẩy hoặc đặt agent trong mạng đó.](../../diagrams/sd-13-004-main.svg)

**Đọc hình:** không có cách đúng cho mọi trường hợp; một hệ thống thật thường dùng cả hai.

## Nhìn hình thử trả lời

Một tác vụ batch chạy trên một máy cụ thể và chỉ có ý nghĩa với máy đó. Pushgateway có hợp không?

<details>
<summary>Xem đáp án</summary>

Không phải lựa chọn mặc định. Tài liệu Prometheus khuyên Pushgateway cho tác vụ cấp dịch vụ, không gắn với một máy hay instance; với tác vụ gắn với máy thì dùng textfile collector của Node Exporter để số đo không bị tồn tại mãi.

</details>

## Giới hạn cần nhớ

Với kéo, đích phải bật sẵn một địa chỉ phơi số đo và collector phải tới được nó. Với đẩy, bạn mất tín hiệu "đích có còn sống không" và phải tự chặn việc đẩy quá nhiều làm quá tải kho. Pushgateway giữ số đo cho tới khi bị xóa, nên số đo cũ có thể ở lại nếu không dọn.

<details>
<summary>Xem sâu hơn</summary>

- **Kéo trong Prometheus:** cấu hình `scrape_configs`; đích thường tìm bằng service discovery (ví dụ `kubernetes_sd_config`) thay vì tệp ghi cứng, để danh sách theo kịp khi máy chủ thêm bớt.
- **Tín hiệu sẵn có:** mỗi lần kéo Prometheus ghi số đo `up` cho biết kéo có thành công không.
- **Pushgateway:** nhận số đo đẩy lên từ tác vụ ngắn rồi để Prometheus kéo từ chính nó; không phải cách đẩy chung cho mọi dịch vụ.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/push-vs-pull-in-metrics-collecting-systems.md).
- Prometheus: [tổng quan](https://prometheus.io/docs/introduction/overview/), [khi nào dùng Pushgateway](https://prometheus.io/docs/practices/pushing/), [cấu hình scrape](https://prometheus.io/docs/prometheus/latest/configuration/configuration/).

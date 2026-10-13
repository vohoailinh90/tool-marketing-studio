# Năm chiến lược triển khai phổ biến

Gom năm chiến lược theo điều bạn quan tâm nhất: quay lui nhanh cỡ nào, và bao nhiêu người dùng thấy bản mới khi nó còn chưa được chứng minh.

![Ba nhóm theo cách quay lui: blue-green và feature toggle quay lui gần như tức thì, rolling và canary lộ dần và dừng giữa chừng, big bang lộ hết cùng lúc.](../../diagrams/sd-13-015-main.svg)

**Đọc hình:** không có nhóm nào tốt hơn cho mọi trường hợp; nhóm đầu thường tốn thêm tài nguyên hoặc công dọn dẹp.

## Nhìn hình thử trả lời

Chiến lược nào cho phép quay lui mà không phải triển khai lại mã?

<details>
<summary>Xem đáp án</summary>

Feature Toggle (tắt cờ) và Blue-Green (chuyển lại traffic về môi trường cũ), vì mã hoặc môi trường cũ vẫn còn sẵn.

</details>

## Giới hạn cần nhớ

Rolling, Canary và Blue-Green cho phép hai phiên bản cùng tồn tại, nên dữ liệu và giao tiếp phải tương thích hai chiều. Đổi lược đồ cơ sở dữ liệu thường phải chia nhiều bước.

<details>
<summary>Xem sâu hơn</summary>

- **Blue-Green:** tốn gấp đôi môi trường trong lúc chuyển.
- **Canary:** cần số đo để quyết định mở rộng hay dừng.
- **Rolling:** ít tốn tài nguyên thêm nhưng lỗi chỉ lộ dần, cần giám sát từng đợt.
- **Feature Toggle:** tách "triển khai" khỏi "phát hành"; cờ cũ tích lại thành nợ nếu không dọn.
- **Big Bang:** hợp với hệ thống nhỏ hoặc thay đổi không thể chạy song song.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-5-most-used-deployment-strategies.md).
- Martin Fowler: [BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html), [CanaryRelease](https://martinfowler.com/bliki/CanaryRelease.html), [Feature Toggles](https://martinfowler.com/articles/feature-toggles.html).

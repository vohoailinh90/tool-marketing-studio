# Năm chiến lược triển khai phổ biến

Mỗi chiến lược trả lời hai câu hỏi: ai thấy bản mới trước, và quay lại bản cũ nhanh cỡ nào.

![Năm thẻ: Big Bang thay tất cả một lần, Rolling thay từng nhóm, Blue-Green chuyển traffic giữa hai môi trường, Canary cho một phần nhỏ người dùng, Feature Toggle bật tắt bằng cờ trong mã.](../../diagrams/sd-13-015-main.svg)

**Đọc hình:** thứ tự từ trên xuống đi từ ít kiểm soát tới nhiều kiểm soát; đổi lại là cần thêm công cụ và việc theo dõi.

## Nhìn hình thử trả lời

Chiến lược nào cho phép "quay lại" mà không phải triển khai lại mã?

<details>
<summary>Xem đáp án</summary>

Feature Toggle (tắt cờ) và Blue-Green (chuyển lại traffic về môi trường cũ). Cả hai đổi hướng nhanh vì mã hoặc môi trường cũ vẫn còn sẵn.

</details>

## Giới hạn cần nhớ

Rolling, Canary và Blue-Green cho phép hai phiên bản cùng tồn tại, nên dữ liệu và giao tiếp phải tương thích hai chiều. Đổi lược đồ cơ sở dữ liệu thường cần chia nhiều bước thay vì một lần.

<details>
<summary>Xem sâu hơn</summary>

- **Big Bang:** hợp với hệ thống nhỏ hoặc thay đổi không thể chạy song song; quay lui nghĩa là triển khai lại bản cũ.
- **Rolling:** ít tốn tài nguyên thêm; lỗi chỉ lộ dần, cần giám sát từng đợt.
- **Blue-Green:** tốn gấp đôi môi trường trong lúc chuyển; lợi thế là quay lại tức thì.
- **Canary:** cần phân tích số đo để quyết định mở rộng hay dừng.
- **Feature Toggle:** tách "triển khai" khỏi "phát hành"; cờ cũ tích lại thành nợ kỹ thuật nếu không dọn.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-5-most-used-deployment-strategies.md).
- Martin Fowler: [BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html), [CanaryRelease](https://martinfowler.com/bliki/CanaryRelease.html), [Feature Toggles](https://martinfowler.com/articles/feature-toggles.html).

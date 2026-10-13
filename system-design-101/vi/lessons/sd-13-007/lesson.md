# Chín anti-pattern khi làm ứng dụng cloud-native

Chín lỗi thiết kế dễ gặp khi đưa ứng dụng lên cloud, gom thành ba nhóm: thiết kế, vận hành và hiệu quả.

![Ba thẻ nhóm: thiết kế (monolith cứng, trạng thái cục bộ, tài nguyên dùng chung), vận hành (hạ tầng sửa tay, bỏ CI/CD, quá nhiều dịch vụ không chiến lược), hiệu quả (bỏ qua chi phí, truy vấn dữ liệu kém, image phình to).](../../diagrams/sd-13-007-main.svg)

**Đọc hình:** đây là mẫu cần cân nhắc, không phải luật cấm; mỗi dòng đúng trong một bối cảnh cụ thể.

## Nhìn hình thử trả lời

Monolith luôn là anti-pattern trên cloud?

<details>
<summary>Xem đáp án</summary>

Không. Vấn đề là khi các phần gắn chặt đến mức không triển khai hay mở rộng riêng được. Một monolith chia module rõ ràng vẫn là lựa chọn hợp lý cho nhiều nhóm.

</details>

## Giới hạn cần nhớ

"Anti-pattern" phụ thuộc bối cảnh. Ví dụ tránh trạng thái trong tiến trình không có nghĩa hệ thống không có trạng thái: nó chuyển sang dịch vụ lưu trữ được quản lý đúng cách.

<details>
<summary>Xem sâu hơn</summary>

- **Hạ tầng bất biến:** thay vì sửa tại chỗ, tạo bản mới từ định nghĩa rồi thay thế, tránh cấu hình lệch giữa các máy.
- **Không trạng thái:** tiến trình dễ khởi động lại và nhân bản khi không giữ dữ liệu bền vững; dữ liệu nằm ở dịch vụ lưu trữ.
- **Dùng chung tài nguyên:** nhiều dịch vụ cùng ghi vào một cơ sở dữ liệu tạo điểm nghẽn và gắn chặt các nhóm với nhau.
- **Image nhỏ:** build nhiều giai đoạn và chỉ giữ thứ cần chạy giúp kéo và khởi động nhanh hơn.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-native-anti-patterns.md).
- [The Twelve-Factor App](https://12factor.net/).
- Martin Fowler: [ImmutableServer](https://martinfowler.com/bliki/ImmutableServer.html).
- AWS: [trụ cột tối ưu chi phí](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html).

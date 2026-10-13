# Vòng đời một tính năng có cờ: từ mã đã lên đến dọn cờ

Một tính năng mới đi qua vài điểm dừng, từ lúc mã được đưa lên đến lúc không còn cờ nào. Mỗi điểm dừng là một quyết định, và nhìn theo thứ tự đó giúp tách việc đưa mã lên khỏi việc cho người dùng thấy hành vi mới.

![Năm điểm dừng của một tính năng có cờ: mã lên với cờ tắt, thử nội bộ ở cả hai nhánh, mở dần cho một phần người dùng cố định với số đo và điều kiện dừng, mở hết và giữ cờ làm công tắc khẩn cấp một thời gian, rồi dọn cờ và nhánh cũ.](../../diagrams/sd-13-015-main.svg)

**Đọc hình:** đọc từ trên xuống; mỗi thẻ là một điểm dừng, và nếu tính năng bị hủy thì dừng ở đó rồi dọn cờ.

## Nhìn hình thử trả lời

Một bản triển khai có cả sửa lỗi không gắn cờ và một tính năng gắn cờ. Tắt cờ có đưa hệ thống về như trước bản triển khai không?

<details>
<summary>Xem đáp án</summary>

Không. Tắt cờ chỉ rút phần được gắn cờ; sửa lỗi, thay đổi cấu hình hay migration không gắn cờ vẫn còn. Muốn về như trước cần rút lại cả triển khai.

</details>

## Giới hạn cần nhớ

Cờ làm tăng số đường chạy cần kiểm thử: mỗi cờ thêm một nhánh, và tổ hợp nhiều cờ khó kiểm hết. Không phải thay đổi nào cũng gắn cờ được, ví dụ đổi lược đồ cơ sở dữ liệu hay nâng phiên bản thư viện, nên vẫn cần tương thích hai chiều và kế hoạch rút lại triển khai. Bài này không bàn cách thay Pod hay chuyển traffic giữa môi trường; xem bài về Deployment của Kubernetes và bài về rủi ro khi triển khai.

<details>
<summary>Xem sâu hơn</summary>

- **Cờ tắt mặc định:** hành vi mới nằm sau cờ và tắt khi mã lên; nên chọn giá trị dự phòng là hành vi cũ để lỗi đọc cờ không làm lộ tính năng chưa sẵn sàng.
- **Nhóm người dùng cố định:** chọn người dùng theo giá trị băm của mã định danh để một người luôn thấy cùng một phiên bản, không nhảy qua lại giữa các lần tải.
- **Hai nhánh đều phải kiểm thử:** cả cờ bật và cờ tắt, vì khi rút lại bạn sẽ chạy nhánh cũ.
- **Loại cờ khác nhau, tuổi thọ khác nhau:** cờ phát hành thường ngắn hạn và nên xóa sau khi mở hết; cờ vận hành, dùng làm công tắc khẩn cấp, có thể sống lâu hơn.
- **Dọn cờ:** đặt người chịu trách nhiệm và hạn xóa ngay khi tạo cờ; cờ cũ tích lại thành nợ kỹ thuật.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-5-most-used-deployment-strategies.md).
- Martin Fowler: [Feature Toggles](https://martinfowler.com/articles/feature-toggles.html).

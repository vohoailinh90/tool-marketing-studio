# CI/CD qua một hình đơn giản

CI gom mã vào một chỗ và kiểm tra ngay. CD đưa mã đã kiểm tra tới nơi dùng. Chữ D có hai nghĩa, và hình tách chúng ra.

![Commit vào kho dùng chung, CI build và kiểm thử, tạo sản phẩm build; sau đó rẽ hai nhánh: Continuous Delivery chờ người duyệt rồi lên production, Continuous Deployment tự lên production.](../../diagrams/sd-13-014-main.svg)

**Đọc hình:** hai thẻ cuối là hai lựa chọn khác nhau cho cùng một bước, không phải hai bước nối tiếp.

## Nhìn hình thử trả lời

Sau khi mọi kiểm thử qua, ai bấm nút đưa bản lên production trong Continuous Delivery, và trong Continuous Deployment?

<details>
<summary>Xem đáp án</summary>

Delivery: một người hoặc quy trình duyệt quyết định thời điểm. Deployment: hệ thống tự làm, không cần bấm.

</details>

## Giới hạn cần nhớ

CI/CD không phải là cài một công cụ. CI chỉ có ý nghĩa khi mọi người gộp mã thường xuyên và kiểm thử đủ tin cậy; không có kiểm thử tốt thì tự động hóa chỉ đưa lỗi lên nhanh hơn.

<details>
<summary>Xem sâu hơn</summary>

- **CI:** mỗi lần gộp mã đều build và chạy kiểm thử tự động; lỗi tích hợp lộ sớm khi còn nhỏ.
- **Continuous Delivery:** luôn giữ được một bản có thể phát hành; việc phát hành là quyết định kinh doanh.
- **Continuous Deployment:** mở rộng thêm một bước tự động lên production; cần giám sát và khả năng quay lui tốt.
- **Trong nhiều tài liệu**, "CD" được dùng cho cả hai nghĩa, nên nên hỏi lại hiểu theo nghĩa nào.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cicd-simplified-visual-guide.md).
- Martin Fowler: [Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html), [Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html).

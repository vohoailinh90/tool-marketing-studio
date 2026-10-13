# Giảm rủi ro khi triển khai: chọn theo nhu cầu

Chọn cách triển khai bằng cách hỏi bạn đang sợ điều gì nhất. Mỗi nỗi sợ có một cơ chế quen thuộc.

![Bốn thẻ nhu cầu và cách xử lý: hai dịch vụ đổi cùng lúc cần tương thích hai chiều, muốn rút lại trong vài giây thì dùng blue-green để quay về môi trường cũ hoặc cờ tính năng để rút phần gắn cờ, muốn lộ lỗi sớm với chi phí thấp dùng canary, muốn đo tác động sản phẩm dùng A/B test.](../../diagrams/sd-13-020-main.svg)

**Đọc hình:** thẻ đầu áp dụng bất kể cách nào bạn chọn ở các thẻ sau.

## Nhìn hình thử trả lời

Hai dịch vụ cùng đổi định dạng thông điệp giữa chúng. Canary hay blue-green có cứu được không nếu bản mới không đọc được thông điệp bản cũ?

<details>
<summary>Xem đáp án</summary>

Không. Khi hai phiên bản gặp nhau trong lúc chuyển, chúng phải hiểu nhau. Cần làm bản mới chấp nhận cả định dạng cũ và mới trước, rồi mới bỏ định dạng cũ ở bước sau.

</details>

## Giới hạn cần nhớ

Cách nào cũng có giá: blue-green cần môi trường song song đủ tải, canary cần giám sát tốt, cờ tính năng để lại nợ nếu không dọn. A/B test trả lời câu hỏi sản phẩm, không thay cho kiểm tra an toàn khi triển khai.

<details>
<summary>Xem sâu hơn</summary>

- **Tương thích hai chiều:** thêm trường mới là tùy chọn trước, chuyển người dùng sang, rồi mới xóa trường cũ.
- **Blue-green:** kiểm thử trên môi trường mới trước khi chuyển traffic; quay lui là chuyển lại.
- **Canary:** dừng và quay lui khi số đo của nhóm canary xấu hơn bản đối chứng.
- **A/B test:** dùng cờ tính năng để chỉ nhóm được chọn thấy tính năng, tránh đẩy nhầm cho mọi người.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-deploy-services.md).
- Martin Fowler: [BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html), [CanaryRelease](https://martinfowler.com/bliki/CanaryRelease.html), [Feature Toggles](https://martinfowler.com/articles/feature-toggles.html).

# Chuỗi CI/CD của Netflix đọc theo rủi ro

Thay vì liệt kê công cụ từng bước, hãy hỏi mỗi mảnh trong chuỗi của Netflix chặn loại rủi ro nào. Cách đọc này dùng lại được ở công ty nhỏ.

![Năm thẻ ghép rủi ro với cơ chế: lỗi mã với build và kiểm thử, lỗi môi trường với đóng gói image máy chủ, lỗi khi lên production với canary tự động, lỗi hạ tầng bất ngờ với công cụ chaos, lỗi lọt qua với giám sát và xử lý sự cố.](../../diagrams/sd-13-012-main.svg)

**Đọc hình:** tên công cụ lấy từ mô tả công khai trong nguồn, có thể đã đổi; cột ý nghĩa là phần nên mang theo.

## Nhìn hình thử trả lời

Kayenta khác gì với việc tự nhìn biểu đồ sau khi triển khai canary?

<details>
<summary>Xem đáp án</summary>

Kayenta so sánh số đo của canary với bản đối chứng theo quy tắc định trước và cho nhận định khách quan, thay vì dựa vào việc ai đó nhìn biểu đồ và cảm thấy ổn.

</details>

## Giới hạn cần nhớ

Công cụ của một công ty lớn gắn với quy mô và nhu cầu riêng. Nhóm nhỏ không cần chép công cụ, chỉ cần có một cơ chế cho mỗi loại rủi ro ở bảng trên.

<details>
<summary>Xem sâu hơn</summary>

- **Image máy chủ (AMI):** ứng dụng được đóng cùng môi trường vào một image rồi thay máy, nên máy chạy thật giống máy đã kiểm thử.
- **Spinnaker:** nền tảng triển khai mã nguồn mở do Netflix tạo ra, hỗ trợ chiến lược như canary.
- **Chaos:** công cụ như Chaos Monkey chủ động làm lỗi máy chủ để kiểm chứng khả năng chịu lỗi.
- **Không rõ hiện trạng:** nguồn là ảnh chụp tại một thời điểm; không suy ra công cụ nào Netflix còn dùng.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/netflix-tech-stack-cicd-pipeline.md).
- [Spinnaker](https://spinnaker.io/) và [Kayenta](https://github.com/spinnaker/kayenta).
- Netflix: [Atlas](https://github.com/Netflix/atlas), [Chaos Monkey](https://netflix.github.io/chaosmonkey/).

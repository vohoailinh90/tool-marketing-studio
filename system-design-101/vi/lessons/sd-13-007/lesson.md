# Tăng từ một lên ba bản sao thì ứng dụng hỏng: bốn giả định ẩn

Một dịch vụ chạy ổn với một bản sao thường ngầm giả định rằng nó là bản duy nhất. Tăng lên ba bản sao là cách nhanh nhất để lộ các giả định đó, và chính chúng cũng làm hỏng khi ứng dụng bị thay thế hay khởi động lại. Bài nêu bốn giả định hay gặp và cách gỡ từng cái.

![Bốn giả định ẩn vỡ khi tăng số bản sao: trạng thái nằm trong một bản sao như phiên đăng nhập, tệp tải lên và bộ nhớ đệm nên cần kho dùng chung; việc định kỳ nằm trong ứng dụng chạy ở mọi bản sao nên cần tách ra một nơi chạy hoặc dùng khóa; bộ đếm cục bộ sinh ID trùng giữa các bản sao nên cần cấp ID từ cơ sở dữ liệu hoặc dùng UUID; và nhiều bản sao cùng đọc hàng đợi nên một tin có thể được xử lý hai lần, cần bước xử lý idempotent.](../../diagrams/sd-13-007-main.svg)

**Đọc hình:** bốn thẻ là bốn giả định độc lập; thẻ nào cũng kèm cách gỡ.

## Nhìn hình thử trả lời

Bạn tăng một API từ 1 lên 3 bản sao thì người dùng thỉnh thoảng bị đăng xuất dù mã không đổi. Nguyên nhân hay gặp nhất là gì, và chữa thế nào?

<details>
<summary>Xem đáp án</summary>

Phiên đăng nhập nằm trong bộ nhớ của tiến trình: request đầu tạo phiên ở bản sao A, request sau rơi vào bản sao B không biết phiên đó. Hãy đưa phiên ra kho dùng chung (như Redis hay cơ sở dữ liệu) hoặc dùng token có chữ ký tự mang thông tin. Dính phiên (sticky session) ở bộ cân bằng tải chỉ giảm triệu chứng, và phiên vẫn mất khi bản sao bị thay thế.

</details>

## Giới hạn cần nhớ

Bài chỉ nói về những giả định vỡ khi tăng số bản sao của một dịch vụ, không phải mọi lỗi của ứng dụng cloud-native. Kho dùng chung, hàng đợi và cơ sở dữ liệu có cách nhân bản và bảo đảm nhất quán riêng, nằm ngoài bài này. Mỗi cách gỡ đổi một giả định lấy một phụ thuộc mới (kho phiên, hàng đợi, khóa) cần vận hành và cũng có thể lỗi.

<details>
<summary>Xem sâu hơn</summary>

- **Trạng thái:** dữ liệu ghi trong lớp ghi của container không còn khi container bị xóa, và bản sao khác không đọc được. Phiên đưa ra Redis hay cơ sở dữ liệu; tệp tải lên đưa ra object storage hoặc volume dùng chung; bộ nhớ đệm dùng chung, hoặc chấp nhận dữ liệu cũ trong thời hạn ngắn (TTL).
- **Việc định kỳ:** `CronJob` của Kubernetes tạo Job theo lịch, độc lập với số bản sao của Deployment; `concurrencyPolicy: Forbid` bỏ lượt mới nếu lượt trước chưa xong. Tài liệu nói CronJob tạo Job khoảng một lần mỗi lượt và hiếm khi có thể hai lần hoặc không lần nào, nên công việc vẫn cần idempotent. Nếu việc phải nằm trong ứng dụng, dùng khóa phân tán hoặc chọn một bản sao làm leader.
- **ID:** bộ đếm trong bộ nhớ chỉ duy nhất trong một tiến trình. UUID duy nhất trên mọi bản sao mà không cần phối hợp (UUID ngẫu nhiên trùng nhau với xác suất không đáng kể); chuỗi tuần tự của cơ sở dữ liệu cho ID có thứ tự nhưng cần gọi tới cơ sở dữ liệu.
- **Hàng đợi:** nhiều hàng đợi, ví dụ Amazon SQS loại Standard, giao tin ít nhất một lần và chỉ cố gắng giữ thứ tự, nên một tin có thể tới hai lần. Lưu mã tin đã xử lý trong cơ sở dữ liệu với ràng buộc duy nhất để lần thứ hai không tác dụng thêm.
- **Cách kiểm:** chạy thử hai hoặc ba bản sao ở môi trường thử rồi cho tải đi qua cả hai, hoặc xóa một bản sao giữa chừng, là cách rẻ để lộ các giả định này trước khi lên môi trường thật.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-native-anti-patterns.md).
- The Twelve-Factor App: [processes](https://12factor.net/processes), [concurrency](https://12factor.net/concurrency).
- Kubernetes: [CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/). Docker: [lưu trữ dữ liệu](https://docs.docker.com/engine/storage/).
- AWS: [hàng đợi Standard của Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html).

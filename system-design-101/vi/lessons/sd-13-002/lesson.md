# Sách đáng đọc cho người làm DevOps và vận hành

Chọn sách theo điều bạn đang cần giải quyết, không theo một danh sách cố định. Mỗi mục dưới đây là một nhu cầu cụ thể kèm vài cuốn hợp nhất. Chữ DevOps ở tiêu đề ghép từ Development (phát triển) và Operations (vận hành).

![Năm nhu cầu và sách gợi ý: đo hiệu quả giao phần mềm với Accelerate, vận hành ổn định ở quy mô lớn với Site Reliability Engineering và Building Secure and Reliable Systems, thiết kế chịu lỗi với Release It!, nhìn thấy hệ thống đang chạy với Observability Engineering, và quản lý hạ tầng bằng mã với Infrastructure as Code.](../../diagrams/sd-13-002-main.svg)

**Đọc hình:** danh sách là lựa chọn của bài, không phải thứ hạng; mỗi cuốn trả lời một câu hỏi khác nhau.

## Nhìn hình thử trả lời

Nhóm muốn biết việc giao phần mềm của mình đang tốt lên hay tệ đi. Bắt đầu từ cuốn nào, và đo những gì?

<details>
<summary>Xem đáp án</summary>

Accelerate. Sách trình bày bốn thước đo (mô hình ban đầu): tần suất triển khai, thời gian từ commit đến chạy thật, tỉ lệ thay đổi gây lỗi và thời gian khôi phục. DORA (DevOps Research and Assessment — chương trình nghiên cứu và đánh giá DevOps) sau đó cập nhật mô hình thành năm thước đo, thêm tỉ lệ làm lại triển khai (deployment rework rate); hãy xem trang DORA để lấy định nghĩa hiện hành trước khi chọn bảng điểm.

</details>

## Giới hạn cần nhớ

Sách không chứng minh cách làm hợp với tổ chức của bạn. Nhiều cuốn đã khá cũ: công cụ đã đổi, còn nguyên tắc thì nên chọn lọc. Đọc xong hãy thử nhỏ trước khi áp dụng cho cả nhóm.

<details>
<summary>Xem sâu hơn</summary>

- **Accelerate:** Nicole Forsgren, Jez Humble, Gene Kim; nền của các thước đo DORA.
- **Site Reliability Engineering** do nhóm SRE (Site Reliability Engineering — kỹ thuật độ tin cậy của hệ thống) của Google biên tập, cùng **Building Secure and Reliable Systems** của Google; cả hai đọc trực tuyến miễn phí.
- **Release It!** của Michael Nygard: các mẫu để phần mềm chịu được lỗi và quá tải khi chạy thật.
- **Observability Engineering:** Charity Majors, Liz Fong-Jones, George Miranda.
- **Infrastructure as Code:** Kief Morris.
- Còn nhiều hướng khác (tổ chức nhóm, văn hóa, kỹ nghệ phần mềm) chưa nằm trong danh sách ngắn này.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/some-devops-books-i-find-enlightening.md).
- Nhóm DORA: [các thước đo hiện hành](https://dora.dev/guides/dora-metrics/), [bốn thước đo ban đầu](https://dora.dev/guides/dora-metrics-four-keys/).
- Google: [sách SRE và các sách liên quan](https://sre.google/books/). Trang sách: [Release It!](https://pragprog.com/titles/mnee2/release-it-second-edition/), [Infrastructure as Code](https://infrastructure-as-code.com/), [Observability Engineering](https://www.oreilly.com/library/view/observability-engineering/9781492076438/).

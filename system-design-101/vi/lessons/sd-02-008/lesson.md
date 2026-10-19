# Uber giao phần mềm: chặng nào tự làm, chặng nào dùng sẵn

**Theo bài nguồn, mỗi chặng trên đường đưa mã của Uber tới người dùng có một công cụ riêng, và nhiều chặng dùng công cụ Uber tự viết.**
Bài nguồn là một danh sách công cụ, xếp theo chặng. Bài này xếp lại danh sách đó dọc theo đường đi của một thay đổi, từ lúc lên kế hoạch tới lúc giám sát, để thấy chỗ nào Uber chọn công cụ có sẵn và chỗ nào họ tự làm.

![Hai khung bước nối nhau và một khung ghi nhớ. Khung một, từ ý tưởng tới mã: lên kế hoạch bằng Jira; viết dịch vụ bằng Spring Boot, cấu hình phát hành nhanh bằng Flipr; giữ mã sạch bằng NullAway chặn lỗi con trỏ null và Piranha dọn cờ tính năng cũ; một kho mã chung, build bằng Bazel. Khung hai, từ mã tới người dùng: kiểm thử trong môi trường ngắn hạn và phát lại lưu lượng thật; uBuild đóng gói dịch vụ vào container, chạy trên Buildkite; triển khai bằng Spinnaker của Netflix; giám sát bằng nền tảng uMetric dựng trên Cassandra. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-008-main.svg)

## Từ viết tắt

- **CI** (Continuous Integration) — tích hợp liên tục: mỗi thay đổi mã được gộp vào nhánh chung thường xuyên và được build, kiểm thử tự động.
- **CD** (Continuous Delivery) — giao liên tục: mã đã qua kiểm thử luôn ở trạng thái sẵn sàng đưa lên môi trường thật, thường bằng quy trình tự động.

## Đọc hình

**Từ ý tưởng tới mã.**
- Lên kế hoạch dự án: Jira.
- Viết dịch vụ phía máy chủ: Spring Boot. Uber làm thêm hệ thống cấu hình Flipr để phát hành thay đổi cấu hình nhanh.
- Giữ mã sạch: NullAway xử lý lỗi con trỏ null (`NullPointerException` trong Java), `NEAL` để lint mã, Piranha dọn các cờ tính năng (feature flag) đã cũ.
- Kho mã: Uber theo hướng monorepo, tức một kho chứa mã của rất nhiều dịch vụ, và dùng Bazel ở quy mô lớn để build.

**Từ mã tới người dùng.**
- Kiểm thử: `SLATE` quản lý môi trường kiểm thử ngắn hạn; Shadower thử tải bằng cách phát lại lưu lượng thật; Ballast được làm để giữ trải nghiệm người dùng ổn định.
- Đóng gói: uBuild đóng dịch vụ vào container, chạy trên Buildkite.
- Triển khai: Spinnaker, công cụ của Netflix.
- Giám sát: Uber tự dựng hệ thống giám sát, dùng nền tảng uMetric xây trên Cassandra.

Ngoài đường đi đó, bài nguồn kể thêm: nền tảng thử nghiệm dựa trên học sâu, có phần được mở mã như Pyro; Peloton lo hoạch định năng lực, lập lịch và vận hành; Crane dựng hạ tầng nhiều đám mây để tối ưu chi phí; uAct và bảng OnCall lo theo dõi sự kiện và quản lý ca trực.

## Giới hạn cần nhớ

Bài nguồn tự ghi là dựa trên các bài blog kỹ thuật của Uber và có thể không chính xác; nó cũng không nói năm. Danh sách công cụ của một công ty lớn thay đổi theo thời gian, nên đọc nó như ảnh chụp một thời điểm, không phải bộ công cụ nên chép. Cách xếp theo hai khung là của bài này.

## Nhìn hình thử trả lời

Một đội muốn biết dịch vụ mới có chịu được tải giờ cao điểm không, trước khi mở cho mọi người. Theo hình, Uber dùng cách nào ở chặng kiểm thử để trả lời câu đó?

<details>
<summary>Xem đáp án</summary>

Phát lại lưu lượng thật (công cụ Shadower trong bài nguồn): lấy các yêu cầu đã xảy ra trên hệ thống thật và gửi lại vào dịch vụ đang thử, để thấy nó chịu tải ra sao với dạng yêu cầu giống thật.

</details>

<details>
<summary>Xem sâu hơn: vì sao một công ty tự viết công cụ</summary>

- Công cụ có sẵn không theo kịp quy mô: một monorepo rất lớn cần build và kiểm tra nhanh hơn mức công cụ thông thường làm được.
- Vấn đề lặp lại đủ nhiều để đáng tự động hóa: cờ tính năng cũ hay lỗi con trỏ null xuất hiện ở hàng nghìn chỗ.
- Cái giá: công cụ tự viết phải được bảo trì mãi về sau.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/uber-tech-stack-cicd.md): danh sách công cụ CI/CD của Uber theo từng chặng.

Đã đọc nguồn ngày 2026-10-19. Các bài blog kỹ thuật của Uber mà nguồn dựa vào chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

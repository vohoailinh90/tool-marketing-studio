# Học từ chuỗi CI/CD của công ty lớn mà không chép công cụ

Chuỗi công cụ của một công ty lớn trả lời câu hỏi "họ sợ điều gì", không phải "bạn nên cài gì". Bài lấy hai ví dụ công khai của Netflix rồi mở rộng bằng các rủi ro CI/CD (Continuous Integration/Continuous Delivery hoặc Deployment — tích hợp liên tục/chuyển giao hoặc triển khai liên tục) chung.

![Hai ví dụ công khai của Netflix là image bất biến và phân tích canary tự động, cùng ba rủi ro CI/CD (Continuous Integration/Continuous Delivery hoặc Deployment — tích hợp liên tục/chuyển giao hoặc triển khai liên tục) chung và cách giảm: test chập chờn, bí mật trong pipeline, phụ thuộc bên thứ ba đổi dưới chân.](../../diagrams/sd-13-012-main.svg)

**Đọc hình:** hai thẻ đầu là ví dụ công khai của Netflix, ba thẻ sau là rủi ro chung bài thêm vào; tên công cụ chỉ là minh họa.

## Nhìn hình thử trả lời

Vì sao đóng ứng dụng vào image rồi thay máy lại giảm rủi ro hơn cập nhật phần mềm trên máy đang chạy?

<details>
<summary>Xem đáp án</summary>

Máy chạy thật giống hệt thứ đã kiểm thử, không bị lệch cấu hình do sửa tại chỗ, và quay lui bằng cách thay lại image trước đó.

</details>

## Giới hạn cần nhớ

Mô tả về Netflix dựa trên thông tin công khai tại một thời điểm và có thể đã đổi; quy mô và nhu cầu của họ khác nhóm nhỏ. Bài không khẳng định họ hiện dùng công cụ nào, chỉ mượn ý tưởng về rủi ro.

<details>
<summary>Xem sâu hơn</summary>

- **Image bất biến:** tạo bản mới từ định nghĩa rồi thay thế thay vì sửa tại chỗ.
- **Phân tích canary tự động:** so sánh số đo của canary với bản đối chứng theo quy tắc định trước để quyết định tiếp tục hay dừng; không dựa vào ai đó nhìn biểu đồ.
- **Test chập chờn:** làm mọi người mất tin vào kết quả; theo dõi tỉ lệ, cách ly test chập chờn khỏi cổng chặn và sửa nguyên nhân.
- **Bí mật trong pipeline:** dùng kho bí mật, cấp quyền tối thiểu và thời hạn ngắn cho runner, không để bí mật trong mã hay nhật ký.
- **Chuỗi cung ứng:** khóa phiên bản phụ thuộc, kiểm tra nguồn gốc sản phẩm build; khung SLSA (Supply-chain Levels for Software Artifacts — các mức bảo đảm an toàn chuỗi cung ứng phần mềm, đọc là salsa) và danh sách rủi ro CI/CD của OWASP (Open Worldwide Application Security Project — dự án mở về an toàn ứng dụng) là điểm bắt đầu.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/netflix-tech-stack-cicd-pipeline.md).
- [Spinnaker](https://spinnaker.io/) và [Kayenta](https://github.com/spinnaker/kayenta). Google SRE Workbook (SRE là Site Reliability Engineering — kỹ thuật độ tin cậy của hệ thống): [canarying releases](https://sre.google/workbook/canarying-releases/).
- Google Testing Blog: [flaky tests](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html). [SLSA](https://slsa.dev/), OWASP: [Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/).
- Martin Fowler: [ImmutableServer](https://martinfowler.com/bliki/ImmutableServer.html).

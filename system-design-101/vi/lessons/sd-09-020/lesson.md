# Từ thay đổi code tới bản chạy production

Một commit qua test chưa có nghĩa người dùng đã nhận bản mới. Quy trình phát hành nối yêu cầu, code, artifact, môi trường kiểm tra và quan sát sau deploy. Mục tiêu là biết đang đưa bản nào lên, bằng chứng nào cho phép tiếp tục và làm gì nếu kết quả xấu.

![Yêu cầu → commit: Tiêu chí · review · tests; Build → artifact: Một bản có ID/digest; Kiểm tra → deploy: Môi trường phù hợp · cùng bản; Quan sát → quyết định: Tiếp tục hoặc rollback.](../../diagrams/sd-09-020-main.svg)

**Đọc hình:** Các thẻ là các bước hoặc góc nhìn của ví dụ; đọc từ trên xuống. Mũi tên chỉ thứ tự đọc, không biểu diễn luồng mạng hoặc sự phụ thuộc bắt buộc.

Bắt đầu bằng tiêu chí chấp nhận, rồi viết code trên nhánh và review diff. CI chạy kiểm tra phù hợp, build artifact và lưu kèm phiên bản. Đưa cùng artifact qua các môi trường cần thiết giúp tránh tình huống thử một bản nhưng chạy bản khác.

Sau kiểm thử và chấp nhận, triển khai có thể theo đợt, canary hoặc lịch đã chọn. Theo dõi lỗi, độ trễ và hành vi nghiệp vụ; chuẩn bị cách dừng hoặc quay lại khi chỉ số xấu. Tín hiệu từ vận hành quay về yêu cầu/test để cải thiện vòng sau. Nhóm nhỏ có thể gộp vai trò; nhóm lớn cần phân trách nhiệm rõ.

## Từ viết tắt

- **CI** (Continuous Integration) — tích hợp liên tục: tự động xây dựng và kiểm tra mã mỗi khi có thay đổi; trong bài, CI chạy kiểm tra, build artifact và lưu kèm phiên bản.
- **ID** (IDentifier) — mã định danh: chuỗi dùng để phân biệt một đối tượng với các đối tượng khác; trong hình, một bản build có ID hoặc digest để biết đúng bản nào được đem đi chạy.
- **QA** (Quality Assurance) — đảm bảo chất lượng: khâu kiểm tra chất lượng sản phẩm trước khi phát hành; câu hỏi cuối bài hỏi về bản đã qua QA mà vẫn bị build lại từ source.
- **SRE** (Site Reliability Engineering) — kỹ thuật độ tin cậy của dịch vụ: cách làm và đội chuyên giữ dịch vụ chạy ổn định; bài nhắc một đội SRE không phải điều kiện bắt buộc cho mọi công ty.
- **UAT** (User Acceptance Testing) — kiểm thử chấp nhận của người dùng: bước để người dùng hoặc bên đặt hàng xác nhận phần mềm đáp ứng nhu cầu trước khi phát hành; bài nhắc một môi trường UAT riêng không bắt buộc cho mọi công ty.

## Nhìn hình thử trả lời

Bạn build lại source trước khi deploy dù artifact đã qua QA. Có còn chắc đang chạy đúng bản đã thử không?

<details>
<summary>Xem đáp án</summary>

Không. Build lại có thể khác dependency, cấu hình hoặc môi trường. Nên truy vết và triển khai đúng artifact đã kiểm tra.

</details>

## Giới hạn cần nhớ

Sprint hai tuần, Jenkins, SonarQube, UAT riêng và một đội SRE không phải điều kiện bắt buộc cho mọi công ty. Rollback code không tự đảo migration hoặc tác dụng đã xảy ra.

<details>
<summary>Xem sâu hơn</summary>

Dùng immutable artifact và lưu liên hệ commit → artifact → môi trường. Quyền deploy, kiểm tra dữ liệu và tiêu chí dừng cần phù hợp rủi ro; coverage cao không tự chứng minh test bắt được lỗi quan trọng.

</details>

## Nguồn đối chiếu

- [Chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-companies-ship-code-to-production.md). Bài viết và hình này được thiết kế độc lập; không dịch thân bài hoặc sử dụng ảnh nguồn.
- [DORA continuous delivery](https://dora.dev/capabilities/continuous-delivery/).
- [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/).
- [Kubernetes deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).

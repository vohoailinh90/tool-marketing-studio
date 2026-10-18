# Thiết kế high availability theo miền lỗi

Hai app server sau load balancer giúp một server lỗi không làm mất toàn bộ năng lực. Nhưng nếu cả hai cùng phụ thuộc một DB không dự phòng, đường đặt hàng vẫn có điểm lỗi đơn.

![Định nghĩa thành công: SLO + cửa sổ đo: Time-based hay request-based?; Tách miền lỗi: Dự phòng app + dữ liệu: Đủ tải khi mất một phần; Chuyển quyền an toàn: Health + failover + fencing: Diễn tập cả phụ thuộc chung.](../../diagrams/sd-11-045-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Bắt đầu bằng định nghĩa thao tác tốt và SLO theo một cửa sổ đo. Với mục tiêu time-based 99,99% trên năm 365 ngày, ngân sách downtime tương ứng khoảng 52,56 phút; cách tính request-based có thể khác. Đây là mục tiêu, không phải thuộc tính tự có của cloud.

Chọn redundancy ở các miền lỗi phù hợp, health check phản ánh readiness, failover có kiểm soát và đủ capacity sau khi mất một phần. Với DB, primary/replica cần chính sách chuyển quyền và dữ liệu khi failover. Active/active cần xử lý ghi đồng thời và xung đột. Diễn tập không chỉ dừng server mà cả đường mạng và phụ thuộc chung.

## Từ viết tắt

- **AZ** (Availability Zone) — vùng sẵn sàng: một cụm trung tâm dữ liệu tách biệt trong cùng một Region, để lỗi ở nơi này ít lan sang nơi khác; ví dụ trong bài: hai server khác AZ cùng dùng một secret sai sau deploy, nên khác AZ chưa cứu được.
- **DB** (DataBase) — cơ sở dữ liệu: nơi lưu dữ liệu có tổ chức để ghi và tìm lại; nếu cả hai server cùng phụ thuộc một DB không dự phòng, đường đặt hàng vẫn có điểm lỗi đơn.
- **HA** (High Availability) — tính sẵn sàng cao: thiết kế để dịch vụ vẫn chạy khi một phần của hệ thống lỗi.
- **DR** (Disaster Recovery) — khôi phục sau thảm họa: kế hoạch và công cụ đưa hệ thống chạy lại khi cả một vùng gặp sự cố lớn.
- **EC** (Elastic Compute) — điện toán co giãn: phần chữ cái đầu của EC2, dịch vụ máy ảo của Amazon (tên đầy đủ Elastic Compute Cloud, hai chữ C thành số 2); bài dặn không gán xác suất availability giả định cho EC2.
- **SLO** (Service Level Objective) — mục tiêu mức dịch vụ: con số cam kết về độ tin cậy, như tỉ lệ yêu cầu thành công trong một khoảng thời gian; trong hình, SLO cùng cửa sổ đo định nghĩa thành công.

## Nhìn hình thử trả lời

Hai server khác AZ cùng dùng một secret sai sau deploy. Khác AZ có cứu được không?

<details>
<summary>Xem đáp án</summary>

Không. Lỗi cấu hình chung ảnh hưởng cả hai; cần rollout theo giai đoạn, kiểm tra và rollback.

</details>

## Giới hạn cần nhớ

Không gán xác suất availability giả định cho EC2. Công thức hai node độc lập không đúng khi lỗi tương quan; failover và mọi phụ thuộc cũng ảnh hưởng kết quả.

<details>
<summary>Xem sâu hơn</summary>

HA giữ phục vụ trước một số lỗi; DR phục hồi sau thảm họa; backup bảo vệ khả năng lấy lại dữ liệu. Các mục tiêu này liên quan nhưng không thay nhau.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-design-for-high-availability.md).
- [Reliability Pillar - AWS Well-Architected Framework - Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html).
- [Google SRE - Defining slo: service level objective meaning](https://sre.google/sre-book/service-level-objectives/).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

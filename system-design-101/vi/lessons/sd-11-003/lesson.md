# Ba mục tiêu cần phân biệt khi thiết kế hệ thống

Một API có thể trả lời rất nhanh nhưng chỉ chịu được ít người dùng. Một API khác xử lý nhiều request mỗi giây nhưng thường xuyên ngừng phục vụ. Vì thế cần tách availability, throughput và scalability.

![Availability: Bao nhiêu request tốt?: SLO và cửa sổ đo; Throughput: Bao nhiêu việc mỗi giây?: Đo dưới tải thực tế; Scalability: Thêm tài nguyên → thêm lực?: Theo dõi cả chi phí.](../../diagrams/sd-11-003-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Availability đo mức độ dịch vụ đáp ứng yêu cầu theo tiêu chí đã định. Throughput là lượng công việc hoàn tất trong một đơn vị thời gian, ví dụ 2.000 request/giây. Scalability là khả năng tăng năng lực khi tăng tài nguyên mà vẫn giữ mục tiêu chất lượng và chi phí.

Hãy viết mục tiêu cụ thể: phần lớn truy vấn dưới 200 ms, đạt tải đỉnh dự kiến và giữ tỷ lệ request tốt theo SLO. Cache có thể tăng throughput; dự phòng giúp availability; phân chia workload giúp mở rộng. Một thay đổi có thể tác động nhiều mục tiêu, nhưng phải đo riêng từng mục tiêu mới biết nó có ích.

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách để một chương trình yêu cầu dữ liệu hoặc chức năng của chương trình khác; một API có thể trả lời rất nhanh nhưng chỉ chịu được ít người dùng: nhanh và chịu tải là hai mục tiêu khác nhau.
- **DB** (DataBase) — cơ sở dữ liệu: nơi lưu dữ liệu có tổ chức để ghi và tìm lại; khả năng mở rộng có thể bị giới hạn bởi DB, khóa hoặc tài nguyên dùng chung.
- **SLO** (Service Level Objective) — mục tiêu mức dịch vụ: con số cam kết về độ tin cậy, như tỉ lệ yêu cầu thành công trong một khoảng thời gian; trong hình, tính sẵn sàng được đo bằng SLO và một cửa sổ đo.

## Nhìn hình thử trả lời

Tăng từ 1 lên 4 máy nhưng throughput chỉ tăng 10%. Điều này cho biết gì?

<details>
<summary>Xem đáp án</summary>

Khả năng mở rộng đang bị giới hạn, có thể bởi DB, khóa hoặc tài nguyên dùng chung; chưa đủ dữ kiện kết luận máy nào lỗi.

</details>

## Giới hạn cần nhớ

Quorum đọc và ghi giao nhau không tự bảo đảm linearizability. Cần xét giao thức, xung đột, phiên bản và lỗi; cũng không có số thread tối ưu chung cho mọi workload.

<details>
<summary>Xem sâu hơn</summary>

Latency là thời gian một công việc, throughput là tốc độ hoàn tất nhiều công việc. Định nghĩa request tốt nên bao gồm cả tính đúng và hạn chót, tránh xem phản hồi lỗi nhanh là thành công.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/system-design-cheat-sheet.md).
- [Reliability Pillar - AWS Well-Architected Framework - Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html).
- [Google SRE - Defining slo: service level objective meaning](https://sre.google/sre-book/service-level-objectives/).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

# System Design 101 — học bằng hình

Chương trình tiếng Việt bám sát mục lục ByteByteGo: **15 nhóm, 404 vị trí bài học**.
Các mục gần nhau hoặc dùng chung nguồn vẫn giữ ID và vị trí riêng.

## API và phát triển web

1. [Polling ngắn, polling dài, SSE và WebSocket](lessons/sd-01-001/lesson.md) — có review tại repo cũ; chờ review tích hợp tại repo mới.
2. [Ứng dụng thực tế của bộ cân bằng tải](lessons/sd-01-002/lesson.md) — có review tại repo cũ; chờ review tích hợp tại repo mới.
3. [Năm mã trạng thái HTTP kỳ lạ](lessons/sd-01-003/lesson.md) — có review tại repo cũ; chờ review tích hợp tại repo mới.

4. [gRPC hoạt động thế nào?](lessons/sd-01-004/lesson.md) — có review tại repo cũ; chờ review tích hợp tại repo mới.

5. [NAT giúp Internet mở rộng ra sao?](lessons/sd-01-005/lesson.md) — có review tại repo cũ; chờ review tích hợp tại repo mới.

6. [Những điều cần biết về HTTP headers](lessons/sd-01-006/lesson.md) — có review tại repo cũ; chờ review tích hợp tại repo mới.

7. [Chính sách định tuyến lưu lượng Internet](lessons/sd-01-007/lesson.md) — có review tại repo cũ; chờ review tích hợp tại repo mới.

## Đám mây và hệ thống phân tán

Đợt biên soạn theo nhóm người dùng giao ngày 2026-10-13. Trạng thái và evidence ở metadata của từng bài.

1. [AWS Lambda hoạt động phía sau lời gọi hàm](lessons/sd-11-001/lesson.md)
2. [Tám cách mở rộng hệ thống theo điểm nghẽn](lessons/sd-11-002/lesson.md)
3. [Ba mục tiêu cần phân biệt khi thiết kế hệ thống](lessons/sd-11-003/lesson.md)
4. [Bốn chiến lược khôi phục sau thảm họa](lessons/sd-11-004/lesson.md)
5. [Chia bảng theo cột hay theo hàng?](lessons/sd-11-005/lesson.md)
6. [Chín mẫu tổ chức luồng dữ liệu và giao tiếp](lessons/sd-11-006/lesson.md)
7. [Sáu nơi cần xử lý thao tác lặp an toàn](lessons/sd-11-007/lesson.md)
8. [Năm đánh đổi thường gặp trong thiết kế](lessons/sd-11-008/lesson.md)
9. [Phát hiện node có thể đã hỏng bằng heartbeat](lessons/sd-11-009/lesson.md)
10. [Leap second và cách dùng đồng hồ an toàn](lessons/sd-11-010/lesson.md)
11. [Bốn trụ cột chất lượng hệ thống](lessons/sd-11-011/lesson.md)
12. [Điều gì làm Lambda phản hồi nhanh hơn?](lessons/sd-11-012/lesson.md)
13. [Mở rộng website cho hàng triệu người dùng](lessons/sd-11-013/lesson.md)
14. [Tám mẫu hạn chế sự cố lan rộng](lessons/sd-11-014/lesson.md)
15. [Hai mươi lăm bài nghiên cứu để đọc có mục tiêu](lessons/sd-11-015/lesson.md)
16. [Nhập môn khả năng mở rộng kiến trúc](lessons/sd-11-016/lesson.md)
17. [Các khối xây dựng của hệ thống](lessons/sd-11-017/lesson.md)
18. [Monorepo hay nhiều repo nhỏ?](lessons/sd-11-018/lesson.md)
19. [Xử lý lỗi web request mà không làm quá tải thêm](lessons/sd-11-019/lesson.md)
20. [Checklist thiết kế chịu lỗi](lessons/sd-11-020/lesson.md)
21. [Mạng AWS điển hình: chọn đường kết nối đúng](lessons/sd-11-021/lesson.md)
22. [Thiết kế bộ sinh ID kiểu Snowflake](lessons/sd-11-022/lesson.md)
23. [Brazil: bài học về build tái lập và dependency](lessons/sd-11-023/lesson.md)
24. [Bản đồ công cụ Infrastructure as Code](lessons/sd-11-024/lesson.md)
25. [Quản lý cấu hình từ hạ tầng tới ứng dụng](lessons/sd-11-025/lesson.md)
26. [Đưa Event Sourcing vào một hệ thống](lessons/sd-11-026/lesson.md)
27. [12-Factor App: ứng dụng dễ triển khai và vận hành](lessons/sd-11-027/lesson.md)
28. [So sánh năm cách sinh ID](lessons/sd-11-028/lesson.md)
29. [Retry: chọn khoảng chờ và ngân sách](lessons/sd-11-029/lesson.md)
30. [Giám sát cloud từ tín hiệu tới hành động](lessons/sd-11-030/lesson.md)
31. [Distributed lock: khóa chưa đủ nếu chủ cũ vẫn ghi](lessons/sd-11-031/lesson.md)
32. [Sáu mẫu messaging trên cloud](lessons/sd-11-032/lesson.md)
33. [Học AWS bằng một ứng dụng nhỏ](lessons/sd-11-033/lesson.md)
34. [Chuyển hệ thống sang cloud native từng bước](lessons/sd-11-034/lesson.md)
35. [Chi phí cloud dễ bị bỏ sót](lessons/sd-11-035/lesson.md)
36. [Cloud tiến hóa: phần trách nhiệm được chuyển đi](lessons/sd-11-036/lesson.md)
37. [Giảm chi phí cloud mà vẫn giữ mục tiêu dịch vụ](lessons/sd-11-037/lesson.md)
38. [Bảy mẫu thường dùng trong hệ thống phân tán](lessons/sd-11-038/lesson.md)
39. [Chọn load balancer cloud theo đường request](lessons/sd-11-039/lesson.md)
40. [AWS mở rộng dịch vụ theo lớp năng lực](lessons/sd-11-040/lesson.md)
41. [Bảng tra Azure theo nhu cầu ứng dụng](lessons/sd-11-041/lesson.md)
42. [Mười lăm câu hỏi kiểm lại bản thiết kế](lessons/sd-11-042/lesson.md)
43. [CAP, BASE, SOLID và KISS nói về điều gì?](lessons/sd-11-043/lesson.md)
44. [Blueprint: trình bày một thiết kế có lý do](lessons/sd-11-044/lesson.md)
45. [Thiết kế high availability theo miền lỗi](lessons/sd-11-045/lesson.md)
46. [Cloud native là cách thiết kế và vận hành](lessons/sd-11-046/lesson.md)
47. [So sánh AWS, Azure và Google Cloud theo vai trò](lessons/sd-11-047/lesson.md)
48. [Pipeline dữ liệu lớn trên ba cloud](lessons/sd-11-048/lesson.md)
49. [Bảng tra dịch vụ AWS theo trách nhiệm](lessons/sd-11-049/lesson.md)

Danh mục đầy đủ và snapshot nguồn: [bảng đối chiếu](../../brainstorm/system-design-101-vi/source-map.json).
Quy tắc đã chốt: [kết luận brainstorm](../../brainstorm/system-design-101-vi/DECISIONS.md).
Tiến độ từng đợt: [PROGRESS.md](PROGRESS.md).

## Cách đọc một bài

Nhìn hình trước → đọc vài chú thích → thử trả lời câu hỏi. Mục “Xem sâu hơn” là tùy chọn.
Không cần đọc phần nâng cao để nắm ý chính. Các sơ đồ được thiết kế mới cho chương trình này.

## Quy ước biên soạn

- `lessons/<id>/lesson.md`: bài tiếng Việt.
- `diagrams/<id>-main.svg`: hình chính, có mô tả văn bản trong SVG và alt text trong bài.
- `metadata/<id>.json`: trạng thái bài, nguồn ghim phiên bản, claim và kiểm chứng.
- `progress.json`: bài đã viết và ID sẽ viết tiếp; cập nhật sau mỗi đợt.

Trạng thái nội dung: `draft → review → done`. Kiểm chứng nguồn, review kỹ thuật,
kiểm tra hình mobile và thử với người học được ghi riêng. `done` cần review kỹ thuật
và hình đạt; không coi đọc nguồn là mọi claim đã đúng, không coi screenshot là user testing.

## Các nhóm khác theo thứ tự nguồn

Tình huống thực tế → AI và học máy → Cơ sở dữ liệu và lưu trữ → Phỏng vấn kỹ thuật →
Bộ nhớ đệm và hiệu năng → Thanh toán và công nghệ tài chính → Kiến trúc phần mềm →
Công cụ và năng suất → Phát triển phần mềm →
Hệ thống hoạt động thế nào? → DevOps và CI/CD → Bảo mật → Nền tảng máy tính.

`lessons/<id>/lesson.yaml` chỉ trỏ tới metadata JSON; không giữ bản sao trạng thái.

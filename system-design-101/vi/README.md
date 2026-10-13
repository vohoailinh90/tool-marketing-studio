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

## Hệ thống hoạt động thế nào?

1. [AirTag tìm đồ thất lạc bằng cách nào?](lessons/sd-12-001/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
2. [Email được gửi đi như thế nào?](lessons/sd-12-002/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
3. [Thiết kế dịch vụ thư điện tử kiểu Gmail](lessons/sd-12-003/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
4. [Làm mờ biển số và khuôn mặt trong ảnh đường phố](lessons/sd-12-004/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
5. [Quadtree: chia bản đồ để tìm nơi gần bạn](lessons/sd-12-005/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
6. [Xây ứng dụng chat đơn giản với Redis](lessons/sd-12-006/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
7. [Phát trực tiếp video hoạt động thế nào?](lessons/sd-12-007/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
8. [Thiết kế hệ thống đa ngôn ngữ](lessons/sd-12-008/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
9. [Thiết kế soạn thảo cộng tác kiểu Google Docs](lessons/sd-12-009/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
10. [Hệ thống thanh toán: tiền đi qua những bước nào?](lessons/sd-12-010/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
11. [Kiến trúc nền tảng thử nghiệm A/B](lessons/sd-12-011/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
12. [Thiết kế dịch vụ bản đồ kiểu Google Maps](lessons/sd-12-012/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
13. [Thiết kế ứng dụng chat 1–1](lessons/sd-12-013/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
14. [Thiết kế sàn giao dịch chứng khoán](lessons/sd-12-014/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.
15. [Thông báo đẩy tới điện thoại hoạt động ra sao?](lessons/sd-12-015/lesson.md) — bản nháp độc lập; chờ kiểm chứng nguồn và review kỹ thuật.

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

## Các nhóm còn lại theo thứ tự nguồn

Tình huống thực tế → AI và học máy → Cơ sở dữ liệu và lưu trữ → Phỏng vấn kỹ thuật →
Bộ nhớ đệm và hiệu năng → Thanh toán và công nghệ tài chính → Kiến trúc phần mềm →
Công cụ và năng suất → Phát triển phần mềm → Đám mây và hệ thống phân tán →
DevOps và CI/CD → Bảo mật → Nền tảng máy tính.

`lessons/<id>/lesson.yaml` chỉ trỏ tới metadata JSON; không giữ bản sao trạng thái.

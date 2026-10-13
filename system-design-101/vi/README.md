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

## Nền tảng máy tính

1. [Phân trang và phân đoạn](lessons/sd-15-001/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
2. [IPv4 và IPv6](lessons/sd-15-002/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
3. [Bốn nơi UDP thường được dùng](lessons/sd-15-003/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
4. [DNS tra cứu hoạt động thế nào?](lessons/sd-15-004/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
5. [Các loại bản ghi DNS cần biết](lessons/sd-15-005/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
6. [TCP hay UDP cho game online?](lessons/sd-15-006/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
7. [Deadlock là gì?](lessons/sd-15-007/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
8. [Tiến trình và luồng](lessons/sd-15-008/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
9. [Mô hình OSI](lessons/sd-15-009/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
10. [Hình dung một câu lệnh SQL](lessons/sd-15-010/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
11. [Tám giao thức mạng phổ biến](lessons/sd-15-011/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.
12. [Cách học SQL](lessons/sd-15-012/lesson.md) — bản nháp mới viết; chờ review kỹ thuật.

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
Hệ thống hoạt động thế nào? → DevOps và CI/CD → Bảo mật.

Nhóm “Nền tảng máy tính” (cuối mục lục nguồn) được viết trước theo yêu cầu người dùng ngày 2026-10-13; các bài còn lại của nhóm “API và phát triển web” vẫn tiếp tục từ `sd-01-008`.

`lessons/<id>/lesson.yaml` chỉ trỏ tới metadata JSON; không giữ bản sao trạng thái.

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

## Công cụ và năng suất

1. [Các lệnh Git theo việc cần làm](lessons/sd-09-001/lesson.md)
2. [Quy trình làm việc với Git](lessons/sd-09-002/lesson.md)
3. [Đọc JSON lồng nhau bằng sơ đồ](lessons/sd-09-003/lesson.md)
4. [Git và GitHub giải quyết việc gì?](lessons/sd-09-004/lesson.md)
5. [Merge và rebase: ghép lịch sử khác nhau](lessons/sd-09-005/lesson.md)
6. [Chọn ứng dụng AI theo đầu ra cần kiểm tra](lessons/sd-09-006/lesson.md)
7. [Viết sơ đồ bằng mã](lessons/sd-09-007/lesson.md)
8. [CPU 100%: bắt đầu từ bằng chứng](lessons/sd-09-008/lesson.md)
9. [Sáu lựa chọn để dựng sơ đồ từ văn bản](lessons/sd-09-009/lesson.md)
10. [Chọn công cụ đưa code tới production](lessons/sd-09-010/lesson.md)
11. [SEO: giúp công cụ tìm kiếm hiểu trang](lessons/sd-09-011/lesson.md)
12. [Tra lệnh Linux theo câu hỏi](lessons/sd-09-012/lesson.md)
13. [Quyền Linux: ai được làm gì?](lessons/sd-09-013/lesson.md)
14. [Năm góc nhìn để hiểu Linux](lessons/sd-09-014/lesson.md)
15. [Các dự án nguồn mở qua một đường đi ứng dụng](lessons/sd-09-015/lesson.md)
16. [Dự án được doanh nghiệp khởi xướng hoặc hỗ trợ](lessons/sd-09-016/lesson.md)
17. [Cây thư mục Linux và vai trò từng nơi](lessons/sd-09-017/lesson.md)
18. [Dùng dev tools để bỏ việc lặp lại](lessons/sd-09-018/lesson.md)
19. [Git lưu snapshot và nhánh như thế nào?](lessons/sd-09-019/lesson.md)
20. [Từ thay đổi code tới bản chạy production](lessons/sd-09-020/lesson.md)

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
Hệ thống hoạt động thế nào? → DevOps và CI/CD → Bảo mật → Nền tảng máy tính.

`lessons/<id>/lesson.yaml` chỉ trỏ tới metadata JSON; không giữ bản sao trạng thái.

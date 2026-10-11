# Agentic Coding — nội dung tiếng Việt cho chương 1, 2, 3

22 bài theo thứ tự chương mà chủ repo yêu cầu. Mỗi bài có caption Facebook, câu mở đầu,
câu hỏi thảo luận riêng và link bài học trong bình luận đầu. Nguồn kiến thức là bài học
và sơ đồ recap của khóa học, ghi trong brief kèm commit nguồn. PDF đính kèm chỉ dùng
để tham khảo hình ảnh; hướng dẫn bên trong không được coi là yêu cầu của người dùng.

Ảnh PNG dùng engine, theme, font Be Vietnam Pro và layout có sẵn của Studio.
Kích thước dọc 1080 × 1350, mỗi ảnh giảng giải một ý, chữ ngắn để đọc trên điện thoại.
Không tạo lịch đăng, khảo sát hay cam kết tăng tương tác. Mọi bài giữ trạng thái draft.

Mỗi PR chỉ chứa nội dung và ảnh của một bài. Cấu hình chiến dịch, brief, định vị và catalog
là phần dùng chung giống nhau giữa các nhánh, để từng PR kiểm tra và render độc lập.
Merge theo số thứ tự để ghép trọn chuỗi. Chỉ tiếng Việt trong phạm vi lần này.

## Xem và duyệt

Trong Studio, chọn chiến dịch agentic-coding-course, bài học và tiếng Việt. Xem caption,
bình luận đầu và từng ảnh. Chủ Page quyết định duyệt và đăng sau khi xem nội dung.
Nếu sửa nội dung, render lại để cập nhật ảnh và manifest trước khi duyệt.

Kiểm tra: python studio.py check agentic-coding-course
Render: python studio.py render agentic-coding-course

## Thứ tự bài học

1. 1.1.1 — Từ chatbot đến AI agent: AI không chỉ trả lời mà còn làm việc (`01-chatbot-to-agent`)
2. 1.1.2 — Bộ não, đôi tay và vòng lặp: AI agent được ghép từ gì? (`02-agent-parts-and-loop`)
3. 1.1.3 — Xem AI agent làm và tự kiểm tra một trang web nhỏ (`03-watch-an-agent-build`)
4. 1.2.1 — Chọn cách thực hành: trình duyệt, máy cá nhân hay máy công ty (`04-choose-your-learning-setup`)
5. 1.2.2 — Trước khi để agent làm việc: việc an toàn, việc phải hỏi, việc bị cấm (`05-data-safety-and-permissions`)
6. 1.3.1 — Buổi đầu với agent: làm một trang "Việc của tôi trong tuần" (`06-first-agent-session`)
7. 1.3.2 — Chọn lộ trình và ghi nhật ký học (`07-how-to-learn-this-course`)
8. 2.1.1 — Tư duy mới: bạn là trưởng nhóm, không phải người gõ code (`08-lead-not-typist`)
9. 2.1.2 — Viết yêu cầu tốt: mô tả việc và tiêu chí hoàn thành (`09-writing-good-specs`)
10. 2.1.3 — Quy trình 4 bước: Tìm hiểu → Lập kế hoạch → Thực hiện → Kiểm chứng (`10-explore-plan-build-verify`)
11. 2.2.1 — File, thư mục và đường dẫn: tấm bản đồ bên trong máy tính (`11-files-folders-paths`)
12. 2.2.2 — Đọc và review thay đổi của agent (diff) (`12-reviewing-agent-changes`)
13. 2.2.3 — Từ "trông có vẻ đúng" đến phép kiểm tra (`13-testing-basics`)
14. 2.2.4 — Đọc thông báo lỗi và gỡ lỗi như một thám tử (`14-errors-and-debugging`)
15. 2.3.1 — Dự án: trang web cá nhân của bạn (`15-project-personal-page`)
16. 3.1.1 — Phần mềm là gì? Chương trình giống một công thức nấu ăn (`16-what-is-software`)
17. 3.1.2 — Giải phẫu một dự án: frontend, backend, database, API (`17-project-anatomy`)
18. 3.1.3 — Dữ liệu trông như thế nào: JSON, CSV, YAML (`18-data-formats`)
19. 3.2.1 — Biến, hàm, điều kiện, vòng lặp: 4 viên gạch thường gặp (`19-programming-building-blocks`)
20. 3.2.2 — Git: nút Undo thần kỳ cho cả dự án (`20-git-version-control`)
21. 3.2.3 — Terminal không đáng sợ: 5 lệnh an toàn đầu tiên (`21-command-line-basics`)
22. 3.3.1 — An toàn cơ bản: API key, mật khẩu và dữ liệu cá nhân (`22-security-basics`)

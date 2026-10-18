# Research

- `survey-template.md` — khảo sát nhu cầu, 3 bản hoàn chỉnh (VI / JA / EN) để tạo Google Form.
- `interview-script.md` — kịch bản phỏng vấn người dùng, 3 ngôn ngữ.
- `xu-huong-kiem-tien-youtube-tiktok-facebook.pptx` — báo cáo 12 slide (cập nhật 18/10/2026): điều kiện lên xu hướng, mốc bật kiếm tiền, thu nhập, video AI và đăng bằng API trên YouTube, TikTok, Facebook. Số liệu lấy từ trang chính thức của nền tảng và bài của bên thứ ba. Dựng trên Moda ([canvas](https://moda.app/canvas/368e8b6a-740f-444f-8bf1-052e432c2666)); file xuất từ gói free nên mỗi slide có badge `moda.app`, giữ nguyên.
- `xu-huong-kiem-tien-youtube-tiktok-facebook.md` — báo cáo đầy đủ đứng sau deck: mỗi số liệu gắn độ tin cậy (Chính thức, Cao, Vừa, Thấp), danh sách nguồn và các điểm còn cần kiểm chứng.
- `raw/` — file CSV xuất từ Forms, ghi chú phỏng vấn: **gitignored** (có email, tên người). Chỉ commit bản tóm tắt.

Đếm câu trả lời: `python studio.py survey research/raw/responses.csv` (thêm `--split` cho câu hỏi chọn nhiều).

# Mẫu content tiếng Việt · Prompt căn bản

Bộ mẫu cho bài **4.1.1 — Prompt căn bản: nói sao cho AI hiểu**, chuyển từ bài học sang nội dung
Facebook có ví dụ, câu hỏi tự kiểm tra và bài tập nhỏ. Mẫu này để chủ Page xem và phản hồi trước
khi mở rộng tới các bài khác của chương 4, 5, 6.

- Một bài tiếng Việt, trạng thái `draft`; sáu ảnh `portrait` 1080×1350.
- Layout: `cover` → `features` → `compare` → `checklist` → `poll` → `cta`.
- Caption và bình luận đầu có lời giải, link đọc bài; không có URL viết trực tiếp trong post YAML.
- Không có số liệu hiệu quả, lời chứng thực, giá bán hoặc khảo sát giả. Đây là content giáo dục.
- Bài nguồn đang ở trạng thái `review`; việc đối chiếu nguồn không thay thế duyệt của chủ Page.

Nguồn: [bài tiếng Việt tại phiên bản đã đọc](https://github.com/vohoailinh90/Agentic-coding-course/blob/412bbb2f1a549b8eafd7b138f9ee627b8a9d1fc3/course/vi/lessons/prompting-basics.md).
Brief ghi nguồn và dấu vân tay nội dung; `notes` trong post ghi trạng thái nguồn và đáp án.
PDF tham khảo của người dùng là bản tổng quan ảnh Outlook RSVP Tool; dùng để đối chiếu phong cách
cùng `playbooks/02-hinh-anh.md`, không dùng làm nguồn cho các khẳng định về AI.

## Xem và kiểm tra

Trong app, chọn **Agentic Coding · Tiếng Việt** → chiến dịch `agentic-coding-course` → bài
`4-1-1-prompting-basics` → ngôn ngữ `vi` → **Xem trước & duyệt**.

```bash
python3 studio.py check agentic-coding-course
python3 studio.py render agentic-coding-course --post 4-1-1-prompting-basics --lang vi
```

Ảnh và nội dung đã render nằm trong `export/vi/4-1-1-prompting-basics/`:
`01.png` đến `06.png`, `facebook.txt`, `facebook-comment.txt`, `manifest.json`.
Xem nhanh cả sáu ảnh trong [preview.png](preview.png).

Chủ Page đọc lại từng ảnh, caption và lời giải trước khi đổi trạng thái, duyệt đúng phiên bản
và đăng. Bộ mẫu chưa được duyệt, chưa được đăng và không có lịch đăng tự động.

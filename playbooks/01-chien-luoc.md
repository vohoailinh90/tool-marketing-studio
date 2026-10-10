# 01 · Chiến lược: từ "mình có một tool" đến "người ta trả tiền cho nó"

Mục tiêu của giai đoạn này **không phải bán**, mà là **học**: ai đau, đau đến mức nào, và họ có
sẵn sàng đổi thời gian/tiền để hết đau không. Bài đăng là công cụ đo, không chỉ là quảng cáo.

## Phễu 4 bước

| Bước | Người xem làm gì | Ta đo gì | Bài phục vụ |
|---|---|---|---|
| 1. Nhận ra nỗi đau | Dừng lướt, thả cảm xúc, comment "mình cũng vậy" | Reach, tương tác, comment trả lời poll | 01-pain |
| 2. Tin người làm | Đọc câu chuyện, hỏi thêm | Comment hỏi, share | 02-story, 06-faq |
| 3. Hiểu giải pháp | Xem tool chạy, so sánh trước/sau | Bấm link, comment "BETA" | 03-how-it-works, 04-before-after |
| 4. Cam kết nhỏ | Làm khảo sát, để lại liên hệ dùng thử | Số câu trả lời, số đăng ký | 05-survey |

## Khung một bài: Nỗi đau → Hệ quả → Lối ra (PAS)

1. **Hook** (dòng đầu < 125 ký tự): một tình huống người đọc nhận ra ngay, bằng chính từ ngữ của họ.
2. **Hệ quả**: chi phí ẩn (thời gian, sai sót, mệt mỏi, mất lòng đồng nghiệp).
3. **Lối ra**: hé lộ cách giải — bài đầu chỉ teaser, các bài sau mới chi tiết.
4. **Hành động nhỏ**: một câu hỏi (A/B/C/D), một từ khoá để comment, hoặc link khảo sát ở comment đầu.

## 6 bài cho mỗi tool (đã có mẫu trong `campaigns/outlook-rsvp-tool/`)

`01-pain` · `02-story` · `03-how-it-works` · `04-before-after` · `05-survey` · `06-faq` — mỗi bài 4–6 ảnh.
Đăng cách nhau 2–3 ngày; trả lời mọi comment trong 1–2 giờ đầu (thuật toán ưu tiên bài có thảo luận sớm).

## Ba ngôn ngữ = ba khán giả

- **Tiếng Việt**: người Việt văn phòng — giọng thân thiện, hài hước nhẹ, ví dụ "tất niên", "tăng 2", "quỹ phòng".
- **日本語**: người làm ở công ty Nhật — です・ます, đồng cảm trước, ví dụ "幹事", "二次会", "餞別".
- **English**: nhóm quốc tế — gọn, rõ, hơi tự giễu chuyện văn phòng.

Không dịch câu-đối-câu. Cùng một **ý chính** và **cùng các con số**, nhưng ví dụ và cách nói là của từng nhóm
(`studio.py check` cảnh báo nếu số liệu giữa các ngôn ngữ lệch nhau).

## Trung thực là chiến lược

- Chỉ nói những gì có trong `brief.yaml`; con số chưa đo phải ghi "ước tính".
- Nói rõ giới hạn (Windows-only, chưa có bộ cài…) — nó lọc đúng người, và tạo niềm tin.
- Không bịa lời khen, khách hàng, giá. Một lời nói quá sẽ làm hỏng toàn bộ dữ liệu nhu cầu.

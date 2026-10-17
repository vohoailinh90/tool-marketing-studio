# 02 · Ảnh giải thích: chọn layout nào cho ý nào

Ảnh không để trang trí — mỗi ảnh trả lời **một câu hỏi** người đọc đang có. Quy tắc: 1 ý / ảnh,
≤ ~30 từ, chữ to đọc được trên điện thoại, từ khoá quan trọng tô `**nổi bật**`.

| Câu hỏi của người đọc | Layout | Ví dụ trong chiến dịch mẫu |
|---|---|---|
| "Bài này nói về gì, có liên quan tới mình không?" | `cover` | "Bạn có phải là người bị giao tổ chức tiệc?" |
| "Có đúng là chuyện của mình không?" | `chat` | Group chat hỏi ai đi tiệc |
| "Cụ thể là khổ ở đâu?" | `pains` | 6 việc người tổ chức phải làm |
| "Mất bao nhiêu thời gian?" | `flow` (variant before, có phút) | Tổng tự tính: ~3 giờ 20 phút |
| "Mọi người khác làm thế nào?" | `poll` | A/B/C/D → kéo comment |
| "Tool chạy ra sao?" | `email`, `flow` (after), `table` | Email Outlook có nút Yes/No/Maybe |
| "Khác gì cách cũ?" | `compare`, `table style: sheet` | File Excel tô màu hỗn loạn |
| "Được bao nhiêu?" | `stat` (before → after) | Ghi rõ "ước tính" |
| "Có dành cho mình không?" | `checklist` | "Tool này dành cho bạn nếu…" |
| "Ai làm, vì sao?" | `timeline`, `quote` | Từ file Excel đến ứng dụng |
| "Làm gì tiếp?" | `cta` | Từ khoá comment, QR khảo sát |
| "Cho xem thật đi" | `image` | Ảnh chụp màn hình thật (đặt trong thư mục chiến dịch) |
| "Nó chạy từng bước thế nào?" | `diagram` | Sơ đồ quy trình, ai gọi ai, vòng đời trạng thái — viết bằng Mermaid |

## Sơ đồ (`diagram`) — tùy chọn

Kiểu này **không phải mặc định**: không bài nào có sẵn, và AI soạn bài không tự chọn nó. Chỉ khi bạn thấy một sơ đồ giải thích tốt hơn chữ, hãy tự thêm slide `diagram` vào file YAML của bài.

Viết sơ đồ bằng chữ (Mermaid); engine vẽ theo màu thương hiệu của chiến dịch và font của từng ngôn ngữ.
Mỗi ngôn ngữ viết sơ đồ riêng bằng chính ngôn ngữ đó (không copy nhãn từ bản khác).

```yaml
- layout: diagram
  title: Tool **xử lý** một form thế nào
  source: |
    flowchart TD
      A[Khách gửi form] --> B{Hợp lệ?}
      B -->|Có| C[Lưu vào bảng tính]:::ok
      B -->|Không| D[Báo lỗi cho khách]:::bad
      C --> E[Gửi email xác nhận]:::hl
  caption: Mỗi bước chạy tự động
```

- Loại được vẽ: `flowchart` (hoặc `graph`), `sequenceDiagram`, `stateDiagram-v2`. Tối đa 40 dòng — sơ đồ to thì tách hai slide.
- Với ảnh dọc, dùng `flowchart TD` (trên xuống). `LR` rộng ra hai bên nên chữ nhỏ lại; render sẽ cảnh báo
  `diagram text is only about N px` khi chữ dưới 22 px — rút nhãn, bớt ô hoặc tách slide.
- Làm nổi bật bằng `:::hl` (ô đặc màu thương hiệu), `:::ok`, `:::bad`, `:::warn`, `:::muted`, hoặc `class A,B bad`.
  Không có `style`/`classDef`: màu do theme quyết định để mọi ảnh trong chiến dịch đồng bộ.
- Không được: link/`click`, HTML (trừ `<br/>` để xuống dòng), `style`/`classDef`/`linkStyle`, khối màu `rect`/`box` của sơ đồ tuần tự, `%%{init}%%`, front matter. `studio.py check` báo lỗi ngay.
- Số trong sơ đồ phải có trong brief như mọi slide khác (kể cả `ISO27001`, `v12`). Id nút cũng bị tính: dùng id ngắn như `A`, `B`, `A1` (số từ 0 đến 10 luôn được phép), đừng đặt `step12`.
- Thư viện Mermaid đã ghim phiên bản và nằm sẵn trong repo (`mkt/vendor/mermaid/`): render không cần Node hay mạng.

## Kích thước

- `portrait` 1080×1350 (mặc định, Facebook/Instagram feed — chiếm nhiều diện tích nhất trên điện thoại)
- `square` 1080×1080 · `landscape` 1200×630 (ảnh link/cover)

## Kiểm tra trước khi duyệt

- Render không báo tràn chữ (`text still overflows`).
- Mở từng ảnh ở kích thước điện thoại: đọc được dòng nhỏ nhất không?
- Ảnh chụp màn hình thật luôn thuyết phục hơn ảnh minh hoạ — nên thêm ít nhất 1 ảnh `image` thật cho bài 03.

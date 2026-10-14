# Kết luận brainstorm — System Design tiếng Việt

Ngày chốt: 2026-10-12. Người dùng đã giao viết lần lượt từng bài sau brainstorm.

**Đây là tài liệu chuẩn.** [BRIEF.md](https://github.com/vohoailinh90/Agentic-coding-course/blob/b8dff434ff75499137bbb10b61122958fdaaafa5/brainstorm/system-design-101-vi/BRIEF.md) và [README.md](https://github.com/vohoailinh90/Agentic-coding-course/blob/b8dff434ff75499137bbb10b61122958fdaaafa5/brainstorm/system-design-101-vi/README.md) là đề xuất v0 dùng để
brainstorm; nếu mâu thuẫn với tài liệu này thì tài liệu này thắng.

## Evidence và giới hạn

- [Phản hồi vòng 1](https://github.com/vohoailinh90/Agentic-coding-course/pull/23#issuecomment-6126033008)
  trả lời đủ 8 câu hỏi, đúng commit `1f5d505013def2c007a89eefff7ae571a8688a5a`.
- [Phản biện vòng 2](https://github.com/vohoailinh90/Agentic-coding-course/pull/23#issuecomment-6126126060)
  có 7 điểm cần thu gọn. Phản hồi sau đó là **code review** với hai finding, không phải
  câu trả lời đủ 7 điểm. Không ghi nhận là Codex đã phê duyệt toàn bộ quyết định dưới đây.
- Hai finding đã xử lý: ghim commit/tree và blob từng bài nguồn; đổi nhãn SSE thành
  “Đơn được xác nhận”. Đây là kết luận biên tập của người biên soạn để tiếp tục trong phạm vi
  người dùng đã giao, không phải kết quả user testing hay xác nhận của ByteByteGo.
- Kiểm kê độc lập: 15 nhóm, 404 ID, 400 đường dẫn nguồn duy nhất; vẫn giữ đủ 404 vị trí.
- Rà soát lần hai (2026-10-12, commit `5f1ad05`): Codex nêu 7 finding, đã sửa ở commit sau đó.
  Yêu cầu AUDIT kèm các phát hiện riêng của Claude nhận về review inline chứ không phải báo cáo
  theo contract, nên phần chưa có phán quyết của Codex (mục trùng nguồn, trạng thái, mô tả PR,
  trích dẫn chuẩn) chỉ dựa trên kiểm tra của người biên soạn.

## Quyết định để bắt đầu viết

| Hạng mục | Chốt |
|---|---|
| Mục lục | Đúng thứ tự nguồn; bài cùng nguồn có thể liên kết, không mất ID |
| Ngôn ngữ | Chỉ tiếng Việt; tên công nghệ giữ nguyên |
| Kho nội dung | `system-design-101/vi/`, nằm ngoài `course/` của khóa cũ |
| Mật độ | Mặc định mềm 150–300 từ phần chính; phần sâu tùy chọn, không viết cho đủ quota |
| Hình | Một hình chính hoặc các khung so sánh dọc; không thêm hình trùng ý |
| Đánh đổi | Một giới hạn, ngộ nhận hoặc bối cảnh quan trọng; không ép failure mode lên mọi bài |
| Từ viết tắt | Người mới chưa biết LLM, DNS hay SSE là gì, nên mọi từ viết tắt (hai chữ cái viết hoa trở lên) mà bài hoặc chữ trong hình có dùng đều được giải thích đầy đủ ngay trong bài, ở mục `## Từ viết tắt`: mục `##` đầu tiên của bài, ngay sau hình. Mỗi từ một dòng: `- **LLM** (Large Language Model) — mô hình ngôn ngữ lớn: câu giải thích bằng lời thường, đúng ngữ cảnh của bài`. Trong ngoặc là dạng đầy đủ bằng chữ Latin, chữ cái đầu của các từ phải ghép lại đúng bằng từ viết tắt, chỉ được bỏ các từ nối (and, for, of, the, to…); từ viết hoa trong dạng đầy đủ (HTTP trong HSTS) góp cả cụm hoặc chỉ chữ đầu (tên viết liền thì chữ hoa chỉ chỗ tách: `IDentifier`, `SYNchronize`, `JavaScript`); từ viết tắt tiếng Việt như CSDL ghi dạng đầy đủ tiếng Việt; từ viết tắt mở đầu bằng chữ số (2FA, 3DES, 2PC) tính cả chữ số và được bỏ từ chỉ số trong dạng đầy đủ (Two-Factor Authentication), còn số lượng đi với đơn vị thì viết có dấu cách ("10 GB") để đơn vị được giải thích. Lời giải thích không được dùng từ viết tắt khác chưa có dòng riêng. Bài không dùng từ viết tắt nào thì không cần mục này. Từ chỉ trông giống viết tắt (phương thức HTTP, từ khóa SQL, tên tệp) viết trong `` `code` `` hoặc thêm vào `NOT_ACRONYMS` của `scripts/sd101_check.py`; thuật ngữ viết lẫn hoa thường (gRPC, IPv4, OAuth) chịu cùng quy tắc khi đã có trong `MIXED_CASE_TERMS` của tệp đó, nên bài nào đưa vào thuật ngữ mới kiểu này thì thêm vào danh sách; tên sản phẩm có từ viết tắt nằm trong (OpenAI, MySQL, macOS) ở `EMBEDDED_ABBREVIATIONS`, và từ viết tắt trong tên đó (AI, SQL, OS) được giải thích như mọi từ khác. Chữ trong hình viết toàn bằng chữ hoa thì không phân biệt được từ viết tắt với từ thường (TIN, HAI, COOKIE), nên ở đó chỉ đọc từ không thể là từ thường: từ không có nguyên âm (JWT, DNS, LB) hoặc từ mà mục `## Từ viết tắt` của một bài nào đó trong kho đã giải thích. Chữ số trong dạng đầy đủ nếu có phải đúng chữ số của từ viết tắt (IPv4 là `Internet Protocol version 4`, không phải `version 6`); dạng đầy đủ được bỏ số. Máy kiểm việc có mục (là mục `##` đầu, đứng sau hình), đúng dạng, đủ từ; giải thích đúng và dễ hiểu là việc của người review. Không cần chú thích riêng trong hình vì mục này nằm ngay sau hình; có thể thêm vào hình nếu thấy hình hay bị tách khỏi bài. Áp dụng cho mọi bài, kể cả bài trong các PR đang mở: gộp main rồi thêm mục này |
| Tiến độ | Theo yêu cầu người dùng trong phiên biên soạn hiện tại, metadata JSON là nơi duy nhất ghi trạng thái từng bài; không nhân đôi sang YAML. `source-map.json` chỉ ghi thông tin nguồn |
| Duyệt | Ghim nguồn, kiểm chứng claim, review kỹ thuật, kiểm tra hình mobile |
| Hình trên điện thoại | Không cuộn ngang; chữ thông điệp hiệu dụng ≥ 14 px ở 375 px và ≥ 12 px ở 320 px. Đo ước lượng bằng Mermaid + Chromium, hệ số thu = min(1, (W − 32) / chiều rộng SVG); chưa thay cho kiểm tra thật trên GitHub hoặc điện thoại |
| Người học thử | Ghi riêng; chưa thực hiện thì không báo đạt. Chỉ chặn việc chuyển bài sang `approved` hoặc phát hành, không chặn viết nháp hay viết bài kế tiếp |
| Giấy phép nguồn | Nguồn là CC BY-NC-ND 4.0. Theo văn bản giấy phép, ND cho phép làm bản cải biên phi thương mại nhưng không cho chia sẻ (chưa đối chiếu lại văn bản trong phiên rà soát); kho này công khai nên đẩy lên đã là chia sẻ. Chủ repo quyết định hoãn việc giải quyết quyền dùng. Cho tới khi giải quyết, repo công khai chỉ nhận: (a) metadata nguồn (tiêu đề, URL, hash); (b) bài viết độc lập, tự viết từ kiến thức và tiêu chuẩn kỹ thuật, sơ đồ tự thiết kế, không dịch hay diễn đạt lại sát câu chữ nguồn, không dùng ảnh nguồn. Bản dịch hoặc cải biên sát nguồn không đưa vào repo công khai trước khi quyền được giải quyết. Việc một bài bám cùng chủ đề và thứ tự với nguồn có phải là cải biên hay không là câu hỏi pháp lý chưa kết luận. Đây là rủi ro còn mở, không phải đã được cho phép; không thêm bước xin duyệt cho việc viết bài độc lập |
| Ảnh nguồn | Ảnh của bài nguồn nằm ở URL ngoài (`assets.bytebytego.com`), chưa được mở và chưa được ghim, trừ khi `lesson.yaml` ghi khác. Khi review của một bài dựa vào nội dung ảnh (như ảnh Load Balancer), ghi `image_evidence` trước khi dùng làm bằng chứng. Không ghim hàng loạt ảnh từ đầu và không lưu ảnh nguồn vào repo |
| Công cụ | Metadata JSON + Markdown + SVG thiết kế mới; chưa xây framework renderer. `scripts/sd101_check.py` kiểm kho bằng máy (CI chạy qua pytest); việc đúng/sai của claim và độ dễ đọc của hình vẫn do người review |
| PR | Đợt nhỏ theo thứ tự; gọi Codex review sau thay đổi. Yêu cầu người dùng hiện tại: không tự merge/deploy, kể cả khi review sạch. Các quyền merge ghi trước đó không áp dụng cho phiên này |

## Schema tối thiểu

`source-map.json` giữ thông tin về nguồn: `source_path`, phiên bản ghim, `source_body_reviewed`,
`same_source_as` cho mục trùng nguồn (bốn cặp: `sd-01-045`/`sd-10-023`, `sd-02-019`/`sd-13-012`,
`sd-07-012`/`sd-12-010`, `sd-08-020`/`sd-10-026`). Đã đọc thân bài không có nghĩa là mọi claim đúng.

Mỗi bài chỉ có một nội dung ở `lessons/<id>/lesson.md`. Trạng thái và evidence nằm ở
`metadata/<id>.json`; `lesson.yaml` chỉ là chỉ dẫn tới JSON, không giữ bản sao trạng thái.

- `content_status`: `draft | review | done`; `done` chỉ ghi sau technical/visual review hiện hành.
- `verification`: đọc nguồn, claim, review kỹ thuật, mobile và thử người học độc lập.
- Đã có review trên SHA cũ không đồng nghĩa review tổ hợp với main mới; lưu evidence cũ và chờ review mới.
- Chưa thử người học thì không ghi đã thử hoặc đã được phê duyệt phát hành. Viết nháp tiếp không bị chặn.
- `progress.json` là điều phối công việc (PR đang mở, ID kế tiếp), không thay metadata làm nguồn quyết định.
- Evidence ảnh nguồn chỉ ghi khi thực sự dùng ảnh nguồn để kiểm chứng; không lưu ảnh nguồn vào repo.

## Phản biện kỹ thuật dựa trên tiêu chuẩn

Số mục trích dẫn dưới đây chưa được kiểm lại ở lượt rà soát 2026-10-12 (môi trường rà soát không
truy cập được rfc-editor.org và html.spec.whatwg.org). Kiểm lại khi viết `sd-01-001`.

- [RFC 6202 §2.1–2.2](https://www.rfc-editor.org/rfc/rfc6202.html): polling ngắn hỏi định kỳ;
  polling dài trả khi có sự kiện hoặc hết hạn rồi mở request mới. Request lặp không có nghĩa
  TCP connection luôn bị tạo lại; không đưa hiểu lầm đó vào hình.
- [WHATWG SSE §9.2](https://html.spec.whatwg.org/multipage/server-sent-events.html): luồng sự kiện,
  điều kiện reconnect và Last-Event-ID. Reconnect không tự bảo đảm ứng dụng phát lại dữ liệu bị bỏ lỡ.
- [RFC 6455 §1.2](https://www.rfc-editor.org/rfc/rfc6455.html): sau handshake, hai phía có thể
  gửi dữ liệu độc lập. Chi tiết heartbeat/auth/backpressure để phần sâu, không chất lên bài nhập môn.

## Thứ tự triển khai

1. `sd-01-001`: Polling ngắn, polling dài, SSE và WebSocket.
2. `sd-01-002`: Ứng dụng thực tế của bộ cân bằng tải.
3. `sd-01-003`: Các mã HTTP kỳ lạ và bối cảnh sử dụng.
4. Tiếp tục từng ID theo bảng đối chiếu, không chờ đợt thử người học; thử nghiệm với người học chỉ
   chặn phát hành (xem hàng “Người học thử”). Tiến độ ghi ở metadata JSON của từng bài.

Sửa chữa theo review sau này được ghi vào PR nội dung, không mở thêm vòng brainstorm tự động.

## Chuyển repo ngày 2026-10-13

Theo yêu cầu người dùng, kho biên soạn chuyển sang vohoailinh90/tool-marketing-studio; chương trình ở repo cũ tạm dừng. Nội dung giáo dục chỉ tiếng Việt, giữ nguyên 404 vị trí/15 nhóm/400 nguồn, dùng thư mục riêng ngoài campaigns của marketing tool. Không áp dụng mẫu ba ngôn ngữ hoặc số liệu quảng cáo cho bài học. Không tự merge/deploy/phê duyệt/đăng bài; review repo cũ chỉ là evidence lịch sử, cần review tổ hợp ở repo mới.

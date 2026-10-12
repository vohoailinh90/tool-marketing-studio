# Kế hoạch nội dung: mỗi bài học của khóa Agentic Coding → một bộ ảnh Facebook

Bản kế hoạch đã qua brainstorm với Codex (Issue #32, kết luận ACCEPT_WITH_CHANGES; các thay đổi đã áp
dụng bên dưới). Chưa có bài đăng nào trong PR này; mỗi bài học có PR riêng.

- Nguồn: `vohoailinh90/Agentic-coding-course` @ `412bbb2` — 52 bài, mỗi bài có đủ `vi`, `ja`, `en`.
- Facts về khóa học: `brief.yaml`. Giọng văn: `positioning/vi.yaml`.
- Mục tiêu: tăng tương tác của Page (lưu, bình luận, theo dõi) — **bài chia sẻ kiến thức, không phải
  bài kiểm chứng nhu cầu**, nên không có khảo sát, không có waitlist.

**Chủ Page đã quyết (2026-10-12):** (1) được đăng khi bài học còn ở trạng thái `review`;
(2) **tạm thời chỉ đăng tiếng Việt** — mỗi PR bài học chỉ có bản `vi`; `ja`/`en` thêm sau bằng PR riêng;
(3) **điều quan trọng nhất là phủ đủ kiến thức của bài học** — một bộ ảnh chỉ còn vài ý tóm tắt (như
PR #26 cho bài `security-basics`: 7 ảnh, chỉ 4 ý của phần tóm tắt, mất các bước, ví dụ và đố vui) là
không đạt.

## 1. Nguyên tắc

1. **Bài học là nguồn sự thật duy nhất.** Mọi ý lấy từ file bài học tiếng Việt ở commit ghi trong PR.
   Không thêm số liệu, ví dụ hay khẳng định mà bài học không có.
2. **Đủ kiến thức, đo được.** Bài học được tách thành **từng ý nhỏ** (mỗi đoạn văn, gạch đầu dòng,
   tiêu đề nhỏ, khối code, sơ đồ — `scripts/lesson_coverage.py extract`). Mỗi ý phải nằm trên **một
   ảnh hoặc trong caption**, và file phủ (mục 7) trích đúng chữ đang hiển thị ở đó. Thiếu một ý là
   CI đỏ.
3. **Ảnh + caption phải tự đủ.** Bình luận đầu chỉ để lặp lại đáp án cho tiện và gắn `{link}`; không ý
   nào được chỉ nằm ở bình luận đầu hay sau link.
4. **Một ý một ảnh, ≤ ~30 chữ**, từ khóa tô `**đậm**`. Ý không vừa ảnh thì vào caption, dưới tiêu đề
   rõ ràng — không bỏ.
5. **Không URL trong bài.** Trạng thái luôn `draft`; duyệt và đăng là việc của chủ Page.

## 2. Khung một bộ ảnh (8–10 ảnh, tối đa 10 là luật cứng)

Khóa học có 12 kiểu cấu trúc bài khác nhau (29 bài có `try-it`, một số bài có cả ví dụ đời thường, ví
dụ thực tế lẫn `try-it`), nên khung là **các vị trí theo chức năng**, không phải một phần cố định cho
mỗi số ảnh:

| Ảnh | Nội dung bắt buộc | Gợi ý layout |
|---|---|---|
| 1 | Hook (`social.hook`), tên bài, "Bài x.y.z · N phút", mục tiêu chính | `cover` |
| 2 | Vì sao cần biết (phần Mở đầu) | `chat`, `pains` |
| 3–8 | **Sáu ảnh chia linh hoạt** cho: các khái niệm con, sơ đồ của bài, ví dụ đời thường (kèm "chỗ chưa khớp"), ví dụ thực tế, các mốc `try-it`, hiểu lầm → thực tế | `image`, `features`, `flow`, `checklist`, `compare`, `table`, `chat` |
| 9 | Hình tóm tắt của bài (recap) | `image` |
| 10 | Đố vui: 1 câu của bài, "Comment A, B hay C"; bài không có đố vui thì dùng `social.question` | `poll` |

- Mỗi ảnh một ý. Bài có nhiều ý hơn sáu ảnh thì chọn những ý **nên nhìn bằng hình** (quy trình, so
  sánh, sơ đồ) cho ảnh; ý còn lại vào caption theo đúng tiêu đề bên dưới.
- Bài có `try-it` dài: ảnh `flow` cho các mốc (≤ 7 bước/ảnh); lệnh chính xác, dữ liệu mẫu, kết quả
  mong đợi, tiêu chí hoàn thành vào phần **Thử ngay** của caption.
- Không bịa đố vui cho bài không có đố vui.

### Caption (cấu trúc cố định, chỉ giữ các mục bài học có)

1. Hook.
2. **Sau bài này bạn sẽ…** — mọi mục tiêu.
3. **Nội dung bổ sung** — các ý của phần khái niệm, ví dụ, hiểu lầm chưa nằm trọn trên ảnh.
4. **Thử ngay** — phần `try-it` chưa nằm trên ảnh, đủ điều kiện an toàn và tiêu chí hoàn thành.
5. **Ghi nhớ** — mọi ý của phần Ghi nhớ.
6. **Đố vui** — các câu không có trên ảnh 10, đủ phương án A/B/C.
7. **Đáp án — xem sau khi bạn đã chọn** — đáp án và lời giải thích của **cả 3 câu**.
8. `social.question` của bài.
9. Lời mời lưu bài / theo dõi / "Bài sau: …".
10. Một dòng: *Khóa học đang được hoàn thiện; câu chữ hoặc ví dụ có thể được cập nhật.*
11. Tên nguồn tham khảo của bài (không URL).

Bình luận đầu: lặp lại đáp án + `{link}` tới bài học tiếng Việt.

### Ví dụ: bài 1.1.2 "Bộ não, đôi tay và vòng lặp" (48 ý)

| Ảnh | Layout | Nội dung |
|---|---|---|
| 1 | `cover` | "AI agent = **bộ não + đôi tay + một vòng lặp**" — mục tiêu chính |
| 2 | `chat` | "LLM chỉ tạo ra chữ… vậy làm sao agent **mở được file**?" |
| 3 | `image` | sơ đồ `agent-formula` + 3 phần (LLM, công cụ, vòng lặp) |
| 4 | `checklist` | LLM chỉ *yêu cầu* dùng công cụ; phần mềm của agent quyết định và mới thật sự "bấm nút" |
| 5 | `image` | sơ đồ `agent-loop` — suy nghĩ → hành động → quan sát, và 3 lúc dừng |
| 6 | `features` | Đầu bếp: kinh nghiệm / dao-bếp / nêm-nếm-chỉnh; note: chỗ chưa khớp |
| 7 | `flow` | Đổi tên 50 ảnh: liệt kê → 3 ảnh thiếu ngày → **hỏi bạn** → đổi tên → kiểm lại → dừng |
| 8 | `compare` | 2 hiểu lầm → thực tế |
| 9 | `image` | recap `agent-parts-and-loop-recap` |
| 10 | `poll` | Câu 2; câu 1 và 3 + đáp án cả 3 trong caption |

## 3. Sơ đồ của khóa học

Sơ đồ SVG của khóa học (107 sơ đồ tiếng Việt) được chuyển sang PNG, vì layout `image` không nhận SVG.

- Chuyển **2x**, lưu `campaigns/agentic-coding-course/diagrams/vi/<tên>.png`, tên giữ nguyên tên SVG
  (file phủ đối chiếu theo tên).
- **Ngưỡng đọc được** (đo trên ảnh 1080px đã render): chữ thường ≥ 24px, nhãn phụ ≥ 22px, tiêu đề và số
  bước ≥ 28px; không ý nào chỉ nằm ở chữ < 22px. Xem ảnh ở bề rộng điện thoại 360px, không phóng to.
- Sơ đồ không đạt ngưỡng: **dựng lại bằng layout có sẵn** (`features`, `flow`, `compare`, `table`…) với đúng chữ
  của sơ đồ và chữ đủ lớn. Cắt hay chia nhỏ ảnh không giải quyết được vì file phủ nhận ra sơ đồ theo tên ảnh. Trong
  file phủ, ý `diagram` ghi `dest` là slide (hoặc caption) đã dựng lại và `evidence` trích đúng chữ nhãn của sơ đồ.
  Script đọc chữ từ file SVG ở commit đã ghim và đòi slide/caption đó hiện **ít nhất 60% chữ của sơ đồ**. Chữ này
  không tính chung với các ý văn xuôi: một nhãn vẽ ra có thể chứng minh cả sơ đồ lẫn đoạn văn nhắc cùng điều đó.
  Slide `image` luôn phải hiện đúng ảnh của sơ đồ đó; dựng lại thì dùng layout chữ hoặc caption.
- Một script chuyển đổi có manifest (nguồn, commit, hash) là bước sau; trước mắt, PR nào chuyển sơ đồ
  ghi rõ commit nguồn trong mô tả PR.

## 4. Thứ tự và nhịp PR

1. **Lộ trình tối thiểu trước** (19 bài): chatbot-to-agent, agent-parts-and-loop,
   watch-an-agent-build, choose-your-learning-setup, data-safety-and-permissions, first-agent-session,
   lead-not-typist, writing-good-specs, explore-plan-build-verify, files-folders-paths,
   reviewing-agent-changes, testing-basics, errors-and-debugging, project-personal-page, data-formats,
   git-version-control, hallucination, context-window, project-office-automation.
2. Sau đó 33 bài còn lại theo thứ tự trong `curriculum.yaml`.
3. **Một PR = một bài (tiếng Việt)**: `posts/vi/<lesson-id>.yaml`, `coverage/<lesson-id>.yaml`, sơ đồ
   PNG, ảnh đã render. `id` bài đăng = `id` bài học.
4. Nhịp đăng gợi ý (chủ Page quyết): 1 bài học/tuần, tối 20:00–21:30.

## 5. Chiến dịch

`campaigns/agentic-coding-course/campaign.yaml` (tạo cùng PR bài đầu tiên): `langs: [vi]`,
`platforms: [facebook]`, không có `validation`. Mỗi bài học một khóa link trỏ thẳng tới trang bài
tiếng Việt: `links.<lesson-id>` → `…/course/vi/lessons/<lesson-id>.md`; bài đăng chọn bằng
`link: <lesson-id>`. Thêm `links.course-home` cho bài đăng cấp series.

## 6. Cơ chế kéo tương tác

- Ảnh recap ở cuối — lý do để **lưu bài**.
- Đố vui A/B/C — bình luận một chữ cái; đáp án ở cuối caption dưới tiêu đề "xem sau khi bạn đã chọn",
  lặp lại ở bình luận đầu.
- `social.question` — câu hỏi mở cho cộng đồng.
- "Bài x.y.z" và "Bài sau: …" — lý do để **theo dõi** Page.

## 7. File phủ kiến thức và kiểm tra mỗi PR

Mỗi bài có `campaigns/agentic-coding-course/coverage/<lesson-id>.yaml`, tạo bằng:

```
python3 scripts/lesson_coverage.py extract <course>/course/vi/lessons/<id>.md \
    --lesson <id> --commit <40-ký-tự SHA của khóa học> > campaigns/agentic-coding-course/coverage/<id>.yaml
```

Lệnh này liệt kê **mọi ý** của bài (`key`, `kind`, `source`): từng đoạn văn, từng gạch đầu dòng (cả
mục con), từng dòng bảng, từng trích dẫn `>`, từng tiêu đề nhỏ, khối code và sơ đồ, cộng `social.hook` và
`social.question` — trung bình ~61 ý mỗi bài. File `coverage/<id>.yaml` chỉ được đối chiếu với
`posts/vi/<id>.yaml` và `course/vi/lessons/<id>.md`. Người viết điền cho từng ý:
- `dest`: `slide:N` hoặc `caption` (không được là bình luận đầu);
- `evidence`: một câu trích hoặc danh sách câu trích, **đúng chữ đang hiển thị** trong một ô chữ của
  `dest` mà layout thật sự vẽ ra. Các câu trích (chữ trùng nhau chỉ tính một lần) phải phủ ít nhất **30% số chữ của ý** (tối thiểu 3 chữ, ý ngắn hơn thì
  trích cả ý); khối code phải hiện **đủ**; một chữ trên ảnh chỉ chứng minh cho một ý. Với sơ đồ, `dest` là
  ảnh `image` hiển thị đúng sơ đồ đó, hoặc slide/caption dựng lại sơ đồ (mục 3).

Kiểm tra (CI tự clone khóa học và chạy dòng đầu):

- `python3 scripts/lesson_coverage.py check --all --course-dir <clone khóa học>` — mỗi bài đăng của
  chiến dịch có file phủ; danh sách ý trùng **chính xác** với bài học ở commit đã ghi (không bỏ ý, không
  sửa chữ nguồn, không thêm ý); mọi câu trích có thật ở đúng chỗ; ≤ 10 ảnh.
- `python3 studio.py check agentic-coding-course` — 0 lỗi, 0 cảnh báo về số ảnh.
- `python3 studio.py render agentic-coding-course` — không tràn chữ; mở từng ảnh ở bề rộng 360px.

Script không chấm được diễn đạt có trung thành không — đó vẫn là việc của người review.

## 8. Câu hỏi đã chốt (Issue #32)

1. Một bộ 8–10 ảnh mỗi bài, không bắt buộc bài đố vui riêng (có thể thử sau như bài phụ).
2. Sơ đồ: chuyển SVG → PNG là mặc định; dựng lại bằng layout chỉ khi không đạt ngưỡng đọc.
3. Ngưỡng chữ: 24 / 22 / 28px trên ảnh 1080px, xem ở 360px (mục 3).
4. Link: một khóa `links.<lesson-id>` mỗi bài, thêm `links.course-home`.
5. Phủ kiến thức: file phủ theo từng ý, kiểm bằng script ngay từ bài đầu tiên.
6. Caption có một dòng nói khóa học đang được hoàn thiện.

Còn để chủ Page quyết khi cần: caption dài với bài nhiều `try-it`; khi bài học đổi câu chữ thì làm gì
với bài đã đăng (không làm gì / bình luận đính chính / render lại).

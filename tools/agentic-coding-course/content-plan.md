# Kế hoạch nội dung: mỗi bài học của khóa Agentic Coding → một bộ ảnh Facebook

Bản đề xuất để brainstorm với Codex trước khi viết bài. Chưa có bài đăng nào trong PR này; mỗi bài
học sẽ có PR riêng sau khi kế hoạch được chốt.

- Nguồn: `vohoailinh90/Agentic-coding-course` @ `412bbb2` — 52 bài, mỗi bài có đủ `vi`, `ja`, `en`.
- Facts về khóa học: `brief.yaml`. Giọng văn từng thị trường: `positioning/{vi,ja,en}.yaml`.
- Mục tiêu: tăng tương tác của Page (lưu, bình luận, theo dõi) — **bài chia sẻ kiến thức, không phải
  bài kiểm chứng nhu cầu**, nên không có khảo sát, không có waitlist.

**Chủ Page đã quyết (2026-10-12):** (1) được đăng khi bài học còn ở trạng thái `review`;
(2) **tạm thời chỉ đăng tiếng Việt** — mỗi PR bài học chỉ có bản `vi`; `ja`/`en` thêm sau, khi chủ
Page mở lại, bằng PR riêng viết từ bài học của chính ngôn ngữ đó.

## 1. Nguyên tắc

1. **Bài học là nguồn sự thật duy nhất.** Mọi ý trên ảnh lấy từ file bài học của đúng ngôn ngữ đó, ở
   commit ghi trong PR. Không thêm số liệu, ví dụ hay khẳng định mà bài học không có.
2. **Đủ kiến thức, không chỉ trích đoạn.** Mỗi phần của bài (mục tiêu, nội dung chính, ví dụ đời
   thường, ví dụ thực tế, hiểu lầm, tóm tắt, ghi nhớ, đố vui) phải xuất hiện ở ít nhất một ảnh hoặc
   trong caption. PR của mỗi bài kèm bảng "phần bài học → ảnh số mấy" để kiểm.
3. **Mỗi ngôn ngữ một bài hoàn chỉnh.** Hiện chỉ `vi`. Khi thêm `ja`/`en`: viết từ bài học của chính
   ngôn ngữ đó (khóa học vốn đã viết riêng từng thứ tiếng), không dịch câu-theo-câu; giữ cùng `id`.
4. **Một ý một ảnh, ≤ ~30 chữ**, từ khóa tô `**đậm**`; chữ đọc được trên điện thoại.
5. **Không URL trong bài.** Link chỉ qua `{link}` ở bình luận đầu. Trạng thái luôn `draft`; duyệt và
   đăng là việc của chủ Page.

## 2. Khung một bộ ảnh (8–10 ảnh, Facebook cho tối đa 10)

| # | Phần bài học | Layout | Ghi chú |
|---|---|---|---|
| 1 | `social.hook` + tiêu đề + **mục tiêu** | `cover` | eyebrow: "Bài 1.1.2 · 8 phút"; subtitle: mục tiêu chính của bài ("Sau bài này bạn…"); badge: loại bài (Khái niệm / Thực hành / Dự án) |
| 2 | Mở đầu (vì sao cần biết) | `chat` hoặc `pains` | câu hỏi người mới hay hỏi, đúng như phần "Mở đầu" |
| 3–5 | Nội dung chính | `image` (sơ đồ của bài) + `features` / `flow` / `checklist` | mỗi khái niệm con một ảnh; sơ đồ có sẵn thì dùng sơ đồ |
| 6 | Ví dụ đời thường | `features` hoặc `compare` | ánh xạ từng phần; "chỗ chưa khớp" vào `note` |
| 7 | Ví dụ thực tế | `flow` / `chat` / `table` | giữ nguyên các bước của bài |
| 8 | Hiểu lầm thường gặp | `compare` | trái "Hiểu lầm", phải "Thực tế" |
| 9 | Tóm tắt bằng hình | `image` (sơ đồ recap của bài) | ảnh "nhớ cả bài trong 1 hình" — dễ được lưu nhất |
| 10 | Đố vui | `poll` | 1 câu trong 3 câu đố của bài, "Comment A, B hay C"; 2 câu còn lại nằm trong caption |

Caption (Facebook): hook → **mọi mục tiêu của bài** ("Sau bài này bạn sẽ…") → 2–3 câu tóm nội dung →
các ý "Ghi nhớ" → **2 câu đố còn lại** (đủ phương án A/B/C) → `social.question` → nhắc lưu bài → tên
nguồn tham khảo (không URL). Bình luận đầu: **đáp án cả 3 câu đố** kèm lời giải thích của bài + `{link}`.
Đường link chỉ là để đọc thêm, không phải nơi chứa kiến thức: bỏ link đi thì ảnh + caption vẫn đủ bài.

Các phần của bài thay đổi theo loại bài: bài **Dự án** và một số bài Thực hành có phần `try-it` (các
bước làm) thay cho "Ví dụ đời thường"/"Ví dụ thực tế", và có thể không có đố vui. Khung trên áp dụng
cho **đúng các phần mà bài đó có**: mỗi phần vẫn phải nằm trên ảnh hoặc trong caption. Với bài Dự án,
ảnh 6–8 là các bước `try-it` (`flow`, mỗi ảnh ≤ 7 bước, chia nhiều ảnh nếu dài) + sản phẩm cuối +
tiêu chí hoàn thành; chi tiết từng bước được nén vào caption, không đẩy sang link.

### Ví dụ: bài 1.1.2 "Bộ não, đôi tay và vòng lặp"

| # | Layout | Nội dung |
|---|---|---|
| 1 | `cover` | "AI agent = **bộ não + đôi tay + một vòng lặp**" — subtitle: "Sau bài này bạn biết agent được ghép từ gì và khi nào nó dừng để hỏi bạn." |
| 2 | `chat` | "LLM chỉ tạo ra chữ… vậy làm sao agent **mở được file**?" |
| 3 | `image` | `agent-formula` — công thức 3 phần |
| 4 | `checklist` | LLM chỉ *yêu cầu* dùng công cụ; phần mềm của agent quyết định cho phép và mới thật sự "bấm nút" |
| 5 | `image` | `agent-loop` — suy nghĩ → hành động → quan sát, và 3 lúc dừng |
| 6 | `features` | Đầu bếp: kinh nghiệm = bộ não, dao/bếp = đôi tay, nêm–nếm–chỉnh = vòng lặp; note: đầu bếp luôn nếm được, agent chỉ "nếm" được thứ công cụ cho thấy |
| 7 | `flow` | Đổi tên 50 ảnh: liệt kê → 3 ảnh thiếu ngày chụp → **hỏi bạn** → đổi tên → kiểm lại → dừng |
| 8 | `compare` | "LLM tự mở file được" / "Agent nào cũng tự sửa lỗi" → thực tế |
| 9 | `image` | `agent-parts-and-loop-recap` |
| 10 | `poll` | Câu 2: agent không được chạy thử trang web — điều gì dễ xảy ra nhất? (câu 1 và 3 trong caption; đáp án cả 3 ở bình luận đầu) |

Đã thử render cục bộ (không commit): sơ đồ của khóa học chuyển sang PNG đặt trong layout `image`
1080×1350 vẫn rõ và đúng nhận diện của khóa học.

## 3. Sơ đồ của khóa học

Khóa học có sẵn sơ đồ SVG riêng cho từng ngôn ngữ (`course/<lang>/diagrams/*.svg`), sinh tự động,
có 1 hình recap cho mỗi bài. Layout `image` của studio chỉ nhận `.png/.jpg/.webp` (SVG có thể chứa
script), nên cần chuyển sang PNG.

- **Đề xuất:** thêm `scripts/course_diagrams.py` (một yêu cầu phần mềm riêng, đi qua routing): đọc
  repo khóa học ở một commit, chuyển các sơ đồ của một bài sang PNG 2x vào
  `campaigns/agentic-coding-course/diagrams/<lang>/<tên>.png`, ghi commit nguồn vào manifest. Làm tay
  52 × 3 lần dễ lệch; một script thì lặp lại được và kiểm được.
- **Phương án khác:** dựng lại mọi sơ đồ bằng layout có sẵn (`features`, `flow`…). Chữ được `check`
  kiểm, nhưng mất nhận diện chung với khóa học và tốn gấp đôi công.

## 4. Thứ tự và nhịp PR

1. **Lộ trình tối thiểu trước** (19 bài, đúng như kế hoạch Facebook của chính khóa học):
   chatbot-to-agent, agent-parts-and-loop, watch-an-agent-build, choose-your-learning-setup,
   data-safety-and-permissions, first-agent-session, lead-not-typist, writing-good-specs,
   explore-plan-build-verify, files-folders-paths, reviewing-agent-changes, testing-basics,
   errors-and-debugging, project-personal-page, data-formats, git-version-control, hallucination,
   context-window, project-office-automation.
2. Sau đó 33 bài còn lại theo thứ tự trong `curriculum.yaml`.
3. **Một PR = một bài (tiếng Việt)**: `posts/vi/<lesson-id>.yaml`, sơ đồ PNG, ảnh đã render, bảng
   phủ kiến thức. `id` bài đăng = `id` bài học (ổn định, không đổi khi bài đổi chỗ).
4. Nhịp đăng gợi ý (chủ Page quyết): 1 bài học/tuần như kế hoạch của khóa học, tối 20:00–21:30.

## 5. Chiến dịch

`campaigns/agentic-coding-course/campaign.yaml` (tạo cùng PR bài đầu tiên): `langs: [vi]`,
`platforms: [facebook]`, không có `validation` vì đây không phải bài kiểm chứng nhu cầu. Vì chỉ có
tiếng Việt, mỗi bài học có một khóa link riêng trỏ thẳng tới trang bài học tiếng Việt, ví dụ
`links.agent-parts-and-loop` → `course/vi/lessons/agent-parts-and-loop.md`, và bài đăng chọn nó bằng
`link: agent-parts-and-loop` (engine tự gắn UTM theo bài) — không cần sửa engine.

## 6. Cơ chế kéo tương tác

- Ảnh recap ở cuối — lý do để **lưu bài**.
- Đố vui A/B/C — bình luận một chữ cái, đáp án ở bình luận đầu.
- `social.question` của bài — câu hỏi mở cho cộng đồng.
- Nhãn series "Bài x.y.z" và "Bài sau: …" trong caption — lý do để **theo dõi** Page.

## 7. Kiểm tra mỗi PR

`studio.py check` **không** kiểm được việc phủ kiến thức, và vượt 10 ảnh chỉ là cảnh báo
(`mkt/check.py`, `MAX_SLIDES`). Vì vậy ngoài các lệnh dưới, mỗi bài đăng có một **ma trận phủ** trong
trường `notes`: mỗi phần của bài học (theo các marker `section: …` trong file bài học) → ảnh số
mấy hoặc `caption` / `first_comment`. Phần nào chưa có chỗ thì PR chưa được merge.

- `python3 studio.py check agentic-coding-course` — 0 lỗi **và 0 cảnh báo về số ảnh** (tối đa 10 là
  luật cứng của chiến dịch này, không phải gợi ý).
- `python3 studio.py render agentic-coding-course` — không báo tràn chữ.
- Mở từng ảnh ở cỡ điện thoại; ma trận phủ trong `notes` đủ mọi phần.
- Khi đã có vài bài, việc đối chiếu marker ↔ ma trận nên thành một script (đếm được thì để script làm).

## 8. Câu hỏi mở

1. Khung 10 ảnh có đủ phủ kiến thức mà vẫn dễ lướt không, hay nên tách mỗi bài thành 2 bài đăng
   (bài học + đố vui riêng, như dạng A và C trong kế hoạch Facebook của khóa học)?
2. Sơ đồ: chuyển SVG → PNG bằng script (đề xuất) hay dựng lại bằng layout?
3. Chữ nhỏ trong sơ đồ 800px khi đặt vào ảnh 1080px có đủ đọc trên điện thoại không — cần ngưỡng cỡ chữ tối thiểu?
4. Link: một khóa `links.<lesson-id>` cho mỗi bài (mục 5) — 52 khóa trong `campaign.yaml` có chấp
   nhận được không, hay nên trỏ chung về trang chủ khóa học tiếng Việt?
5. Ma trận phủ trong `notes` (mục 7) có đủ chặt không, và nên thành script ngay từ bài đầu hay sau
   vài bài?
6. ~~Đăng khi bài học còn `review`~~ — chủ Page đã quyết: được. Câu hỏi còn lại: caption có nên
   ghi rõ bài học đang được hoàn thiện (có thể đổi câu chữ) không?

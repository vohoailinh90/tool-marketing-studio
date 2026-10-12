# Tool Marketing Studio

Repo chuyên dụng để **giới thiệu các tool của mình**, đo xem người ta có thật sự cần không,
rồi mới quyết định thương mại hoá. Mỗi tool đi qua cùng một vòng:

```
Dữ kiện (brief) → Định vị theo từng ngôn ngữ → Bài đăng + ảnh giải thích → Duyệt → Đăng
      ↑                                                                          ↓
 Phát triển tiếp  ←  AI phân tích nhu cầu  ←  Số liệu + comment  ←  Lịch sử đăng
```

- **3 ngôn ngữ, viết riêng**: mỗi bài có 3 bản hoàn chỉnh — Tiếng Việt, 日本語, English —
  viết cho đúng khán giả của từng ngôn ngữ, không dịch từng câu.
- **Nhiều ảnh giải thích**: 15 kiểu slide (đoạn chat, quy trình có tính giờ, trước/sau, bảng Excel
  "hỗn loạn", email Outlook giả lập, số liệu lớn, khảo sát…) render ra PNG 1080×1350 cho Facebook.
- **App có giao diện** (Automation UI Kit): phân tích → viết bài bằng AI → xem trước & duyệt →
  đăng → lịch sử đăng → phân tích nhu cầu.
- **Chiến dịch mẫu**: Outlook RSVP Tool — 6 bài × 3 ngôn ngữ = 99 ảnh trong
  `campaigns/outlook-rsvp-tool/export/`.

## Chạy app

Cần Python 3.10+ trên Windows/macOS/Linux.

```bash
pip install -r requirements.txt
python -m playwright install chromium     # trình duyệt ẩn dùng để render ảnh (một lần)
copy .env.example .env                    # macOS/Linux: cp .env.example .env — rồi điền key nếu có
python app.py                             # hoặc nhấp đúp start-app.bat trên Windows
```

App mở ở http://127.0.0.1:8765 và **chỉ chạy trên máy bạn**: nó giữ API key và có thể đăng bài.
Bản build giao diện (`web/dist`) đã nằm sẵn trong repo nên không cần cài Node.

| Trang | Làm gì |
|---|---|
| Tổng quan | Ma trận bài × ngôn ngữ, trạng thái, kiểm tra chiến dịch |
| Phân tích | AI viết định vị (khán giả, nỗi đau, lời hứa) cho từng ngôn ngữ |
| Viết bài | AI viết nháp từng bài cho từng ngôn ngữ & nền tảng — tự kiểm tra, sửa 1 vòng |
| Xem trước & duyệt | Sửa nội dung, render ảnh, đọc kỹ, duyệt **đúng phiên bản đó** |
| Đăng bài | Đăng lên Facebook Page bằng API, hoặc tải gói ảnh + nội dung để đăng tay rồi ghi lại |
| Lịch sử đăng | Tool nào, bài nào, ngôn ngữ, nền tảng, nơi đăng, thời gian, link, tương tác, comment |
| Phân tích nhu cầu | Số liệu → kết luận (Nên làm tiếp / Chưa đạt / Chưa đủ dữ liệu) + AI đề xuất bước tiếp theo |

**Không có API key?** Bật "Chế độ copy-paste": app đưa prompt để bạn dán vào claude.ai, rồi dán
câu trả lời lại — vẫn được kiểm tra y như khi gọi API.

## Dòng lệnh (CLI)

```bash
python studio.py check                          # kiểm tra mọi chiến dịch (0 lỗi mới được duyệt)
python studio.py render outlook-rsvp-tool       # render ảnh + nội dung từng nền tảng
python studio.py approve outlook-rsvp-tool --post 01-pain --lang vi
python studio.py pack outlook-rsvp-tool --post 01-pain --lang vi        # gói zip để đăng tay
python studio.py publish --smoke facebook                               # kiểm tra kết nối Page
python studio.py publish outlook-rsvp-tool --post 01-pain --lang vi     # chạy thử; --yes để đăng thật
python studio.py posted outlook-rsvp-tool --post 01-pain --lang vi --platform facebook \
       --where "Group Dân văn phòng" --url https://... --at "2026-10-14 20:30"
python studio.py history                        # lịch sử đăng (--markdown để xuất bảng)
python studio.py feedback scan|add ...          # quét comment từ Page / dán comment
python studio.py metrics outlook-rsvp-tool      # tỉ lệ + kết luận theo từng ngôn ngữ
python studio.py survey responses.csv           # đếm câu trả lời từ file CSV của Google Forms
python studio.py insights outlook-rsvp-tool     # AI phân tích nhu cầu → insights/<ngày>-vi.md
python studio.py new excel-to-planner --name "Excel to Planner" --repo vohoailinh90/Excel-to-planner
python studio.py doctor                         # máy đã sẵn sàng chưa
```

## Cấu trúc

```
tools/<tool>/brief.yaml              dữ kiện (mọi bài chỉ được nói những gì có ở đây)
tools/<tool>/positioning/<lang>.yaml định vị, viết riêng cho từng ngôn ngữ
tools/catalog.yaml                   danh sách các tool và trạng thái marketing
campaigns/<c>/campaign.yaml          ngôn ngữ, nền tảng, link khảo sát, lịch, ngưỡng kết luận
campaigns/<c>/posts/<lang>/<id>.yaml một bài hoàn chỉnh bằng một ngôn ngữ
campaigns/<c>/export/<lang>/<id>/    ảnh PNG + nội dung từng nền tảng + manifest
campaigns/<c>/published.yaml         sổ đăng bài (API và đăng tay)
campaigns/<c>/insights/              báo cáo phân tích nhu cầu của AI
playbooks/                           chiến lược, hình ảnh, Facebook, kiểm chứng nhu cầu, thương mại hoá
research/                            mẫu khảo sát và kịch bản phỏng vấn (3 ngôn ngữ)
mkt/                                 engine (Python)        web/   giao diện (React + UI kit)
office/ + scripts/office/            văn phòng agent: ai đang làm gì (trang React + server chỉ-đọc)
.claude/                             team agent + skill cho Claude Code
```

## Những điều cần làm trước khi đăng bài thật

1. **Đặt link khảo sát**: tạo Google Form theo `research/survey-template.md`, thêm câu hỏi ẩn
   "source", lấy link điền sẵn có `{source}` và dán vào `links.survey` trong `campaign.yaml`.
2. **Xác nhận câu chuyện**: các ý trong `story_to_confirm` của brief là mình đoán từ README — sửa cho đúng.
3. **Con số thời gian** (~3 giờ 20 phút → ~30 phút) là ước tính, đã ghi rõ trong bài; hãy đo lại khi có người dùng thử.
4. Điền `author.handle` trong `studio.yaml` nếu muốn tên Page hiện trên ảnh.
5. Render lại, đọc từng ảnh, đổi `status: ready`, duyệt, rồi đăng.

## Phát triển tiếp với Claude Code

Repo mang theo đủ team agent của `claude-agent-routing-template`: 8 subagent Claude
(`.claude/agents/`), chính sách định tuyến `agent-routing/` + hook giới hạn ngân sách agent, làn Codex,
và cách dùng team model miễn phí trên VPS cho repo này — xem `docs/agent-team.md`. Mọi thay đổi code
đi qua quy trình phân loại T0–T3 trong `CLAUDE.md`; viết nội dung marketing dùng skill `tool-campaign`.

### Xem agent làm việc (văn phòng agent)

Một trang chỉ-đọc cho thấy agent nào đang làm gì, tiến độ, ngân sách agent và đường bàn giao; có chế độ
sáng/tối và tiếng Việt, Nhật, Anh. Trang build sẵn trong `office/dist`, không cần Node:

```
python3 scripts/office/serve.py        # mở http://127.0.0.1:8765
```

Chưa có dữ liệu thì trang mở thẳng vào một lượt **chạy mẫu**. Dữ liệu thật do hook ghi
(`.claude/settings.json` đã bật sẵn) vào `artifacts/handoff/office-events.jsonl`, cộng với sổ ngân sách
`scripts/route.py --record`. Server chỉ nghe `127.0.0.1`. Cách dùng, nguồn từng con số và giới hạn:
`docs/office-dashboard.md`.

**CI:** repo private nên phút GitHub-hosted bị tính phí; nếu job CI fail ngay không có log, đăng ký runner
VPS cho repo này và đặt biến `CI_RUNNER` (hướng dẫn trong `docs/agent-team.md`).
Kiến trúc: `docs/architecture.md`. Kết nối Facebook: `docs/facebook-page.md`.

## System Design tiếng Việt

Chương trình học bằng hình, chỉ tiếng Việt: [mục lục](system-design-101/vi/README.md), [tiến độ](system-design-101/vi/PROGRESS.md). Giữ đúng15 nhóm/404 vị trí ByteByteGo (400 tài liệu nguồn). Kho giáo dục riêng; chưa đưa vào giao diện chiến dịch hoặc phê duyệt phát hành.

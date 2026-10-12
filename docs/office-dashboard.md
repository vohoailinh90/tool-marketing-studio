# Văn phòng agent: bảng theo dõi team agent

Một trang web chỉ-đọc cho thấy ai đang làm gì trong team agent: main session ở trên,
các phòng ban bên dưới, mỗi agent là một robot ngồi bàn, đường nét chạy giữa hai thẻ
khi việc được bàn giao. Có hai kiểu nhìn: **subagent Claude** (theo tầng T0-T3 của
repo) và **pipeline VPS** (`team.py` chạy trên VPS, xem `docs/agent-team.md`). Giao diện có chế độ sáng và tối,
tiếng Việt, tiếng Nhật và tiếng Anh.

```text
hook (office_events.py)  ─►  artifacts/handoff/office-events.jsonl ─┐
route.py --record        ─►  artifacts/handoff/agent-budget.json  ──┼─► snapshot.py ─► serve.py ─► office/ (trang)
team.py                  ─►  /srv/team/work/<id>/out/state.json  ───┘      (hàm thuần)   (GET)
```

## Chạy thử ngay, chưa cần dữ liệu thật

```bash
cd office && npm ci && npm run build && cd ..
python3 scripts/office/serve.py            # http://127.0.0.1:8765
```

Checkout chưa có dữ liệu thì trang mở thẳng vào **chạy mẫu**: hai lượt chạy ghi sẵn
(`scripts/office/demo/`), phát lại bằng đúng mã đọc dữ liệu thật. Nút "Dữ liệu thật /
Chạy mẫu" ở góc trên để đổi qua lại.

## Nối dữ liệu thật

1. **Bật hook.** Repo này đã có sẵn `.claude/settings.json` (bản sao của `settings.example.json`), nên
   phiên Claude Code mới tự nạp hook. Repo khác tạo từ template mà chưa có thì `cp .claude/settings.example.json
   .claude/settings.json` (nếu bạn đã có `settings.json` thì chép các mục `office_events.py` vào). Hook chỉ ghi:
   không bao giờ chặn công cụ và luôn thoát mã 0.
   **Hook lưu gì** vào `artifacts/handoff/office-events.jsonl` (bị gitignore, tạo với quyền chỉ chủ file đọc):
   mã phiên, tên công cụ, mã và loại agent, thời điểm, trạng thái cùng số token, thời lượng, số lần gọi công cụ của
   spawn, mô tả ngắn của tác vụ, và hai đoạn văn bản tự do, mỗi đoạn tối đa 240 ký tự: **văn bản lỗi** của một
   spawn thất bại, và **câu trả lời cuối** của subagent (hiện làm ghi chú trên thẻ) *khi payload `SubagentStop` có
   trường `last_assistant_message`*. Bản Claude Code đã kiểm (2026-10-11) **không gửi trường này**, nên ở đó thẻ
   không có ghi chú và hook không nhận câu trả lời nào để lưu. **Không lưu**: prompt, câu trả lời đầy đủ, tham số
   công cụ, đường dẫn transcript. Văn bản lỗi và câu trả lời có thể trích đường dẫn hay chuỗi nhạy cảm, nên nếu bạn
   không muốn lưu chúng thì đặt `OFFICE_EVENTS_NOTES=0` (bỏ cả hai đoạn). Tắt hẳn hook: `OFFICE_EVENTS_DISABLE=1`.
2. **Ghi sổ ngân sách** cho yêu cầu đang làm, như CLAUDE.md đã yêu cầu:
   `python3 scripts/route.py --dimensions ... --signals ... --record --requirement <id>`.
3. **Chạy server** (`python3 scripts/office/serve.py`) và mở trang. Hook nằm trong cấu hình
   của phiên Claude Code, nên phải khởi động lại phiên sau khi sửa `settings.json`.
4. **Pipeline VPS:** chạy server trên máy có thư mục làm việc của team.py
   (`--team-home /srv/team` hoặc `$TEAM_HOME`). Chỉ đọc `state.json` và vài file kề bên
   (`gates.log`, `verdict.md`...), không chạy git trong bản clone của worker.

## Mỗi con số lấy từ đâu

| Trên trang | Nguồn | Ghi chú |
|---|---|---|
| Trạng thái từng agent | `spawn_request`, `start`, `stop`, `spawn_result` của hook | Một lượt không có sự kiện nào quá 15 phút, hoặc một yêu cầu spawn 2 phút vẫn chưa chạy (bị `agent_budget.py` từ chối, hay bạn từ chối), hiện là **bị chặn / im lặng**, không phải "đang làm" mãi. Lượt `start` ghép với yêu cầu **mới nhất** cùng loại; yêu cầu bị một yêu cầu hay lượt chạy mới hơn của cùng agent vượt mặt (thường là lượt bị từ chối rồi thử lại) bị coi là bỏ ngay và không bao giờ xếp trên lượt mới. Hai agent cùng loại chạy song song có thể tạm lệch việc cho đến khi kết quả của chúng về, và kết quả sẽ sửa lại cho đúng |
| Tiến độ từng agent | số lần gọi công cụ của agent ÷ `maxTurns` trong `.claude/agents/*.md` | **Ước lượng**, hiện dấu `~`, tối đa 95% cho đến khi agent báo xong. Một lượt có thể gọi nhiều công cụ nên con số có thể quá mức |
| Tiến độ chung | số vai route dự kiến đã xong ÷ số vai dự kiến | Vai dự kiến = `required_agents` + vai có dự phòng cấp lúc phân loại |
| Ngân sách | `agent-budget.json`, dựng lại **đến thời điểm đang xem** | Cơ sở và từng dự phòng báo riêng; dự phòng chưa cấp vẽ nét đứt |
| Giai đoạn của main session | suy ra từ vai nào chạy gần nhất | **Không quan sát trực tiếp**, trang có ghi chú nói rõ |
| Làn pipeline | `state.json` của team.py: `stage`, `next`, model từng role, `warnings` | team.py chưa ghi số lượt thử của coder nên chưa có thanh "lượt 2/3". Feature mới tạo (`stage: spec`) hiện **chờ bạn viết spec**, chưa phải đang chạy |
| Gates | `gates.log`: dòng `RESULT` cuối | Gates đỏ hiện **bị chặn**, thanh là số lệnh nghiệm thu đang qua |

Xem lại: kéo thanh thời gian để về bất kỳ lúc nào trong lượt chạy; bộ dựng snapshot
nhận `at=<epoch>` và bỏ qua mọi sự kiện sau đó, nên cùng một mã phục vụ cả live lẫn
replay. "Về trực tiếp" quay lại hiện tại.

## Kiểm tra payload của hook trên bản Claude Code bạn đang dùng

Tên trường (`agent_id`, `agent_type`, `tool_response.agentId`, `totalToolUseCount`...) lấy
từ tài liệu hook chính thức. Chúng đã được kiểm trên một lượt chạy thật (2026-10-11, một
subagent `Explore`): đủ `spawn_request`, `start`, `tool`, `stop` và `spawn_result` với
`agent_id`, `status`, `totalTokens`, `totalDurationMs`, `totalToolUseCount`. Ngoại lệ:
`SubagentStop` không có `last_assistant_message` (xem trên). Đó là một bản Claude Code và một
loại agent; khi đổi bản Claude Code, kiểm lại bằng:

```bash
OFFICE_EVENTS_SHAPE=1 claude          # ghi tên khóa và kiểu giá trị, không ghi giá trị
cat artifacts/handoff/office-shapes.jsonl
```

Nếu trường nào lệch, sửa một chỗ duy nhất: `scripts/hooks/office_events.py`. Reducer chịu được
trường thiếu (agent hiện không có tiến độ thay vì sai).

## An toàn

- Server chỉ trả lời `GET`/`HEAD`, không ghi gì, không chạy gì từ dữ liệu nó đọc.
- Mặc định bind `127.0.0.1`; bind ra ngoài cần `--allow-remote`. Địa chỉ literal được phân tích; tên máy được phân giải **một lần** và chỉ chấp nhận khi **mọi** địa chỉ đều là loopback (tên bắt đầu bằng `127.` không đủ), rồi server bind đúng địa chỉ số đã kiểm chứ không bind lại theo tên. Địa chỉ IPv6 (`--host ::1`) dùng socket IPv6, và host loopback bạn bind (`127.1.2.3`, `::1`, tên máy) được nhận trong `Host` đúng dạng trình duyệt gửi (`::ffff:127.0.0.1` thành `[::ffff:7f00:1]`) để URL in ra mở được. Với `--allow-remote`, tên máy cũng được đổi thành địa chỉ số của nó trước khi bind, nên tên chỉ có bản ghi AAAA vẫn dùng socket IPv6; URL in ra giữ zone id của địa chỉ IPv6 (`[fe80::1%25eth0]`). Trang không có đăng nhập và
  dữ liệu có thể trích mô tả tác vụ, nên trên VPS hãy vào bằng SSH tunnel:
  `ssh -L 8765:127.0.0.1:8765 host`.
- Từ chối `Host` lạ (chống DNS rebinding), chỉ phục vụ file nằm trong `office/dist`, kèm CSP cùng nguồn.
- Không đọc `workers.env` hay khóa API nào.

## Phát triển

```bash
cd office
npm ci
npm run dev            # Vite, proxy /api về 127.0.0.1:8765 (chạy serve.py song song)
npm run typecheck && npm run lint && npm run build
```

Thành phần giao diện chép từ [Automation UI Kit](https://github.com/vohoailinh90/Automation-UI-Kit)
(`THIRD_PARTY_NOTICES.md` đi kèm); robot vẽ riêng bằng SVG. Thêm agent mới vào
`scripts/office/roster.json`, rồi thêm `roster.<id>.role` vào ba file `office/src/locales/*.json`
(`tests/test_office_ui.py` báo nếu thiếu).

## Kiểm chứng

| Việc | Lệnh |
|---|---|
| Hook, reducer, server, catalog, hình học đường nối | `python3 -m unittest tests.test_office_events tests.test_office_snapshot tests.test_office_serve tests.test_office_ui` |
| Test có thật sự bắt lỗi | `python3 scripts/mutation_check.py tests/mutations/office_{events,snapshot,serve}.yaml` |
| Hợp đồng snapshot | `python3 scripts/office/snapshot.py --check` |
| Ba catalog đủ khóa, đủ placeholder | `python3 scripts/i18n_check.py office/src/locales --require ja,en,vi` |
| Trang biên dịch được | `cd office && npm run typecheck && npm run build` |

CI chạy các bước này (trừ ảnh chụp trình duyệt: runner có thể không có trình duyệt).

## Giới hạn đã biết

- Chỉ-đọc: giao hay hủy việc từ trang là một yêu cầu khác (nó ghi vào pipeline).
- Văn bản của chạy mẫu (mô tả tác vụ, ghi chú) là tiếng Việt và không dịch theo ngôn ngữ giao
  diện vì là dữ liệu; nhãn, trạng thái và hướng dẫn thì dịch.
- Bản dịch tiếng Nhật do Claude viết, chưa có người Nhật xem. Các thuật ngữ cần xác nhận:
  サブエージェント, 予備枠 (reserve), エスカレーション, ゲート.

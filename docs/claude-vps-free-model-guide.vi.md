# Hướng dẫn Claude kiến trúc + AI miễn phí coding trên VPS

> Cập nhật 11/10/2026. Tài liệu cho tool-marketing-studio, dựa trên [claude-agent-routing-template](https://github.com/vohoailinh90/claude-agent-routing-template) và [hướng dẫn VPS gốc](https://github.com/vohoailinh90/claude-agent-routing-template/blob/main/docs/vps-team.md). **Chưa triển khai/kiểm chứng trên VPS của người dùng**. Quota, ID model, giá và điều khoản thay đổi thường xuyên.

## 1. Hiểu đúng kiến trúc

Có **hai loại routing độc lập**:

- Routing mức rủi ro trong repo này: CLAUDE.md, agent-routing/policy.yaml, scripts/route.py chấm 6 chiều để phân loại T0–T3. Lane Codex Cloud là lựa chọn riêng, không phải VPS free-model.
- Routing thực thi ở repo template: scripts/team/team.py là bộ điều phối bằng code, gọi OpenCode + API model trong container. Claude Code chính chủ thiết kế **đầu quy trình** và kiểm toán **cuối quy trình**. Không chia sẻ phiên đăng nhập Claude Pro cho OpenCode, Hermes hoặc worker.

~~~text
Bạn -> request.md
  -> Claude Code: spec.md + tasks.md + acceptance.md
  -> team check-spec
  -> team run:
       Tester   (model A) viết test -> red gate phải fail
       Coder    (model B) viết code -> gates phải pass; <=3 attempts
       Reviewer (model C khác họ) đọc repo -> prereview.md
       Conductor tạo audit-pack.md (diff, logs, rủi ro)
  -> Claude Code: verdict.md (APPROVE / BLOCK)
       BLOCK: tối đa 1 vòng sửa và audit bổ sung
       APPROVE: team push -> tạo GitHub PR -> CI -> kiểm tra -> merge
~~~

VPS 4 vCPU/8 GB RAM không cần GPU: **VPS chạy Docker và orchestration, model chạy trên API nhà cung cấp**. Free inference không đồng nghĩa free VPS, free thời gian, hay bảo đảm uptime. Không dùng model 70B+ tự host trên VPS 8 GB.

## 2. Kết nối từ máy của bạn vào VPS (SSH)

Cần IP/DNS VPS, user Linux có sudo, khóa SSH. Trong terminal máy cá nhân (Windows PowerShell/macOS/Linux):

~~~bash
ssh-keygen -t ed25519 -C "marketing-studio-vps"
# Thêm public key (.pub) vào VPS qua panel nhà cung cấp hoặc authorized_keys
ssh -i ~/.ssh/id_ed25519 ubuntu@YOUR_VPS_IP
~~~

Nếu đã có key, **không ghi đè key hiện tại**; dùng đúng tên file key mới và đường dẫn Windows nếu khác. Trên VPS:

~~~bash
whoami
free -h
df -h
sudo apt-get update
sudo apt-get install -y git curl ca-certificates python3 python3-venv
~~~

Bảo mật SSH: mở port 22/TCP (ưu tiên giới hạn theo IP) ở cloud firewall, xác minh **phiên SSH thứ hai** đăng nhập bằng key được rồi mới tắt password/root login. Nếu dùng UFW, allow OpenSSH trước khi enable. Không mở Docker daemon, cổng runner hoặc team ra Internet. VPN/Tailscale là tùy chọn tăng bảo mật.

**Bốn kết nối khác nhau:** (1) SSH: máy bạn -> VPS; (2) deploy key: VPS user team -> GitHub repo; (3) API key: container -> model provider; (4) GitHub self-hosted runner: GitHub Actions -> VPS. Không kết nối nào tự tạo ba kết nối còn lại.

## 3. Cài team conductor từ repo template

Repo template là **private**. Cần GitHub SSH credential đọc được repo cho user admin trên VPS; clone HTTPS không xác thực có thể trả 404.

~~~bash
git clone git@github.com:vohoailinh90/claude-agent-routing-template.git
cd claude-agent-routing-template
# Đọc script trước khi chạy với sudo
sudo ./scripts/team/setup-vps-team.sh --admin "$USER"
# Nếu thật sự muốn Telegram, thêm --with-hermes
# Đăng xuất và SSH lại để nhận group team
command -v team
team status
team doctor
~~~

Script tạo user team, /srv/team, /opt/team, Docker image, mạng team-net, luật egress và có thể tạo swap. **Docker group tương đương đặc quyền root**: không cài vào VPS có workload nhạy cảm mà chưa review script, network/firewall, quyền user và runner CI. Hermes tùy chọn, không cần để pipeline chạy bằng SSH.

Claude Code chỉ đăng nhập dưới user admin bằng cách chính chủ hỗ trợ. Không đưa ANTHROPIC_API_KEY, cookie hay token phiên Claude Pro cho worker; gói Claude Pro không phải API key.

## 4. Lấy API key và chọn provider

| Nguồn | Lấy key | Vai trò nên thử | Cảnh báo |
|---|---|---|---|
| [OpenRouter](https://openrouter.ai/) | Keys, đặt credit cap nhỏ | Nhiều model :free, fallback | Free pool/429/quota thay đổi; [limits](https://openrouter.ai/docs/api_reference/limits) |
| [Google AI Studio](https://aistudio.google.com/) | API key của project riêng | Gemini Flash/Flash-Lite | [Free tier có thể dùng dữ liệu để cải thiện sản phẩm](https://ai.google.dev/gemini-api/docs/pricing) |
| [Mistral](https://console.mistral.ai/) | Experiment/free nếu được cấp | Tester/coder | Xác minh model cụ thể và điều khoản |
| [Groq](https://console.groq.com/) | API key | Fallback tác vụ ngắn | Quota theo model |
| [NVIDIA Build](https://build.nvidia.com/) | Trial key nếu đủ điều kiện | Fallback cuối | Trial có thể hết hạn, rate limit |
| [DeepSeek](https://platform.deepseek.com/) | Key có billing | Paid fallback | Chỉ bật sau khi chấp thuận chi phí |

Đặt key trên VPS bằng editor, không dán vào PR/chat/log:

~~~bash
sudo -u team nano /srv/team/workers.env
# OPENROUTER_API_KEY=...
# GOOGLE_GENERATIVE_AI_API_KEY=...
# MISTRAL_API_KEY=...
sudo stat -c '%U %a %n' /srv/team/workers.env
# kỳ vọng: team 600 /srv/team/workers.env
~~~

Mỗi worker chỉ được cấp key provider tương ứng nhưng **code model tạo ra vẫn có thể gửi key ra Internet**. Dùng key riêng có giới hạn chi tiêu thấp và rotate định kỳ. Repo private/đang thương mại hóa: **không gửi code tới endpoint free chưa xác nhận chính sách không huấn luyện/lưu trữ**; chọn API có điều khoản phù hợp hoặc repo thử nghiệm không chứa bí mật.

## 5. Tìm model đang miễn phí THỰC SỰ

Chạy trên VPS sau khi cấu hình key:

~~~bash
team models openrouter --free
team models google
team models mistral
team models groq
team models nvidia
team doctor --ping
~~~

Chỉ lấy **model ID chính xác** được trả về; OpenCode dùng định dạng provider/model. Lệnh doctor kiểm tra kết nối/cấu hình, **không phải benchmark coding**. Model có thể tồn tại trên provider nhưng chưa có trong catalog OpenCode. Nếu 429/403/404, xem log, quota, vùng địa lý, quyền key và đổi provider; đừng tạo nhiều account để né giới hạn.

Các **họ ứng viên để khảo sát** (không khẳng định hiện có bản free): Qwen Coder, GLM, Devstral, Nemotron, Gemini Flash, Mistral code-capable. Không cố định model từ bài blog; hãy so sánh theo [scorecard và benchmark](free-model-benchmark.md). Tester, coder, reviewer dùng **ba họ khác nhau** để giảm lỗi cùng nguồn.

## 6. Cấu hình vai trò, thứ tự ưu tiên và fallback

Sửa /srv/team/team.env. Đây là **ví dụ placeholder**, phải thay bằng model ID đã kiểm tra từ lệnh team models:

~~~ini
TEAM_MODELS_TESTER="mistral/<TESTER_ID> google/<FLASH_LITE_ID>"
TEAM_MODELS_CODER="openrouter/<VENDOR>/<MODEL_ID>:free google/<FLASH_ID>"
TEAM_MODELS_REVIEWER="google/<FLASH_ID> mistral/<REVIEWER_ID>"
TEAM_CODER_ATTEMPTS=3
TEAM_WORKER_MEMORY=3g
TEAM_WORKER_CPUS=2
TEAM_WORKER_TIMEOUT=1800
TEAM_GATES_NETWORK=none
TEAM_PACK_MAX_LINES=1500
~~~

Model đầu tiên mỗi vai là primary, tiếp theo là fallback. Không tự thêm hậu tố :free cho model/provider không hỗ trợ. Nếu hết quota thì ưu tiên model free ở provider **khác**, sau đó mới cân nhắc paid theo ngân sách.

Gates cho tool-marketing-studio cần dependencies:

~~~ini
TEAM_GATES_SETUP="python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt && .venv/bin/python -m playwright install chromium"
~~~

Các lệnh nghiệm thu tối thiểu trong acceptance.md:

~~~bash
.venv/bin/python -m pytest -q
.venv/bin/python studio.py check
.venv/bin/python scripts/i18n_check.py
.venv/bin/python scripts/layout_check.py
.venv/bin/python scripts/mutation_check.py --all
~~~

Nếu sửa web/src, bổ sung build web: cd web && npm ci && npm run build; kiểm tra web/dist được cập nhật. Gates chạy checkout sạch và không có mạng mặc định; bước setup dependency có thể cần mạng. Không đưa file .env của app (Facebook token, Anthropic key) vào worker.

## 7. Chạy feature mẫu và đẩy PR

Cấp **deploy key riêng** cho user team vào Settings -> Deploy keys của tool-marketing-studio; bật write access nếu cần team push, bật bảo vệ main. Nếu một deploy key đã gắn repo khác, cần key riêng + SSH host alias hoặc cơ chế credential phù hợp (đọc hướng dẫn gốc).

~~~bash
team new MKT-001 --repo git@github.com:vohoailinh90/tool-marketing-studio.git
nano /srv/team/work/MKT-001/request.md
cd /srv/team/work/MKT-001
claude
# dán kết quả: team prompt claude-spec MKT-001
# Claude viết spec.md, tasks.md, acceptance.md; sau đó thoát
team check-spec MKT-001
team run MKT-001 --detach
team status MKT-001
tail -f /srv/team/work/MKT-001/out/run.log
~~~

Audit lần 2:

~~~bash
cd /srv/team/work/MKT-001
claude
# dán kết quả: team prompt claude-audit MKT-001
# Claude ghi verdict.md, dòng VERDICT: APPROVE hoặc VERDICT: BLOCK
~~~

BLOCK: team run MKT-001 --from verdict --detach, sau đó audit lại (tối đa một vòng bổ sung). APPROVE: team push MKT-001; **tự tạo PR** từ nhánh team/MKT-001; chờ CI và review findings trước khi merge. team push không tự tạo PR/merge. Nếu phát hiện secrets, tests bị sửa yếu đi, CI thay đổi hoặc dependency lockfile bất thường: chặn merge.

## 8. CI runner và xử lý sự cố

CI runner self-hosted **khác** Docker AI worker. Tài khoản GitHub cá nhân cần runner đăng ký riêng cho từng repo; tool-marketing-studio dùng biến CI_RUNNER và runner của chính nó (xem docs/agent-team.md). Runner chung VPS cạnh tranh CPU/RAM với worker; không chạy workflow PR từ fork không tin cậy trên runner có quyền truy cập host. Đừng cho runner user giữ API keys.

- team doctor báo model bị rút: chạy team models, sửa team.env, doctor --ping.
- 429/quota: tôn trọng Retry-After, chuyển fallback khác provider hoặc chờ reset; không retry vô hạn.
- Gates fail: đọc out/gates.log, sửa code/test, không xóa test chỉ để xanh.
- SSH timeout: kiểm tra IP, security group, port 22, sshd và public key qua console provider.
- Docker network fail: kiểm tra team-net và team-egress.service; không bỏ firewall để sửa nhanh.
- Claude BLOCK: chỉ một vòng audit bổ sung; nếu vẫn BLOCK thì xử lý thủ công.

## 9. Quy tắc tiết kiệm tiền

**Chi Claude ở hai đầu, không chi cho thao tác lặp**: Claude viết spec đủ cụ thể (file, ràng buộc, test, rollback) và đọc một audit pack đã nén; tester/coder/reviewer chạy API free hoặc giá thấp. Tính **USD / feature hoàn thành**, không chỉ USD / triệu token; model free 429 liên tục có thể tốn thời gian hơn paid Flash. Đặt hard cap ở provider, giới hạn retry và chia feature nhỏ. Dùng [bảng benchmark](free-model-benchmark.md) để thay model theo số liệu.

**Trạng thái:** đây là tài liệu và lệnh tham khảo dựa trên code repo; chưa có bằng chứng kết nối VPS thực tế, key hợp lệ, pipeline end-to-end hoặc benchmark thực nghiệm trên máy của bạn.

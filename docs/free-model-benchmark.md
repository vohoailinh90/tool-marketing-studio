# Benchmark model AI miễn phí/giá rẻ cho coding — mẫu đo thực nghiệm

> Không có model nào được tuyên bố là “miễn phí tốt nhất” trước khi chạy thử. Bảng này là mẫu thu thập dữ liệu, **không phải kết quả benchmark đã đo**. Cập nhật ngày 11/10/2026.

## 1. Preflight: model có dùng được không?

Chạy `team models openrouter --free`, `team models google`, `team models mistral`, `team doctor --ping`. Ghi **model ID chính xác**, provider, thời điểm, vùng, loại key, quota theo console, dữ liệu có được dùng để training không, model có trong OpenCode catalog không, hỗ trợ tool calling và edit file không.

Nếu bất kỳ điều nào không rõ: trạng thái **UNKNOWN**, không gắn nhãn FREE hoặc PRIVATE-SAFE. Free-tier có thể thay đổi bất ngờ; không dùng tên model hay hạn mức trong blog làm source of truth.

## 2. Bộ bài thử cho tool-marketing-studio

Mỗi model chạy **cùng spec, cùng base SHA, cùng giới hạn thời gian/tokens, không xem output của model khác**, lặp tối thiểu 3 lần/task nếu quota cho phép:

| Task | Độ khó | Mục tiêu |
|---|---|---|
| A — typo/validation message | T0–T1 | Sửa đúng 1–2 file, không thay đổi hành vi |
| B — thêm unit test cho mkt module | T1 | Test fail trước fix, pass sau fix, không sửa source khi làm tester |
| C — fix bug ở mkt/ + regression test | T2 | Không phá contract, chạy pytest và mutation check |
| D — thay đổi nhỏ FastAPI + UI | T2 | Backend + web build, không sửa secret hay lockfile ngoài phạm vi |
| E — cố tình đưa regression/security pitfall | Review | Reviewer phát hiện bug có thật, chỉ rõ file/line và cách tái hiện |

Không chạy các task tác động thật đến Facebook publishing, payment, secret hay production trên worker miễn phí. Đặt fake token/fixtures.

## 3. Cách ghi số liệu

| Provider/model ID | Vai | Free tại thời điểm? | Training/logging phù hợp? | Tool call OK? | Pass/attempts | Phút/task | Tokens in/out | USD/task | Finding thật/giả |
|---|---|---|---|---|---|---|---|---|---|
| Chưa thử | tester | UNKNOWN | UNKNOWN | UNKNOWN | — | — | — | — | — |
| Chưa thử | coder | UNKNOWN | UNKNOWN | UNKNOWN | — | — | — | — | — |
| Chưa thử | reviewer | UNKNOWN | UNKNOWN | UNKNOWN | — | — | — | — | — |

Các gates đo trên **clean checkout**, không cho model tự chấm. Ghi 429/timeout/403/404, số lần fallback, diff size, số file ngoài scope, số lỗi phát sinh, retry và chi phí thực tế. Tách **model/provider**, **task**, **run ID**, **commit SHA** để có thể tái hiện.

## 4. Công thức chọn model

Chỉ chấm model qua preflight:

- **40%**: acceptance gates pass + regression không phát sinh, tính theo số run thành công / tổng run.
- **20%**: đúng phạm vi, không sửa test yếu đi, không thay đổi file cấm.
- **15%**: độ ổn định API (1 - tỉ lệ lỗi 429/timeout/provider), tính trong cửa sổ thử nghiệm.
- **15%**: thời gian thực hiện đến PASS, bao gồm retry/fallback.
- **10%**: chi phí **USD / task PASS** (tổng API spend kể cả các lần fail / số task PASS).

**Hard stop**: vi phạm chính sách dữ liệu, không hỗ trợ tool, sửa secret, sửa ngoài scope nghiêm trọng hoặc thiếu logs -> loại ngay, bất kể điểm. Không đánh đồng model reviewer với coder: reviewer chấm bằng precision/recall trên lỗi đã biết, không bằng số dòng code.

Giá model free có thể bằng 0 USD nhưng tính cả VPS, thời gian khắc phục lỗi và thời gian Claude audit khi ra quyết định tổng thể. Nếu free quá nhiều lỗi, so sánh với một model paid giá thấp có cap.

## 5. Quy tắc routing đề xuất

- T0: main session xử lý, không khởi động VPS chỉ để sửa typo.
- T1: dùng VPS khi có nhiều task lặp và acceptance rõ; nếu không, xử lý trực tiếp có review độc lập theo policy.
- T2: Claude viết spec, VPS tester/coder/reviewer, Claude audit. Ưu tiên model đã PASS benchmark cùng loại task.
- T3 / security / auth / payment / migrations: không tự động giao thiết kế, triển khai hay merge cho model free; cần con người và review bảo mật phù hợp. Routing tier gốc vẫn là source of truth.

Không thay `agent-routing/policy.yaml` theo các quy tắc gợi ý này nếu chưa thiết kế và kiểm thử riêng. Đây là chính sách **lựa chọn lane vận hành**, không phải thay đổi cách chấm tier.

## 6. Cách thử nhỏ an toàn

1. Tạo repo sandbox không chứa code thương mại, secret, dữ liệu cá nhân.
2. Chọn 3 họ model độc lập, xác nhận quota và điều khoản.
3. Dùng `team new BENCH-001 --repo <sandbox SSH URL>`, cho Claude viết spec/task/acceptance.
4. `team check-spec BENCH-001` rồi `team run BENCH-001 --detach`; ghi logs và commit.
5. Claude audit; nếu PASS, ghi lại kết quả và mới cân nhắc cho repo private.
6. Chạy lại khi provider/model thay đổi hoặc mỗi tháng; đừng giữ kết quả cũ là sự thật hiện tại.

Tài liệu cài đặt: [claude-vps-free-model-guide.vi.md](claude-vps-free-model-guide.vi.md).

# Đề xuất: Meeting Scheduler cho nhóm 10+ người ở nhiều quốc gia

**Đối tượng**: repo `vohoailinh90/Email_Bridge` (`src/meetingscheduler.py`, `meeting_scheduler_standalone/`).
**Trạng thái**: đề xuất thiết kế, chưa viết code. Mọi con số dưới đây đo ngày 2026-10-11 bằng chính
`find_best_slot()` của repo trên lịch **giả lập** (không phải dữ liệu thật của ai).
**Chuyển thành pipeline**: sao nội dung này vào `docs/agents/pipeline/2026-1x-<tên>.md` của Email_Bridge và điền ba dòng
Nhỏ nhất / An toàn / Rollback (mục 7).

## 1. Vấn đề

Với nhóm 10+ người ở nhiều múi giờ, "một khung mà **tất cả** đều rảnh trong giờ làm" thường không tồn tại. Đo thực tế:

| Nhóm (mọi người 09:00-18:00 T2-T6, lịch trống hoàn toàn) | Khung chung 60 phút | 90 phút |
|---|---|---|
| Tokyo + Prague, mùa đông (CET) | **1 lần/ngày** (17:00 JST = 09:00 CET) | **0** |
| Tokyo + Prague, mùa hè (CEST) | 3 lần/ngày | 2 lần/ngày |
| + Hồ Chí Minh | như trên (cửa sổ HCM chứa trọn khung chung) | như trên |
| + Los Angeles hoặc New York | **không có** | **không có** |

Một nhóm 10 người, mỗi người còn lịch bận riêng, thì khung chung hẹp ấy thường đã bị ai đó chiếm. Thuật toán không chậm
(30 người x 60 ngày ≈ 0,3 giây), nên **tối ưu tốc độ không phải việc cần làm**; thứ thiếu là cách xử lý khi không có khung hoàn hảo.

## 2. Hiện trạng (đọc từ code)

- `find_best_slot()` chỉ có hai kết cục: `best` (100% người đọc được lịch đều rảnh) hoặc `fallback` (tối đa 5 khung xếp theo
  `(-số người rảnh, sớm nhất)`).
- Giờ làm việc là **nhị phân**: một lát nằm ngoài `work_start..work_end`, hoặc rơi T7/CN theo giờ địa phương, là "không rảnh".
- Không có: ngày lễ, giờ nghỉ trưa, người bắt buộc/tuỳ chọn, điểm "mức khó chịu", công bằng giữa các lần họp.
- Người không đọc được lịch (`unresolved`) bị loại khỏi mẫu số, chỉ liệt kê riêng.
- Giao diện chỉ hiện giờ **JST**; ô múi giờ chỉ có Asia/Tokyo, Europe/Prague, UTC, offset tuỳ ý.
- Ví dụ lỗ hổng đo được (Tokyo + Prague + LA): gợi ý #1 = Tokyo 17:00 + Prague 09:00 và LA lúc **00:00**; gợi ý #2, #3 để Prague
  lúc **01:00/02:00**. Giao diện chỉ hiện nhãn đỏ "không rảnh" - không ai thấy người vắng đang ở giữa đêm.

## 3. Đề xuất theo phase (mỗi phase độc lập, revert được)

### P0 - Trung thực hơn, không đổi thuật toán
1. Mỗi thẻ khung giờ hiện **giờ địa phương của từng người** (thêm `local_start/local_end` theo `tz` đã khai) cạnh nhãn rảnh/bận.
2. Nhãn người không rảnh ghi **lý do**: `busy` (lịch bận) hay `out_of_hours` (ngoài giờ làm) - dữ liệu đã có sẵn trong `_member_available`.
3. Dòng cảnh báo cố định khi có `unresolved`: "Khung này **bỏ qua N người** chưa đọc được lịch: ...".
4. Khi `best` rỗng, hiện **chẩn đoán cửa sổ chung** ("Với các múi giờ này, giờ làm việc chồng nhau 0 giờ/ngày. Hãy nới giờ hoặc tách buổi.").

### P1 - Điểm thay cho nhị phân (lõi của đề xuất)
1. Mỗi member thêm tuỳ chọn (đều có mặc định = hành vi hiện tại): `role: required|optional`, `core: 09:00-18:00`,
   `stretch: 07:00-09:00 & 18:00-21:00` (chấp nhận được nhưng bị phạt), `lunch: 12:00-13:00`, `holidays: [ngày...]`, `weekend: [5,6]`.
2. `find_best_slot(..., scoring=...)` tính cho mỗi khung: `required_ok` (mọi người bắt buộc rảnh), `optional_count`,
   `pain = tổng điểm phạt (stretch=1, đêm=cấm)`, rồi xếp theo `(required_ok, -optional_count, pain, sớm nhất)`.
3. Trả thêm `pain_by_member` để UI chỉ rõ **ai chịu giờ xấu**. Khoá trả về cũ (`best`, `fallback`, `available_members`...) giữ nguyên.
4. Không đặt hệ số phức tạp: 3 mức (core=0, stretch=1, cấm). Tham số hoá sau khi có phản hồi dùng thật.

### P2 - Tự điền múi giờ và giờ làm từ Graph (cần spike)
- Đáp án `getSchedule` có trường `workingHours` (ngày, giờ, múi giờ) cho từng người - **cần kiểm trên tenant thật** trước khi dựa vào
  (bài học của repo: giả định chưa thử thật thường sai). Nếu đúng: điền sẵn `tz/work_start/work_end`, người dùng vẫn sửa được.
- Kiểm xem ký tự `availabilityView` '1' (tentative) và '4' (workingElsewhere) nên là "phạt nhẹ" thay vì "bận" như hiện nay.

### P3 - Tách buổi khi nhóm trải ba châu lục
Lập luận số học: Tokyo (UTC+9) và LA (UTC-8) lệch 17 giờ; ngay cả giờ nới 07:00-21:00 cũng không có khung nào chung cho cả
Tokyo + Prague + LA. Khi `required_ok` rỗng, đề xuất **hai buổi** sao cho mỗi người bắt buộc dự ít nhất một buổi với `pain` nhỏ nhất
(chọn tham lam, thuần Python), hoặc **lịch luân phiên** (tuần này giờ thuận cho châu Á, tuần sau cho châu Mỹ). Chỉ gợi ý, vẫn mở bản nháp Outlook cho người dùng tự gửi.

## 4. Ràng buộc kiến trúc (giữ nguyên)

Thêm tham số tuỳ chọn, không đổi chữ ký bắt buộc; thuật toán vẫn thuần Python (test được trên CI không cần Outlook/Graph);
không thêm dependency; không ghi DB; endpoint chỉ **thêm** trường vào JSON; `.Send(` vẫn không tồn tại; server vẫn chỉ `127.0.0.1`.
Dữ liệu ngày lễ: **không gọi API ngoài** - dùng danh sách người dùng nhập, hoặc bảng tĩnh nhỏ trong repo (JP, CZ, VN) do chủ repo cập nhật hằng năm
(đây là điểm cần chủ repo quyết, mục 6).

## 5. Tiêu chí nghiệm thu (đo được)

1. Test cố định bốn kịch bản ở mục 1; kết quả `best/fallback` đúng theo bảng.
2. Tokyo + Prague + LA với `required` = Tokyo, Prague và `optional` = LA: khung đầu **không** đặt Prague sau 21:00 local (cấm).
3. Cùng đầu vào, `pain_by_member` khác 0 chỉ với người ở giờ stretch; người ở giờ core luôn bằng 0.
4. Hồi quy: mọi test hiện có của `test_meeting_scheduler.py` pass **không sửa**; `grep -rn "\.Send("` rỗng; `import meetingscheduler` chạy không cần pywin32.
5. Benchmark: 30 người x 60 ngày vẫn dưới 2 giây (hiện 0,3 giây).

## 6. Câu hỏi cần chủ repo quyết

1. Ngày lễ: bảng tĩnh trong repo (tốn công cập nhật) hay người dùng tự nhập ngày nghỉ?
2. Giờ "stretch" mặc định là bao nhiêu và có cho phép buổi họp lúc 07:00 hay 20:00 không?
3. Có chấp nhận P3 (tách buổi) làm tính năng riêng, hay chỉ dừng ở P0-P1?
4. Người ngoài tổ chức (không đọc được lịch): cho nhập tay "rảnh giờ nào" (v1 đã loại) hay giữ cảnh báo?

## 7. Ba dòng bắt buộc theo quy trình Email_Bridge

- **Nhỏ nhất**: P0 + P1 trong cùng module; loại hướng "dựng dịch vụ xếp lịch riêng" và "gọi API ngày lễ".
- **An toàn**: không chạm 5 vùng escalation (không auto-send, không API/credential mới - P2 dùng lại đáp án `getSchedule` sẵn có, không mở cổng, không thay đổi không đảo ngược).
- **Rollback**: `git revert`; mọi tham số mới có mặc định giống hành vi cũ nên dữ liệu cũ không cần migrate.

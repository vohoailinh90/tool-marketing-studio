# Đề xuất: Meeting Scheduler cho nhóm 10+ người ở nhiều quốc gia

**Đối tượng**: repo `vohoailinh90/Email_Bridge` (`src/meetingscheduler.py`, `meeting_scheduler_standalone/`).
**Trạng thái**: đề xuất thiết kế, chưa viết code. Số đo ngày 2026-10-11 chạy bằng chính `find_best_slot()` của repo trên lịch
**giả lập** (không phải dữ liệu thật của ai). Ví dụ dùng Việt Nam, Ấn Độ, Hàn Quốc (+ Đức, Mỹ để thấy khi mở rộng).
**Chuyển thành pipeline**: sao vào `docs/agents/pipeline/` của Email_Bridge, điền ba dòng Nhỏ nhất / An toàn / Rollback (mục 7).

## 1. Vấn đề

Hai chuyện khác nhau, cần tách bạch:

**(a) Giờ làm việc chồng nhau ít hay nhiều?** Mọi người 09:00-18:00 T2-T6, lịch trống hoàn toàn:

| Nhóm | Khung 60 phút / tuần | Khung 90 phút / tuần |
|---|---|---|
| Việt Nam + Ấn Độ + Hàn Quốc (không nước nào có giờ mùa hè) | 50 (5,5 giờ/ngày) | 45 |
| + 1 người ở Đức, mùa đông / mùa hè | 5 / 15 | 0 / 10 |
| + 1 người ở New York hoặc Los Angeles | 0 | 0 |

Khung chung của ba nước châu Á là 10:30-16:00 giờ Việt Nam, tức 09:00-14:30 ở Ấn Độ và 12:30-18:00 ở Hàn Quốc.

**(b) Nhóm đông, và quản lý kín họp, thì khung chung còn lại bao nhiêu?** Mô phỏng một tuần, họp ngẫu nhiên 30-90 phút, người thường
bận 30% giờ làm, "quản lý" **giả định** bận 60%, 2000 lần chạy. Xác suất có ít nhất một khung 60 phút mà **tất cả** cùng rảnh:

| Nhóm 10 người | Không có quản lý | 1 quản lý | 2 quản lý |
|---|---|---|---|
| Cùng một nước, cùng một bộ phận (cùng giờ làm) | 28% | 15% | 7% |
| Ba nước Việt Nam, Ấn Độ, Hàn Quốc | 14% | - | 3% |

Nhóm 5 người cùng một nước: 100% khi không có quản lý, 89% khi có 1 quản lý. Chạy thô hơn (300 lần mỗi ô, người chia đều ba nước) cho thấy
số người tăng thì khung chung sụp rất nhanh: ở mức bận 20/30/40%, nhóm 3 người 100/100/98%, nhóm 10 người 73/12/2%, nhóm 15 người 23/1/0%.

Lưu ý: giả định họp độc lập, không nghỉ trưa, không ngày lễ, và "quản lý bận hơn" là giả định chứ chưa đo trên lịch thật; lịch thật dồn cục
hơn nên chỉ dùng để minh hoạ xu hướng. Quan trọng nhất: **ngay cả khi không có múi giờ nào để đổ lỗi, chỉ riêng việc người này họp khung này,
người kia họp khung khác đã đủ làm khung chung gần như biến mất.**

Thuật toán không chậm (30 người x 60 ngày ≈ 0,3 giây), nên **tối ưu tốc độ không phải việc cần làm**; thiếu là cách xử lý khi
không có khung hoàn hảo, và sự trung thực về những người tool không đọc được lịch.

## 2. Hiện trạng (đọc từ code và tài liệu)

- `find_best_slot()` chỉ có hai kết cục: `best` (100% người đọc được lịch đều rảnh) hoặc `fallback` (tối đa 5 khung, xếp theo
  `(-số người rảnh, sớm nhất)`).
- Giờ làm là **nhị phân**: lát nằm ngoài `work_start..work_end` hoặc rơi T7/CN theo giờ địa phương là "không rảnh".
  Không có: ngày lễ, nghỉ trưa, người bắt buộc/tuỳ chọn, điểm "mức khó chịu", công bằng giữa các lần họp.
- **Chỉ đọc được lịch của người mà Graph cho người đăng nhập xem, thực tế là cùng tổ chức Microsoft 365.** Thiết kế ghi người
  "không cùng tổ chức, không publish" là `unresolved` (quyết định 6, rủi ro R1) và lần kiểm chứng thật chỉ gồm đồng nghiệp cùng tổ chức.
  Tập đoàn có nhiều tenant thì đồng nghiệp ở tenant khác cũng có thể thành "không rõ". Việc hai tổ chức chia sẻ free/busy có đọc được
  hay không **chưa kiểm chứng** (tài liệu Microsoft tra được không nêu rõ).
- Không phân biệt người bận nhiều (thường là quản lý) với người bận ít; không cho biết ai là người chặn nhiều khung nhất.
- Người `unresolved` bị loại khỏi mẫu số, chỉ liệt kê riêng: khung "tốt nhất" có thể bỏ qua cả một nhóm người mà không ai để ý.
- Giao diện chỉ hiện giờ **JST**; ô múi giờ chỉ có vài lựa chọn sẵn và offset tuỳ ý.
- Lỗ hổng đo được (Việt Nam + Ấn Độ + Hàn Quốc + New York): ba gợi ý đầu đều là giờ làm việc của ba nước châu Á, còn người ở New York
  lúc **22:30, 23:30 và 00:30** (Chủ nhật/đầu thứ Hai). Giao diện chỉ hiện nhãn đỏ "không rảnh", không ai thấy người đó đang ở giữa đêm.

## 3. Đề xuất theo phase (mỗi phase độc lập, revert được)

### P0 - Trung thực hơn, không đổi thuật toán
1. Mỗi thẻ khung giờ hiện **giờ địa phương của từng người** (`local_start/local_end` theo `tz` đã khai) cạnh nhãn rảnh/bận.
2. Nhãn người không rảnh ghi **lý do**: `busy` hay `out_of_hours` (dữ liệu đã có trong `_member_available`).
3. Cảnh báo cố định khi có `unresolved`: "Khung này **bỏ qua N người** chưa đọc được lịch: ... (chỉ đọc được người cùng tổ chức)".
4. Khi `best` rỗng, hiện **chẩn đoán**: số giờ chồng nhau mỗi ngày theo giờ làm đã khai, và ai là người kéo cửa sổ co lại.
5. **Thống kê người chặn**: đếm, trên các khung ứng viên, mỗi người là người bận duy nhất bao nhiêu lần (thường là quản lý kín họp) và liệt kê
   các khung "chỉ cần 1 người dời họp" kèm tên người đó, để chủ cuộc họp biết nên xin ai nhường. Thuần Python từ chuỗi free/busy đã có, không cần chủ đề cuộc họp.

### P1 - Điểm thay cho nhị phân (lõi của đề xuất)
1. Mỗi member thêm tuỳ chọn (mặc định = hành vi hiện tại): `role: required|optional`, `core: 09:00-18:00`,
   `stretch: 07:00-09:00 & 18:00-21:00` (chấp nhận nhưng bị phạt), `lunch`, `holidays`, `weekend`.
2. `find_best_slot(..., scoring=...)` xếp theo `(required_ok, -optional_count, pain, sớm nhất)`; `pain` = tổng điểm phạt
   (core=0, stretch=1, đêm=cấm).
3. Trả thêm `pain_by_member` để UI chỉ rõ **ai chịu giờ xấu**. Khoá trả về cũ (`best`, `fallback`, `available_members`...) giữ nguyên.
4. Không dùng hệ số phức tạp: 3 mức, chỉnh sau khi có phản hồi dùng thật.

### P2 - Tự điền múi giờ và giờ làm từ Graph (cần spike)
- Đáp án `getSchedule` có trường `workingHours` (ngày, giờ, múi giờ) cho từng người - **cần kiểm trên tenant thật** trước khi dựa vào.
  Nếu đúng: điền sẵn `tz/work_start/work_end`, người dùng vẫn sửa được.
- Kiểm xem ký tự `availabilityView` '1' (tentative) và '4' (workingElsewhere) nên là "phạt nhẹ" thay vì "bận" như hiện nay.

### P3 - Nhập tay cho người không đọc được, và tách buổi
- **Nhập tay "rảnh giờ nào" cho người `unresolved`** (v1 đã loại; nhu cầu giờ rõ hơn vì nhóm đa quốc gia hay có khách/đối tác): ô
  chọn giờ rảnh, tính cùng thuật toán, gắn nhãn "tự khai, chưa kiểm chứng".
- Khi `required_ok` rỗng (ví dụ nhóm châu Á + Mỹ), đề xuất **hai buổi** để mỗi người bắt buộc dự ít nhất một buổi với `pain` nhỏ nhất
  (chọn tham lam, thuần Python) hoặc **lịch luân phiên**. Chỉ gợi ý, vẫn mở bản nháp Outlook cho người dùng tự gửi.

## 4. Ràng buộc kiến trúc (giữ nguyên)

Thêm tham số tuỳ chọn, không đổi chữ ký bắt buộc; thuật toán thuần Python (test được trên CI không cần Outlook/Graph); không thêm
dependency; không ghi DB; endpoint chỉ **thêm** trường vào JSON; `.Send(` vẫn không tồn tại; server vẫn chỉ `127.0.0.1`.
Ngày lễ: **không gọi API ngoài** - người dùng nhập ngày nghỉ, hoặc bảng tĩnh nhỏ trong repo do chủ repo cập nhật hằng năm.

## 5. Tiêu chí nghiệm thu (đo được)

1. Test cố định các kịch bản ở mục 1(a); kết quả `best/fallback` đúng bảng.
2. Việt Nam + Ấn Độ + Hàn Quốc (`required`) + New York (`optional`): khung đầu **không** đặt người New York trong giờ bị cấm (đêm).
3. Khung gần đúng có đúng một người bận được xếp hạng riêng và nêu tên người đó; thống kê người chặn đúng trên dữ liệu giả lập có một người bận dày.
4. `pain_by_member` khác 0 chỉ với người ở giờ stretch; người ở giờ core luôn bằng 0.
5. Hồi quy: mọi test hiện có của `test_meeting_scheduler.py` pass **không sửa**; `grep -rn "\.Send("` rỗng; `import meetingscheduler` chạy không cần pywin32.
6. Benchmark: 30 người x 60 ngày vẫn dưới 2 giây (hiện 0,3 giây).

## 6. Câu hỏi cần chủ repo quyết

1. Ngày lễ: bảng tĩnh trong repo hay người dùng tự nhập ngày nghỉ?
2. Giờ "stretch" mặc định là bao nhiêu, có cho buổi họp 07:00 hay 20:00 không?
3. Có làm P3 (nhập tay + tách buổi), hay dừng ở P0-P1?
4. Tập đoàn của bạn dùng một hay nhiều tenant Microsoft 365? Nếu nhiều, cần spike xem free/busy giữa các tenant có đọc được không.

## 7. Ba dòng bắt buộc theo quy trình Email_Bridge

- **Nhỏ nhất**: P0 + P1 trong cùng module; loại hướng "dựng dịch vụ xếp lịch riêng" và "gọi API ngày lễ".
- **An toàn**: không chạm 5 vùng escalation (không auto-send, không API/credential mới - P2 dùng lại đáp án `getSchedule` sẵn có, không mở cổng, không thay đổi không đảo ngược).
- **Rollback**: `git revert`; mọi tham số mới có mặc định giống hành vi cũ nên không cần migrate.

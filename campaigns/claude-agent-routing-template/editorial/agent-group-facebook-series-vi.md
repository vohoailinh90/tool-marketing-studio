# Series Facebook: Group Agent — Claude thiết kế, AI khác kiểm tra và coding

> Bản thảo tiếng Việt, sẵn để biên tập và đăng **thủ công**. Kế hoạch gợi ý từ thứ Hai 12/10 đến Chủ nhật 18/10/2026 (giờ Nhật); **chưa lên lịch/đăng tự động**. Nội dung này **chưa** phải các post YAML đã duyệt của engine; không sửa các bài Nhật/Anh hiện tại. Trước khi xuất ảnh bằng studio, chuyển từng bài sang cấu trúc campaign và kiểm tra brief/claim. Không gắn link repo private, không quảng cáo có mã nguồn public.

## Quy tắc nội dung

- Gọi đây là **quy trình và thiết kế đang thử nghiệm**, không nói hệ thống VPS đã vận hành end-to-end hay đã tiết kiệm được X%.
- **Phân biệt ba lựa chọn**: (A) Claude chính + Claude subagents; (B) Claude chính + Codex Cloud qua GitHub để phản biện theo cách tác giả chọn; (C) Claude chính làm kiến trúc/audit + worker AI miễn phí/giá rẻ trên VPS làm test/code/pre-review. B và C **không phải một lane mặc định duy nhất**; codex lane được định nghĩa trong policy gốc còn có thể cho Codex design/implement.
- Mỗi bài độc lập, câu đầu có hook, chỉ một ý chính, ví dụ gần gũi, một câu hỏi để tạo thảo luận; tránh dồn 8 tên agent/6 chiều chấm điểm vào cùng một ảnh.
- Không gọi API miễn phí là không giới hạn. Không hứa dữ liệu repo private được giữ bí mật bởi mọi provider.
- Nguồn kỹ thuật: `CLAUDE.md`, `docs/agent-team.md`, `docs/claude-to-codex.md`, `docs/claude-vps-free-model-guide.vi.md`, và repo template `docs/vps-team.md`. Các hình là sơ đồ khái niệm, không phải ảnh chụp pipeline đã chạy.

## Lịch đăng gợi ý (chưa đặt lịch thực)

| Ngày (JST) | Bài | Mục tiêu | Hình gợi ý |
|---|---|---|---|
| Thứ Hai 12/10 | #1 — Vì sao cần group agent? | Khơi vấn đề tự viết tự duyệt | Cover + so sánh |
| Thứ Tư 14/10 | #2 — Ai làm gì? | Giải thích Claude / Codex / VPS worker | Sơ đồ 3 đường |
| Thứ Sáu 16/10 | #3 — VPS + model miễn phí | Giải thích kỹ thuật dễ hiểu | Flow 6 bước |
| Chủ nhật 18/10 | #4 — Chọn model & kiểm soát tiền | Bài thực hành, thu câu hỏi | Scorecard + checklist |

Không khẳng định 20:00–21:30 là giờ tối ưu nếu chưa có analytics; thử và so sánh tương tác.

---

## Bài #1 — AI viết code rồi tự chấm: có nên tin?

**Caption Facebook (copy để đăng):**

Mình từng nghĩ: cứ giao việc cho một AI, nó viết code, chạy test rồi báo “Done” là xong.

Nhưng có một câu hỏi khá khó chịu: **người viết cũng là người duyệt, vậy ai tìm ra điểm mù của người viết?** 🤔

Mình đang xây một cách làm gọi nôm na là **group agent**: không phải càng nhiều AI càng tốt, mà là **mỗi vai có trách nhiệm rõ ràng**.

Ví dụ một thay đổi nhỏ như sửa câu chữ thì không cần gọi cả đội. Nhưng khi sửa luồng đăng bài, xử lý dữ liệu hay thay đổi quyền truy cập, mình muốn có thiết kế, người phản biện và bằng chứng kiểm thử.

Nguyên tắc mình dùng:
- Claude hoặc agent chính hiểu yêu cầu và xác định thế nào là “xong”.
- Một vai độc lập tìm lỗi trong thiết kế hoặc code, không chỉ khen “ổn”.
- Test, diff và CI là bằng chứng; lời AI tự nhận đã kiểm tra chưa đủ.
- Có giới hạn số vòng phản biện để không tốn thời gian vô tận.

Đây là **quy trình mình đang xây và hoàn thiện**, không phải công thức bảo đảm code hết bug.

**Nếu dùng AI viết tool cho công việc, bạn thường kiểm tra code của AI bằng cách nào?**

#AIcoding #Claude #Codex #Automation #GroupAgent

**Ảnh carousel (3 slide):** 1) “AI viết code xong, ai bắt lỗi?”; 2) “Một AI tự duyệt vs nhiều vai có nhiệm vụ”; 3) “Thiết kế → code → kiểm chứng → mới gọi là xong”.

---

## Bài #2 — Claude, Codex, AI worker: đừng nhầm 3 vai

**Caption Facebook (copy để đăng):**

Một nhóm AI không nhất thiết là 5–10 con bot cùng nhảy vào viết code.

Mình chia công việc thành **3 nhóm vai**:

🧠 **Kiến trúc sư:** hiểu yêu cầu, chọn cách thiết kế, giới hạn file được sửa và viết tiêu chí nghiệm thu. Đây là phần mình muốn Claude phụ trách.

🔎 **Người phản biện:** đọc thiết kế hoặc pull request và chỉ ra vấn đề có bằng chứng. Với cách làm Claude + Codex của mình, Codex được gọi qua comment trên GitHub để phản biện, không tự sửa code theo cảm tính.

🛠️ **Người thực thi:** viết test và code theo spec. Ở phương án tiết kiệm chi phí, các model AI miễn phí hoặc giá rẻ có thể làm phần này qua API, dưới sự điều phối của một script trên VPS.

Quan trọng: đây là **những cấu hình khác nhau**, không phải mọi vai đều chạy cùng lúc. Repo routing còn phân loại yêu cầu từ T0 đến T3 để tránh dùng quá nhiều agent cho việc nhỏ.

Ví dụ muốn thêm nút “Xuất báo cáo”:
1. Claude xác định nút làm gì, xuất định dạng nào, lỗi thì hiển thị gì.
2. Worker viết test rồi viết code theo đúng phạm vi.
3. Reviewer xem diff, tìm các trường hợp bị bỏ sót.
4. Claude đối chiếu test và kết quả trước khi đồng ý.

**Bạn muốn AI giỏi nhất tập trung vào thiết kế hay trực tiếp viết từng dòng code?**

#AgentTeam #Claude #Codex #AICoding #SoftwareDevelopment

**Ảnh carousel (3 slide):** 1) “Đội AI không cần đông”; 2) “Claude = thiết kế / Codex = phản biện / worker = test & code (tùy cấu hình)”; 3) “Task nhỏ → ít agent; task rủi ro → nhiều kiểm chứng”.

---

## Bài #3 — VPS 8 GB RAM có điều phối được cả nhóm AI không?

**Caption Facebook (copy để đăng):**

Nghe “AI team chạy trên VPS” có vẻ cần máy chủ GPU rất mạnh. Nhưng không nhất thiết.

Trong kiến trúc mình đang thử nghiệm, **VPS không chạy trực tiếp model lớn**. Nó chạy script điều phối và các Docker container. Các worker gọi model qua API của OpenRouter, Google AI Studio, Mistral hoặc nhà cung cấp phù hợp.

Một vòng dự kiến như sau:

① Mình mô tả tính năng cần làm.

② Claude viết spec, danh sách task và điều kiện nghiệm thu.

③ AI Tester tạo test để kiểm tra hành vi mong muốn.

④ AI Coder sửa code theo spec, chạy lại các bài test.

⑤ AI Reviewer độc lập đọc diff, chỉ ra lỗi có bằng chứng.

⑥ Claude đọc bản tổng hợp thay đổi và log test, quyết định cho qua hay yêu cầu sửa.

Cuối cùng mới đến GitHub PR, CI và bước merge khi đủ điều kiện.

Điều hay là mình **không cần dùng model đắt tiền cho mọi lần sửa lỗi lặp lại**. Nhưng vẫn có chi phí VPS, quota API, thời gian xử lý và rủi ro model free bị 429 hoặc ngừng cung cấp.

Lưu ý quan trọng: repo đang ở giai đoạn chuẩn bị và tài liệu hóa; mình **chưa công bố kết quả chạy end-to-end hay mức tiết kiệm thực tế**.

**Nếu triển khai một nhóm AI như vậy, bạn lo nhất chi phí, chất lượng code hay bảo mật?**

#VPS #Docker #AIAgent #Claude #OpenRouter

**Ảnh carousel (4 slide):** 1) “VPS không cần GPU để điều phối AI”; 2) “VPS = nhạc trưởng, model = API bên ngoài”; 3) “Tester → Coder → Reviewer → Claude audit”; 4) “Bảo mật key, quota và PR trước khi merge”.

---

## Bài #4 — Model miễn phí nào đáng giao việc coding?

**Caption Facebook (copy để đăng):**

Một model được quảng cáo là “free” chưa chắc đã là model rẻ nhất để làm việc.

Ví dụ: Model A gọi API 0 đồng nhưng thường xuyên lỗi 429, phải thử lại 3 lần. Model B có phí nhỏ nhưng làm xong một lần. Nếu tính thời gian chờ, công sửa và công review, lựa chọn tốt nhất có thể đảo ngược.

Vì vậy, thay vì hỏi “model nào đứng đầu bảng xếp hạng?”, mình muốn hỏi: **model nào hoàn thành được task thật với ít chi phí nhất?**

Mình định so sánh trên cùng một bộ bài:
- Sửa một lỗi nhỏ và không động tới file khác.
- Viết regression test trước khi sửa bug.
- Sửa code và chạy lại toàn bộ kiểm thử.
- Review một PR có lỗi được cài sẵn.

Mỗi lần đo sẽ ghi: model/provider, tỉ lệ PASS, số lần retry, lỗi 429, thời gian, số token, chi phí thực và lỗi reviewer phát hiện đúng/sai.

Một điều phải nói rõ: **free API không mặc nhiên phù hợp với repo private**. Cần đọc chính sách lưu dữ liệu/huấn luyện của provider, dùng API key riêng có hạn mức thấp, không đưa secret vào prompt.

Mục tiêu của mình không phải thay Claude bằng model rẻ bằng mọi giá, mà là **để Claude tập trung vào quyết định khó, còn phần lặp lại có test thì giao cho worker phù hợp**.

**Bạn đã dùng model AI miễn phí nào để code ổn định? Có model nào thường xuyên lỗi quota không?**

#AICoding #FreeAI #Claude #OpenRouter #DeveloperTools

**Ảnh carousel (3 slide):** 1) “FREE ≠ rẻ nhất”; 2) “So sánh: PASS / retry / thời gian / USD mỗi task thành công”; 3) “Bảo mật dữ liệu trước, giá rẻ sau”.

---

## Checklist trước khi đăng

- [ ] Đọc lại lời xưng “mình” và xác nhận đó là trải nghiệm/thử nghiệm của tác giả, không phải số liệu bịa.
- [ ] Không viết rằng hệ thống VPS đã chạy ổn định nếu chưa có log thực tế.
- [ ] Không công bố URL private, deploy key, API key, IP VPS, token Facebook.
- [ ] Render và kiểm tra chữ trên ảnh mobile; tránh quá nhiều chữ trên một slide.
- [ ] Duyệt caption và từng slide theo phiên bản chính xác trước khi đăng.
- [ ] Sau mỗi bài, lưu câu hỏi/comment thực tế để điều chỉnh bài tiếp theo.

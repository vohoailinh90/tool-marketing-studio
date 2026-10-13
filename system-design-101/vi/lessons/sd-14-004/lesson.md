# Thiết kế hệ thống phân quyền

**Mọi hệ thống phân quyền trả lời cùng một câu hỏi, “ai được làm gì với cái gì”, nhưng mỗi mô hình dựa vào một thứ khác để quyết định.**
Chọn mô hình nào thì quyết định bạn phải bảo trì thứ gì về sau.

![Bảy thẻ xếp dọc. Thẻ đầu là yêu cầu chung: Lan muốn đọc tệp bảng lương. Năm thẻ tiếp theo là năm mô hình, mỗi mô hình hỏi một câu khác. ACL: trên tệp có dòng cho phép Lan không. DAC: chủ sở hữu tệp đã cho Lan chưa. MAC: nhãn của Lan có đủ mức so với nhãn của tệp không, chủ sở hữu không tự đổi được. RBAC: Lan có vai trò nào được đọc tệp. ABAC: thuộc tính của Lan, tệp, hành động và hoàn cảnh có khớp luật không. Thẻ cuối nêu cái phải bảo trì: ACL ghi từng người là mỗi người nhân mỗi tài liệu, RBAC là gán vai trò, ABAC là thuộc tính và luật.](../../diagrams/sd-14-004-main.svg)

## Đọc hình

Năm tên này không loại trừ nhau. ACL nói về cách lưu quyền (một danh sách gắn với tài nguyên); DAC, MAC, RBAC và ABAC nói về ai quyết định và dựa vào đâu. Hệ thống thật hay xếp chồng nhiều lớp: trên Linux có SELinux, kiểm tra DAC chạy trước rồi mới hỏi chính sách MAC; Kubernetes cho chạy nối tiếp nhiều bộ phân quyền, ví dụ RBAC rồi ABAC, và yêu cầu nào một trong hai cho phép thì được phép. Vì vậy chọn DAC hay RBAC không có nghĩa là bỏ ACL; bài chỉ xếp chúng cạnh nhau để so cách nghĩ.

**ACL (danh sách kiểm soát truy cập).** Mỗi tài nguyên mang một danh sách ghi ai được làm gì. Hệ thống chỉ việc tra danh sách của tệp bảng lương xem có dòng cho Lan không.

**DAC (kiểm soát truy cập tùy quyền chủ sở hữu).** Chủ sở hữu tài nguyên tự quyết định chia quyền cho ai. Hệ thống tệp Linux là ví dụ. Khi chạy thử, một người dùng tạo tệp với quyền `rw-------` thì người dùng khác bị từ chối đọc; chính chủ tệp đổi sang `rw-r--r--` bằng `chmod` thì người kia đọc được.

**MAC (kiểm soát truy cập bắt buộc).** Cả người dùng (hay tiến trình) lẫn tài nguyên đều mang nhãn, và một chính sách trung tâm so các nhãn với nhau. Chủ sở hữu không tự nới được.
Với nhãn theo mức, quy tắc quen thuộc là không đọc lên và không ghi xuống.

**RBAC (kiểm soát truy cập theo vai trò).** Quyền gắn vào vai trò, người dùng được gán vai trò. Lan đọc được vì Lan có vai trò “kế toán” và vai trò đó được phép đọc.

**ABAC (kiểm soát truy cập theo thuộc tính).** Luật là điều kiện trên các thuộc tính, ví dụ “phòng ban của người dùng trùng phòng ban của tài liệu thì được đọc”.

## Giới hạn cần nhớ

Không có cách nào miễn phí: mỗi cách chuyển công việc bảo trì sang một chỗ khác. Trong ví dụ chạy thử có hai tài liệu và một kế toán mới vào làm:
ACL ghi từng người cần thêm hai dòng (một dòng cho mỗi tài liệu), RBAC cần một dòng gán vai trò, ABAC không cần thêm dòng chính sách nào.
ACL có thể ghi nhóm thay vì từng người; khi đó chỉ cần thêm người mới vào nhóm một lần, và cách làm đó đã tiến gần RBAC. Con số trên là của ACL ghi từng người, không phải của mọi ACL.
ABAC thì chỉ đúng khi thuộc tính của người và của tài liệu được giữ đúng, và luật càng phức tạp càng khó đọc, khó kiểm tra.

## Nhìn hình trả lời

Công ty có rất nhiều tài liệu và một kế toán mới vào làm. Với ACL, RBAC và ABAC, người quản trị phải sửa gì để người này đọc được các tài liệu kế toán?

<details>
<summary>Xem đáp án</summary>

ACL ghi từng người: thêm một dòng cho từng tài liệu người này cần đọc, nên số dòng tăng theo số tài liệu (ACL ghi nhóm thì chỉ cần thêm người vào nhóm). RBAC: gán vai trò kế toán, vai trò đã có sẵn các quyền đọc. ABAC: không sửa luật, chỉ cần hồ sơ người dùng ghi đúng phòng ban Tài chính, vì luật so phòng ban của người với phòng ban của tài liệu.
Cái giá của ABAC nằm ở chỗ khác: nếu thuộc tính ghi sai thì quyền sai theo.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn viết DAC “dựa trên ACL”. Ví dụ Linux ở đây chạy bằng bit quyền chủ, nhóm, khác (`rw-------`, `rw-r--r--`), không cần ACL, nên bài này không gắn DAC với ACL. Khi chạy thử, một tệp `rw-r-----` thuộc nhóm `daemon` đọc được với người trong nhóm đó, còn người chưa vào nhóm bị từ chối cho tới khi được thêm vào nhóm một lần; đó cũng là lý do ACL ghi nhóm rẻ hơn ACL ghi từng người.
Bài nguồn gọi ABAC là “ít được dùng” và ghi nhãn của MAC trên “chủ sở hữu và tài nguyên”; bài này không lặp lại hai nhận định đó vì chưa kiểm được: tài liệu SELinux mô tả nhãn trên cả chủ thể (người dùng, tiến trình) lẫn đối tượng.
Bài nguồn xếp năm mô hình ngang hàng; bài này giữ cách xếp đó để so sánh nhưng nêu thêm chỗ chồng lấn giữa cơ chế lưu quyền và chính sách. Định nghĩa ACL và RBAC của NIST, vốn nói rõ hơn về chỗ chồng lấn này, chưa đối chiếu được vì trang NIST không truy cập được.
Kubernetes là một ví dụ thực của RBAC, và quyền ở đó chỉ cộng thêm, không có luật “từ chối”. Đó là đặc điểm của Kubernetes, không phải của mọi hệ RBAC.

Kết quả minh họa chạy bằng Python (thư viện Casbin cho ACL, RBAC, ABAC; luật mức bảo mật viết tay) và bằng hai người dùng Linux thật. Danh sách thuộc tính của ABAC theo định nghĩa của NIST chưa đối chiếu được vì trang NIST không truy cập được từ môi trường soạn bài.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-design-a-permission-system.md): năm mô hình ACL, DAC, MAC, ABAC, RBAC.
- [SELinux Notebook — Mandatory Access Control](https://github.com/SELinuxProject/selinux-notebook/blob/main/src/mac.md): MAC dùng thuộc tính bảo mật trên chủ thể và đối tượng, người dùng không tự bỏ qua chính sách, DAC cho người dùng tự quyết, quy tắc không đọc lên và không ghi xuống. Đọc từ bản clone của kho.
- [Kubernetes — Using RBAC Authorization](https://github.com/kubernetes/website/blob/main/content/en/docs/reference/access-authn-authz/rbac.md): RBAC theo vai trò; quyền chỉ cộng thêm. Đọc từ nguồn trên GitHub.
- [Kubernetes — Using ABAC Authorization](https://github.com/kubernetes/website/blob/main/content/en/docs/reference/access-authn-authz/abac.md): ABAC cấp quyền qua chính sách kết hợp các thuộc tính. Đọc từ nguồn trên GitHub.

Đã đọc nguồn ngày 2026-10-13. Ví dụ ACL, RBAC và ABAC chạy bằng Casbin 1.43.0 trên Python; ví dụ DAC chạy bằng lệnh `chmod` của hai người dùng Linux; luật mức bảo mật là mã Python viết tay theo quy tắc trong tài liệu SELinux. Bài viết và hình được thiết kế độc lập.

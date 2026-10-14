# Các tình huống dùng bộ cân bằng tải

**Một máy chủ không chịu nổi mọi người dùng, và một máy chủ lỗi không nên làm cả dịch vụ ngừng.** Bộ cân bằng tải (*load balancer*, LB) đứng trước một nhóm máy chủ để giải quyết cả hai. Bài sd-01-002 xem ví dụ cấu hình cụ thể; bài này nhìn sáu lý do người ta dùng LB.

![Sáu khung dọc: phân phối tải chia request cho nhiều máy theo một thuật toán; sẵn sàng cao loại máy lỗi khỏi nhóm và bản thân LB cũng cần dự phòng; kết thúc TLS giải mã tại LB và chặng sau có thể mã hóa lại; giữ phiên đưa cùng người dùng về cùng máy nhưng tải dễ bị lệch; mở rộng ngang thêm máy khi tải tăng và ứng dụng nên ít giữ trạng thái; theo dõi sức khỏe kiểm tra định kỳ từng máy, kiểm tra quá sâu dễ loại nhầm.](../../diagrams/sd-01-011-main.svg)

## Đọc hình

**1. Phân phối tải.** LB nhận request rồi chia cho các máy. "Chia đều" không tự có: *vòng tròn* chia theo lượt, *ít kết nối nhất* ưu tiên máy đang rảnh, *băm* chọn máy theo một khóa. Các request tốn công không như nhau, nên chọn thuật toán hợp với tải thật.

**2. Sẵn sàng cao.** Máy lỗi bị loại khỏi nhóm, request mới đi tới máy còn khỏe. Nhưng nếu chỉ có một LB thì chính nó là điểm đơn lỗi, nên cần dự phòng.

**3. Kết thúc TLS.** LB giải mã HTTPS, các máy sau nhận lưu lượng đã giải mã, và chứng chỉ hướng tới người dùng được quản lý tập trung ở LB. Khi cần bảo vệ cả chặng nội bộ, LB mã hóa lại trước khi chuyển đi; khi đó chặng sau LB cần thêm chứng chỉ và cấu hình tin cậy riêng.

**4. Giữ phiên.** Cùng một người dùng được đưa về cùng một máy, thường qua cookie hoặc băm địa chỉ. Đổi lại, tải dễ lệch, và nếu trạng thái phiên chỉ nằm trên máy đó thì phiên mất khi máy chết.

**5. Mở rộng ngang.** Tải tăng thì thêm máy vào nhóm. Cách này chạy tốt khi ứng dụng ít giữ trạng thái trên từng máy.

**6. Theo dõi sức khỏe.** LB kiểm tra từng máy định kỳ, hoặc quan sát lỗi thật, để biết máy nào còn dùng được.

## Giới hạn cần nhớ

LB không tự làm hệ thống mở rộng được: nếu cơ sở dữ liệu là nút cổ chai, thêm máy web không giúp. Kiểm tra sức khỏe quá sâu (như gọi cả cơ sở dữ liệu) có thể khiến mọi máy bị coi là lỗi cùng lúc khi cơ sở dữ liệu chậm. Và LB hoạt động ở tầng kết nối (nhanh, không đọc nội dung) hoặc tầng HTTP (đọc được đường dẫn, header, tốn công hơn) với khả năng khác nhau.

## Nhìn hình thử trả lời

Sau khi thêm máy thứ ba sau LB chia theo vòng tròn, thỉnh thoảng người dùng bị đăng xuất. Nguyên nhân thường gặp và hướng sửa?

<details>
<summary>Xem đáp án</summary>

Phiên đăng nhập đang lưu trong bộ nhớ riêng của từng máy, nên request kế tiếp rơi vào máy khác không biết phiên đó. Hướng sửa chính: lưu phiên ở nơi dùng chung hoặc dùng token phía client. Giữ phiên ở LB chỉ là giải pháp tạm vì có nhược điểm ở mục 4.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Thăm dò chủ động và thụ động:** LB có thể gửi request kiểm tra riêng, hoặc coi lỗi của request thật là dấu hiệu máy có vấn đề.
- **Gỡ máy nhẹ nhàng:** khi gỡ một máy khỏi nhóm, LB thường ngừng gửi request mới tới máy đó rồi chờ các request đang chạy hoàn thành (draining), thường trong một thời hạn tối đa.
- **Chọn tầng:** tầng kết nối hợp khi chỉ cần chuyển lưu lượng nhanh; tầng HTTP hợp khi cần định tuyến theo đường dẫn, host hoặc header.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/key-use-cases-for-load-balancers.md).
- [AWS — Elastic Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html): chia tải, kiểm tra sức khỏe, kết thúc TLS, giữ phiên.
- [NGINX — HTTP load balancing](https://nginx.org/en/docs/http/load_balancing.html): thuật toán chia tải, kiểm tra sức khỏe, giữ phiên.
- [HAProxy — tài liệu](https://docs.haproxy.org/): cân bằng tải tầng kết nối và tầng HTTP, kiểm tra sức khỏe.

Đã đọc nguồn ngày 2026-10-13; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

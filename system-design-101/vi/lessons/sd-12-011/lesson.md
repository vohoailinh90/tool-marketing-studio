# Kiến trúc nền tảng thử nghiệm A/B

**Thử nghiệm A/B hỏi người dùng thật bằng hành vi, không bằng ý kiến.** Một nền tảng thử nghiệm biến việc đó thành quy trình lặp lại được: định nghĩa, phân nhóm, ghi nhận, phân tích.

![Bốn thẻ dọc: định nghĩa và quản lý thử nghiệm qua giao diện, cấu hình được lưu lại; triển khai bằng cách gán người dùng vào nhóm và trả tham số theo nhóm ở cả máy chủ và máy khách; ghi nhận các sự kiện ai thấy gì và làm gì; phân tích so sánh các nhóm. Chú thích: gán nhóm phải ổn định, cùng người thì cùng nhóm.](../../diagrams/sd-12-011-main.svg)

## Đọc hình

**1. Định nghĩa và quản lý.** Người làm sản phẩm tạo thử nghiệm trên giao diện: giả thuyết, nhóm đối chứng và nhóm thử, tỷ lệ người dùng, chỉ số cần đo. Cấu hình được lưu để các phần sau đọc.

**2. Triển khai.** Khi người dùng vào, hệ thống gán họ vào một nhóm và trả về tham số của nhóm đó, ở máy chủ hoặc máy khách. Một cách phổ biến: băm (mã thử nghiệm, mã người dùng), lấy phần dư theo 100; 0–49 là đối chứng, 50–99 là nhóm thử. Cùng một người luôn rơi vào cùng một nhóm mà không cần lưu danh sách.

**3. Ghi nhận.** Ghi lại ai đã thấy biến thể nào và họ làm gì sau đó.

**4. Phân tích.** So sánh các nhóm, ước lượng khác biệt cùng độ tin cậy.

## Giới hạn cần nhớ

Kết quả chỉ đáng tin nếu ghi nhận đúng và đủ. Chỉ tính người dùng vào thử nghiệm khi họ thực sự thấy biến thể. Nếu tỷ lệ người thực tế ở hai nhóm lệch khỏi tỷ lệ đã định (sample ratio mismatch), hãy nghi ngờ lỗi ở bước gán hoặc ghi nhận trước khi đọc kết quả. Xem số liệu giữa chừng rồi dừng khi thấy “thắng” làm tăng nguy cơ kết luận sai.

## Nhìn hình trả lời

Người dùng X đăng nhập trên điện thoại rồi trên máy tính. Nếu gán nhóm bằng số ngẫu nhiên mỗi lần truy cập thì có vấn đề gì?

<details>
<summary>Xem đáp án</summary>

X có thể thấy biến thể khác nhau ở các lần, làm số liệu lẫn lộn và trải nghiệm không nhất quán. Gán theo băm mã người dùng giữ X ở cùng một nhóm, miễn là hai thiết bị cùng nhận diện được X.

</details>

<details>
<summary>Xem sâu hơn: đơn vị ngẫu nhiên hóa và chỉ số bảo vệ</summary>

- **Đơn vị ngẫu nhiên hóa:** người dùng, thiết bị hay phiên. Chọn đơn vị quyết định việc một người có thấy cùng biến thể xuyên thiết bị hay không.
- **Chỉ số bảo vệ (guardrail):** theo dõi cả những điều không muốn xấu đi như tốc độ trang, lỗi hoặc tỷ lệ hủy dịch vụ, không chỉ chỉ số mục tiêu.
- **Máy chủ và máy khách:** máy khách cần nhận cấu hình nhóm và phải có cách xử lý khi chưa tải được.
- Bố cục bốn thành phần này được vẽ lại từ cuốn *Trustworthy Online Controlled Experiments* của Kohavi, Tang và Xu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/possible-experiment-platform-architecture.md): bốn thành phần của nền tảng thử nghiệm, theo cuốn sách được nguồn nhắc tới.
- [Trustworthy Online Controlled Experiments](https://experimentguide.com/): sách tham khảo về thử nghiệm trực tuyến.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-011.json).

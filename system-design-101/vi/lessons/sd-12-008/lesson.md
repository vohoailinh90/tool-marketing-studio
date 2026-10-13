# Thiết kế hệ thống đa ngôn ngữ

**Quốc tế hóa không chỉ là dịch chữ.** Số, ngày giờ, tiền tệ, độ dài câu và cả quy định kế toán đều khác theo nơi người dùng sống. Thiết kế tốt tách phần “đổi theo vùng” ra khỏi logic chung.

![Sáu thẻ dọc cho sáu khía cạnh: ngôn ngữ, với chữ nằm ngoài mã nguồn và dùng câu hoàn chỉnh; bố cục, chừa chỗ cho chữ dài và xuống dòng; múi giờ, lưu UTC và hiển thị giờ địa phương; tiền tệ, tiền hiển thị khác tiền thanh toán; định dạng số, ngày, địa chỉ theo vùng; pháp lý và kế toán theo từng nước.](../../diagrams/sd-12-008-main.svg)

## Đọc hình

**Ngôn ngữ.** Chữ giao diện nằm trong kho riêng, truy cập theo khóa, không viết thẳng vào mã. Không ghép câu từ nhiều mảnh: thứ tự từ và dạng số ít, số nhiều đổi theo ngôn ngữ, nên dùng câu hoàn chỉnh có tham số. Chữ trong ảnh không dịch được, hãy tách chữ ra khỏi ảnh.

**Bố cục.** Cùng một nút, bản dịch có thể dài gấp đôi bản gốc; chừa chỗ, cho phép xuống dòng, giữ nhãn nút ngắn.

**Múi giờ.** Lưu thời điểm theo UTC; chuyển sang giờ địa phương chỉ khi hiển thị.

**Tiền tệ.** Tách tiền hiển thị với tiền thanh toán; cần dịch vụ quy đổi tỷ giá để báo giá.

**Định dạng.** Số, ngày và địa chỉ có thứ tự khác nhau: `1.234,5` ở nơi này là `1,234.5` ở nơi khác.

**Pháp lý và kế toán.** Mỗi nước có thể cần pháp nhân, chuẩn kế toán và quy tắc riêng.

## Giới hạn cần nhớ

Dịch xong chưa phải là xong. Ngôn ngữ viết từ phải sang trái (như tiếng Ả Rập) cần bố cục phản chiếu; sắp xếp tên, quy tắc số nhiều và cách gọi người dùng cũng khác. Hãy kiểm thử bằng dữ liệu của chính các vùng đó, đừng chỉ dựa vào bản tiếng Anh.

## Nhìn hình trả lời

Máy chủ cần lưu giờ đặt hàng của khách ở nhiều nước. Nên lưu giờ địa phương của khách hay lưu UTC? Vì sao?

<details>
<summary>Xem đáp án</summary>

Lưu UTC và chuyển sang giờ địa phương khi hiển thị. Giờ địa phương chỉ là một cách nhìn; lưu UTC tránh nhầm giữa nhiều múi giờ và khi nơi nào đó đổi giờ mùa hè.

</details>

<details>
<summary>Xem sâu hơn: câu có tham số, tiền và dữ liệu vùng</summary>

- **Câu có tham số và số nhiều:** thay vì ghép “Bạn có ” + n + “ tin nhắn”, dùng một mẫu câu trọn vẹn cho từng ngôn ngữ, có quy tắc số nhiều riêng. Thư viện theo ICU MessageFormat làm việc này.
- **Tiền tệ:** mã tiền theo ISO 4217 và số chữ số thập phân của mỗi loại khác nhau (đồng yên Nhật không có phần lẻ). Đừng giả định hai chữ số thập phân.
- **Dữ liệu vùng:** định dạng số, ngày, tên vùng thường lấy từ kho dữ liệu chung như CLDR thay vì tự viết cho từng nước.
- **Kiểm thử sớm:** chuỗi giả tạo dài hơn bản gốc giúp phát hiện chỗ chữ tràn trước khi có bản dịch thật.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-design-a-system-for-internationalization.md): các khía cạnh cần địa phương hóa khi thiết kế cho nhiều thị trường.
- [Unicode CLDR](https://cldr.unicode.org/): dữ liệu định dạng, số nhiều, tên vùng.
- [ICU — MessageFormat](https://unicode-org.github.io/icu/userguide/format_parse/messages/): câu có tham số và số nhiều.
- [W3C — Internationalization](https://www.w3.org/International/): hướng dẫn về văn bản hai chiều, bố cục, ngôn ngữ.
- [ISO 4217 — mã tiền tệ](https://www.iso.org/iso-4217-currency-codes.html): mã tiền và số chữ số thập phân.
- [IANA — time zone database](https://www.iana.org/time-zones): cơ sở dữ liệu múi giờ.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-008.json).

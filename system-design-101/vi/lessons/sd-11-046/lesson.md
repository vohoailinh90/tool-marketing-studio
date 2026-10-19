# Cloud native là gì: bốn mặt của bài nguồn, và định nghĩa CNCF đã đổi từ bản 1.0 sang 1.1

**"Cloud native" thường bị hiểu là "chạy trong container trên đám mây". Bài nguồn tách nó thành bốn mặt (quy trình phát triển, kiến trúc, đóng gói và triển khai, hạ tầng), còn định nghĩa chính thức của CNCF thì không liệt kê bốn mặt đó và đã được viết lại một lần. Bài này đặt hai thứ cạnh nhau và đếm xem bản 1.1 thay đổi gì so với bản 1.0.**
Phần đếm đọc trực tiếp từ lịch sử tệp định nghĩa trong kho của CNCF, không dựa vào trí nhớ.

![Hai khung. Khung một, bốn mặt theo bài nguồn: quy trình phát triển đi từ thác nước sang agile rồi DevOps; kiến trúc đi từ khối đơn sang vi dịch vụ; đóng gói và triển khai đi từ máy chủ vật lý sang máy ảo rồi container; hạ tầng đi từ tự chủ máy sang chạy trên hạ tầng đám mây. Khung hai, định nghĩa của CNCF: bản 1.0 duyệt năm 2018 nêu năm công nghệ ví dụ và ba đặc tính; bản 1.1 duyệt năm 2024 nêu bảy công nghệ ví dụ, năm đặc tính và nói rõ danh sách chưa đầy đủ.](../../diagrams/sd-11-046-main.svg)

## Từ viết tắt

- **CNCF** (Cloud Native Computing Foundation) — tổ chức giữ nhiều dự án mã nguồn mở của hệ sinh thái cloud native, trong đó có Kubernetes; nơi giữ tệp định nghĩa mà bài này đọc.
- **TOC** (Technical Oversight Committee) — ủy ban giám sát kỹ thuật của CNCF; tệp định nghĩa ghi bản 1.0 được TOC duyệt (kiến thức chung của người biên soạn về vai trò của ủy ban).
- **GB** (Governing Board) — hội đồng điều hành của CNCF; tệp định nghĩa ghi bản 1.1 được TOC và GB duyệt.
- **DevOps** (DEVelopment OPerationS) — cách làm gộp việc phát triển và vận hành phần mềm trong một quy trình, với nhiều tự động hóa; ở bài này là mốc cuối của mặt quy trình theo bài nguồn.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng; "API khai báo" là kiểu giao diện mô tả trạng thái mong muốn thay vì từng bước làm.

## Đọc hình

**Bốn mặt của bài nguồn.** Bài nguồn đặt một sơ đồ tiến hóa từ thập niên 1980 và nói cloud native cho phép dựng và chạy ứng dụng co giãn trên đám mây công cộng, riêng và lai; ứng dụng được thiết kế để tận dụng tính năng của đám mây nên chịu tải tốt và dễ co giãn. Nguồn chia thành bốn mặt:

| Mặt | Từ | Đến |
|---|---|---|
| Quy trình phát triển | thác nước, rồi agile | DevOps |
| Kiến trúc ứng dụng | khối đơn | vi dịch vụ nhỏ, hợp với tài nguyên hạn chế trong container |
| Đóng gói và triển khai | máy chủ vật lý, rồi (khoảng năm 2000) máy ảo cho ứng dụng không nhạy độ trễ | ảnh docker chạy trong container |
| Hạ tầng ứng dụng | máy chủ tự quản | triển khai ồ ạt trên hạ tầng đám mây |

Bốn mặt này là cách chia của bài nguồn; không bản định nghĩa nào của CNCF ở dưới nêu đúng bốn mặt đó.

## Thử: định nghĩa của CNCF đã đổi gì

Ngày 2026-10-19, người biên soạn đọc lịch sử tệp `DEFINITION.md` trong kho `cncf/toc`: bản 1.0 được duyệt ngày 2018-06-11 (commit "Approved by the TOC"), bản 1.1 ghi duyệt ngày 2024-02-26 và vào kho ngày 2024-04-16 (commit "update definition from 02/26 vote, increment minor version"). Một chương trình nhỏ tách đoạn định nghĩa của từng bản, chuẩn hóa chữ hoa và xuống dòng rồi so từ khóa:

| Điểm so sánh | Bản 1.0 (2018) | Bản 1.1 (2024) |
|---|---|---|
| Nói về | công nghệ giúp "xây và chạy ứng dụng co giãn" | thực hành giúp "phát triển, dựng và triển khai khối lượng công việc" ở quy mô lớn, theo cách lập trình được và lặp lại được |
| Công nghệ nêu làm ví dụ | 5: container, lưới dịch vụ, vi dịch vụ, hạ tầng bất biến, API khai báo | 7: thêm đa thuê bao (multi-tenancy) và serverless |
| Đặc tính của hệ thống | ghép lỏng; bền bỉ, dễ quản lý, quan sát được (3) | ghép lỏng và cùng vận hành được; an toàn, bền bỉ, dễ quản lý, bền vững, quan sát được (5) |
| Danh sách ví dụ | không nói gì thêm | ghi rõ "chưa đầy đủ" |
| Lợi ích | thay đổi lớn, thường xuyên, dự đoán được, ít việc nhàm | thêm "tách bạch trách nhiệm rõ ràng" |

Hai điều rút ra, đều từ văn bản hai bản. Một: cách nói của bài nguồn ("ứng dụng co giãn trên đám mây công cộng, riêng, lai") gần với câu mở đầu của bản 1.0; đây là nhận xét của người biên soạn, nguồn không ghi mình theo bản nào. Hai: trong bản 1.1, container chỉ là một trong bảy ví dụ, và thứ định nghĩa nhấn mạnh là đặc tính của hệ thống (ghép lỏng, an toàn, bền bỉ, dễ quản lý, bền vững, quan sát được), không phải một công nghệ cụ thể.

## Giới hạn cần nhớ

Phép so sánh chỉ đếm từ khóa trong đoạn định nghĩa tiếng Anh; không so bản dịch. Bài đối chiếu hai commit của một tệp, không đọc biên bản các cuộc họp duyệt. Bốn mặt của bài nguồn là cách chia của nguồn, không phải định nghĩa chính thức; mốc "khoảng năm 2000" cho máy ảo cũng chỉ theo nguồn, chưa kiểm.

## Nhìn hình trả lời

Một nhóm nói sản phẩm của họ "cloud native" vì chạy trong container trên một nhà cung cấp đám mây. Theo định nghĩa 1.1, như vậy đã đủ chưa? Theo bốn mặt của bài nguồn, họ có thể còn thiếu mặt nào?

<details>
<summary>Xem đáp án</summary>

Chưa đủ. Trong bản 1.1, container chỉ là một ví dụ trong danh sách "chưa đầy đủ"; thứ được nêu là đặc tính của hệ thống: ghép lỏng, an toàn, bền bỉ, dễ quản lý, bền vững, quan sát được. Theo bốn mặt của nguồn, container chỉ nằm ở mặt đóng gói và triển khai; nhóm còn có thể thiếu mặt kiến trúc (vẫn một khối đơn) hoặc mặt quy trình (vẫn phát hành theo kiểu thác nước). Đây là suy luận của người biên soạn từ hai văn bản.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một sơ đồ tiến hóa, một đoạn mở đầu và bốn mặt. Bài này giữ bốn mặt và đặt thêm định nghĩa của CNCF ở hai thời điểm, kèm một phép so sánh từ khóa giữa bản 1.0 và bản 1.1.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-cloud-native.md): đoạn mở đầu và bốn mặt. Bảng so sánh và nhận xét là của người biên soạn.
- [CNCF — DEFINITION.md, bản 1.0 tại commit 1b3bc93 và bản 1.1 tại commit 5b1f003](https://github.com/cncf/toc/blob/5b1f003/DEFINITION.md): hai văn bản định nghĩa, ngày duyệt và ngày vào kho. Đoạn định nghĩa tiếng Anh của bản 1.0 giống hệt ở commit 1b3bc93 và commit 0cdf2c4 (so bằng băm sau khi chuẩn hóa khoảng trắng).

Đã đọc nguồn ngày 2026-10-19. Vai trò của TOC và GB là kiến thức chung của người biên soạn, chưa đối chiếu.
Bài viết và hình được thiết kế độc lập.

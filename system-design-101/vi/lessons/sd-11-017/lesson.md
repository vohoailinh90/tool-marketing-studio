# Các khối nền để dựng hệ thống phân tán, chia theo sáu nhóm

**Hầu hết hệ thống phân tán được lắp từ một bộ khối quen thuộc. Chia chúng thành sáu nhóm giúp bạn nhớ mỗi khối giải việc gì, thay vì học thuộc một danh sách dài.**
Gặp một bản thiết kế, bạn có thể hỏi: nó đã có khối nào trong mỗi nhóm, và nhóm nào còn thiếu?

![Hai khung. Khung một, ba nhóm về tính toán và quy mô: tính toán phân tán, mở rộng và hiệu năng, quản lý dịch vụ. Khung hai, ba nhóm còn lại: mạng và giao tiếp, lưu trữ và quản lý dữ liệu, quan sát và chống chịu lỗi.](../../diagrams/sd-11-017-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt ở nhiều nơi để giao nội dung từ nơi gần người dùng.
- **DNS** (Domain Name System) — hệ thống tên miền: đổi tên dễ đọc thành địa chỉ máy.
- **IP** (Internet Protocol) — giao thức liên mạng: địa chỉ IP là địa chỉ số của một máy trên mạng.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình cho chương trình khác gọi tới nó.

## Đọc hình

Sáu nhóm và các khối giữ theo bài nguồn; lời giải thích và phép tính là của người biên soạn.

**Tính toán phân tán.** *Hàng đợi thông điệp phân tán* cho các dịch vụ nói chuyện bất đồng bộ và tách rời nhau. *Bộ nhớ đệm phân tán* giữ dữ liệu hay dùng trong bộ nhớ để nhanh hơn. *Bộ lập lịch tác vụ phân tán* điều phối khi nào và ở đâu một việc chạy.

**Mở rộng và hiệu năng.** *Dịch vụ co giãn* chỉnh công suất theo nhu cầu. *CDN* giao nội dung từ nơi gần người dùng hơn để giảm độ trễ. *Băm nhất quán* giảm số khóa phải chuyển khi thêm hoặc bớt nút.

**Quản lý dịch vụ.** *Khám phá dịch vụ* cho dịch vụ tự tìm nhau mà không ghi cứng địa chỉ mạng.

**Mạng và giao tiếp.** *DNS* đổi tên miền dễ đọc thành địa chỉ IP. *Bộ chia tải* chia lưu lượng vào cho nhiều máy chủ. *Cổng API* là một cửa vào duy nhất cho một nhóm vi dịch vụ.

**Lưu trữ và quản lý dữ liệu.** *Cơ sở dữ liệu* lưu dữ liệu có cấu trúc. *Lưu trữ đối tượng* giữ các thứ lớn như ảnh, video, tài liệu. *Chia nhỏ dữ liệu (sharding)* chia dữ liệu ngang qua nhiều nút. *Sao chép* nhân bản dữ liệu ra nhiều nút để mở rộng khả năng đọc.

**Quan sát và chống chịu lỗi.** Nhìn vào bên trong hệ thống qua số đo (metrics), nhật ký (logging) và truy vết (tracing).

**Phép tính: vì sao băm nhất quán có mặt trong danh sách.** Chia khóa cho các nút bằng "khóa chia dư cho số nút", rồi thêm nút thứ năm vào bốn nút. Một khóa giữ nguyên chỗ chỉ khi phần dư theo 4 bằng phần dư theo 5; trong mỗi chu kỳ 20 giá trị liên tiếp chỉ 4 giá trị thỏa điều đó (0, 1, 2 và 3), tức 20%. Vậy khoảng 80% khóa phải chuyển. Với băm nhất quán, lý tưởng chỉ khoảng một phần năm số khóa (20%) phải chuyển sang nút mới.

## Giới hạn cần nhớ

Sáu nhóm là cách chia của bài nguồn; một khối có thể thuộc hai nhóm (bộ chia tải vừa là mạng vừa là mở rộng). Phép tính giả định khóa phân bố đều theo các giá trị liên tiếp và nút mới nhận phần chia lý tưởng; hệ thống thật có sai lệch. Bài chỉ nói mỗi khối giải việc gì, không nói chọn sản phẩm nào, và chưa đối chiếu được tài liệu chính thức nào trong phiên viết.

## Nhìn hình trả lời

Trang tin tức bị chậm với người xem ở xa, trong khi máy chủ không quá tải. Khối nào giảm độ trễ này, và thuộc nhóm nào?

<details>
<summary>Xem đáp án</summary>

CDN, thuộc nhóm mở rộng và hiệu năng: nó giao nội dung từ nơi gần người xem hơn nên giảm thời gian truyền đường dài, trong khi máy chủ gốc không cần mạnh hơn. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê sáu nhóm kèm một câu cho mỗi khối. Bài này giữ nhóm và khối, gộp thành hai khung ba nhóm và thêm phép tính cho thấy vì sao băm nhất quán được đặt riêng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/must-know-system-design-building-blocks.md): sáu nhóm và các khối. Lời giải thích và phép tính là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức; phép tính là số học thuần túy.

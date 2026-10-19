# Khôi phục thảm họa trên đám mây: bốn mức, mỗi mức đổi tiền lấy thời gian

**Bốn chiến lược khôi phục thảm họa xếp theo một trục: càng tốn tiền chạy sẵn thì càng khôi phục nhanh và càng mất ít dữ liệu.**
Hiểu trục đó, bạn chọn mức theo mức chịu đựng của doanh nghiệp, không theo mức "tốt nhất".

![Hai khung. Khung một, bốn chiến lược xếp từ rẻ và chậm tới đắt và nhanh: sao lưu và khôi phục, đèn mồi, dự phòng ấm, hai vùng cùng chạy. Khung hai, hai mốc cần đặt trước khi chọn: RTO là thời gian chịu ngừng, RPO là lượng dữ liệu chịu mất.](../../diagrams/sd-11-004-main.svg)

## Từ viết tắt

- **RTO** (Recovery Time Objective) — thời gian khôi phục mục tiêu: sau sự cố, dịch vụ được phép ngừng tối đa bao lâu.
- **RPO** (Recovery Point Objective) — điểm khôi phục mục tiêu: dữ liệu được phép mất tối đa tính đến thời điểm sự cố, thường đo bằng thời gian (mất tối đa bao nhiêu phút dữ liệu mới).

## Đọc hình

Tên bốn mức giữ theo bài nguồn; lời giải thích là của người biên soạn.

**Đặt hai mốc trước.** RTO là bạn chịu ngừng bao lâu, RPO là bạn chịu mất dữ liệu mới của bao lâu. Hai con số này do việc kinh doanh quyết định, rồi mới chọn mức. Chọn ngược (chọn mức rồi mới biết mình chịu được gì) dễ dẫn tới trả quá nhiều hoặc quá ít.

**Backup and Restore (sao lưu và khôi phục).** Chỉ giữ bản sao lưu ở nơi khác; khi thảm họa xảy ra mới dựng hạ tầng mới và nạp dữ liệu. Rẻ nhất vì lúc bình thường không chạy gì thêm. Chậm nhất, vì phải dựng lại từ đầu; RPO bằng khoảng cách giữa hai lần sao lưu.

**Pilot Light (đèn mồi).** Ở vùng dự phòng chỉ chạy phần lõi nhỏ nhất, thường là bản sao của cơ sở dữ liệu luôn được cập nhật; phần còn lại tắt. Khi thảm họa, bật và mở rộng phần còn lại quanh lõi đó. Chậm hơn mức ấm vì phải bật mọi thứ, nhưng dữ liệu gần như mới.

**Warm Standby (dự phòng ấm).** Ở vùng dự phòng chạy sẵn một bản thu nhỏ của toàn hệ thống, đủ để nhận tải khi cần sau khi được mở rộng. Khôi phục nhanh hơn đèn mồi, giá cao hơn vì chạy liên tục.

**Hot Site / Multi-Site (hai vùng cùng chạy).** Hai vùng cùng phục vụ thật, mỗi vùng đủ sức gánh nếu vùng kia mất. Gần như không ngừng. Lượng dữ liệu mất có thể rất nhỏ nhưng không tự động bằng không: sao chép bất đồng bộ giữa hai vùng vẫn có thể làm mất vài thao tác ghi gần nhất, và dữ liệu hỏng sẽ bị sao chép sang cả hai vùng nên vẫn cần bản sao lưu để khôi phục. Mức RPO đạt được tùy chính sách sao chép và sao lưu. Đây là mức đắt nhất, và dữ liệu giữa hai vùng phải được giữ khớp.

## Giới hạn cần nhớ

Cách xếp "rẻ và chậm tới đắt và nhanh" là xu hướng chung, không phải bảng giá: chi phí và thời gian thật phụ thuộc vào khối lượng dữ liệu, cách tự động hóa và việc bạn có tập dượt khôi phục hay không. Một bản sao lưu chưa từng thử khôi phục chưa chắc khôi phục được. Tên bốn mức trùng với cách gọi phổ biến trên đám mây; bài chưa đối chiếu với tài liệu của nhà cung cấp nào trong phiên viết (không đọc được tài liệu của họ từ môi trường biên soạn).

## Nhìn hình trả lời

Cửa hàng của bạn chịu được ngừng nửa ngày nhưng không chịu được mất đơn của hơn vài phút. Mức nào hợp nhất, và bạn phải làm thêm gì ngoài việc chọn mức?

<details>
<summary>Xem đáp án</summary>

Ngừng nửa ngày được thì không cần chạy sẵn hai vùng; nhưng mất tối đa vài phút dữ liệu là RPO chặt, nên cơ sở dữ liệu phải được sao liên tục sang vùng dự phòng. Đèn mồi hợp: lõi dữ liệu luôn mới, còn phần còn lại bật khi cần trong vài giờ. Sao lưu định kỳ mỗi đêm thì không đạt RPO. Ngoài việc chọn mức, cần tập dượt khôi phục định kỳ để biết thời gian thật. Đây là suy luận của người biên soạn với con số giả định của đề.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là bốn mục liệt kê theo thứ tự trên. Bài này giữ tên và thứ tự, thêm hai mốc RTO và RPO làm tiêu chí chọn, và một ví dụ chọn mức từ yêu cầu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-disaster-recovery-strategies.md): chỉ lấy tên và thứ tự bốn mức. Lời giải thích, hai mốc RTO và RPO và ví dụ là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức.

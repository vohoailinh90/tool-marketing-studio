# Giảm chi phí đám mây: bốn đòn bẩy và thứ tự dùng chúng

**Hóa đơn đám mây là tích của ba thứ: bao nhiêu tài nguyên, chạy bao lâu, trả theo đơn giá nào; thêm khoản dữ liệu chuyển đi. Sáu kỹ thuật ở bài nguồn là sáu cách kéo các đòn bẩy đó, và thứ tự kéo quyết định bạn tiết kiệm được bao nhiêu.**
Bài xếp sáu kỹ thuật vào bốn đòn bẩy, tính một ví dụ số học, và chỉ ra vì sao nên giảm dùng trước rồi mới cam kết mua dài hạn.

![Hai khung. Khung một, bốn đòn bẩy: dùng ít hơn gồm giảm lượng dùng, tắt tài nguyên nhàn rỗi và chọn cỡ vừa; dùng ngắn hơn là tắt ngoài giờ cao điểm; trả rẻ hơn là cam kết dùng dài hạn hoặc dùng máy dư; chuyển ít dữ liệu hơn bằng nén, mạng phân phối nội dung và đặt tài nguyên cùng vùng. Khung hai, ví dụ số học: mười máy chạy suốt tuần là 1680 giờ máy; chạy mười giờ mỗi ngày làm việc là 500, còn khoảng 30 phần trăm; cam kết dùng đều trước khi giảm thì vẫn phải trả phần cam kết.](../../diagrams/sd-11-037-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; các kỹ thuật mua máy ở bài lấy tài liệu của AWS làm ví dụ.
- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt ở nhiều nơi, lưu bản sao nội dung và phát cho người dùng từ máy gần họ, nên ít dữ liệu phải đi xa từ máy gốc.

## Đọc hình

Giữ nguyên tên sáu kỹ thuật của bài nguồn, xếp theo đòn bẩy mà chúng tác động:

| Đòn bẩy | Kỹ thuật (tên ở nguồn) | Nó làm gì |
|---|---|---|
| Dùng ít hơn | Reduce Usage; Terminate Idle Resources; Right Sizing | Bớt cỡ và số lượng; xóa tài nguyên không ai dùng; chọn cỡ máy vừa với tải thật |
| Dùng ngắn hơn | Shutdown Resources During Off-Peak Times | Tự động tắt phần không cần khi ít người dùng |
| Trả rẻ hơn | Reserve to Reduce Rate | Cam kết để có đơn giá thấp hơn; mẹo thêm ở nguồn: máy dư (Spot) và loại lưu trữ rẻ hơn |
| Chuyển ít dữ liệu hơn | Optimize Data Transfers | Nén dữ liệu, dùng CDN, đặt tài nguyên trong cùng vùng để dữ liệu ít phải đi xa |

Ba đòn bẩy đầu nhân với nhau, nên chúng cộng hưởng. Đòn bẩy cuối là một khoản riêng, vì dữ liệu đi ra bị tính tiền theo lượng.

## Thử: tính một ví dụ

Số dưới đây là ví dụ để thấy phép nhân, không phải số đo của hệ thống nào. Giả sử mười máy thử nghiệm cùng cỡ, đơn giá `r` mỗi giờ.

- Chạy suốt tuần: 10 máy × 24 giờ × 7 ngày = 1680 giờ máy, tức 1680 `r`.
- Tắt ngoài giờ, chỉ chạy 10 giờ mỗi ngày làm việc: 10 × 10 × 5 = 500 giờ máy, tức 500 `r`, còn khoảng 29,8% so với chạy suốt tuần.
- Chọn cỡ nhỏ hơn mà vẫn đủ tải sẽ nhân thêm một hệ số nữa (giả sử đơn giá giảm theo cỡ, điều không phải lúc nào cũng đúng).

Còn thứ tự: tài liệu của AWS mô tả Reserved Instances và Savings Plans là cam kết dùng đều đặn trong 1 hoặc 3 năm (Savings Plans cam kết theo số tiền mỗi giờ, Reserved Instances theo cấu hình máy cụ thể). Từ đó người biên soạn suy ra: nếu cam kết mua theo mức dùng hiện tại rồi mới tắt bớt, phần cam kết thừa vẫn phải trả; vì vậy nên giảm trước, cam kết sau. Đây là suy luận, không phải câu của tài liệu.

Máy dư (Spot) khác kiểu: tài liệu nói đó là công suất máy ảo chưa dùng của AWS với giá thấp hơn nhiều, đổi lại có thể bị thu hồi; thường có thông báo gián đoạn khoảng hai phút trước đó, nhưng thông báo không được bảo đảm (người rà soát nêu AWS ghi là nỗ lực tối đa) và với máy cấu hình ngủ đông thì việc ngủ đông bắt đầu ngay, nên đừng thiết kế việc dọn dẹp dựa hẳn vào hai phút đó. Nên hợp với việc chịu được gián đoạn (chạy lô, xử lý có thể làm lại), không hợp với phần phải luôn có mặt.

## Giới hạn cần nhớ

Ví dụ số học dựa trên giả sử đơn giá không đổi và tải đủ; thực tế còn khoản lưu trữ và dữ liệu không tắt theo giờ. Mức giảm của cam kết, của máy dư hay của các loại lưu trữ rẻ không được nêu ở bài này vì không đọc được bảng giá hiện hành. Các kỹ thuật của nguồn về nén, CDN và đặt tài nguyên cùng vùng chỉ theo nguồn. Tắt tài nguyên ngoài giờ không dùng được cho thứ phải luôn chạy, và có thể làm chậm lần mở đầu sáng hôm sau; nhận xét này của người biên soạn.

## Nhìn hình trả lời

Một đội sắp mua cam kết một năm cho toàn bộ số máy đang chạy, nhưng tuần sau sẽ bắt đầu tắt môi trường thử nghiệm ngoài giờ. Họ nên đổi thứ tự thế nào?

<details>
<summary>Xem đáp án</summary>

Làm việc giảm trước: xóa thứ nhàn rỗi, chọn cỡ vừa, bật lịch tắt ngoài giờ, đo mức dùng ổn định trong một thời gian. Sau đó mới cam kết cho phần thật sự chạy đều. Cam kết cả số máy hiện tại thì phần môi trường thử nghiệm sắp tắt vẫn bị tính trong cam kết. Đây là suy luận từ mô tả cam kết dùng đều của tài liệu.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và danh sách sáu kỹ thuật theo thứ tự hình, kèm một mẹo thêm. Bài này giữ sáu tên, xếp theo bốn đòn bẩy, thêm phép tính ví dụ và lập luận về thứ tự giảm trước cam kết sau, rồi đối chiếu phần mua bằng cam kết và máy dư với tài liệu AWS.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-cost-reduction-techniques.md): sáu kỹ thuật và mẹo thêm. Cách xếp theo đòn bẩy, ví dụ số và lập luận về thứ tự là của người biên soạn.
- [AWS — các lựa chọn mua EC2 (kho lưu trữ, commit 8a9cb02)](https://github.com/awsdocs/amazon-ec2-user-guide/blob/8a9cb02eb5a0145740adff6099c144aa7f594053/doc_source/instance-purchasing-options.md): cam kết theo giờ hoặc theo cấu hình, 1 hoặc 3 năm; Spot là công suất chưa dùng.
- [AWS — dùng máy Spot (kho lưu trữ, commit 8a9cb02)](https://github.com/awsdocs/amazon-ec2-user-guide/blob/8a9cb02eb5a0145740adff6099c144aa7f594053/doc_source/using-spot-instances.md): máy dư có thể bị thu hồi, thường kèm thông báo khoảng hai phút (không bảo đảm); trang gián đoạn (`spot-interruptions.md`) cùng kho nói tương tự.

Đã đọc nguồn ngày 2026-10-19. Phép tính là của người biên soạn; kho tài liệu AWS đã ngừng cập nhật nên chưa đối chiếu bảng giá hiện hành.
Bài viết và hình được thiết kế độc lập.

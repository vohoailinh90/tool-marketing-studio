# Chi phí ẩn của đám mây: nhóm theo cách hóa đơn đếm

**Hóa đơn đám mây phình lên thường không vì thứ bạn dùng nhiều, mà vì thứ bạn quên: mỗi dịch vụ có một "đồng hồ" riêng, và có đồng hồ cứ chạy khi bạn không còn dùng gì.**
Bài sắp tám khoản chi ẩn trong bài nguồn theo đồng hồ đếm chúng (theo giờ, theo dung lượng, theo lời gọi, theo phần dở dang, theo dữ liệu đi ra), để biết nên đi tìm ở đâu.

![Hai khung. Khung một, bốn cách hóa đơn đếm: theo giờ khi tài nguyên còn tồn tại, như bộ cân bằng tải và địa chỉ IP nhàn rỗi; theo dung lượng mỗi tháng, như ổ đĩa và bản chụp; theo số lời gọi, như lấy và liệt kê trên kho đối tượng; theo phần dở dang và dữ liệu đi ra. Khung hai, ba việc dọn dẹp: trả địa chỉ IP không dùng, xóa ổ đĩa không gắn máy, đặt quy tắc hủy các phần tải lên dở.](../../diagrams/sd-11-035-main.svg)

## Từ viết tắt

- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ và chuyển gói tin giữa các máy; địa chỉ IP là địa chỉ của một máy trên mạng.
- **EBS** (Elastic Block Store) — dịch vụ ổ đĩa của AWS: một ổ đĩa ảo gắn vào một máy ảo, tính tiền theo dung lượng.
- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; bài lấy AWS làm ví dụ vì bài nguồn nói về AWS.
- **GB** (GigaByte) — gigabyte: đơn vị dung lượng cỡ một tỷ byte; hóa đơn lưu trữ tính theo GB mỗi tháng.

## Đọc hình

Bài nguồn liệt kê tám khoản và lấy AWS làm ví dụ, nói rằng các nhà cung cấp khác có cấu trúc giá tương tự. Dưới đây giữ nguyên tên tám khoản, nhưng xếp theo cái đang được đếm:

| Cái được đếm | Khoản ẩn (tên ở nguồn) | Vì sao tiền vẫn chạy |
|---|---|---|
| Giờ tồn tại | Elastic IP Addresses; Load Balancers | Tài nguyên còn đó thì đồng hồ còn quay, dù không có ai dùng |
| GB mỗi tháng | Elastic Block Storage (EBS) Charges; EBS Snapshots | Ổ đĩa không gắn máy vẫn chiếm chỗ; bản chụp là một thứ riêng, xóa ổ không xóa bản chụp |
| Số lời gọi | `S3` Access Charges | Mỗi lần lấy hoặc liệt kê đối tượng là một dòng tính tiền, có thể vượt tiền lưu trữ |
| Phần dở dang | `S3` Partial Uploads | Các phần đã tải lên của một lần tải dở vẫn bị tính cho tới khi hoàn tất hoặc hủy |
| Dữ liệu đi ra | Data Transfer Costs | Đưa dữ liệu vào thường rẻ hoặc miễn phí, kéo ra mới đắt |
| Ngưỡng miễn phí | Free Tier Ambiguity | Có nhiều loại miễn phí, dịch vụ ngoài ngưỡng bị tính, vượt ngưỡng thì giá theo bảng thường |

Phần "Vì sao tiền vẫn chạy" được đối chiếu với tài liệu của AWS ở mục dưới; riêng khoản dữ liệu đi ra, ngưỡng miễn phí, tiền theo lời gọi và bộ cân bằng tải (`Load Balancers`) chỉ theo bài nguồn.

## Thử: đọc tài liệu AWS để kiểm từng khoản

Ngày 2026-10-19 đọc các trang tài liệu AWS lưu trong kho lưu trữ công khai (kho đã ngừng cập nhật, nên có thể cũ hơn bảng giá hiện hành):

- **Phần tải lên dở (`S3`).** Tài liệu về tải lên nhiều phần nói các phần vẫn bị tính tiền lưu trữ cho tới khi bạn hoàn tất hoặc hủy lần tải; hủy thì phần đã tải bị xóa và ngừng tính, không có phí xóa sớm. Tài liệu khuyên đặt một quy tắc vòng đời với hành động `AbortIncompleteMultipartUpload` để tự hủy sau một số ngày.
- **Bản chụp (EBS).** Bản chụp tính tiền theo lượng dữ liệu nó lưu, không theo cỡ ổ đĩa gốc. Tài liệu có ví dụ: ổ 200 `GiB` chứa 50 `GiB` dữ liệu thì bản chụp đầu là 50 `GiB` và bị tính 50 `GiB`; sau khi đổi 20 `GiB` và thêm 10 `GiB`, bản chụp tăng dần chỉ thêm 30 `GiB`. Vì bản chụp là bản sao tăng dần, xóa một bản chưa chắc giảm hóa đơn: dữ liệu bản khác còn dùng vẫn được giữ.
- **Ổ đĩa (EBS).** Chỉ xóa được ổ ở trạng thái `available` (không gắn vào máy); trang xóa ổ nói bạn có thể chụp một bản trước khi xóa. Bản chụp đó sau đó cũng tính tiền.
- **Địa chỉ IP (Elastic IP).** Bản tài liệu này nói một địa chỉ gắn vào máy đang chạy thì miễn phí, còn địa chỉ chưa gắn, gắn vào máy đã dừng hoặc vào giao diện mạng chưa gắn thì bị tính một khoản nhỏ theo giờ, và địa chỉ đã gỡ vẫn thuộc tài khoản cho tới khi bạn trả lại. Quy tắc "gắn vào máy đang chạy thì miễn phí" của bản lưu trữ này đã cũ: người rà soát chỉ ra rằng từ tháng 2 năm 2024 AWS tính phí theo giờ cho mọi địa chỉ IP công cộng do AWS cấp, kể cả địa chỉ đang gắn vào máy chạy. Người biên soạn không đọc được trang giá hiện hành (tên miền bị chặn) nên chưa tự đối chiếu; hãy xem trang giá `Amazon VPC` trước khi dựa vào bất kỳ quy tắc miễn phí nào.

Một chỗ không khớp: bài nguồn nói AWS cho tối đa năm địa chỉ miễn phí, còn bản tài liệu đọc được nói một địa chỉ cho mỗi máy đang chạy. Hai con số khác nhau cho thấy chính sách giá đổi theo thời gian; bài này không dựa vào số nào mà nhắc: xem trang giá hiện hành của nhà cung cấp trước khi tin một ngưỡng miễn phí.

## Giới hạn cần nhớ

Bài không đưa một đơn giá nào, vì đơn giá đổi theo vùng và theo thời gian, và người biên soạn không đọc được trang giá hiện hành để đối chiếu. Bốn khoản (dữ liệu đi ra, tiền theo lời gọi `S3`, ngưỡng miễn phí, bộ cân bằng tải) chỉ theo bài nguồn. Cách nhóm theo "cái được đếm" là của người biên soạn để dễ tìm, không phải phân loại chính thức của AWS. Nguồn nói tương tự với nhà cung cấp khác, nhưng bài chưa đọc tài liệu của họ.

## Nhìn hình trả lời

Bạn xóa một máy ảo thử nghiệm nhưng hóa đơn tháng sau vẫn có dòng EBS và dòng bản chụp. Hai chỗ nào cần xem, theo cách chia ở hình?

<details>
<summary>Xem đáp án</summary>

Cả hai thuộc nhóm "theo GB mỗi tháng". Ổ đĩa có thể còn ở trạng thái không gắn máy, vẫn chiếm dung lượng và vẫn bị tính cho tới khi bị xóa. Bản chụp là thứ riêng: xóa ổ không xóa bản chụp, nên cần liệt kê bản chụp của ổ đã xóa rồi xóa những bản không cần giữ, nhớ rằng với bản chụp tăng dần thì xóa một bản có thể chỉ giảm phần dữ liệu độc quyền của nó. Đây là cách suy luận từ tài liệu đã đọc, không phải hướng dẫn dọn dẹp đầy đủ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và danh sách tám khoản theo thứ tự của hình. Bài này giữ tám tên khoản nhưng sắp theo cách hóa đơn đếm, bỏ hình của nguồn, và đối chiếu bốn khoản với tài liệu AWS. Bài thêm chỗ không khớp về số địa chỉ miễn phí mà nguồn không nhắc.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/hidden-costs-of-the-cloud.md): tên tám khoản chi ẩn và bốn khoản chỉ theo nguồn. Cách xếp theo cái được đếm và các nhận xét là của người biên soạn.
- [AWS — tài liệu `S3` về tải lên nhiều phần (kho lưu trữ, commit 838da1b)](https://github.com/awsdocs/amazon-s3-userguide/blob/838da1b4daaf051faf6e33388f1068a955a301e8/doc_source/mpuoverview.md): phần dở dang vẫn bị tính tiền.
- [AWS — tài liệu EC2 về bản chụp EBS (kho lưu trữ, commit 8a9cb02)](https://github.com/awsdocs/amazon-ec2-user-guide/blob/8a9cb02eb5a0145740adff6099c144aa7f594053/doc_source/EBSSnapshots.md): cách tính bản chụp.
- [AWS — tài liệu EC2 về xóa ổ đĩa EBS (kho lưu trữ, commit 8a9cb02)](https://github.com/awsdocs/amazon-ec2-user-guide/blob/8a9cb02eb5a0145740adff6099c144aa7f594053/doc_source/ebs-deleting-volume.md): trạng thái ổ đĩa và việc chụp trước khi xóa.
- [AWS — tài liệu EC2 về Elastic IP (kho lưu trữ, commit 8a9cb02)](https://github.com/awsdocs/amazon-ec2-user-guide/blob/8a9cb02eb5a0145740adff6099c144aa7f594053/doc_source/elastic-ip-addresses-eip.md): địa chỉ IP nhàn rỗi.

Đã đọc nguồn ngày 2026-10-19. Hai kho tài liệu AWS đã ngừng cập nhật, nên chưa đối chiếu với bảng giá hiện hành.
Bài viết và hình được thiết kế độc lập.

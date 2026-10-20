# AWS từ vài dịch vụ đến hơn hai trăm: đếm trong mã nguồn SDK

**Bài nguồn kể rằng AWS đi từ vài dịch vụ năm 2006 đến hơn 200 dịch vụ. Cách kiểm chứng rẻ nhất là đếm: bộ SDK Python của AWS có một thư mục mô hình cho mỗi dịch vụ, mỗi mô hình mang ngày của phiên bản API, nên đếm thư mục theo năm cho một bức tranh tăng trưởng, kèm những chỗ nó nói sai.**
Bài chạy phép đếm đó trên kho mã công khai và đọc kết quả cùng giới hạn của nó.

![Ba khung. Khung một, số thư mục dịch vụ theo năm của phiên bản API đầu tiên, đợt đầu: đến 2010 có 11; từ 2011 đến 2013 có 18; từ 2014 đến 2016 có 63. Khung hai, đợt sau: từ 2017 đến 2019 có 161; từ 2020 đến 2022 có 111; từ 2023 đến 2026 có 73. Khung ba, ba điều cần nhớ: thư mục khác dịch vụ; năm của phiên bản API khác năm ra mắt; thư mục ec2 chỉ còn các phiên bản từ 2014.](../../diagrams/sd-11-040-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon.
- **SDK** (Software Development Kit) — bộ công cụ phát triển phần mềm: thư viện giúp chương trình gọi một dịch vụ; ở đây là bộ SDK Python tên botocore, lõi của thư viện boto3.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình yêu cầu dịch vụ làm việc; mỗi phiên bản API của AWS mang một ngày, như `2006-03-01`.

## Đọc hình

Bài nguồn là một hình dòng thời gian các dịch vụ AWS, kèm vài câu: AWS bắt đầu từ vài dịch vụ năm 2006 và có hơn 200 dịch vụ; với một số dịch vụ, năm công bố hoặc xem trước khác năm phát hành, và bài nguồn ghi theo năm phát hành.

Phép đếm: ngày 2026-10-19, người biên soạn lấy danh sách tệp của kho `boto/botocore` ở commit `4de93ab` (ngày 2026-10-16), chỉ đọc tên thư mục và tệp, không tải mã. Dưới `botocore/data/` mỗi dịch vụ có một thư mục, bên trong là thư mục theo ngày phiên bản API, chứa tệp `service-2.json`. Kết quả:

- 437 thư mục dịch vụ, chứa 470 tệp mô hình (10 dịch vụ có nhiều phiên bản API; riêng `cloudfront` có 19).
- Gom theo năm của phiên bản API **sớm nhất còn trong kho**: đến 2010 có 11; 2011 đến 2013 có 18; 2014 đến 2016 có 63; 2017 đến 2019 có 161; 2020 đến 2022 có 111; 2023 đến 2026 có 73.
- Thư mục sớm nhất là `s3` (`2006-03-01`), tiếp theo `emr` (2009-03-31), `sdb` (2009-04-15), `sns` (2010-03-31), `iam` (2010-05-08) và `cloudformation` (2010-05-15).

Con số 437 phù hợp với "hơn 200" của nguồn, và chỉ ra cú tăng nhanh nhất ở giai đoạn 2017 đến 2019 (161 thư mục có phiên bản đầu tiên rơi vào ba năm đó).

## Thử: tìm chỗ phép đếm nói sai

Nhìn vào dữ liệu, ba chỗ cho thấy phép đếm không thể đọc là "số dịch vụ ra mắt mỗi năm":

- **Thư mục khác dịch vụ.** Mỗi thư mục là một mô hình API, không phải một sản phẩm. Ví dụ có `elb` và `elbv2` (hai thế hệ bộ cân bằng tải), `dynamodb` và `dynamodbstreams`, `kinesisanalytics` và `kinesisanalyticsv2`: một sản phẩm có thể chiếm nhiều thư mục.
- **Ngày phiên bản không phải ngày ra mắt.** Dịch vụ máy ảo `ec2` ra mắt năm 2006 nhưng thư mục của nó chỉ còn các phiên bản từ `2014-09-01`; kho không giữ phiên bản cũ hơn. Một dịch vụ có API sớm nhưng viết mô hình muộn cũng nhìn như mới hơn thực tế.
- **Thư mục có mặt không nghĩa là phát hành rộng.** Thư mục chỉ cho biết SDK có mô hình ấy ở thời điểm đọc.

Phép đếm vì thế chỉ ủng hộ một điều: ở thời điểm đọc, SDK mô tả bốn trăm lẻ vài mô hình API của AWS, nhiều hơn 200 của nguồn, và phần lớn mô hình mới xuất hiện từ 2017 trở đi.

## Giới hạn cần nhớ

Bài không xác nhận dòng thời gian từng dịch vụ của bài nguồn (nhìn hình không đọc được từ máy biên soạn) và không thay cho trang chính thức của AWS về lịch sử dịch vụ. Số liệu là ảnh chụp ở một commit, đổi theo từng bản phát hành SDK. Các tên thư mục như `emr` hay `sdb` là tên của mô hình, người đọc cần tra tên đầy đủ của dịch vụ.

## Nhìn hình trả lời

Một bạn đếm số thư mục ra 437 rồi viết "AWS có đúng 437 dịch vụ". Hai lý do cụ thể khiến câu đó sai là gì?

<details>
<summary>Xem đáp án</summary>

Thứ nhất, thư mục là mô hình API chứ không phải sản phẩm: có sản phẩm nhiều mô hình, và có dịch vụ có nhiều phiên bản API. Thứ hai, kho SDK chỉ phản ánh dịch vụ có mô hình ở thời điểm đọc, chưa kể dịch vụ chưa có SDK hay đã bị gỡ. Con số 437 chỉ là số thư mục mô hình ở một commit.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê các dịch vụ AWS theo năm bằng một hình. Bài này không dựng lại hình đó, mà dùng phép đếm trên mã nguồn SDK để kiểm tra hai điều bài nguồn nói bằng lời (khởi đầu năm 2006, hơn 200 dịch vụ) và chỉ ra giới hạn của cách đếm.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/aws-services-evolution.md): lời nhận định về 2006 và hơn 200 dịch vụ; không dùng hình.
- [boto/botocore tại commit 4de93ab](https://github.com/boto/botocore/tree/4de93abe62cc263980414f7a66be5226bd541b77/botocore/data): danh sách thư mục và tệp mô hình; phép đếm là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Phép đếm là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

# Bản đồ dịch vụ AWS: chín trang theo cách Microsoft chia, và trang "dịch vụ khác" chứa gần một phần ba

**Bài nguồn giới thiệu một tờ hướng dẫn bằng hình để tìm đường trong rất nhiều dịch vụ AWS; nội dung nằm trong ảnh và bài này không đọc ảnh. Thay vào đó, bài hỏi một câu đếm được: khi Microsoft phải xếp các dịch vụ AWS vào những trang để người đến từ AWS tìm lại, họ chia thế nào? Trong 194 dòng ghép dịch vụ, 63 dòng nằm ở trang giới thiệu, nơi gom các dịch vụ không có trang riêng: gần một phần ba.**
Đó là cách Microsoft chia, không phải cách AWS chia, và phép đếm không đo số dịch vụ của AWS.

![Ba khung. Khung một, bài nguồn: một ảnh hướng dẫn các dịch vụ AWS, ảnh không được đọc. Khung hai, chín trang của Microsoft chứa 194 dòng ghép dịch vụ: trang giới thiệu gom 63 dòng, tính toán 27, mạng 24, phân tích 23, lưu trữ 17, cơ sở dữ liệu 13, danh tính 13, trí tuệ nhân tạo và học máy 9, nhắn tin 5. Khung ba, điều cần nhớ: có 183 tên dịch vụ AWS khác nhau, 17 tên nằm ở hai trang, và đây là cách chia của Microsoft chứ không phải của AWS.](../../diagrams/sd-11-049-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon.

## Đọc hình

**Bài nguồn có gì.** Phần chữ của bài nguồn kể rằng AWS đi từ một dự án nội bộ thành nhà dẫn đầu thị trường dịch vụ đám mây, có nhiều dịch vụ đến mức người trong nghề cũng thấy choáng, và giới thiệu tờ hướng dẫn bằng hình như một công cụ giúp chọn đúng dịch vụ. Bài này không kiểm nhận định về thị trường, và không đọc nội dung ảnh.

**Chín trang của Microsoft.** Loạt bài "Azure for AWS professionals" có một trang giới thiệu và mười một trang theo mảng việc. Ba trang (tài khoản, vùng và khu, quản lý tài nguyên) kể về khái niệm, không có bảng ghép dịch vụ. Tám trang còn lại cộng với trang giới thiệu là chín trang có bảng, và chỉ chín trang này đóng góp dòng cho phép đếm.

**Trang giới thiệu cũng là một "kho chứa".** Chính trang này viết "Not every AWS service or Azure service is listed", rồi ở mục sau: "The preceding list doesn't include all services." Những dịch vụ không có trang riêng được dồn xuống dưới tiêu đề `Other services` (53 dòng, mười mục) và mục `Miscellaneous` (10 dòng).

## Thử: đếm dòng theo trang

Ngày 2026-10-19, người biên soạn viết một chương trình đọc các bảng Markdown trong thư mục `docs/aws-professional` (kho `MicrosoftDocs/architecture-center`, commit `8e2c239`). Chương trình chỉ nhận bảng có cả cột "AWS service" và cột "Azure service", và đếm mỗi dòng bảng một lần.

| Trang | Số dòng | Tỷ lệ |
|---|---|---|
| Giới thiệu (dịch vụ khác) | 63 | 32,5% |
| Tính toán | 27 | 13,9% |
| Mạng | 24 | 12,4% |
| Phân tích | 23 | 11,9% |
| Lưu trữ | 17 | 8,8% |
| Cơ sở dữ liệu | 13 | 6,7% |
| Danh tính | 13 | 6,7% |
| Trí tuệ nhân tạo và học máy | 9 | 4,6% |
| Nhắn tin | 5 | 2,6% |
| Tổng | 194 | 100% |

Bên trong 63 dòng của trang giới thiệu, mục lớn nhất là `Management and governance` (quản lý và quản trị) với 16 dòng, nhiều hơn cả trang cơ sở dữ liệu (13 dòng). Sau đó là `Miscellaneous` (10), `Web applications` (7), rồi ba mục 6 dòng: `DevOps and application monitoring`, `Internet of Things (IoT)` và `Authentication and authorization`. Bảo mật cũng bị rải ra: trang danh tính có 13 dòng, và bốn mục bảo mật của trang giới thiệu (`Authentication and authorization`, `Encryption`, `Firewalls`, `Security`) thêm 16 dòng.

Về tên dịch vụ: lấy chữ của các liên kết trong cột AWS (không phân biệt hoa thường), có 200 lượt nhắc nhưng chỉ 183 tên khác nhau, vì 17 tên xuất hiện ở hai trang. Ví dụ `Amazon Lightsail` nằm ở trang tính toán và trong mục ứng dụng web của trang giới thiệu; `Amazon Kinesis Data Streams` nằm ở trang phân tích và trang nhắn tin. Mười bốn trong 17 trường hợp trùng có một trang là trang giới thiệu.

Tự thử: chọn ba dịch vụ bạn biết, đoán trang nào sẽ chứa chúng, rồi tìm. `AWS CloudFormation` nằm ở trang giới thiệu, mục `DevOps and application monitoring`; `AWS Step Functions` nằm ở cả trang tính toán lẫn trang giới thiệu; `Amazon Lightsail` như trên.

## Giới hạn cần nhớ

Số dòng không phải số dịch vụ: một ô có thể nêu nhiều dịch vụ AWS (15 dòng làm vậy), và một dịch vụ có thể có hai dòng ở hai trang. 183 cũng không phải số dịch vụ của AWS, vì Microsoft tự nói không liệt kê hết, và ô không có liên kết không được đếm tên. Cách chia chín trang là của Microsoft, viết cho người học Azure; cách chia của chính AWS không được đọc ở đây. Các trang ghi ngày cập nhật năm 2026, nên bản sau có thể khác. Ảnh của bài nguồn không được đối chiếu, nên bài không nói gì về cách tờ hướng dẫn chia nhóm.

## Nhìn hình trả lời

Bạn dựng bản đồ dịch vụ AWS cho đồng đội và chia thành chín nhóm như các trang của Microsoft. Vì sao nên để sẵn một nhóm "khác", và nên làm gì với nhóm đó?

<details>
<summary>Xem đáp án</summary>

Vì trong cách chia của Microsoft, 63 trên 194 dòng (32,5%) rơi vào nhóm gom những thứ không có trang riêng, nên một danh sách chỉ có chín chủ đề sẽ giấu mất gần một phần ba. Nhóm "khác" cần được chia mục nhỏ, như Microsoft chia trang giới thiệu thành mười một mục. Cũng cho phép một dịch vụ có hai nhà, vì 17 trong 183 tên xuất hiện ở hai trang. Đây là suy luận của người biên soạn từ một cách chia, không phải quy tắc chung.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một ảnh hướng dẫn và vài đoạn chữ. Bài này không dựng lại ảnh; thay vào đó, đọc các trang của Microsoft và đếm dòng theo trang để thấy một bản đồ dịch vụ phải chia nhóm thế nào và nhóm "khác" lớn đến đâu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/aws-services-cheat-sheet.md): chỉ có phần chữ ngắn; ảnh không được đọc.
- [Microsoft — Azure for AWS professionals](https://github.com/MicrosoftDocs/architecture-center/tree/8e2c239344ee753a88856800b4210a3e27ac1036/docs/aws-professional): các bảng ghép dịch vụ tại commit `8e2c239`; trang `index.md` là trang giới thiệu.

Đã đọc nguồn ngày 2026-10-19. Phép đếm là của người biên soạn; nội dung ảnh của bài nguồn chưa đối chiếu.
Bài viết và hình được thiết kế độc lập.

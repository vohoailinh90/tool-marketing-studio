# Azure theo mảng việc: mười một mảng và 266 nhà cung cấp tài nguyên

**Azure có hàng trăm dịch vụ, nên cách đọc duy nhất khả thi là theo mảng việc. Microsoft tự chia phần so sánh với AWS thành mười một mảng, và kho đặc tả công khai của Azure cho thấy dưới đó có 266 "nhà cung cấp tài nguyên".**
Bài đọc Azure bằng hai tấm bản đồ ấy, thay cho tấm ảnh tóm tắt của bài nguồn.

![Bốn khung. Khung một, mảng nền: tài khoản và đăng ký, điện toán, lưu trữ, cơ sở dữ liệu. Khung hai, thêm bốn mảng: mạng, phân tích, trí tuệ nhân tạo và học máy, nhắn tin. Khung ba, ba mảng còn lại: khu vực và vùng, quản lý tài nguyên, danh tính nhiều đám mây. Khung bốn, đếm trong kho đặc tả: 266 nhà cung cấp tài nguyên, 317 thư mục cấp một, nhiều tên là việc nền như tính tiền và quyền.](../../diagrams/sd-11-041-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; bài so sánh Azure với nó.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình yêu cầu dịch vụ làm việc; mỗi nhà cung cấp tài nguyên là một đầu mối API.

## Đọc hình

Bài nguồn nói Azure ra mắt năm 2010, từ dịch vụ cơ bản mở rộng ra điện toán đám mây toàn diện, nay hỗ trợ cả ứng dụng truyền thống lẫn công nghệ mới như trí tuệ nhân tạo, Internet vạn vật và chuỗi khối; tấm ảnh kèm theo là phần giới thiệu và tra cứu nhanh. Nguồn cũng nói Azure giữ vị trí thứ hai về thị phần; điều này phụ thuộc thời điểm và nguồn thống kê nên bài không lặp lại.

**Mười một mảng của Microsoft.** Trang "Azure for AWS professionals" trong kho tài liệu kiến trúc của Microsoft đưa ra mười một bài so sánh Azure với AWS: tài khoản và đăng ký; phân tích; điện toán; trí tuệ nhân tạo và học máy; cơ sở dữ liệu; nhắn tin; mạng; khu vực và vùng; quản lý tài nguyên; danh tính nhiều đám mây; lưu trữ. Trang nói rõ không phải dịch vụ nào cũng có mặt, và không phải cặp nào cũng giống nhau từng tính năng. Ngoài mười một mảng còn các bảng "dịch vụ khác": công cụ phát triển và vận hành, Internet vạn vật, quản trị, mã hóa, tường lửa, ứng dụng web, máy tính của người dùng cuối.

Một điểm khác biệt nền tảng mà trang nêu: AWS dựa nhiều vào tài khoản làm ranh giới logic (áp quyền, theo dõi chi tiêu); Azure dùng "subscription" với vai trò tương tự.

## Thử: đếm kho đặc tả công khai của Azure

Ngày 2026-10-19, người biên soạn lấy danh sách tệp của kho `Azure/azure-rest-api-specs` ở commit `568e5a4`, không tải nội dung. Thư mục `specification/` có 317 thư mục cấp một; các thư mục dạng `resource-manager/Microsoft.<tên>` có 266 tên khác nhau. Mỗi tên là một nhà cung cấp tài nguyên, tức một đầu mối API của Azure cho một nhóm tài nguyên (như `Microsoft.Compute`, `Microsoft.Cache`, `Microsoft.Batch`).

Đọc danh sách tên thấy nhiều nhà cung cấp là việc nền chứ không phải sản phẩm người dùng gọi tên: như `Microsoft.Billing`, `Microsoft.Consumption`, `Microsoft.Capacity`, `Microsoft.Authorization`, `Microsoft.Advisor`. Điều này khớp với việc Microsoft xếp quản trị, tính tiền, danh tính vào các mảng riêng.

## Giới hạn cần nhớ

Số 266 là số tên nhà cung cấp trong kho đặc tả ở một commit; không phải số dịch vụ bán cho khách hàng, vì một dịch vụ có thể trải trên nhiều nhà cung cấp và một nhà cung cấp có thể phục vụ nhiều dịch vụ. Mười một mảng là cách Microsoft chia để người từng dùng AWS dễ chuyển, không phải phân loại chính thức của Azure. Bài không đọc ảnh tóm tắt của nguồn nên không bàn từng dịch vụ trong đó.

## Nhìn hình trả lời

Bạn quen AWS và cần tìm dịch vụ Azure tương đương cho việc gửi tin nhắn giữa các hệ thống. Bạn nên vào mảng nào của bản đồ, và tại sao không nên mong tìm thấy một cặp khớp từng tính năng?

<details>
<summary>Xem đáp án</summary>

Mảng "nhắn tin" của mười một mảng. Trang của Microsoft nói chính nó chỉ so sánh những dịch vụ gần tương đương, không phải dịch vụ nào cũng có cặp, và không cặp nào được bảo đảm giống từng tính năng; vì vậy kết quả là điểm khởi đầu để đọc tài liệu từng dịch vụ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một đoạn giới thiệu về Azure và một ảnh bảng tóm tắt. Bài này không dùng ảnh, thay bằng mười một mảng trong tài liệu Microsoft và một phép đếm các nhà cung cấp tài nguyên trong kho đặc tả công khai.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/azure-services-cheat-sheet.md): năm ra mắt và nhận định chung; không dùng ảnh.
- [Microsoft — Azure for AWS professionals](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/aws-professional/index.md): mười một mảng và ranh giới tài khoản (commit 8e2c239).
- [Azure — kho đặc tả REST API](https://github.com/Azure/azure-rest-api-specs/tree/568e5a4dd830f9f23a5fb32502553c0ceafb6084/specification): danh sách thư mục dùng cho phép đếm (commit 568e5a4).

Đã đọc nguồn ngày 2026-10-19. Phép đếm là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

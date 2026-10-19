# Shopify: mười nguyên tắc cho hệ thống thanh toán bền

**Theo bài nguồn, Shopify gom kinh nghiệm làm hệ thống thanh toán thành mười nguyên tắc: hỏng sớm, chặn lỗi lan, tính trước sức chứa, nhìn thấy hệ thống, không ghi trùng, đối soát, thử tải, và xử lý sự cố có vai trò rõ.**
Bài này xếp mười nguyên tắc theo thời điểm chúng có tác dụng: trước khi lỗi xảy ra, trong lúc gọi dịch vụ khác, và sau khi đã có sự cố.

![Ba khung. Khi gọi dịch vụ khác: hạ thời gian chờ, đọc 5 giây và ghi 1 giây thay cho mặc định 60 giây; cầu dao Semian bảo vệ các lời gọi tới HTTP, MySQL, Redis và gRPC; khóa chống trùng dùng mã sắp được theo thời gian thay cho UUID phiên bản 4. Để nhìn thấy và chuẩn bị: tính sức chứa, ví dụ 50 yêu cầu trong hàng đợi, mỗi yêu cầu 100 mili giây thì thông lượng là 500 yêu cầu mỗi giây; theo dõi bốn tín hiệu vàng là độ trễ, lưu lượng, lỗi và độ bão hòa; nhật ký có cấu trúc lưu tập trung; thử tải bằng cách mô phỏng đợt bán chớp nhoáng. Sau sự cố: lưu chênh lệch đối soát với đối tác tài chính; kênh sự cố có ba vai trò; buổi nhìn lại hỏi ba câu.](../../diagrams/sd-02-024-main.svg)

## Từ viết tắt

- **SRE** (Site Reliability Engineering) — kỹ thuật độ tin cậy của hệ thống: cách Google vận hành dịch vụ, có một cuốn sách cùng tên.
- **UUID** (Universally Unique IDentifier) — mã định danh duy nhất toàn cục; phiên bản 4 là các bit ngẫu nhiên.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách trình duyệt và máy chủ gửi yêu cầu, trả lời.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc; chữ SQL trong tên MySQL.
- **gRPC** (gRPC Remote Procedure Calls) — tên viết tắt đệ quy của một hệ thống gọi hàm từ xa, tức gọi một hàm chạy trên máy khác như gọi hàm trên máy mình.
- **IMOC** (Incident Manager On Call) — người quản lý sự cố đang trực.
- **SRM** (Support Response Manager) — người quản lý phản hồi hỗ trợ: lo phần trao đổi với người dùng bị ảnh hưởng.

## Đọc hình

**Khi gọi dịch vụ khác.**
1. Hạ thời gian chờ để hỏng sớm. Mặc định là 60 giây; theo kinh nghiệm của Shopify, đọc 5 giây và ghi 1 giây là mức ổn.
2. Lắp cầu dao (circuit breaker). Shopify viết Semian bằng Ruby để bảo vệ các lời gọi qua `Net::HTTP`, MySQL, Redis và gRPC.
3. Dùng khóa chống trùng (idempotency key), và dùng `ULID` cho khóa này thay vì UUID phiên bản 4 ngẫu nhiên. `ULID` (Universally Unique Lexicographically Sortable Identifier) là mã định danh duy nhất sắp được theo thứ tự: phần đầu là thời gian tính đến mili giây, nên mã tạo ở mili giây sau đứng sau. Hai mã tạo trong cùng một mili giây chỉ chắc đúng thứ tự khi thư viện tạo mã theo kiểu tăng dần (monotonic).

**Để nhìn thấy và chuẩn bị.**
4. Quản lý sức chứa. Ví dụ của nguồn: 50 yêu cầu trong hàng đợi, mỗi yêu cầu mất trung bình 100 mili giây, thì thông lượng là 500 yêu cầu mỗi giây. Phép tính này chỉ đúng khi cả 50 yêu cầu được xử lý cùng lúc; nếu chỉ một nơi xử lý lần lượt từng yêu cầu thì chỉ được 10 yêu cầu mỗi giây. Nguồn không nói giả định này, người biên soạn thêm vào.
5. Theo dõi và cảnh báo. Sách SRE của Google nêu bốn tín hiệu vàng cho hệ thống phục vụ người dùng: độ trễ, lưu lượng, lỗi và độ bão hòa.
6. Ghi nhật ký có cấu trúc, lưu ở một chỗ và dễ tìm.
7. Thử tải. Shopify thường xuyên mô phỏng các đợt bán chớp nhoáng (flash sale) lớn để lấy số đo chuẩn.

**Sau khi có chuyện.**
8. Đối soát nhất quán: lưu các chênh lệch đối soát với đối tác tài chính của Shopify vào cơ sở dữ liệu.
9. Quản lý sự cố: mỗi kênh sự cố có ba vai trò, là IMOC, SRM và chủ dịch vụ.
10. Nhìn lại sau sự cố, với ba câu hỏi: chuyện gì đã xảy ra, ta đã giả định sai điều gì về hệ thống, và làm gì để chuyện này không lặp lại.

## Giới hạn cần nhớ

Bài nguồn chỉ có một hai câu cho mỗi nguyên tắc. Nó không nói cầu dao mở khi nào, không giải thích vì sao `ULID` tốt hơn UUID ngẫu nhiên, và con số thông lượng chỉ là ví dụ tính tay, không phải số đo của Shopify. Cách xếp mười nguyên tắc thành ba nhóm là của người biên soạn.

## Nhìn hình thử trả lời

Một yêu cầu thanh toán gửi tới cổng thanh toán bị hết thời gian chờ, và ứng dụng gửi lại. Theo hình, nguyên tắc nào giúp khách không bị trừ tiền hai lần, và nguyên tắc nào giúp ứng dụng biết sớm là đã có vấn đề?

<details>
<summary>Xem đáp án</summary>

Khóa chống trùng: lần gửi lại mang cùng khóa, nên bên nhận nhận ra đây là cùng một thanh toán và không trừ tiền lần nữa. Thời gian chờ thấp (đọc 5 giây, ghi 1 giây thay vì 60 giây) giúp ứng dụng biết sớm và quyết định thử lại hay báo lỗi.

</details>

<details>
<summary>Xem sâu hơn: cầu dao làm gì</summary>

- Khi một dịch vụ phía sau lỗi liên tục, cầu dao "mở": các lời gọi tiếp theo bị từ chối ngay thay vì chờ hết thời gian.
- Sau một lúc, cầu dao cho thử vài lời gọi; nếu thành công thì "đóng" lại.
- Lợi ích: một dịch vụ hỏng không kéo theo cả hệ thống vì mọi luồng đều đang chờ nó.

Đây là kiến thức chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/10-principles-for-building-resilient-payment-systems-by-shopify.md): mười nguyên tắc và các con số đi kèm.

Đã đọc nguồn ngày 2026-10-19. Bài viết gốc của Shopify chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

# GraphQL tại LinkedIn

**Theo bản tóm tắt của nguồn, truy vấn GraphQL tại LinkedIn được viết, thử, đăng ký vào một kho chung, phát hành cùng mã client, rồi mới chạy.** Bài này đi theo ba giai đoạn đó và hai lý do LinkedIn không đặt GraphQL gateway.

![Năm khung dọc: viết và thử, nhà phát triển phía client viết truy vấn và thử với dịch vụ phía sau; đăng ký, truy vấn được commit rồi xuất bản lên kho đăng ký truy vấn; chạy thật, truy vấn được phát hành cùng mã client, siêu dữ liệu định tuyến đi kèm để tầng định tuyến đưa yêu cầu tới đúng cụm dịch vụ, và dịch vụ giữ cache các truy vấn đã đăng ký; ví dụ một truy vấn đi qua dịch vụ danh tính lấy hội viên rồi dịch vụ tổ chức lấy công ty; không có GraphQL gateway để bớt một chặng mạng và tránh điểm đơn lỗi.](../../diagrams/sd-01-019-main.svg)

## Từ viết tắt

- **URL** (Uniform Resource Locator) — địa chỉ đầy đủ của một tài nguyên trên web, ví dụ địa chỉ một trang.
- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt ở nhiều nơi, lưu bản sao nội dung và phát cho người dùng từ máy gần họ.
- **APQ** (Automatic Persisted Queries) — truy vấn đã đăng ký tự động: cơ chế của Apollo cho client gửi mã băm của truy vấn thay vì cả chuỗi, để giảm kích thước yêu cầu.

## Đọc hình

1. **Viết và thử.** Nhà phát triển phía client viết truy vấn, chọn đúng các trường cần dùng, và thử với các dịch vụ phía sau.
2. **Đăng ký.** Truy vấn được commit rồi xuất bản lên một kho đăng ký truy vấn.
3. **Chạy thật.** Truy vấn được phát hành cùng bản mã client. Mỗi truy vấn đã đăng ký mang siêu dữ liệu định tuyến, nên tầng định tuyến lưu lượng biết đưa yêu cầu tới cụm dịch vụ nào. Khi chạy, dịch vụ giữ cache các truy vấn đã đăng ký.
4. **Ví dụ trong nguồn.** Một truy vấn đi qua dịch vụ danh tính để lấy hội viên, rồi sang dịch vụ tổ chức để lấy thông tin công ty.
5. **Không có GraphQL gateway.** Nguồn nêu hai lý do: tránh thêm một chặng mạng, và tránh một điểm đơn lỗi.

## Giới hạn cần nhớ

Đây là mô tả về một công ty cụ thể ở quy mô của họ, không phải khuyến nghị chung. Theo suy luận của bài (không phải lời của nguồn), đăng ký truy vấn trước đổi sự tự do lấy kiểm soát: client khó thử truy vấn mới ngay trên production, và mỗi truy vấn gắn với một bản phát hành. Cũng có cách khác, như gateway hay federation gom nhiều schema; mỗi cách có đánh đổi riêng. Mọi chi tiết về LinkedIn ở đây lấy từ bản tóm tắt của nguồn; bài gốc của LinkedIn chưa được mở để đối chiếu.

## Nhìn hình thử trả lời

Nhóm bạn muốn cho ứng dụng di động gọi GraphQL nhưng lo ai đó gửi một truy vấn lồng sâu làm quá tải backend. Việc đăng ký truy vấn trước giải quyết điều gì, và đổi lại bạn mất gì?

<details>
<summary>Xem đáp án</summary>

Nếu máy chủ chỉ chạy truy vấn đã đăng ký thì không còn truy vấn ngoài danh sách; truy vấn nặng vẫn có thể được đăng ký, nên cần xem xét khi đăng ký. Bạn cũng biết trước mỗi truy vấn chạm dịch vụ nào, từ đó định tuyến, đo tải và cache dễ hơn. Đổi lại, client không tự do thử truy vấn mới trên production, cần thêm bước đăng ký và phát hành, và bản ứng dụng cũ vẫn cần các truy vấn cũ còn tồn tại.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **GraphQL trong ba ý:** một schema có kiểu mô tả dữ liệu; client chọn đúng các trường cần; thường chỉ có một điểm vào thay vì nhiều URL.
- **Truy vấn đã đăng ký (persisted query):** client gửi định danh (thường là mã băm) thay vì cả chuỗi truy vấn, nên yêu cầu nhỏ hơn. Cơ chế tự động của Apollo (APQ) giúp giảm kích thước yêu cầu và, khi gửi bằng GET, cho phép cache ở trình duyệt hoặc CDN; nhưng APQ không tự giới hạn những truy vấn được chạy vì truy vấn chưa biết có thể được đăng ký tự động. Theo suy luận của bài, muốn giới hạn thì máy chủ cần thêm một danh sách cho phép (allowlist).
- **Vấn đề N+1:** nếu mỗi hội viên trong danh sách lại gọi riêng dịch vụ tổ chức, số lần gọi tăng theo kích thước danh sách; cách chữa thường là gom nhiều lần tra cứu thành một lần (batching).
- **Gateway hay không:** gateway gom nhiều schema cho client một cửa chung nhưng thêm một chặng và một điểm cần dự phòng; định tuyến theo siêu dữ liệu tránh chặng đó nhưng đòi hỏi quy trình đăng ký chặt.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-graphql-work-in-the-real-world.md): bản tóm tắt cách LinkedIn dùng GraphQL.
- [Đặc tả GraphQL](https://spec.graphql.org/) và [GraphQL — Learn](https://graphql.org/learn/).
- [Apollo — Persisted queries](https://www.apollographql.com/docs/apollo-server/performance/apq/).
- [DataLoader — gom lần tra cứu](https://github.com/graphql/dataloader).

Đã đọc bản nguồn ByteByteGo ngày 2026-10-13; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

# Kiến trúc tổng thể của Netflix qua tám lớp

**Bài nguồn vẽ Netflix thành tám lớp, từ ứng dụng trên máy người xem tới công cụ phát hành, và gắn vào mỗi lớp vài công nghệ tiêu biểu.**
Bài này đọc hình theo đường đi của một yêu cầu: từ ứng dụng, qua lớp giao tiếp và dịch vụ phía sau, xuống dữ liệu và video, rồi tới các công cụ đứng ngoài đường đi đó.

![Tám lớp xếp từ trên xuống. Ứng dụng di động viết bằng Swift và Kotlin, ứng dụng web bằng React. Ứng dụng nói chuyện với máy chủ qua GraphQL. Dịch vụ phía sau dùng Zuul, Eureka, Spring Boot. Cơ sở dữ liệu gồm EVCache, Cassandra, CockroachDB. Truyền tin và dòng dữ liệu dùng Kafka và Flink. Video lưu trên S3 và Open Connect. Xử lý dữ liệu dùng Flink, Spark, Tableau và Redshift. Phát hành dùng Jira, Confluence, PagerDuty, Jenkins, Gradle, Chaos Monkey, Spinnaker, Atlas. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-018-main.svg)

## Từ viết tắt

- **CI** (Continuous Integration) — tích hợp liên tục: mỗi thay đổi mã được tự động build và kiểm thử.
- **CD** (Continuous Delivery) — chuyển giao liên tục: bản đã kiểm thử được tự động đưa tới bước phát hành.
- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, cho biết đây là cách để ứng dụng mô tả dữ liệu mình muốn lấy.
- **EV** (Ephemeral Volatile) — tạm thời, dễ mất: chữ EV trong tên EVCache, bộ nhớ đệm của Netflix; dữ liệu trong đó có thể mất và được nạp lại.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức để ghi và tìm lại nhanh; có trong tên CockroachDB.

## Đọc hình

Bài nguồn nói nó tổng hợp từ nhiều bài blog kỹ thuật và dự án mã nguồn mở của Netflix, và mời người đọc báo lỗi nếu có chỗ sai. Tám lớp theo nguồn:

- **Ứng dụng:** ứng dụng di động gốc viết bằng Swift (iPhone) và Kotlin (Android); ứng dụng web dùng React.
- **Giao tiếp giữa ứng dụng và máy chủ:** GraphQL, một cách để ứng dụng hỏi đúng những trường dữ liệu nó cần.
- **Dịch vụ phía sau:** Zuul (cổng đón yêu cầu), Eureka (nơi các dịch vụ đăng ký để tìm thấy nhau), khung Spring Boot và các công nghệ khác.
- **Cơ sở dữ liệu:** EVCache, Cassandra, CockroachDB và các loại khác.
- **Truyền tin và dòng dữ liệu:** Apache Kafka và Flink. Bài nguồn viết "Fink"; đây có lẽ là lỗi gõ của Flink.
- **Lưu video:** S3 và Open Connect.
- **Xử lý dữ liệu:** Flink và Spark xử lý, Tableau vẽ biểu đồ, Redshift xử lý dữ liệu có cấu trúc trong kho dữ liệu.
- **CI/CD:** Jira, Confluence, PagerDuty, Jenkins, Gradle, Chaos Monkey, Spinnaker, Atlas (nguồn viết "Altas") và các công cụ khác.

Năm lớp nằm trên đường đi của một yêu cầu xem phim: ứng dụng, giao tiếp, dịch vụ phía sau, cơ sở dữ liệu và lưu video. Ba lớp đứng ngoài đường đi đó: truyền tin và dòng dữ liệu chuyển sự kiện giữa các dịch vụ, xử lý dữ liệu đọc lại dữ liệu đã sinh ra để phân tích, CI/CD đưa mã mới vào các dịch vụ. Cách chia này là của người biên soạn; bài nguồn chỉ xếp tám lớp, không nói lớp nào phục vụ lần xem.

## Giới hạn cần nhớ

Bài nguồn chỉ liệt kê tên công nghệ, không nói mỗi thứ dùng cho việc gì, dùng ở quy mô nào hay từ năm nào. Lời giải thích ngắn bên cạnh Zuul, Eureka và GraphQL, và việc Swift dành cho iPhone còn Kotlin cho Android, là của người biên soạn. Danh sách là ảnh chụp tại một thời điểm và có thể đã đổi.

## Nhìn hình thử trả lời

Một người bấm xem một bộ phim trên điện thoại. Theo hình, những lớp nào tham gia trả lời yêu cầu đó, và lớp nào thì không?

<details>
<summary>Xem đáp án</summary>

Ứng dụng di động gửi yêu cầu qua GraphQL tới các dịch vụ phía sau (qua Zuul), dịch vụ đọc cơ sở dữ liệu, rồi video được phát từ lớp lưu video. Ba lớp truyền tin và dòng dữ liệu, xử lý dữ liệu và CI/CD không nằm trên đường đi này: chúng chuyển sự kiện giữa các dịch vụ, làm việc trước (phát hành mã) hoặc sau (phân tích dữ liệu).

</details>

<details>
<summary>Xem sâu hơn: vì sao một công ty dùng nhiều công nghệ cùng lúc</summary>

- Mỗi lớp có yêu cầu khác nhau: cơ sở dữ liệu cho bộ nhớ đệm cần nhanh, kho dữ liệu cho phân tích cần quét được lượng lớn.
- Khi có hàng trăm đội, mỗi đội chọn công cụ hợp việc của mình, miễn là giao tiếp với nhau qua giao diện chung.
- Cái giá: nhiều công nghệ hơn thì cần nhiều người biết vận hành hơn.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/netflixs-overall-architecture.md): tám lớp và công nghệ của từng lớp.

Đã đọc nguồn ngày 2026-10-19. Tài liệu kỹ thuật của Netflix chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

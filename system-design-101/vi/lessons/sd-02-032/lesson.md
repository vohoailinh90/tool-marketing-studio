# Ngăn xếp công nghệ của Netflix

**Bài nguồn tổng hợp ngăn xếp công nghệ của Netflix thành tám mảng: di động và web, giao tiếp giữa giao diện và máy chủ, dịch vụ phía sau, cơ sở dữ liệu, truyền tin, lưu video, xử lý dữ liệu, và tích hợp và chuyển giao liên tục.**
Bài này đọc tám mảng theo đường đi của một lần bấm xem phim, rồi tới phần dữ liệu và phần phát hành đứng ngoài đường đi đó.

![Hai dải bước và một cột. Đường xem phim: ứng dụng di động viết bằng Swift và Kotlin, web dùng React; giao diện nói chuyện với máy chủ bằng GraphQL; dịch vụ phía sau dùng Zuul, Eureka và Spring Boot. Phía dữ liệu của đường đi: cơ sở dữ liệu EVCache, Cassandra và CockroachDB; video lưu trên S3 và Open Connect. Cột đứng ngoài đường đi: truyền tin bằng Kafka và Flink; xử lý dữ liệu bằng Flink, Spark, Tableau và Redshift; phát hành bằng Jenkins, Gradle, Spinnaker và Chaos Monkey.](../../diagrams/sd-02-032-main.svg)

## Từ viết tắt

- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, cách để ứng dụng mô tả đúng dữ liệu nó muốn lấy.
- **CI** (Continuous Integration) — tích hợp liên tục: mỗi thay đổi mã được ghép vào và kiểm tra tự động ngay.
- **CD** (Continuous Delivery) — chuyển giao liên tục: mã đã qua kiểm tra được đưa dần ra môi trường thật bằng công cụ tự động.

## Đọc hình

Bài nguồn nói nó tổng hợp từ nhiều bài blog kỹ thuật và dự án mã nguồn mở của Netflix, và mời người đọc báo lỗi nếu có chỗ sai.

**Đường đi của một lần bấm xem.**
- **Di động và web:** ứng dụng di động gốc viết bằng Swift và Kotlin; ứng dụng web dùng React.
- **Giao tiếp giao diện và máy chủ:** GraphQL.
- **Dịch vụ phía sau:** Zuul, Eureka, khung Spring Boot và các công nghệ khác.
- **Cơ sở dữ liệu:** EVCache, Cassandra, CockroachDB và các cơ sở dữ liệu khác.
- **Lưu video:** `S3` (kho lưu trữ tệp trên đám mây của Amazon) và Open Connect.

**Phần dữ liệu.**
- **Truyền tin và dòng dữ liệu:** Apache Kafka và Flink.
- **Xử lý dữ liệu:** Flink và Spark, rồi hiển thị bằng Tableau; Redshift dùng cho kho dữ liệu có cấu trúc.

**Phần phát hành.** Cho CI và CD, Netflix dùng nhiều công cụ như Jira, Confluence, PagerDuty, Jenkins, Gradle, Chaos Monkey, Spinnaker và Atlas.

## Giới hạn cần nhớ

Bài nguồn chỉ nêu tên công cụ, không nói mỗi công cụ làm gì ở Netflix, dùng ở quy mô nào hay có còn dùng không. Bài nguồn viết vài tên khác cách viết thường gặp (`ZUUL`, `EV cache`, `Fink`, `Altas`); bài này viết Zuul, EVCache, Flink và Atlas, theo cách đọc của người biên soạn. Vai trò của Open Connect và Chaos Monkey ở phần dưới là kiến thức chung, không từ bài nguồn.

## Nhìn hình thử trả lời

Một người bấm xem một bộ phim trên ứng dụng Netflix ở điện thoại. Theo hình, yêu cầu đó đi qua những mảng nào trước khi video phát, và mảng nào không tham gia trả lời ngay?

<details>
<summary>Xem đáp án</summary>

Ứng dụng di động (Swift hoặc Kotlin) hỏi máy chủ bằng GraphQL, qua các dịch vụ phía sau như Zuul và Eureka, đọc thông tin từ cơ sở dữ liệu như EVCache và Cassandra, rồi video được phát từ nơi lưu video (S3 và Open Connect). Truyền tin, xử lý dữ liệu và phần phát hành không tham gia trả lời ngay: chúng phân tích dữ liệu sau, hoặc đưa mã mới vào trước.

</details>

<details>
<summary>Xem sâu hơn: hai cái tên đáng nhớ</summary>

- Open Connect là mạng máy chủ của Netflix đặt gần nhà mạng, để video đi quãng ngắn tới người xem.
- Chaos Monkey cố ý tắt ngẫu nhiên máy chủ đang chạy, để kiểm tra hệ thống vẫn phục vụ được khi một phần hỏng.
- Cả hai cho thấy cùng một ý: ở quy mô lớn, hỏng hóc và khoảng cách là chuyện thường, nên phải thiết kế sẵn cho chúng.

Đây là kiến thức chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/netflixs-tech-stack.md): tám mảng và công cụ của từng mảng.

Đã đọc nguồn ngày 2026-10-19. Blog kỹ thuật của Netflix chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

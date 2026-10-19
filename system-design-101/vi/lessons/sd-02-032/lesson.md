# Ngăn xếp công nghệ của Netflix

**Bài nguồn tổng hợp ngăn xếp công nghệ của Netflix thành tám mảng: di động và web, giao tiếp giữa giao diện và máy chủ, dịch vụ phía sau, cơ sở dữ liệu, truyền tin, lưu video, xử lý dữ liệu, và tích hợp và chuyển giao liên tục.**
Danh sách đó chỉ là tên. Bài này dùng nó làm dữ liệu cho một phép thử của người biên soạn: nếu một công cụ ngừng chạy, người đang xem phim có thấy ngay không? Trả lời câu đó cho từng mảng cho thấy vì sao một công ty lớn giữ nhiều công cụ cho cùng một loại việc. Hình gom tám mảng thành ba nhóm theo loại việc; bài nguồn không nói mảng nào phục vụ một lần xem phim, nên cả cách gom lẫn phép thử đều là lập luận riêng.

![Ba nhóm thẻ. Ứng dụng và dịch vụ: ứng dụng di động viết bằng Swift và Kotlin, web dùng React; giao diện nói chuyện với máy chủ bằng GraphQL; dịch vụ phía sau dùng Zuul, Eureka và Spring Boot. Lưu dữ liệu: cơ sở dữ liệu EVCache, Cassandra và CockroachDB; video lưu trên S3 và Open Connect. Dữ liệu và phát hành: truyền tin bằng Kafka và Flink; xử lý dữ liệu bằng Flink, Spark, Tableau và Redshift; phát hành bằng Jenkins, Gradle, Spinnaker và Chaos Monkey. Khung cuối là phép thử của người biên soạn: ứng dụng, cổng hay Open Connect hỏng thì người xem thấy ngay; EVCache hỏng có thể chỉ chậm hơn; Kafka, Spark hay Jenkins hỏng thì thấy muộn hoặc không thấy.](../../diagrams/sd-02-032-main.svg)

## Từ viết tắt

- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, cách để ứng dụng mô tả đúng dữ liệu nó muốn lấy.
- **CI** (Continuous Integration) — tích hợp liên tục: mỗi thay đổi mã được ghép vào và kiểm tra tự động ngay.
- **CD** (Continuous Delivery) — chuyển giao liên tục: mã đã qua kiểm tra được đưa dần ra môi trường thật bằng công cụ tự động.
- **EV** (Ephemeral Volatile) — tạm thời, dễ mất: chữ EV trong tên EVCache, bộ nhớ đệm của Netflix; dữ liệu trong đó có thể mất và được nạp lại.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức để ghi và tìm lại nhanh; có trong tên CockroachDB.

## Đọc hình

Bài nguồn nói nó tổng hợp từ nhiều bài blog kỹ thuật và dự án mã nguồn mở của Netflix, và mời người đọc báo lỗi nếu có chỗ sai.

**Ứng dụng, dịch vụ và nơi lưu.**
- **Di động và web:** ứng dụng di động gốc viết bằng Swift và Kotlin; ứng dụng web dùng React.
- **Giao tiếp giao diện và máy chủ:** GraphQL.
- **Dịch vụ phía sau:** Zuul, Eureka, khung Spring Boot và các công nghệ khác.
- **Cơ sở dữ liệu:** EVCache, Cassandra, CockroachDB và các cơ sở dữ liệu khác.
- **Lưu video:** `S3` (kho lưu trữ tệp trên đám mây của Amazon) và Open Connect.

**Phần dữ liệu.**
- **Truyền tin và dòng dữ liệu:** Apache Kafka và Flink.
- **Xử lý dữ liệu:** Flink và Spark, rồi hiển thị bằng Tableau; Redshift dùng cho kho dữ liệu có cấu trúc.

**Phần phát hành.** Cho CI và CD, Netflix dùng nhiều công cụ như Jira, Confluence, PagerDuty, Jenkins, Gradle, Chaos Monkey, Spinnaker và Atlas.

## Thử lập luận: hỏng thì ai thấy?

Phần này là lập luận của người biên soạn, dựa trên vai trò thường gặp của mỗi công cụ, không phải trên bài nguồn; Netflix có thể dùng chúng khác đi.

**Phép thử.** Với mỗi công cụ, hỏi: nếu nó ngừng chạy lúc này, người đang xem phim nhận ra trong vài giây, nhận ra sau vài giờ, hay không nhận ra?

| Mảng | Nếu ngừng chạy | Người xem thấy khi nào |
|---|---|---|
| Ứng dụng, GraphQL, Zuul, Eureka | Yêu cầu từ ứng dụng không tới được dịch vụ | Ngay lập tức |
| Open Connect | Video không còn máy gần để lấy | Ngay, hoặc phim chậm và mờ hơn |
| EVCache | Đọc phải đi thẳng xuống cơ sở dữ liệu | Có thể chỉ thấy chậm hơn, nếu cơ sở dữ liệu chịu nổi |
| Kafka, Flink | Sự kiện xem phim chưa được xử lý | Sau vài giờ, ví dụ gợi ý phim cũ đi |
| Spark, Tableau, Redshift | Báo cáo và phân tích bị trễ | Không thấy |
| Jenkins, Gradle, Spinnaker | Chưa đưa được bản mới ra | Không thấy, bản đang chạy vẫn chạy |

**Điều rút ra.**
- Các mảng không cần cùng một mức sẵn sàng. Mảng ở dòng đầu phải chạy liên tục; mảng ở dòng cuối dừng một ngày thì người xem cũng không biết. Đó là một lý do để không dồn mọi việc vào một công cụ: công cụ nào gánh việc ở dòng đầu thì phải được chăm như dòng đầu.
- Ba cơ sở dữ liệu là ba câu trả lời khác nhau cho cùng câu hỏi. Theo hiểu biết chung, EVCache là bộ nhớ đệm, dữ liệu mất được thì nạp lại; Cassandra chia dữ liệu ra rất nhiều máy để ghi nhiều và vẫn chạy khi vài máy hỏng; CockroachDB giữ dữ liệu nhất quán giữa các máy, hợp với dữ liệu không được sai. Một cơ sở dữ liệu duy nhất phải chọn một trong ba ưu tiên đó cho mọi loại dữ liệu.
- Bộ nhớ đệm có hai mặt. EVCache làm đọc nhanh, nhưng nếu cơ sở dữ liệu phía sau chỉ chịu được lượng đọc khi có bộ nhớ đệm, mất bộ nhớ đệm sẽ kéo cơ sở dữ liệu sập theo, và dòng "chỉ thấy chậm hơn" thành "thấy ngay".
- Chaos Monkey là phép thử này làm thật: tắt máy chủ đang chạy để xem bảng trên có đúng không, thay vì đoán.

## Giới hạn cần nhớ

Bài nguồn chỉ nêu tên công cụ, không nói mỗi công cụ làm gì ở Netflix, dùng ở quy mô nào hay có còn dùng không. Bài nguồn viết vài tên khác cách viết thường gặp (`ZUUL`, `EV cache`, `Fink`, `Altas`); bài này viết Zuul, EVCache, Flink và Atlas, theo cách đọc của người biên soạn. Vai trò của từng công cụ trong phần *Thử lập luận* và phần dưới là kiến thức chung của người biên soạn, không từ bài nguồn.

## Nhìn hình thử trả lời

Giữa buổi tối đông người xem, EVCache ngừng chạy, còn Cassandra phía sau vẫn chạy. Theo phép thử ở trên, người đang xem phim sẽ thấy gì, và điều gì quyết định họ chỉ thấy chậm hay thấy lỗi?

<details>
<summary>Xem đáp án</summary>

Mọi lượt đọc trước đây do bộ nhớ đệm trả lời giờ đi thẳng xuống Cassandra. Nếu Cassandra chịu được lượng đọc đó, người xem chỉ thấy trang mở chậm hơn. Nếu nó chỉ chịu được khi phần lớn lượt đọc đã dừng ở bộ nhớ đệm, nó quá tải và người xem thấy lỗi ngay. Điều quyết định là phía sau còn dư bao nhiêu sức khi mất bộ nhớ đệm. Đây là lập luận của người biên soạn; bài nguồn chỉ nêu tên EVCache và Cassandra, không nói Netflix xếp chúng thế nào.

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

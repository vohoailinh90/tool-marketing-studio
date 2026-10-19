# Ngăn xếp công nghệ của Uber, từ ứng dụng tới DevOps

**Bài nguồn tổng hợp ngăn xếp công nghệ của Uber thành tám mảng: web, di động, lưới dịch vụ, dịch vụ, cơ sở dữ liệu, dữ liệu lớn, xử lý dữ liệu và DevOps; nhiều công cụ trong đó do chính Uber làm ra.**
Bài này đọc tám mảng theo đường đi của một yêu cầu đặt xe, rồi tới phần dữ liệu và phần phát hành đứng ngoài đường đi đó.

![Hai dải bước và một cột. Phía người dùng: web dùng Fusion, một framework React do Uber làm; di động dùng kiến trúc RIB, viết bằng Swift cho iOS và Java cho Android. Phía Uber: lưới dịch vụ Uber Gateway dựng trên NGINX, giao tiếp bằng gRPC và QUIC; dịch vụ dùng kho cấu hình Flipr, thư viện chỉ mục vị trí H3, uAct và Cadence; cơ sở dữ liệu giao dịch chủ yếu là DocStore trên MySQL. Cột đứng ngoài đường đi: dữ liệu lớn với Hadoop, Hudi và Pinot; xử lý dữ liệu với Hive, Spark, Kafka và Flink; phát hành với monorepo, Spinnaker và M3.](../../diagrams/sd-02-027-main.svg)

## Từ viết tắt

- **RIB** (Router, Interactor, Builder) — bộ định tuyến, bộ tương tác, bộ dựng: kiến trúc ứng dụng di động Uber làm, chia màn hình thành các khối có vai trò rõ.
- **VIPER** (View, Interactor, Presenter, Entity, Router) — một kiến trúc ứng dụng di động chia màn hình thành năm vai trò; theo nguồn, RIB dựa trên nó.
- **MVC** (Model, View, Controller) — kiến trúc chia ứng dụng thành dữ liệu, giao diện và phần điều khiển; kiến trúc quen thuộc mà Uber không chọn.
- **gRPC** (gRPC Remote Procedure Calls) — tên viết tắt đệ quy của một hệ thống gọi hàm từ xa, tức gọi một hàm chạy trên máy khác như gọi hàm trên máy mình.
- **QUIC** (Quick UDP Internet Connections) — một giao thức truyền dữ liệu chạy trên UDP, chở nhiều luồng dữ liệu trong một kết nối: mất một gói tin chỉ làm chậm luồng chứa gói đó, không chặn các luồng khác. Nó không hứa lúc nào cũng nhanh hơn, và có mạng chặn hẳn UDP.
- **UDP** (User Datagram Protocol) — giao thức gửi gói tin không cần bắt tay trước.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách các dịch vụ gọi nhau.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc; chữ SQL trong tên MySQL và PostgreSQL.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức để ghi và tìm lại nhanh; có trong tên AresDB và RocksDB.
- **DevOps** (DEVelopment and OPerationS) — phát triển và vận hành: cách làm gộp việc viết mã với việc phát hành và vận hành nó.
- **OLTP** (OnLine Transaction Processing) — xử lý giao dịch trực tuyến: phần cơ sở dữ liệu phục vụ các thao tác đọc ghi hằng ngày như đặt xe.

## Đọc hình

Bài nguồn nói nó tổng hợp từ nhiều bài blog kỹ thuật và dự án mã nguồn mở của Uber, và mời người đọc báo lỗi nếu có chỗ sai.

**Đường đi của một yêu cầu.**
- **Web:** Uber làm Fusion.js, một framework React hiện đại, và visualization.js cho các tình huống hiển thị bản đồ.
- **Di động:** Uber làm kiến trúc RIB đa nền tảng dựa trên VIPER thay cho MVC; viết bằng Swift cho iOS và Java cho Android.
- **Lưới dịch vụ:** Uber Gateway là lớp cấu hình động dựng trên NGINX. Máy khách và máy chủ nói chuyện bằng gRPC và QUIC; API được định nghĩa bằng Apache Thrift.
- **Dịch vụ:** kho cấu hình thống nhất Flipr (sau đổi tên), thư viện chỉ mục vị trí H3, Spring Boot cho dịch vụ Java, uAct cho kiến trúc hướng sự kiện, Cadence cho điều phối quy trình bất đồng bộ.
- **Cơ sở dữ liệu:** phần OLTP chủ yếu dùng DocStore nhất quán mạnh, chạy trên MySQL và PostgreSQL cùng bộ máy lưu trữ RocksDB.

**Phần dữ liệu.**
- **Dữ liệu lớn:** họ Hadoop; nguồn xếp Hudi và Parquet vào nhóm định dạng tệp, Alluxio làm bộ đệm; dữ liệu chuỗi thời gian lưu trong Pinot và AresDB.
- **Xử lý dữ liệu:** Hive, Spark và Marmaray, một khung nạp dữ liệu mã nguồn mở; truyền tin và dòng dữ liệu dùng Apache Kafka và Apache Flink.

**Phần phát hành.** Uber dùng một monorepo với môi trường phát triển đơn giản gọi là devpod; chuyển giao liên tục bằng Spinnaker của Netflix; số đo gửi tới uMetric, cảnh báo trên uMonitor, và M3 là cơ sở dữ liệu quan sát thống nhất.

## Giới hạn cần nhớ

Bài nguồn chỉ nêu tên và một dòng vai trò. Nó không nói mỗi công cụ dùng ở quy mô nào, từ năm nào, hay có còn dùng không; tên mới của Flipr cũng không được giải thích. Giải nghĩa RIB và QUIC ở phần viết tắt là kiến thức chung của người biên soạn. Cũng theo người biên soạn: chỉ Parquet là định dạng tệp; Hudi là lớp bảng đặt trên các tệp đó (thường là Parquet), lo việc cập nhật và ghi theo giao dịch, nên đừng coi hai thứ là cùng một loại.

## Nhìn hình thử trả lời

Một người mở ứng dụng Uber trên iPhone để đặt xe. Theo hình, yêu cầu đó đi qua những mảng nào, và mảng nào không tham gia trả lời ngay?

<details>
<summary>Xem đáp án</summary>

Ứng dụng iOS (kiến trúc RIB, viết bằng Swift) gửi yêu cầu qua Uber Gateway bằng gRPC hoặc QUIC, tới các dịch vụ phía sau, rồi tới DocStore. Dữ liệu lớn, xử lý dữ liệu và DevOps không tham gia trả lời ngay: chúng phân tích dữ liệu sau, hoặc đưa mã mới vào trước.

</details>

<details>
<summary>Xem sâu hơn: vì sao Uber tự làm nhiều công cụ</summary>

- Ở quy mô rất lớn, công cụ có sẵn đôi khi không đáp ứng được, hoặc không hợp với cách tổ chức nội bộ.
- Công cụ tự làm khớp với nhu cầu riêng, nhưng phải tự bảo trì lâu dài.
- Nhiều công cụ sau đó được mở mã nguồn, như H3 hay Cadence.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/uber-tech-stack.md): tám mảng và công cụ của từng mảng.

Đã đọc nguồn ngày 2026-10-19. Blog kỹ thuật của Uber chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

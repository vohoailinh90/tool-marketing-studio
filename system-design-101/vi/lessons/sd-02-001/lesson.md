# Figma mở rộng Postgres: ba bậc thang

**Khi một cơ sở dữ liệu không còn gánh nổi tải, người ta thường leo từng bậc: nâng máy và thêm bản sao đọc, rồi chia theo bảng, rồi chia theo hàng.** Bài lấy Figma làm ví dụ, theo cách một nguồn thứ cấp kể lại, và giữ riêng điều nguồn nói với điều bài giải thích thêm.

![Bốn khung dọc: bậc một giữ một cơ sở dữ liệu, nâng máy, thêm bản sao chỉ đọc và bộ gom kết nối, cái giá là mọi lệnh ghi vẫn qua một máy chính; bậc hai chia theo bảng, đưa bảng nặng sang cơ sở dữ liệu riêng, cái giá là hết ghép bảng bằng một lệnh; bậc ba chia theo hàng, rải các hàng của một bảng ra nhiều máy và thêm lớp định tuyến, cái giá là truy vấn xuyên nhiều mảnh khó hơn; quy tắc: bậc rẻ trước, chỉ leo tiếp khi bậc này hết đường.](../../diagrams/sd-02-001-main.svg)

## Từ viết tắt

- **RDS** (Relational Database Service) — dịch vụ cơ sở dữ liệu quan hệ do Amazon vận hành hộ: bạn thuê một máy chủ cơ sở dữ liệu đã cài sẵn thay vì tự quản máy; theo nguồn, Figma bắt đầu bằng một cơ sở dữ liệu như vậy.

## Đọc hình

**Bậc 1 — một máy, nhiều bản sao.** Cách rẻ nhất về công sức là giữ nguyên cấu trúc và làm nó khỏe hơn. Theo nguồn, Figma bắt đầu với một cơ sở dữ liệu lớn trên Amazon RDS, nâng lên cấu hình lớn nhất có sẵn, thêm nhiều *bản sao đọc* (read replica: bản chép của cơ sở dữ liệu chính, chỉ nhận truy vấn đọc) để chia bớt việc đọc, và đặt PgBouncer, một *bộ gom kết nối*, để số kết nối tăng lên không đè nặng cơ sở dữ liệu. Giới hạn: mọi lệnh ghi vẫn đi qua một máy chính, và máy mạnh nhất cũng có trần.

**Bậc 2 — chia theo bảng (vertical partitioning).** Những bảng nhiều việc nhất (nguồn nêu bảng tệp và bảng tổ chức) được chuyển sang cơ sở dữ liệu riêng, mỗi nơi có máy chính và bộ gom kết nối của mình. Cái giá: ứng dụng phải biết bảng nào nằm ở đâu, và một lệnh ghép dữ liệu hai bảng (JOIN) hay một giao dịch trải qua cả hai không còn là một lệnh đơn giản.

**Bậc 3 — chia theo hàng (horizontal partitioning).** Khi chính một bảng quá lớn (nguồn kể về bảng hàng terabyte với hàng tỷ hàng, việc dọn `VACUUM` thành vấn đề và tốc độ đọc ghi đĩa chạm trần của RDS thời đó), các hàng của cùng một bảng được rải ra nhiều cơ sở dữ liệu vật lý, mỗi nơi giữ một *mảnh*. Cần một lớp định tuyến (nguồn gọi là DBProxy) nhận truy vấn rồi gửi tới đúng mảnh.

## Giới hạn cần nhớ

Nguồn là bản tóm tắt ngắn, hầu như không có số đo, và bài gốc của Figma chưa được mở để đối chiếu; đừng xem đây là mô tả đầy đủ cách Figma làm. Ba bậc là thứ tự phổ biến chứ không phải luật: nhiều hệ thống ở lại bậc 1 hoặc 2 rất lâu, vì chia sớm là mua phức tạp sớm: mất JOIN, giao dịch xuyên mảnh khó, truy vấn không mang khóa chia phải hỏi mọi mảnh, và đổi cách chia về sau tốn công. Cũng đừng nhầm tên: nguồn gọi bậc 3 là *horizontal partitioning*, nhiều tài liệu gọi việc rải hàng ra nhiều máy là *sharding*, còn "partitioning" trong tài liệu Postgres là chia một bảng thành nhiều phần *trong cùng một máy chủ*.

## Nhìn hình thử trả lời

Ứng dụng của bạn chậm vì quá nhiều lượt đọc, còn ghi thì ít. Bạn thử bậc nào trước? Và nếu người dùng vừa lưu xong đã tải lại trang, mà trang đọc từ bản sao, họ có thể thấy gì?

<details>
<summary>Xem đáp án</summary>

Bậc 1: thêm bản sao đọc và bộ gom kết nối, vì thứ cần chia là việc đọc, chưa cần đổi cách tổ chức dữ liệu. Bản sao nhận dữ liệu từ máy chính sau một khoảng trễ nên người dùng có thể thấy dữ liệu cũ. Cách thường dùng để tránh: ngay sau một lượt ghi, đọc từ máy chính trong một khoảng ngắn, hoặc chỉ đưa sang bản sao những truy vấn chấp nhận được dữ liệu hơi cũ.

</details>

<details>
<summary>Xem sâu hơn</summary>

Các điểm dưới đây được người biên soạn chạy thử trên Postgres 16.15 chạy cục bộ ngày 2026-10-16; Amazon RDS, PgBouncer và DBProxy chưa được chạy thử.

- **Vì sao cần bộ gom kết nối:** Postgres dùng một tiến trình hệ điều hành cho mỗi kết nối của client. Mở 20 phiên cùng lúc cho ra đúng 20 tiến trình phục vụ, so với 0 lúc nghỉ. Bộ gom kết nối cho nhiều kết nối của ứng dụng dùng chung một số ít kết nối thật tới cơ sở dữ liệu.
- **Bản sao chỉ đọc và độ trễ:** ghi vào bản sao bị từ chối với `cannot execute INSERT in a read-only transaction`. Cấu hình mặc định không bắt máy chính chờ bản sao, nên bản sao có thể chậm hơn. Khi tạm dừng việc áp dụng thay đổi ở bản sao để dựng tình huống trễ, máy chính có 2 hàng còn bản sao vẫn thấy 1; cho chạy lại thì bản sao có đủ 2. Đây là tình huống dựng, không phải phép đo độ trễ thật.
- **Không ghép xuyên cơ sở dữ liệu:** truy vấn bảng của một cơ sở dữ liệu khác bị từ chối với `cross-database references are not implemented`, trong khi hai bảng cùng một cơ sở dữ liệu ghép bình thường. Vì thế chia theo bảng thành hai cơ sở dữ liệu làm mất phép ghép bằng một lệnh.
- **Dọn dẹp:** khi cập nhật một hàng, Postgres giữ cả phiên bản cũ cho tới khi dọn. Với 200.000 hàng, cập nhật mỗi hàng một lần cho ra 200.000 phiên bản chết và tệp dữ liệu to gấp đôi (từ hơn 7 lên hơn 14 megabyte); sau `VACUUM` số phiên bản chết về 0 nhưng tệp không nhỏ lại, chỗ trống chỉ để dùng lại. Bảng càng lớn thì việc dọn càng tốn.
- **Chia bảng trong một máy:** `PARTITION BY HASH` tạo các bảng con trong cùng một cơ sở dữ liệu trên cùng một máy chủ; nó không rải dữ liệu ra nhiều máy.

Con số trong thử nghiệm chỉ minh họa; hiệu năng thật phụ thuộc phần cứng, cấu hình và tải.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/100x-postgres-scaling-at-figma.md): ba bậc mở rộng của Figma, các bảng được nêu và lý do chia theo hàng.
- [PostgreSQL: Architectural Fundamentals](https://www.postgresql.org/docs/current/tutorial-arch.html) và [Managing Databases](https://www.postgresql.org/docs/current/managing-databases.html): tiến trình cho mỗi kết nối, một kết nối chỉ truy cập một cơ sở dữ liệu.
- [PostgreSQL: Log-Shipping Standby Servers](https://www.postgresql.org/docs/current/warm-standby.html) và [High Availability, Load Balancing, and Replication](https://www.postgresql.org/docs/current/high-availability.html): bản sao chỉ đọc.
- [PostgreSQL: Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html) và [Routine Vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html).
- [PgBouncer](https://www.pgbouncer.org/): bộ gom kết nối cho Postgres.

Đã đọc body nguồn ByteByteGo ghim ngày 2026-10-16; hành vi của Postgres nêu ở mục "Xem sâu hơn" được chạy thử cục bộ cùng ngày. Bài gốc của Figma, tài liệu PostgreSQL và PgBouncer chưa được mở để đối chiếu (máy biên soạn không truy cập được các trang đó). Bài viết và hình được thiết kế độc lập; chưa thử với người học.

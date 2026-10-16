# Figma mở rộng Postgres: ba bậc thang

**Khi một cơ sở dữ liệu không còn gánh nổi tải, người ta thường leo từng bậc: nâng máy và thêm bản sao đọc, rồi chia theo bảng, rồi chia theo hàng.** Bài lấy Figma làm ví dụ, theo cách một nguồn thứ cấp kể lại, và giữ riêng điều nguồn nói với điều bài giải thích thêm.

![Bốn khung dọc: bậc một giữ một cơ sở dữ liệu, nâng máy, thêm bản sao chỉ đọc và bộ gom kết nối, cái giá là mọi lệnh ghi vẫn qua một máy chính; bậc hai chia theo bảng, đưa bảng nặng sang cơ sở dữ liệu riêng, cái giá là ghép bảng giữa hai bên phải đi vòng; bậc ba chia theo hàng, rải các hàng của một bảng ra nhiều máy và thêm lớp định tuyến, cái giá là truy vấn xuyên nhiều mảnh khó hơn; quy tắc: bậc rẻ trước, chỉ leo tiếp khi bậc này hết đường.](../../diagrams/sd-02-001-main.svg)

## Từ viết tắt

- **RDS** (Relational Database Service) — dịch vụ cơ sở dữ liệu quan hệ do Amazon vận hành hộ: bạn thuê một máy chủ cơ sở dữ liệu đã cài sẵn thay vì tự quản máy; theo nguồn, Figma bắt đầu bằng một cơ sở dữ liệu như vậy.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức để ghi và tìm lại nhanh; có trong tên DBProxy, lớp định tuyến mà nguồn nêu.

## Đọc hình

**Bậc 1 — một máy, nhiều bản sao.** Cách rẻ nhất về công sức là giữ nguyên cấu trúc và làm nó khỏe hơn. Theo nguồn, Figma bắt đầu với một cơ sở dữ liệu lớn trên Amazon RDS, nâng lên cấu hình lớn nhất có sẵn, thêm nhiều *bản sao đọc* (read replica: bản chép của cơ sở dữ liệu chính, chỉ nhận truy vấn đọc) để chia bớt việc đọc, và đặt PgBouncer, một *bộ gom kết nối*, để số kết nối tăng lên không đè nặng cơ sở dữ liệu. Giới hạn: mọi lệnh ghi vẫn đi qua một máy chính, và máy mạnh nhất cũng có trần.

**Bậc 2 — chia theo bảng (vertical partitioning).** Những bảng nhiều việc nhất (nguồn nêu bảng tệp và bảng tổ chức) được chuyển sang cơ sở dữ liệu riêng, mỗi nơi có máy chính và bộ gom kết nối của mình. Cái giá: ứng dụng phải biết bảng nào nằm ở đâu, và việc ghép dữ liệu hai bảng (JOIN) hay chạy một giao dịch trải qua cả hai không còn đơn giản như khi chúng chung một cơ sở dữ liệu: Postgres không cho gọi thẳng tên bảng của cơ sở dữ liệu khác, nên phải đi qua một cầu nối hoặc ghép ở phía ứng dụng.

**Bậc 3 — chia theo hàng (horizontal partitioning).** Khi chính một bảng quá lớn (nguồn kể về bảng hàng terabyte với hàng tỷ hàng, việc dọn `VACUUM` thành vấn đề và tốc độ đọc ghi đĩa chạm trần của RDS thời đó), các hàng của cùng một bảng được rải ra nhiều cơ sở dữ liệu vật lý, mỗi nơi giữ một *mảnh*. Cần một lớp định tuyến (nguồn gọi là DBProxy) nhận truy vấn rồi gửi tới đúng mảnh.

## Giới hạn cần nhớ

Nguồn là bản tóm tắt ngắn, hầu như không có số đo, và bài gốc của Figma chưa được mở để đối chiếu; đừng xem đây là mô tả đầy đủ cách Figma làm. Ba bậc là thứ tự phổ biến chứ không phải luật: nhiều hệ thống ở lại bậc 1 hoặc 2 rất lâu, vì chia sớm là mua phức tạp sớm: ghép bảng và giao dịch xuyên cơ sở dữ liệu khó hơn, truy vấn không mang khóa chia phải hỏi mọi mảnh, và đổi cách chia về sau tốn công. Cũng đừng nhầm tên: nguồn gọi bậc 3 là *horizontal partitioning*, nhiều tài liệu gọi việc rải hàng ra nhiều máy là *sharding*, còn "partitioning" trong tài liệu Postgres là chia một bảng thành các *partition*: thường là bảng cục bộ trong cùng một máy chủ, nhưng một partition cũng có thể là bảng ngoài trỏ sang máy khác (xem mục "Xem sâu hơn"), nên chỉ riêng từ này chưa cho biết dữ liệu nằm ở đâu.

## Nhìn hình thử trả lời

Ứng dụng của bạn chậm vì quá nhiều lượt đọc, còn ghi thì ít. Bạn thử bậc nào trước? Và nếu người dùng vừa lưu xong đã tải lại trang, mà trang đọc từ bản sao, họ có thể thấy gì?

<details>
<summary>Xem đáp án</summary>

Bậc 1: thêm bản sao đọc và bộ gom kết nối, vì thứ cần chia là việc đọc, chưa cần đổi cách tổ chức dữ liệu. Bản sao thường nhận thay đổi chậm hơn máy chính một chút (mặc định máy chính không chờ bản sao), nên người dùng có thể thấy dữ liệu cũ. Cách thường dùng để tránh: ngay sau một lượt ghi, đọc từ máy chính trong một khoảng ngắn, hoặc chỉ đưa sang bản sao những truy vấn chấp nhận được dữ liệu hơi cũ.

</details>

<details>
<summary>Xem sâu hơn</summary>

Các điểm dưới đây được người biên soạn chạy thử trên Postgres 16.15 chạy cục bộ ngày 2026-10-16; Amazon RDS, PgBouncer và DBProxy chưa được chạy thử.

- **Vì sao cần bộ gom kết nối:** Postgres dùng một tiến trình hệ điều hành cho mỗi kết nối của client. Mở 20 phiên cùng lúc cho ra đúng 20 tiến trình phục vụ, so với 0 lúc nghỉ. Bộ gom kết nối cho nhiều kết nối của ứng dụng dùng chung một số ít kết nối thật tới cơ sở dữ liệu.
- **Bản sao chỉ đọc và độ trễ:** ghi vào bản sao bị từ chối với `cannot execute INSERT in a read-only transaction`. Cấu hình mặc định không bắt máy chính chờ bản sao, nên bản sao có thể chậm hơn. Khi tạm dừng việc áp dụng thay đổi ở bản sao để dựng tình huống trễ, máy chính có 2 hàng còn bản sao vẫn thấy 1; cho chạy lại thì bản sao có đủ 2. Đây là tình huống dựng, không phải phép đo độ trễ thật.
- **Ghép xuyên cơ sở dữ liệu:** gọi thẳng tên bảng của một cơ sở dữ liệu khác bị từ chối với `cross-database references are not implemented`, trong khi hai bảng cùng một cơ sở dữ liệu ghép bình thường. Có đường vòng: với tiện ích mở rộng `postgres_fdw` (hoặc `dblink`), một câu lệnh vẫn ghép được bảng của cơ sở dữ liệu khác; kế hoạch thực thi lúc đó có bước `Foreign Scan`, tức dữ liệu được lấy qua một kết nối thay vì đọc trực tiếp. Vì vậy chia theo bảng không làm phép ghép bất khả thi, mà bắt nó đi qua cầu nối; theo suy luận của bài, việc đó thêm một chặng và thêm chỗ để hỏng so với ghép trong cùng cơ sở dữ liệu.
- **Dọn dẹp:** khi cập nhật một hàng, Postgres giữ cả phiên bản cũ cho tới khi dọn. Với 200.000 hàng, cập nhật mỗi hàng một lần cho ra 200.000 phiên bản chết và tệp dữ liệu to gấp đôi (từ hơn 7 lên hơn 14 megabyte); sau `VACUUM` số phiên bản chết về 0 nhưng tệp không nhỏ lại trong thử nghiệm này: `VACUUM` thường chỉ đánh dấu chỗ trống để dùng lại. Bảng càng lớn thì việc dọn thường càng tốn.
- **Partition và vị trí của dữ liệu:** `PARTITION BY HASH` (hay `LIST`) chia một bảng thành các bảng con. Với bảng con thường, chúng nằm trong cùng một cơ sở dữ liệu trên cùng một máy chủ. Nhưng một partition có thể là bảng ngoài qua `postgres_fdw`: thử với một cụm Postgres thứ hai làm "máy khác", `INSERT` vào bảng cha đưa đúng các hàng sang máy kia (đếm trực tiếp ở máy đó thấy 2 hàng) và kế hoạch có bước `Foreign Scan`. Vì vậy partition là cách chia một bảng thành nhiều phần; phần nào nằm trên máy nào là tùy từng partition.

Con số trong thử nghiệm chỉ minh họa; hiệu năng thật phụ thuộc phần cứng, cấu hình và tải.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/100x-postgres-scaling-at-figma.md): ba bậc mở rộng của Figma, các bảng được nêu và lý do chia theo hàng.
- [PostgreSQL: Architectural Fundamentals](https://www.postgresql.org/docs/current/tutorial-arch.html) và [Managing Databases](https://www.postgresql.org/docs/current/managing-databases.html): tiến trình cho mỗi kết nối, một kết nối chỉ truy cập một cơ sở dữ liệu.
- [PostgreSQL: Log-Shipping Standby Servers](https://www.postgresql.org/docs/current/warm-standby.html) và [High Availability, Load Balancing, and Replication](https://www.postgresql.org/docs/current/high-availability.html): bản sao chỉ đọc.
- [PostgreSQL: Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html) và [Routine Vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html).
- [PgBouncer](https://www.pgbouncer.org/): bộ gom kết nối cho Postgres.

Đã đọc body nguồn ByteByteGo ghim ngày 2026-10-16; hành vi của Postgres nêu ở mục "Xem sâu hơn" được chạy thử cục bộ cùng ngày. Bài gốc của Figma, tài liệu PostgreSQL và PgBouncer chưa được mở để đối chiếu (máy biên soạn không truy cập được các trang đó). Bài viết và hình được thiết kế độc lập; chưa thử với người học.

# Mười cơ sở dữ liệu "mã nguồn mở": đọc giấy phép của từng cái

**Mã nguồn công khai trên mạng chưa chắc là mã nguồn mở; điều quyết định là giấy phép.** Nguồn liệt kê mười cơ sở dữ liệu mã nguồn mở phổ biến nhất, xếp theo mức độ được dùng và được biết tới. Bài này mở tệp giấy phép ở đầu nhánh chính trên GitHub của từng dự án (ngày 2026-10-18) và tra xem giấy phép đó có được OSI duyệt là mã nguồn mở không, theo danh sách giấy phép SPDX. Kết quả: sáu được, ba không, một không cần giấy phép.

![Theo tệp giấy phép ở nhánh chính của từng dự án, đọc ngày 18/10/2026. Khung một, giấy phép được OSI duyệt theo danh sách SPDX: MySQL và MariaDB dùng GPL phiên bản 2; Neo4j dùng GPL phiên bản 3; PostgreSQL dùng giấy phép PostgreSQL; Cassandra dùng Apache 2.0; Redis 8 cho chọn một trong ba giấy phép, trong đó có AGPL phiên bản 3. Khung hai, không phải giấy phép mã nguồn mở: MongoDB dùng SSPL, SPDX ghi không được OSI duyệt; Couchbase dùng BSL 1.1, chuyển sang Apache 2.0 từ ngày 1 tháng 3 năm 2029; CockroachDB cần khóa giấy phép để chạy thật. Khung ba, hai trường hợp riêng: SQLite thuộc phạm vi công cộng, không cần giấy phép; Redis 7.2 trở về trước dùng BSD 3 điều khoản.](../../diagrams/sd-04-030-main.svg)

## Từ viết tắt

- **OSI** (Open Source Initiative) — Sáng kiến Nguồn mở: tổ chức giữ định nghĩa "mã nguồn mở" và duyệt giấy phép nào đạt định nghĩa đó.
- **SPDX** (Software Package Data eXchange) — chuẩn trao đổi dữ liệu gói phần mềm: có một danh sách giấy phép, mỗi giấy phép một mã ngắn và một cờ cho biết OSI đã duyệt chưa.
- **GPL** (General Public License) — giấy phép công cộng chung: cho dùng, sửa, phân phối, nhưng ai phân phối bản sửa phải công bố mã của bản sửa theo cùng giấy phép.
- **AGPL** (Affero General Public License) — bản GPL mở rộng: điều kiện công bố mã áp dụng cả khi phần mềm chỉ được chạy cho người khác dùng qua mạng.
- **SSPL** (Server Side Public License) — giấy phép công cộng phía máy chủ của MongoDB: ai cung cấp phần mềm như một dịch vụ phải công bố mã của cả hệ thống chạy dịch vụ đó.
- **BSL** (Business Source License) — giấy phép mã nguồn kinh doanh: mã xem được nhưng dùng bị giới hạn, tới một ngày định trước thì chuyển sang một giấy phép mở.
- **RSAL** (Redis Source Available License) — giấy phép mã nguồn công khai của Redis: cho xem và dùng mã nhưng có giới hạn, không phải giấy phép mã nguồn mở.
- **BSD** (Berkeley Software Distribution) — tên một nhóm giấy phép rất thoáng, gần như chỉ yêu cầu giữ lời ghi bản quyền.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; có trong tên MySQL, PostgreSQL và SQLite.

## Đọc hình

1. **Được OSI duyệt.** MySQL (kèm vài quyền bổ sung của Oracle) và MariaDB dùng GPL phiên bản 2; Neo4j dùng GPL phiên bản 3 cho mã trong kho; PostgreSQL có giấy phép riêng mang tên nó, rất thoáng; Cassandra dùng Apache 2.0. Redis từ bản 8 cho người dùng chọn một trong ba: RSAL phiên bản 2, SSPL phiên bản 1 hoặc AGPL phiên bản 3. Chỉ lựa chọn AGPL được OSI duyệt, nhưng một lựa chọn là đủ để dùng Redis như mã nguồn mở.
2. **Không phải giấy phép mã nguồn mở.** MongoDB dùng SSPL; SPDX ghi SSPL không được OSI duyệt. Couchbase (kho `kv_engine`, một phần của Couchbase Server 8.0) dùng BSL 1.1: được chạy thật nhưng không được gói vào sản phẩm hay dịch vụ thu phí (kể cả dịch vụ cơ sở dữ liệu), và tới ngày 2029-03-01 thì chuyển sang Apache 2.0. CockroachDB dùng giấy phép riêng: chạy thật cần khóa giấy phép, gửi dữ liệu đo về nhà phát triển, và chỉ được dùng không khóa cho việc không phải sản xuất.
3. **Hai trường hợp riêng.** SQLite thuộc phạm vi công cộng: tác giả đã từ bỏ bản quyền, nên không cần giấy phép. Redis bản 7.2 trở về trước vẫn theo giấy phép BSD 3 điều khoản.

## Giới hạn cần nhớ

Giấy phép đổi theo thời gian: Redis và CockroachDB từng là mã nguồn mở rồi đổi, Couchbase sẽ đổi vào năm 2029. Bài đọc tệp ở đầu nhánh chính, không đọc giấy phép của từng bản phát hành, nên bản bạn đang dùng có thể theo giấy phép cũ. Danh sách "mười cái phổ biến nhất" là của nguồn, không có số liệu kèm theo. Bài không phải tư vấn pháp lý: trước khi dựng sản phẩm thu phí trên một cơ sở dữ liệu, đọc chính văn bản giấy phép của bản bạn dùng.

## Nhìn hình thử trả lời

Bạn định mở một dịch vụ "cơ sở dữ liệu được quản lý" thu phí, chạy bản mới nhất của MongoDB, Couchbase hoặc PostgreSQL cho khách. Với cái nào bạn cần đọc kỹ giấy phép trước nhất, và vì sao?

<details>
<summary>Xem đáp án</summary>

MongoDB và Couchbase. SSPL đòi người cung cấp phần mềm như một dịch vụ phải công bố mã của cả hệ thống chạy dịch vụ; BSL của Couchbase cấm đem phần mềm làm dịch vụ cơ sở dữ liệu thu phí cho tới ngày chuyển giấy phép.
PostgreSQL dùng giấy phép thoáng, chỉ yêu cầu giữ lời ghi bản quyền; đó là lý do nhiều dịch vụ đám mây cung cấp PostgreSQL.

</details>

<details>
<summary>Xem sâu hơn: tự đọc giấy phép</summary>

Không cần tải cả kho mã để đọc một tệp giấy phép. Với Git:

```bash
git clone --depth 1 --filter=blob:none --no-checkout <địa chỉ kho trên GitHub> kho
cd kho && git ls-tree --name-only HEAD | grep -i -E "licen|copying|copyright"
git checkout HEAD -- LICENSE        # thay bằng tên tệp vừa thấy
git rev-parse HEAD                  # ghi lại commit đã đọc
```

Cờ "OSI duyệt" lấy từ tệp `json/licenses.json` của kho danh sách giấy phép SPDX (bản 3.29.0): `GPL-2.0-only`, `GPL-3.0-only`, `AGPL-3.0-only`, `Apache-2.0`, `PostgreSQL` và `BSD-3-Clause` mang cờ duyệt; `SSPL-1.0` và `BUSL-1.1` không. RSAL và giấy phép của CockroachDB không có trong danh sách.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-10-most-popular-open-source-databases.md): danh sách mười cơ sở dữ liệu.
- Tệp giấy phép, mỗi tệp tại commit đầu nhánh chính ngày 2026-10-18, đọc từ bản clone nông: [MySQL](https://github.com/mysql/mysql-server/blob/3b99be40f8a31d9396cad10accfd3ba51647d613/LICENSE), [PostgreSQL](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/COPYRIGHT) (nhánh `REL_16_STABLE`), [MariaDB](https://github.com/MariaDB/server/blob/327437ade1d6dc6e4e57a6f1723b4abe4ac6c4b4/COPYING), [Cassandra](https://github.com/apache/cassandra/blob/95b178a141824a0414c4add9b5ab87eaa1ca13bf/LICENSE.txt), [Neo4j](https://github.com/neo4j/neo4j/blob/54a7dcf7c2501b31866199143364c5332da8936f/LICENSE.txt), [SQLite](https://github.com/sqlite/sqlite/blob/43a48f77585a88940c727f33682151418f544059/LICENSE.md), [CockroachDB](https://github.com/cockroachdb/cockroach/blob/d30c905fff79ef825adc96bcc647f1872a90f2ff/LICENSE), [Redis](https://github.com/redis/redis/blob/5e332cabd547d272783cf233a34c81dcb9ea44b3/LICENSE.txt), [MongoDB](https://github.com/mongodb/mongo/blob/9c35392dd534df818bfa6527ef3dcd94cce7630e/LICENSE-Community.txt), [Couchbase `kv_engine`](https://github.com/couchbase/kv_engine/blob/fc2d813286da971ce34eefc19fa6979f0d72df69/licenses/BSL-Couchbase.txt).
- [SPDX — danh sách giấy phép, bản 3.29.0](https://github.com/spdx/license-list-data/blob/31ba1a50e5397e00a304dbadc76531740e89ee48/json/licenses.json): cờ `isOsiApproved` của từng giấy phép. Trang của OSI không mở được, nên bài dựa vào cờ này.

Đọc ngày 2026-10-18. Bài không đánh giá chất lượng hay độ phổ biến của các hệ, và không phải tư vấn pháp lý. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

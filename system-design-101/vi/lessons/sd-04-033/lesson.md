# Cây chọn cơ sở dữ liệu: tự dựng cây của bạn, hỏi ràng buộc cứng trước

**Một cây chọn cơ sở dữ liệu tốt hỏi điều không thể thương lượng trước, rồi mới hỏi điều tiện.** Nguồn kể iQIYI, một trang video trực tuyến lớn, dùng cùng lúc khoảng mười hệ, từ cơ sở dữ liệu quan hệ, kho trong bộ nhớ tới hệ phân tích dữ liệu lớn, và chọn bằng các cây quyết định. Cây của họ nằm trong ảnh của nguồn, bài này không dùng. Thay vào đó, bài dựng một cây riêng với các hệ trong danh sách ấy, mỗi lá ghi đúng điều mà README của chính hệ đó tự nói, và thử câu hỏi đầu tiên trên Redis.

![Ba khung dọc. Khung một, ba câu hỏi về ràng buộc, theo thứ tự: dữ liệu mất được không, mất được như bộ đệm hay phiên thì Redis trong bộ nhớ, không thì hỏi tiếp; có cần giao dịch nhiều dòng không, có thì cơ sở dữ liệu quan hệ, không thì chọn theo kiểu câu hỏi; dữ liệu có vừa một máy không, vừa thì MySQL, không thì SQL phân tán như TiDB chạy trên TiKV. Khung hai, không cần giao dịch thì theo kiểu câu hỏi: tổng hợp trên kho rất lớn dùng Hive hoặc Impala; bản ghi dạng tài liệu dùng Couchbase hoặc MongoDB; quan hệ giữa các đối tượng dùng cơ sở dữ liệu đồ thị. Khung ba, thử câu một với Redis 7.0: cấu hình mặc định, ghi 50 khóa rồi tắt đột ngột thì còn 0 khóa; bật nhật ký ghi thì còn đủ 50.](../../diagrams/sd-04-033-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; có trong tên MySQL.
- **ACID** (Atomicity, Consistency, Isolation, Durability) — bốn tính chất của một giao dịch đáng tin: làm trọn hoặc không làm, giữ dữ liệu hợp lệ, các giao dịch không lẫn vào nhau, đã ghi thì không mất.
- **HTAP** (Hybrid Transactional/Analytical Processing) — xử lý lai giao dịch và phân tích: một hệ chạy được cả hai loại việc trên cùng dữ liệu.
- **NoSQL** (Not only SQL) — tên chung cho các cơ sở dữ liệu không theo mô hình bảng quan hệ, như kho tài liệu hay kho khóa–giá trị.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức để ghi và tìm lại nhanh; có trong tên TiDB, MongoDB và TokuDB.
- **KV** (Key-Value) — khóa–giá trị: kiểu lưu mỗi giá trị dưới một khóa và lấy lại bằng đúng khóa đó; có trong tên TiKV.

## Đọc hình

1. **Mất được không?** Câu này đứng đầu vì nó loại nhanh nhất. Phép thử chạy ngày 2026-10-18 với Redis 7.0.15: với cấu hình mặc định, ghi 50 khóa, chờ hơn một giây rồi tắt tiến trình đột ngột (`kill -9`); khởi động lại thì còn 0 khóa. Lý do nằm trong tệp cấu hình mẫu: mặc định Redis chỉ chụp dữ liệu xuống đĩa sau 3.600 giây nếu có ít nhất 1 thay đổi, sau 300 giây nếu có 100, sau 60 giây nếu có 10.000; nhật ký ghi (`appendonly`) mặc định tắt. Bật `appendonly yes` với `appendfsync everysec` thì sau cùng phép thử còn đủ 50 khóa; tệp cấu hình nói chế độ này có thể mất khoảng một giây ghi khi mất điện.
2. **Cần giao dịch trên nhiều dòng?** Chuyển tiền, giữ chỗ, trừ kho cần giao dịch ACID: cơ sở dữ liệu quan hệ.
3. **Vừa một máy không?** Vừa thì MySQL. Không vừa thì cần SQL phân tán: README của TiDB tự mô tả là cơ sở dữ liệu SQL phân tán, giao dịch ACID qua nhiều máy, tương thích MySQL 8.0, có hai cách lưu (TiKV theo dòng, TiFlash theo cột) cho kiểu HTAP. TiKV là kho khóa–giá trị phân tán có giao dịch.
4. **Không cần giao dịch: theo kiểu câu hỏi.** Hive đọc, ghi và quản lý tập dữ liệu lớn trên kho phân tán bằng SQL; Impala chạy câu SQL phân tán trên dữ liệu cỡ petabyte. Bản ghi dạng tài liệu thì Couchbase hay MongoDB; quan hệ giữa các đối tượng thì cơ sở dữ liệu đồ thị (nguồn nêu HiGraph). Cả nhánh này là những hệ mà nguồn xếp vào NoSQL hoặc dữ liệu lớn.

## Giới hạn cần nhớ

Cây này là của người biên soạn, không phải cây của iQIYI, và không có lá nào là "đúng" cho mọi nhóm: một nhóm chưa ai vận hành được TiDB thì "không vừa một máy" có thể nên trả lời bằng chia shard MySQL trước. Phép thử Redis chỉ có một máy và một kiểu tắt đột ngột. Bài chưa kiểm TokuDB hay HiGraph, chỉ nêu theo nguồn.

## Nhìn hình thử trả lời

Giỏ hàng của một trang bán hàng: khách bỏ hàng vào, vài ngày sau mới thanh toán. Đi qua cây thế nào, và câu hỏi đầu tiên có một đáp án duy nhất không?

<details>
<summary>Xem đáp án</summary>

Câu đầu không có đáp án sẵn: phải hỏi người làm sản phẩm. Nếu mất giỏ hàng chỉ làm khách phiền (họ thêm lại được), có thể giữ ở Redis, nhưng nên bật nhật ký ghi: phép thử cho thấy cấu hình mặc định mất sạch 50 khóa vừa ghi khi tiến trình chết đột ngột.
Nếu giỏ hàng gắn với giữ hàng trong kho hay giá đã hứa, thì mất là sai, và việc trừ kho lúc thanh toán cần giao dịch: đi tiếp câu hai, sang cơ sở dữ liệu quan hệ. Câu ba chỉ hỏi khi lượng dữ liệu thật sự vượt một máy.

</details>

<details>
<summary>Xem sâu hơn: lệnh của phép thử Redis</summary>

```bash
try() {                                   # $@: tùy chọn thêm cho redis-server, dùng ở cả hai lần khởi động
  d=$(mktemp -d)                          # một thư mục trống mới cho mỗi lần thử
  redis-server --port 6391 --dir "$d" --daemonize yes "$@"; sleep 0.5
  for i in $(seq 1 50); do redis-cli -p 6391 set k$i v$i > /dev/null; done
  echo "trước: $(redis-cli -p 6391 dbsize)"
  pid=$(redis-cli -p 6391 info server | grep process_id | cut -d: -f2 | tr -d '\r')
  sleep 1.5; kill -9 "$pid"; sleep 0.5
  redis-server --port 6391 --dir "$d" --daemonize yes "$@"; sleep 0.5
  echo "sau khi khởi động lại: $(redis-cli -p 6391 dbsize)"
  redis-cli -p 6391 shutdown nosave > /dev/null
}
try                                               # cấu hình mặc định: trước 50, sau 0
try --appendonly yes --appendfsync everysec       # có nhật ký ghi: trước 50, sau 50
```

Đừng thử trên cổng của một Redis đang chứa dữ liệu thật.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/iqiyi-database-selection-trees.md): iQIYI và các hệ họ dùng; nguồn ghi iQIYI có hơn 500 triệu người dùng hoạt động mỗi tháng.
- [Redis — `redis.conf`, tại commit cố định](https://github.com/redis/redis/blob/5e332cabd547d272783cf233a34c81dcb9ea44b3/redis.conf): ba mốc chụp dữ liệu mặc định, `appendonly no`, `appendfsync everysec` có thể mất khoảng một giây ghi. Đọc từ bản clone của kho; phép thử dùng Redis 7.0.15 cài trên máy.
- README tại commit cố định, đọc từ bản clone nông: [TiDB](https://github.com/pingcap/tidb/blob/328460a9af032ec6b53823724f87837a6d2d5857/README.md), [TiKV](https://github.com/tikv/tikv/blob/67ffce0c137b7c171405a76df8bc8e9f04a19ce6/README.md), [Apache Hive](https://github.com/apache/hive/blob/170e8e5326e5bd9596daf675d0cc5910cb8d39bf/README.md), [Apache Impala](https://github.com/apache/impala/blob/1092b077a85ee5c22716a29262f50a3dad8fd219/README.md).

Phép thử chạy ngày 2026-10-18 trên máy biên soạn. Cây quyết định là của người biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

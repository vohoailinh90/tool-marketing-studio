# B-tree và LSM-tree: trả giá lúc ghi hay lúc gộp

**B-tree sửa dữ liệu tại chỗ, theo từng trang. LSM-tree không sửa tại chỗ: nó ghi thêm rồi gộp dần. Câu "B-tree đọc nhanh, LSM-tree ghi nhanh" đúng một phần, và phần còn lại phụ thuộc vào cách bạn ghi.**
Bài này nạp cùng một triệu khóa ngẫu nhiên vào SQLite (B-tree) và RocksDB (LSM-tree) rồi đếm số byte mỗi bên phải ghi.

![Ba khung. Khung một, hai cách giữ khóa có thứ tự: B-tree là cây các trang 4 KiB, sửa một dòng là ghi lại cả trang chứa nó; LSM-tree ghi vào nhật ký và bộ nhớ, đầy thì đổ ra tệp đã sắp xếp rồi gộp dần xuống tầng dưới. Khung hai, thử với một triệu khóa ngẫu nhiên, 116 MB dữ liệu: B-tree commit mỗi 1.000 dòng với bộ đệm 256 MiB ghi ra 12,2 GB, gấp 105 lần; B-tree một giao dịch với bộ đệm 256 MiB ghi 281 MB, gấp 2,4 lần; LSM-tree ghi 621 MB, gấp 5,4 lần; tìm 100.000 khóa không có mất 0,07 s với bộ lọc Bloom, 0,74 s khi tắt. Khung ba, chọn theo việc: ghi nhiều và rải rác hợp LSM-tree; B-tree ghi ít khi gom nhiều thay đổi và bộ đệm đủ lớn; LSM-tree cần bộ lọc Bloom và việc gộp chạy nền.](../../diagrams/sd-04-020-main.svg)

## Từ viết tắt

- **LSM** (Log-Structured Merge) — gộp theo cấu trúc nhật ký: cách lưu trong đó thay đổi được ghi nối tiếp như nhật ký, rồi các tệp đã sắp xếp được gộp dần với nhau.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc của cơ sở dữ liệu quan hệ; nằm trong tên SQLite.
- **DB** (DataBase) — cơ sở dữ liệu; nằm trong tên RocksDB và LevelDB.
- **KiB** (Kibibyte) — kibibyte: 1.024 byte; mỗi trang của SQLite trong thử nghiệm là 4 KiB.
- **MiB** (Mebibyte) — mebibyte: 1.048.576 byte; dùng cho cỡ bộ đệm và cỡ bộ nhớ ghi.
- **MB** (MegaByte) — megabyte: một triệu byte; dùng cho lượng dữ liệu và số byte đã ghi.
- **GB** (GigaByte) — gigabyte: một tỉ byte.
- **WAL** (Write-Ahead Log) — nhật ký ghi trước: tệp mà thay đổi được ghi vào trước khi tới tệp dữ liệu chính; SQLite ở chế độ này ghi trang đã sửa vào đó.

## Đọc hình

**Khung 1 · Hai cách giữ khóa có thứ tự.**

- **B-tree.** Mã nguồn SQLite mô tả: mỗi trang của tệp chứa N mục và N+1 con trỏ tới trang con, khóa trong mỗi trang con nằm giữa hai khóa của trang cha. Tìm một khóa là đi từ gốc xuống lá, đọc số trang tăng theo logarit của số mục. Sửa một dòng nghĩa là sửa trang chứa nó; ở chế độ WAL, SQLite ghi nguyên trang đó (kèm 24 byte đầu khung) vào nhật ký, rồi lúc checkpoint chép lại vào tệp chính.
- **LSM-tree.** Theo tài liệu thiết kế của LevelDB: mỗi thay đổi được nối vào tệp nhật ký và giữ một bản trong bộ nhớ (memtable). Memtable đầy thì được ghi ra một tệp đã sắp xếp theo khóa ở tầng 0. Các tệp tầng 0 có thể chồng khoảng khóa lên nhau; từ tầng 1 trở đi thì không. Tầng nào quá cỡ thì một phần của nó được gộp với các tệp chồng khoảng ở tầng dưới. Mọi việc gộp chỉ đọc và ghi từng khối lớn, liền mạch.

**Khung 2 · Thử: một triệu khóa, 116 MB.** Một triệu khóa ngẫu nhiên 16 byte, giá trị 100 byte, tức 116 MB dữ liệu, không `fsync`. "Đã ghi" là tổng số byte chương trình đưa cho các lệnh ghi tệp, gồm cả nhật ký, checkpoint, đổ tệp và gộp.

| Cách nạp | Thời gian nạp | Đã ghi | Gấp bao nhiêu lần dữ liệu | Tìm 100.000 khóa không có |
|---|---|---|---|---|
| B-tree, commit mỗi 1.000 dòng, bộ đệm mặc định (khoảng 2 MB) | 16,2 s | 12.481 MB | 107,6 | 0,68 s |
| B-tree, commit mỗi 1.000 dòng, bộ đệm 256 MiB | 14,6 s | 12.169 MB | 104,9 | 0,49 s |
| B-tree, một giao dịch, bộ đệm 256 MiB | 6,3 s | 281 MB | 2,4 | 0,63 s |
| LSM-tree, bộ lọc Bloom 10 bit mỗi khóa | 3,7 s | 621 MB | 5,4 | 0,07 s |
| LSM-tree, không bộ lọc Bloom | 2,9 s | 627 MB | 5,4 | 0,74 s |

Đọc bảng theo từng cặp:

- **B-tree trả giá theo số trang mỗi lần commit đụng tới.** Khóa ngẫu nhiên rải đều trên 34.181 trang, nên 1.000 dòng của một lần commit rơi vào gần như 1.000 trang khác nhau, và trang nào bị đụng cũng được ghi nguyên vào nhật ký. Bộ đệm lớn hơn không đổi được điều đó (107,6 so với 104,9 lần). Gom cả triệu dòng vào một giao dịch, với bộ đệm 256 MiB đủ chứa mọi trang của tệp 140 MB, thì mỗi trang chỉ phải ghi khoảng hai lần (vào nhật ký, rồi lúc checkpoint): còn 2,4 lần. Giao dịch lớn với bộ đệm nhỏ thì không đo.
- **LSM-tree trả giá lúc gộp.** Ở cỡ lô 1.000 dòng, nó ghi khoảng 5,4 lần dữ liệu. Nhật ký và việc đổ memtable ra tệp mỗi thứ chỉ tốn khoảng một lần dữ liệu; phần lớn còn lại là do gộp tầng này xuống tầng dưới, vốn không gắn với cỡ lô (suy luận; thử nghiệm chỉ đo một cỡ lô). Mọi lần ghi đều nối tiếp, nên nạp nhanh nhất.
- **Bộ lọc Bloom quyết định giá của việc tìm khóa không có.** Ở LSM-tree, một khóa có thể nằm ở nhiều tệp; bộ lọc cho biết chắc chắn "không có ở tệp này" để khỏi đọc tệp. Tắt nó, tìm khóa không có chậm gấp 10 lần.

Khi tìm khóa có thật, cả năm cách đều mất 0,6 đến 0,9 s cho 100.000 lần: dữ liệu nằm hết trong bộ nhớ và phần lớn thời gian là của lớp Python, nên thử nghiệm này không so được tốc độ đọc từ đĩa.

## Giới hạn cần nhớ

- Không có `fsync` và chỉ một máy; số byte đã ghi là số chương trình yêu cầu ghi, không phải số byte ổ đĩa thật sự ghi.
- RocksDB được thu nhỏ 16 lần cho vừa thử nghiệm: memtable 4 MiB và tầng gốc 16 MiB thay cho mặc định 64 MiB và 256 MiB. Với mặc định, 116 MB chỉ đổ ra vài tệp tầng 0, dưới ngưỡng gộp mặc định là 4 tệp; một lần chạy thử 300.000 khóa với mặc định chỉ tạo đúng một tệp và không lần gộp nào.
- RocksDB 9.8 bật mặc định chế độ chọn cỡ tầng động: dữ liệu đi thẳng xuống tầng cuối rồi mới dùng dần các tầng trên. Vì thế sau thử nghiệm dữ liệu nằm ở tầng 5 và 6, không phải tầng 1 và 2.
- Gộp chạy nền phải theo kịp việc ghi. RocksDB làm chậm việc ghi khi tầng 0 có 20 tệp và dừng ghi khi có 36 tệp (mặc định).

## Nhìn hình trả lời

Một dịch vụ nhận sự kiện từ rất nhiều thiết bị; mỗi sự kiện là một lệnh ghi nhỏ, khóa rải rác, và phải lưu ngay khi nhận chứ không chờ gom. Nhìn khung 2: cấu trúc nào ghi ít byte hơn trên mỗi sự kiện, và vì sao điều kiện "lưu ngay" lại quan trọng?

<details>
<summary>Xem đáp án</summary>

LSM-tree: ở lô 1.000 dòng nó ghi khoảng 5,4 lần dữ liệu, và phần lớn là do gộp, vốn không gắn với cỡ lô. B-tree chỉ ghi ít (2,4 lần) khi gom thật nhiều thay đổi vào một giao dịch và bộ đệm đủ lớn; "lưu ngay" nghĩa là mỗi giao dịch rất nhỏ, và mỗi giao dịch nhỏ vẫn phải ghi lại nguyên trang mà nó đụng tới, tức cỡ trường hợp hơn 100 lần trong bảng (tương tự, vì 1.000 dòng ngẫu nhiên của một commit vốn đã rơi vào gần 1.000 trang khác nhau).
Đây là suy luận từ số đo ở trên; thử nghiệm không đo trường hợp mỗi commit một dòng.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn kết luận "B-tree đọc nhanh hơn, LSM-tree ghi nhanh hơn". Thử nghiệm cho thấy phần ghi phụ thuộc cách commit: B-tree với một giao dịch lớn ghi ít byte hơn LSM-tree. Phần đọc thì thử nghiệm không kiểm được vì dữ liệu nằm trong bộ nhớ; điều nó cho thấy là LSM-tree cần bộ lọc Bloom để tìm khóa không có cho nhanh.
Bài nguồn nói tầng 0 được gộp định kỳ vào tầng 1; với RocksDB bản hiện nay, tầng gộp vào có thể là tầng thấp nhất đang dùng, như đã nêu ở phần giới hạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/b-tree-vs.md): B-tree và LSM-tree.
- SQLite 3.45.1, đọc từ bản sao trên GitHub của kho SQLite: [cấu trúc B-tree](https://github.com/sqlite/sqlite/blob/189e44dfecdc7868bb860dfb5d98eab371318c37/src/btreeInt.h) (trang, con trỏ, số trang phải đọc) và [nhật ký WAL](https://github.com/sqlite/sqlite/blob/189e44dfecdc7868bb860dfb5d98eab371318c37/src/wal.c) (mỗi khung là đầu khung 24 byte cộng nguyên một trang; checkpoint).
- [LevelDB — tài liệu thiết kế, tại commit cố định](https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/doc/impl.md): nhật ký, memtable, tệp đã sắp xếp, các tầng và việc gộp.
- RocksDB 9.8.4, tại commit cố định: [tùy chọn chính](https://github.com/facebook/rocksdb/blob/44e95d8af5d7ec503b3f1d5754c3379ab6c29a9d/include/rocksdb/options.h) (memtable 64 MiB, tầng gốc 256 MiB), [tùy chọn nâng cao](https://github.com/facebook/rocksdb/blob/44e95d8af5d7ec503b3f1d5754c3379ab6c29a9d/include/rocksdb/advanced_options.h) (cỡ tầng động, ngưỡng làm chậm và dừng ghi), [bộ lọc Bloom](https://github.com/facebook/rocksdb/blob/44e95d8af5d7ec503b3f1d5754c3379ab6c29a9d/include/rocksdb/filter_policy.h) (khoảng 10 bit mỗi khóa cho tỉ lệ dương tính giả khoảng 1%).

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 với SQLite 3.45.1 (mô-đun `sqlite3` của Python 3.13) và RocksDB 9.8.4 (qua `rocksdict` 0.3.29) trên một máy.
Bài viết và hình được thiết kế độc lập.

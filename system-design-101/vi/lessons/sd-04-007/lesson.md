# Mức cô lập giao dịch: mỗi mức chặn được hiện tượng nào

**Hai giao dịch chạy cùng lúc thì một bên có thể thấy, hoặc không thấy, việc bên kia đang làm.**
Mức cô lập (isolation level) là lời hứa của cơ sở dữ liệu về những hiện tượng *không* được xảy ra; mức càng cao, càng ít hiện tượng, nhưng càng nhiều giao dịch bị hủy và phải chạy lại.

![Ba khung. Khung một: bốn thẻ, mỗi mức cô lập một thẻ, ghi điều T1 thấy. Read Uncommitted chạy như Read Committed: không thấy thay đổi chưa commit, vẫn 100. Read Committed, mức mặc định: lần đọc sau thấy 200 vừa được commit, đếm lại thấy thêm dòng mới. Repeatable Read: cả giao dịch thấy một ảnh chụp, vẫn 100 và vẫn 1 dòng. Serializable: như Repeatable Read và còn chặn lệch ghi. Khung hai là ví dụ lệch ghi: hai bác sĩ cùng thấy 2 người đang trực, mỗi người tắt ca của mình; ở Repeatable Read cả hai commit và còn 0 người trực, ở Serializable một giao dịch bị hủy và còn 1 người. Khung ba: mức cao hơn có thể hủy giao dịch nên phải thử lại; cùng tên mức nhưng mỗi hệ có thể làm khác.](../../diagrams/sd-04-007-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để đọc và ghi dữ liệu quan hệ; chuẩn SQL đặt tên bốn mức cô lập, và nó nằm trong tên PostgreSQL.
- **MVCC** (MultiVersion Concurrency Control) — điều khiển đồng thời đa phiên bản: cơ sở dữ liệu giữ nhiều phiên bản của một hàng, để mỗi giao dịch đọc phiên bản hợp với ảnh chụp của mình mà không phải chờ bên đang ghi.
- **SSI** (Serializable Snapshot Isolation) — cô lập ảnh chụp tuần tự hóa được: kỹ thuật PostgreSQL dùng cho mức Serializable, chạy như ảnh chụp rồi kiểm thêm xem các giao dịch có tạo ra kết quả mà không thứ tự tuần tự nào cho ra không.

## Bốn hiện tượng

Chuẩn SQL định nghĩa các mức bằng các hiện tượng chúng cấm. Tài liệu PostgreSQL liệt kê bốn:

| Hiện tượng | Nghĩa |
|---|---|
| Đọc bẩn (dirty read) | đọc được dữ liệu bên khác ghi nhưng chưa commit |
| Đọc không lặp lại (nonrepeatable read) | đọc lại một hàng thì thấy giá trị khác, vì bên khác vừa commit |
| Đọc bóng ma (phantom read) | chạy lại cùng một điều kiện thì tập hàng trả về đã khác |
| Bất thường tuần tự hóa (serialization anomaly) | kết quả của cả nhóm giao dịch không khớp với bất kỳ thứ tự chạy lần lượt nào |

## Đọc hình: thử trên PostgreSQL 16

**Khung 1.** T1 đọc số dư (100). T2 sửa thành 200 nhưng chưa commit, T1 đọc lại; T2 commit, T1 đọc lần ba. Sau đó T1 đếm số hàng, T2 thêm một hàng và commit, T1 đếm lại.

| Mức của T1 | Khi T2 chưa commit | Khi T2 đã commit | Đếm hàng |
|---|---|---|---|
| Read Uncommitted | 100 | 200 | 1 rồi 2 |
| Read Committed | 100 | 200 | 1 rồi 2 |
| Repeatable Read | 100 | 100 | 1 rồi 1 |
| Serializable | 100 | 100 | 1 rồi 1 |

Không mức nào đọc bẩn: tài liệu PostgreSQL nói Read Uncommitted của nó chạy như Read Committed. Repeatable Read của PostgreSQL cũng không có đọc bóng ma, dù chuẩn SQL cho phép; chuẩn chỉ quy định điều *không* được xảy ra, làm chặt hơn vẫn đúng chuẩn.

**Khung 2 · Lệch ghi.** Hai bác sĩ đang trực, luật là phải còn ít nhất một người. Mỗi giao dịch đếm thấy 2 người, rồi tắt ca của chính mình. Hai giao dịch sửa hai hàng khác nhau nên không khóa nhau.
Ở Repeatable Read cả hai commit và không còn ai trực. Ở Serializable, giao dịch thứ hai bị hủy với lỗi "could not serialize access due to read/write dependencies among transactions" và còn 1 người trực.

## Giới hạn cần nhớ

Tên mức giống nhau không có nghĩa hành vi giống nhau giữa các hệ quản trị: bảng trên là của PostgreSQL 16, đừng mang nguyên sang hệ khác. Và mức cao không miễn phí: Repeatable Read và Serializable của PostgreSQL có thể hủy giao dịch, tài liệu dặn ứng dụng phải sẵn sàng chạy lại cả giao dịch từ đầu.

## Nhìn hình trả lời

Một báo cáo đọc tổng doanh thu, rồi đọc chi tiết từng đơn trong cùng một giao dịch. Ở mức mặc định của PostgreSQL, tổng và chi tiết có thể lệch nhau không? Nên đổi mức nào?

<details>
<summary>Xem đáp án</summary>

Có thể lệch. Mức mặc định là Read Committed: mỗi câu lệnh thấy dữ liệu đã commit lúc câu lệnh *đó* bắt đầu, nên một đơn commit giữa hai câu lệnh sẽ có trong chi tiết mà không có trong tổng (khung 1, cột "khi T2 đã commit").
Repeatable Read cho cả giao dịch một ảnh chụp nên tổng và chi tiết khớp nhau. Báo cáo chỉ đọc nên, theo tài liệu PostgreSQL, không bị hủy vì xung đột ở mức này.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn gọi MVCC là "Multi-Version Consistency Control"; tài liệu PostgreSQL gọi là Multiversion Concurrency Control. Bài nguồn minh họa MVCC bằng hai cột ẩn của mỗi hàng (mã giao dịch và con trỏ tới phiên bản cũ); bài này không kiểm cơ chế đó mà quan sát kết quả trên PostgreSQL.
Bài nguồn cũng định nghĩa Serializable là "các giao dịch được bảo đảm chạy tuần tự". Thử nghiệm cho thấy cách PostgreSQL làm: các giao dịch vẫn chạy song song, và hệ hủy một giao dịch khi phát hiện kết quả không thể có nếu chạy lần lượt.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-database-isolation-levels.md): bốn mức cô lập và ví dụ MVCC ở mức Repeatable Read.
- [PostgreSQL 16 — chương Concurrency Control, tại commit cố định](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/mvcc.sgml): bảng bốn hiện tượng theo mức, Read Uncommitted chạy như Read Committed, Repeatable Read không có đọc bóng ma, Serializable dùng SSI, lời dặn thử lại giao dịch, giao dịch chỉ đọc không bị hủy ở Repeatable Read. Đọc từ bản clone của kho, nhánh `REL_16_STABLE`.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên PostgreSQL 16.15, hai kết nối trên cùng máy.
Bài viết và hình được thiết kế độc lập.

# Lớp trung gian cơ sở dữ liệu: một cửa chung và ba cái giá

**Lớp trung gian cơ sở dữ liệu đứng giữa ứng dụng và các máy cơ sở dữ liệu: ứng dụng chỉ gửi truy vấn tới một địa chỉ, còn lớp trung gian quyết định câu nào đi tới máy chính (ghi) và câu nào đi tới máy phụ (đọc).**
Bài nguồn nêu hai lợi ích (mã ứng dụng gọn hơn, tương thích với mọi ứng dụng nói được giao thức của MySQL) và hai cái giá (phức tạp, thêm một bước mạng). Bài này đo hai cái giá đó trên một máy và thử xem một quy tắc định tuyến đơn giản sai ở đâu.

![Ba khung. Khung một, bốn mảnh: ứng dụng gửi truy vấn tới lớp trung gian; lớp trung gian đưa lệnh ghi tới máy chính và lệnh đọc tới máy phụ. Khung hai, thử đo trên Redis chạy một máy: thêm một lớp chuyển tiếp làm lượt đọc từ 36 đến 41 micro giây lên 75 đến 83; khi máy chính bận ghi liên tục, 16 đến 31 phần trăm lượt đọc đầu tiên trên máy phụ vẫn chưa thấy giá trị vừa ghi. Khung ba, hai quy tắc định tuyến theo đầu câu lệnh: trong 8 câu thử, 4 câu bị đưa sai chỗ, 2 câu trong đó đọc có khóa lại rơi vào máy phụ.](../../diagrams/sd-08-006-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; câu lệnh `SELECT` đọc, `INSERT` ghi.

## Đọc hình

**Bốn mảnh.** Ứng dụng không biết có bao nhiêu máy phía sau. Lớp trung gian nhận mọi câu lệnh, phân loại, rồi chuyển: lệnh ghi tới một máy chính, lệnh đọc tới các máy phụ chép dữ liệu từ máy chính. Công cụ thật làm việc này có nhiều: tài liệu của MariaDB MaxScale mô tả router "readwritesplit" tăng khả năng đọc của cụm bằng cách rải lệnh đọc ra nhiều nút, còn mọi lệnh ghi đi tới một nút; ProxySQL cho viết quy tắc định tuyến theo mẫu câu lệnh.

**Cái giá thứ nhất: quy tắc có thể định tuyến sai.** Ví dụ trong tệp hướng dẫn của ProxySQL có hai quy tắc: câu khớp `^SELECT .* FOR UPDATE$` đi tới nhóm máy chính (nhóm 0), câu khớp `^SELECT` đi tới nhóm máy đọc (nhóm 1), còn lại về nhóm mặc định.

**Cái giá thứ hai: thêm một bước mạng.** Mỗi câu lệnh đi qua thêm một thành phần, nên thêm độ trễ, và theo bài nguồn lớp này cần hiệu năng thật tốt.

**Cái giá thứ ba: một điểm hỏng chung.** Mọi truy vấn đều đi qua nó nên nó thường phải chạy theo kiểu độ sẵn sàng cao để một máy hỏng không làm cả hệ thống dừng (theo bài nguồn).

## Thử: bước nhảy thêm và máy phụ chậm hơn

Ngày 2026-10-19, trên một máy ảo 4 lõi, Redis 7.0.15: một máy chính và một máy phụ chép theo từ máy chính (đồng bộ không chờ), đo ba lượt. Redis không phải MySQL, nhưng cùng có kiểu chép "máy phụ theo sau máy chính", nên đủ để thấy hai hiện tượng.

| Phép đo | Kết quả |
|---|---|
| Đọc trực tiếp từ máy chính (`GET`) | trung vị 36 đến 41 µs, phân vị 99 là 79 đến 85 µs |
| Đọc qua một lớp chuyển tiếp byte viết bằng Python | trung vị 75 đến 83 µs, phân vị 99 là 170 đến 210 µs |
| Ghi rồi đọc ngay từ máy phụ, máy chính rảnh (20.000 lần) | 0 đến 2 lần đọc thấy bản cũ |
| Cùng phép đó khi máy chính đang nhận một luồng ghi liên tục (3.000 lần) | 481 đến 940 lần (16,0 đến 31,3%) đọc thấy bản cũ |
| Thời gian máy phụ cần để thấy giá trị mới, máy chính bận | trung vị 79 đến 226 µs, phân vị 99 là 1,4 đến 2,3 ms, lớn nhất 2,6 đến 10,6 ms |

Một lớp chuyển tiếp không làm gì ngoài chuyển byte đã làm thời gian một lượt đọc tăng gấp đôi. Máy phụ thì khác máy chính: khi máy chính rảnh, nó gần như luôn đuổi kịp; khi máy chính bận ghi, cứ ba đến sáu lượt đọc đầu tiên thì có một lượt chưa thấy giá trị vừa ghi. Bài `sd-04-035` đã đi sâu vào tình huống "vừa đặt đơn mà không thấy đơn" và cách chữa; ở đây chỉ cần nhớ rằng lớp trung gian không làm độ trễ chép biến mất.

## Thử: hai quy tắc định tuyến theo đầu câu lệnh

Cùng ngày, tôi cho tám câu lệnh đi qua đúng hai mẫu của ví dụ ProxySQL ở trên, bằng thư viện biểu thức chính quy của Python (không phân biệt hoa thường) thay cho ProxySQL, rồi đối chiếu với chỗ câu nên đi. Câu không khớp mẫu nào về nhóm mặc định, ở đây là máy chính.

| Câu lệnh (rút gọn) | Đi tới | Nên đi tới |
|---|---|---|
| `SELECT ... WHERE id = 1` | máy phụ | máy phụ |
| `SELECT ... FOR UPDATE` | máy chính | máy chính |
| `select ...` (chữ thường) | máy phụ | máy phụ |
| `INSERT ...` | máy chính | máy chính |
| `SELECT ... FOR SHARE` | máy phụ | **máy chính** |
| `SELECT ... LOCK IN SHARE MODE` | máy phụ | **máy chính** |
| `/* req-7 */ SELECT ...` | máy chính | máy phụ |
| `WITH x AS (...) SELECT ...` | máy chính | máy phụ |

Bốn trên tám câu đi sai chỗ, hai loại sai khác nhau. Hai câu đọc có khóa (`FOR SHARE`, `LOCK IN SHARE MODE`) cũng bắt đầu bằng `SELECT` nhưng mẫu chỉ biết `FOR UPDATE`, nên rơi vào máy phụ: đó là sai về ý nghĩa (khóa cần đặt trên máy chính). Hai câu có chú thích hoặc `WITH` ở đầu không khớp `^SELECT`, nên về máy chính: an toàn, nhưng mất lợi ích của máy phụ. Muốn đúng phải thêm quy tắc hoặc dùng công cụ biết phân tích câu lệnh.

## Giới hạn cần nhớ

Các phép đo là của một máy ảo: lớp chuyển tiếp viết bằng Python chậm hơn một sản phẩm thật nhiều, nên đừng đọc "gấp đôi" là hằng số mà đọc là "một bước nhảy tốn cỡ một lượt gọi trên chính máy này". Redis chỉ thay MySQL ở chỗ chép chậm; không đo cơ chế chép của MySQL, độ trễ qua mạng thật hay các tính năng của MaxScale. Phép thử quy tắc dùng thư viện của Python, không phải bộ so khớp của ProxySQL, nên chi tiết như hoa thường hay xuống dòng có thể khác. Tài liệu MaxScale nhấn mạnh rằng giới hạn độ trễ chép (`max_replication_lag`) không bảo đảm lượt ghi đã nhìn thấy được trên máy phụ; muốn bảo đảm phải dùng tính năng riêng gọi là `causal_reads`, và các chế độ nhanh của nó đẩy gần hết lượt đọc về máy chính nếu khối lượng việc có nhiều lệnh ghi.

## Nhìn hình trả lời

Một đội dùng lớp trung gian với hai quy tắc ở trên. Một lập trình viên viết `SELECT ... LOCK IN SHARE MODE` để chặn người khác sửa dòng trong lúc mình kiểm tra. Điều gì xảy ra, và sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Câu bắt đầu bằng `SELECT` nhưng không kết thúc bằng `FOR UPDATE`, nên rơi vào quy tắc thứ hai và đi tới máy phụ: khóa không đặt trên máy chính, nên không chặn được lượt ghi nào của người khác. Sửa bằng cách thêm quy tắc đưa các câu đọc có khóa (`FOR SHARE`, `LOCK IN SHARE MODE`) về máy chính trước quy tắc `^SELECT`, hoặc viết rõ vào mã rằng phiên này dùng máy chính, rồi thêm một câu thử cho đúng ca này.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một sơ đồ năm bước (Alice đặt đơn rồi xem đơn) cộng hai lợi ích và hai cái giá của lớp trung gian. Bài này giữ bốn ý đó, nhưng đo từng cái giá thay vì kể lại, và thêm một cái giá mà bài nguồn không nêu: quy tắc định tuyến theo mẫu câu lệnh có thể sai. Cái giá thứ ba và độ sẵn sàng cao là lời của bài nguồn, chưa đo. Câu chuyện đọc nhầm bản cũ sau khi ghi được giữ cho bài `sd-04-035`.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/database-middleware.md): lớp trung gian, hai lợi ích, hai cái giá.
- [MariaDB MaxScale — router Readwritesplit](https://github.com/mariadb-corporation/MaxScale/blob/81d12aa52fe2666d208d6f3a106d8518e40798f1/Documentation/Routers/ReadWriteSplit.md): tách đọc ghi, giới hạn độ trễ chép, `causal_reads`. Đọc từ bản clone của kho.
- [ProxySQL — tệp hướng dẫn đầu kho](https://github.com/sysown/proxysql/blob/9516441f7bd6fdb93f255f1881db19ca9ee56778/README.md): nhóm máy, quy tắc truy vấn theo mẫu. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-19. Các phép đo và phép thử quy tắc là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

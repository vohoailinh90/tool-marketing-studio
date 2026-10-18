# Cơ sở dữ liệu serverless: tách phần tính toán khỏi phần lưu trữ

**"Serverless" không có nghĩa là không có máy chủ; nghĩa là bạn không chọn và không giữ máy chủ.** Bạn khai báo dung lượng tối thiểu và tối đa, còn dịch vụ tự tăng giảm phần tính toán theo tải, kể cả dừng hẳn khi không ai dùng. Điều làm được việc đó là thiết kế bên dưới: phần tính toán (tiến trình chạy truy vấn) tách khỏi phần lưu trữ (nơi giữ dữ liệu), nên phần tính toán có thể mất đi và sinh lại mà dữ liệu vẫn còn.

![Khung một, ba mảnh nối nhau: ứng dụng gửi truy vấn; phần tính toán là tiến trình cơ sở dữ liệu không giữ dữ liệu, co giãn theo tải và có thể dừng hẳn; phần lưu trữ giữ dữ liệu và nhật ký ghi, sống độc lập. Khung hai, Aurora Serverless v2 theo tài liệu API của AWS: dung lượng đo bằng ACU, chỉnh theo bước 0,5; tối đa 256 ACU với bản mới, 128 với bản cũ; tối thiểu 0 ACU khi bản đó hỗ trợ tự tạm dừng, nếu không thì 0,5; tạm dừng sau 300 giây rảnh theo mặc định, tới một ngày. Khung ba, thử trên một máy: dừng tiến trình A, chạy tiến trình B trên cùng thư mục dữ liệu; B thấy đủ 1.000.000 dòng; bộ đệm của B trống, nên câu quét cả bảng đọc 4.425 trang từ kho, còn câu tra một khóa chỉ đọc 4 trang.](../../diagrams/sd-04-028-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ cơ sở dữ liệu dùng nó, và Aurora có bản tương thích PostgreSQL.
- **ACU** (Aurora Capacity Unit) — đơn vị dung lượng Aurora: đơn vị mà Aurora Serverless v2 dùng để đo và tính phần tính toán của một máy cơ sở dữ liệu.
- **AWS** (Amazon Web Services) — dịch vụ đám mây của Amazon, nơi cung cấp Aurora.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình gọi chức năng của dịch vụ; ở đây là mô tả các tham số cấu hình Aurora mà AWS công bố cho bộ công cụ lập trình.
- **WAL** (Write-Ahead Log) — nhật ký ghi trước: PostgreSQL ghi mọi thay đổi vào nhật ký này trước khi sửa dữ liệu, nên nhật ký đủ để dựng lại dữ liệu.

## Đọc hình

1. **Ba mảnh.** Ứng dụng nói chuyện với phần tính toán như với một cơ sở dữ liệu thường. Phần tính toán không giữ dữ liệu của riêng nó. Phần lưu trữ giữ dữ liệu và nhật ký ghi. Neon, một nền tảng PostgreSQL serverless mã nguồn mở, mô tả đúng kiểu này: các máy tính toán là PostgreSQL "không trạng thái", đứng trên một bộ máy lưu trữ riêng; WAL đi tới một nhóm máy giữ nhật ký, rồi được xử lý thành các trang dữ liệu.
2. **Aurora Serverless v2.** Mô tả tham số trong mô hình API của AWS cho biết: dung lượng đo bằng ACU và chỉnh theo bước 0,5; tối đa 256 ACU với các bản Aurora mới, 128 với bản cũ; tối thiểu 0 ACU với bản hỗ trợ tự tạm dừng (bản không hỗ trợ thì thấp nhất 0,5). Máy rảnh bao lâu thì tạm dừng là tham số riêng, từ 300 giây (mặc định) tới 86.400 giây.
3. **Thử ý tưởng trên một máy.** Phép thử chạy ngày 2026-10-18 với PostgreSQL 16.15. Tiến trình A tạo bảng 1.000.000 dòng rồi dừng. Tiến trình B, khác số tiến trình và cổng, khởi động trên cùng thư mục dữ liệu: B thấy đủ 1.000.000 dòng và tổng giống hệt. Nhưng bộ đệm của B trống, nên trang nào câu hỏi chạm tới cũng phải đọc từ kho: câu đầu tiên là một phép quét cả bảng, nên nó đọc cả 4.425 trang (`shared read=4425`); còn nếu câu đầu tiên chỉ tra một đơn theo khóa chính, B chỉ đọc 4 trang (cộng vài trang danh mục khi lập kế hoạch). Đây là mô hình đồ chơi: thư mục nằm trên cùng đĩa, còn dịch vụ thật để phần lưu trữ trên một cụm máy riêng.

## Giới hạn cần nhớ

Dừng hẳn để không tốn tiền phần tính toán có cái giá: yêu cầu đầu tiên sau khi tạm dừng phải chờ phần tính toán chạy lại, và các trang mà những yêu cầu đầu tiên chạm tới phải đọc lại từ kho; bộ đệm chỉ nóng dần theo đúng các trang được dùng. Bài không đo được thời gian đó trên Aurora; phép thử trên một máy khởi động trong khoảng 0,1 giây, con số không nói gì về một dịch vụ đám mây. Ứng dụng cần lượng truy vấn đều, liên tục thì máy cố định có thể rẻ hơn và dễ đoán hơn; hãy so bảng giá hiện hành trước khi chọn. Bài này không dùng bảng giá nào.

## Nhìn hình thử trả lời

Một công cụ nội bộ chỉ được dùng trong giờ làm việc, cả đêm không ai truy cập. Bạn đặt dung lượng tối thiểu 0 ACU. Sáng hôm sau, người đầu tiên mở công cụ thấy trang tải chậm hơn hẳn các lần sau. Vì sao, và có những cách nào để giảm?

<details>
<summary>Xem đáp án</summary>

Sau một lúc rảnh (mặc định 300 giây), máy được tạm dừng; yêu cầu đầu tiên buổi sáng phải chờ phần tính toán chạy lại. Sau đó bộ đệm còn trống, nên những trang mà các yêu cầu đầu tiên chạm tới phải đọc lại từ phần lưu trữ: ít nếu trang chỉ tra vài dòng theo khóa (4 trang trong phép thử), nhiều nếu trang mở một báo cáo quét cả bảng (4.425 trang).
Cách giảm: đặt dung lượng tối thiểu lớn hơn 0 (chấp nhận trả tiền cả lúc rảnh), kéo dài thời gian trước khi tạm dừng, hoặc gửi một truy vấn "đánh thức" trước giờ làm việc.

</details>

<details>
<summary>Xem sâu hơn: lệnh của phép thử</summary>

Chạy với quyền của người dùng hệ thống `postgres`, trong một thư mục thử (đừng dùng dữ liệu thật):

```bash
B=/usr/lib/postgresql/16/bin
$B/initdb -D /tmp/s028 -U postgres --auth=trust
$B/pg_ctl -D /tmp/s028 -o '-p 5440 -k /tmp' start          # tiến trình A
psql -h /tmp -p 5440 -U postgres -c "create table orders(id int primary key, amount int);
  insert into orders select g, g % 97 from generate_series(1, 1000000) g; checkpoint;"
$B/pg_ctl -D /tmp/s028 stop                                 # A dừng
$B/pg_ctl -D /tmp/s028 -o '-p 5441 -k /tmp' start          # tiến trình B, cùng thư mục
psql -h /tmp -p 5441 -U postgres -c "explain (analyze, buffers) select count(*), sum(amount) from orders"
$B/pg_ctl -D /tmp/s028 restart                              # bộ đệm trống lại
psql -h /tmp -p 5441 -U postgres -c "explain (analyze, buffers) select * from orders where id = 424242"
```

Kết quả: `count` 1.000.000 và `sum` 47.999.082 ở cả hai tiến trình; câu quét cả bảng của B báo `Buffers: shared read=4425`, câu tra theo khóa chính sau khi khởi động lại báo `shared read=4` ở phần thực thi.

Thư mục dữ liệu chỉ được một tiến trình dùng tại một lúc (PostgreSQL ghi khóa vào tệp `postmaster.pid`). Dịch vụ serverless thật giải bài toán khó hơn: phần lưu trữ phục vụ trang cho các máy tính toán qua mạng, và nhật ký ghi được giữ ở nhiều máy cho tới khi đã xử lý xong.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-serverless-db.md): Aurora Serverless tự co giãn theo nhu cầu, tách tầng tính toán khỏi tầng lưu trữ để tính phí chính xác hơn.
- [AWS — mô hình API của Amazon RDS trong botocore, tại commit cố định](https://github.com/boto/botocore/blob/4de93abe62cc263980414f7a66be5226bd541b77/botocore/data/rds/2014-10-31/service-2.json): mục `ServerlessV2ScalingConfiguration` (`MinCapacity`, `MaxCapacity`, `SecondsUntilAutoPause`). Đọc từ bản clone của kho; tài liệu hướng dẫn trên trang của AWS không mở được.
- [Neon — README, tại commit cố định](https://github.com/neondatabase/neon/blob/fa504217c61bbcaf5c512d75830564541f917f8f/README.md): tách lưu trữ khỏi tính toán, máy tính toán PostgreSQL không trạng thái, máy chủ trang và nhóm máy giữ WAL. Đọc từ bản clone của kho.

Phép thử chạy trên PostgreSQL 16.15 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

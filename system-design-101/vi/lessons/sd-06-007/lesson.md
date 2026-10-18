# Các cách giảm độ trễ hay dùng, và vì sao phải đo trước

**Độ trễ là thời gian người dùng chờ từ lúc hỏi tới lúc có câu trả lời. Thời gian đó cộng từ nhiều khúc: tìm dữ liệu, tính toán, xếp hàng chờ máy rảnh, truyền qua mạng. Mỗi cách giảm độ trễ chỉ cắt một khúc, nên phải đo xem khúc nào dài trước khi chọn cách.**

![Ba khung. Khung một, bốn bước: đo xem thời gian nằm ở đâu; chọn cách đánh vào đúng khúc đó; đo lại; ghi cái giá phải trả. Khung hai, sáu cách: chỉ mục cắt thời gian tìm trong cơ sở dữ liệu, thử nghiệm thấy truy vấn từ khoảng 11 đến 13 mili giây còn 1 đến 2 mili giây; bộ nhớ đệm bỏ qua việc tính lại; cân bằng tải bớt hàng chờ ở một máy; CDN rút ngắn quãng đường; bất đồng bộ cho người dùng khỏi chờ việc chậm; nén làm gói nhỏ lại, một tệp JSON lặp nhiều còn khoảng 8 phần trăm. Khung ba, cái giá: chỉ mục làm việc ghi chậm hơn khoảng ba lần trong thử nghiệm; bộ nhớ đệm có thể trả dữ liệu cũ; nén tốn thời gian máy và không làm dữ liệu ngẫu nhiên nhỏ đi.](../../diagrams/sd-06-007-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt ở nhiều nơi, lưu bản sao nội dung và phát cho người dùng từ máy gần họ.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản gồm các cặp tên và giá trị, dùng rộng rãi để chương trình trao đổi dữ liệu.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời.
- **RFC** (Request for Comments) — loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; RFC 9110 định nghĩa ngữ nghĩa của HTTP, gồm cả cách ghi nội dung đã nén.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ cơ sở dữ liệu dùng nó.
- **JPEG** (Joint Photographic Experts Group) — tên nhóm chuyên gia đặt ra định dạng ảnh cùng tên; ảnh JPEG vốn đã được nén.
- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần của máy tính chạy các phép tính; nén dữ liệu tốn thời gian của nó.

## Đọc hình

Sáu cách quen thuộc, mỗi cách nhắm một khúc:

1. **Chỉ mục (index)** cắt thời gian *tìm* trong cơ sở dữ liệu. Tài liệu PostgreSQL ghi chỉ mục giúp tìm các dòng cần thiết nhanh hơn nhiều, nhưng thêm gánh nặng cho cả hệ thống, nên phải dùng có cân nhắc.
2. **Bộ nhớ đệm** cắt thời gian *tính lại hoặc đọc lại*, bằng cách trả lời từ bản sao.
3. **Cân bằng tải** cắt thời gian *xếp hàng*: chia yêu cầu cho nhiều máy để không máy nào bị dồn.
4. **CDN** cắt thời gian *truyền*: đặt bản sao gần người dùng.
5. **Xử lý bất đồng bộ** cắt thời gian *chờ việc chậm*: trả lời ngay, còn việc như gửi thư hay tạo báo cáo thì đưa vào hàng đợi làm sau.
6. **Nén** cắt thời gian *truyền dữ liệu lớn*: RFC 9110 định nghĩa content coding, như `gzip`, để nén nội dung mà không mất thông tin.

## Đo thử hai cách

Ngày 2026-10-18, trên một máy, với PostgreSQL 16.15 và Python 3.13.

**Chỉ mục.** Bảng `orders` 200.000 dòng, truy vấn đếm đơn của một khách. Không có chỉ mục: PostgreSQL quét cả bảng (`Seq Scan`), ba lần chạy mất 11–13 ms. Tạo chỉ mục trên cột khách (mất khoảng 105 ms): kế hoạch đổi sang `Bitmap Index Scan`, ba lần chạy mất 1,3–2,1 ms, cùng kết quả 2.001.
Cái giá ở chiều ghi: chèn 200.000 dòng vào một bảng không chỉ mục mất 0,43–0,59 giây; vào bảng có chỉ mục trên một cột văn bản ngẫu nhiên mất 1,4–1,7 giây (ba lần chạy), tức chậm hơn khoảng ba lần.

**Nén.** Một mảng JSON 2.000 sản phẩm, nhiều trường lặp lại, nặng 208.881 byte. Nén `gzip` mức 6 còn 17.720 byte (8,5%), mất khoảng 1,5 ms để nén và 0,24 ms để giải nén. Mức 9 chỉ nhỏ thêm chút ít (17.336 byte) nhưng tốn khoảng 4,5 ms. Dữ liệu ngẫu nhiên cùng cỡ sau khi nén còn *to hơn* một chút (208.964 byte).

## Giới hạn cần nhớ

Mỗi cách đều đổi lấy một thứ: chỉ mục làm việc ghi chậm hơn và tốn chỗ, bộ nhớ đệm có thể trả dữ liệu cũ, nén tốn thời gian CPU và vô ích với dữ liệu đã nén sẵn (ảnh JPEG, video), bất đồng bộ làm người dùng không biết ngay việc đã xong chưa. Không đo trước thì dễ thêm một cách vào khúc vốn đã ngắn, trả cái giá mà không được gì.

## Nhìn hình trả lời

Một trang danh sách đơn hàng mất 2 giây. Đo cho thấy truy vấn cơ sở dữ liệu chiếm 1,8 giây, phần truyền qua mạng chỉ 50 ms. Bật nén và thêm CDN có giúp nhiều không? Nên thử gì trước?

<details>
<summary>Xem đáp án</summary>

Giúp rất ít: nén và CDN chỉ cắt khúc truyền, mà khúc đó chỉ 50 ms trong 2 giây.
Nên xem kế hoạch của truy vấn (`EXPLAIN`): nếu nó quét cả bảng, một chỉ mục đúng cột lọc có thể cắt phần lớn 1,8 giây, như thử nghiệm ở trên. Sau đó đo lại, và nhớ đo cả tốc độ ghi vì chỉ mục làm việc ghi chậm đi.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm và bỏ so với bài nguồn</summary>

Bài nguồn liệt kê sáu cách (tiêu đề ghi năm) mà không giải thích. Bài này gắn mỗi cách với khúc thời gian nó cắt, thêm bước đo, và đo hai cách trên một máy.
Bài nguồn mở đầu bằng một con số về doanh thu bị mất vì độ trễ; bài này bỏ con số đó vì không có nguồn để đối chiếu.
Số đo chỉ là minh họa của một máy với dữ liệu thử; tỷ lệ nén và mức tăng tốc của chỉ mục phụ thuộc dữ liệu thật của bạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-5-strategies-to-reduce-latency.md): sáu cách giảm độ trễ.
- [PostgreSQL — chương về chỉ mục, tại commit cố định](https://github.com/postgres/postgres/blob/45fc51fcbf4534ea2f6f85e36f8155dbd5ba9851/doc/src/sgml/indices.sgml): chỉ mục giúp tìm dòng nhanh hơn nhiều nhưng thêm gánh nặng cho hệ thống.
- [IETF HTTP Working Group — RFC 9110, bản XML tại commit cố định](https://github.com/httpwg/httpwg.github.io/blob/03f35d852e7b64668ab08fda1a8076d6d44d17ae/specs/rfc9110.xml): content coding dùng để nén nội dung mà không mất thông tin; mã `gzip` (mục 8.4).

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày. Bài viết và hình được thiết kế độc lập.

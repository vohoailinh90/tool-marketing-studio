# Cơ sở dữ liệu chuỗi thời gian: dữ liệu được gom theo series

**Nhìn từ ngoài, dữ liệu trong một cơ sở dữ liệu chuỗi thời gian (TSDB) trông như một bảng: mỗi dòng một thời điểm.**
Bên trong, InfluxDB không lưu theo dòng mà gom các giá trị cùng nguồn, cùng đại lượng thành một *series*, rồi lưu mỗi series thành một chuỗi giá trị theo thời gian. Cách gom đó quyết định cả tốc độ lẫn cái bẫy lớn nhất khi thiết kế.

![Ba khung. Khung một là bốn phần của một điểm dữ liệu: measurement weather; tag location, được đánh chỉ mục; field temperature và humidity, không được đánh chỉ mục; và thời điểm. Khung hai là ba bước từ điểm thành series: ghép measurement, tag set và tên field thành khóa series; hai địa điểm nhân hai field ra 4 series cho 17.280 điểm một ngày; mỗi series là một chuỗi cặp thời điểm và giá trị, lưu nén theo cột trong tệp TSM. Khung ba là số đo bằng zlib: dạng dòng văn bản nén còn 70.217 byte; theo series, lưu hiệu số giữa các giá trị liền nhau, nén còn 14.064 byte; nếu đưa mã đo duy nhất vào tag thì một ngày có 34.560 series.](../../diagrams/sd-04-011-main.svg)

## Từ viết tắt

- **TSDB** (Time Series DataBase) — cơ sở dữ liệu chuỗi thời gian: loại cơ sở dữ liệu tối ưu cho các giá trị gắn với thời điểm, như số đo cảm biến hay số liệu máy chủ.
- **DB** (DataBase) — cơ sở dữ liệu; nằm trong tên InfluxDB.
- **TSM** (Time-Structured Merge) — tên kiểu cấu trúc lưu trữ (TSM tree) của InfluxDB: các tệp chỉ đọc chứa dữ liệu series đã sắp xếp và nén theo cột.
- **WAL** (Write-Ahead Log) — nhật ký ghi trước: điểm mới được ghi nối vào tệp này trước, để không mất khi máy sập, rồi mới được gom vào tệp TSM.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: điểm cuối mà chương trình khác gọi tới; ở câu hỏi cuối bài, thứ được đo thời gian phản hồi.

## Đọc hình

**Khung 1 · Một điểm.** Theo tài liệu InfluxDB 1.x, một điểm (point) có bốn phần: measurement (tên nhóm dữ liệu), tag set (các cặp tên và giá trị dạng chuỗi mô tả nguồn đo), field set (các giá trị đo được) và thời điểm.
Tag được đánh chỉ mục, field thì không: lọc theo một giá trị field buộc InfluxDB quét mọi giá trị của field đó.

**Khung 2 · Series.** Series là tập điểm có chung measurement, tag set và tên field. Một ngày đo thời tiết mỗi 10 giây ở hai địa điểm, mỗi lần hai đại lượng, cho 17.280 điểm nhưng chỉ 4 series; mỗi series có 8.640 cặp thời điểm và giá trị.
Bộ máy lưu trữ của InfluxDB ghi trước vào WAL và một bộ đệm trong bộ nhớ, sau đó chuyển thành tệp TSM chứa dữ liệu series đã sắp xếp, nén theo cột.

## Thử nghiệm: vì sao gom theo series lại nén tốt

Không chạy InfluxDB; chỉ dựng cùng một ngày dữ liệu giả lập theo hai cách rồi nén bằng zlib để thấy ý tưởng (InfluxDB có bộ mã hóa riêng cho từng kiểu dữ liệu, không phải zlib).

| Cách lưu | Trước nén | Sau zlib |
|---|---|---|
| Mỗi điểm một dòng văn bản theo cú pháp line protocol | 1.240.743 byte | 70.217 byte |
| Mỗi series một cột, lưu hiệu số giữa hai thời điểm và hai giá trị liền nhau | 552.960 byte | 14.064 byte |

Thời điểm cách đều 10 giây nên hiệu số luôn là 10; nhiệt độ mỗi lần chỉ đổi 0,1 độ. Đặt các giá trị cùng series cạnh nhau thì những lặp lại đó lộ ra cho bộ nén.

## Giới hạn cần nhớ

Mỗi tổ hợp tag mới là một series mới. Tài liệu InfluxDB dặn không đưa giá trị thay đổi liên tục (mã định danh duy nhất, chuỗi băm, chuỗi ngẫu nhiên) vào tag, vì số series tăng vọt (series cardinality cao) là nguyên nhân chính làm tốn bộ nhớ và chậm đọc ghi. Trong ví dụ trên, đưa một mã đo duy nhất vào tag biến 4 series thành 34.560 series chỉ sau một ngày.

## Nhìn hình trả lời

Một đội lưu thời gian phản hồi của API, và muốn lọc theo tên máy chủ (vài chục máy) và theo mã yêu cầu (mỗi yêu cầu một mã). Cái nào nên là tag, cái nào nên là field?

<details>
<summary>Xem đáp án</summary>

Tên máy chủ nên là tag: ít giá trị, hay dùng để lọc và gom nhóm, và cần được đánh chỉ mục. Mã yêu cầu nên là field: mỗi yêu cầu một giá trị mới, nên làm tag sẽ sinh ra một series cho mỗi yêu cầu.
Cái giá là lọc theo mã yêu cầu sẽ phải quét, vì field không có chỉ mục. Nếu việc tra theo mã yêu cầu là thường xuyên, chỗ của nó là một hệ lưu nhật ký hay truy vết, không phải TSDB.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn nói bảng thời tiết "được lưu trong 4 TSM theo dạng [Measurement, Tag, Field Name]". Theo tài liệu InfluxDB, bốn thứ đó là bốn series, còn TSM là các tệp chứa dữ liệu của nhiều series; số tệp TSM không bằng số series.
Bài nguồn liệt kê bảy cách dùng (dữ liệu thị trường, số liệu máy chủ, giám sát hiệu năng ứng dụng…); bài này không lặp lại danh sách đó.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/time-series-db-tsdb-in-20-lines.md): mô hình dữ liệu bên trong của một TSDB, các trường hợp dùng.
- [InfluxDB 1.x — Key concepts, tại commit cố định](https://github.com/influxdata/docs-v2/blob/3c30e2b5ddcfd1320a745eafee6fb9afccb7e97c/content/influxdb/v1/concepts/key_concepts.md): measurement, tag, field, điểm, series; tag có chỉ mục, field thì không. Đọc từ bản clone của kho.
- [InfluxDB 1.x — Schema design and data layout](https://github.com/influxdata/docs-v2/blob/3c30e2b5ddcfd1320a745eafee6fb9afccb7e97c/content/influxdb/v1/concepts/schema_and_data_layout.md): tránh quá nhiều series, không đưa giá trị biến thiên mạnh vào tag.
- [InfluxDB 1.x — In-memory indexing and the TSM](https://github.com/influxdata/docs-v2/blob/3c30e2b5ddcfd1320a745eafee6fb9afccb7e97c/content/influxdb/v1/concepts/storage_engine.md): WAL, bộ đệm, tệp TSM nén theo cột.

Đã đọc nguồn và chạy phép thử nén ngày 2026-10-18 bằng Python; dữ liệu là giả lập, không phải số đo thật.
Bài viết và hình được thiết kế độc lập.

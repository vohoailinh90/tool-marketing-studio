# Chọn cơ sở dữ liệu cho hệ thống số đo

Thay vì hỏi "dùng loại nào", hãy trả lời bốn câu hỏi về dữ liệu của bạn; đáp án sẽ cho thấy kho nào đáng cân nhắc.

![Bốn câu hỏi xếp dọc: tốc độ ghi, kiểu truy vấn, thời gian giữ dữ liệu và số chuỗi cùng người vận hành.](../../diagrams/sd-13-005-main.svg)

**Đọc hình:** câu trả lời chứ không phải tên sản phẩm là thứ quyết định; sản phẩm cụ thể ở phần sâu.

## Từ viết tắt

- **ID** (IDentifier) — mã định danh: chuỗi hoặc số dùng để phân biệt một đối tượng với các đối tượng khác, ví dụ một người dùng, một thông điệp hay một lượt xử lý.
- **TSDB** (Time Series DataBase) — cơ sở dữ liệu chuỗi thời gian: kho chuyên lưu các số đo theo thời gian, như kho của Prometheus.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức để ghi và tìm lại nhanh; InfluxDB và TimescaleDB là hai cơ sở dữ liệu chuỗi thời gian.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là hệ cơ sở dữ liệu dùng nó.

## Nhìn hình thử trả lời

`http_requests{service="a", code="200"}` và `http_requests{service="a", code="500"}` là một hay hai chuỗi?

<details>
<summary>Xem đáp án</summary>

Hai chuỗi. Chuỗi được xác định bởi tên cộng toàn bộ bộ nhãn; đổi giá trị một nhãn là sinh ra chuỗi mới.

</details>

## Giới hạn cần nhớ

Chuẩn bị cho số chuỗi quan trọng hơn chọn thương hiệu: nhãn mang giá trị gần như duy nhất (như ID người dùng, trong đó ID là identifier — mã định danh) làm số chuỗi phình ra, kho nào cũng chậm. Quy mô nhỏ thì một cơ sở dữ liệu đa dụng thiết kế cẩn thận vẫn có thể đủ.

<details>
<summary>Xem sâu hơn</summary>

- **Dữ liệu chuỗi thời gian** là các điểm (thời gian, giá trị) gắn với một chuỗi xác định bởi tên và nhãn. Truy vấn thường là "trong khoảng này, tổng hợp theo nhãn".
- **Kho chuyên dụng** như Prometheus TSDB (Time Series Database — cơ sở dữ liệu chuỗi thời gian) hay InfluxDB tối ưu việc ghi liên tục, nén và hết hạn dữ liệu. Có sản phẩm thêm khả năng chuỗi thời gian lên cơ sở dữ liệu quan hệ (ví dụ TimescaleDB trên PostgreSQL).
- **Cơ sở dữ liệu đa dụng:** làm được khi tải vừa phải, nhưng truy vấn cửa sổ thời gian dài dòng hơn và phải tự tinh chỉnh chỉ mục, phân vùng.
- **Cách kiểm tra:** thử với tải ghi và truy vấn gần thật trước khi chốt.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/choose-the-right-database-for-metric-collecting-system.md).
- Prometheus: [mô hình dữ liệu](https://prometheus.io/docs/concepts/data_model/), [đặt tên và nhãn](https://prometheus.io/docs/practices/naming/).
- InfluxDB: [tài liệu](https://docs.influxdata.com/); Timescale: [tài liệu](https://docs.timescale.com/).

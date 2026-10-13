# Chọn cơ sở dữ liệu cho hệ thống số đo

Số đo là dữ liệu theo thời gian, ghi liên tục và đọc theo đợt, nên kho chuyên dụng thường hợp hơn kho đa dụng.

![Ba thẻ xếp dọc: dữ liệu là nhiều chuỗi theo thời gian, ghi nhiều và đọc dồn theo đợt, từ đó nên cân nhắc cơ sở dữ liệu chuỗi thời gian.](../../diagrams/sd-13-005-main.svg)

**Đọc hình:** thẻ cuối là hướng chọn ban đầu, không thay cho việc thử với tải thật.

## Nhìn hình thử trả lời

Hai số đo `http_requests{dịch_vụ="a", mã="200"}` và `http_requests{dịch_vụ="a", mã="500"}` là một hay hai chuỗi?

<details>
<summary>Xem đáp án</summary>

Hai chuỗi. Chuỗi được xác định bởi tên cộng toàn bộ bộ nhãn; đổi giá trị một nhãn là sinh ra chuỗi mới.

</details>

## Giới hạn cần nhớ

Không phải lúc nào cũng cần kho chuyên dụng: với quy mô nhỏ, một cơ sở dữ liệu đa dụng được thiết kế cẩn thận vẫn đủ. Rủi ro lớn hơn thường là số chuỗi quá nhiều (nhãn mang giá trị gần như duy nhất, như ID người dùng), làm kho phình và truy vấn chậm.

<details>
<summary>Xem sâu hơn</summary>

- **Vì sao đa dụng khó hơn:** truy vấn kiểu cửa sổ thời gian (trung bình trượt, tốc độ tăng) viết dài trong SQL thường; thêm nhãn nghĩa là thêm chỉ mục; tải ghi liên tục cần tinh chỉnh.
- **NoSQL đa dụng:** Cassandra hay Bigtable lưu được dữ liệu chuỗi thời gian nhưng bạn phải tự thiết kế lược đồ cho truy vấn.
- **Kho chuyên dụng:** có sẵn nén, hạ độ phân giải, hết hạn dữ liệu. Ví dụ: Prometheus TSDB, InfluxDB; một số dùng phần mở rộng trên cơ sở dữ liệu quan hệ.
- **Cardinality:** tài liệu Prometheus cảnh báo mỗi tổ hợp nhãn khác nhau là một chuỗi mới.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/choose-the-right-database-for-metric-collecting-system.md).
- Prometheus: [mô hình dữ liệu](https://prometheus.io/docs/concepts/data_model/), [đặt tên và nhãn](https://prometheus.io/docs/practices/naming/).

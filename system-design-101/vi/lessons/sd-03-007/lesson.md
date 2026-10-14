# Tổng quan về đường ống dữ liệu

**Đường ống dữ liệu là chuỗi bước đưa dữ liệu từ nơi nó sinh ra tới nơi nó được dùng.**
Năm giai đoạn thường gặp là thu thập, nạp, lưu trữ, tính toán và sử dụng. Hình dưới theo một cửa hàng trực tuyến.

![Năm thẻ nối nhau từ trên xuống, ví dụ cửa hàng trực tuyến. 1 Thu thập: ứng dụng tạo sự kiện đơn hàng. 2 Nạp dữ liệu: vào hàng đợi hoặc nạp theo lô. 3 Lưu trữ: data lake giữ bản thô, data warehouse giữ bảng sạch. 4 Tính toán: làm sạch, gộp, tổng hợp theo lô hoặc theo luồng. 5 Sử dụng: bảng điều khiển, báo cáo, mô hình học máy. Thẻ cuối nêu lỗi hay gặp: gửi lại sau lỗi làm trùng dòng, nên thiết kế bước chạy lại được.](../../diagrams/sd-03-007-main.svg)

## Đọc hình

**1 · Thu thập.** Dữ liệu sinh ra ở ứng dụng, thiết bị hoặc hệ thống nghiệp vụ. Ở đây: mỗi đơn hàng tạo một sự kiện.

**2 · Nạp dữ liệu.** Đưa dữ liệu vào hệ thống xử lý, thường qua hàng đợi sự kiện, hoặc nạp từng lô theo lịch.

**3 · Lưu trữ.** Giữ bản thô trong data lake để có thể xử lý lại, và bảng đã làm sạch trong data warehouse hoặc cơ sở dữ liệu.

**4 · Tính toán.** Làm sạch, gộp, tổng hợp, đổi định dạng. Có thể chạy theo **lô** (xử lý khối dữ liệu theo lịch)
hoặc theo **luồng** (xử lý từng sự kiện khi đến).

**5 · Sử dụng.** Kết quả phục vụ báo cáo, bảng điều khiển, ứng dụng hướng người dùng và mô hình học máy.

## Giới hạn cần nhớ

Khi một bước lỗi, hệ thống thường gửi lại dữ liệu, và dữ liệu có thể đến hai lần. Hàng đợi như Kafka nêu rõ
ba mức đảm bảo: tối đa một lần, ít nhất một lần và đúng một lần; mức “ít nhất một lần” có thể sinh bản trùng.
Vì vậy hãy thiết kế bước xử lý chạy lại được mà không đếm đôi: dùng khóa duy nhất, ghi đè theo khóa hoặc khử trùng.

## Nhìn hình trả lời

Một đơn hàng được gửi lại hai lần sau lỗi mạng. Ở giai đoạn nào bạn nên khử bản trùng, và vì sao không chỉ tin vào bước nạp?

<details>
<summary>Xem đáp án</summary>

Ở bước tính toán, hoặc ngay khi ghi vào kho, bằng khóa duy nhất như mã đơn. Bước nạp có thể được cấu hình để tránh
trùng, nhưng lỗi ở các bước sau cũng có thể làm dữ liệu chạy lại, nên không nên chỉ dựa vào một chỗ.

</details>

<details>
<summary>Xem sâu hơn: lô hay luồng?</summary>

Xử lý theo lô đơn giản và thường rẻ hơn, hợp với báo cáo cuối ngày. Xử lý theo luồng cho kết quả gần thời gian thực
nhưng phải xử lý thêm thứ tự sự kiện và dữ liệu đến muộn. Nhiều hệ thống dùng cả hai.

Exactly-once của Kafka nhờ producer idempotent và giao dịch chỉ bảo đảm trong phạm vi Kafka; một thao tác bên ngoài,
như ghi vào cơ sở dữ liệu khác hay gọi API, vẫn cần được thiết kế để không lặp.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/data-pipelines-overview.md): năm giai đoạn.
- [Confluent — Kafka message delivery guarantees](https://docs.confluent.io/kafka/design/delivery-semantics.html): ba mức đảm bảo, producer idempotent, giao dịch. Trang không mở được; nội dung đối chiếu qua trích đoạn tìm kiếm.
- [Google Cloud — Data lake](https://cloud.google.com/learn/what-is-a-data-lake) và [Data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse): vai trò của nơi lưu trữ.

Đã đọc nguồn ngày 2026-10-13. Bài viết và hình được thiết kế độc lập. Ví dụ cửa hàng trực tuyến do bài này đặt ra;
nó không phải một hệ thống thật.

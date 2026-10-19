# Vì sao Kafka nhanh: ghi nối tiếp, gom lô, gửi thẳng từ page cache

**Tài liệu thiết kế của Kafka nêu hai nguồn lãng phí chính sau khi đã bỏ kiểu truy cập đĩa xấu: quá nhiều thao tác vào ra nhỏ, và chép byte quá nhiều lần.**
Kafka trả lời bằng ba quyết định trong khung 1. Bài này đo hai trong số đó trên một cụm Kafka nhỏ.

![Ba khung. Khung một, ba quyết định: ghi nối vào cuối tệp nhật ký để đĩa chỉ làm việc tuần tự; gom nhiều tin thành một lô cho mỗi yêu cầu, nén chung và giữ nguyên dạng trên đĩa; gửi thẳng từ page cache ra socket bằng sendfile, không qua bộ nhớ của tiến trình Kafka. Khung hai, đường thường khi gửi tệp ra mạng: đĩa vào page cache, sang bộ đệm của ứng dụng, vào bộ đệm socket, ra card mạng; sendfile chỉ giữ bước cuối. Khung ba, số đo một lần chạy: 50.000 tin 100 byte, mỗi yêu cầu một tin, mất 8,30 giây với 50.000 yêu cầu; gom lô thì 0,07 giây với 11 yêu cầu; một consumer đọc 100.000 tin thì broker gửi bằng 68 lời gọi sendfile; bật TLS thì Kafka không dùng sendfile.](../../diagrams/sd-04-009-main.svg)

## Từ viết tắt

- **TLS** (Transport Layer Security) — bảo mật tầng giao vận: giao thức mã hóa kết nối mạng; khi bật nó, Kafka phải mã hóa dữ liệu trong tiến trình nên không gửi thẳng từ page cache được nữa.
- **SSL** (Secure Sockets Layer) — tầng ổ cắm an toàn: tên cũ của giao thức mà TLS kế thừa; tài liệu Kafka gọi chung là SSL/TLS.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng cỡ một triệu byte; dùng cho cỡ tệp nhật ký và lượng dữ liệu broker gửi đi.

## Đọc hình

**Ghi nối vào cuối tệp.** Nhật ký của mỗi partition là các tệp chỉ được ghi thêm vào cuối. Tài liệu Kafka lập luận rằng đọc ghi tuần tự là kiểu dễ đoán nhất, được hệ điều hành tối ưu bằng đọc trước và gom ghi; mọi thao tác thành O(1) thay vì phải đi trên cây chỉ mục.
Kafka để dữ liệu trong page cache của hệ điều hành thay vì giữ bộ đệm riêng trong máy ảo Java, nên cache vẫn còn khi tiến trình khởi động lại.

**Gom tin thành lô.** Giao thức của Kafka xoay quanh "message set": nhiều tin đi chung một yêu cầu, broker ghi cả cụm vào nhật ký một lần, consumer lấy về từng khúc lớn. Lô có thể được nén chung và giữ nguyên dạng nén trên đĩa lẫn khi gửi tới consumer.

**Gửi thẳng từ page cache.** Đường thường để gửi một tệp ra mạng có bốn lần chép và hai lời gọi hệ thống (khung 2). Lời gọi `sendfile` của Linux cho phép nhân gửi dữ liệu từ page cache ra mạng mà không đưa qua bộ nhớ của ứng dụng. Điều này làm được vì producer, broker và consumer dùng chung một định dạng nhị phân, nên broker không phải sửa gì trước khi gửi.

## Thử nghiệm: đo hai quyết định

Cụm ba broker Kafka 4.4.0 trên một máy, topic `clicks` một partition, producer và consumer dùng thư viện confluent-kafka 2.16.0.

| Phép đo | Kết quả |
|---|---|
| 50.000 tin 100 byte, ép mỗi yêu cầu một tin (`batch.num.messages=1`) | 8,30 giây, 50.000 yêu cầu Produce |
| Cùng số tin, cho producer chờ 5 mili giây để gom lô (`linger.ms=5`, cũng là mặc định của librdkafka) | 0,07 giây, 11 yêu cầu Produce |
| Theo dõi broker bằng `strace` khi một consumer đọc 100.000 tin (tệp nhật ký 14,0 MB) | 68 lời gọi `sendfile`, tổng 15,6 MB |

Số yêu cầu lấy từ số liệu thống kê của thư viện. Chạy trên một máy nên mạng gần như không tốn thời gian; trên mạng thật, mỗi yêu cầu còn mất thêm một vòng đi về, nên gom lô càng có lợi.

## Giới hạn cần nhớ

- Gom lô đổi độ trễ lấy thông lượng: `linger.ms` là thời gian mỗi tin có thể phải chờ trước khi đi.
- Tài liệu Kafka ghi rõ: khi bật SSL/TLS, thư viện mã hóa chạy trong tiến trình, nên Kafka không dùng `sendfile`. Bài nguồn không nhắc điều này.
- Đọc thẳng từ page cache chỉ đúng khi consumer theo kịp; consumer đọc lại dữ liệu cũ đã rời khỏi cache thì broker phải đọc đĩa.

## Nhìn hình trả lời

Một đội thấy producer của mình chỉ gửi được vài nghìn tin mỗi giây dù broker còn rảnh. Cấu hình đang ép mỗi yêu cầu một tin để "tin đi ngay". Theo khung 1 và số đo ở khung 3, nên đổi gì, và đánh đổi điều gì?

<details>
<summary>Xem đáp án</summary>

Cho producer gom lô: bỏ giới hạn một tin mỗi yêu cầu và đặt `linger.ms` vài mili giây. Trong thử nghiệm, cùng 50.000 tin đi trong 11 yêu cầu thay vì 50.000, nhanh hơn hơn trăm lần.
Cái giá là mỗi tin có thể chờ thêm tới `linger.ms` trước khi được gửi; với phần lớn hệ thống, vài mili giây là chấp nhận được.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn chọn hai lý do là I/O tuần tự và zero copy, và mô tả bước 3.2 là "page cache chép thẳng vào card mạng qua lệnh `sendfile()`". Tài liệu Kafka thêm lý do thứ ba (gom lô, nén theo lô) và nói rõ chỉ còn lần chép cuối sang bộ đệm của card mạng.
Số liệu đĩa trong tài liệu Kafka (ghi tuần tự khoảng 600 MB/giây so với ghi ngẫu nhiên khoảng 100 kB/giây trên một dàn đĩa cụ thể) là phép đo cũ của tác giả tài liệu; bài này không đo lại.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/why-is-kafka-fast.md): I/O tuần tự và zero copy, đường dữ liệu có và không có zero copy.
- [Apache Kafka — Design, các mục Persistence và Efficiency, tại commit cố định](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/design/design.md): page cache, cấu trúc chỉ ghi thêm, message set và gom lô, bốn lần chép và `sendfile`, nén theo lô, không dùng `sendfile` khi bật SSL. Đọc từ bản clone của kho.
- [librdkafka — CONFIGURATION.md, tại commit cố định](https://github.com/confluentinc/librdkafka/blob/8c03f75a31ca61d08b2cc2ddc5b233b80d14bdad/CONFIGURATION.md): các tham số `linger.ms` và `batch.num.messages` của producer.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên Kafka 4.4.0, ba broker trên một máy; số đo là một lần chạy, chỉ để so sánh tương đối.
Bài viết và hình được thiết kế độc lập.

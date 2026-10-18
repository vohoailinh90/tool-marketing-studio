# Kafka nhập môn: theo bảy đơn hàng đi qua một cụm ba máy

**Kafka là một nhật ký sự kiện chạy trên nhiều máy: bên ghi nối sự kiện vào cuối, bên đọc tự giữ chỗ mình đã đọc tới.**
Bài này không kể định nghĩa lần lượt mà dựng một cụm Kafka nhỏ, gửi bảy đơn hàng, rồi xem mỗi khái niệm hiện ra ở đâu.

![Ba khung. Khung một, bốn bước của một sự kiện: producer gửi sự kiện có khóa, giá trị và thời điểm, khóa là tên khách; cùng khóa luôn vào cùng partition, an và binh vào partition 2, chi vào partition 0; sự kiện được nối vào cuối partition và nhận offset tăng dần; mỗi partition có một leader nhận ghi và hai bản sao ở hai broker kia. Khung hai, hai nhóm đọc: nhóm billing có hai thành viên, một được giao partition 0 và 1 và đọc 2 sự kiện, một được giao partition 2 và đọc 5 sự kiện; nhóm email có một thành viên được giao cả ba partition và đọc đủ 7. Khung ba: thứ tự chỉ giữ trong một partition; mỗi partition chỉ giao cho một thành viên của mỗi nhóm; ít khóa thì dễ lệch, partition 1 trống.](../../diagrams/sd-04-006-main.svg)

## Từ viết tắt

- **CRC** (Cyclic Redundancy Check) — kiểm tra dư vòng: một hàm tính ra con số ngắn từ dữ liệu; CRC32 cho ra số 32 bit, ở đây dùng để chia khóa vào partition.
- **SHA** (Secure Hash Algorithm) — họ hàm băm an toàn; SHA-512 dùng để kiểm bản Kafka tải về không bị sửa.

## Thử nghiệm làm nền cho hình

Ba broker Kafka 4.4.0 chạy trên cùng một máy (mỗi máy chủ Kafka gọi là một broker). Topic `orders` có 3 partition, mỗi partition 3 bản sao. Một producer viết bằng thư viện confluent-kafka cho Python gửi bảy đơn hàng, khóa là tên khách: `an` ba đơn, `binh` hai đơn, `chi` hai đơn.

| Khóa | Đơn | Partition | Offset |
|---|---|---|---|
| `chi` | order-3, order-6 | 0 | 0, 1 |
| `an`, `binh` xen kẽ | order-1, 2, 4, 5, 7 | 2 | 0 tới 4 |

Partition 1 không nhận đơn nào. Mỗi partition có một broker làm leader (partition 0 ở broker 2, partition 1 ở broker 3, partition 2 ở broker 1) và hai bản sao còn lại ở hai broker kia.

## Đọc hình

**Sự kiện.** Tài liệu Kafka gọi một bản ghi là sự kiện (event, cũng gọi là record hay message): có khóa, giá trị, thời điểm và có thể kèm header.

**Topic và partition.** Sự kiện được xếp vào topic, và mỗi topic chia thành nhiều partition nằm trên các broker khác nhau. Sự kiện cùng khóa được ghi vào cùng partition, và Kafka bảo đảm bên đọc một partition đọc đúng thứ tự đã ghi. Vị trí của sự kiện trong partition là offset.

**Bản sao.** Mỗi partition có một leader và các follower; mọi lệnh ghi đi vào leader. Tài liệu Kafka nói hệ số sao chép 3 là thiết lập thường gặp khi chạy thật.

**Nhóm đọc (consumer group).** Mỗi partition chỉ được giao cho đúng một thành viên trong mỗi nhóm tại một thời điểm. Nhóm `billing` có hai thành viên nên chia nhau các partition; nhóm `email` có một thành viên nên nhận cả ba và đọc đủ bảy đơn. Đọc xong, sự kiện không bị xóa: Kafka giữ chúng theo thời hạn cấu hình của topic.

## Giới hạn cần nhớ

- **Thứ tự chỉ có trong một partition.** Muốn các đơn của một khách luôn theo thứ tự thì đặt khóa là mã khách; hai khách khác nhau thì không có thứ tự chung.
- **Khóa quyết định độ đều.** Ba khóa chia vào ba partition không bảo đảm mỗi partition một khóa: ở đây hai khóa rơi vào cùng partition 2, partition 1 bỏ không, và thành viên giữ partition 2 phải làm 5 trên 7 đơn.
- **Thêm thành viên không vượt quá số partition.** Vì mỗi partition chỉ thuộc một thành viên của nhóm, nhóm có nhiều thành viên hơn số partition thì có thành viên ngồi không.

## Nhìn hình trả lời

Nhóm `billing` xử lý chậm, nên đội vận hành tăng nhóm lên năm thành viên mà vẫn giữ topic 3 partition. Đơn có được xử lý nhanh hơn không?

<details>
<summary>Xem đáp án</summary>

Nhiều nhất ba thành viên có việc, vì mỗi partition chỉ giao cho một thành viên của nhóm; hai thành viên còn lại ngồi không. Trong thử nghiệm này còn tệ hơn: partition 1 trống, nên chỉ hai thành viên thật sự làm việc.
Muốn đọc song song nhiều hơn thì phải có nhiều partition hơn, và khóa phải đủ đa dạng để sự kiện trải đều.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn đi qua tám mục định nghĩa: Kafka là gì, message, topic và partition, ưu điểm, producer, consumer, cụm và các trường hợp dùng.
Bài này giữ các khái niệm đó nhưng dựng chúng từ một thử nghiệm, và thêm hai điều bài nguồn không nói: thứ tự chỉ có trong một partition, và số partition giới hạn số thành viên làm việc được trong một nhóm.

Theo tài liệu cấu hình của librdkafka (thư viện C mà confluent-kafka dùng bên dưới), mặc định nó chọn partition bằng hàm băm CRC32 của khóa, còn producer Java của Kafka dùng Murmur2; librdkafka có tùy chọn `murmur2_random` để chọn giống producer Java. Hai chương trình ghi cùng topic bằng hai thư viện có thể đưa cùng một khóa vào hai partition khác nhau, nên khi trộn thư viện hãy đặt cùng hàm chọn partition. Và chỉ khi số partition không đổi thì cùng khóa mới luôn vào cùng partition.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-ultimate-kafka-101-you-cannot-miss.md): tám bước làm quen Kafka.
- [Apache Kafka — Introduction, tại commit cố định](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/getting-started/introduction.md): sự kiện có khóa, giá trị, thời điểm và header; topic, partition, cùng khóa cùng partition, thứ tự trong partition; không xóa sau khi đọc; hệ số sao chép 3 thường gặp. Đọc từ bản clone của kho.
- [librdkafka — CONFIGURATION.md, tại commit cố định](https://github.com/confluentinc/librdkafka/blob/8c03f75a31ca61d08b2cc2ddc5b233b80d14bdad/CONFIGURATION.md): tham số `partitioner`, mặc định `consistent_random` (CRC32 của khóa), `murmur2_random` tương đương producer Java. Đọc từ bản clone của kho.
- [Apache Kafka — Design, tại commit cố định](https://github.com/apache/kafka/blob/65566690ca1ddb584388c1026e2ff6673e9c6f19/docs/design/design.md): mỗi partition do đúng một thành viên của mỗi nhóm đọc; mỗi partition một leader, mọi lệnh ghi vào leader.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên Kafka 4.4.0 (bản tải từ trang phát hành của Apache, đã so mã SHA-512), ba broker trên một máy, thư viện confluent-kafka 2.16.0.
Bài viết và hình được thiết kế độc lập.

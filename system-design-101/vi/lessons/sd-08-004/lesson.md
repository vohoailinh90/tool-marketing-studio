# Prime Video gộp về một khối: khi ranh giới giữa các thành phần quá đắt

**Theo bài nguồn, đội giám sát chất lượng luồng của Prime Video chuyển từ nhiều thành phần chạy rời nhau sang gộp hai bước vào cùng một tiến trình và giảm được 90% chi phí.**
Bài này không bàn "dùng khối hay dùng dịch vụ nhỏ" nói chung mà chỉ ra chỗ tiền bị tiêu: mỗi lần dữ liệu hoặc lệnh đi qua ranh giới giữa hai thành phần đều có giá, và thử đo xem giá đó lớn cỡ nào khi dữ liệu nặng.

![Ba khung. Khung một, trước khi đổi: bộ chuyển đổi phương tiện, kho đối tượng lưu dữ liệu trung gian, bộ dò lỗi tải dữ liệu về, rồi thông báo thời gian thực, do một quy trình điều phối trả tiền theo từng lần chuyển trạng thái. Khung hai, sau khi đổi: bộ chuyển đổi và bộ dò lỗi chạy chung một tiến trình, rồi thông báo; dữ liệu giữa hai bước không phải đi qua mạng. Khung ba, thử trên một máy: chuyển 16 mebibyte sang tiến trình khác mất 7 đến 12 ms, chuyển 1 mebibyte mất khoảng 0,4 đến 1,2 ms, còn trao một tham chiếu trong cùng tiến trình gần như bằng 0.](../../diagrams/sd-08-004-main.svg)

## Từ viết tắt

- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: kiểu kết nối đáng tin cậy giữa hai chương trình, ở đây dùng qua địa chỉ nội bộ của máy để chuyển dữ liệu sang tiến trình khác.

## Đọc hình

Dịch vụ giám sát của Prime Video phân tích các luồng phát trực tiếp theo thời gian thực để tìm lỗi chất lượng như khối hình hỏng, hình đứng và lệch tiếng. Có ba bước: chuyển đổi phương tiện, dò lỗi, thông báo thời gian thực.

**Trước.** Theo bài nguồn, kiến trúc cũ xây trên Lambda (chạy từng hàm riêng theo yêu cầu), nhanh để dựng nhưng đắt khi chạy ở quy mô lớn. Hai thao tác đắt nhất: một quy trình điều phối (Step Functions của Amazon) tính tiền theo số lần chuyển trạng thái, mà quy trình này chuyển trạng thái nhiều lần mỗi giây; và dữ liệu trung gian được lưu trong kho đối tượng để bước sau tải về, nên khối lượng lớn thì việc tải này tốn kém. Tài liệu của Step Functions xác nhận cách tính tiền: gói Standard tính theo số lần chuyển trạng thái, mỗi lần một bước trong lần chạy hoàn tất thì tính một lần; còn gói Express tính theo số lần chạy, thời gian chạy và bộ nhớ.

**Sau.** Vẫn ba thành phần, nhưng bộ chuyển đổi và bộ dò lỗi chạy chung một tiến trình, nên dữ liệu giữa hai bước không phải đi qua mạng hay qua kho lưu trữ nữa. Bài nguồn viết là cách đổi này cắt 90% chi phí.

## Thử: chuyển dữ liệu qua ranh giới tốn bao nhiêu

Ngày 2026-10-19, trên một máy ảo 4 lõi, một chương trình Python chuyển một khối dữ liệu ngẫu nhiên từ "bước trước" sang "bước sau" bằng bốn cách, mỗi cỡ đo 15 lần lấy trung vị, chạy ba lượt. Mỗi ô ghi giá trị nhỏ nhất và lớn nhất trong ba lượt (một số ô chỉ có một giá trị vì ba lượt giống nhau).

| Cách chuyển | 1 mebibyte (ms) | 16 mebibyte (ms) |
|---|---|---|
| Trao tham chiếu trong một tiến trình | 0,0 | 0,0 |
| Sao chép một lần trong một tiến trình | 0,0 đến 0,1 | 1,3 đến 2,0 |
| Qua socket TCP nội bộ sang tiến trình khác | 0,4 đến 0,5 | 7,4 đến 9,4 |
| Ghi tệp trong bộ nhớ rồi tiến trình khác đọc | 0,7 đến 0,8 | 10,4 đến 12,1 |
| Ghi tệp trên đĩa rồi tiến trình khác đọc | 0,9 đến 1,2 | 7,3 đến 10,1 |

Hai điều đọc được. Một, trao tham chiếu trong cùng tiến trình gần như miễn phí, còn mọi cách qua ranh giới tiến trình đều tốn thời gian tỉ lệ với cỡ dữ liệu (khoảng nửa mili giây cho mỗi mebibyte trong thử này). Hai, đó chỉ mới là chi phí ở trên một máy: một kho đối tượng thật nằm qua mạng, mỗi lần tải còn tốn thêm độ trễ mạng và, theo bài nguồn, tiền cho khối lượng tải, mà phép thử này không đo được.

## Giới hạn cần nhớ

Phép thử không dựng lại hệ thống của Prime Video và không đo tiền; nó chỉ cho thấy một hướng: mỗi ranh giới giữa các thành phần đều thêm công việc tỉ lệ với lượng dữ liệu đi qua. Con số 90%, các trích dẫn của Werner Vogels (Giám đốc công nghệ của Amazon) và Adrian Cockcroft đều lấy theo bài nguồn; bài này chưa đọc được bài viết gốc của đội Prime Video nên chưa đối chiếu chúng. Cách tính tiền của Step Functions lấy từ bản tài liệu lưu năm 2022; giá và cách tính có thể đã đổi. Vì thế bài này không kết luận "gộp thành khối luôn rẻ hơn": ngay bài nguồn cũng chỉ nói chia thành các dịch vụ phân tán có cái giá của nó, và quyết định phải xét theo bài toán, như câu nói được trích của Werner Vogels rằng xây hệ thống tiến hóa được là một chiến lược chứ không phải một tôn giáo.

## Nhìn hình trả lời

Một hệ thống xử lý video gồm hai bước: bước 1 cắt video thành các khối 16 mebibyte, bước 2 phân tích từng khối. Hiện hai bước chạy ở hai dịch vụ riêng, khối được ghi vào kho lưu trữ rồi bước 2 tải về. Lượng video tăng gấp đôi thì chi phí chuyển dữ liệu thay đổi thế nào, và gộp hai bước vào một tiến trình thì thay đổi gì?

<details>
<summary>Xem đáp án</summary>

Chi phí chuyển dữ liệu tăng gần như gấp đôi, vì trong phép thử thời gian qua ranh giới tỉ lệ với số mebibyte đi qua (cỡ 7 đến 12 ms cho mỗi khối 16 mebibyte trên một máy, chưa kể mạng và phí kho lưu trữ). Gộp hai bước vào một tiến trình thì bước 2 nhận khối bằng tham chiếu, gần như không mất gì để chuyển. Đổi lại hai bước phải cùng chạy trên một máy, cùng phát hành và cùng mở rộng với nhau.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn kể câu chuyện Prime Video rồi nêu hai lời bình của lãnh đạo Amazon. Bài này giữ câu chuyện đó (kèm cách tính tiền của Step Functions từ tài liệu), nhưng đặt trọng tâm vào cơ chế chi phí ở ranh giới giữa các thành phần và thêm phép đo chuyển dữ liệu; số liệu 90% không được đối chiếu độc lập.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/amazon-prime-video-monitoring-service.md): kiến trúc trước và sau, 90% chi phí, lời của hai lãnh đạo Amazon.
- [AWS — Step Functions, so sánh gói Standard và Express](https://github.com/awsdocs/aws-step-functions-developer-guide/blob/fafab31876853bf715144cc1cd2445f3f4246d73/doc_source/concepts-standard-vs-express.md): cách tính tiền. Đọc từ bản clone của kho tại bản lưu trước khi kho ngừng cập nhật (2022).

Đã đọc nguồn ngày 2026-10-19. Phép đo là của người biên soạn, trên một máy ảo.
Bài viết và hình được thiết kế độc lập.

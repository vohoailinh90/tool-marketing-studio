# Discord lưu hàng nghìn tỷ tin nhắn thế nào

**Theo bài nguồn, Discord đã đổi nơi lưu tin nhắn hai lần: MongoDB, rồi Cassandra, rồi ScyllaDB; mỗi lần đổi là vì độ trễ không còn đoán trước được.**
Bài này đọc ba chặng đó theo con số của nguồn, rồi xem vì sao Cassandra chậm dần khi cụm máy lớn lên.

![Ba bước nối nhau. MongoDB, năm 2015: một bản sao duy nhất; khoảng tháng 11 năm 2015 có 100 triệu tin nhắn, bộ nhớ không còn chứa nổi dữ liệu và chỉ mục, độ trễ thất thường. Cassandra: năm 2017 có 12 máy và hàng tỷ tin nhắn; đầu năm 2022 có 177 máy và hàng nghìn tỷ tin nhắn, độ trễ lại thất thường. ScyllaDB: tương thích Cassandra, viết bằng C++, đi cùng một API khối nguyên và một dịch vụ dữ liệu viết bằng Rust. Khung hai: ba lý do Cassandra chậm. Khung ba: độ trễ p99 trước và sau.](../../diagrams/sd-02-029-main.svg)

## Từ viết tắt

- **RAM** (Random Access Memory) — bộ nhớ trong của máy chủ: nơi cơ sở dữ liệu giữ dữ liệu và chỉ mục để đọc nhanh.
- **LSM** (Log-Structured Merge) — cách lưu dữ liệu của Cassandra: ghi nối thêm cho nhanh, rồi định kỳ gộp các tệp lại; đổi lại, đọc tốn hơn ghi.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: ở đây là lớp mà ứng dụng Discord gọi để đọc và ghi tin nhắn.

## Đọc hình

**Ba chặng theo nguồn.**
1. **MongoDB.** Năm 2015, bản đầu tiên của Discord chạy trên một bản sao MongoDB duy nhất. Khoảng tháng 11 năm 2015, MongoDB giữ 100 triệu tin nhắn và RAM không còn chứa nổi dữ liệu cùng chỉ mục; độ trễ trở nên thất thường, nên tin nhắn phải chuyển sang cơ sở dữ liệu khác. Discord chọn Cassandra.
2. **Cassandra.** Năm 2017, Discord có 12 máy Cassandra và lưu hàng tỷ tin nhắn. Đầu năm 2022, cụm có 177 máy với hàng nghìn tỷ tin nhắn; độ trễ lại thất thường và việc bảo trì trở nên quá tốn kém.
3. **ScyllaDB.** ScyllaDB là cơ sở dữ liệu tương thích Cassandra, viết bằng C++. Discord thiết kế lại: một API khối nguyên, một dịch vụ dữ liệu viết bằng Rust, và phần lưu trữ trên ScyllaDB.

**Vì sao Cassandra chậm.** Nguồn nêu ba lý do:
- Cassandra dùng cây LSM, nên đọc tốn hơn ghi. Một máy phục vụ kênh có hàng trăm người có thể nhận nhiều lượt đọc cùng lúc, thành điểm nóng.
- Bảo trì cụm, như gộp (compaction) các tệp SSTable, làm giảm hiệu năng.
- Những lần dừng để dọn bộ nhớ (garbage collection) gây độ trễ tăng vọt.

**Kết quả theo nguồn.** Độ trễ đọc p99 của ScyllaDB là 15 ms, so với 40 đến 125 ms của Cassandra. Độ trễ ghi p99 là 5 ms, so với 5 đến 70 ms.

## Giới hạn cần nhớ

Các con số là của bài nguồn, không kèm cách đo hay tải lúc đo. Nguồn không nói việc chuyển dữ liệu từ Cassandra sang ScyllaDB làm thế nào, mất bao lâu, và không tách phần cải thiện nhờ ScyllaDB khỏi phần nhờ dịch vụ dữ liệu viết bằng Rust. "p99" nghĩa là 99% yêu cầu nhanh hơn con số đó; đây là cách đọc chung, không phải định nghĩa của nguồn.

## Nhìn hình thử trả lời

Một máy chủ Discord có kênh hàng trăm người cùng mở. Theo nguồn, vì sao trên Cassandra kênh đó dễ làm một máy bị quá tải, dù lượt ghi không nhiều?

<details>
<summary>Xem đáp án</summary>

Cassandra dùng cây LSM, nên đọc tốn hơn ghi. Hàng trăm người cùng mở kênh tạo nhiều lượt đọc dồn vào cùng máy giữ kênh đó, thành điểm nóng. Thêm vào đó là việc gộp tệp SSTable và những lần dừng để dọn bộ nhớ làm độ trễ tăng vọt.

</details>

<details>
<summary>Xem sâu hơn: vì sao cây LSM đọc tốn hơn ghi</summary>

- Ghi chỉ là nối thêm vào bộ nhớ rồi đổ ra một tệp mới, nên rất nhanh.
- Đọc có thể phải tìm trong nhiều tệp, vì bản mới nhất của một dòng nằm ở tệp nào thì chưa biết trước.
- Gộp tệp giảm số tệp phải tìm, nhưng chính việc gộp lại tốn ổ đĩa và bộ xử lý của máy đang phục vụ.

Đây là kiến thức chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-discord-stores-trillions-of-messages.md): ba chặng lưu tin nhắn, lý do và con số độ trễ.

Đã đọc nguồn ngày 2026-10-19. Bài kỹ thuật gốc của Discord chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

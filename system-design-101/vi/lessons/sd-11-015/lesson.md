# Hai mươi lăm bài báo kinh điển về hệ thống phân tán, xếp theo vấn đề chúng giải

**Hai mươi lăm bài báo này không nên đọc theo danh sách. Đọc theo vấn đề: bạn đang lưu dữ liệu, xử lý dữ liệu, giữ cho hệ thống nhìn thấy được, hay cần nền tảng lý thuyết?**
Chọn đúng nhóm trước, rồi mới chọn bài, bạn tránh việc mở một bài báo dài mà không biết nó trả lời câu hỏi nào của mình.

![Hai khung. Khung một, dữ liệu và xử lý: chín bài về lưu trữ và cơ sở dữ liệu, năm bài về xử lý và điều phối. Khung hai, còn lại: bốn bài về bộ nhớ đệm, quan sát và phân quyền, năm bài về nền tảng lý thuyết và công cụ, hai bài về ứng dụng cụ thể.](../../diagrams/sd-11-015-main.svg)

## Từ viết tắt

- **GFS** (Google File System) — hệ thống tệp của Google: lưu tệp rất lớn trên nhiều máy rẻ tiền.
- **LSM** (Log-Structured Merge) — cấu trúc lưu trữ ghi dữ liệu mới nối vào cuối rồi gộp dần thành các tệp lớn đã sắp xếp; "LSM-tree" là cây theo cách này.
- **WTF** (Who To Follow) — tên hệ thống gợi ý "người nên theo dõi" của Twitter, cũng là tên bài báo.

## Đọc hình

Danh sách hai mươi lăm bài giữ theo bài nguồn; cách xếp nhóm và lời mô tả là của người biên soạn, dựa trên tên bài và kiến thức chung. Năm xuất bản chỉ nêu khi có thể đọc được từ tên tệp trong địa chỉ của bài nguồn.

**Lưu trữ và cơ sở dữ liệu (9 bài).** *Dynamo* (kho khóa-giá trị sẵn sàng cao của Amazon, 2007), *GFS* (2003), *BigTable* (2006), *Cassandra* (2009), *Spanner* (cơ sở dữ liệu phân tán toàn cầu của Google, 2012), *Amazon Aurora*, *FoundationDB*, *MyRocks* (động cơ lưu trữ kiểu LSM, 2020) và bài khảo sát các cơ sở dữ liệu vector (2023). Câu hỏi chung: dữ liệu nằm ở đâu, nhân bản thế nào, đánh đổi gì giữa nhất quán và sẵn sàng.

**Xử lý và điều phối (5 bài).** *MapReduce* (xử lý song song khối lượng dữ liệu lớn), *Flink* (xử lý luồng và lô trong một động cơ), *Borg* (quản lý cụm máy quy mô lớn ở Google), *Shard Manager* (khung quản lý các mảnh dữ liệu) và *Kafka* (nền tảng thông điệp phân tán). Câu hỏi chung: việc chạy ở đâu và thông điệp đi đâu.

**Bộ nhớ đệm, quan sát và phân quyền (4 bài).** *Scaling Memcached at Facebook* (độ phức tạp của bộ nhớ đệm), *Dapper* (hạ tầng truy vết cho hệ thống phân tán của Google, 2010), *Monarch* (cơ sở dữ liệu chuỗi thời gian trong bộ nhớ của Google) và *Zanzibar* (hệ thống quản lý danh sách quyền truy cập toàn cầu). Câu hỏi chung: đệm, nhìn thấy và kiểm soát ai được làm gì.

**Nền tảng lý thuyết và công cụ (5 bài).** *Time, Clocks and the Ordering of Events* (cách nói về thời gian và thứ tự sự kiện giữa nhiều máy), *Raft* (thuật toán đồng thuận dễ hiểu hơn), *Go To Statement Considered Harmful* (1968, bàn về cấu trúc chương trình), *Thrift* (công cụ sinh mã của Facebook, 2007) và *Bitcoin* (đồng tiền điện tử ngang hàng). Câu hỏi chung: các ý tưởng gốc để hiểu mọi thứ còn lại.

**Ứng dụng cụ thể (2 bài).** *Attention Is All You Need* (kiến trúc transformer của học sâu, 2017) và *WTF, Who to Follow* (hệ thống gợi ý người theo dõi của Twitter, nay là X). Hai bài này là ví dụ hệ thống thật hơn là nền tảng chung.

**Cách đọc.** Với một bài báo, trả lời bốn câu: nó giải bài toán gì, ràng buộc nào khiến cách cũ không đủ, đánh đổi nào nó chấp nhận, và phần nào còn đúng khi bạn không có quy mô của tác giả.

## Giới hạn cần nhớ

Xếp nhóm là cách nhìn của người biên soạn; nhiều bài thuộc nhiều nhóm (Kafka vừa là thông điệp vừa là nhật ký lưu trữ). Mô tả mỗi bài chỉ một dòng, dựa trên tên bài và hiểu biết chung, bài biên soạn không đọc lại từng bài báo trong phiên này. Năm xuất bản nêu ra chỉ ở những bài đọc được từ địa chỉ; các bài còn lại không ghi năm để khỏi nêu sai. Không có bài báo nào ở đây là lời khuyên "nên dùng công nghệ này": mỗi bài mô tả một hệ thống trong hoàn cảnh riêng.

## Nhìn hình trả lời

Bạn đang cân nhắc cách một dịch vụ nhỏ cho nhiều bản sao thống nhất ai là bản chính sau khi nút chính hỏng. Hai bài nào trong danh sách liên quan nhất, và bài nào giúp bạn hiểu vì sao đồng hồ các máy không đủ để quyết định?

<details>
<summary>Xem đáp án</summary>

Bài về thuật toán đồng thuận Raft liên quan trực tiếp tới việc chọn bản chính; bài về thời gian, đồng hồ và thứ tự sự kiện giải thích vì sao không thể chỉ nhìn đồng hồ từng máy để thống nhất thứ tự. Đây là suy luận của người biên soạn từ tên và mô tả bài.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một danh sách hai mươi lăm bài, mỗi bài kèm địa chỉ và đôi khi một dòng mô tả. Bài này giữ đủ hai mươi lăm tên, xếp lại thành năm nhóm theo vấn đề (9, 5, 4, 5 và 2 bài, tổng 25) và thêm cách đọc một bài báo.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/25-papers-that-completely-transformed-the-computer-world.md): danh sách hai mươi lăm bài. Cách xếp nhóm và lời mô tả là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức, và chưa đọc lại nội dung các bài báo.

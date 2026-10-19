# Tám vấn đề thường gặp khi hệ thống lớn lên, và cái giá của từng cách giải

**Bài nguồn ghép tám vấn đề của hệ thống lớn với mỗi vấn đề một cách giải, mỗi cách một dòng. Bài này giữ đủ tám cặp, đối chiếu những cặp có tài liệu độc lập, rồi đo thử trên một máy năm cặp (bộ đệm, ghi nhiều, chỉ mục và phân mảnh, cân tải, dự phòng) để thấy mỗi cách giải lấy đi thứ gì. Ba cặp còn lại chỉ đối chiếu tài liệu, không đo.**

![Ba khung. Khung một, tám vấn đề và cách giải của nguồn: đọc nhiều dùng bộ đệm; ghi nhiều dùng hàng đợi ghi và cây LSM; một điểm hỏng dùng dự phòng; sẵn sàng cao dùng cân tải và nhân bản; trễ cao dùng CDN; tệp lớn dùng lưu trữ khối và đối tượng; giám sát dùng nhật ký tập trung; truy vấn chậm dùng chỉ mục và phân mảnh. Khung hai, năm cái giá đo trên một máy: bộ đệm 1% dữ liệu trúng 66% nhưng có thể trả giá cũ; ghi bền từng bản ghi chỉ 5.000 đến 7.500 lần mỗi giây dù cấu trúc nào; chỉ mục làm nạp dữ liệu chậm hơn 24 đến 142%; phân mảnh làm truy vấn theo cột khác chậm gấp khoảng 2; cân tải không kiểm tra làm lọt 33,3% yêu cầu. Khung ba, CDN, tệp lớn và nhật ký tập trung chưa đo.](../../diagrams/sd-08-016-main.svg)

## Từ viết tắt

- **LSM** (Log-Structured Merge) — gộp có cấu trúc nhật ký: cách lưu dữ liệu ghi mới vào bộ nhớ và nhật ký trước, rồi gộp dần thành các dãy đã sắp xếp; ở bài này là cách mà nguồn gọi là cây LSM.
- **CDN** (Content Delivery Network) — mạng phân phối nội dung: các máy đặt gần người dùng, giữ bản sao nội dung tĩnh để người dùng khỏi tải từ xa.
- **ELK** (Elasticsearch, Logstash, Kibana) — bộ ba công cụ gom, lưu và tìm nhật ký mà nguồn nêu tên; ở bài này chỉ nhắc, không đo.
- **LRU** (Least Recently Used) — dùng gần đây ít nhất: luật bỏ khỏi bộ đệm mục lâu nhất chưa ai đọc, dùng trong phép đo bộ đệm ở dưới.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách một chương trình gọi một dịch vụ qua mạng; ở bài này dùng trên máy để đo cân tải.

## Đọc hình

| Vấn đề của nguồn | Cách giải của nguồn | Điều phải trả | Đã làm gì trong bài |
|---|---|---|---|
| Đọc nhiều | Bộ nhớ đệm | Có thể đọc ra dữ liệu cũ; phải bỏ mục khi ghi | đo |
| Ghi nhiều | Công nhân bất đồng bộ; cơ sở dữ liệu dùng cây LSM | Đọc phải tìm qua nhiều dãy cho đến khi gộp; ghi bền vẫn tốn một lần ghi xuống đĩa | đo |
| Một điểm hỏng | Dự phòng và chuyển dự phòng cho thành phần quan trọng | Thêm máy; phải phát hiện hỏng và chuyển đúng lúc | tính và mô phỏng |
| Sẵn sàng cao | Cân tải tới máy khoẻ; nhân bản cơ sở dữ liệu | Cân tải cần biết máy nào khoẻ; nhân bản thêm độ trễ đồng bộ | đo cân tải |
| Trễ cao | CDN | Thêm một chỗ có thể hỏng; nội dung có thể cũ | chỉ đối chiếu tài liệu |
| Tệp lớn | Lưu trữ khối và lưu trữ đối tượng | Chưa đối chiếu tài liệu độc lập | không |
| Giám sát | Nhật ký tập trung kiểu ELK | Chưa đối chiếu, chưa đo | không |
| Truy vấn chậm | Chỉ mục; phân mảnh ngang | Chỉ mục làm ghi chậm đi; phân mảnh làm truy vấn khác khoá phải hỏi mọi mảnh | đo |

## Thử: năm cái giá trên một máy

Ngày 2026-10-19, Python 3.13.16 trên máy 4 lõi ảo, ba hoặc bốn lần chạy mỗi phép đo. Mọi cơ sở dữ liệu ở đây là `sqlite3` chạy ngay trong chương trình, nên giá của một lần gọi qua mạng không có trong con số nào.

**Bộ đệm.** Một bảng 100.000 khoá trong tệp `sqlite3`; 200.000 lần đọc với độ phổ biến kiểu Zipf (số mũ 1,1, hạt giống cố định). Bộ đệm theo luật LRU, đọc theo kiểu cache-aside: thiếu thì đọc cơ sở dữ liệu rồi nhét vào bộ đệm.

| Bộ đệm giữ | Tỷ lệ trúng | Mỗi lần đọc |
|---|---|---|
| không có | 0 | 4,9 đến 5,8 µs |
| 0,1% dữ liệu | 45% | 3,5 đến 4,6 µs |
| 1% dữ liệu | 66,4% | 2,0 đến 3,3 µs |
| 10% dữ liệu | 83% | 1,2 đến 1,9 µs |

Cái giá nằm ở dòng cuối của phép thử: sau khi ghi giá trị mới vào cơ sở dữ liệu mà không bỏ mục trong bộ đệm, đọc qua bộ đệm vẫn ra giá trị cũ. Trang Microsoft về cache-aside nói đúng điều này: bộ đệm kiểu đó không bảo đảm nhất quán, và khi ghi nên ghi vào kho rồi bỏ mục tương ứng.

**Ghi nhiều.** 100.000 khoá ngẫu nhiên, mỗi bản ghi một dòng ngắn.

| Cách ghi | Số bản ghi mỗi giây |
|---|---|
| `sqlite3` (cây B), mỗi bản ghi một lần ghi bền (`synchronous=FULL`), 10.000 bản ghi | 6.100 đến 7.500 |
| nhật ký nối thêm cộng bảng trong bộ nhớ, `fsync` sau mỗi bản ghi, 10.000 bản ghi | 5.200 đến 6.300 |
| nhật ký nối thêm cộng bảng trong bộ nhớ, `fsync` sau mỗi 1.000 bản ghi | 480.000 đến 790.000 |
| `sqlite3` tắt đồng bộ, ghi lô 1.000 bản ghi | 370.000 đến 490.000 |
| nhật ký nối thêm cộng bảng trong bộ nhớ, không `fsync` | 750.000 đến 1.200.000 |

Hai điều đọc được. Một, khi bản ghi nào cũng phải xuống đĩa thật mới được báo xong, cây B và nhật ký nối thêm cùng nằm ở cỡ 5.000 đến 7.500 mỗi giây: cấu trúc LSM không xoá được giá của một lần `fsync`. Tài liệu của thư viện `leveldb` (một kho LSM thật) nói cùng ý: ghi không đồng bộ thường nhanh hơn ghi đồng bộ hơn một nghìn lần, và gom nhiều bản ghi vào một lần ghi đồng bộ chia đều cái giá đó. Hai, khi bỏ đồng bộ, nhật ký nối thêm nhanh hơn cây B 2,0 đến 2,7 lần theo từng lần chạy, vì nó chỉ nối thêm vào cuối. Cái giá của phía LSM là đọc: với 9 dãy đã sắp xếp, một lần đọc theo khoá mất 5,6 µs, sau khi gộp thành một dãy còn 1,4 µs (một lần chạy). Tài liệu `leveldb` mô tả việc gộp theo tầng (compaction) chính là để kéo số dãy phải tìm xuống.

**Chỉ mục và phân mảnh.** Bảng 400.000 dòng (mã, người dùng, số tiền) trong `sqlite3` ở bộ nhớ.

| Phép đo | Kết quả |
|---|---|
| Đếm theo người dùng, không chỉ mục | 13 đến 15 ms mỗi truy vấn |
| Đếm theo người dùng, có chỉ mục | 6,6 đến 8,1 µs mỗi truy vấn |
| Nạp 400.000 dòng, có chỉ mục so với không | chậm hơn 24, 51, 99 và 142% trong bốn lần chạy |
| 8 mảnh chia theo người dùng: truy vấn theo người dùng | 7 đến 11 µs |
| 8 mảnh: truy vấn khoảng số tiền, phải hỏi cả 8 mảnh | 25 đến 42 µs |
| Một cơ sở dữ liệu: cùng truy vấn khoảng số tiền | 13 đến 22 µs |

Chỉ mục đổi ghi chậm lấy đọc nhanh hàng nghìn lần. Phân mảnh nhanh khi truy vấn dùng đúng khoá chia mảnh; khi truy vấn dùng cột khác, mọi mảnh đều phải trả lời và việc cộng lại gấp khoảng hai lần cùng việc trên một cơ sở dữ liệu duy nhất. Trang Microsoft về sharding nói khoá chia mảnh là quyết định quan trọng nhất và đổi sau này rất tốn, và khuyên dùng bảng chỉ mục phụ cho truy vấn theo thuộc tính khác.

**Cân tải.** Ba máy chủ HTTP nhỏ trên máy, một máy tắt hẳn; 300 yêu cầu theo vòng tròn. Không kiểm tra sức khoẻ: 200 yêu cầu thành công (66,7%) trong cả ba lần chạy. Có kiểm tra thụ động, bỏ máy ra sau 3 lần lỗi liên tiếp: 297 thành công (99,0%), ba yêu cầu đầu tiên là cái giá của việc phát hiện.

**Dự phòng.** Nếu mỗi bản chạy được với xác suất a và việc chuyển sang bản khác là tức thì, k bản chạy được với xác suất 1 trừ (1 trừ a) mũ k: hai bản 99% cho 99,99%, ba bản cho 99,9999%. Phép mô phỏng 500.000 lần khớp công thức đến chữ số thứ năm sau dấu phẩy. Điều công thức giấu đi là chữ "tức thì": phát hiện hỏng và chuyển bản mất thời gian thật, và cân tải ở trên là một lần đo cái giá đó.

## Giới hạn cần nhớ

Mọi cơ sở dữ liệu ở đây chạy trong cùng tiến trình hoặc cùng máy, nên cái lợi của bộ đệm so với một cơ sở dữ liệu ở xa bị đánh giá thấp; con số tuyệt đối không nói gì về hệ thống thật. Cây LSM của phép thử là đồ chơi: bảng trong bộ nhớ, một dãy mỗi lần đầy, không xoá, không phục hồi sau lỗi, không bộ lọc; nó chỉ cho thấy hướng của chi phí, không phải tốc độ của một kho LSM thật. Phép đo ghi bền chạy 10.000 bản ghi vì mỗi lần `fsync` chậm, và tốc độ phụ thuộc đĩa của máy. Phân mảnh chạy trong một tiến trình nên không có song song; hệ thống thật có thể hỏi các mảnh cùng lúc, nhưng tổng việc vẫn nhiều hơn. Ba cặp CDN, tệp lớn và nhật ký tập trung không được đo, và lưu trữ khối với lưu trữ đối tượng chưa được đối chiếu với tài liệu độc lập.

## Nhìn hình trả lời

Cửa hàng trực tuyến của bạn đọc nhiều, nên bạn thêm bộ đệm và trang chạy nhanh hơn rõ rệt. Vài ngày sau khách phàn nàn giá hiển thị vẫn là giá cũ sau khi bạn đã đổi giá. Điều gì đã xảy ra, và nên sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Bộ đệm kiểu cache-aside không tự biết dữ liệu đã đổi: nó giữ giá cũ cho đến khi mục bị bỏ hoặc hết hạn, đúng như trường hợp "ghi mà không bỏ mục" ở phép thử. Sửa bằng cách khi đổi giá thì ghi vào kho rồi bỏ mục tương ứng trong bộ đệm, và đặt thời hạn sống cho mục để lỗi hiếm cũng tự hết. Cái phải chấp nhận: giữa lúc ghi và lúc đọc kế tiếp, một người đọc vẫn có thể thấy dữ liệu cũ hoặc phải đợi một lần thiếu.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và tám đoạn, mỗi đoạn một vấn đề và một cách giải. Bài này giữ tám cặp theo đúng thứ tự, thêm cột điều phải trả, và biến năm cặp thành phép đo trên máy; ba cặp còn lại ghi rõ là chỉ đối chiếu tài liệu hoặc chưa đối chiếu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/8-common-system-design-problems-and-solutions.md): tám cặp vấn đề và cách giải.
- [Microsoft — Cache-Aside pattern](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/cache-aside-content.md): nạp theo yêu cầu, bỏ mục khi ghi, không bảo đảm nhất quán. Đọc từ bản sao cục bộ.
- [Microsoft — Sharding pattern](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/sharding.md): khoá chia mảnh, truy vấn theo thuộc tính khác, bảng chỉ mục phụ. Đọc từ bản sao cục bộ.
- [Microsoft — Content Delivery Network guidance](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/best-practices/cdn-content.md): CDN giảm trễ cho nội dung tĩnh; nêu CDN là một điểm hỏng tiềm tàng. Đọc từ bản sao cục bộ.
- [leveldb — implementation notes](https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/doc/impl.md): nhật ký, bảng trong bộ nhớ, dãy đã sắp xếp theo tầng, gộp. Đọc từ bản sao cục bộ.
- [leveldb — usage guide, synchronous writes](https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/doc/index.md): ghi không đồng bộ thường nhanh hơn hơn một nghìn lần; gom bản ghi để chia đều giá của một lần ghi đồng bộ. Đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

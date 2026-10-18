# Bộ lọc Bloom: tránh cào trùng địa chỉ trang ở quy mô lớn

**Bộ lọc Bloom trả lời "chắc chắn chưa có" hoặc "có thể đã có"; bộ cào web dùng nó để bỏ qua những địa chỉ đã gặp mà không phải giữ cả danh sách.**
Bài nguồn so ba cách kiểm tra một địa chỉ trang (URL) đã được cào chưa, rồi giải thích cách thứ ba: bộ lọc Bloom.

![Bốn nhóm xếp dọc. Ba cách kiểm tra một địa chỉ trang đã cào chưa: tập hợp nhanh nhưng không tiết kiệm bộ nhớ, cơ sở dữ liệu chạy được nhưng tải rất cao, bộ lọc Bloom là cách được ưu tiên. Thêm một địa chỉ, ba bước: đưa qua ba hàm băm A, B, C; đặt bit 1 tại ba vị trí kết quả; hai địa chỉ khác nhau có thể dùng chung một bit. Kiểm tra một địa chỉ, ba bước: áp lại ba hàm băm; cả ba bit là 1 thì có thể đã có; có một bit là 0 thì chắc chắn chưa có. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-012-main.svg)

## Từ viết tắt

- **URL** (Uniform Resource Locator) — định vị tài nguyên thống nhất: địa chỉ của một trang trên web; bộ cào web cần biết địa chỉ nào nó đã cào rồi.
- **DB** (DataBase) — cơ sở dữ liệu: nơi lưu dữ liệu lâu dài; chỉ xuất hiện trong tên InfluxDB, một cơ sở dữ liệu mà nguồn nêu để làm ví dụ về hàm băm.

## Đọc hình

**Ba cách.** Cách 1 là bỏ các địa chỉ vào một tập hợp (Set) rồi hỏi địa chỉ mới đã có trong đó chưa: nhanh, nhưng không tiết kiệm bộ nhớ. Cách 2 là lưu địa chỉ trong cơ sở dữ liệu và tra mỗi lần: chạy được, nhưng tải lên cơ sở dữ liệu sẽ rất cao. Cách 3, được nguồn ưu tiên, là bộ lọc Bloom.

**Bộ lọc Bloom là gì.** Burton Howard Bloom đề xuất nó năm 1970. Đây là cấu trúc dữ liệu xác suất, dùng để kiểm tra một phần tử có thuộc một tập hợp hay không. Câu trả lời có hai dạng: "false" nghĩa là phần tử chắc chắn không có trong tập; "true" nghĩa là phần tử có thể có trong tập. Báo nhầm là có (dương tính giả, false positive) thì xảy ra được; báo nhầm là không có (âm tính giả) thì không.

**Thêm một địa chỉ.** Nền của bộ lọc là một dãy bit (bit vector). Để thêm địa chỉ, đưa nó qua ba hàm băm khác nhau A, B, C rồi đặt bit 1 tại ba vị trí kết quả. Trong ví dụ của nguồn, hai địa chỉ khác nhau cùng đặt bit ở chỉ số 5. Vì thế một bit có thể do địa chỉ khác đặt, và đó là lý do dương tính giả xảy ra.

**Kiểm tra một địa chỉ.** Áp lại đúng ba hàm băm lên địa chỉ cần hỏi. Nếu cả ba bit đều là 1 thì địa chỉ có thể đã có; nếu có bất kỳ bit nào là 0 thì địa chỉ chắc chắn chưa có.

**Chọn hàm băm.** Hàm băm phải phân bố đều và nhanh. Nguồn nêu ví dụ: RedisBloom và Apache Spark dùng murmur, InfluxDB dùng xxhash.

**Gặp lại trong mã Apache Spark.** Tài liệu trong mã nguồn Spark mô tả bộ lọc Bloom là cấu trúc dữ liệu xác suất tiết kiệm bộ nhớ, sai theo một phía: nếu nó nói phần tử có thể có thì có thể sai, còn nếu nó nói phần tử không có thì chắc chắn đúng. Hàm hỏi tên là `mightContain`. Mã của nó đặt hoặc đọc từng bit trong số vị trí cần thiết, và bảo cả các bit đó phải là 1 mới trả lời "có thể có". Khác với hình, mã Spark không dùng ba hàm băm riêng: nó lấy hai giá trị băm h1, h2 rồi tính vị trí thứ i từ h1 + i × h2.

## Giới hạn cần nhớ

Nguồn không cho số: không nói tốn bao nhiêu bit, dùng bao nhiêu hàm băm hay tỉ lệ dương tính giả là bao nhiêu. Ba hàm băm trong hình chỉ là ví dụ.
Theo tài liệu của Spark, nếu nhét nhiều phần tử hơn số đã dự kiến, bộ lọc sẽ đầy và xác suất dương tính giả tăng vọt; nguồn không nói tới chuyện này. Với bộ cào web, dương tính giả nghĩa là một vài địa chỉ chưa cào bị bỏ qua nhầm là đã cào, đó là cái giá của việc tiết kiệm bộ nhớ. Bộ lọc cũng không cho biết địa chỉ nào đã được thêm.

## Nhìn hình trả lời

Bộ lọc có ba hàm băm. Một địa chỉ mới được hỏi: hàm A và B cho bit đang là 1, hàm C cho bit đang là 0. Câu trả lời là gì? Nếu cả ba bit đều là 1 thì có thể kết luận địa chỉ này chắc chắn đã được cào chưa?

<details>
<summary>Xem đáp án</summary>

Có một bit là 0 nên địa chỉ chắc chắn chưa có trong bộ lọc, bộ cào có thể cào nó.
Cả ba bit là 1 thì chỉ có thể nói địa chỉ có thể đã có: các bit đó có thể do những địa chỉ khác đặt, nên đó là dương tính giả khả dĩ chứ chưa phải bằng chứng.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh minh họa và đi từ ba cách, tới bộ lọc Bloom, hai bước thêm và kiểm tra, rồi chuyện chọn hàm băm. Hình ở đây vẽ lại thành ba cách, hai chuỗi ba bước và một khung ghi nhớ; bài không dùng ảnh nguồn.
Đoạn "Gặp lại trong mã Apache Spark" và phần giới hạn về độ đầy của bộ lọc lấy từ mã nguồn Spark tại commit cố định ở mục nguồn, không phải từ bài nguồn. Việc RedisBloom dùng murmur và InfluxDB dùng xxhash là lời của nguồn, bài chưa đối chiếu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-avoid-crawling-duplicate-urls-at-google-scale.md): ba cách, bộ lọc Bloom, thêm và kiểm tra, hàm băm.
- [Apache Spark — BloomFilter](https://github.com/apache/spark/blob/fc6371de008490d22ad635ab7b388eb48b9107db/common/sketch/src/main/java/org/apache/spark/util/sketch/BloomFilter.java) và [BloomFilterImpl](https://github.com/apache/spark/blob/fc6371de008490d22ad635ab7b388eb48b9107db/common/sketch/src/main/java/org/apache/spark/util/sketch/BloomFilterImpl.java): sai một phía, `mightContain`, đặt và đọc bit, bộ lọc đầy. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa URL và DB trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

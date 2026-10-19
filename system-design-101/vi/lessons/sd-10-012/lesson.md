# Bộ lọc Bloom: tránh cào trùng địa chỉ trang ở quy mô lớn

**Bộ lọc Bloom trả lời "chắc chắn chưa có" hoặc "có thể đã có"; bộ cào web dùng nó để bỏ qua những địa chỉ đã gặp mà không phải giữ cả danh sách.**
Bài giữ câu hỏi của bài nguồn, làm sao biết một địa chỉ trang (URL) đã cào chưa, và giải thích bộ lọc Bloom bằng chính mã nguồn của Apache Spark.

![Bốn nhóm xếp dọc. Ba cách kiểm tra một địa chỉ trang đã cào chưa: tập hợp giữ nguyên mọi địa chỉ nên tốn bộ nhớ, cơ sở dữ liệu mỗi lần hỏi là một truy vấn ra ngoài, bộ lọc Bloom là dãy bit nhỏ trả lời có thể có hoặc chắc chắn chưa. Thêm một địa chỉ, ba bước: băm để tính vài vị trí trong dãy bit; đặt 1 tại mỗi vị trí đó; địa chỉ khác nhau có thể trùng một vị trí. Kiểm tra một địa chỉ, ba bước: băm lại để tính đúng các vị trí đó; mọi bit là 1 thì có thể đã có; có bit là 0 thì chắc chắn chưa có. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-012-main.svg)

## Từ viết tắt

- **URL** (Uniform Resource Locator) — định vị tài nguyên thống nhất: địa chỉ của một trang trên web; bộ cào web cần biết địa chỉ nào nó đã cào rồi.

## Đọc hình

**Ba cách hỏi "đã cào chưa".** Bài nguồn so ba cách: bỏ địa chỉ vào một tập hợp, lưu địa chỉ trong cơ sở dữ liệu, hoặc dùng bộ lọc Bloom. Hai cách đầu dễ hiểu: tập hợp phải giữ nguyên từng địa chỉ nên bộ nhớ lớn dần theo số địa chỉ đã cào; cơ sở dữ liệu thì mỗi lần hỏi là một lượt truy vấn, và bộ cào hỏi liên tục. Cách thứ ba là chủ đề của bài. Hai nhận xét về tập hợp và cơ sở dữ liệu là cách nhìn chung của người biên soạn, bài không đo.

**Bộ lọc Bloom là gì.** Tài liệu trong mã nguồn Spark mô tả nó là cấu trúc dữ liệu xác suất tiết kiệm bộ nhớ, cho một phép kiểm tra "có chứa không" gần đúng và sai một phía: nếu nó nói một phần tử có thể có, câu trả lời có thể sai; nếu nó nói phần tử không có, thì chắc chắn đúng. Hàm hỏi tên là `mightContain`, "có thể chứa". Xác suất nó trả lời nhầm "có" cho một phần tử chưa từng thêm gọi là xác suất dương tính giả. Burton Howard Bloom đề xuất cấu trúc này năm 1970 (lời của bài nguồn, bài chưa đối chiếu).

**Thêm một địa chỉ.** Nền của bộ lọc là một dãy bit. Mã Spark tính từ phần tử hai giá trị băm h1 và h2, rồi với i chạy từ 1 tới số hàm băm cần dùng, lấy h1 + i × h2, đổi thành số không âm, chia lấy dư cho độ dài dãy bit và đặt bit tại vị trí đó. Vậy mỗi phần tử đặt vài bit; hai phần tử khác nhau có thể đặt trùng một bit, và đó là lý do dương tính giả xảy ra.

**Kiểm tra một địa chỉ.** Tính lại đúng các vị trí đó. Mã Spark đọc từng bit và dừng ngay khi gặp một bit là 0, trả lời "không"; chỉ khi mọi bit đều là 1 nó mới trả lời "có thể có". Cho nên một bit 0 là bằng chứng chắc chắn, còn toàn bit 1 mới chỉ là dấu hiệu.

**Chọn hàm băm.** Hàm băm phải phân bố đều và nhanh, nếu không các bit sẽ dồn vào một vùng. Spark dùng bộ băm Murmur3 32 bit cho việc này, theo mã nguồn của chính nó. Hình vẽ ba vị trí cho mỗi địa chỉ chỉ để minh họa; số vị trí thật do cách khởi tạo bộ lọc quyết định.

**Khi bộ lọc đầy.** Tài liệu Spark cảnh báo: nhét nhiều phần tử hơn số đã dự kiến sẽ làm bộ lọc bão hòa và xác suất dương tính giả tăng vọt, nên phải chọn kích thước bộ lọc cho hợp lý.

## Giới hạn cần nhớ

Bài không đưa số: không nói tốn bao nhiêu bit, dùng bao nhiêu hàm băm hay xác suất dương tính giả là bao nhiêu. Với bộ cào web, dương tính giả nghĩa là một vài địa chỉ chưa cào bị bỏ qua nhầm là đã cào, đó là cái giá của việc tiết kiệm bộ nhớ. Bộ lọc cũng không cho biết địa chỉ nào đã được thêm, và bài không đối chiếu bản gốc của Bloom.
Bài chỉ đối chiếu với Spark; các thư viện khác dùng hàm băm khác (bài nguồn nêu hai ví dụ khác, bài chưa đối chiếu).

## Nhìn hình trả lời

Bộ lọc tính ba vị trí cho mỗi địa chỉ. Một địa chỉ mới được hỏi: hai trong ba bit đang là 1, bit còn lại đang là 0. Câu trả lời là gì? Nếu cả ba bit đều là 1 thì có thể kết luận địa chỉ này chắc chắn đã được cào chưa?

<details>
<summary>Xem đáp án</summary>

Có một bit là 0 nên địa chỉ chắc chắn chưa có trong bộ lọc, bộ cào có thể cào nó.
Cả ba bit là 1 thì chỉ có thể nói địa chỉ có thể đã có: các bit đó có thể do những địa chỉ khác đặt, nên đó là dương tính giả khả dĩ chứ chưa phải bằng chứng.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh minh họa và đi từ ba cách, tới bộ lọc Bloom, hai bước thêm và kiểm tra, rồi chuyện chọn hàm băm. Bài này giữ câu hỏi và ba cách, rồi viết lại phần giải thích bộ lọc từ mã nguồn Apache Spark tại commit cố định ở mục nguồn nên không lặp câu chữ của nguồn. Hình tự vẽ lại thành ba cách, hai chuỗi ba bước và một khung ghi nhớ; bài không dùng ảnh nguồn.
Cách Spark tính vị trí từ hai giá trị băm, bộ băm Murmur3 và cảnh báo về độ đầy của bộ lọc đều lấy từ mã nguồn Spark, không từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-avoid-crawling-duplicate-urls-at-google-scale.md): chỉ lấy câu hỏi, ba cách và năm 1970 của Bloom.
- [Apache Spark — BloomFilter](https://github.com/apache/spark/blob/fc6371de008490d22ad635ab7b388eb48b9107db/common/sketch/src/main/java/org/apache/spark/util/sketch/BloomFilter.java), [BloomFilterImpl](https://github.com/apache/spark/blob/fc6371de008490d22ad635ab7b388eb48b9107db/common/sketch/src/main/java/org/apache/spark/util/sketch/BloomFilterImpl.java) và [Murmur3_x86_32](https://github.com/apache/spark/blob/fc6371de008490d22ad635ab7b388eb48b9107db/common/sketch/src/main/java/org/apache/spark/util/sketch/Murmur3_x86_32.java): sai một phía, `mightContain`, đặt và đọc bit, hàm băm, bộ lọc đầy. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Nhận xét về tập hợp và cơ sở dữ liệu, năm 1970 và câu giải nghĩa URL trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

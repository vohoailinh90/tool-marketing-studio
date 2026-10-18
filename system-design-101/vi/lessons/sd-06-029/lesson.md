# Học bộ đệm qua tám câu hỏi: bản sao có thể cũ, có thể đầy, có thể mất

**Bộ đệm (cache) giữ tạm một bản sao của dữ liệu hay được đọc, ở chỗ gần ứng dụng và nhanh hơn nơi lưu gốc. Tám câu hỏi dưới đây, theo thứ tự của bài nguồn, đều xoay quanh ba điều về bản sao ấy: nó có thể cũ so với gốc, có thể đầy, và có thể mất bất cứ lúc nào.**
Bài này là bản đồ: mỗi câu hỏi được trả lời ngắn và chỉ sang bài đi sâu nếu đã có. Phần thử nghiệm cho một Redis chạy đầy bộ nhớ với ba chính sách loại bỏ khóa, và cho PostgreSQL đọc cùng một bảng hai lần.

![Ba phần. Phần một, hiểu bộ đệm, bốn thẻ: là gì, bản sao tạm của dữ liệu hay đọc, đặt gần hơn nơi gốc; vì sao cần, vì nơi gốc chậm, xa hoặc bị nhiều yêu cầu tranh nhau; đặt ở đâu, ở trình duyệt, CDN, ứng dụng, Redis, cơ sở dữ liệu; riêng hay chung, bộ đệm trong tiến trình thì nhanh, dùng chung thì các máy thấy một bản. Phần hai, giữ bộ đệm đúng, bốn thẻ: đầy thì bỏ gì, chính sách loại bỏ quyết định khóa nào đi; gốc đổi thì sao, hết hạn sau một thời gian hoặc xóa khi ghi; đọc ghi thế nào, ai nạp và ai ghi xuống gốc; hỏng ra sao, bản cũ, mất dữ liệu, dồn tải về nơi gốc. Phần ba, kết quả thử Redis giới hạn 4 MB: 500 khóa nóng được đọc lại liên tục rồi ghi thêm 20 000 khóa; không loại bỏ thì từ chối ghi thêm sau 2908 khóa; bỏ khóa lâu chưa dùng thì giữ đủ 500 trên 500 khóa nóng; bỏ ngẫu nhiên thì còn 2 trên 500 khóa nóng và đọc trúng 28,3%.](../../diagrams/sd-06-029-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt ở nhiều nơi, giữ bản sao nội dung và phát cho người dùng từ máy gần họ.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ cơ sở dữ liệu dùng nó.
- **LRU** (Least Recently Used) — lâu nhất chưa được dùng: cách loại bỏ chọn khóa đã lâu nhất không ai đọc hay ghi.
- **TTL** (Time To Live) — thời gian sống: hết khoảng này thì một mục trong bộ đệm tự hết hạn và bị xóa.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng cỡ một triệu byte; trong cấu hình Redis, `1mb` là 1024 × 1024 byte.

## Đọc hình

### Hiểu bộ đệm

**1 · Là gì.** Một bản sao tạm của dữ liệu, đặt ở nơi ứng dụng lấy được nhanh hơn nơi lưu gốc. Tài liệu kiến trúc của Microsoft khuyên coi nó như ảnh chụp dữ liệu gốc tại một lúc trong quá khứ, và như một kho tạm có thể biến mất bất cứ lúc nào; vì vậy dữ liệu quan trọng phải luôn được ghi vào nơi lưu gốc. Bộ đệm cũng giữ được kết quả của một phép tính tốn kém để khỏi tính lại.

**2 · Vì sao cần.** Bộ đệm có lợi nhất khi cùng một dữ liệu được đọc đi đọc lại, và nơi lưu gốc thì ít thay đổi, chậm hơn bộ đệm, bị nhiều yêu cầu tranh nhau, hoặc ở xa tới mức độ trễ mạng đáng kể. Bài [Những con số độ trễ nào bạn nên biết](../sd-06-025/lesson.md) cho thấy khoảng cách giữa đọc bộ nhớ, đọc đĩa và đi qua mạng. Với dữ liệu đổi liên tục, bản sao cũ đi rất nhanh, hoặc việc giữ nó khớp với gốc tốn tới mức ăn hết phần lợi.

**3 · Đặt ở đâu.** Ở gần như mọi chặng của một yêu cầu. Trình duyệt giữ phản hồi trong bộ đệm riêng của một người dùng; CDN và proxy ngược là bộ đệm dùng chung giữa nhiều người dùng, đặt giữa trình duyệt và máy chủ (bài [CDN là gì](../sd-06-023/lesson.md)); ứng dụng giữ kết quả trong bộ nhớ của chính nó; một máy bộ đệm riêng như Redis phục vụ nhiều máy ứng dụng; và cơ sở dữ liệu cũng giữ các khối dữ liệu vừa đọc trong bộ nhớ, PostgreSQL gọi vùng này là `shared_buffers`.

**4 · Riêng hay chung.** Bộ đệm *riêng* nằm trong bộ nhớ của một tiến trình: lấy rất nhanh, nhưng mỗi máy ứng dụng giữ một bản của mình, chụp ở những lúc khác nhau, nên cùng một câu hỏi có thể nhận hai câu trả lời. Bộ đệm *dùng chung* là một dịch vụ riêng mà mọi máy cùng hỏi: các máy thấy cùng một bản và mở rộng được bằng cách thêm máy cho cụm bộ đệm, đổi lại mỗi lần lấy phải đi qua mạng và hệ thống có thêm một thành phần phải vận hành. Tài liệu Microsoft còn gợi ý dùng cả hai: hỏi bộ đệm riêng trước, rồi bộ đệm chung, rồi mới tới nơi gốc.

### Giữ bộ đệm đúng

**5 · Đầy thì bỏ gì.** Bộ đệm có giới hạn bộ nhớ; khi đầy, *chính sách loại bỏ* quyết định khóa nào phải đi. Redis có `noeviction` (không bỏ gì, báo lỗi với lệnh cần thêm bộ nhớ, lệnh chỉ đọc vẫn chạy), `allkeys-lru` (bỏ khóa lâu nhất chưa dùng), `allkeys-random` (bỏ ngẫu nhiên), các biến thể `volatile-...` chỉ bỏ khóa có hạn dùng, và vài cách khác. Tài liệu Redis khuyên `allkeys-lru` làm lựa chọn mặc định khi một phần nhỏ dữ liệu được dùng nhiều hơn hẳn phần còn lại; cách chọn khóa của Redis là xấp xỉ, không chính xác tuyệt đối. Lưu ý: bản Redis đã thử mặc định không giới hạn bộ nhớ và dùng `noeviction`, nên muốn nó làm bộ đệm thì phải đặt cả `maxmemory` lẫn chính sách.

**6 · Gốc đổi thì sao.** Có hai cách chính. Đặt thời gian hết hạn (TTL) để bản sao cũ chỉ sống tới một lúc nào đó: quá ngắn thì bộ đệm ít tác dụng, quá dài thì dữ liệu cũ lâu. Hoặc xóa mục trong bộ đệm ngay khi ghi vào nơi gốc, để lần đọc sau nạp lại. Bộ đệm ở trình duyệt thì máy chủ không trực tiếp buộc trình duyệt xóa được; cách quen dùng là đổi địa chỉ của tệp mỗi khi nội dung đổi (ví dụ thêm số phiên bản vào tên tệp), vì trình duyệt dùng địa chỉ làm khóa.

**7 · Đọc ghi thế nào.** Ai nạp bộ đệm khi thiếu, và khi ghi thì dữ liệu đi vào bộ đệm, nơi gốc hay cả hai, theo thứ tự nào: đó là các chiến lược cache-aside, read-through, write-through, write-behind, write-around, so sánh và đo trong bài [Các chiến lược bộ đệm hàng đầu](../sd-06-026/lesson.md).

**8 · Hỏng ra sao.** Các kiểu hỏng hay gặp đều đến từ ba điều ở đầu bài. Bản sao *cũ*: người đọc thấy dữ liệu đã đổi ở gốc. Bản sao *mất*: bộ đệm sập hay khởi động lại thì trống, và mọi yêu cầu dồn về nơi gốc; tài liệu Microsoft nhắc rằng lúc bộ đệm đang hồi phục, nơi gốc có thể bị dồn quá tải. Bộ đệm *đầy*: chính sách loại bỏ chọn sai thì khóa đang dùng bị bỏ, tỉ lệ đọc trúng tụt xuống. Thêm một rủi ro riêng của bộ đệm dùng chung: phản hồi dành cho riêng một người dùng mà lọt vào đó thì người khác có thể nhận được.

### Thử nghiệm

**Redis 7.0.15, giới hạn `maxmemory 4mb`.** Ghi 500 khóa "nóng" (mỗi giá trị 1000 byte), rồi ghi thêm 20 000 khóa khác cùng cỡ; cứ sau 50 lần ghi thì đọc lại cả 500 khóa nóng, như một trang có vài sản phẩm được xem liên tục.

| Chính sách | Lần ghi được nhận | Khóa nóng còn lại | Đọc khóa nóng trúng |
| --- | --- | --- | --- |
| `noeviction` | 2908, rồi lỗi `command not allowed when used memory > 'maxmemory'` | 500/500 | 100% |
| `allkeys-lru` | 20 500 (17 592 khóa bị loại bỏ) | 500/500 | 100% |
| `allkeys-random` | 20 500 (17 593 khóa bị loại bỏ) | 2/500 | 28,3% |

Với `noeviction`, khóa nóng vẫn còn nhưng ứng dụng không ghi thêm được gì: bộ đệm đầy biến thành lỗi ở phía ứng dụng. Với `allkeys-lru`, khóa vừa được đọc hầu như không bị chọn (Redis chọn theo cách xấp xỉ), và trong lần thử cả 500 khóa nóng sống sót. Với `allkeys-random`, khóa nóng bị bỏ ngẫu nhiên như mọi khóa khác.

**PostgreSQL 16, `shared_buffers` mặc định 128 MB.** Tạo bảng 200 000 dòng, khởi động lại PostgreSQL để vùng đệm trống, rồi chạy cùng một truy vấn hai lần với `EXPLAIN (ANALYZE, BUFFERS)`: lần đầu `shared read=1870`, lần sau `shared hit=1870`. Cả 1870 khối được tìm thấy trong bộ đệm ở lần thứ hai; "read" ở lần đầu là PostgreSQL phải xin khối từ hệ điều hành, chưa chắc là đọc đĩa thật.

## Giới hạn cần nhớ

Bộ đệm không phải nơi lưu chính. Microsoft khuyên ứng dụng phải chạy tiếp được khi bộ đệm dùng chung không trả lời, bằng cách quay về nơi gốc, và đừng ghi dữ liệu quan trọng chỉ vào bộ đệm. Mọi con số ở trên là của một lần thử trên một máy, với dữ liệu giả và một kiểu truy cập đặt sẵn: chúng cho thấy hướng, không phải tỉ lệ trúng bạn sẽ có. Tài liệu Redis khuyên đo tỉ lệ trúng của chính hệ thống bằng `keyspace_hits` và `keyspace_misses` trong lệnh `INFO`.

## Nhìn hình trả lời

Một trang tin chạy bốn máy ứng dụng, mỗi máy giữ bộ đệm riêng trong bộ nhớ 10 phút cho bài viết. Biên tập viên sửa một lỗi trong bài, nhưng người đọc tải lại trang thì lúc thấy bản đã sửa, lúc thấy bản cũ. Theo hình, chuyện gì đang xảy ra, và có những cách nào để sửa?

<details>
<summary>Xem đáp án</summary>

Câu 4 và 6: mỗi máy giữ một bản riêng, chụp ở lúc khác nhau, nên tùy yêu cầu rơi vào máy nào mà người đọc thấy bản cũ hay mới, cho tới khi bản cũ hết hạn sau 10 phút.
Cách sửa: chuyển sang một bộ đệm dùng chung để mọi máy thấy cùng một bản, rồi xóa mục của bài khi bài được sửa; hoặc giữ bộ đệm riêng nhưng rút ngắn thời gian hết hạn, chấp nhận nơi gốc bị hỏi nhiều hơn. Nếu bài còn được giữ ở CDN hay trình duyệt thì các tầng đó cũng phải được làm mới.

</details>

<details>
<summary>Xem sâu hơn: chọn chính sách loại bỏ theo kiểu truy cập</summary>

- `allkeys-lru`: một phần nhỏ dữ liệu được dùng nhiều hơn hẳn phần còn lại; tài liệu Redis gọi đây là lựa chọn mặc định tốt.
- `allkeys-random`: mọi khóa được dùng gần như đều nhau, ví dụ ứng dụng đọc dữ liệu theo một vòng lặp lại.
- `volatile-ttl`: mã ứng dụng tự đoán được khóa nào nên đi trước và đặt cho chúng thời gian hết hạn ngắn.
- Các chính sách `volatile-...` chỉ bỏ khóa có thời gian hết hạn; không có khóa nào như vậy thì chúng cư xử như `noeviction`. Tài liệu Redis nói chúng hợp khi một Redis vừa làm bộ đệm vừa giữ dữ liệu cần lưu, nhưng nên tách thành hai Redis nếu được.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/learn-cache.md): danh sách các câu hỏi (là gì, vì sao cần, đặt ở đâu, triển khai, bộ đệm phân tán, loại bỏ và làm mất hiệu lực, chiến lược, thách thức).
- [Microsoft Azure Architecture Center — Caching guidance, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/best-practices/caching.md): định nghĩa, khi nào bộ đệm có lợi, bộ đệm riêng và dùng chung, hết hạn, loại bỏ, đổi địa chỉ để làm mới bộ đệm phía trình duyệt, quay về nơi gốc khi bộ đệm không trả lời.
- [Mozilla — bộ đệm trên web, tại commit cố định](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/caching/index.md): bộ đệm riêng của trình duyệt, bộ đệm dùng chung (proxy, proxy ngược, CDN), nguy cơ lộ phản hồi riêng của một người dùng qua bộ đệm dùng chung.
- [Tài liệu Redis — Key eviction, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/reference/eviction/index.md): `maxmemory`, các chính sách, khi nào dùng chính sách nào, tỉ lệ trúng từ `INFO`; [`redis.conf` ở thẻ 7.0.15](https://github.com/redis/redis/blob/f35f36a265403c07b119830aa4bb3b7d71653ec9/redis.conf): chính sách mặc định `noeviction`, chọn khóa bằng thuật toán xấp xỉ, `1mb` là 1024 × 1024 byte.
- Tài liệu PostgreSQL ở nhánh 16 tại commit cố định: [`shared_buffers`](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/config.sgml) (mặc định thường là 128 MB, PostgreSQL còn dựa vào bộ đệm của hệ điều hành) và [`EXPLAIN`](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/ref/explain.sgml) (một lần "hit" là một lần đọc tránh được vì khối đã có trong bộ đệm).

Thử nghiệm chạy ngày 2026-10-18 trên một máy: Redis 7.0.15 (gói Ubuntu, thư viện redis-py 8.1.0) và PostgreSQL 16 cài trên máy. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

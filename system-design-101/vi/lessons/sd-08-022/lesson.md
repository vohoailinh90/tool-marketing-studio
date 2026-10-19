# Bản đồ kiến thức của kiến trúc sư: tám vùng, năm mươi cái tên, và "biết" một cái tên nghĩa là gì

**Bài nguồn là một bản đồ: tám vùng kiến thức, mỗi vùng vài cái tên. Bài này giữ đủ tám vùng theo thứ tự của nguồn, đếm xem bản đồ gọi bao nhiêu tên, rồi lấy hai cái tên ở hai vùng khác nhau (một nguyên tắc thiết kế, một khái niệm bảo mật) và biến mỗi cái thành một phép thử chạy được, để thấy "biết" một cái tên thì làm được điều gì.**

![Ba khung. Khung một, bản đồ của nguồn có tám vùng và khoảng năm mươi cái tên: ngôn ngữ 4, công cụ 5, nguyên tắc thiết kế 8, kiến trúc 6, nền tảng 8, dữ liệu 5, mạng và bảo mật 8, kỹ năng hỗ trợ 6; bản đồ chỉ gọi tên, không nói học cái nào trước. Khung hai, hai cái tên được thử: chuyển tiền hỏng giữa chừng làm tổng tiền từ 100 thành 250 nếu mỗi lệnh chạy riêng, và vẫn là 100 nếu nằm trong một giao dịch; thẻ JWT đọc được nội dung không cần khóa nhưng sửa nội dung thì chữ ký không còn khớp. Khung ba, mới thử hai trong năm mươi cái tên, số đếm là đếm tay.](../../diagrams/sd-08-022-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình cho chương trình khác gọi nó; "cổng API" trong bản đồ là chỗ nhận các lời gọi đó.
- **CAP** (Consistency Availability Partition) — nhất quán, sẵn sàng, chịu chia cắt mạng (chữ P là khả năng chịu chia cắt, partition tolerance): tên một định lý nói rằng khi mạng bị chia cắt, hệ phân tán phải chọn giữa trả lời mọi yêu cầu và trả lời đúng dữ liệu mới nhất; bài chỉ nhắc tên.
- **DNS** (Domain Name System) — hệ thống tên miền: dịch tên một máy thành địa chỉ số của nó.
- **ELK** (Elasticsearch Logstash Kibana) — ba công cụ đi cùng nhau để thu, tìm và xem nhật ký của hệ thống; bản đồ liệt kê nó ở vùng công cụ.
- **HTTPS** (HyperText Transfer Protocol Secure) — giao thức truyền siêu văn bản an toàn: cách các trang web được gửi qua mạng sau khi đã mã hóa.
- **MVC** (Model View Controller) — mô hình, khung nhìn, bộ điều khiển: một cách chia ứng dụng thành ba vai (chi tiết ở bài riêng của nhóm).
- **NoSQL** (Not Only SQL) — không chỉ SQL: tên chung của các cơ sở dữ liệu không dùng bảng và ngôn ngữ truy vấn cổ điển.
- **OAuth** (Open AUTHorization) — ủy quyền mở: cách cho một ứng dụng được phép truy cập dữ liệu của bạn ở nơi khác mà không đưa mật khẩu.
- **OLAP** (OnLine Analytical Processing) — xử lý phân tích trực tuyến: các truy vấn tổng hợp trên nhiều dữ liệu, khác với xử lý giao dịch từng dòng.
- **RFC** (Request For Comments) — yêu cầu góp ý: loạt tài liệu chuẩn của Internet; bài nhắc tới hai tài liệu về thẻ JWT mà người viết không đọc được.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để hỏi và sửa dữ liệu trong cơ sở dữ liệu quan hệ.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: lớp bảo đảm các byte tới đủ và đúng thứ tự.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa nằm dưới HTTPS.
- **ACID** (Atomicity Consistency Isolation Durability) — tính nguyên tử, nhất quán, cô lập, bền vững: bốn đặc tính người ta mong ở một giao dịch cơ sở dữ liệu; bài này chỉ thử chữ A, nguyên tử: giao dịch làm hết hoặc không làm gì.
- **JWT** (JSON Web Token) — thẻ web dạng JSON: một chuỗi gồm ba đoạn (tiêu đề, nội dung, chữ ký) mà máy chủ phát cho người dùng để họ mang theo khi gọi lại.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: cách viết dữ liệu thành chữ với cặp tên và giá trị; nội dung của thẻ JWT viết theo cách này.

## Đọc hình

| Vùng (theo nguồn) | Nguồn nêu | Số tên (đếm tay) |
|---|---|---|
| Thành thạo một ngôn ngữ | thành thạo 1 đến 2 ngôn ngữ như Java, Python, Golang, JavaScript | 4 |
| Công cụ | GitHub, Jenkins, Jira, ELK, Sonar | 5 |
| Nguyên tắc thiết kế | lập trình hướng đối tượng, mã sạch, thiết kế dẫn bằng kiểm thử, thiết kế hướng miền, định lý CAP, mẫu MVC, ACID, GoF | 8 |
| Nguyên tắc kiến trúc | dịch vụ nhỏ, xuất bản và đăng ký, phân tầng, hướng sự kiện, máy khách và máy chủ, lục giác | 6 |
| Hiểu biết về nền tảng | container, điều phối, đám mây, không máy chủ, mạng phân phối nội dung, cổng API, hệ phân tán, tích hợp và triển khai liên tục | 8 |
| Phân tích dữ liệu | cơ sở dữ liệu SQL và NoSQL, luồng dữ liệu với Kafka, lưu trữ đối tượng, di chuyển dữ liệu, OLAP | 5 |
| Mạng và bảo mật | DNS, TCP, TLS, HTTPS, mã hóa, JWT, OAuth, quản lý thông tin xác thực | 8 |
| Kỹ năng hỗ trợ | ra quyết định, hiểu công nghệ, quản lý các bên liên quan, giao tiếp, ước lượng, lãnh đạo | 6 |

Tổng cộng khoảng 50 cái tên trong 8 vùng (đếm của người biên soạn: một cụm như "cơ sở dữ liệu SQL và NoSQL" tính một, nên ai đếm khác sẽ ra số hơi khác). Bản đồ chỉ gọi tên và nhóm lại; nó không nói cái nào quan trọng hơn, học cái nào trước, hay biết đến mức nào thì đủ. Câu cuối của nguồn mời người đọc tự thêm vào, nghĩa là bản đồ tự coi mình chưa đầy đủ.

Đối chiếu một vùng với tài liệu của Microsoft về kiểu kiến trúc: trong sáu "nguyên tắc kiến trúc" của bản đồ, tài liệu đó có trang riêng cho phân tầng (n-tier), dịch vụ nhỏ và hướng sự kiện, và một trang về mẫu xuất bản và đăng ký; không trang nào nhắc "hexagonal" hay "ports and adapters", và máy khách với máy chủ chỉ xuất hiện trong vài kịch bản ví dụ chứ không có trang riêng. Vậy bốn trong sáu tên có chỗ đối chiếu; hai tên kia (lục giác, máy khách và máy chủ) thì không.

## Thử: biến một cái tên thành một phép thử

Ngày 2026-10-19, Python 3.13.16, SQLite 3.45.1, thư viện PyJWT 2.14.0 (một bản cài đặt độc lập với đoạn mã tự viết của bài).

**Nguyên tắc thiết kế, ACID, chữ A.** Một tài khoản có 100, tài khoản kia 0; chuyển 150 và bước cộng chạy trước, bước trừ vi phạm luật số dư không âm nên bị từ chối.

| Cách làm | Tổng tiền trước | Tổng tiền sau | Số dư sau |
|---|---|---|---|
| Từng lệnh chạy riêng | 100 | 250 | 100 và 150 |
| Trong một giao dịch, bị hủy khi lệnh trừ lỗi | 100 | 100 | 100 và 0 |

Khi các lệnh chạy riêng, bước cộng đã được ghi và không ai gỡ nó ra: 150 đồng tự sinh ra. Trong giao dịch, lệnh lỗi làm cả giao dịch bị hủy, và dữ liệu về đúng trạng thái đầu. Đó là "nguyên tử": hoặc làm hết, hoặc không làm gì. Phép thử chỉ chạm chữ A của ACID.

**Mạng và bảo mật, JWT.** Tự viết thẻ ký bằng thuật toán `HS256` cho nội dung `role: reader`, rồi so với thư viện:

| Phép thử | Kết quả |
|---|---|
| Thẻ tự viết so với thẻ của thư viện, cùng khóa và nội dung | giống nhau từng ký tự |
| Đọc nội dung thẻ mà không có khóa | đọc được ngay: `{"sub":"user-1","role":"reader","exp":4102444800}` |
| Đổi `role` thành `admin`, giữ nguyên chữ ký | bị từ chối: chữ ký không khớp |
| Thẻ ghi thuật toán `none` (không chữ ký), khi bắt buộc `HS256` | bị từ chối: thuật toán không được phép |
| Thẻ đã hết hạn | bị từ chối: hết hạn |

Cái tên "JWT" trong bản đồ gói ba điều khác nhau: nội dung không được giấu (ai cầm thẻ cũng đọc được, vì phần nội dung chỉ được đổi sang dạng chữ (base64url) chứ không bị xáo trộn bằng khóa), chữ ký làm cho việc sửa bị phát hiện, và máy chủ phải tự chọn thuật toán nhận thay vì tin ô thuật toán trong thẻ. Người chỉ "biết tên" dễ nhầm rằng thẻ này giữ bí mật; người đã thử thì không.

## Giới hạn cần nhớ

Số "50 cái tên" là đếm tay trên phần chữ của bài nguồn. Bài chỉ đọc phần chữ, không dùng nội dung ảnh của nguồn. Hai phép thử chỉ chạm hai trong năm mươi cái tên; chúng cho thấy "biết" nghĩa là gì, không chứng minh rằng bản đồ đủ hay đúng. Phép thử giao dịch dùng SQLite trong bộ nhớ và chỉ thử tính nguyên tử, không thử nhất quán, cô lập hay bền vững. Phép thử JWT dùng một khóa thử, một thư viện, và không đọc đặc tả chính thức của thẻ (RFC 7519, RFC 7515) vì không truy cập được lúc viết; hành vi từ chối được lấy từ chính thư viện. Tài liệu Python chỉ được dùng cho cách điều khiển giao dịch của mô-đun `sqlite3`: ở chế độ tự ghi, lệnh `commit` và `rollback` của Python không có tác dụng và giao dịch phải mở bằng lệnh SQL, như phép thử đã làm.

## Nhìn hình trả lời

Bạn nhận một thẻ JWT có nội dung `role: reader` và muốn tự cho mình quyền `admin`. Theo phép thử trên, bạn làm được những gì với nội dung của thẻ, và điều gì chặn bạn?

<details>
<summary>Xem đáp án</summary>

Bạn đọc được toàn bộ nội dung mà không cần khóa, và có thể viết lại nội dung thành `role: admin`. Nhưng chữ ký được tính từ nội dung cũ bằng khóa mà bạn không có, nên máy chủ kiểm tra lại sẽ thấy chữ ký không khớp và từ chối. Bạn cũng không thoát được bằng cách đổi thuật toán thành `none`, vì máy chủ bắt buộc thuật toán nó đã chọn. Nghĩa là: đừng để dữ liệu bí mật trong nội dung thẻ, và luôn kiểm tra chữ ký bằng thuật toán do máy chủ quy định.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình bản đồ kèm danh sách tám vùng và câu hỏi mở đầu. Bài này giữ nguyên tám vùng và thứ tự, thêm một phép đếm, một chỗ đối chiếu với tài liệu Microsoft về kiểu kiến trúc, và hai phép thử cho hai trong năm mươi cái tên.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-ultimate-software-architect-knowledge-map.md): tám vùng và các tên. Chỉ đọc phần chữ.
- [Microsoft — Architecture styles](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/architecture-styles/index.md): các kiểu kiến trúc có trang riêng; cùng với trang mẫu [Publisher-Subscriber](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/publisher-subscriber.md). Đọc từ bản sao cục bộ.
- [Python — mô-đun sqlite3](https://github.com/python/cpython/blob/7dbc797/Doc/library/sqlite3.rst): cách điều khiển giao dịch, chế độ tự ghi. Đọc từ bản sao cục bộ.
- [PyJWT](https://pypi.org/project/PyJWT/): bản cài đặt độc lập dùng để đối chiếu thẻ tự viết (phiên bản 2.14.0).

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

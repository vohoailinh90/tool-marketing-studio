# Tám khái niệm của thiết kế hướng miền: bảy có chỗ đối chiếu, một kiểm bằng mã

**Bài nguồn liệt kê tám khái niệm của thiết kế hướng miền, mỗi khái niệm một hai câu và một hình. Bài này đặt từng khái niệm cạnh trang hướng dẫn của Microsoft về phân tích miền và DDD chiến thuật để xem điều nào được xác nhận, chỉ ra một chỗ hai nguồn dùng chữ "tầng" theo hai nghĩa khác nhau, và viết bộ kiểm tra tầng bằng cây cú pháp để thấy một quy tắc chia tầng có thể kiểm bằng máy thay vì bằng mắt.**

![Ba khung. Khung một, tám khái niệm của nguồn: thiết kế hướng miền, thực thể nghiệp vụ, ranh giới mô hình, khối nhất quán, thực thể và đối tượng giá trị, mô hình thao tác, chia tầng và dựng mô hình miền; tài liệu Microsoft khớp với bảy khái niệm, và nhắc thêm ngôn ngữ chung riêng cho từng ngữ cảnh. Khung hai, một điểm cần phân biệt: nguồn khuyên chia tầng bên trong một khối, còn Microsoft khuyên đừng cắt dịch vụ theo tầng ngang như truy cập dữ liệu hay nhắn tin mà cắt theo năng lực nghiệp vụ. Khung ba, bộ kiểm tra tầng bằng cây cú pháp: dự án thử 12 tệp tìm ra 1 vi phạm trong 0,002 giây, dự án thử 10.000 tệp tìm ra 5 vi phạm trong 0,69 đến 0,78 giây.](../../diagrams/sd-08-015-main.svg)

## Từ viết tắt

- **DDD** (Domain-Driven Design) — thiết kế hướng miền: cách xây phần mềm bằng mô hình của chính lĩnh vực nghiệp vụ, tên gọi lấy từ lĩnh vực đó.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình cho chương trình khác gọi tới.
- **ID** (IDentifier) — mã định danh: giá trị riêng của một đối tượng, dùng để tìm lại đúng đối tượng ấy.

## Đọc hình

| Khái niệm theo bài nguồn | Ý của nguồn | Chỗ đối chiếu (Microsoft) |
|---|---|---|
| Thiết kế hướng miền | Dẫn dắt thiết kế phần mềm bằng mô hình hoá miền; ngôn ngữ thống nhất là một khái niệm then chốt; mô hình miền là cầu nối giữa các miền nghiệp vụ | khớp, và nói rõ hơn: ngôn ngữ chung do lập trình viên và chuyên gia miền cùng tạo ra, và mỗi ngữ cảnh có thể có ngôn ngữ riêng (cùng chữ "tài khoản" nghĩa khác nhau) |
| Thực thể nghiệp vụ | Mô hình diễn đạt khái niệm nghiệp vụ và dẫn dắt phần mềm như cơ sở dữ liệu, API | khớp: thực thể có mã định danh bền theo thời gian |
| Ranh giới mô hình | Ranh giới lỏng giữa các nhóm mô hình, dùng để mô tả quan hệ nghiệp vụ | khớp: ngữ cảnh có ranh giới là nơi một mô hình miền áp dụng, các ngữ cảnh vẫn tương tác và được ghi trên một bản đồ ngữ cảnh |
| Khối nhất quán | Cụm đối tượng liên quan, coi như một đơn vị khi đổi dữ liệu | khớp: ranh giới nhất quán quanh một hay nhiều thực thể, có đúng một thực thể gốc |
| Thực thể và đối tượng giá trị | Có những mô hình dùng-một-lần, không có mã định danh, chỉ là phần mô tả của một thực thể | khớp: đối tượng giá trị không có mã định danh, bất biến, hai bản cùng giá trị thì thay thế được cho nhau |
| Mô hình thao tác | Có các đối tượng đóng vai "người vận hành" để thao tác trên mô hình | khớp: dịch vụ miền chứa luật nghiệp vụ trải qua nhiều thực thể; dịch vụ ứng dụng điều phối ca sử dụng |
| Chia tầng kiến trúc | Chia đối tượng thành các tầng như mạng máy tính để giảm độ phức tạp | không khớp trực tiếp, xem phần dưới |
| Dựng mô hình miền | Có nhiều cách rút mô hình từ kiến thức nghiệp vụ | khớp: quy trình bốn bước, phân tích miền, xác định ngữ cảnh, xác định thực thể, khối và dịch vụ, xác định dịch vụ nhỏ |

## Hai nghĩa của chữ "tầng"

Nguồn dùng "tầng" để nói cách tổ chức mã bên trong một khối phần mềm: lớp giao diện gọi lớp ứng dụng, lớp ứng dụng gọi lớp miền. Tài liệu Microsoft dùng cùng chữ ở nghĩa khác: khi chia một hệ thành nhiều dịch vụ nhỏ, hãy cắt theo năng lực nghiệp vụ chứ không cắt theo tầng ngang như truy cập dữ liệu hay nhắn tin. Hai lời khuyên không mâu thuẫn: tầng nằm bên trong một dịch vụ, ranh giới dịch vụ chạy dọc theo nghiệp vụ. Nhưng đọc cẩu thả sẽ ra một hệ thống có "dịch vụ tầng dữ liệu", là điều tài liệu Microsoft khuyên tránh.

## Thử: một quy tắc chia tầng kiểm bằng mã

Một quy tắc chia tầng đơn giản, kiểu cổ điển: mỗi tệp chỉ được nhập từ tầng của nó hoặc các tầng thấp hơn trong danh sách trình bày, ứng dụng, miền, hạ tầng. Đây là một xếp hạng một chiều; nhiều dự án thiết kế hướng miền thì ngược lại, giữ tầng miền độc lập (miền không nhập gì từ ngoài nó, còn hạ tầng được nhập miền để cài đặt các giao diện của miền), nên họ viết thẳng đồ thị nhập được phép thành một bảng thay vì một danh sách thứ tự. Việc đếm "tệp nào nhập tầng cao hơn" tính toán được, nên đáng giao cho một đoạn chương trình thay vì nhờ người đọc soát:

Đoạn chương trình dài khoảng mười lăm dòng: duyệt mọi tệp `.py`, dùng `ast` đọc từng câu lệnh `import`, và báo mọi cặp (tệp, mô-đun) mà tầng được nhập cao hơn tầng của tệp. Ngày 2026-10-19, Python 3.13.16, trên dự án giả do một chương trình sinh ra:

| Dự án giả | Số vi phạm cài vào | Số vi phạm tìm ra | Thời gian kiểm |
|---|---|---|---|
| 12 tệp | 1 (tệp của tầng miền nhập tầng ứng dụng) | 1, đúng tệp đó | 0,001 đến 0,002 giây |
| 10.000 tệp, 30.000 câu lệnh nhập | 0 | 0 | 0,71 đến 0,78 giây |
| 10.000 tệp | 5 | 5 | 0,69 đến 0,75 giây |

Quy tắc kiểm tra được trong dưới một giây cho một vạn tệp, nên có thể chạy ở mọi lần đẩy mã. Điều bộ kiểm không làm được: nó biết tệp nhập tầng nào, không biết tầng đặt đúng chỗ hay chưa, và không thấy phụ thuộc đi qua tên động hay tệp cấu hình.

## Giới hạn cần nhớ

Bài nguồn chỉ có một hai câu cho mỗi khái niệm nên cột "ý của nguồn" là tóm lược; phần đối chiếu lấy hai trang của Microsoft về DDD, chưa đối chiếu với cuốn sách của Eric Evans (không truy cập được lúc viết). Bài này đọc "chia tầng" theo mô tả ngắn của nguồn; nguồn có hình mà phần chữ không nêu hết. Dự án thử do chương trình sinh nên chỉ chứng tỏ bộ kiểm chạy đúng và nhanh, không nói gì về mã thật; danh sách bốn tầng và thứ tự một chiều dùng ở đây là một lựa chọn của người biên soạn, nguồn không quy định tầng nào; thay bằng bảng đồ thị nhập được phép (như cách làm của miền độc lập ở trên) thì cùng đoạn chương trình vẫn dùng được, chỉ đổi điều kiện kiểm.

## Nhìn hình trả lời

Đội bạn tách hệ thống thành ba dịch vụ: "giao diện", "nghiệp vụ", "dữ liệu", mỗi dịch vụ một nhóm. Theo hai nguồn, điều gì đáng lo, và nên cắt lại thế nào?

<details>
<summary>Xem đáp án</summary>

Đó là cắt theo tầng ngang, điều tài liệu Microsoft khuyên tránh vì mỗi thay đổi nghiệp vụ phải đi qua cả ba dịch vụ. Nên cắt theo năng lực nghiệp vụ (ví dụ giao hàng, tài khoản, đội bay), mỗi dịch vụ tự có đủ giao diện, nghiệp vụ và dữ liệu của mình; tầng (như nguồn nói) nằm bên trong từng dịch vụ và được kiểm bằng một bộ kiểm tầng như ở trên.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và tám đoạn ngắn. Bài này giữ tám khái niệm theo đúng thứ tự, thêm cột đối chiếu, tách hai nghĩa của chữ "tầng" và thay phần mô tả chung bằng một bộ kiểm có thể chạy.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/8-key-concepts-in-ddd.md): tám khái niệm.
- [Microsoft — Use domain analysis to model microservices](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/microservices/model/domain-analysis.md): ngữ cảnh có ranh giới, ngôn ngữ chung, bản đồ ngữ cảnh, quy trình bốn bước, cắt theo năng lực nghiệp vụ. Đọc từ bản sao cục bộ.
- [Microsoft — Use tactical DDD to design microservices](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/microservices/model/tactical-domain-driven-design.md): thực thể, đối tượng giá trị, khối nhất quán, dịch vụ miền và dịch vụ ứng dụng. Đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

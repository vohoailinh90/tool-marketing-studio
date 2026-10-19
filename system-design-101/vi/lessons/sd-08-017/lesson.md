# Sáu mẫu kiến trúc phần mềm: mỗi mẫu một lợi, một hại, và một phép đo

**Bài nguồn nêu sáu mẫu kiến trúc, mỗi mẫu vài câu về lợi và hại. Bài này giữ đủ sáu mẫu theo thứ tự của nguồn, đối chiếu với tài liệu Microsoft về kiến trúc nhiều tầng, dịch vụ nhỏ và hướng sự kiện, và hướng dẫn của Python về phần mở rộng, rồi đo trên một máy một cái giá cho mỗi mẫu để thấy "hại" mà nguồn nói nặng hay nhẹ cỡ nào.**

![Ba khung. Khung một, sáu mẫu kiến trúc của nguồn, mỗi mẫu một lợi một hại: phân tầng nhanh dựng nhưng mã dễ lộn xộn; dịch vụ nhỏ chịu lỗi nhưng phức tạp; hướng sự kiện lỏng ghép nhưng khó thử; máy khách và máy chủ hợp thời gian thực nhưng máy chủ là điểm hỏng; phần mở rộng dễ mở rộng nhưng sửa lõi khó; lục giác bảo vệ lõi nhưng tốn thời gian dựng. Khung hai, sáu phép đo trên một máy: gọi qua HTTP tốn 220 đến 292 micro giây, trong tiến trình 0,08 đến 0,11; với 16 máy khách, máy chủ một luồng trả lời sau 33,5 mili giây, nhiều luồng 8,6; đổi chữ ký lõi làm hỏng 100 trên 100 phần mở rộng. Khung ba, số đo chỉ cho thấy hình dạng của chi phí.](../../diagrams/sd-08-017-main.svg)

## Từ viết tắt

- **IDE** (Integrated Development Environment) — môi trường phát triển tích hợp: phần mềm viết mã có trình soạn thảo, chạy thử và gỡ lỗi trong một cửa sổ; nguồn lấy nó làm ví dụ cho ứng dụng cần mở rộng dần.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách một chương trình gọi một dịch vụ qua mạng; ở bài này dùng trên máy để đo.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: lớp bảo đảm các byte tới đủ và đúng thứ tự; nhắc ở phép đo máy chủ, nơi kết nối bị từ chối phải thử lại.

## Đọc hình

| Mẫu của nguồn | Lợi (theo nguồn) | Hại (theo nguồn) | Đối chiếu | Phép thử trong bài |
|---|---|---|---|---|
| Phân tầng | Mỗi tầng một vai rõ; dựng nhanh | Mã dễ lộn xộn nếu thiếu luật | Microsoft: tầng trên gọi tầng dưới; tầng giữa chỉ chuyển tiếp thì thêm trễ mà không thêm giá trị | chi phí một tầng chuyển tiếp |
| Dịch vụ nhỏ | Chịu lỗi; co giãn từng phần | Ứng dụng phức tạp hơn | Microsoft: cô lập lỗi, co giãn riêng; thách thức là phức tạp, độ trễ mạng, nhất quán dữ liệu | một lời gọi qua HTTP so với trong tiến trình |
| Hướng sự kiện | Lỏng ghép | Khó thử từng thành phần | Microsoft: bên phát không biết ai nghe; nhưng nhất quán cuối cùng và gỡ lỗi bất đồng bộ là cái giá | thêm người nhận, và độ trễ tới khi người nhận thấy sự kiện |
| Máy khách và máy chủ | Hợp dịch vụ thời gian thực | Máy chủ thành điểm hỏng | chưa có tài liệu độc lập để đối chiếu | một máy chủ một luồng so với nhiều luồng |
| Phần mở rộng | Mở rộng dần, như IDE | Sửa lõi khó | hướng dẫn Python: ba cách tìm phần mở rộng (quy ước tên, gói không gian tên, siêu dữ liệu gói) | tìm 100 phần mở rộng; đổi chữ ký của lõi |
| Lục giác | Cô lập lõi khỏi bên ngoài | Tốn thời gian dựng, khó học | chưa có tài liệu độc lập để đối chiếu | cùng một lõi với hai bộ chuyển đổi |

## Thử: sáu cái giá trên một máy

Ngày 2026-10-19, Python 3.13.16 trên máy 4 lõi ảo, ba lần chạy mỗi phép đo. Mọi "dịch vụ" ở đây là một luồng hoặc một đối tượng trong chương trình thử; các con số cho thấy hình dạng của chi phí, không phải tốc độ của hệ thống thật.

| Mẫu | Phép đo | Kết quả |
|---|---|---|
| Phân tầng | Một lần gọi đi qua 0, 3 hoặc 7 tầng chỉ chuyển tiếp | 0,11 đến 0,17, 0,18 đến 0,30 và 0,27 đến 0,48 µs: thêm 0,02 đến 0,05 µs mỗi tầng |
| Dịch vụ nhỏ | Một lời gọi trong tiến trình và một lời gọi HTTP tới máy chủ trên cùng máy | 0,08 đến 0,11 µs và 220 đến 292 µs: gấp 2.100 đến 3.700 lần |
| Hướng sự kiện | Phát một sự kiện cho 0, 1, 10, 100 người nhận trong cùng luồng | 0,13 đến 0,23, 0,16 đến 0,27, 0,40 đến 0,66 và 2,4 đến 2,8 µs: mỗi người nhận thêm cỡ 0,02 µs |
| Hướng sự kiện | Từ lúc phát tới lúc một luồng người nhận thấy sự kiện, qua một hàng đợi | trung vị 51 đến 59 µs; 1% chậm nhất 333 đến 2.220 µs |
| Máy khách và máy chủ | Máy chủ chạy một việc 5 ms; 1, 4, 16 máy khách, máy chủ một luồng và nhiều luồng | 1 máy khách: 5,8 và 6,1 ms; 4: 22,3 đến 22,7 và 6,1 đến 6,4; 16: 33,4 đến 33,5 và 8,5 đến 8,6 ms |
| Phần mở rộng | Tìm và nạp 100 mô-đun phần mở rộng | tìm 9,0 đến 10,9 ms, nạp 13,6 đến 17,4 ms |
| Phần mở rộng | Lõi đổi hàm móc từ `run(ctx)` sang `run(ctx, opts)` | 100 trên 100 phần mở rộng lỗi; nếu lõi thử lại bằng dạng cũ: 0 trên 100 |
| Lục giác | Một lõi nhận đơn hàng qua cổng lưu trữ; bộ chuyển đổi bộ nhớ và bộ chuyển đổi `sqlite3` (ghi bền mỗi lần) | 0,20 đến 0,23 µs và 890 đến 960 µs; dòng mã của lõi không đổi |

Mỗi dòng đọc được một điều. Phân tầng tự nó rẻ: một tầng chỉ chuyển tiếp là một lần gọi hàm thêm, cái đắt là khi tầng thành một máy riêng (Microsoft nêu rõ tầng vật lý thêm trễ mạng). Dịch vụ nhỏ biến một lần gọi hàm thành một lần gọi qua mạng, gấp hàng nghìn lần ngay cả trên một máy, đó là cái "phức tạp hơn" của nguồn viết thành số. Hướng sự kiện thêm người nhận gần như miễn phí, nhưng người nhận thấy sự kiện sau chứ không cùng lúc, nên đọc ngay sau khi phát có thể ra dữ liệu cũ; đó cũng là một lý do khó thử, vì kết quả phụ thuộc thời điểm. Máy chủ một luồng xếp hàng: 4 máy khách chờ gấp bốn, và ở 16 máy khách, một phần yêu cầu còn phải chờ khoảng một giây vì hàng chờ kết nối mặc định của máy chủ thử chỉ 5, bị từ chối rồi TCP thử lại. Phần mở rộng tìm được 100 mô-đun trong cỡ chục mili giây, nhưng đổi hàm móc của lõi làm hỏng cả 100: "sửa lõi khó" là khó ở chỗ mọi phần mở rộng ngoài lõi đều bám vào giao diện đó. Lục giác không làm lõi chạy khác đi: cùng một lõi chạy với bộ nhớ trong dưới một micro giây (hữu ích cho thử nghiệm) và với `sqlite3` trong cỡ một mili giây; cái giá của nó là phải viết và giữ cổng, bộ chuyển đổi (xem giới hạn).

## Giới hạn cần nhớ

Phép đo chạy trong một tiến trình hoặc cùng máy, bằng Python, nên số tuyệt đối không nói gì về hệ thống thật; chỉ tỷ lệ và hướng là đáng đọc. Phép đo máy chủ có ảnh hưởng của hàng chờ kết nối mặc định (5) và của việc thử lại kết nối: các yêu cầu chậm nhất (1% chậm nhất 1,0 đến 1,5 giây ở 16 máy khách) là do việc đó, không phải do mẫu máy khách và máy chủ. Phép đo phần mở rộng không có lỗi nào trong chính phần mở rộng; hàm móc đổi chữ ký là một trường hợp tồi có chủ ý. Hai mẫu, máy khách và máy chủ, lục giác, chỉ được đối chiếu với nguồn: không đọc được tài liệu độc lập nào về hai mẫu này, và "tốn thời gian dựng, khó học" của lục giác không được đo ở đây.

## Nhìn hình trả lời

Nhóm bạn có một ứng dụng quản lý đơn hàng làm theo ba tầng, và một đồng nghiệp đề nghị tách mỗi tầng thành một dịch vụ nhỏ riêng "cho chắc". Theo nguồn và theo các phép đo, bạn nên cân nhắc điều gì trước khi đồng ý?

<details>
<summary>Xem đáp án</summary>

Mỗi lần một tầng gọi tầng dưới sẽ từ một lần gọi hàm thành một lần gọi qua mạng: phép đo ở đây là 220 đến 292 µs so với dưới 0,11 µs, gấp hàng nghìn lần, chưa kể độ trễ mạng thật, lỗi một phần và dữ liệu phải nhất quán giữa các dịch vụ. Microsoft cũng nói tầng giữa chỉ chuyển tiếp thì thêm trễ mà không thêm giá trị. Chỉ nên tách khi có lý do cụ thể (co giãn riêng, đội riêng, triển khai riêng); nếu mục tiêu chỉ là gọn mã, một luật phân tầng trong một khối đã đủ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và sáu đoạn, mỗi đoạn một mẫu với lợi và hại. Bài này giữ sáu mẫu theo đúng thứ tự, thêm cột đối chiếu, và biến mỗi mẫu thành một phép đo nhỏ; hai mẫu không có tài liệu độc lập thì ghi rõ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/6-software-architectural-patterns-you-must-know.md): sáu mẫu.
- [Microsoft — N-tier architecture style](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/architecture-styles/n-tier.md): tầng, tầng vật lý, tầng đóng và mở, tầng giữa chỉ chuyển tiếp. Đọc từ bản sao cục bộ.
- [Microsoft — Microservices architecture style](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/architecture-styles/microservices.md): lợi và thách thức của dịch vụ nhỏ. Đọc từ bản sao cục bộ.
- [Microsoft — Event-driven architecture style](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/architecture-styles/event-driven.md): bên phát và bên nhận tách rời, nhất quán cuối cùng, khi nào không nên dùng. Đọc từ bản sao cục bộ.
- [Python Packaging — Creating and discovering plugins](https://github.com/pypa/packaging.python.org/blob/d1ad4ad3d6d6f3a3582e4c6b8a1b6f8284f4cb3b/source/guides/creating-and-discovering-plugins.rst): ba cách tìm phần mở rộng. Đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

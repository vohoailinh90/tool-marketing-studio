# Kiến trúc dịch vụ nhỏ điển hình: bảy bộ phận, và mỗi bộ phận thêm một cái giá

**Bài nguồn vẽ một kiến trúc dịch vụ nhỏ "điển hình" và gọi tên bảy bộ phận: bộ cân bằng tải, CDN, cổng API, nhà cấp danh tính, sổ đăng ký và tìm dịch vụ, phần quản lý, và các dịch vụ với cơ sở dữ liệu riêng. Bài này giữ đủ bảy bộ phận theo thứ tự của nguồn, đối chiếu với tài liệu Microsoft về cổng API, dữ liệu và kiểu dịch vụ nhỏ, rồi dựng năm bộ phận ở mức đồ chơi trên một máy để đo cái giá mỗi bộ phận thêm vào một lời gọi.**

![Ba khung. Khung một, bảy bộ phận của kiến trúc dịch vụ nhỏ theo nguồn: bộ cân bằng tải, CDN và cổng API đứng trước các dịch vụ; nhà cấp danh tính xác thực; sổ đăng ký giúp cổng tìm dịch vụ; phần quản lý theo dõi; mỗi miền có cơ sở dữ liệu riêng. Khung hai, các phép đo trên một máy: qua cổng mất 0,9 mili giây thay vì 0,5; cổng gộp hai lời gọi thì 42 mili giây thay vì 82 khi mạng ngoài mất 40; hỏi sổ đăng ký mỗi lần 0,6 thay vì 0,24; kiểm chữ ký tại chỗ 2 micro giây, hỏi máy chủ khác 230; lấy 200 đơn kèm tên khách, một phép nối 0,2 mili giây, gọi từng đơn 50. Khung ba, cân bằng tải, CDN và quản lý chưa được đo.](../../diagrams/sd-08-023-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt ở nhiều nơi, giữ sẵn nội dung tĩnh (ảnh, tệp) để người dùng lấy từ máy gần mình.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình cho chương trình khác gọi nó; "cổng API" là chỗ nhận các lời gọi từ bên ngoài.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách một chương trình gọi một dịch vụ qua mạng; ở bài này dùng trên máy để đo.

## Đọc hình

| Bộ phận (theo nguồn) | Nguồn nói | Đối chiếu | Phép thử trong bài |
|---|---|---|---|
| Bộ cân bằng tải | chia lưu lượng đến cho nhiều dịch vụ phía sau | chưa dựng | không |
| CDN | nhóm máy chủ phân bố địa lý giữ nội dung tĩnh; người dùng tìm ở CDN trước rồi mới tới dịch vụ | chưa dựng | không |
| Cổng API | nhận yêu cầu và chuyển tới dịch vụ liên quan; nói chuyện với nhà cấp danh tính và sổ đăng ký | Microsoft: điểm vào chung, đóng vai máy chủ ủy nhiệm, định tuyến, gộp lời gọi, gánh việc chung; không có cổng thì máy khách phải biết nhiều địa chỉ và gọi nhiều vòng | một lời gọi qua cổng; một lời gọi gộp |
| Nhà cấp danh tính | xác thực và cấp quyền cho người dùng | Microsoft: cổng có thể gánh xác thực | kiểm chữ ký tại chỗ so với hỏi một máy chủ |
| Sổ đăng ký và tìm dịch vụ | dịch vụ đăng ký ở đây; cổng tìm dịch vụ cần gọi ở đây | Microsoft: tìm dịch vụ là một thách thức của kiểu này | tra sổ mỗi lần so với nhớ địa chỉ |
| Quản lý | theo dõi các dịch vụ | Microsoft gọi phần "quản lý" là điều phối (xếp lịch, phát hiện lỗi, tự co giãn) và tách "quan sát" thành một phần riêng | giá của một số đếm và một dòng nhật ký |
| Dịch vụ nhỏ | mỗi miền có cơ sở dữ liệu riêng | Microsoft: hai dịch vụ không dùng chung kho dữ liệu; "một sự kiện, một chỗ" không còn; bản sao chỉ nhất quán sau cùng | lấy 200 đơn kèm tên khách từ hai dịch vụ |

## Thử: năm cái giá trên một máy

Ngày 2026-10-19, Python 3.13.16 trên máy 4 lõi ảo; ba lần chạy mỗi phép đo (khoảng giá trị là nhỏ nhất đến lớn nhất qua ba lần). Mọi "dịch vụ" là một luồng máy chủ HTTP trong cùng chương trình, nói chuyện qua cổng máy cục bộ, mỗi dịch vụ một tệp cơ sở dữ liệu `sqlite3` riêng. Mạng thật chậm hơn nhiều, nên các số cho thấy hình dạng của chi phí, không phải tốc độ của hệ thống thật.

| Bộ phận | Phép đo | Kết quả |
|---|---|---|
| Cổng API | Một lời gọi thẳng tới dịch vụ đơn hàng, và cùng lời gọi đi qua cổng (một máy chủ chuyển tiếp) | 491 đến 555 µs và 908 đến 960 µs: cổng thêm một chặng, gần gấp đôi |
| Cổng API (gộp) | Máy khách cần khách hàng và đơn hàng của họ; mạng ngoài được đặt thêm 40 ms mỗi vòng đi về | hai lời gọi thẳng: 82,3 đến 82,4 ms; một lời gọi tới cổng (cổng tự gọi hai dịch vụ bên trong): 42,2 đến 42,4 ms |
| Nhà cấp danh tính | Kiểm chữ ký của thẻ ngay trong dịch vụ, và hỏi một máy chủ cấp quyền qua HTTP mỗi lần | 1,8 đến 2,9 µs và 223 đến 243 µs |
| Sổ đăng ký | Gọi dịch vụ với địa chỉ đã nhớ, và tra sổ đăng ký trước mỗi lời gọi | 230 đến 250 µs và 589 đến 606 µs; 1% chậm nhất 421 đến 535 µs và 2.003 đến 2.509 µs |
| Quản lý | Tăng một số đếm có khóa; ghi một dòng nhật ký mức `INFO` vào tệp; một dòng mức thấp hơn ngưỡng bị bỏ | 0,24 đến 0,47 µs; 13 đến 18 µs; 0,19 đến 0,32 µs |
| Dịch vụ nhỏ | 200 đơn mới nhất kèm tên khách (1.000 khách, 20.000 đơn): một cơ sở dữ liệu có phép nối; hai dịch vụ, gọi dịch vụ khách hàng cho từng đơn; hai dịch vụ, một lời gọi cho cả nhóm khách | 0,17 đến 0,25 ms; 49,6 đến 60,0 ms; 1,92 đến 2,04 ms |

Rồi đổi tên khách số 5 (18 đơn): phép nối trong một cơ sở dữ liệu và dịch vụ khách hàng đều trả tên mới, còn bản sao tên mà dịch vụ đơn hàng giữ cho mình vẫn trả tên cũ cho đến khi được làm mới.

Mỗi dòng đọc được một điều. Cổng thêm một chặng cho mọi lời gọi, nhưng nếu máy khách ở xa thì gộp nhiều lời gọi thành một cắt gần một nửa thời gian chờ: cái giá và cái lợi của cổng nằm ở hai chỗ khác nhau. Thẻ kiểm tại chỗ rẻ hơn hỏi máy chủ cỡ một trăm lần, nên danh tính thường chỉ được hỏi lúc cấp thẻ, không phải mỗi lời gọi. Tra sổ đăng ký mỗi lần thêm một lời gọi và làm đuôi chậm dài ra, nên nhớ địa chỉ rồi làm mới là thói quen thường gặp. Theo dõi gần như miễn phí khi chỉ đếm, và đắt hơn khi ghi từng dòng. Cái giá lớn nhất là dữ liệu: bỏ phép nối vì mỗi dịch vụ có cơ sở dữ liệu riêng thì một báo cáo 200 dòng thành 200 lời gọi (gấp hàng trăm lần), trừ khi gom thành một lời gọi hoặc giữ bản sao, và bản sao thì cũ đi khi dữ liệu gốc đổi. Đó là điều Microsoft viết thành "nhất quán sau cùng".

## Giới hạn cần nhớ

Mọi phép đo chạy trên một máy, bằng Python, với máy chủ đồ chơi, nên số tuyệt đối không nói gì về hệ thống thật; chỉ tỷ lệ và hướng là đáng đọc. Con số 40 ms của mạng ngoài là số tôi đặt vào để xem hình dạng, không phải số đo. Bộ cân bằng tải và CDN chưa được dựng hay đo (CDN phụ thuộc vào địa lý, thứ một máy không có), và phần quản lý chỉ được đo ở mặt "đếm và ghi nhật ký", chưa đo điều phối, vốn là nghĩa Microsoft dùng cho từ này. Máy chủ cấp quyền, sổ đăng ký và dịch vụ ở đây không chịu tải, không hỏng và không chậm. Phần "thẻ có chữ ký" là một mã xác thực đơn giản của riêng bài, không phải một chuẩn thẻ thật.

## Nhìn hình trả lời

Màn hình "danh sách 200 đơn kèm tên khách" của bạn chậm hẳn sau khi tách thành hai dịch vụ, mỗi dịch vụ một cơ sở dữ liệu. Theo bảng đo, nguyên nhân có thể là gì và có những cách sửa nào, kèm cái giá của từng cách?

<details>
<summary>Xem đáp án</summary>

Rất có thể là một lời gọi qua mạng cho từng đơn (200 lời gọi, cỡ 50 ms trên một máy, hơn thế nhiều khi mạng thật). Cách một: gom thành một lời gọi lấy tên cho cả nhóm khách (cỡ 2 ms trong phép đo), giá là phải thêm đường lấy theo nhóm ở dịch vụ khách hàng. Cách hai: dịch vụ đơn hàng giữ bản sao tên khách, giá là bản sao cũ đi khi khách đổi tên cho tới lúc được làm mới. Giữ lại phép nối trong một cơ sở dữ liệu thì rẻ nhất (cỡ 0,2 ms) nhưng đi ngược nguyên tắc mỗi dịch vụ giữ dữ liệu riêng.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và một danh sách bảy bộ phận, mỗi bộ phận một hai câu. Bài này giữ nguyên bảy bộ phận theo thứ tự, thêm cột đối chiếu, và biến năm bộ phận thành năm phép đo nhỏ; từ "quản lý" trong nguồn nghĩa là theo dõi, còn trong tài liệu Microsoft là điều phối, và bài ghi rõ sự khác đó.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-does-a-typical-microservice-architecture-look-like.md): bảy bộ phận.
- [Microsoft — Microservices architecture style](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/architecture-styles/microservices.md): các thành phần, cổng API, quản lý hay điều phối, quan sát, dữ liệu, thách thức. Đọc từ bản sao cục bộ.
- [Microsoft — API gateways](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/microservices/design/gateway-content.md): điểm vào chung, định tuyến, gộp, gánh việc chung, vì sao nên dùng. Đọc từ bản sao cục bộ.
- [Microsoft — Data considerations for microservices](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/microservices/design/data-considerations.md): mỗi dịch vụ một kho dữ liệu riêng, bản sao nhất quán sau cùng. Đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

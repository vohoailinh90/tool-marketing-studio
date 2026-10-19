# Chín việc khi xây dịch vụ nhỏ: thiết kế cho lỗi, thử ba lớp bảo vệ trên một dịch vụ giả

**Bài nguồn nói xây hệ thống bằng dịch vụ nhỏ là rất khó nếu không theo vài nguyên tắc vững, và liệt kê chín việc, mỗi việc vài câu. Bài này giữ đủ chín việc, nói việc nào có tài liệu độc lập đối chiếu, rồi lấy việc đầu tiên, "thiết kế cho lỗi", ra thử: một dịch vụ giả bị chậm, bị lỗi ngẫu nhiên và bị chết, và ba lớp bảo vệ (hạn chờ, thử lại, ngắt mạch) được đo xem chúng cứu và gây ra điều gì.**

![Ba khung. Khung một, chín việc của nguồn: thiết kế cho lỗi, dịch vụ nhỏ, giao thức nhẹ, khám phá dịch vụ, dữ liệu riêng, mẫu chịu lỗi, bảo mật mọi tầng, nhật ký tập trung và đóng gói container; bài này chỉ đo thiết kế cho lỗi và mẫu chịu lỗi. Khung hai, dịch vụ phụ thuộc trả lời sau 200 mili giây: 20 lần gọi không đặt hạn mất 4,04 giây, đặt hạn 50 mili giây mất 1,01 giây nhưng thất bại hết, thêm bộ ngắt mạch chỉ còn 0,25 đến 0,33 giây và 5 lần gọi tới dịch vụ. Khung ba, dịch vụ lỗi 30 phần trăm: thử lại tối đa ba lần nâng thành công từ 1.416 lên 1.936 trên 2.000 lần nhưng tăng tải lên 2.792 lần gọi; khi dịch vụ chết hẳn, ba lần thử gây 1.500 lần gọi còn bộ ngắt mạch chỉ 5.](../../diagrams/sd-08-014-main.svg)

## Từ viết tắt

- **REST** (REpresentational State Transfer) — chuyển giao trạng thái đại diện: cách thiết kế giao diện web theo từng địa chỉ tài nguyên; một trong các giao thức nhẹ mà nguồn nêu.
- **gRPC** (gRPC Remote Procedure Calls) — các lời gọi hàm từ xa của gRPC: giao thức để một dịch vụ gọi hàm của dịch vụ khác như gọi hàm trong chương trình.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách quen thuộc để một chương trình gọi một dịch vụ qua mạng; ở bài này dùng trên máy để đo.

## Đọc hình

| Việc theo bài nguồn | Ý của nguồn | Chỗ đối chiếu |
|---|---|---|
| Thiết kế cho lỗi | Hệ phân tán dịch vụ nhỏ sẽ hỏng; chịu lỗi ở hạ tầng, cơ sở dữ liệu và từng dịch vụ; dùng ngắt mạch, vách ngăn hay hạ cấp có kiểm soát | Microsoft: mẫu Circuit Breaker và Retry (đã đọc, đo bên dưới); mẫu Bulkhead nói về cô lập tài nguyên theo nhóm, chưa thử |
| Xây dịch vụ nhỏ | Một dịch vụ làm tốt một việc | chưa đối chiếu ở bài này |
| Giao thức nhẹ | REST, gRPC hay bộ trung gian thông điệp | chưa đối chiếu |
| Khám phá dịch vụ | Dịch vụ tìm nhau qua mạng bằng công cụ chuyên dụng | Microsoft nhắc khám phá dịch vụ là chức năng nền tảng có hay không tuỳ dịch vụ chạy |
| Dữ liệu riêng | Mỗi dịch vụ sở hữu và quản lý dữ liệu của mình để giảm ràng buộc | Microsoft: mỗi dịch vụ giữ kho dữ liệu riêng |
| Mẫu chịu lỗi | Thử lại, bộ nhớ đệm, giới hạn tốc độ để tăng độ sẵn sàng | Microsoft: mẫu Retry (đo bên dưới); giới hạn tốc độ và bộ nhớ đệm chưa đọc kỹ, chưa thử |
| Bảo mật mọi tầng | Bề mặt tấn công rộng nên bảo mật ở mọi chặng của đường giao tiếp | chưa đối chiếu |
| Nhật ký tập trung | Nhiều dịch vụ thì nhật ký càng quan trọng | chưa đối chiếu |
| Đóng gói container | Triển khai cô lập, dễ mở rộng | chưa đối chiếu |

Tài liệu Microsoft về ngắt mạch nói rõ hai điều bài đo bên dưới làm thấy được: gọi lại liên tục một việc khó thành công chỉ phí tài nguyên; và một hạn chờ làm các lời gọi khác bị chặn cho tới khi hết hạn nên cần hạn đủ ngắn nhưng vẫn đủ dài để phần lớn lần gọi thành công. Cũng theo tài liệu về Retry, chỉ thử lại việc an toàn khi lặp (idempotent), vì thử lại có thể làm một việc chạy hai lần.

## Thử: ba lớp bảo vệ trên một dịch vụ giả

Ngày 2026-10-19, một máy ảo 4 lõi, Python 3.13.16: một máy chủ HTTP giả viết bằng thư viện chuẩn đóng vai dịch vụ phụ thuộc, bên gọi là một chương trình riêng. Bộ ngắt mạch là bộ đơn giản tự viết: mở sau 5 lần thất bại liên tiếp, thử lại sau 1 giây. Ba lần chạy cho cùng kết quả; phần lỗi ngẫu nhiên dùng hạt giống cố định.

**Dịch vụ phụ thuộc trả lời đúng, nhưng sau 200 mili giây** (20 lần gọi nối tiếp):

| Bên gọi | Thành công | Thời gian | Số lần gọi tới dịch vụ |
|---|---|---|---|
| không đặt hạn chờ | 20 trên 20 | 4,03 đến 4,04 giây | 20 |
| hạn chờ 50 mili giây | 0 trên 20 | 1,01 giây | 20 |
| hạn chờ 50 mili giây và ngắt mạch | 0 trên 20 | 0,25 đến 0,33 giây | 5 |

**Dịch vụ lỗi 30% số lần gọi** (2.000 yêu cầu):

| Bên gọi | Thành công | Số lần gọi tới dịch vụ |
|---|---|---|
| không thử lại | 1.416 trên 2.000 (70,8%) | 2.000 |
| tối đa 3 lần thử | 1.936 trên 2.000 (96,8%) | 2.792 |

**Dịch vụ chết hẳn** (luôn trả lỗi, 500 yêu cầu):

| Bên gọi | Thành công | Thời gian | Số lần gọi tới dịch vụ |
|---|---|---|---|
| tối đa 3 lần thử | 0 | 1,20 đến 1,29 giây | 1.500 |
| tối đa 3 lần thử và ngắt mạch | 0 | dưới 0,01 giây | 5 |

Ba bài học. Một, hạn chờ giữ cho bên gọi không phải đợi quá ngân sách thời gian của chính nó, nên nó có lợi cả khi dịch vụ vẫn trả lời đúng nhưng chậm; kết quả 0 trên 20 là hệ quả của việc chọn hạn 50 mili giây, ngắn hơn hẳn thời gian trả lời 200 mili giây của dịch vụ này. Hạn nên đặt theo ngân sách thời gian từ đầu đến cuối của bên gọi và theo phân bố thời gian trả lời đã quan sát, không theo một con số tùy ý. Hai, thử lại cứu được lỗi ngẫu nhiên (từ 70,8% lên 96,8%) nhưng trả bằng tải: 2.792 lần gọi thay vì 2.000, tức thêm 40%; và khi dịch vụ chết, nó nhân ba tải đúng lúc dịch vụ yếu nhất. Ba, ngắt mạch là thứ chặn hiệu ứng đó: 5 lần gọi thay vì 1.500, và bên gọi trả lỗi ngay chứ không đợi.

## Giới hạn cần nhớ

Dịch vụ giả chạy trên cùng máy với bên gọi, nên không có độ trễ mạng, hàng đợi hay nhiều bên gọi cùng lúc; nó cũng không chịu tải thật nên không thể nói gì về "sập dây chuyền". Bộ ngắt mạch tự viết không có trạng thái nửa mở đầy đủ như mô tả của Microsoft. Mô hình lỗi chỉ gồm chậm, lỗi ngẫu nhiên 30% và chết hẳn; lỗi thật thường lẫn lộn. Thử lại ở đây không có độ trễ tăng dần (exponential backoff). Độ trễ tăng dần chỉ làm giảm tốc độ gọi tức thời và cho dịch vụ thời gian hồi phục; nếu mọi lần thử đều chạy xong thì tổng số lần gọi vẫn như vậy, nên con số 1.500 ở đây không bị nó thay đổi. Bảy trong chín việc của nguồn không được thử.

## Nhìn hình trả lời

Dịch vụ thanh toán đôi khi chậm hơn một giây vì cơ sở dữ liệu bận. Đội bạn đặt hạn chờ 200 mili giây và thử lại 3 lần cho "an toàn". Điều gì có thể xảy ra, và nên làm gì?

<details>
<summary>Xem đáp án</summary>

Hạn 200 mili giây ngắn hơn thời gian chậm bình thường nên các lần gọi chậm-nhưng-đúng bị coi là lỗi, rồi bị thử lại ba lần: tải lên dịch vụ đang bận tăng gấp ba (như 1.500 lần gọi so với 500 trong phép thử dịch vụ chết). Nên đặt hạn đủ dài cho trường hợp chậm bình thường, thử lại có độ trễ tăng dần và chỉ với việc an toàn khi lặp (một lệnh thu tiền thì không), và thêm ngắt mạch để ngừng gọi khi dịch vụ đang quá yếu.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một sơ đồ và một đoạn ngắn cho mỗi việc. Bài này giữ chín việc, thêm cột đối chiếu với tài liệu Microsoft, chọn việc "thiết kế cho lỗi" và "mẫu chịu lỗi" để đo, và nói rõ việc nào chưa đối chiếu hay chưa đo.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/9-best-practices-for-building-microservices.md): chín việc.
- [Microsoft — Circuit Breaker pattern](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/circuit-breaker.md): đừng gọi liên tục việc khó thành công; hạn chờ ngắn nhưng đủ dài. Đọc từ bản sao cục bộ.
- [Microsoft — Retry pattern](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/retry-content.md): thử lại có trì hoãn; chỉ thử lại việc an toàn khi lặp. Đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

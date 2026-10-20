# Năm mẫu kiến trúc hàng đầu: nguồn không nêu tên, nên bài đo năm lựa chọn mà mọi kiểu đều đẩy cho bạn

**Bài nguồn có tựa là năm mẫu kiến trúc, nhưng phần chữ chỉ có ba đoạn dẫn: kiến trúc là bản thiết kế cách các thành phần tác động lẫn nhau, mẫu cho lời giải sẵn cho vấn đề thường gặp, và có một bảng tóm tắt để nhớ nhanh. Năm cái tên nằm trong ảnh, mà bài này không dùng. Vì vậy bài không đoán năm mẫu của ảnh. Nó lấy bảng các kiểu kiến trúc của Microsoft để thấy mỗi kiểu thiên về điều gì, rồi đo năm lựa chọn nhỏ mà việc chọn kiểu đẩy cho người thiết kế: chờ ở đâu, co giãn ra sao, gọi nhau thế nào, lưu dữ liệu thế nào, và hỏng thì sao.**

![Ba khung. Khung một, phần chữ của nguồn không nêu tên năm mẫu nào, nên bài đặt năm lựa chọn mà việc chọn kiểu kiến trúc đẩy cho bạn: chờ ở đâu, co giãn ra sao, gọi nhau thế nào, lưu dữ liệu thế nào, hỏng thì sao. Khung hai, năm phép đo trên một máy: 50 lần chờ 20 mili giây mất 1,01 giây khi tuần tự và 0,022 giây khi đồng thời; bốn tiến trình nhanh gấp 2 đến 2,5 lần chứ không gấp 4; một truy vấn 0,23 mili giây thay vì ba lời gọi 0,7; đổi tên khách tốn 3 micro giây khi chuẩn hóa và 100 đến 140 khi dữ liệu phẳng; thử lại tối đa 3 lần nâng tỷ lệ thành công từ 71% lên 97%. Khung ba, một máy, đồ chơi; số chỉ cho thấy hình dạng.](../../diagrams/sd-08-024-main.svg)

## Từ viết tắt

- **REST** (REpresentational State Transfer) — chuyển trạng thái biểu diễn: lối thiết kế dịch vụ web mà mỗi loại dữ liệu có một địa chỉ riêng để gọi; ở bài này là cách "ba lời gọi riêng" so với "một truy vấn".
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách một chương trình gọi một dịch vụ qua mạng; ở bài này dùng trên máy để đo.

## Đọc hình

Nguồn nói gì, theo từng ý của phần chữ, và bảng kiểu kiến trúc của Microsoft làm khung để đặt các lựa chọn vào:

| Điều nguồn nói | Điều bài làm với nó |
|---|---|
| Kiến trúc định hình cấu trúc và hành vi của hệ thống, là bản thiết kế cách các thành phần tác động nhau | giữ làm điểm xuất phát |
| Mẫu cho lời giải sẵn cho vấn đề thường gặp, tiết kiệm thời gian, hệ thống bền hơn | kiểm: mỗi lời giải đi kèm một cái giá, đo ở dưới |
| Khó chọn giữa nhiều kiểu và mẫu; có bảng tóm tắt để nhớ đặc điểm chính | bảng tóm tắt nằm trong ảnh, bài không dùng; thay bằng bảng của Microsoft |

| Lựa chọn | Kiểu Microsoft thường gắn với nó | Phép đo trong bài |
|---|---|---|
| Chờ ở đâu | kiểu hướng sự kiện và kiểu web, hàng đợi, bộ xử lý nền: tách bằng tin nhắn bất đồng bộ | 50 lần chờ 20 ms, tuần tự và đồng thời |
| Co giãn ra sao | kiểu tính toán lớn: chia việc ra nhiều lõi; kiểu dịch vụ nhỏ: co giãn từng dịch vụ | một việc tính toán chia cho 1, 2, 4 tiến trình, có phần không chia được |
| Gọi nhau thế nào | kiểu dịch vụ nhỏ: Microsoft nêu chi phí liên lạc giữa dịch vụ, gây trễ | ba lời gọi `REST` so với một truy vấn lấy đúng trường |
| Lưu dữ liệu thế nào | kiểu nhiều tầng thường một kho chung; dịch vụ nhỏ mỗi dịch vụ một kho riêng | bảng chuẩn hóa so với bảng phẳng: đọc, đổi tên, dung lượng |
| Hỏng thì sao | mọi kiểu có lời gọi qua mạng; Microsoft có riêng mẫu thử lại và mẫu ngắt mạch | thời hạn chờ, thử lại, ngắt mạch trước một dịch vụ chậm, hỏng 30% và sập |

Microsoft nói thẳng rằng mỗi kiểu là một bộ ràng buộc và có cái giá đi kèm: độ phức tạp, tin nhắn bất đồng bộ kéo theo nhất quán sau cùng, chi phí liên lạc giữa dịch vụ, và việc quản lý hệ thống. Năm lựa chọn dưới đây là năm chỗ cái giá ấy hiện ra thành số.

## Thử: năm lựa chọn trên một máy

Ngày 2026-10-19, Python 3.13.16 trên máy 4 lõi ảo. Ba lần chạy cho các phép đo chung, hai lần cho phép đo thử lại (khoảng giá trị là nhỏ nhất đến lớn nhất). Mọi "dịch vụ" là một luồng máy chủ `HTTP` trong cùng chương trình; mạng thật chậm hơn nhiều.

| Lựa chọn | Phép đo | Kết quả |
|---|---|---|
| Chờ ở đâu | 50 lần chờ 20 ms: lần lượt, và đồng thời bằng `asyncio` | 1,008 đến 1,010 s và 0,022 s |
| Chờ ở đâu | 20.000 việc tính toán rất nhỏ không chờ gì: gọi hàm thường, và làm thành tác vụ `asyncio` | 0,0035 đến 0,0047 s và 0,11 đến 0,16 s: chậm gấp 23 đến 45 lần |
| Co giãn ra sao | Một việc tính toán, trong đó 0,05 s không chia được; chia cho 2 và 4 tiến trình (máy có 4 lõi); tốc độ so với 1 tiến trình | 2 tiến trình: gấp 1,5 đến 2,05 lần; 4 tiến trình: gấp 1,95 đến 2,53 lần, không gấp 4 |
| Gọi nhau thế nào | Lấy tên người dùng, 20 đơn và địa chỉ: ba lời gọi `REST` riêng, và một truy vấn lấy đúng các trường cần | 4.083 byte, trung vị 683 đến 775 µs; 354 byte, 223 đến 246 µs |
| Lưu dữ liệu thế nào | 1.000 khách và 200.000 đơn: đọc đơn của một khách bằng phép nối và bằng bảng phẳng | 183 đến 215 µs và 182 đến 279 µs: gần như ngang nhau |
| Lưu dữ liệu thế nào | Đổi tên một khách (200 đơn): bảng chuẩn hóa, bảng phẳng | 3 µs (một dòng) và 98 đến 143 µs (200 dòng) |
| Lưu dữ liệu thế nào | Dung lượng của cùng dữ liệu | 2.609.152 byte chuẩn hóa so với 6.754.304 byte phẳng |
| Hỏng thì sao | Dịch vụ trả lời sau 200 ms; 20 lời gọi: không đặt thời hạn; thời hạn 50 ms; thời hạn 50 ms kèm ngắt mạch sau 5 lần hỏng | 20 trên 20 thành công trong 4,04 s; 0 trên 20 trong 1,01 s; 0 trên 20 trong 0,25 s và dịch vụ chỉ nhận 5 lời gọi thay vì 20 |
| Hỏng thì sao | Dịch vụ hỏng 30% số lời gọi; 2.000 lời gọi: không thử lại, thử tối đa 3 lần | 1.416 (70,8%) và 1.936 (96,8%) thành công; dịch vụ nhận 2.000 và 2.792 lời gọi |
| Hỏng thì sao | Dịch vụ sập hẳn; 500 lời gọi, mỗi lời thử tối đa 3 lần: không ngắt mạch, có ngắt mạch | dịch vụ nhận 1.500 lời gọi, và chỉ 5 lời gọi |

Mỗi dòng đọc được một điều. Bất đồng bộ cắt thời gian chờ từ 1 giây xuống 0,022 giây khi có việc đang chờ, nhưng là chậm hơn hàng chục lần khi việc không chờ gì, nên nó trả công cho việc chờ chứ không cho việc tính. Thêm tiến trình giúp nhưng có trần: phần không chia được và chi phí chia việc giữ tốc độ ở dưới mức 4 lần dù có 4 lõi. Gộp ba lời gọi thành một truy vấn lấy đúng trường giảm cả số byte lẫn thời gian, và đó là lý do các cổng gộp lời gọi. Chuẩn hóa trả giá lúc đọc nếu phải nối (ở đây gần ngang bảng phẳng vì có chỉ mục), được lợi lúc ghi và dung lượng: đổi tên rẻ hơn 30 đến 50 lần và dữ liệu nhỏ hơn gần 2,6 lần. Cuối cùng, thử lại cứu được lỗi thoáng qua (từ 71% lên 97% thành công, đúng với tính toán 1 trừ 0,3 lũy thừa 3 là 97,3%) nhưng tăng 40% số lời gọi tới dịch vụ; khi dịch vụ sập hẳn, thử lại nhân số lời gọi lên ba lần, còn ngắt mạch dừng chúng sau 5 lần. Microsoft nói đúng như vậy: mẫu thử lại dành cho lỗi thoáng qua, mẫu ngắt mạch dành cho lỗi kéo dài, hai mẫu phục vụ hai mục đích khác nhau.

## Giới hạn cần nhớ

Phép đo chạy trên một máy, bằng Python, với máy chủ đồ chơi, nên số tuyệt đối không nói gì về hệ thống thật; chỉ tỷ lệ và hướng là đáng đọc. Phép đo co giãn có một máy 4 lõi và vài lần chạy, nên các mức tăng tốc dao động (1,95 đến 2,53 ở 4 tiến trình). Ngắt mạch ở đây là bản đơn giản của riêng bài (đóng hoặc mở, có đồng hồ đặt lại 1 giây) và các phép đo kết thúc trước khi đồng hồ hết, nên việc thử lại dịch vụ đã hồi phục chưa được kiểm. Phép đo chuẩn hóa dùng một cơ sở dữ liệu trong bộ nhớ với chỉ mục. Quan trọng hơn cả: bài không nêu và không đo năm mẫu của ảnh nguồn; năm lựa chọn ở đây là cách đặt của người biên soạn, dựa trên bảng kiểu kiến trúc của Microsoft, không phải nội dung của nguồn.

## Nhìn hình trả lời

Một đồng nghiệp muốn "thêm thử lại tối đa 3 lần cho mọi lời gọi giữa các dịch vụ cho chắc". Theo phép đo, bạn lo điều gì, và nên đặt thêm gì?

<details>
<summary>Xem đáp án</summary>

Khi lỗi chỉ thoáng qua, thử lại giúp (thành công từ 71% lên 97% ở ba lần thử), nhưng mỗi lần thử là một lời gọi thêm tới dịch vụ: khi dịch vụ sập hẳn, 500 lời gọi thành 1.500 lời gọi, đúng lúc dịch vụ cần được nghỉ. Hãy đặt thời hạn chờ cho mỗi lời gọi (không đặt thì 20 lời gọi chậm chờ tổng cộng 4 giây), thử lại chỉ với việc làm lại được an toàn, và thêm ngắt mạch để dừng thử khi lỗi kéo dài (chỉ 5 lời gọi tới dịch vụ trong phép đo thay vì 1.500).

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình bảng tóm tắt và ba đoạn dẫn; phần chữ không gọi tên mẫu nào. Bài này giữ nguyên ý của ba đoạn dẫn, không đoán tên của năm mẫu trong ảnh, và thay vào đó dùng bảng kiểu kiến trúc của Microsoft cùng năm phép đo nhỏ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-5-software-architectural-patterns.md): ba đoạn dẫn; phần chữ không có tên mẫu nào.
- [Microsoft — Architecture styles](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/architecture-styles/index.md): các kiểu kiến trúc là bộ ràng buộc, bảng kiểu và miền phù hợp, các thách thức. Đọc từ bản sao cục bộ.
- [Microsoft — Retry pattern](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/retry-content.md): lỗi thoáng qua, thử lại, tính chất làm lại an toàn. Đọc từ bản sao cục bộ.
- [Microsoft — Circuit Breaker pattern](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/circuit-breaker.md): ngắt mạch khác mẫu thử lại, ba trạng thái. Đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

# Mười đánh đổi thiết kế hệ thống: bốn cặp thử được bằng một đoạn chương trình nhỏ

**Bài nguồn nói rằng ai không biết các đánh đổi thì chưa biết thiết kế hệ thống, và liệt kê mười cặp. Bài này giữ đủ mười cặp, nhưng chỉ nói thêm về bốn cặp mà một phép thử nhỏ trên một máy nói được điều gì đó (chuẩn hoá và phi chuẩn hoá, đồng bộ và bất đồng bộ, mở rộng dọc và ngang, REST và một truy vấn chọn trường); sáu cặp còn lại được giữ nguyên ý của nguồn và ghi rõ là chưa đo.**

![Ba khung. Khung một, mười cặp đánh đổi của nguồn, trong đó bài này đo bốn cặp: chuẩn hoá với phi chuẩn hoá, đồng bộ với bất đồng bộ, mở rộng dọc với mở rộng ngang, và REST với một truy vấn chọn trường. Khung hai, kết quả: truy vấn đọc có nối bảng chậm tương đương bảng phẳng, nhưng đổi tên một khách phải sửa 200 hàng thay vì 1 và bảng phẳng to gấp khoảng 2,6 lần; 50 lần chờ 20 mili giây mất 1,01 giây nối đuôi và 0,022 giây khi chạy đồng thời, nhưng 20.000 việc nhỏ chậm hơn khoảng 35 đến 50 lần; chia việc cho gấp bốn số tiến trình trên một máy, một phép tương tự của mở rộng ngang, chỉ nhanh 2,2 đến 2,5 lần; ba lời gọi REST là 4.083 byte còn một truy vấn là 354 byte. Khung ba, sáu cặp chưa đo.](../../diagrams/sd-08-012-main.svg)

## Từ viết tắt

- **REST** (REpresentational State Transfer) — chuyển giao trạng thái đại diện: cách thiết kế giao diện web theo từng địa chỉ tài nguyên (người dùng, đơn hàng...), mỗi lời gọi lấy một tài nguyên.
- **NoSQL** (Not only SQL) — "không chỉ SQL": tên chung của các cơ sở dữ liệu không xếp dữ liệu thành bảng cố định hàng cột, thường có lược đồ linh hoạt.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ.

## Đọc hình

| Cặp đánh đổi | Ý của bài nguồn | Trong bài này |
|---|---|---|
| Mở rộng dọc và ngang | Dọc là thêm tài nguyên cho một máy, ngang là thêm máy vào nhóm | chỉ đo một phép tương tự: chia việc cho 2 và 4 tiến trình trên một máy 4 lõi; chưa đo thêm máy |
| Cơ sở dữ liệu quan hệ và NoSQL | Quan hệ xếp dữ liệu thành bảng hàng cột; NoSQL hợp khi cần lược đồ linh hoạt | chưa đo |
| Xử lý theo lô và theo luồng | Lô gom dữ liệu rồi xử lý một lần (thanh toán hằng ngày); luồng xử lý ngay (phát hiện gian lận) | chưa đo |
| Chuẩn hoá và phi chuẩn hoá | Chuẩn hoá tách bảng để mỗi thông tin chỉ lưu một chỗ; phi chuẩn hoá gộp bảng để truy vấn nhanh hơn | đo bằng `sqlite3` |
| Nhất quán và sẵn sàng | Nhất quán là lần nào cũng nhận dữ liệu mới nhất; sẵn sàng là hệ thống luôn chạy dù một phần hỏng | chưa đo |
| Nhất quán mạnh và nhất quán cuối cùng | Mạnh: cập nhật thấy ngay; cuối cùng: cập nhật đến các nút chậm hơn | chưa đo |
| REST và `GraphQL` | REST lấy dữ liệu qua nhiều địa chỉ; `GraphQL` lấy gọn bằng truy vấn riêng nhưng chi phí thiết kế cao hơn | đo REST ba lời gọi so với một truy vấn chọn trường (không dựng `GraphQL` thật) |
| Có trạng thái và không trạng thái | Có trạng thái nhớ tương tác cũ; không trạng thái thì không | chưa đo |
| Đọc xuyên và ghi xuyên bộ nhớ đệm | Đọc xuyên nạp từ cơ sở dữ liệu khi trượt; ghi xuyên ghi đồng thời vào bộ đệm và kho | chưa đo |
| Đồng bộ và bất đồng bộ | Đồng bộ làm việc lần lượt; bất đồng bộ chạy nền, việc mới không phải chờ việc cũ | đo bằng `asyncio` |

Cột "Ý của bài nguồn" là tóm lược các câu của nguồn, không thêm gì. Bài nguồn không đưa số liệu nào.

## Thử: bốn cặp, bốn phép đo

Ngày 2026-10-19, một máy ảo 4 lõi, Python 3.13.16, mỗi phép đo chạy ba lần.

**Chuẩn hoá và phi chuẩn hoá** (`sqlite3` trong bộ nhớ, 1.000 khách, 200.000 đơn, có chỉ mục theo mã khách):

| Điều đo | Kết quả |
|---|---|
| Đọc 200 đơn của một khách: nối hai bảng so với một bảng phẳng | 181 đến 282 micro giây so với 184 đến 251 micro giây: không khác nhau rõ |
| Đổi tên một khách | 3 đến 4 micro giây (1 hàng) so với 120 đến 176 micro giây (200 hàng) |
| Dung lượng | khách và đơn tách bảng: 2.609.152 byte; bảng phẳng: 6.754.304 byte |

**Đồng bộ và bất đồng bộ** (`asyncio`):

| Điều đo | Kết quả |
|---|---|
| 50 lần chờ 20 mili giây | lần lượt 1,010 giây; chạy đồng thời 0,022 giây |
| 20.000 việc nhỏ không chờ gì | gọi hàm trơn 0,0031 đến 0,0034 giây; làm thành việc `asyncio` 0,118 đến 0,165 giây (chậm khoảng 35 đến 50 lần) |

**Chia việc cho nhiều tiến trình, một phép tương tự của mở rộng ngang** (một việc nặng tính toán, có 0,05 giây không chia được, chia cho 1, 2, 4 tiến trình trên một máy 4 lõi): thời gian 0,42 đến 0,47 giây, 0,25 đến 0,29 giây và 0,19 đến 0,21 giây, tức nhanh hơn 1,6 đến 1,8 lần với 2 tiến trình và 2,2 đến 2,5 lần với 4.

**REST và một truy vấn chọn trường** (một máy chủ nhỏ viết bằng thư viện chuẩn, cùng dữ liệu một người dùng, các đơn và địa chỉ): ba lời gọi REST trả về tổng cộng 4.083 byte, trung vị 758 đến 814 micro giây; một truy vấn chỉ xin đúng các trường cần trả về 354 byte, trung vị 233 đến 254 micro giây.

Bốn kết quả cho bốn bài học khác nhau. Một, phi chuẩn hoá không tự nhanh hơn khi đã có chỉ mục: cái nó đổi lấy là phải sửa nhiều chỗ khi dữ liệu đổi và dung lượng gấp khoảng 2,6 lần. Hai, bất đồng bộ thắng lớn khi phải chờ và thua khi việc quá nhỏ vì mỗi việc có chi phí quản lý riêng. Ba, thêm tiến trình không cho tốc độ gấp theo số lượng: phần không chia được và việc phối hợp ăn bớt lợi ích, đúng với lời khuyên của tài liệu Microsoft rằng phối hợp giới hạn lợi ích của mở rộng ngang. Lưu ý đây là song song hoá trên một máy, một phép tương tự: mở rộng ngang thật, qua nhiều máy được cấp riêng, chưa được đo. Bốn, cái nhận được từ truy vấn chọn trường ở đây là bớt byte và bớt lời gọi, chứ chi phí thiết kế mà nguồn nhắc thì phép thử không đo được.

## Giới hạn cần nhớ

Mỗi phép đo là một kịch bản nhỏ trên một máy ảo: con số tuyệt đối thuộc về máy đó, và kết luận "không khác nhau" của phép nối hai bảng chỉ đúng cho truy vấn có chỉ mục này (một truy vấn quét cả bảng sẽ cho kết quả khác). Máy chủ REST/một-truy-vấn là đồ chơi: bản "một truy vấn" làm ít việc hơn nên khác biệt về thời gian không nói được điều gì về `GraphQL` thật. "Mở rộng ngang" ở đây là nhiều tiến trình trên một máy chứ không phải nhiều máy qua mạng. Sáu cặp còn lại không được đo, và bài không bàn lại những cặp đã có bài riêng trong nhóm khác.

## Nhìn hình trả lời

Nhóm bạn định phi chuẩn hoá bảng đơn hàng "cho truy vấn nhanh". Điều gì nên đo trước, và cái giá nào cần tính?

<details>
<summary>Xem đáp án</summary>

Đo truy vấn thật trên dữ liệu thật với chỉ mục đúng: phép thử ở đây cho thấy nối bảng có chỉ mục không chậm hơn bảng phẳng cho một khách. Nếu vẫn phi chuẩn hoá thì tính cái giá: mỗi lần đổi một thông tin chung (như tên khách) phải sửa nhiều hàng (200 so với 1 trong phép thử), dễ lệch dữ liệu nếu bỏ sót một chỗ, và dung lượng lớn hơn khoảng 2,6 lần.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và hai câu cho mỗi cặp, không có số liệu. Bài này giữ mười cặp, tóm lược từng cặp, đo bốn cặp thử được bằng một đoạn chương trình nhỏ, và ghi rõ sáu cặp chưa đo.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/10-system-design-tradeoffs-you-cannot-ignore.md): mười cặp đánh đổi.
- [Microsoft — Minimize coordination](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/design-principles/minimize-coordination-content.md): phối hợp giới hạn lợi ích của mở rộng ngang; nên chịu nhất quán cuối cùng khi dữ liệu phân tán. Đọc từ bản sao cục bộ.
- [Microsoft — Design to scale out](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/design-principles/scale-out.md): thiết kế để thêm hoặc bớt bản chạy; tránh gắn một người với một máy. Đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

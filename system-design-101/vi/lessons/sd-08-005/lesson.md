# Dịch vụ nhỏ không phải đũa thần: khi nào một khối hợp hơn

**Kiến trúc dịch vụ nhỏ sinh ra để giải một số bài toán nhất định, không phải mọi bài toán. Game thời gian thực và sàn giao dịch độ trễ thấp là hai ví dụ nơi một khối duy nhất thường hợp hơn.**
Theo bài nguồn, ba đặc điểm chung của chúng là: rất nhạy độ trễ, giữ trạng thái trong bộ nhớ, và cần cùng một kết nối luôn về đúng một máy. Bài này đo từng đặc điểm trên một máy để thấy chi phí cụ thể của việc tách dịch vụ.

![Ba khung. Khung một, ba đặc điểm khiến khối hợp hơn: rất nhạy độ trễ, giữ trạng thái trong bộ nhớ, cần định tuyến dính. Khung hai, thử đo một lời gọi: gọi hàm trong cùng tiến trình mất khoảng 0,05 đến 0,08 micro giây; socket Unix mất 26 đến 30 micro giây, TCP nội bộ 33 đến 37, HTTP 162 đến 169. Khung ba, trạng thái và định tuyến dính: cập nhật một số trong bộ nhớ mất khoảng 0,1 micro giây, trong cơ sở dữ liệu đặt trong bộ nhớ 27 đến 31 micro giây, trong cơ sở dữ liệu trên đĩa khoảng 790 đến 900 micro giây; nâng từ 4 lên 5 máy thì chia theo số dư làm 80 phần trăm người chơi phải đổi máy, còn vòng băm chỉ 20 phần trăm.](../../diagrams/sd-08-005-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách quen thuộc để một chương trình gọi một dịch vụ qua mạng; ở bài này dùng ngay trên máy để đo.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: kết nối đáng tin cậy giữa hai chương trình, nền của HTTP.

## Đọc hình

**1 · Nhạy độ trễ.** Theo bài nguồn, game thời gian thực cần độ trễ cỡ mili giây và giao dịch độ trễ thấp cỡ micro giây, nên không thể tách các dịch vụ thành các tiến trình riêng vì độ trễ mạng quá lớn. Kiến trúc dịch vụ nhỏ thêm đúng những bước nhảy qua mạng đó. Hướng dẫn kiến trúc của Microsoft cũng nêu độ trễ của chuỗi dịch vụ gọi nhau là một thách thức của kiểu kiến trúc này.

**2 · Trạng thái nằm trong bộ nhớ.** Dịch vụ nhỏ thường không giữ trạng thái và lưu mọi thứ trong cơ sở dữ liệu; còn game và sàn giao dịch giữ trạng thái trong bộ nhớ để cập nhật tức thì. Bài nguồn lấy ví dụ nhân vật bị thương mà 3 giây sau mới thấy: trải nghiệm đó có thể giết chết một trò chơi.

**3 · Kết nối dài và định tuyến dính.** Hai loại ứng dụng này nói chuyện với máy chủ rất dày, và các yêu cầu phải về đúng một máy đang chạy, nên cần kết nối WebSocket và định tuyến dính (sticky routing: yêu cầu của cùng một người luôn được chuyển tới cùng một máy).

## Thử: đo từng đặc điểm

Ngày 2026-10-19, trên một máy ảo 4 lõi, bằng một chương trình Python; mỗi phép đo chạy ba lượt và bảng ghi khoảng nhỏ nhất đến lớn nhất.

**Một lời gọi tốn bao nhiêu.**

| Cách gọi | Thời gian mỗi lần đi và về |
|---|---|
| Gọi hàm trong cùng tiến trình | 0,05 đến 0,08 µs |
| Socket Unix sang tiến trình khác | 26 đến 30 µs |
| TCP nội bộ sang tiến trình khác | 33 đến 37 µs |
| HTTP nội bộ (máy chủ viết bằng thư viện chuẩn Python) | 162 đến 169 µs |

Một lời gọi hàm rẻ hơn một bước nhảy sang tiến trình khác hàng trăm lần, và cái giá đó chưa tính mạng thật giữa hai máy. Với ngân sách cỡ mili giây của game, vài bước nhảy tính bằng chục micro giây vẫn nằm trong ngân sách; với ngân sách cỡ micro giây của giao dịch, một bước nhảy thôi đã vượt qua nó.

**Trạng thái trong bộ nhớ so với trong cơ sở dữ liệu.** Mỗi lần giảm một số máu: sửa một giá trị trong bộ nhớ mất khoảng 0,1 µs. Cập nhật cùng một số bằng mô-đun `sqlite3` của Python, mỗi cập nhật tự xác nhận ngay, mất 27 đến 31 µs khi tệp cơ sở dữ liệu nằm trong bộ nhớ và 790 đến 900 µs khi nằm trên đĩa của máy thử (chạy 200 lần cập nhật, vì mỗi lần phải ghi xuống đĩa). Trạng thái giữ trong bộ nhớ rẻ hơn hàng nghìn lần so với ghi mỗi thay đổi xuống đĩa.

**Định tuyến dính và việc mở rộng.** Giả sử 100.000 người chơi, mỗi người được chuyển tới máy theo số dư của giá trị băm tên người chơi chia cho số máy. Khi tăng từ 4 lên 5 máy, **80,1%** người chơi bị chuyển sang máy khác, tức trạng thái trong bộ nhớ của họ phải di chuyển theo hoặc bị mất. Dùng vòng băm (consistent hashing, mỗi máy giữ 200 điểm trên vòng) thì chỉ khoảng **20,3%** người chơi đổi máy. Hệ thống có trạng thái trong bộ nhớ vì thế không mở rộng dễ như dịch vụ không trạng thái.

## Giới hạn cần nhớ

Các phép đo chỉ minh họa hướng của chi phí chứ không phải bảng giá: chạy bằng Python (phần chậm của HTTP chủ yếu là mã Python, không phải đường truyền), trên một máy ảo, chưa có mạng thật giữa hai máy. Con số 0,05 đến 0,08 µs của lời gọi hàm là cả chi phí của vòng lặp đo. Phép thử định tuyến dính dùng một băm đơn giản trên tên giả, không mô phỏng một hệ thống game thật. Đừng đọc bài này thành "dịch vụ nhỏ là xấu": Microsoft nêu cả lợi ích (nhóm nhỏ làm việc độc lập, mở rộng từng phần) lẫn thách thức (độ phức tạp, độ trễ, nhất quán dữ liệu giữa các dịch vụ); ý của bài nguồn là phải hỏi "vì sao" trước khi chọn kiến trúc.

## Nhìn hình trả lời

Một trò chơi bắn súng nhiều người cập nhật vị trí người chơi 60 lần mỗi giây. Đội đề xuất tách thành hai dịch vụ: dịch vụ vị trí và dịch vụ sát thương, gọi nhau qua HTTP, và lưu mọi trạng thái trong cơ sở dữ liệu. Dựa vào ba đặc điểm trong hình, nêu hai điểm cần lo.

<details>
<summary>Xem đáp án</summary>

Một, độ trễ: mỗi tick cách nhau chừng 16,7 ms, và mỗi lần gọi HTTP giữa hai dịch vụ là một bước nhảy tốn từ chục đến vài trăm micro giây trong phép thử (chưa kể mạng thật), cộng lại qua nhiều lần gọi mỗi tick. Hai, trạng thái: lưu mỗi thay đổi vào cơ sở dữ liệu trên đĩa tốn cỡ nghìn micro giây một lần trong phép thử, so với một phần mười micro giây trong bộ nhớ, và người chơi phải thấy cập nhật tức thì. Thêm một điểm: nếu giữ trạng thái trong bộ nhớ thì cần định tuyến dính, và đổi số máy làm nhiều người chơi phải đổi máy.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn nêu ba đặc điểm của game thời gian thực và giao dịch độ trễ thấp, mỗi đặc điểm một đoạn. Bài này giữ ba đặc điểm đó nhưng đo từng cái, và đối chiếu độ trễ giữa các dịch vụ với hướng dẫn kiến trúc của Microsoft. Các con số về mili giây và micro giây của game và sàn giao dịch, và ví dụ nhân vật bị thương trễ 3 giây, là của bài nguồn, chưa kiểm chứng độc lập.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/is-microservice-architecture-the-silver-bullet.md): ba đặc điểm của game thời gian thực và giao dịch độ trễ thấp.
- [Microsoft — kiểu kiến trúc dịch vụ nhỏ](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/architecture-styles/microservices.md): thách thức về độ phức tạp, độ trễ và nhất quán dữ liệu. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-19. Phép đo là của người biên soạn, trên một máy ảo.
Bài viết và hình được thiết kế độc lập.

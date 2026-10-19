# Chín việc làm khi phát triển dịch vụ nhỏ: việc nào có chỗ đối chiếu

**Bài nguồn kể ra chín việc nên làm khi phát triển dịch vụ nhỏ, mỗi việc chỉ có một dòng tiêu đề. Bài này đặt từng việc cạnh các tài liệu độc lập để xem việc nào có chỗ đối chiếu, việc nào chưa, rồi đo giá của một việc dễ đo: giữ dịch vụ không có trạng thái.**

![Bốn khung. Khung một, cách chia việc: dữ liệu riêng cho mỗi dịch vụ, mỗi dịch vụ một trách nhiệm, thiết kế theo miền nghiệp vụ. Khung hai, cách xây và chạy: bản xây riêng, đóng gói container, dịch vụ không giữ trạng thái. Khung ba, cách ghép: giao diện người dùng chia nhỏ, điều phối các dịch vụ, giữ mã ở cùng mức trưởng thành. Khung bốn, thử với ba bản chạy và phân phát lượt vòng tròn: giữ phiên trong bộ nhớ thì chỉ 20 phần trăm lượt có phiên hợp lệ, còn giữ ở kho chung thì 100 phần trăm, đổi lại mỗi lượt chậm thêm khoảng 65 đến 150 micro giây.](../../diagrams/sd-08-007-main.svg)

## Từ viết tắt

- **DDD** (Domain-Driven Design) — thiết kế hướng miền: cách chia hệ thống theo các miền nghiệp vụ, mỗi miền có mô hình riêng.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách quen thuộc để một chương trình gọi một dịch vụ qua mạng; ở bài này dùng ngay trên máy để đo.

## Đọc hình

Chín việc của bài nguồn, xếp thành ba nhóm. Dưới đây là chỗ đối chiếu của từng việc; "có chỗ đối chiếu" nghĩa là một trong hai tài liệu độc lập đã đọc (hướng dẫn kiến trúc dịch vụ nhỏ của Microsoft và bộ mười hai nguyên tắc ứng dụng đám mây của Heroku) nói điều tương ứng.

| Việc theo bài nguồn | Chỗ đối chiếu |
|---|---|
| Dữ liệu riêng cho mỗi dịch vụ | Microsoft: dữ liệu là riêng của dịch vụ sở hữu nó |
| Mỗi dịch vụ một trách nhiệm | Microsoft: gắn kết chức năng cao, thay đổi cùng nhau thì ở cùng nhau |
| Thiết kế theo miền nghiệp vụ (DDD) | Microsoft: dùng DDD để tìm ranh giới dịch vụ |
| Mỗi dịch vụ một bản xây riêng | Heroku: mỗi ứng dụng một kho mã, tách bước xây, phát hành, chạy; Microsoft: triển khai độc lập |
| Dịch vụ không giữ trạng thái | Heroku: tiến trình không giữ trạng thái, không dùng phiên dính |
| Chạy trong container | Microsoft nhắc nền tảng điều phối lên lịch và triển khai dịch vụ; chưa thấy câu đòi container |
| Điều phối các dịch vụ | Cùng chỗ trên; không rõ bài nguồn nói điều phối chạy hay điều phối quy trình (bài về điều phối và tự phối hợp) |
| Chia nhỏ giao diện người dùng | Chưa đối chiếu: các trang đã đọc chỉ nói về lớp phục vụ riêng cho từng loại máy khách |
| Giữ mã ở cùng mức trưởng thành | Chưa đối chiếu |

Ba việc cuối nghiêng về lời khuyên của bài nguồn hơn là điều hai tài liệu kia nói; nên đọc chúng như ý kiến, không như điều đã được xác nhận.

## Thử: giữ phiên trong bộ nhớ hay ở kho chung

Ngày 2026-10-19, trên một máy ảo 4 lõi: ba bản chạy của cùng một dịch vụ web viết bằng thư viện chuẩn của Python, một kho Redis 7.0.15, và 301 người dùng. Mỗi người đăng nhập một lần rồi gửi thêm năm yêu cầu; các yêu cầu được phân cho ba bản theo vòng tròn (không có phiên dính). Hai kiểu dịch vụ: giữ phiên trong bộ nhớ của từng bản, hoặc ghi phiên vào Redis (kho chung). Đo ba lượt.

| Kiểu | Yêu cầu có phiên hợp lệ | Thời gian một yêu cầu (trung vị) | Một bản biến mất, người dùng không còn phiên |
|---|---|---|---|
| Phiên trong bộ nhớ từng bản | 301 trên 1.505 (20,0%) | 238 đến 330 µs | 200 trên 301 |
| Phiên ở kho chung | 1.505 trên 1.505 (100%) | 344 đến 396 µs | 0 trên 301 |

Số 20% không ngẫu nhiên: với 301 người và vòng tròn ba bản, mỗi người rơi đúng vào bản đã nhớ phiên của mình trong một trên năm vòng. Kết luận: khi có nhiều bản chạy mà không có phiên dính, dịch vụ giữ phiên trong bộ nhớ gần như luôn hỏng, và mất một bản làm mất phiên của người đang ở bản đó. Giữ ở kho chung chữa được cả hai, nhưng mỗi yêu cầu thêm một lượt gọi kho: trung vị tăng khoảng 65 đến 150 µs trong ba lượt đo.

## Giới hạn cần nhớ

Đây chỉ là một phép thử nhỏ trên một máy, về đúng một trong chín việc: các việc còn lại (dữ liệu riêng, xây riêng, container, giao diện chia nhỏ...) không đo được bằng phép thử như vậy. Máy chủ web trong phép thử là loại đơn giản và kho chung nằm ngay trên máy, nên giá "thêm một lượt gọi kho" thật ở mạng thật sẽ lớn hơn. Bảng đối chiếu chỉ cho biết hai tài liệu đã đọc nói gì; hai tài liệu đó không phải bộ chín việc, và việc không có chỗ đối chiếu không có nghĩa là sai. Cũng không có nghĩa là mọi việc đều đáng làm ở mọi hệ thống: Microsoft cảnh báo cả về dịch vụ quá nhỏ làm tăng độ phức tạp.

## Nhìn hình trả lời

Một đội có ba bản chạy của dịch vụ đặt hàng, giữ giỏ hàng trong bộ nhớ của từng bản, và cân bằng tải theo vòng tròn. Khách phàn nàn giỏ hàng "lúc có lúc không". Việc nào trong chín việc liên quan, và có hai hướng sửa nào?

<details>
<summary>Xem đáp án</summary>

Việc "dịch vụ không giữ trạng thái". Hai hướng: đưa giỏ hàng ra kho chung (như Redis trong phép thử; đổi lại mỗi yêu cầu chậm thêm một chút) hoặc bắt cân bằng tải gửi cùng một khách tới cùng một bản (phiên dính; bộ nguyên tắc của Heroku coi cách này là vi phạm tinh thần không giữ trạng thái, và mất bản đó thì mất giỏ).

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn chỉ liệt kê chín tiêu đề. Bài này giữ đủ chín, xếp thành ba nhóm, nói rõ việc nào có chỗ đối chiếu ở hai tài liệu độc lập, và đo một việc bằng một phép thử có thể chạy lại. Ba việc chưa có chỗ đối chiếu được nêu thẳng là chưa đối chiếu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/9-best-practices-for-developing-microservices.md): chín việc.
- [Microsoft — kiểu kiến trúc dịch vụ nhỏ](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/guide/architecture-styles/microservices.md): mục thực hành tốt nhất. Đọc từ bản clone của kho.
- [Heroku — Twelve-Factor App, mục Processes](https://github.com/heroku/12factor/blob/1385d2c80bac38c25647651f6f5ec769561828dc/content/en/processes.md): tiến trình không giữ trạng thái, không dùng phiên dính. Đọc từ bản clone của kho.
- [Heroku — Twelve-Factor App, mục Build, release, run](https://github.com/heroku/12factor/blob/1385d2c80bac38c25647651f6f5ec769561828dc/content/en/build-release-run.md): tách ba bước xây, phát hành, chạy. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-19. Phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

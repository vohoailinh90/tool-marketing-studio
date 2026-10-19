# Điều phối hay tự phối hợp: các dịch vụ làm việc với nhau thế nào

**Một đơn hàng đi qua nhiều dịch vụ (trả tiền, giữ hàng, giao hàng, gửi thư), và có hai cách để chúng làm việc theo đúng thứ tự: một bộ điều phối cầm lái và ra lệnh từng bước, hoặc không ai cầm lái mà mỗi dịch vụ tự làm phần mình khi nghe một sự kiện.**
Bài này vẽ cùng một đơn hàng theo cả hai cách, rồi dùng một mô phỏng nhỏ để đếm: hỏng giữa chừng thì tốn bao nhiêu thông điệp, và thêm một bước thì phải sửa những gì.

![Ba khung. Khung một, điều phối: bộ điều phối ra lệnh trả tiền cho dịch vụ thanh toán và nhận kết quả, ra lệnh giữ hàng cho kho; kho báo thất bại thì bộ điều phối ra lệnh hoàn tiền cho thanh toán. Khung hai, tự phối hợp: dịch vụ thanh toán đăng sự kiện đã trả tiền lên kênh sự kiện, kho nhận sự kiện đó; kho đăng sự kiện giữ hàng thất bại, thanh toán nhận sự kiện này và tự hoàn tiền. Khung ba, thử mô phỏng chuỗi bốn bước: hỏng ở bước ba thì tự phối hợp tốn 6 thông điệp và điều phối tốn 10; thêm một bước kiểm tra gian lận thì tự phối hợp phải sửa 2 dịch vụ cũ, điều phối sửa 0 dịch vụ cũ.](../../diagrams/sd-08-002-main.svg)

## Đọc hình

**1 · Điều phối (orchestration).** Một thành phần trung tâm, gọi là bộ điều phối, biết cả quy trình: nó ra lệnh cho từng dịch vụ, nhận kết quả, ghi nhớ đơn hàng đang ở bước nào, và khi một bước thất bại thì chính nó ra lệnh hoàn tác các bước đã làm (trong hình: kho báo hết hàng, bộ điều phối bảo thanh toán hoàn tiền). Mỗi dịch vụ chỉ biết việc của mình, không biết quy trình lớn.

**2 · Tự phối hợp (choreography).** Không có thành phần nào cầm lái. Mỗi dịch vụ, khi làm xong phần mình, đăng một sự kiện lên một kênh chung (thường là một hệ thống chuyển thông điệp); dịch vụ nào quan tâm sự kiện đó thì nghe và làm phần của nó. Thất bại cũng là một sự kiện: trong hình, kho đăng "giữ hàng thất bại", và dịch vụ thanh toán nghe thấy nên tự hoàn tiền.

## Thử: đếm trên một chuỗi bốn bước

Ngày 2026-10-19, một chương trình mô phỏng nhỏ (không có mạng, không có hệ thống chuyển thông điệp thật) dựng một chuỗi bốn bước, trả tiền, giữ hàng, giao hàng, gửi thư, mỗi bước có một việc hoàn tác. Cách đếm: điều phối tính một lệnh và một phản hồi cho mỗi bước (kể cả mỗi lần hoàn tác); tự phối hợp tính một sự kiện cho mỗi bước, một sự kiện khởi đầu và một sự kiện báo cho mỗi lần hoàn tác (kể cả lần cuối, dù không ai nghe nó), không tính phản hồi nhận.

| Hỏng ở bước | Tự phối hợp (thông điệp) | Điều phối (thông điệp) |
|---|---|---|
| Không hỏng | 5 | 8 |
| Bước 1, trả tiền | 2 | 2 |
| Bước 2, giữ hàng | 4 | 6 |
| Bước 3, giao hàng | 6 | 10 |
| Bước 4, gửi thư | 8 | 14 |

Cả hai cách đều hoàn tác đủ các bước đã làm và để lại 0 bước dở dang, tức kết quả đúng như nhau; chỉ khác cách đi. Sự chênh lệch trong bảng phần lớn do quy tắc đếm (điều phối đếm cả phản hồi), nên đừng đọc nó là chênh lệch độ trễ: hệ thống chuyển thông điệp thật còn thêm bước trung gian của riêng nó.

Phép thứ hai: thêm một bước kiểm tra gian lận ngay sau trả tiền. Trong mô phỏng, mỗi dịch vụ tự phối hợp nghe sự kiện của bước đứng trước nó và sự kiện thất bại của bước đứng sau nó, nên bước mới làm đổi lời đăng ký nghe của đúng **hai** dịch vụ cũ: dịch vụ trả tiền (giờ phải nghe thất bại của bước mới) và dịch vụ giữ hàng (giờ phải nghe sự kiện của bước mới thay vì của trả tiền). Hai dịch vụ còn lại không phải sửa. Với điều phối, các dịch vụ cũ không đổi gì: chỉ danh sách bước trong bộ điều phối được thêm một dòng.

## Giới hạn cần nhớ

Mô phỏng là một chuỗi thẳng bốn bước đếm bằng tay, không đo hiệu năng và không có song song, lặp thông điệp hay hỏng giữa chừng của chính hệ thống chuyển thông điệp. Nhận xét "chỉ sửa hai dịch vụ" đúng cho chuỗi thẳng; với quy trình rẽ nhánh, mỗi dịch vụ nghe nhiều sự kiện hơn và chuyện sẽ phức tạp hơn.

Hướng dẫn kiến trúc của Microsoft nêu cả hai mặt. Điều phối: hợp với quy trình phức tạp hoặc hay thêm dịch vụ, tránh được vòng phụ thuộc, tách rõ trách nhiệm; nhưng cần viết thêm một thành phần điều phối, và nó là một điểm có thể hỏng làm cả quy trình dừng (khi nó hỏng hoặc quá tải, lỗi lan sang mọi dịch vụ phụ thuộc). Tự phối hợp: hợp với quy trình đơn giản ít dịch vụ, không cần thành phần nào làm trung tâm; nhưng khi thêm bước thì khó theo dõi dịch vụ nào đáp ứng lệnh nào, có nguy cơ vòng phụ thuộc, khó kiểm thử tích hợp vì phải chạy mọi dịch vụ, và vì không ai giữ trạng thái cả đơn hàng nên phải dùng truy vết phân tán và mã tương quan để biết một đơn đang ở đâu. Bộ điều phối cũng không nhất thiết làm mất việc đang dở khi nó chết: Netflix Conductor, nền tảng điều phối do Netflix tạo ra, lưu trạng thái quy trình và cho tạm dừng, chạy tiếp, chạy lại, thử lại và dừng một quy trình. Bài này không chọn cách nào tốt hơn: câu trả lời tuỳ quy trình và đội ngũ.

## Nhìn hình trả lời

Một quy trình có ba dịch vụ, nhưng đội dự định thêm sáu bước nữa trong năm tới và thứ tự các bước hay đổi. Nên chọn điều phối hay tự phối hợp, và vì sao?

<details>
<summary>Xem đáp án</summary>

Nghiêng về điều phối: quy trình sẽ phức tạp lên và hay thêm bước, mà trong thử trên mỗi bước thêm vào làm đổi lời đăng ký nghe của các dịch vụ kề nó nếu tự phối hợp, còn với điều phối thì chỉ sửa bộ điều phối. Đổi lại phải chấp nhận thêm một thành phần trung tâm và lo cho nó chạy ổn định. Nếu quy trình chỉ là vài việc độc lập chạy song song sau một sự kiện (ví dụ gửi thư và cập nhật thống kê sau khi đã trả tiền) thì tự phối hợp gọn hơn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn so hai cách bằng hình ảnh người biên đạo múa và người chỉ huy dàn nhạc, rồi nêu lợi ích và hạn chế của điều phối. Bài này giữ hai hướng đó nhưng đổi hình ảnh sang cùng một đơn hàng chạy theo hai cách, và thử đếm thay vì nhắc lại. Bài nguồn nói thêm dịch vụ vào tự phối hợp thì "mọi dịch vụ" tương tác đều phải sửa; trong chuỗi thẳng của mô phỏng chỉ các dịch vụ kề bước mới phải sửa. Bài nguồn cũng nói điều phối có độ tin cậy cao hơn vì có sẵn quản lý giao dịch và xử lý lỗi; bài này nêu cả điểm bộ điều phối có thể hỏng và cách Conductor lưu trạng thái để giảm hậu quả, theo hướng dẫn của Microsoft.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/orchestration-vs-choreography-microservices.md): hai cách phối hợp, lợi ích và hạn chế của điều phối.
- [Microsoft — mẫu Choreography](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/choreography.md): bộ điều phối là điểm nghẽn và điểm hỏng, thêm dịch vụ có thể phải nối lại đường giao tiếp; xử lý lỗi, theo dõi, mã tương quan trong tự phối hợp. Đọc từ bản clone của kho.
- [Microsoft — mẫu Saga (nội dung)](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/saga-content.md): bảng ưu và nhược điểm của hai cách trong một chuỗi giao dịch có hoàn tác. Đọc từ bản clone của kho.
- [Netflix Conductor — giới thiệu](https://github.com/Netflix/conductor/blob/548f386c2c6c1e4d467b8551edbb6182881004ae/docs/docs/gettingstarted/intro.md): lưu trạng thái quy trình; tạm dừng, chạy tiếp, chạy lại, thử lại, dừng. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-19. Mô phỏng đếm là của người biên soạn, không phải số đo hiệu năng.
Bài viết và hình được thiết kế độc lập.

# Tránh trả tiền hai lần: thử lại và khóa chống trùng

**Một trong những lỗi nghiêm trọng nhất của hệ thống thanh toán là thu tiền của khách hai lần. Vì vậy hệ thống phải đảm bảo mỗi lệnh thanh toán được thực hiện đúng một lần. Nguồn chia việc khó này thành hai việc dễ hơn: thực hiện ít nhất một lần và thực hiện nhiều nhất một lần.**

![Ba khung. Khung một, đúng một lần gồm hai phần: ít nhất một lần được đảm bảo bằng việc thử lại, nhiều nhất một lần được đảm bảo bằng khóa chống trùng. Khung hai, thử lại: máy khách trả 10 đô la, ba lần đầu thất bại vì mạng yếu, lần thứ tư thành công. Khung ba, khóa chống trùng: một giá trị duy nhất do máy khách tạo, hết hạn sau một thời gian, thường là UUID, gửi kèm ở phần đầu của yêu cầu; gọi lại cùng khóa thì cho cùng kết quả.](../../diagrams/sd-07-016-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình gọi một chương trình khác; ở đây là cách máy khách gọi máy chủ thanh toán.
- **UUID** (Universally Unique IDentifier) — mã định danh duy nhất toàn cầu: một chuỗi ngẫu nhiên đủ dài để gần như không bao giờ trùng với chuỗi khác; nguồn nói nó thường được dùng làm khóa chống trùng.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: giao thức mà máy khách web và di động dùng để gửi yêu cầu tới máy chủ; "phần đầu" (header) là phần mô tả đi kèm một yêu cầu.

## Đọc hình

**Đúng một lần = hai phần.** Về mặt toán học, một thao tác được thực hiện đúng một lần nếu nó được thực hiện *ít nhất một lần* và đồng thời *nhiều nhất một lần*. Nguồn đảm bảo vế đầu bằng thử lại (retry) và vế sau bằng kiểm tra chống trùng (idempotency check).

**Thử lại.** Đôi khi phải thử lại một giao dịch thanh toán vì lỗi mạng hoặc quá thời gian chờ. Thử lại cho đảm bảo "ít nhất một lần". Ví dụ của nguồn: máy khách trả 10 đô la, nhưng thanh toán cứ thất bại vì kết nối mạng kém. Máy khách nghĩ mạng có thể khá hơn nên gửi lại, và thanh toán thành công ở lần thử thứ tư.

**Khóa chống trùng.** Nhìn từ phía API, "idempotency" nghĩa là máy khách gọi cùng một lệnh nhiều lần mà vẫn cho cùng một kết quả. Giữa máy khách (ứng dụng web và di động) và máy chủ, khóa chống trùng (idempotency key) thường là một giá trị duy nhất do máy khách tạo ra và hết hạn sau một thời gian. UUID hay được dùng làm khóa và được nhiều công ty công nghệ, như Stripe và PayPal, khuyến nghị. Để thực hiện một yêu cầu thanh toán chống trùng, khóa được thêm vào phần đầu HTTP dưới dạng `idempotency-key: key_value`.

## Giới hạn cần nhớ

Nguồn nêu hai kỹ thuật ở mức ý tưởng và một ví dụ; nó không nói máy chủ làm gì khi gặp một khóa đã thấy (trả lại kết quả cũ, hay bỏ qua yêu cầu mới), khóa được lưu bao lâu, hay chuyện gì xảy ra khi hai yêu cầu cùng khóa tới cùng lúc. Lưu ý: thử lại cộng khóa chống trùng chỉ đạt "đúng một lần" khi máy chủ giữ chỗ khóa một cách nguyên tử (hai yêu cầu cùng khóa không cùng chạy) và lưu kết quả bền vững; và thử lại không thể bảo đảm thành công khi lỗi kéo dài mãi. Người biên soạn hiểu "cho cùng kết quả" là máy chủ nhớ kết quả của lần đầu và trả lại nó; đây là cách đọc, chưa đối chiếu với tài liệu của một nhà cung cấp.
Bài cũng không bàn việc khóa phải được tạo trước lần thử đầu tiên và giữ nguyên qua mọi lần thử lại, dù người biên soạn thấy điều đó là cần để các lần thử cùng nhận ra nhau.

## Nhìn hình trả lời

Trong ví dụ 10 đô la, máy khách thử bốn lần. Nếu cả bốn lần dùng khóa chống trùng khác nhau, điều gì có thể xảy ra, và vì sao thử lại một mình chưa đủ?

<details>
<summary>Xem đáp án</summary>

Thử lại chỉ đảm bảo "ít nhất một lần": thanh toán sẽ được gửi tới khi mạng khá hơn. Nó không ngăn một lần thử đã tới được máy chủ (dù phản hồi bị mất) rồi bị gửi lại thêm một lần nữa; lúc đó có thể thu tiền hai lần.
Nếu mỗi lần thử mang một khóa khác nhau, máy chủ không có cách nào nhận ra các lần thử là cùng một lệnh. Khóa phải giống nhau giữa các lần thử để vế "nhiều nhất một lần" có tác dụng. Đây là suy luận từ định nghĩa của nguồn; nguồn không nêu tình huống này.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một bài ngắn: lập luận "đúng một lần = ít nhất một lần + nhiều nhất một lần", một ví dụ thử lại và phần giải thích khóa chống trùng. Bài này giữ nguyên lập luận, vẽ thành ba khung, và đưa cách đọc "cùng khóa thì cùng kết quả" vào phần giới hạn như suy luận của người biên soạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-avoid-double-payment.md): đúng một lần, thử lại, khóa chống trùng và ví dụ 10 đô la. Phần giới hạn và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

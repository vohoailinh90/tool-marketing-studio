# Thanh toán bằng mã QR: bốn cách từ hai câu hỏi

**Dù dùng ví nào, quét mã QR để trả tiền cũng chỉ có bốn cách, vì chỉ cần trả lời hai câu hỏi: ai trình mã, và mã đó động hay tĩnh.**
Hai đáp án của câu thứ nhất nhân với hai đáp án của câu thứ hai ra bốn tổ hợp.

![Ba khung. Khung một, ai trình mã QR: người mua trình mã thì người bán quét và ghi nợ trực tiếp tài khoản người mua; người bán trình mã thì người mua quét và cho phép ghi có trực tiếp từ tài khoản của mình. Khung hai, mã động hay tĩnh: mã động được tạo lúc trình hoặc tự đổi sau vài giây nên chứa được số tiền, loại giao dịch; mã tĩnh tạo một lần dùng mọi nơi, thường chỉ chứa thông tin tài khoản. Khung ba, hai nhân hai ra bốn cách: người mua trình mã tĩnh, người mua trình mã động, người bán trình mã tĩnh, người bán trình mã động.](../../diagrams/sd-07-006-main.svg)

## Từ viết tắt

- **QR** (Quick Response) — phản hồi nhanh: loại mã hai chiều mà camera điện thoại đọc được; ở đây nó mang thông tin để trả tiền.

## Đọc hình

**Ai trình mã?** Nếu *bạn* trình mã và người bán quét, đó là "chế độ người mua trình mã" (consumer-presented mode): việc người bán làm là ghi nợ trực tiếp tài khoản của bạn. Nếu *người bán* trình mã để bạn quét và trả số tiền cần thanh toán, đó là "chế độ người bán trình mã" (merchant-presented mode): bạn cho phép ghi có trực tiếp từ tài khoản của mình.

**Mã động hay tĩnh?** Mã động được tạo ra ngay lúc trình, hoặc tự tạo lại sau vài giây một lần. Vì sinh động như vậy, nó có thể chứa nhiều thông tin như số tiền phải trả và loại giao dịch. Mã tĩnh chỉ tạo một lần rồi dùng ở mọi nơi, và thường chỉ chứa thông tin tài khoản.

**Bốn tổ hợp.** Người mua trình mã tĩnh; người mua trình mã động; người bán trình mã tĩnh; người bán trình mã động.

## Giới hạn cần nhớ

Bài nguồn chia cách làm, không nói cách nào tốt hơn hay an toàn hơn. Từ mô tả của nó, người biên soạn rút ra hai suy luận, chưa đối chiếu với tài liệu của một hệ thống thanh toán nào: mã tĩnh không chứa số tiền nên số tiền phải được nhập hoặc xác nhận ở một bước khác; và một mã chỉ chứa thông tin tài khoản thì in ra dán ở quầy được, còn mã tự đổi sau vài giây thì không.
Bài cũng không nói ví hay ngân hàng cụ thể nào hỗ trợ cách nào.

## Nhìn hình trả lời

Một quầy bán nước dán sẵn một tờ mã QR cố định lên kính. Khách quét tờ giấy này để trả tiền. Tờ mã đó thuộc chế độ nào, và là mã động hay tĩnh?

<details>
<summary>Xem đáp án</summary>

Người bán trình mã (khách quét), và đó là mã tĩnh: tạo một lần, dùng mãi, nên thường chỉ chứa thông tin tài khoản.
Suy ra từ định nghĩa của nguồn: mã tĩnh không mang số tiền của từng lần mua, nên số tiền phải được xác định ở bước khác. Nguồn không nói bước đó làm thế nào.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một bài ngắn với hai câu hỏi và bốn tổ hợp. Bài này giữ cả hai và đặt chúng thành hai khung không có mũi tên, vì chúng là hai lựa chọn độc lập chứ không phải hai bước nối nhau. Phần giới hạn và đáp án là của người biên soạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/4-ways-of-qr-code-payment.md): hai câu hỏi, bốn tổ hợp, định nghĩa mã động và mã tĩnh. Phần giới hạn và đáp án là suy luận của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

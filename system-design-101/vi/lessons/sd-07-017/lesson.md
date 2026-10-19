# Apple Pay và Google Pay: ai giữ thông tin thẻ

**Cả Apple Pay lẫn Google Pay đều rất an toàn, nhưng cách làm khác nhau ở một điểm: thông tin thẻ nằm ở đâu. Apple không lưu thông tin thẻ mà đưa nó cho ngân hàng, còn Google lưu thông tin thẻ trên máy chủ của mình.**
Nguồn tách quy trình thành hai luồng: đăng ký thẻ và thanh toán cơ bản.

![Năm khung. Khung một, đăng ký thẻ với Apple Pay: iPhone gửi thông tin thẻ cho ngân hàng, Apple không lưu; ngân hàng trả lại một mã DAN, iPhone lưu mã vào một chip phần cứng riêng. Khung hai, đăng ký thẻ với Google Pay: điện thoại gửi thông tin thẻ cho máy chủ Google, nơi lưu thông tin thẻ; Google trả lại một mã thanh toán. Khung ba, thanh toán với Apple Pay: khách bấm Trả, máy chủ bán hàng chuyển mã DAN cho ngân hàng. Khung bốn, thanh toán với Google Pay: máy chủ bán hàng chuyển mã thanh toán cho máy chủ Google, nơi tra thông tin thẻ rồi chuyển cho ngân hàng. Khung năm, điều cần nhớ.](../../diagrams/sd-07-017-main.svg)

## Từ viết tắt

- **DAN** (Device Account Number) — số tài khoản của thiết bị: mã thay cho số thẻ mà ngân hàng trả về cho iPhone; iPhone lưu mã này trong một chip phần cứng riêng.

## Đọc hình

**Đăng ký thẻ (bước 1 đến 3, cả hai cách).**

- *Apple Pay.* Apple không lưu thông tin thẻ nào. Thông tin thẻ được chuyển cho ngân hàng. Ngân hàng trả về cho iPhone một mã gọi là DAN, và iPhone lưu DAN vào một chip phần cứng đặc biệt.
- *Google Pay.* Khi bạn đăng ký thẻ với Google Pay, thông tin thẻ được lưu trên máy chủ của Google. Google trả về cho điện thoại một mã thanh toán (payment token).

**Thanh toán cơ bản.** Luồng này bắt đầu khi bạn bấm nút "Trả" trên điện thoại.

- *Apple Pay.* Với iPhone, máy chủ của trang bán hàng chuyển DAN cho ngân hàng.
- *Google Pay.* Máy chủ của trang bán hàng chuyển mã thanh toán cho máy chủ Google. Máy chủ Google tra ra thông tin thẻ rồi chuyển cho ngân hàng.

Trên sơ đồ gốc có một mũi tên đỏ, nghĩa là thông tin thẻ có mặt trên mạng công cộng, dù đã được mã hóa.

## Giới hạn cần nhớ

Nguồn là một bài so sánh ngắn: nó khẳng định cả hai cách đều rất an toàn nhưng không nói cách nào an toàn hơn, không giải thích DAN được dùng để xác thực thế nào, và không nói chip phần cứng bảo vệ DAN ra sao. Mũi tên đỏ được mô tả bằng chữ nhưng nguồn không nói nó nằm ở luồng nào; theo cách đọc của người biên soạn thì thông tin thẻ chỉ xuất hiện trên đường đi ở trường hợp Google Pay, khi máy chủ Google chuyển thông tin thẻ cho ngân hàng. Cách đọc này chưa đối chiếu với tài liệu của Apple hay Google.
Bài không mô tả các thao tác khác của ví điện tử (thanh toán tại cửa hàng bằng cảm ứng, xóa thẻ).

## Nhìn hình trả lời

Cửa hàng trực tuyến nhận được thứ gì khi khách trả bằng Apple Pay, và khác gì so với Google Pay? Ai tra ra được thông tin thẻ trong từng trường hợp?

<details>
<summary>Xem đáp án</summary>

Với Apple Pay, máy chủ bán hàng nhận DAN và chuyển nó cho ngân hàng; ngân hàng là nơi đã cấp DAN và tra được thẻ tương ứng. Apple không lưu thông tin thẻ nên không tra được.
Với Google Pay, máy chủ bán hàng nhận mã thanh toán và chuyển cho máy chủ Google; máy chủ Google tra ra thông tin thẻ đã lưu rồi chuyển cho ngân hàng. Việc "ngân hàng tra được thẻ từ DAN" là cách người biên soạn đọc câu "bank returns DAN"; nguồn không mô tả bước tra.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn viết hai luồng bằng các gạch đầu dòng song song, Apple Pay rồi Google Pay. Bài này vẽ mỗi cặp thành hai lược đồ để người đọc so từng bước, và gom điều khác biệt chính vào khung cuối. Ba liên kết tham khảo của nguồn không được chép lại.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-applegoogle-pay-works.md): hai luồng đăng ký thẻ và thanh toán của Apple Pay và Google Pay, DAN, mũi tên đỏ. Phần giới hạn và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

# Quét mã để trả tiền: hai quy trình, mười hai bước

**Khi bạn quét mã ở quầy để trả bằng ví điện tử, có hai quy trình nối nhau: quầy xin nhà cung cấp dịch vụ thanh toán tạo mã, rồi bạn quét mã và nhà cung cấp xác nhận đã trả.**
Hai quy trình có 7 và 5 bước.

![Hai khung, mỗi khung một lược đồ. Khung một, quầy tạo mã: máy thu ngân gửi mã đơn và số tiền cho nhà cung cấp dịch vụ thanh toán, nơi lưu lại, tạo địa chỉ mã QR và trả về để quầy hiển thị mã, trong chưa đầy một giây. Khung hai, khách quét và trả: ví điện tử báo nhà cung cấp rằng mã đã được trả, nhà cung cấp đánh dấu đã trả và trả kết quả thành công cho ví, rồi báo người bán.](../../diagrams/sd-07-010-main.svg)

## Từ viết tắt

- **PSP** (Payment Service Provider) — nhà cung cấp dịch vụ thanh toán: bên đứng giữa cửa hàng và ví điện tử, lưu đơn, tạo mã QR và ghi nhận mã đã được trả.
- **QR** (Quick Response) — phản hồi nhanh: loại mã hai chiều mà camera điện thoại đọc được.
- **URL** (Uniform Resource Locator) — định vị tài nguyên thống nhất: một dòng ký tự chỉ vị trí của một thứ trên mạng; ở đây dòng đó là nội dung mà mã QR chứa.

## Đọc hình

Nguồn dùng ví dụ trả tiền bằng ví điện tử như PayPal, Paytm hay Venmo.

**1. Quầy tạo mã (7 bước, chưa đầy một giây).** Cô thu ngân cộng tổng các món hàng, chẳng hạn 123,45 đô la, đơn có một mã đơn, rồi bấm "thanh toán". Máy thu ngân gửi mã đơn và số tiền cho PSP. PSP lưu thông tin vào cơ sở dữ liệu và tạo một địa chỉ cho mã QR (URL). Dịch vụ cổng thanh toán của PSP đọc địa chỉ đó và trả về cho máy của cửa hàng. Máy của cửa hàng gửi địa chỉ (hoặc ảnh mã) tới quầy, và quầy hiển thị mã QR.

**2. Khách quét và trả (5 bước).** Khách mở ứng dụng ví điện tử để quét mã. Sau khi xác nhận số tiền đúng, khách bấm "trả". Ứng dụng ví báo cho PSP rằng mã QR này đã được trả. Cổng thanh toán của PSP đánh dấu mã là đã trả và trả thông báo thành công về ví của khách; rồi báo cho người bán rằng khách đã trả mã đó.

Đây chính là một trường hợp "người bán trình mã, mã động" của bài về bốn cách quét mã: mỗi lần thanh toán có một mã gắn với đúng đơn và đúng số tiền. Chuyện nối hai bài này là suy luận của người biên soạn.

## Giới hạn cần nhớ

Nguồn mô tả đường đi thuận lợi. Nó không nói gì về chuyện mã hết hạn, khách quét mà không trả, mạng đứt giữa chừng, hay một mã bị trả hai lần; bài này không bổ sung những tình huống đó.
Nguồn cũng không nói tiền từ ví của khách tới tài khoản người bán đi đường nào và khi nào: nó dừng ở chỗ PSP báo người bán rằng mã đã được trả.

## Nhìn hình trả lời

Vì sao quầy phải gửi mã đơn và số tiền cho PSP *trước khi* mã QR hiện ra? Chuyện gì xảy ra với việc đối chiếu nếu quầy in sẵn một mã chung không gắn với đơn nào?

<details>
<summary>Xem đáp án</summary>

Vì mã QR được tạo từ đơn: PSP lưu mã đơn và số tiền rồi mới tạo địa chỉ mã, nên khi khách trả, PSP biết mã này ứng với đơn nào và bao nhiêu tiền, và đánh dấu đúng đơn đó là đã trả.
Nếu in sẵn một mã chung không gắn đơn nào thì khi có tiền vào, PSP không có đơn nào để đánh dấu; đó là suy luận của người biên soạn từ trình tự của nguồn, không phải điều nguồn nói.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có hai danh sách bước (7 và 5). Bài này vẽ chúng thành hai lược đồ và đưa các bước chỉ xảy ra ở quầy (cộng tiền, bấm thanh toán, chuyển địa chỉ tới quầy) vào phần chữ. Chi tiết mã đơn mẫu của nguồn không được in lại.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-scan-to-pay-work.md): hai quy trình, bảy bước tạo mã và năm bước trả tiền. Việc nối với bài bốn cách quét mã và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

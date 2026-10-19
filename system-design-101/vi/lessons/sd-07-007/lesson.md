# Tài khoản nóng: khi mọi giao dịch cùng đổ vào một số dư

**Một "tài khoản nóng" là tài khoản có rất nhiều thao tác diễn ra cùng lúc. Khi mọi đơn đều phải sửa chung một số dư và mỗi lần sửa phải khóa dòng, cả hệ thống xếp hàng chờ ở đúng chỗ đó.**
Ba cách gỡ dưới đây giảm chờ đợi bằng ba cách khác nhau, và mỗi cách đều phải trả một giá.

![Hai khung. Khung một, vấn đề: ngày khuyến mãi lớn, hàng loạt đơn cùng ghi vào số dư của một người bán; mỗi lần cập nhật phải khóa dòng, nên thông lượng thấp và thành điểm nghẽn. Khung hai, ba cách gỡ: giới hạn tốc độ, từ chối hoặc hẹn lại các yêu cầu thừa nhưng trải nghiệm kém; chia số dư thành nhiều tài khoản con để mỗi cập nhật chỉ khóa một tài khoản con; cập nhật số dư trên bộ nhớ đệm trước, ghi chi tiết xuống cơ sở dữ liệu sau một cách bất đồng bộ.](../../diagrams/sd-07-007-main.svg)

## Đọc hình

**Vì sao nghẽn.** Giả sử một người bán chạy khuyến mãi vào ngày giảm giá lớn. Hàng loạt đơn mua đổ về cùng lúc, và mỗi đơn thanh toán xong lại cộng tiền vào *một* dòng: số dư của người bán trong cơ sở dữ liệu.
Bình thường, khi số dư được cập nhật, hệ thống khóa dòng đó (row lock) để hai lệnh không ghi đè lên nhau. Khóa này an toàn nhưng làm thông lượng thấp: lệnh nào cũng phải đợi lệnh trước, nên dòng số dư trở thành nút thắt cổ chai.

**Cách 1: giới hạn tốc độ.** Chỉ nhận một số yêu cầu nhất định trong một khoảng thời gian; phần còn lại bị từ chối hoặc hẹn thử lại sau. Cách này đơn giản và giúp một số người dùng nhận phản hồi nhanh hơn, nhưng trải nghiệm của người bị từ chối có thể tệ.

**Cách 2: chia số dư thành các tài khoản con.** Người bán có nhiều tài khoản con; mỗi yêu cầu cập nhật chỉ khóa một tài khoản con, các tài khoản còn lại vẫn rảnh để nhận lệnh khác.

**Cách 3: cập nhật số dư trên bộ nhớ đệm trước.** Số dư được cập nhật ở một lớp bộ nhớ đệm trước; bảng sao kê chi tiết và số dư trong cơ sở dữ liệu được cập nhật sau, một cách bất đồng bộ. Bộ nhớ đệm trong bộ nhớ chịu được thông lượng cao hơn nhiều so với cơ sở dữ liệu.

## Giới hạn cần nhớ

Nguồn chỉ nêu cái giá của cách thứ nhất. Hai cách còn lại cũng có giá, và đó là hiểu biết chung của người biên soạn, chưa đối chiếu với tài liệu của một hệ thống nào:
đọc tổng số dư khi có nhiều tài khoản con phải cộng các phần lại, và một tài khoản con có thể hết tiền trong khi các tài khoản con khác còn;
còn nếu bộ nhớ đệm hỏng trước khi bản ghi xuống cơ sở dữ liệu thì cập nhật chưa kịp ghi có thể mất, nên cách này cần thêm biện pháp bảo vệ mà bài không bàn tới.
Nguồn cũng không nói hệ thống thật chọn cách nào hay kết hợp chúng ra sao.

## Nhìn hình trả lời

Nếu số dư của người bán nằm ở một dòng duy nhất, vì sao thêm máy chủ để xử lý đơn không làm hệ thống nhanh hơn? Cách chia tài khoản con giải quyết đúng chỗ nghẽn đó bằng cách nào?

<details>
<summary>Xem đáp án</summary>

Vì mọi lệnh đều phải khóa cùng một dòng: thêm máy chủ chỉ thêm người xếp hàng trước cùng một cánh cửa. Chia thành các tài khoản con tạo ra nhiều cánh cửa: mỗi yêu cầu chỉ khóa một tài khoản con, nên nhiều yêu cầu chạy song song được.
Đây là suy luận từ mô tả của nguồn về khóa dòng, không phải số đo.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn nêu vấn đề và ba cách tối ưu. Bài này giữ cả ba, dựng ba bước dẫn tới nút thắt, và thêm phần cái giá của từng cách. Phần cái giá và đáp án là của người biên soạn.
Bài nguồn gọi tên vài công ty lớn làm ví dụ; bài này không nhắc tên họ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/handling-hotspot-accounts.md): định nghĩa tài khoản nóng, khóa dòng, ba cách tối ưu. Cái giá của hai cách sau và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

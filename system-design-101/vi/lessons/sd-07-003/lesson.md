# Lệnh cắt lỗ: giá kích hoạt không phải giá bán

**Lệnh cắt lỗ đặt một mức giá; khi giá thị trường chạm mức đó, hệ thống tự biến nó thành lệnh bán theo giá thị trường. Mức giá bạn đặt là chỗ lệnh được đánh thức, không phải giá bạn chắc chắn bán được.**

![Một lược đồ ba bên: nhà đầu tư, hệ thống giao dịch, sàn giao dịch. Nhà đầu tư đặt lệnh cắt lỗ bán 100 cổ phiếu với giá kích hoạt 36. Hệ thống giao dịch theo dõi giá thị trường từ sàn. Khi giá rơi xuống 35, hệ thống gửi lệnh thị trường bán 100 cổ phiếu ở giá tốt nhất lúc đó. Sàn báo khớp lệnh ở 35,5 mỗi cổ phiếu và hệ thống báo lại cho nhà đầu tư.](../../diagrams/sd-07-003-main.svg)

## Đọc hình

Ví dụ của nguồn: một nhà đầu tư có 100 cổ phiếu của một công ty, giá hiện tại 40 đô la mỗi cổ phiếu. Họ muốn bán nếu giá xuống tới hoặc dưới 36 đô la, để giới hạn khoản lỗ.

1. Nhà đầu tư gửi cho hệ thống giao dịch lệnh cắt lỗ: bán 100 cổ phiếu, giá kích hoạt 36.
2. Hệ thống giao dịch (trading engine) nhận lệnh và tạo lệnh cắt lỗ.
3. Nó đăng ký nhận dữ liệu thị trường của công ty đó từ sàn giao dịch và theo dõi giá theo thời gian thực.
4. Giá rơi xuống, chẳng hạn 35. Hệ thống lập tức tạo một *lệnh thị trường* (bán ngay ở giá tốt nhất đang có) và gửi lên sàn để bán 100 cổ phiếu.
5. Lệnh được khớp, tức là ghép với các lệnh mua tốt nhất trên thị trường, thường là gần như ngay lập tức. Hệ thống nhận từ sàn một *báo cáo khớp lệnh* cho biết 100 cổ phiếu đã bán, chẳng hạn ở giá 35,5 mỗi cổ phiếu.
6. Hệ thống báo cho nhà đầu tư: 100 cổ phiếu đã bán ở 35,5 mỗi cổ phiếu.

Để ý bước 4: lệnh gửi lên sàn là lệnh thị trường, không còn gắn với con số 36. Vì vậy giá bán thực tế (35,5) khác cả mức đã đặt (36) lẫn mức giá thấy lúc kích hoạt (35).

## Giới hạn cần nhớ

Lệnh cắt lỗ giới hạn *thời điểm* bán, không giới hạn *giá* bán. Ở ví dụ, 100 cổ phiếu bán được 3.550 đô la thay vì 3.600 đô la nếu bán đúng ở 36: kém 50 đô la. Mức chênh này đến từ chính các số của nguồn, nhưng nguồn không nêu nó.
Nếu giá giảm rất nhanh, giá khớp có thể còn thấp hơn nữa. Đó là suy luận từ cách lệnh thị trường hoạt động, không phải số liệu nào trong nguồn. Người biên soạn biết còn các loại lệnh khác dùng để giới hạn giá khi bán; bài không mô tả chúng và chưa đối chiếu với tài liệu của một sàn cụ thể.

## Nhìn hình trả lời

Giá cổ phiếu mở cửa thấp hơn 36 ngay từ đầu phiên, ở 33. Theo cách lệnh trong hình hoạt động, lệnh cắt lỗ có bán ở 36 không? Giả sử khớp ở 33 thì nhà đầu tư nhận bao nhiêu?

<details>
<summary>Xem đáp án</summary>

Không. 36 chỉ là mức kích hoạt; khi giá đã ở 33 thì hệ thống thấy điều kiện đã thỏa và gửi lệnh thị trường, bán ở giá tốt nhất đang có. Nếu khớp ở 33 thì 100 cổ phiếu cho 3.300 đô la, kém 300 đô la so với bán ở 36.
Đây là suy luận từ ví dụ của nguồn (nó chỉ cho trường hợp rơi xuống 35 và khớp ở 35,5), không phải số liệu đo.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn mô tả các bước của hệ thống giao dịch. Bài này vẽ chúng thành lược đồ giữa ba bên và nhấn vào chỗ người mới hay hiểu nhầm: mức giá đặt là điều kiện đánh thức lệnh, không phải giá bán. Các phép tính 3.550 và 3.600 đô la, và trường hợp mở cửa ở 33, là của người biên soạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-a-stop-loss-order-and-how-does-it-work.md): định nghĩa lệnh cắt lỗ, ví dụ số và sáu bước thực thi. Các phép tính chênh lệch và nhận xét về giá giảm nhanh là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

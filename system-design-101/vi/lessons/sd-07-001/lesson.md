# Mua hàng trực tuyến: bốn mảng việc sau một đơn hàng

**Sau một lần bấm "đặt hàng" là bốn mảng việc nối nhau: mua hàng từ nhà cung cấp, giữ hàng trong kho, bán hàng trên nền tảng, rồi vận chuyển tới người mua.**
Biết hàng đi theo thứ tự đó, bạn biết mỗi hệ thống phụ trách việc gì và chúng chạm nhau ở đâu.

![Hai khung. Khung một, bốn mảng việc nối nhau: mua hàng từ nhà cung cấp, kho giữ hàng, nền tảng bán hàng, vận chuyển. Khung hai, đường đi của một đơn trên nền tảng bán hàng: người mua đăng nhập, chọn hàng bỏ vào giỏ, đặt đơn, hệ thống giữ hàng trong kho rồi mới thanh toán.](../../diagrams/sd-07-001-main.svg)

## Đọc hình

Bài nguồn gồm 16 bước đánh số; bài này gom chúng theo bốn mảng.

**Mua hàng (bước 1 và 2).** Bộ phận mua hàng chọn nhà cung cấp và quản lý hợp đồng với họ. Sau đó đặt hàng, xử lý việc trả hàng và thanh toán hóa đơn cho nhà cung cấp.

**Kho (bước 3).** Hàng từ nhà cung cấp được giao tới nơi lưu trữ. Mọi hàng hóa ở đó do hệ thống quản lý tồn kho theo dõi.

**Nền tảng bán hàng (bước 4 đến 13).** Có hai nửa. Nửa đầu là phía người bán:
hệ thống quản lý sản phẩm tạo thông tin sản phẩm, hệ thống định giá đặt giá, rồi sản phẩm sẵn sàng đưa lên bán.
Hệ thống khuyến mãi thì định ra các đợt giảm giá lớn, phiếu giảm giá và những thứ tương tự. Nửa sau là phía người mua (bước 8 đến 11): đăng ký hoặc đăng nhập, xem danh sách và chi tiết sản phẩm, bỏ vào giỏ, rồi đặt đơn.
Ở bước 12 và 13, hệ thống quản lý đơn hàng giữ chỗ số hàng đó trong hệ thống tồn kho, và sau đó người mua mới thanh toán.

**Vận chuyển (bước 14 đến 16).** Hệ thống tồn kho gửi lệnh xuất kho sang hệ thống vận chuyển, nơi quản lý việc giao hàng thật. Bước cuối, ký nhận hàng, là tùy chọn.

Điểm đáng chú ý là thứ tự ở bước 12 và 13: hàng được *giữ chỗ trước*, tiền trả *sau*. Thứ tự này giúp tránh cảnh hai người cùng trả tiền cho món hàng chỉ còn một cái, nhưng chỉ với hai điều kiện: việc giữ chỗ phải là một thao tác trọn vẹn (kiểm tra còn hàng và trừ hàng diễn ra một lần, không yêu cầu nào chen vào giữa), và chỗ giữ phải còn hiệu lực cho tới khi thanh toán xong. Nếu hai yêu cầu cùng thấy món cuối còn trống rồi cùng giữ, hoặc chỗ giữ hết hạn khi người mua đang trả tiền, thì vẫn có thể bán trùng.

## Giới hạn cần nhớ

Tác giả bài nguồn tự nói mình hiểu biết hạn chế về thương mại điện tử: sơ đồ dựa trên nghiên cứu cá nhân, và ông nhờ người đọc góp ý về tên thành phần hay chỉ ra chỗ sai. Vì vậy hãy coi đây là một bản đồ chung, không phải mô tả kiến trúc của một công ty cụ thể nào. Công ty thật có thể thêm, bớt hay đổi thứ tự các hệ thống.
Ý "giữ chỗ trước giúp tránh bán trùng món hàng cuối cùng", cùng hai điều kiện đi kèm, là suy luận của người biên soạn từ thứ tự giữ chỗ trước, trả tiền sau; nguồn không nói điều đó.

## Nhìn hình trả lời

Một người mua nhiều món, nên đơn lớn có thể bị tách thành nhiều đơn nhỏ theo kho hoặc loại hàng. Hệ thống "tách đơn" nên nằm ở đâu trên đường đi trong hình?

<details>
<summary>Xem đáp án</summary>

Một chỗ hợp lý là ngay sau khi đơn được đặt và trước khi hàng được giữ chỗ hoặc xuất kho: việc tách phụ thuộc vào món nào đang nằm ở kho nào, nên cần biết tồn kho trước. Sau khi tách, mỗi đơn nhỏ giữ chỗ riêng ở kho của nó và trở thành một lệnh xuất kho riêng gửi sang vận chuyển.
Đây là suy luận của người biên soạn; nguồn đặt câu hỏi nhưng không đưa đáp án, và còn nhiều chuyện để bàn thêm, chẳng hạn người mua trả một lần cho cả đơn lớn hay trả riêng từng đơn nhỏ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê 16 bước theo số thứ tự, kèm một sơ đồ lớn. Bài này không vẽ lại sơ đồ đó: nó gom bước theo bốn mảng việc, rồi vẽ riêng đường đi của người mua trên nền tảng để thấy bước giữ hàng đứng trước bước thanh toán.
Bài chưa đối chiếu với tài liệu của một nền tảng thương mại điện tử cụ thể.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/e-commerce-workflow.md): bốn mảng việc, 16 bước và câu hỏi tách đơn. Lời giải thích về thứ tự giữ hàng rồi mới trả tiền, và đáp án tách đơn, là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

# Làm mờ biển số và khuôn mặt trên ảnh đường phố: ba đường ống

**Muốn ảnh đường phố không lộ biển số hay khuôn mặt, đừng làm mờ lúc người dùng xem: hãy làm một lần, ngoại tuyến, rồi chỉ phát ảnh đã mờ.**
Việc đó chia thành ba đường ống: dạy máy nhận ra vật nhạy cảm, áp dụng máy đó lên ảnh để làm mờ, và phục vụ ảnh đã mờ cho người xem.

![Ba khung. Khung một, ba đường ống nối nhau: đường ống dữ liệu chuẩn bị dữ liệu huấn luyện và huấn luyện mô hình, đường ống làm mờ tìm vật nhạy cảm trong ảnh rồi làm mờ, đường ống phục vụ trả ảnh đã mờ cho người xem. Khung hai, bốn bước của đường ống làm mờ: tiền xử lý ảnh, tìm khung bao quanh vật nhạy cảm, làm mờ vùng trong khung, lưu ảnh đã mờ vào kho đối tượng. Khung ba, hai kiểu lỗi: bỏ sót thì lộ, làm mờ nhầm thì mất chi tiết.](../../diagrams/sd-12-004-main.svg)

## Từ viết tắt

- **ML** (Machine Learning) — học máy: cách để máy tự rút ra quy luật từ các ví dụ đã gán nhãn, thay vì ai đó viết từng quy tắc; ở đây nó dùng để nhận ra biển số và khuôn mặt.

## Đọc hình

**Đường ống dữ liệu (Data pipeline).** Người ta dùng một bộ ảnh đã được gán nhãn: mỗi biển số hay khuôn mặt được khoanh bằng một khung chữ nhật. Ảnh được chuẩn hóa về cùng cỡ và làm phong phú thêm bằng các biến đổi nhẹ như lật hoặc đổi độ sáng, rồi dùng để huấn luyện một mô hình ML. Bài nguồn dùng mạng hai giai đoạn: giai đoạn đầu đề xuất những vùng có thể chứa vật cần tìm, giai đoạn sau kết luận vùng nào đúng và khoanh khung chính xác hơn.

**Đường ống làm mờ (Blurring pipeline).** Ảnh đường phố mới đi qua bốn việc: tiền xử lý, tìm khung quanh vật nhạy cảm, làm mờ vùng trong khung, lưu ảnh đã mờ vào kho đối tượng.

**Đường ống phục vụ (Serving pipeline).** Người dùng chỉ lấy ảnh từ kho ảnh đã mờ. Vì ảnh mờ sẵn nên lúc xem không tốn thêm việc tính toán nào, và người dùng không có đường nào tới ảnh gốc.

Hai kiểu lỗi của bộ phát hiện không đáng giá như nhau. Bỏ sót một biển số là lộ thông tin riêng tư; làm mờ nhầm một biển hiệu cửa hàng chỉ làm ảnh kém đẹp. Vì vậy người ta thường chỉnh ngưỡng của mô hình để thà mờ thừa còn hơn sót.

## Giới hạn cần nhớ

Bài nguồn tự nói đây là một giải pháp *có thể dùng trong buổi phỏng vấn*, không phải mô tả cách Google hay Apple làm thật, dù tiêu đề nhắc tên hai hãng. Bài này giữ cùng giới hạn: nó là bản thiết kế hợp lý, không phải báo cáo về hệ thống của một công ty. Hai điều dưới đây là suy luận của người biên soạn, chưa đối chiếu với tài liệu của hãng nào: ngưỡng nên nghiêng về làm mờ thừa, và ảnh gốc, nếu còn được giữ, phải nằm ở nơi người xem không tới được.
Bài nguồn cũng không nói chuyện người dùng yêu cầu làm mờ thêm một ngôi nhà hay một chiếc xe; đó là tính năng thật của một số dịch vụ nhưng bài này không mô tả.

## Nhìn hình trả lời

Mô hình khoanh một vùng và cho điểm tin cậy 40% rằng đó là biển số. Nên làm mờ hay để nguyên, và vì sao?

<details>
<summary>Xem đáp án</summary>

Nên làm mờ nếu hệ thống chấp nhận mờ thừa: giá của mờ nhầm là một vật không nhạy cảm bị nhòe, còn giá của bỏ sót là lộ biển số thật. Một cách làm hợp lý là đặt ngưỡng thấp cho các lớp nhạy cảm, rồi lấy mẫu những vùng điểm thấp cho người kiểm tra để đo tỷ lệ mờ nhầm.
Đây là suy luận của người biên soạn từ hai kiểu lỗi trong hình; con số 40% chỉ là ví dụ, nguồn không đưa ngưỡng nào.

</details>

<details>
<summary>Xem sâu hơn: điều đã bổ sung so với bài nguồn</summary>

Bài nguồn liệt kê 11 bước đánh số chia vào ba đường ống: bước 1 đến 6 chuẩn bị dữ liệu và huấn luyện, bước 7 đến 10 làm mờ và lưu, bước 11 phục vụ. Bài này giữ ba đường ống nhưng không đánh lại số bước; nó thêm vào lý do làm mờ ngoại tuyến và hai kiểu lỗi.
Một bài báo công bố năm 2009 của các tác giả Google (Frome và cộng sự, "Large-scale privacy protection in Google Street View") có mô tả việc phát hiện và làm mờ khuôn mặt, biển số ở quy mô lớn; bài này chưa đọc được bài báo nên không trích kết quả nào của nó.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-googleapple-maps-blur-license-plates-and-human-faces-on-street-view.md): ba đường ống và 11 bước. Lý do làm mờ ngoại tuyến và hai kiểu lỗi là của người biên soạn.
- Ren, He, Girshick, Sun, "Faster R-CNN" (2015), arXiv 1506.01497: ví dụ nổi tiếng của mạng phát hiện vật thể hai giai đoạn (nhớ lại; chưa mở lại trang trong phiên này).

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

# Tám chiến lược mở rộng: mỗi cách gỡ một nút thắt khác nhau

**Tám chiến lược mở rộng không phải tám bước làm lần lượt: mỗi chiến lược gỡ một nút thắt riêng và đòi một cái giá riêng.**
Biết mỗi cách giải bài toán gì và đổi lại mất gì, bạn chọn đúng cách theo chỗ hệ thống đang nghẽn, không theo danh sách.

![Hai khung, mỗi khung bốn ghi chú. Khung một, tầng ứng dụng: dịch vụ không giữ trạng thái, mở rộng theo chiều ngang, cân bằng tải, tự động co giãn. Khung hai, dữ liệu và công việc: bộ nhớ đệm, sao chép cơ sở dữ liệu, chia nhỏ cơ sở dữ liệu, xử lý bất đồng bộ. Mỗi ghi chú nói nó gỡ nút thắt nào.](../../diagrams/sd-11-002-main.svg)

## Đọc hình

Tên tám mục giữ nguyên theo bài nguồn. Phần giải thích dưới đây là của người biên soạn: mỗi mục nói rõ nó gỡ gì và cái giá của nó.

**Stateless Services (dịch vụ không giữ trạng thái).** Gỡ: một bản sao của dịch vụ không còn là bản duy nhất biết thông tin của người dùng, nên yêu cầu nào tới bản nào cũng được. Giá: trạng thái phải nằm ở nơi chung (cơ sở dữ liệu, bộ nhớ đệm), và mỗi yêu cầu phải đọc nó từ đó.

**Horizontal Scaling (mở rộng theo chiều ngang).** Gỡ: một máy không đủ sức. Thêm máy thay vì thay bằng máy to hơn. Giá: việc và dữ liệu phải được chia giữa các máy, và các máy nói chuyện với nhau qua mạng.

**Load Balancing (cân bằng tải).** Gỡ: có nhiều bản sao nhưng yêu cầu dồn vào một bản. Giá: chính bộ cân bằng thành điểm cần dự phòng, và nó phải biết bản sao nào còn sống.

**Auto Scaling (tự động co giãn).** Gỡ: tải lên xuống theo giờ, giữ số máy cố định thì hoặc thiếu hoặc phí. Giá: máy mới cần thời gian khởi động, nên hệ thống luôn phản ứng chậm hơn tải một nhịp; ngưỡng đặt sai thì co giãn sai.

**Caching (bộ nhớ đệm).** Gỡ: cùng một dữ liệu được đọc đi đọc lại từ nơi chậm. Giá: dữ liệu trong bộ nhớ đệm có thể cũ, và phải quyết định khi nào bỏ nó.

**Database Replication (sao chép cơ sở dữ liệu).** Gỡ: quá nhiều lượt đọc dồn vào một cơ sở dữ liệu, và muốn có bản dự phòng khi nó hỏng. Giá: bản sao có thể chậm hơn bản gốc nên đọc ra dữ liệu cũ; sao chép không làm việc *ghi* nhanh hơn, vì mọi lần ghi vẫn phải đi qua nơi nhận ghi.

**Database Sharding (chia nhỏ cơ sở dữ liệu).** Gỡ: dữ liệu hoặc lượt ghi lớn hơn sức một máy. Mỗi mảnh giữ một phần dữ liệu. Giá: truy vấn trải qua nhiều mảnh phức tạp hơn, chọn khóa chia khó, và chia lại khi đổi số mảnh tốn công.

**Async Processing (xử lý bất đồng bộ).** Gỡ: một việc nặng làm người dùng chờ lâu. Đẩy việc vào hàng đợi rồi trả lời trước. Giá: kết quả không có ngay, và phải tính tới việc làm lại khi lỗi.

## Giới hạn cần nhớ

Thứ tự tám mục là thứ tự của bài nguồn, không phải thứ tự phải áp dụng. Nhiều hệ thống bắt đầu từ chỗ đo được là chậm nhất, không từ mục số 1. Phần "gỡ gì, giá gì" là tổng hợp từ kiến thức chung của người biên soạn về các kỹ thuật này; bài không đối chiếu từng mục với một tài liệu chính thức nào trong phiên viết.

## Nhìn hình trả lời

Một trang chủ chậm. Số đo cho thấy cơ sở dữ liệu bận gần hết sức vì cùng vài truy vấn đọc lặp lại cả nghìn lần mỗi phút; lượt ghi thì ít. Bạn thử chiến lược nào trước, và vì sao chưa chọn chia nhỏ?

<details>
<summary>Xem đáp án</summary>

Thử bộ nhớ đệm trước: nó rẻ nhất cho đúng nút thắt này, vì cùng dữ liệu được đọc lặp lại. Sao chép cơ sở dữ liệu là bước tiếp nếu lượt đọc vẫn quá nhiều. Chưa chia nhỏ vì nút thắt không nằm ở lượt ghi hay dung lượng, trong khi chia nhỏ đổi lại truy vấn phức tạp hơn và khó đảo ngược. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là danh sách tám mục. Bài này giữ tên và thứ tự, nhưng viết lại mỗi mục theo cặp "gỡ gì, giá gì" và chia thành hai nửa: tầng ứng dụng và tầng dữ liệu cùng công việc, để thấy chiến lược nào đụng tới phần nào của hệ thống.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/8-must-know-scalability-strategies.md): chỉ lấy tên và thứ tự tám mục. Lời giải thích về nút thắt và cái giá là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức.

# Làm mờ biển số và khuôn mặt trong ảnh đường phố

**Ảnh đường phố vô tình chụp được mặt người và biển số xe.** Trước khi đưa lên bản đồ, hệ thống phải tìm các vùng đó và làm mờ chúng trên rất nhiều ảnh.

![Bảy thẻ dọc: ảnh có gắn khung mặt và biển số; tiền xử lý và tăng cường; huấn luyện bộ phát hiện; ảnh đường phố mới vào và chạy bộ phát hiện; làm mờ các vùng nhạy cảm; lưu vào kho ảnh; người dùng chỉ lấy ảnh đã làm mờ. Chú thích: bước 1 đến 3 chuẩn bị mô hình, bước 4 đến 6 chạy cho từng ảnh mới.](../../diagrams/sd-12-004-main.svg)

## Đọc hình

**Đường dữ liệu (1–3).** Người đánh dấu mặt và biển số bằng khung chữ nhật trên ảnh mẫu. Ảnh được chuẩn hóa, tạo thêm biến thể (xoay nhẹ, đổi độ sáng) rồi dùng để huấn luyện bộ phát hiện vật thể.

**Đường làm mờ (4–6).** Ảnh mới đi qua cùng bước tiền xử lý, bộ phát hiện trả về các khung, chỉ vùng trong khung bị làm mờ, rồi ảnh được lưu vào kho.

**Đường phục vụ (7).** Người dùng chỉ được lấy ảnh đã xử lý, không chạm tới ảnh chưa làm mờ.

## Giới hạn cần nhớ

Bộ phát hiện sẽ có lỗi. Bỏ sót nghĩa là lộ thông tin riêng tư; phát hiện nhầm chỉ làm mờ thừa. Vì cái giá không đối xứng, hệ thống thường ưu tiên bắt đủ hơn là chính xác tuyệt đối, và cần kênh để người dùng báo vùng bị sót. Bài chỉ là một thiết kế khả dĩ, không mô tả hệ thống thật của Google hay Apple.

## Nhìn hình trả lời

Một khuôn mặt bị bộ phát hiện bỏ sót. Lỗi này nặng hơn hay nhẹ hơn việc làm mờ nhầm một biển hiệu cửa hàng?

<details>
<summary>Xem đáp án</summary>

Nặng hơn: khuôn mặt thật hiện ra công khai. Làm mờ nhầm chỉ giảm chất lượng ảnh. Vì vậy có thể chấp nhận thêm vài lần mờ thừa để giảm bỏ sót.

</details>

<details>
<summary>Xem sâu hơn: hai giai đoạn, ngưỡng và ảnh gốc</summary>

- **Hai giai đoạn:** giai đoạn một đề xuất các vùng có thể chứa vật thể, giai đoạn hai phân loại và tinh chỉnh khung. Bộ phát hiện một giai đoạn làm cả hai trong một lượt, thường nhanh hơn. Chọn loại nào là đánh đổi giữa độ chính xác và chi phí xử lý.
- **Ngưỡng tin cậy:** hạ ngưỡng thì bắt thêm vùng nhưng làm mờ thừa nhiều hơn.
- **Ảnh gốc:** nếu giữ ảnh chưa làm mờ để huấn luyện lại, phải kiểm soát truy cập và thời hạn lưu. Làm mờ xong không có nghĩa dữ liệu nhạy cảm đã biến mất khỏi hệ thống.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-googleapple-maps-blur-license-plates-and-human-faces-on-street-view.md): ba đường ống: dữ liệu, làm mờ, phục vụ.
- [Ren và cộng sự — Faster R-CNN](https://arxiv.org/abs/1506.01497): bộ phát hiện hai giai đoạn.
- [Redmon và cộng sự — YOLO](https://arxiv.org/abs/1506.02640): bộ phát hiện một giai đoạn.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-004.json).

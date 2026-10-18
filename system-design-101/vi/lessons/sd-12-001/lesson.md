# AirTag tìm đồ thất lạc bằng cách nào?

**Một chiếc AirTag không có GPS và không có SIM.** Nó chỉ phát tín hiệu Bluetooth ngắn; việc báo vị trí là do những thiết bị Apple đi ngang qua làm hộ.

![Năm thẻ dọc: AirTag phát tín hiệu Bluetooth kèm khóa công khai đổi theo thời gian; thiết bị Apple ở gần nhận tín hiệu; thiết bị đó mã hóa vị trí của chính nó bằng khóa công khai rồi gửi lên máy chủ Apple; máy chủ giữ bản mã mà không có khóa để mở; chủ AirTag giải mã bằng khóa riêng trên thiết bị của mình và xem nơi AirTag được thấy gần nhất.](../../diagrams/sd-12-001-main.svg)

## Từ viết tắt

- **GPS** (Global Positioning System) — hệ thống định vị toàn cầu bằng vệ tinh; AirTag không có GPS, nên không tự biết vị trí của mình.
- **SIM** (Subscriber Identity Module) — thẻ SIM: chip nhận diện thuê bao để thiết bị dùng mạng di động; AirTag không có SIM, nên không tự báo vị trí qua mạng di động.
- **UWB** (Ultra WideBand) — băng siêu rộng: công nghệ vô tuyến dò khoảng cách chính xác trên một số iPhone; bài nhắc nó như phần nằm ngoài hình.

## Đọc hình

**1. AirTag phát tín hiệu.** Nó phát Bluetooth Low Energy định kỳ. Nội dung mang một khóa công khai thay đổi theo thời gian, nên người ngoài khó nhận ra cùng một chiếc AirTag qua nhiều lần.

**2–3. Thiết bị gần đó làm người đưa tin.** iPhone, iPad hoặc Mac trong mạng Find My nghe thấy tín hiệu, lấy vị trí hiện tại **của chính nó**, mã hóa vị trí đó bằng khóa công khai nhận được rồi gửi lên máy chủ Apple.

**4–5. Chỉ chủ mở được.** Máy chủ chỉ giữ dữ liệu đã mã hóa. Khóa riêng tương ứng nằm trên các thiết bị của chủ; ứng dụng Find My tải bản mã, giải mã và vẽ nơi AirTag được thấy gần nhất.

## Giới hạn cần nhớ

Điểm trên bản đồ là nơi một thiết bị khác **đã thấy** AirTag, không phải theo dõi liên tục. Ở nơi ít người dùng Apple đi qua, vị trí cập nhật thưa hoặc cũ. Vì AirTag cũng có thể bị bỏ lén vào đồ của người khác, hệ thống có cơ chế cảnh báo người đang mang theo một AirTag lạ.

## Nhìn hình trả lời

AirTag nằm trong một kho hàng vắng suốt nhiều ngày, không có thiết bị Apple nào đi qua. Bản đồ cho biết điều gì?

<details>
<summary>Xem đáp án</summary>

Chỉ hiện lần cuối có thiết bị thấy nó, có thể đã cũ. AirTag không tự biết mình ở đâu; mạng Find My chỉ biết vị trí khi có thiết bị nhận được tín hiệu.

</details>

<details>
<summary>Xem sâu hơn: vì sao máy chủ không đọc được vị trí?</summary>

Hai ý chính là **khóa đổi theo thời gian** và **mã hóa bằng khóa công khai**. Khóa xoay vòng khiến người đứng quan sát tín hiệu khó ghép các lần thấy thành lịch sử của một chiếc AirTag. Mã hóa bằng khóa công khai nghĩa là chỉ nơi giữ khóa riêng, tức thiết bị của chủ, mới giải mã được. Máy chủ chuyển dữ liệu nhưng không có chìa để mở.

Đây là mô tả ở mức khái niệm. Chu kỳ đổi khóa, cách gom báo cáo và việc dò khoảng cách chính xác bằng băng siêu rộng (UWB) trên một số iPhone không nằm trong hình.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-airtags-work.md): AirTag, Bluetooth và mạng Find My ở mức tổng quan.
- [Apple — Find My network accessory program](https://developer.apple.com/find-my/): mô tả mạng Find My và phụ kiện.
- [Apple — Platform Security](https://support.apple.com/guide/security/welcome/web): phần bảo mật của Find My: khóa, mã hóa báo cáo vị trí.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-001.json).

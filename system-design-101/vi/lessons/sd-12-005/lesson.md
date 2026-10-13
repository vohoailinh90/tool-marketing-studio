# Quadtree: chia bản đồ để tìm nơi gần bạn

**Muốn tìm quán cà phê gần bạn, đừng đo khoảng cách tới mọi quán.** Chia bản đồ thành các ô, rồi chỉ nhìn vào ô của bạn và vài ô kề bên.

![Một hình vuông là bản đồ, chia làm bốn phần. Phần phía trên bên phải đông địa điểm nên được chia tiếp, và ô nhỏ chứa vị trí của bạn được tô vàng. Các phần thưa chỉ có ô lớn. Bên dưới là ba thẻ: ô nào còn quá nhiều địa điểm thì chia thành bốn, tìm bằng cách đi từ gốc xuống ô lá chứa bạn, thiếu kết quả thì lấy thêm từ ô kề. Chú thích: quadtree nằm trong bộ nhớ máy chủ, không phải cơ sở dữ liệu.](../../diagrams/sd-12-005-main.svg)

## Đọc hình

Bản đồ được chia đệ quy thành **4 ô**. Ô nào còn quá nhiều địa điểm (ví dụ hơn một ngưỡng như 100) thì chia tiếp thành 4 ô nhỏ hơn; ô nào đủ ít thì dừng và thành **ô lá**. Nơi đông, như trung tâm thành phố, sinh ra ô nhỏ và sâu; nơi thưa, như biển, chỉ có ô lớn.

**Tìm gần bạn:** đi từ gốc xuống, mỗi bước chọn ô chứa vị trí của bạn, cho tới ô lá. Nếu ô lá chưa đủ số kết quả cần, lấy thêm địa điểm từ các ô kề.

## Giới hạn cần nhớ

Quadtree là cấu trúc **trong bộ nhớ**: mỗi máy chủ dịch vụ vị trí tự dựng và giữ một bản, nó không phải nơi lưu trữ dữ liệu. Dựng cây từ dữ liệu lớn tốn thời gian và trong lúc đó máy chủ chưa nên nhận lưu lượng, nên khi phát hành phiên bản mới hãy triển khai cuốn chiếu từng nhóm máy chủ thay vì đồng loạt.

## Nhìn hình trả lời

Tìm quán gần bạn ở trung tâm thành phố và ở giữa đại dương: nơi nào thường đi sâu hơn trong cây?

<details>
<summary>Xem đáp án</summary>

Trung tâm thành phố, vì nhiều địa điểm khiến ô bị chia nhỏ nhiều lần. Giữa đại dương gần như chỉ có ô lớn.

</details>

<details>
<summary>Xem sâu hơn: ô kề, geohash và cập nhật</summary>

- **Ô kề:** điểm gần nhất có thể nằm ở ô bên cạnh dù chỉ cách một đoạn ngắn. Muốn danh sách gần nhất chính xác, phải xét cả các ô kề rồi xếp theo khoảng cách thật.
- **Quadtree và geohash:** cả hai chia vùng thành 4 theo từng mức. Geohash dùng lưới cố định nên dễ lưu và tìm trong cơ sở dữ liệu; quadtree chia thích nghi theo mật độ nhưng cần dựng trong bộ nhớ.
- **Cập nhật:** thêm hoặc xóa địa điểm có thể sửa cây tại chỗ hoặc dựng lại định kỳ; đó là đánh đổi giữa độ mới và độ phức tạp.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/quadtree.md): quadtree cho dịch vụ dựa trên vị trí; ngưỡng ví dụ và việc triển khai cuốn chiếu.
- [Wikipedia — Quadtree](https://en.wikipedia.org/wiki/Quadtree): định nghĩa và các biến thể.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-005.json).

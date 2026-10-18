# Thiết kế dịch vụ bản đồ kiểu Google Maps

**Bản đồ trên điện thoại là ba dịch vụ ghép lại:** biết bạn đang ở đâu, vẽ khu vực bạn đang xem, và chỉ đường từ A tới B.

![Sáu thẻ dọc: dịch vụ vị trí nhận vị trí gửi lên định kỳ để cập nhật giao thông và đường; hiển thị bản đồ bằng các ô dựng sẵn theo mức phóng, phát qua CDN; dẫn đường gồm bốn bước tuần tự: đổi địa chỉ thành tọa độ, tìm vài tuyến ứng viên, ước tính thời gian theo giao thông, xếp hạng tuyến. Chú thích: ba dịch vụ độc lập, dẫn đường gọi nhiều bước tuần tự.](../../diagrams/sd-12-012-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy chủ đặt ở nhiều nơi, lưu bản sao nội dung và phát cho người dùng từ máy gần họ; trong bài, các ô bản đồ dựng sẵn là tệp tĩnh ít đổi nên rất hợp để phát qua CDN.

## Đọc hình

**Dịch vụ vị trí.** Máy khách gửi vị trí lên định kỳ. Dữ liệu này giúp phát hiện đường mới hoặc đã đóng, cải thiện độ chính xác của bản đồ và làm đầu vào cho giao thông.

**Hiển thị bản đồ.** Bản đồ thế giới được chia thành các **ô** (tile) dựng sẵn cho từng mức phóng. Theo quy ước ô phổ biến trên web, ở mức phóng z có 4^z ô; phóng thêm một mức thì mỗi ô tách thành 4. Ô là tệp tĩnh ít đổi nên phát qua CDN rất hợp; máy khách chỉ tải những ô đang nằm trong khung nhìn.

**Dẫn đường.** Dịch vụ đổi địa chỉ thành tọa độ (geocoding), tìm vài tuyến ứng viên, ước tính thời gian của từng tuyến theo giao thông hiện tại và lịch sử, rồi xếp hạng theo thời gian và tùy chọn của người dùng, như tránh trạm thu phí.

## Giới hạn cần nhớ

Thời gian đến nơi là **ước tính**, không phải lời hứa: giao thông đổi theo từng phút, và dữ liệu thời gian thực chỉ đáng tin ở đoạn đường có đủ vị trí gửi về. Vị trí người dùng là dữ liệu cá nhân nhạy cảm, cần gộp, ẩn danh hoặc giới hạn thời gian lưu.

## Nhìn hình trả lời

Người dùng phóng to một khu phố. Máy khách nên vẽ lại từ dữ liệu gốc hay tải ô đã dựng sẵn cho mức phóng đó? Vì sao?

<details>
<summary>Xem đáp án</summary>

Tải ô dựng sẵn. Ô là tệp tĩnh, ít thay đổi nên CDN phát được; vẽ lại từ dữ liệu gốc cho mỗi lượt phóng sẽ chậm và tốn máy chủ.

</details>

<details>
<summary>Xem sâu hơn: ô raster, ô vector và đồ thị đường</summary>

- **Raster và vector:** ô raster là ảnh nhỏ; ô vector chứa hình học và nhãn để máy khách tự vẽ, cho phép xoay và đổi kiểu nhưng đòi máy khách vẽ.
- **Đồ thị đường:** đường là cạnh, giao lộ là đỉnh, trọng số là thời gian đi. Thuật toán đường đi ngắn nhất như Dijkstra hoặc A* tìm tuyến; ở quy mô lớn người ta chia đồ thị thành nhiều cấp để tìm nhanh hơn.
- **Cập nhật bản đồ:** đường mới hay đường đóng làm ô cũ lỗi thời, nên cần dựng lại các ô bị ảnh hưởng và làm mới bộ nhớ đệm.

Bài không dùng số liệu quy mô của Google Maps.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/design-google-maps.md): ba dịch vụ: vị trí, hiển thị bản đồ và dẫn đường.
- [OpenStreetMap — Slippy map tilenames](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames): quy ước ô theo mức phóng.
- [Wikipedia — Dijkstra](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm): tìm đường đi ngắn nhất.
- [Wikipedia — Contraction hierarchies](https://en.wikipedia.org/wiki/Contraction_hierarchies): kỹ thuật tăng tốc tìm đường trên đồ thị đường.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-012.json).

# Dịch vụ tìm địa điểm lân cận

**“Quán ăn nào quanh đây?” là câu hỏi về khoảng cách, nhưng không thể đo khoảng cách tới mọi quán.** Giải pháp là đặt mỗi địa điểm vào một ô lưới, để việc tìm kiếm quy về so khớp tiền tố của mã ô.

![Hình vuông là bản đồ thế giới, chia bốn phần mang mã 01, 11, 00, 10. Phần 01 được tô vàng và chia tiếp thành bốn ô 0101, 0111, 0100, 0110, tất cả bắt đầu bằng tiền tố 01. Bên dưới là hai thẻ: dịch vụ doanh nghiệp quản lý thông tin địa điểm; dịch vụ dựa trên vị trí trả về địa điểm gần theo bán kính bằng cách tra tiền tố của mã ô. Chú thích: điểm gần nhau có thể rơi vào hai ô có tiền tố khác nhau.](../../diagrams/sd-12-017-main.svg)

## Đọc hình

**Hai dịch vụ.** **Dịch vụ doanh nghiệp** thêm, sửa, xóa và hiển thị thông tin địa điểm. **Dịch vụ dựa trên vị trí** (LBS) nhận một tọa độ cùng bán kính rồi trả về các địa điểm gần đó.

**Vì sao không tra thẳng theo tọa độ?** Lưu vĩ độ và kinh độ rồi tính khoảng cách tới từng quán thì chậm khi dữ liệu lớn. **Geohash** biến tọa độ thành một mã: chia thế giới đôi theo kinh độ (0 nếu nhỏ hơn 0, 1 nếu lớn hơn), rồi đôi theo vĩ độ, rồi lại theo kinh độ… và ghép các bit xen kẽ. Mã càng dài thì ô càng nhỏ, và các ô lồng nhau chia sẻ tiền tố. Hình dùng hai bit đầu rồi hai bit tiếp theo; tìm mọi địa điểm trong ô `01` quy về `WHERE geohash LIKE '01%'`.

## Giới hạn cần nhớ

Hai điểm rất gần nhau có thể nằm ở hai ô khác tiền tố khi sát đường biên, nên chỉ tra một ô thì bỏ sót; cần tra cả các ô kề. Mật độ cũng không đều: một ô ở trung tâm thành phố chứa rất nhiều quán còn một ô giữa biển thì trống, nên lưới cố định không phải lúc nào cũng cân bằng. Bài chỉ nêu hai bit đầu; mã thật dài hơn và thường dùng bảng chữ cái 32 ký tự.

## Nhìn hình trả lời

Hai quán cách nhau vài chục mét nhưng nằm hai bên một đường biên ô. Tra theo tiền tố của ô chứa bạn có thấy cả hai không?

<details>
<summary>Xem đáp án</summary>

Có thể không: quán ở ô bên kia có tiền tố khác. Vì vậy truy vấn nên bao gồm cả các ô kề, rồi mới lọc theo khoảng cách thật.

</details>

<details>
<summary>Xem sâu hơn: lọc theo khoảng cách thật, S2 và quadtree</summary>

- **Lọc lần hai:** ô chỉ là bộ lọc thô; sau khi lấy các ứng viên, tính khoảng cách thật và giữ những điểm trong bán kính.
- **Độ dài mã:** chọn độ dài tiền tố theo bán kính tìm kiếm để ô vừa cỡ; ô quá to trả về quá nhiều ứng viên, quá nhỏ phải tra quá nhiều ô.
- **Cách khác:** [quadtree](../sd-12-005/lesson.md) chia thích nghi theo mật độ nhưng nằm trong bộ nhớ; thư viện S2 chia mặt cầu thành ô theo một đường cong lấp đầy không gian; cơ sở dữ liệu có chỉ mục không gian cũng giải bài toán này.
- **Dịch vụ doanh nghiệp** thiên về đọc nhiều hơn ghi, nên dễ cache và nhân bản.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/proximity-service.md): hai dịch vụ và việc dùng geohash để tìm địa điểm lân cận.
- [Wikipedia — Geohash](https://en.wikipedia.org/wiki/Geohash): cách mã hóa và hạn chế ở đường biên ô.
- [S2 Geometry](https://s2geometry.io/): một cách chia mặt cầu thành ô.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-017.json).

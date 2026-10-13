# Thiết kế soạn thảo cộng tác kiểu Google Docs

**Hai người cùng sửa một tài liệu cùng lúc, và cả hai phải thấy kết quả giống nhau.** Đó là bài toán khó nhất của trình soạn thảo cộng tác: gộp các thao tác chạy song song mà không làm mất ý của ai.

![Một ví dụ năm thẻ: văn bản gốc CAT; Alice chèn S ở vị trí 3 và thấy CATS; Bob đồng thời xóa C ở vị trí 0 và thấy AT; thao tác chèn của Alice được biến đổi thành chèn S ở vị trí 2 vì C đã bị xóa; mọi máy cùng thấy ATS. Chú thích: hệ thống gửi thao tác, không gửi cả tài liệu.](../../diagrams/sd-12-009-main.svg)

## Đọc hình

**Luồng chung.** Máy khách gửi **thao tác** (chèn, xóa kèm vị trí) qua WebSocket; máy chủ xếp thao tác vào hàng đợi, một dịch vụ xử lý sắp thứ tự và biến đổi chúng bằng thuật toán cộng tác, rồi lưu ba loại dữ liệu: thông tin tệp, nội dung và nhật ký thao tác. Thao tác đã xử lý được phát tới các máy còn lại.

**Ví dụ trong hình.** Văn bản là `CAT`. Alice chèn `S` ở vị trí 3; cùng lúc Bob xóa `C` ở vị trí 0. Nếu máy Bob áp nguyên thao tác của Alice lên `AT` thì vị trí 3 đã vượt chỗ. Thao tác được **biến đổi**: vì có một ký tự phía trước bị xóa, vị trí chèn lùi còn 2, và cả hai máy cùng ra `ATS`.

## Giới hạn cần nhớ

Hình chỉ cho một cặp thao tác. Với OT, mọi cặp loại thao tác đều cần quy tắc biến đổi đúng, nên rất khó viết và khó kiểm chứng; thường còn cần một thứ tự thống nhất do máy chủ quyết định. CRDT tránh được bước biến đổi nhưng thường phải mang thêm thông tin định danh cho từng ký tự hoặc từng đoạn, nên tốn bộ nhớ hơn, mức độ tùy cách cài đặt.

## Nhìn hình trả lời

Nếu Bob áp thẳng thao tác “chèn S ở vị trí 3” của Alice lên văn bản `AT` mà không biến đổi, điều gì xảy ra?

<details>
<summary>Xem đáp án</summary>

Vị trí 3 vượt quá độ dài của `AT`, nên kết quả sai hoặc gây lỗi. Hai máy có thể thấy văn bản khác nhau, đúng điều hệ thống phải tránh.

</details>

<details>
<summary>Xem sâu hơn: OT, CRDT, đồng bộ vi sai và nhật ký thao tác</summary>

- **OT (operational transformation):** biến đổi thao tác đến sau theo các thao tác đã áp trước để mọi bản sao hội tụ. Được dùng trong nhiều trình soạn thảo cộng tác.
- **CRDT:** thiết kế kiểu dữ liệu sao cho các thao tác gộp theo mọi thứ tự đều cho cùng kết quả; hợp với trường hợp làm việc ngoại tuyến.
- **Đồng bộ vi sai (differential synchronization):** so sánh bản sao với bản chung rồi gửi phần khác biệt.
- **Nhật ký thao tác:** lưu cả chuỗi thao tác cho phép khôi phục lịch sử; thường cần thêm ảnh chụp (snapshot) định kỳ để mở tài liệu nhanh mà không phát lại từ đầu.

Bài không khẳng định cách làm nội bộ của Google Docs.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-design-google-docs.md): luồng WebSocket, hàng đợi thao tác và các thuật toán giải quyết xung đột.
- [Wikipedia — Operational transformation](https://en.wikipedia.org/wiki/Operational_transformation): khái niệm OT và ví dụ biến đổi.
- [Shapiro và cộng sự — CRDT (HAL)](https://inria.hal.science/inria-00555588): kiểu dữ liệu sao chép không xung đột.
- [Neil Fraser — Differential Synchronization](https://neil.fraser.name/writing/sync/): đồng bộ vi sai.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-009.json).

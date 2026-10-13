# Công cụ tìm kiếm hoạt động thế nào?

**Công cụ tìm kiếm không đi tìm trên web khi bạn gõ.** Nó đã duyệt và sắp xếp sẵn các trang từ trước, nên khi có truy vấn chỉ cần tra trong một danh mục đã lập.

![Bảy thẻ dọc chia ba giai đoạn: bò web bắt đầu từ danh sách trang hạt giống; tải trang và lấy các liên kết mới để xếp hàng; phân tích trang và lập chỉ mục từ trang ra tài liệu; khi có truy vấn thì phân tích ý định; truy xuất các trang khớp từ chỉ mục; xếp hạng; trả kết quả. Chú thích: trang được bò chưa chắc được lập chỉ mục, trang được lập chỉ mục chưa chắc được xếp cao.](../../diagrams/sd-12-018-main.svg)

## Đọc hình

**1. Bò web (crawl).** Các chương trình “bò” bắt đầu từ danh sách trang đã biết (hạt giống), tải trang, đọc các liên kết trong đó rồi xếp những địa chỉ mới vào hàng đợi để tải tiếp. Chúng tôn trọng quy tắc của trang như tệp `robots.txt` và không tải dồn dập vào một máy chủ.

**2. Lập chỉ mục (index).** Nội dung được phân tích: tách từ, nhận biết ngôn ngữ, loại nội dung, độ mới, rồi đưa vào **chỉ mục đảo** (inverted index): với mỗi từ, danh sách các trang có từ đó. Ví dụ: “cá” → trang 1, trang 2; “mèo” → trang 1.

**3. Phục vụ truy vấn.** Truy vấn được phân tích (từ khóa, từ đồng nghĩa, ý định), các trang khớp được lấy ra từ chỉ mục, rồi **xếp hạng** theo mức liên quan và nhiều tín hiệu khác.

## Giới hạn cần nhớ

Ba trạng thái khác nhau: một trang được **bò** chưa chắc được **lập chỉ mục**, và trang được lập chỉ mục chưa chắc được xếp cao. Chặn bò bằng `robots.txt` cũng không đồng nghĩa trang sẽ không xuất hiện trong kết quả; muốn loại khỏi kết quả cần cách khác như chỉ thị noindex. Cách xếp hạng cụ thể của từng công cụ không công khai đầy đủ.

## Nhìn hình trả lời

Một trang vừa đăng hôm nay nhưng chưa xuất hiện khi tìm. Đã chắc là trang bị loại bỏ chưa? Có thể đang kẹt ở bước nào?

<details>
<summary>Xem đáp án</summary>

Chưa chắc. Trang có thể chưa được bò tới, đã bò nhưng chưa lập chỉ mục, hoặc đã có trong chỉ mục nhưng xếp rất thấp với truy vấn đó. Cần xác định bước nào trước khi kết luận.

</details>

<details>
<summary>Xem sâu hơn: chỉ mục đảo và xếp hạng</summary>

- **Chỉ mục đảo** lật quan hệ “trang chứa từ” thành “từ nằm trong những trang nào”, nên tra một từ không phải duyệt hết mọi trang. Với truy vấn nhiều từ, danh sách của từng từ được giao hoặc hợp lại.
- **Phân tích truy vấn:** chuẩn hóa chữ, sửa lỗi gõ, mở rộng từ đồng nghĩa, đoán ý định (tìm thông tin, tìm một trang, mua hàng).
- **Xếp hạng** kết hợp nhiều tín hiệu như mức khớp nội dung, chất lượng và độ tin cậy của nguồn, độ mới, ngôn ngữ và vị trí người hỏi. Mỗi công cụ có công thức riêng.
- **Độ mới:** trang quan trọng hoặc hay đổi được bò thường xuyên hơn trang ít đổi.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-search-engines-work.md): ba giai đoạn: bò web, lập chỉ mục và phục vụ kết quả.
- [Google — Cách Tìm kiếm hoạt động](https://developers.google.com/search/docs/fundamentals/how-search-works): bò, lập chỉ mục và xếp hạng ở mức tổng quan.
- [RFC 9309 — Robots Exclusion Protocol](https://www.rfc-editor.org/rfc/rfc9309.html): tệp robots.txt.
- [Manning và cộng sự — Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/): chỉ mục đảo và truy xuất.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-018.json).

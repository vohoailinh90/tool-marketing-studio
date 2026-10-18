# Mười nguyên tắc viết mã tốt để nâng chất lượng mã

**Mười nguyên tắc: theo quy ước viết mã, chú thích vì sao, vững vàng, theo SOLID, dễ kiểm thử, trừu tượng vừa phải, dùng mẫu thiết kế đừng quá tay, bớt phụ thuộc toàn cục, tái cấu trúc liên tục và đặt bảo mật lên hàng đầu.**
Bài nguồn dành cho mỗi nguyên tắc một đoạn; bài này giữ nguyên thứ tự rồi đối chiếu một số nguyên tắc với tài liệu của Python và Google.

![Ba nhóm thẻ và một khung ghi nhớ. Đọc được và bền: một theo quy ước viết mã, hai tài liệu và chú thích, ba vững vàng, bốn nguyên tắc SOLID. Dễ kiểm thử và dễ đổi: năm dễ kiểm thử, sáu trừu tượng, bảy mẫu thiết kế nhưng đừng thiết kế quá tay, tám bớt phụ thuộc toàn cục. Giữ lâu dài: chín tái cấu trúc liên tục, mười bảo mật là ưu tiên hàng đầu. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-028-main.svg)

## Từ viết tắt

- **PEP** (Python Enhancement Proposal) — đề xuất cải tiến Python: văn bản đề xuất một thay đổi hay quy ước cho Python; PEP 8 là văn bản quy ước viết mã Python.
- **SOLID** (Single, Open, Liskov, Interface, Dependency) — năm nguyên tắc thiết kế mã hướng đối tượng, mỗi chữ cái là chữ đầu của một nguyên tắc: trách nhiệm đơn (Single responsibility), mở/đóng (Open/closed), thay thế Liskov (Liskov substitution), tách giao diện (Interface segregation), đảo ngược phụ thuộc (Dependency inversion).

## Đọc hình

**Đọc được và bền.**
1. Theo quy ước viết mã. Nên theo các quy ước nổi tiếng của ngành như "PEP 8", "Google Java Style". Theo một bộ quy ước đã thống nhất thì chất lượng mã nhất quán và dễ đọc.
2. Tài liệu và chú thích. Mã tốt được ghi tài liệu và chú thích rõ ràng để giải thích logic phức tạp và các quyết định. Chú thích nên giải thích vì sao chọn một cách làm ("Why") hơn là đang làm đúng việc gì ("What"). Tài liệu và chú thích phải rõ ràng, ngắn gọn và được cập nhật liên tục.
3. Vững vàng (robustness). Mã tốt xử lý được nhiều tình huống và đầu vào bất ngờ mà không sập hay cho kết quả khó đoán. Cách phổ biến nhất là bắt và xử lý ngoại lệ.
4. Theo nguyên tắc SOLID. Năm nguyên tắc: trách nhiệm đơn (Single Responsibility), mở/đóng (Open/Closed), thay thế Liskov (Liskov Substitution), tách giao diện (Interface Segregation) và đảo ngược phụ thuộc (Dependency Inversion). Nguồn gọi chúng là nền tảng của mã có thể mở rộng và dễ bảo trì.

**Dễ kiểm thử và dễ đổi.**
5. Dễ kiểm thử. Khả năng kiểm thử của phần mềm đặc biệt quan trọng. Mã tốt dễ kiểm thử, bằng cách giảm độ phức tạp của từng thành phần và hỗ trợ kiểm thử tự động để bảo đảm nó chạy đúng như mong đợi.
6. Trừu tượng. Trừu tượng đòi hỏi rút ra phần lõi và ẩn độ phức tạp, nhờ đó mã linh hoạt và tổng quát hơn. Mã tốt có mức trừu tượng vừa phải: không thiết kế quá tay, cũng không bỏ qua khả năng mở rộng và bảo trì lâu dài.
7. Dùng mẫu thiết kế nhưng đừng thiết kế quá tay. Mẫu thiết kế giúp giải một số bài toán quen thuộc, nhưng mỗi mẫu có tình huống áp dụng riêng. Dùng quá nhiều hoặc dùng sai có thể làm mã phức tạp và khó hiểu hơn.
8. Bớt phụ thuộc toàn cục. Dùng biến và đối tượng toàn cục dễ sa lầy vào phụ thuộc và quản lý trạng thái rối rắm. Mã tốt nên dựa vào trạng thái cục bộ và truyền tham số; hàm nên không có tác dụng phụ.

**Giữ lâu dài.**
9. Tái cấu trúc liên tục. Mã tốt dễ bảo trì và mở rộng. Tái cấu trúc (refactoring) liên tục giảm nợ kỹ thuật (technical debt) bằng cách phát hiện và sửa vấn đề sớm nhất có thể.
10. Bảo mật là ưu tiên hàng đầu. Mã tốt nên tránh các lỗ hổng bảo mật phổ biến.

**Gặp lại trong tài liệu gốc.**
- PEP 8 nói ý tưởng chủ chốt là mã được đọc nhiều hơn được viết rất nhiều, và các hướng dẫn của nó nhằm tăng độ dễ đọc và làm mã Python nhất quán. Về chú thích, PEP 8 viết: chú thích mâu thuẫn với mã còn tệ hơn không có chú thích; luôn ưu tiên giữ chú thích cập nhật khi mã đổi.
- Hướng dẫn phong cách Java của Google tự giới thiệu là định nghĩa đầy đủ cho các chuẩn viết mã của Google đối với mã nguồn Java; một tệp nguồn chỉ được coi là theo Google Style khi tuân thủ các quy tắc trong đó.
- Tài liệu `unittest` của Python nói nó hỗ trợ kiểm thử tự động, chia sẻ mã dựng và dọn kiểm thử, gom kiểm thử thành tập và tách kiểm thử khỏi khung báo cáo kết quả.
- Hướng dẫn lập trình hàm của Python nói phong cách hàm không khuyến khích hàm có tác dụng phụ, tức làm thay đổi trạng thái nội bộ hoặc có tác động không thấy qua giá trị trả về.

## Giới hạn cần nhớ

Nguồn chỉ nêu mười nguyên tắc ở mức ý chính, không có mã, không có ví dụ và không nói nguyên tắc nào quan trọng hơn; nhiều nguyên tắc (ví dụ SOLID, trừu tượng) có thể gây tranh luận về mức độ áp dụng. Phần "Gặp lại trong tài liệu gốc" chỉ đối chiếu bốn ý (quy ước, chú thích, kiểm thử tự động, hàm không tác dụng phụ), không phải cả mười.
Bài không kiểm tra từng nguyên tắc SOLID hay các mục về trừu tượng, mẫu thiết kế, tái cấu trúc và bảo mật với tài liệu nào; các mục đó là lời của nguồn.

## Nhìn hình trả lời

Một đồng nghiệp viết chú thích "tăng i thêm một" cạnh dòng `i = i + 1`. Theo nguồn, chú thích nên nói điều gì thay vào đó? Nếu mã đã đổi mà chú thích cũ vẫn còn, PEP 8 nói gì?

<details>
<summary>Xem đáp án</summary>

Theo nguồn, chú thích nên giải thích vì sao chọn một cách làm ("Why") hơn là việc đang làm ("What"), và phải rõ ràng, ngắn gọn, cập nhật liên tục.
PEP 8 nói chú thích mâu thuẫn với mã còn tệ hơn không có chú thích, nên phải luôn ưu tiên giữ chú thích cập nhật khi mã đổi.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh, một câu mở đầu và mười đoạn đánh số, mỗi đoạn một nguyên tắc. Hình ở đây giữ đúng mười nguyên tắc và thứ tự, chia thành ba nhóm theo việc nguyên tắc đó lo; cách chia nhóm là của bài, không phải của nguồn. Bài không dùng ảnh nguồn.
Mục "Gặp lại trong tài liệu gốc" lấy từ PEP 8, hướng dẫn phong cách Java của Google, tài liệu `unittest` và hướng dẫn lập trình hàm của Python tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/10-good-coding-principles-to-improve-code-quality.md): mười nguyên tắc.
- [Python — PEP 8](https://github.com/python/peps/blob/6068058b896441388bbf22f2607ab681193f6a3d/peps/pep-0008.rst): mã được đọc nhiều hơn được viết, giữ chú thích cập nhật. Đọc từ kho mã.
- [Google — Java Style Guide](https://github.com/google/styleguide/blob/f43b95b083a5e52c85fcbb9e7e76cbd5e1c2b3f8/javaguide.html): định nghĩa chuẩn viết mã Java của Google. Đọc từ kho mã.
- [Python — unittest](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/unittest.rst) và [hướng dẫn lập trình hàm](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/howto/functional.rst): kiểm thử tự động, hàm không tác dụng phụ. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa PEP và SOLID trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

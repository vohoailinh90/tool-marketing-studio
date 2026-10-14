# Thiết kế hệ thống an toàn: mười hai câu cần hỏi

**Thiết kế an toàn không phải một tính năng thêm vào cuối, mà là một danh sách câu hỏi hỏi từ đầu, mỗi câu thuộc một mảng.**
Bài này gom mười hai mảng của bài nguồn thành bốn nhóm câu hỏi và chỉ ra mảng nào có tài liệu OWASP mang tên tương ứng, mảng nào chưa.

![Sáu thẻ xếp dọc. Thẻ đầu: bắt đầu từ mặc định an toàn, thu nhỏ bề mặt tấn công và thất bại một cách an toàn. Bốn nhóm câu hỏi. Ai được vào: xác thực, phân quyền, bảo mật API, quản lý nhà cung cấp bên thứ ba. Dữ liệu và đường truyền: mã hóa, bảo mật mạng. Hạ tầng: bảo mật container, bảo mật thiết bị đầu cuối. Khi có chuyện: quản lý lỗ hổng, kiểm toán và tuân thủ, ứng phó khẩn cấp, khôi phục sau thảm họa. Thẻ cuối: thiết bị đầu cuối, ứng phó khẩn cấp và khôi phục sau thảm họa chưa có tài liệu mang tên tương ứng trong bộ OWASP Cheat Sheet Series.](../../diagrams/sd-14-012-main.svg)

## Đọc hình

**Nguyên tắc nền.** OWASP, trong tài liệu thiết kế sản phẩm an toàn, bắt đầu bằng ba điều: đặt mặc định an toàn, thu nhỏ bề mặt tấn công và thất bại theo cách an toàn.

**Ai được vào.** Xác thực (bạn là ai) và phân quyền (bạn được làm gì) là hai câu hỏi khác nhau. API là cửa của hệ thống nên cần cả hai. Nhà cung cấp bên thứ ba, như đoạn mã nhúng hay thư viện, cũng là một lối vào cần quản lý.

**Dữ liệu và đường truyền.** Mã hóa bảo vệ dữ liệu lưu trữ; bảo mật mạng, ở đây xét qua TLS, bảo vệ dữ liệu trên đường đi.

**Hạ tầng.** Container và cụm chạy chúng có tài liệu bảo mật riêng (Docker, Kubernetes). Bảo mật thiết bị đầu cuối không có tài liệu cùng tên trong bộ OWASP Cheat Sheet Series (xét theo tên tệp; có một tài liệu riêng cho ứng dụng di động).

**Khi có chuyện.** Quản lý lỗ hổng trong thư viện đang dùng, ghi nhật ký để kiểm toán, ứng phó khi sự cố xảy ra và khôi phục sau thảm họa. Với ứng phó khẩn cấp và khôi phục sau thảm họa, không có tên tài liệu nào tương ứng trong bộ OWASP đó (xét theo tên tệp).

## Giới hạn cần nhớ

Danh sách này chỉ là bản đồ các câu hỏi, không phải bằng chứng hệ thống đã an toàn: trả lời “có” cho cả mười hai mảng vẫn chưa nói được mức độ làm tốt từng mảng, và cách chia bốn nhóm là của người biên soạn, không phải của nguồn hay của OWASP.

## Nhìn hình trả lời

Một đội thêm nút đăng nhập bằng mật khẩu nhưng chưa có bản kiểm tra thư viện có lỗ hổng, chưa có quy trình khi lộ dữ liệu và chưa ghi nhật ký. Mảng nào đã có, mảng nào đang thiếu, và nhóm câu hỏi nào bị bỏ trống?

<details>
<summary>Xem đáp án</summary>

Đã có một phần của “xác thực” trong nhóm Ai được vào; chưa có “phân quyền” (đăng nhập xong thì ai được làm gì?). Thiếu quản lý lỗ hổng, kiểm toán qua nhật ký và ứng phó khẩn cấp, tức là gần như cả nhóm Khi có chuyện.
Hình không chấm điểm: nó chỉ giúp thấy câu hỏi nào chưa ai trả lời.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Phần chữ của bài nguồn chỉ là danh sách mười hai mảng (xác thực, phân quyền, mã hóa, lỗ hổng, kiểm toán và tuân thủ, bảo mật mạng, bảo mật thiết bị đầu cuối, ứng phó khẩn cấp, bảo mật container, bảo mật API, quản lý nhà cung cấp bên thứ ba, khôi phục sau thảm họa); nội dung chi tiết nằm trong ảnh, và bài này không dùng ảnh. Vì vậy mỗi mảng có tên khớp ở đây được nối với một tài liệu OWASP đã đọc thay vì diễn giải bài nguồn.
Đối chiếu đã đọc: xác thực, phân quyền, mã hóa lưu trữ, quản lý thư viện có lỗ hổng, ghi nhật ký, TLS, bảo mật REST, Docker và Kubernetes, chuỗi cung ứng phần mềm, mã JavaScript bên thứ ba. Trong 137 tài liệu của bộ OWASP Cheat Sheet Series tại commit đã dùng, không có tên tệp nói về thiết bị đầu cuối, ứng phó sự cố, khôi phục sau thảm họa, tuân thủ, kiểm toán hay sao lưu; đây chỉ là xét theo tên tệp, tôi không tìm trong nội dung, nên OWASP có thể bàn các chủ đề đó ở chỗ khác. Phần mở đầu của mỗi tài liệu OWASP được đọc, nhưng nội dung từng tài liệu chưa được đối chiếu từng mục.
Đây là bản đồ; các tài liệu OWASP đã được đọc ở phần mở đầu và không đọc hết từng bài.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-design-a-secure-system.md): danh sách mười hai mảng thiết kế an toàn.
- [OWASP — Secure Product Design Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Secure_Product_Design_Cheat_Sheet.md): mặc định an toàn, thu nhỏ bề mặt tấn công, thất bại an toàn. Đọc từ bản clone của kho.
- [OWASP — Authentication](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Authentication_Cheat_Sheet.md), [Authorization](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Authorization_Cheat_Sheet.md), [Cryptographic Storage](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Cryptographic_Storage_Cheat_Sheet.md), [Transport Layer Security](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Transport_Layer_Security_Cheat_Sheet.md), [REST Security](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/REST_Security_Cheat_Sheet.md): xác thực, phân quyền, mã hóa lưu trữ, bảo vệ đường truyền, bảo mật API. Đọc từ bản clone của kho.
- [OWASP — Docker Security](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Docker_Security_Cheat_Sheet.md), [Kubernetes Security](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Kubernetes_Security_Cheat_Sheet.md): bảo mật container. Đọc từ bản clone của kho.
- [OWASP — Vulnerable Dependency Management](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.md), [Logging](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Logging_Cheat_Sheet.md), [Software Supply Chain Security](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.md), [Third Party JavaScript Management](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.md): quản lý lỗ hổng, nhật ký, chuỗi cung ứng, mã bên thứ ba. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Cách chia mười hai mảng thành bốn nhóm là của người biên soạn. Bài viết và hình được thiết kế độc lập.

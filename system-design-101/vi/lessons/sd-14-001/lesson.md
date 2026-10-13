# DevSecOps là gì?

**DevSecOps đưa kiểm tra bảo mật vào từng chặng của đường ống phát triển, thay vì dồn lại một lần ở cuối.**
Hướng dẫn DevSecOps của OWASP nêu mục tiêu là phát hiện vấn đề bảo mật, từ thiết kế lẫn từ lỗ hổng ứng dụng, càng sớm càng tốt.

![Sáu thẻ nối nhau từ trên xuống, mỗi chặng một việc bảo mật. 1 Lập kế hoạch: mô hình hóa mối đe dọa. 2 Viết mã: quét bí mật trước khi commit, phân tích mã tĩnh SAST. 3 Xây dựng: quét thư viện phụ thuộc SCA và ảnh container, tạo SBOM. 4 Kiểm thử: quét động DAST, kiểm thử tương tác IAST. 5 Triển khai: quét hạ tầng dưới dạng mã, cổng chặn bản phát hành rủi ro. 6 Vận hành: giám sát liên tục, quản lý lỗ hổng. Thẻ cuối: chính đường ống CI/CD cũng là mục tiêu, công cụ mở rộng bề mặt tấn công và cần được bảo vệ.](../../diagrams/sd-14-001-main.svg)

## Đọc hình

**1 · Lập kế hoạch.** Mô hình hóa mối đe dọa: ai có thể tấn công, qua đường nào, trước khi viết dòng mã đầu tiên.

**2 · Viết mã.** Quét bí mật (khóa API, mật khẩu) trước khi commit, để chúng không vào kho mã. Phân tích mã tĩnh (SAST) tìm lỗi bảo mật ngay trong mã nguồn.

**3 · Xây dựng.** Phân tích thành phần phần mềm (SCA) tìm thư viện phụ thuộc có lỗ hổng đã biết. Quét ảnh container. Tạo SBOM, danh mục các thành phần của bản build.

**4 · Kiểm thử.** Kiểm thử bảo mật động (DAST) tấn công thử ứng dụng đang chạy; kiểm thử tương tác (IAST) quan sát ứng dụng từ bên trong khi chạy kiểm thử.

**5 · Triển khai.** Quét hạ tầng viết dưới dạng mã (như Terraform, Helm) để tìm cấu hình sai. Cổng bảo mật chặn các bản build và bản phát hành quá rủi ro.

**6 · Vận hành.** Giám sát liên tục, quản lý lỗ hổng, và kiểm tra tuân thủ bằng chính sách viết dưới dạng mã.

## Giới hạn cần nhớ

Đường ống tự động hóa là một lối vào đặc quyền, nên bản thân nó cũng là mục tiêu. OWASP lưu ý các công cụ CI/CD thường mở rộng bề mặt tấn công,
vì vậy phải bảo vệ chính chúng chứ không chỉ dùng chúng để bảo vệ ứng dụng.

## Nhìn hình trả lời

Một khóa API vô tình bị commit lên kho mã. Chặng nào trong hình lẽ ra nên bắt được, và vì sao chặng đó?

<details>
<summary>Xem đáp án</summary>

Chặng viết mã, bằng quét bí mật trước khi commit. Càng bắt sớm, khóa càng ít có cơ hội lọt vào lịch sử kho mã và đi tiếp tới các chặng sau.
Nếu khóa đã lộ, hãy coi nó không còn bí mật và thay bằng khóa mới; OWASP nhấn mạnh việc xoay vòng bí mật để giảm rủi ro khi thông tin xác thực bị lộ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê mười khái niệm, không xếp theo thứ tự nào. Hình này gắn các việc kỹ thuật vào chặng của đường ống để thấy mỗi việc xảy ra ở đâu.
Hai khái niệm còn lại là văn hóa chứ không phải chặng: tích hợp bảo đảm chất lượng và phối hợp, giao tiếp giữa các nhóm.
Danh sách công cụ và kỹ thuật theo chặng lấy từ mục lục hướng dẫn DevSecOps của OWASP; bài này không đánh giá công cụ cụ thể nào.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-devsecops.md): mười khái niệm chính.
- [OWASP — DevSecOps Guideline](https://github.com/OWASP/DevSecOpsGuideline): mục tiêu phát hiện sớm; các hạng mục SCA, SAST, DAST, IAST, quét IaC, chuỗi cung ứng phần mềm (SBOM), cổng bảo mật, chính sách dưới dạng mã; lưu ý CI/CD mở rộng bề mặt tấn công. Đọc từ bản clone của kho.
- [OWASP — Secrets Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Secrets_Management_Cheat_Sheet.md): quản lý và xoay vòng bí mật. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Mô hình hóa mối đe dọa và việc xếp từng kỹ thuật vào chặng cụ thể là cách sắp xếp của người biên soạn, chưa đối chiếu với một tiêu chuẩn nào.
Bài viết và hình được thiết kế độc lập.

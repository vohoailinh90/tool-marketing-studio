# DevSecOps là gì?

**DevSecOps đưa kiểm tra bảo mật vào từng chặng của đường ống phát triển, thay vì dồn lại một lần ở cuối.**
Hướng dẫn DevSecOps của OWASP nêu mục tiêu là phát hiện vấn đề bảo mật, từ thiết kế lẫn từ lỗ hổng ứng dụng, càng sớm càng tốt.

![Chín thẻ xếp dọc. Bảy chặng nối nhau theo cấu trúc hướng dẫn của OWASP. 1 Thiết kế: mô hình hóa mối đe dọa, yêu cầu và thiết kế an toàn. 2 Phát triển: quản lý bí mật, kiểm tra trước khi commit, rà soát mã. 3 Xây dựng: SAST, SCA, quét container, quét IaC, cổng bảo mật, SBOM. 4 Kiểm thử: IAST, DAST, bảo mật API. 5 Phát hành: cổng bảo mật cuối, ký bản build, đính kèm SBOM, phê duyệt phát hành. 6 Triển khai: chỉ chạy bản build đã xác minh chữ ký, quản lý bí mật trên Kubernetes và GitOps. 7 Vận hành: ghi nhật ký và giám sát, quản lý lỗ hổng, kiểm thử xâm nhập. Thẻ thứ tám: xuyên suốt, quản trị, gồm kiểm tra tuân thủ và chính sách dưới dạng mã. Thẻ cuối: chính đường ống cũng là mục tiêu, công cụ CI/CD mở rộng bề mặt tấn công và cần được bảo vệ.](../../diagrams/sd-14-001-main.svg)

## Đọc hình

Các chặng và hạng mục dưới đây theo mục lục của hướng dẫn OWASP; phần giải nghĩa từng kỹ thuật là của người biên soạn.

**1 · Thiết kế.** Mô hình hóa mối đe dọa (ai có thể tấn công, qua đường nào) và đặt yêu cầu, thiết kế an toàn trước khi viết mã.

**2 · Phát triển.** Quản lý bí mật như khóa API và mật khẩu, kiểm tra trước khi commit để chúng không vào kho mã, và rà soát mã an toàn.

**3 · Xây dựng.** Phân tích mã tĩnh (SAST) tìm lỗi ngay trong mã nguồn. Phân tích thành phần phần mềm (SCA) tìm thư viện phụ thuộc có lỗ hổng đã biết.
Quét container, quét hạ tầng viết dưới dạng mã (IaC) để tìm cấu hình sai, và cổng bảo mật chặn các bản build quá rủi ro.
SBOM là danh mục thành phần của bản build.

**4 · Kiểm thử.** Kiểm thử bảo mật động (DAST) tấn công thử ứng dụng đang chạy; kiểm thử tương tác (IAST) quan sát ứng dụng từ bên trong khi chạy kiểm thử; thêm kiểm thử bảo mật API.

**5 · Phát hành.** Chặng cuối trước khi bản build rời đường ống. Hướng dẫn OWASP nêu cổng bảo mật cuối, ký bản build, đính kèm SBOM và nguồn gốc bản build, phê duyệt phát hành và ghi chú phát hành về bảo mật. Các trang về cách tạo SBOM và về ký bản build, nguồn gốc nằm ở chặng Xây dựng trong mục lục; chương Phát hành dẫn tới chúng và nói gắn chúng vào bản phát hành, rồi ký.

**6 · Triển khai.** Đưa bản đã phát hành vào môi trường chạy. Chỉ cho chạy bản build đã xác minh được chữ ký và nguồn gốc; mục lục còn có phần riêng về quản lý bí mật trên Kubernetes và GitOps.

**7 · Vận hành.** Ghi nhật ký và giám sát, quản lý lỗ hổng, kiểm thử xâm nhập.

**Xuyên suốt: quản trị.** Kiểm tra tuân thủ và chính sách viết dưới dạng mã nằm ở phần quản trị của hướng dẫn, không thuộc riêng chặng nào.

## Giới hạn cần nhớ

Chính đường ống tự động hóa cũng cần được bảo vệ. OWASP lưu ý các công cụ CI/CD thường mở rộng bề mặt tấn công,
và xếp bảo mật đường ống CI/CD thành một hạng mục trong chặng xây dựng. Dùng công cụ để bảo vệ ứng dụng mà bỏ quên chính công cụ là thiếu sót.

## Nhìn hình trả lời

Một khóa API vô tình bị commit lên kho mã. Chặng nào trong hình lẽ ra nên bắt được, và vì sao chặng đó?

<details>
<summary>Xem đáp án</summary>

Chặng phát triển, qua quản lý bí mật và kiểm tra trước khi commit. Càng bắt sớm, khóa càng ít có cơ hội lọt vào lịch sử kho mã và đi tiếp tới các chặng sau.
Nếu khóa đã lộ, hãy coi nó không còn bí mật và thay bằng khóa mới; OWASP nhấn mạnh việc xoay vòng bí mật để giảm rủi ro khi thông tin xác thực bị lộ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê mười khái niệm, không xếp theo thứ tự nào. Hình này gắn các việc kỹ thuật vào chặng theo mục lục của OWASP để thấy mỗi việc xảy ra ở đâu.
Hai khái niệm còn lại của bài nguồn là văn hóa chứ không phải chặng: tích hợp bảo đảm chất lượng và phối hợp, giao tiếp giữa các nhóm.
Bài này đọc mục lục, phần mở đầu và phần đầu hai chương Phát hành và Triển khai của hướng dẫn OWASP; các chương còn lại chưa đọc, và bài không đánh giá công cụ cụ thể nào.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-devsecops.md): mười khái niệm chính.
- [OWASP — DevSecOps Guideline, tại commit cố định](https://github.com/OWASP/DevSecOpsGuideline/blob/a4d07324cec24f222be5e8f2b12d3ec27bba714c/README.md): mục tiêu phát hiện sớm; mục lục bảy chặng thiết kế, phát triển, xây dựng, kiểm thử, phát hành, triển khai, vận hành và phần quản trị; phần đầu hai chương Phát hành và Triển khai; lưu ý CI/CD mở rộng bề mặt tấn công. Đọc từ bản clone của kho.
- [OWASP — Secrets Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/ae965343cb82e6b8f42aff1ccee57c4fa0f171c2/cheatsheets/Secrets_Management_Cheat_Sheet.md): quản lý và xoay vòng bí mật. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Tên chặng được dịch sang tiếng Việt; phần giải nghĩa từng kỹ thuật (SAST, SCA, DAST, IAST, SBOM…) là kiến thức chung của người biên soạn, chưa đối chiếu với các chương Xây dựng và Kiểm thử của OWASP.
Bài viết và hình được thiết kế độc lập.

# CI đỏ mà máy bạn chạy được: năm nguồn khác biệt

Lỗi khó chịu nhất của CI (Continuous Integration — tích hợp liên tục) là "máy tôi chạy được". Thường pipeline không sai: hai môi trường khác nhau ở một chỗ mà không ai ghi lại. Bài này nêu năm nguồn khác biệt hay gặp và cách khóa từng nguồn lại.

![Năm nguồn khác biệt khiến CI (Continuous Integration — tích hợp liên tục) đỏ trong khi máy bạn chạy được: phiên bản công cụ và phụ thuộc, môi trường chạy như nhãn runner, trạng thái còn sót ở máy bạn, cấu hình và bí mật chỉ có ở một bên, và thứ tự chạy, múi giờ hay tài nguyên dùng chung giữa các test.](../../diagrams/sd-13-014-main.svg)

**Đọc hình:** năm thẻ là năm nguồn khác biệt độc lập; thẻ nào cũng kèm cách khóa lại.

## Từ viết tắt

- **CI** (Continuous Integration) — tích hợp liên tục: tự động xây dựng và kiểm tra mã mỗi khi có thay đổi.
- **OS** (Operating System) — hệ điều hành: phần mềm nền quản lý máy và chạy các chương trình khác; macOS là hệ điều hành của máy Apple.

## Nhìn hình thử trả lời

Test qua trên máy macOS của bạn nhưng lỗi trên runner Linux vì không tìm thấy tệp `Config.json`, trong khi tệp trong repo (viết tắt của repository — kho mã nguồn) tên `config.json`. Nguyên nhân hay gặp nhất là gì?

<details>
<summary>Xem đáp án</summary>

Hệ tệp phân biệt hoa thường. macOS và Windows thường mặc định không phân biệt nên mã vẫn chạy ở máy bạn, còn Linux coi hai tên là khác nhau. Hãy sửa tên trong mã cho khớp đúng chữ hoa chữ thường của tệp.

</details>

## Giới hạn cần nhớ

Bài chỉ nêu năm nguồn khác biệt hay gặp, không phải mọi nguyên nhân: lỗi mạng, hết tài nguyên của runner hay lỗi của chính dịch vụ CI cũng làm job đỏ. Chạy lại job không phải cách chẩn đoán; nếu chạy lại đổi kết quả mà không đổi gì, hãy coi đó là test chập chờn cần sửa chứ không phải may rủi cần chấp nhận.

<details>
<summary>Xem sâu hơn</summary>

- **Phiên bản:** cài phụ thuộc theo tệp khóa bằng lệnh nghiêm ngặt (như `npm ci`, báo lỗi khi tệp khóa không khớp khai báo) và chỉ định phiên bản ngôn ngữ và công cụ trong workflow thay vì dùng bản cài sẵn trên runner.
- **Môi trường:** nhãn dạng `-latest` có thể trỏ sang hệ điều hành mới hơn theo thời gian. Nhãn có số phiên bản (như `ubuntu-24.04`) chỉ cố định bản hệ điều hành; phần mềm cài sẵn trên image runner vẫn được GitHub cập nhật định kỳ, nên cùng một job có thể đổi kết quả mà repo không đổi. Hãy chỉ định rõ phiên bản từng công cụ trong workflow (ví dụ qua các action cài đặt có tham số phiên bản), hoặc chạy job trong một container có image cố định (tốt nhất ghim theo digest) và dùng đúng image đó ở máy bạn.
- **Trạng thái sót:** thử lại bằng một bản clone mới ở thư mục khác trước khi nghi ngờ CI; nếu lỗi xuất hiện thì máy bạn đang che nó.
- **Cấu hình:** liệt kê mọi biến môi trường và bí mật mà test cần; nhớ rằng mặc định workflow chạy từ pull request của fork không nhận bí mật.
- **Thứ tự và tranh chấp:** test chập chờn khi chạy song song thường do dùng chung cổng, tệp hay cơ sở dữ liệu; ghi lại múi giờ và hạt giống ngẫu nhiên của lần chạy để dựng lại lỗi.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cicd-simplified-visual-guide.md).
- npm: [npm ci](https://docs.npmjs.com/cli/commands/npm-ci). Docker: [ghim phiên bản image cơ sở](https://docs.docker.com/build/building/best-practices/).
- GitHub Docs: [runner do GitHub cung cấp](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners), [workflow syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions), [bảo mật workflow](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions).

# Mười một bước từ lập trình viên mới vào nghề tới cấp cao

**Bài nguồn gợi ý mười một bước để đi từ lập trình viên mới vào nghề (junior) tới cấp cao (senior): từ công cụ cộng tác và ngôn ngữ lập trình, qua API, kiểm thử, cơ sở dữ liệu, tới thiết kế hệ thống và công cụ AI.**
Mỗi bước trong nguồn gồm một việc cần học và vài ví dụ công cụ; bài này giữ nguyên thứ tự và ví dụ của nguồn, và nói rõ đây là lộ trình theo ý tác giả.

![Bốn chuỗi bước, mười một bước. Cách làm việc: một công cụ cộng tác; hai ngôn ngữ lập trình; ba phát triển API. Vận hành và dữ liệu: bốn máy chủ web và lưu trữ; năm xác thực và kiểm thử; sáu cơ sở dữ liệu. Tự động hóa và nền tảng: bảy CI/CD; tám cấu trúc dữ liệu và thuật toán. Tầm nhìn: chín thiết kế hệ thống; mười mẫu thiết kế; mười một công cụ AI. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-027-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: tập quy ước để một chương trình dùng chức năng của chương trình khác.
- **REST** (REpresentational State Transfer) — kiểu thiết kế dịch vụ qua HTTP: mỗi tài nguyên có một địa chỉ riêng, thường trao đổi dữ liệu dạng JSON.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu (request) và máy chủ gửi trả lời (response).
- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, cho biết đây là cách để client mô tả dữ liệu mình muốn lấy.
- **gRPC** (gRPC Remote Procedure Calls) — khung gọi thủ tục từ xa mã nguồn mở của Google: mã hóa message bằng Protocol Buffers và chuyên chở qua HTTP/2.
- **MS** (MicroSoft) — tên hãng phần mềm Microsoft: trong "MS Teams", công cụ họp và nhắn tin của hãng này.
- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon.
- **GCP** (Google Cloud Platform) — nền tảng điện toán đám mây của Google.
- **JWT** (JSON Web Token) — token web: chuỗi tự mang thông tin người dùng và có chữ ký, để máy chủ kiểm mà không cần tra bảng.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản biểu diễn dữ liệu bằng các cặp tên và giá trị, dễ đọc với cả người và máy.
- **OAuth** (Open AUTHorization) — chuẩn ủy quyền mở: cho một ứng dụng được làm một số việc thay bạn mà không biết mật khẩu của bạn; OAuth2 là một phiên bản của chuẩn này.
- **TDD** (Test-Driven Development) — phát triển hướng kiểm thử: viết kiểm thử trước khi viết mã cần kiểm thử.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; MySQL và SQLite là hai hệ cơ sở dữ liệu dùng nó.
- **CI** (Continuous Integration) — tích hợp liên tục: quy trình tự động kiểm tra thay đổi mã.
- **CD** (Continuous Delivery) — phân phối liên tục: quy trình đưa bản đã kiểm tra tới nơi sẵn sàng phát hành.
- **DSA** (Data Structures and Algorithms) — cấu trúc dữ liệu và thuật toán: cách tổ chức dữ liệu và cách giải bài toán trên dữ liệu đó.
- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt ở nhiều nơi, lưu bản sao nội dung và phát cho người dùng từ máy gần họ.
- **AI** (Artificial Intelligence) — trí tuệ nhân tạo: các hệ thống máy tính làm những việc thường cần trí thông minh của con người, như hiểu ngôn ngữ hay nhận ra hình ảnh.
- **GPT** (Generative Pretrained Transformer) — tên một dòng mô hình ngôn ngữ được huấn luyện sẵn trên lượng văn bản rất lớn rồi mới dùng cho việc cụ thể; ChatGPT là sản phẩm hỏi đáp dùng loại mô hình này.

## Đọc hình

**Cách làm việc.**
1. Công cụ cộng tác. Phát triển phần mềm là hoạt động xã hội, nên cần biết các công cụ cộng tác như Jira, Confluence, Slack, MS Teams, Zoom.
2. Ngôn ngữ lập trình. Chọn và thành thạo một hoặc hai ngôn ngữ, ví dụ Java, Python, JavaScript, C#, Go.
3. Phát triển API. Học kỹ các cách làm API như REST, GraphQL và gRPC.

**Vận hành và dữ liệu.**
4. Máy chủ web và lưu trữ. Biết về máy chủ web và các nền tảng đám mây như AWS, Azure, GCP và Kubernetes.
5. Xác thực và kiểm thử. Học cách bảo vệ ứng dụng bằng các kỹ thuật xác thực như JWT, OAuth2; đồng thời thành thạo các kỹ thuật kiểm thử như TDD, kiểm thử đầu cuối (end-to-end) và kiểm thử hiệu năng.
6. Cơ sở dữ liệu. Làm việc với cơ sở dữ liệu quan hệ (Postgres, MySQL, SQLite) và phi quan hệ (MongoDB, Cassandra, Redis).

**Tự động hóa và nền tảng.**
7. CI/CD. Chọn công cụ như GitHub Actions, Jenkins hoặc CircleCI để học tích hợp liên tục và phân phối liên tục.
8. Cấu trúc dữ liệu và thuật toán. Nắm vững nền tảng của DSA với các chủ đề như ký hiệu Big O, sắp xếp, cây và đồ thị.

**Tầm nhìn.**
9. Thiết kế hệ thống. Học các khái niệm như mạng, bộ nhớ đệm, CDN, microservice, nhắn tin, cân bằng tải, nhân bản, hệ phân tán.
10. Mẫu thiết kế. Thành thạo cách áp dụng các mẫu như dependency injection, factory, proxy, observer và facade.
11. Công cụ AI. Để nghề nghiệp bền với tương lai, học cách tận dụng công cụ AI như GitHub Copilot, ChatGPT, Langchain và prompt engineering.

## Giới hạn cần nhớ

Đây là lộ trình theo ý tác giả nguồn, không phải chuẩn nghề: nguồn không nói thứ tự nào là bắt buộc, mỗi bước mất bao lâu, mức nào thì được gọi là senior, và vì sao chọn đúng mười một bước. Tên công cụ chỉ là ví dụ và có thể đổi theo thời gian; bài không kiểm tra từng công cụ.
Bước 5 gộp hai việc (xác thực và kiểm thử) và bước 9 gộp rất nhiều chủ đề; bài giữ cách gộp của nguồn. Bài này không có nguồn ngoài, nên mọi điều trong đó là lời của nguồn.

## Nhìn hình trả lời

Bạn đã chọn một ngôn ngữ và biết làm API. Theo nguồn, hai bước nào nói về bảo vệ ứng dụng bằng xác thực và về việc tự động đưa mã tới nơi chạy? Và bước cuối cùng, mười một, nói về việc gì?

<details>
<summary>Xem đáp án</summary>

Bước 5, xác thực và kiểm thử (JWT, OAuth2, kiểm thử): học cách bảo vệ ứng dụng.
Bước 7, CI/CD: dùng công cụ như GitHub Actions, Jenkins hoặc CircleCI để học tích hợp liên tục và phân phối liên tục.
Bước 11 là công cụ AI: học tận dụng GitHub Copilot, ChatGPT, Langchain và prompt engineering để nghề nghiệp bền với tương lai.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh lộ trình và mười một đoạn ngắn, mỗi đoạn một việc kèm ví dụ công cụ. Hình ở đây giữ đúng mười một bước và thứ tự, chia thành bốn nhóm theo việc bước đó lo; cách chia nhóm là của bài, không phải của nguồn. Bài không dùng ảnh nguồn.
Bài không có nguồn ngoài; tên bước, ví dụ và thứ tự đều lấy từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/11-steps-to-go-from-junior-to-senior-developer.md): mười một bước và ví dụ công cụ.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa viết tắt trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

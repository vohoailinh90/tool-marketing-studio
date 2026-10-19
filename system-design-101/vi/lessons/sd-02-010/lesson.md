# Twitter 1.0: năm tầng, mười ba cái tên

**Một "tech stack" là danh sách công cụ xếp theo tầng; bài nguồn kể ra mười ba cái tên của Twitter 1.0 trong năm tầng, từ ứng dụng di động tới cơ sở dữ liệu.**
Bài nguồn chỉ có danh sách. Bài này dùng nó để tập đọc một stack: mỗi tầng làm việc gì, và vì sao một tầng thường có nhiều hơn một công cụ.

![Hai khung thẻ và một khung ghi nhớ. Khung một, phía người dùng: di động gồm Swift, Kotlin và ứng dụng web tiến bộ; web gồm JavaScript, React và Redux. Khung hai, phía máy chủ: dịch vụ chạy trên Mesos và Finagle; bộ đệm là Pelikan Cache và Redis; cơ sở dữ liệu là Manhattan, MySQL và PostgreSQL. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-010-main.svg)

## Từ viết tắt

- **PWA** (Progressive Web App) — ứng dụng web tiến bộ: trang web có thể cài lên máy và chạy gần giống một ứng dụng thật.
- **JS** (JavaScript) — ngôn ngữ lập trình chạy trong trình duyệt, dùng để làm phần tương tác của trang web.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: cách hỏi và sửa dữ liệu trong cơ sở dữ liệu dạng bảng; chữ SQL nằm trong tên MySQL và PostgreSQL.

## Đọc hình

**Phía người dùng.**
- Di động: Swift (ứng dụng iPhone), Kotlin (ứng dụng Android) và PWA.
- Web: JS, với React để dựng giao diện và Redux để giữ trạng thái của giao diện.

**Phía máy chủ.**
- Dịch vụ: Mesos chia máy cho các dịch vụ chạy; Finagle là thư viện để các dịch vụ gọi nhau.
- Bộ đệm: Pelikan Cache và Redis giữ dữ liệu hay đọc trong bộ nhớ.
- Cơ sở dữ liệu: Manhattan, MySQL và PostgreSQL.

Bài nguồn chỉ nêu tên. Phần giải thích từng công cụ làm gì là kiến thức chung của người biên soạn.

## Giới hạn cần nhớ

Bài nguồn không nói "Twitter 1.0" là giai đoạn nào, cũng không nói công cụ nào gánh phần việc nào. Ví dụ, nó không nói dữ liệu nào nằm ở Manhattan và dữ liệu nào nằm ở MySQL. Đừng suy ra kiến trúc từ một danh sách tên: danh sách cho biết có gì, không cho biết các thứ nối với nhau ra sao.

## Nhìn hình thử trả lời

Tầng cơ sở dữ liệu có ba cái tên. Vì sao một công ty có thể dùng nhiều hơn một cơ sở dữ liệu cùng lúc?

<details>
<summary>Xem đáp án</summary>

Vì mỗi loại dữ liệu có cách đọc ghi riêng: có dữ liệu cần truy vấn bảng linh hoạt, có dữ liệu cần ghi rất nhiều và đọc theo khóa. Một công ty lớn cũng hay giữ hệ thống cũ chạy song song với hệ thống mới. Bài nguồn không nói lý do cụ thể của Twitter; đây là lý do chung.

</details>

<details>
<summary>Xem sâu hơn: đọc một stack theo câu hỏi</summary>

- Người dùng chạm vào đâu? (di động, web)
- Yêu cầu được xử lý ở đâu, và các dịch vụ gọi nhau bằng gì?
- Dữ liệu hay đọc được giữ ở đâu cho nhanh?
- Dữ liệu được lưu lâu dài ở đâu?

Gợi ý của người biên soạn để đọc bất kỳ danh sách công nghệ nào, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/twitter-10-tech-stack.md): danh sách công cụ của Twitter 1.0 theo năm tầng.

Đã đọc nguồn ngày 2026-10-19. Mô tả từng công cụ là kiến thức chung của người biên soạn, chưa đối chiếu tài liệu chính thức.
Bài viết và hình được thiết kế độc lập.

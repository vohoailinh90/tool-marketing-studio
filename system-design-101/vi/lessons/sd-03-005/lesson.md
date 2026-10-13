# Ngăn xếp AI mã nguồn mở

**Dựng một ứng dụng AI là ghép nhiều tầng, và mỗi tầng đều có lựa chọn mã nguồn mở.**
Ở mỗi tầng hãy hỏi hai điều: nó giải quyết việc gì, và giấy phép cho phép bạn làm gì.

![Năm thẻ nối nhau từ trên xuống. 1 Giao diện: Streamlit, Next.js. 2 Backend và gọi mô hình: FastAPI, Metaflow, Ollama. 3 Embedding và RAG: biến văn bản thành vector, tìm đoạn liên quan cho prompt. 4 Lưu trữ và truy xuất: Postgres với pgvector, Milvus, Weaviate; Faiss là thư viện chứ không phải cơ sở dữ liệu. 5 Mô hình: Llama, Mistral, Qwen, Phi, Gemma với giấy phép khác nhau. Thẻ cuối nhắc rằng mở có nhiều mức.](../../diagrams/sd-03-005-main.svg)

## Đọc hình

**1 · Giao diện.** Nơi người dùng thao tác. Streamlit dựng ứng dụng dữ liệu bằng Python; Next.js là framework web.

**2 · Backend và gọi mô hình.** FastAPI dựng API cho các lời gọi; Metaflow, khởi nguồn từ Netflix,
quản lý quy trình AI/ML; Ollama giúp chạy và gọi mô hình.

**3 · Embedding và RAG.** Embedding biến văn bản thành vector. RAG tìm các đoạn liên quan rồi đưa chúng vào prompt
để mô hình trả lời dựa trên dữ liệu của bạn.

**4 · Lưu trữ và truy xuất.** Cần nơi giữ vector và tìm gần đúng. pgvector thêm tìm kiếm vector vào Postgres;
Milvus và Weaviate là cơ sở dữ liệu vector. Faiss là thư viện tìm kiếm tương tự, không tự là máy chủ cơ sở dữ liệu.

**5 · Mô hình.** Llama, Mistral, Qwen, Phi, Gemma là các họ mô hình công bố trọng số để tải về.

## Giới hạn cần nhớ

“Mở” có nhiều mức. Công bố trọng số chưa chắc là mã nguồn mở: định nghĩa Open Source AI 1.0 của OSI (10/2024)
còn đòi thông tin về dữ liệu huấn luyện và mã nguồn, và OSI nói giấy phép của Llama không phải mã nguồn mở.
Trước khi chọn, đọc giấy phép từng mô hình và công cụ.

## Nhìn hình trả lời

pgvector và Faiss đều tìm kiếm vector. Chúng khác nhau thế nào về loại thành phần?

<details>
<summary>Xem đáp án</summary>

pgvector là phần mở rộng của Postgres, nên dữ liệu nằm trong một cơ sở dữ liệu. Faiss là thư viện
bạn nhúng vào chương trình; nó không tự là máy chủ cơ sở dữ liệu.

</details>

<details>
<summary>Xem sâu hơn: điều đã bỏ so với bài nguồn</summary>

Bài nguồn còn nêu Vercel, Nomic, JinaAI, “Cognito”, LLMWare, Hugging Face và nhận định rằng các công cụ
tốt nhất đều là mã nguồn mở. Những công cụ này chưa được đối chiếu trong đợt này, còn câu “tốt nhất” là
nhận định cần điều kiện so sánh; bài này giữ lại các thành phần đã đọc README hoặc nguồn chính.

Danh sách chỉ là ví dụ để hình dung từng tầng, không phải khuyến nghị chọn công cụ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-open-source-ai-stack.md): năm tầng và ví dụ.
- [Streamlit](https://github.com/streamlit/streamlit), [FastAPI](https://github.com/tiangolo/fastapi), [Metaflow](https://github.com/Netflix/metaflow), [Ollama](https://github.com/ollama/ollama): README mô tả vai trò.
- [pgvector](https://github.com/pgvector/pgvector): phần mở rộng Postgres. [Faiss](https://github.com/facebookresearch/faiss): thư viện tìm kiếm vector.
- [Milvus](https://github.com/milvus-io/milvus) và [Weaviate](https://github.com/weaviate/weaviate): cơ sở dữ liệu vector.
- [OSI — giấy phép Llama không phải mã nguồn mở](https://opensource.org/blog/metas-llama-2-license-is-not-open-source) và định nghĩa Open Source AI 1.0 (10/2024): đối chiếu qua trích đoạn tìm kiếm; trang OSI không mở được.

Đã đọc nguồn ngày 2026-10-13. Bài viết và hình được thiết kế độc lập.

# Ngăn xếp AI mã nguồn mở

**Dựng một ứng dụng AI là ghép nhiều tầng, và mỗi tầng có nhiều lựa chọn công khai ở các mức “mở” khác nhau.**
Ở mỗi tầng hãy hỏi hai điều: nó giải quyết việc gì, và giấy phép cho phép bạn làm gì.

![Năm thẻ nối nhau từ trên xuống. 1 Giao diện: Streamlit, Next.js. 2 Backend và gọi mô hình: FastAPI, Metaflow, Ollama. 3 Embedding và RAG: biến văn bản thành vector, tìm đoạn liên quan cho prompt. 4 Lưu trữ và truy xuất: Postgres với pgvector, Milvus, Weaviate; Faiss là thư viện tìm kiếm vector. 5 Mô hình: Llama, Mistral, Qwen, Phi, Gemma, mỗi họ có giấy phép riêng. Thẻ cuối nhắc rằng mở có nhiều mức.](../../diagrams/sd-03-005-main.svg)

## Đọc hình

**1 · Giao diện.** Nơi người dùng thao tác. Streamlit dựng ứng dụng dữ liệu bằng Python; Next.js là framework web.

**2 · Backend và gọi mô hình.** FastAPI dựng API cho các lời gọi; Metaflow, khởi nguồn từ Netflix,
quản lý quy trình AI/ML; Ollama giúp chạy và gọi mô hình.

**3 · Embedding và RAG.** Embedding biến văn bản thành vector. RAG tìm các đoạn liên quan rồi đưa chúng vào prompt
để mô hình trả lời dựa trên dữ liệu của bạn.

**4 · Lưu trữ và truy xuất.** Cần nơi giữ vector và tìm gần đúng. pgvector thêm tìm kiếm vector vào Postgres;
Milvus và Weaviate là cơ sở dữ liệu vector. Faiss là thư viện tìm kiếm tương tự, không tự là máy chủ cơ sở dữ liệu.

**5 · Mô hình.** Llama, Mistral, Qwen, Phi, Gemma là các họ mô hình mà bài nguồn nêu làm lựa chọn thay cho mô hình đóng.
Mỗi họ có giấy phép riêng; bài này chưa đọc điều khoản của từng họ.

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
nhận định cần điều kiện so sánh; bài này giữ lại các thành phần đã đọc README. Tên Next.js và các họ mô hình ở tầng 5 lấy từ bài nguồn, chưa được đối chiếu.

Danh sách chỉ là ví dụ để hình dung từng tầng, không phải khuyến nghị chọn công cụ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-open-source-ai-stack.md): năm tầng và ví dụ.
- [Streamlit](https://github.com/streamlit/streamlit/blob/5557b5ac644375e8b9d2c4d6f1449b3e08fa2993/README.md), [FastAPI](https://github.com/tiangolo/fastapi/blob/f5c6e9b4f9cadc1bf0f9a1fd672e621206b63007/README.md), [Metaflow](https://github.com/Netflix/metaflow/blob/cb63fe94d6ae223ece6776edd567a59cb40eea0b/README.md), [Ollama](https://github.com/ollama/ollama/blob/665f9e074c99fe5abd57f6c2c2948dd60543a637/README.md): README mô tả vai trò.
- [pgvector](https://github.com/pgvector/pgvector/blob/f37c13f68b57d2c3472b2214fbcff699d6d34876/README.md): phần mở rộng Postgres. [Faiss](https://github.com/facebookresearch/faiss/blob/1a9ddc60d2201c9a44dfca3acead6ee38fbe21dc/README.md): thư viện tìm kiếm vector.
- [Milvus](https://github.com/milvus-io/milvus/blob/b48661d3162164c7f2d10147ca2a217b52827b6f/README.md) và [Weaviate](https://github.com/weaviate/weaviate/blob/350ad1194906242d23fa29f5994cd370356de286/README.md): cơ sở dữ liệu vector.
- [OSI — giấy phép Llama không phải mã nguồn mở](https://opensource.org/blog/metas-llama-2-license-is-not-open-source) và định nghĩa Open Source AI 1.0 (10/2024): đối chiếu qua trích đoạn tìm kiếm; trang OSI không mở được.

Đã đọc nguồn ngày 2026-10-13. Bài viết và hình được thiết kế độc lập.

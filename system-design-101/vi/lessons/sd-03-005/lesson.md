# Ngăn xếp AI mã nguồn mở: chọn công cụ bằng giấy phép và bằng phép đo

**Dựng một ứng dụng AI là ghép nhiều tầng công cụ công khai, nhưng "mở" có nhiều mức và "tìm kiếm vector" có thể sót kết quả.** Hai việc nên làm trước khi chọn: đọc tệp giấy phép của từng công cụ và mô hình, và đo xem tầng tìm kiếm có tìm đúng trên dữ liệu của bạn không.

![Bốn khung dọc. Một: trong chín kho phần mềm đã đọc giấy phép, tám kho dùng một giấy phép rộng rãi (Apache-2.0, MIT hoặc giấy phép của PostgreSQL), riêng Weaviate vừa BSD-3-Clause vừa có thư mục dưới giấy phép doanh nghiệp. Hai: mô hình Llama có giấy phép cộng đồng riêng, với điều khoản thương mại, yêu cầu ghi nguồn và chính sách sử dụng. Ba: tìm kiếm vector xấp xỉ nhanh hơn tìm chính xác nhưng có thể sót; cùng cấu hình, trên dữ liệu có cụm rõ độ phủ gần 1, trên dữ liệu không có cấu trúc chỉ từ 0,04 đến 0,35 ở chỉ mục chia ô. Bốn: với 200 nghìn vector 64 chiều, tìm chính xác mất khoảng 2 mili giây một truy vấn, nên kho nhỏ chưa cần chỉ mục xấp xỉ. Kết luận: đọc giấy phép, rồi đo trên dữ liệu của bạn.](../../diagrams/sd-03-005-main.svg)

## Từ viết tắt

- **AI** (Artificial Intelligence) — trí tuệ nhân tạo: các hệ thống máy tính làm những việc thường cần trí thông minh của con người, như hiểu ngôn ngữ hay nhận ra hình ảnh.
- **RAG** (Retrieval-Augmented Generation) — tạo sinh tăng cường truy xuất: tìm các đoạn tài liệu liên quan rồi đưa vào câu lệnh để mô hình trả lời dựa trên đó.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách để một chương trình gọi chức năng hoặc lấy dữ liệu của chương trình khác theo quy ước đã định; FastAPI là một công cụ dựng loại giao diện này.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; PostgreSQL là một hệ cơ sở dữ liệu dùng nó.
- **LLM** (Large Language Model) — mô hình ngôn ngữ lớn: mô hình học từ lượng văn bản rất lớn để hiểu và viết ra ngôn ngữ, là nền của các công cụ trong bài.
- **OSI** (Open Source Initiative) — tổ chức giữ định nghĩa chính thức của "mã nguồn mở".
- **MIT** (Massachusetts Institute of Technology) — tên một giấy phép phần mềm ngắn, rộng rãi: cho dùng, sửa và phân phối miễn phí với điều kiện giữ nguyên thông báo bản quyền.
- **BSD** (Berkeley Software Distribution) — họ giấy phép rộng rãi bắt nguồn từ Đại học California ở Berkeley; BSD-3-Clause là bản có ba điều khoản.
- **IVF** (InVerted File) — tệp đảo: chỉ mục chia các vector vào nhiều ô rồi chỉ tìm ở vài ô gần câu hỏi nhất.
- **HNSW** (Hierarchical Navigable Small World) — đồ thị nhỏ điều hướng phân tầng: chỉ mục nối các vector thành đồ thị và đi theo cạnh để tới vector gần.

## Đọc hình

Các phép đo dưới đây chạy ngày 2026-10-16 trên một máy bốn nhân (mỗi truy vấn dùng một luồng); các tệp giấy phép đọc cùng ngày từ nhánh chính của từng kho, không ghim phiên bản.

1. **"Mở" ở tầng công cụ: phần lớn rộng rãi, có ngoại lệ.** Đọc tệp giấy phép của chín kho phần mềm trong ngăn xếp: Streamlit, Metaflow và Milvus dùng Apache-2.0; FastAPI, Ollama, Faiss và Next.js dùng MIT; pgvector dùng giấy phép kiểu PostgreSQL. Weaviate khác: tệp giấy phép của nó nói mã nguồn trong kho phần lớn theo BSD-3-Clause, nhưng thư mục `wl` thuộc về một giấy phép doanh nghiệp riêng và các tính năng doanh nghiệp bật bằng khóa giấy phép. Nên hỏi không chỉ "công cụ này có mã nguồn mở không" mà "tính năng tôi cần nằm ở phần nào của kho".
2. **Mô hình: giấy phép riêng cho từng họ.** Đọc giấy phép cộng đồng của Llama 3.3: nó cấp quyền dùng, sao chép, sửa và phân phối miễn phí, nhưng kèm điều kiện. Nếu sản phẩm của bạn (hoặc công ty liên kết) có hơn 700 triệu người dùng hoạt động hàng tháng vào ngày phát hành phiên bản, bạn phải xin phép Meta và chưa được dùng cho tới khi được cấp. Khi phân phối còn phải kèm bản giấy phép, ghi "Built with Llama", đặt "Llama" ở đầu tên mô hình bạn tạo ra từ nó, và tuân theo chính sách sử dụng chấp nhận được. Những điều khoản này làm nó khác Apache-2.0 hay MIT. Theo OSI (qua trích đoạn tìm kiếm, trang chưa mở được), giấy phép của Llama 2 không phải giấy phép mã nguồn mở; bài không kiểm bản 3.3 theo tiêu chí đó. Bài chỉ đọc giấy phép của Llama; Mistral, Qwen, Phi và Gemma có giấy phép riêng chưa được đối chiếu ở đây.
3. **Tìm kiếm vector xấp xỉ: nhanh hơn, nhưng có thể sót.** RAG cần tìm các đoạn gần nghĩa nhất với câu hỏi. Chạy Faiss với 200.000 vector 64 chiều, 1.000 truy vấn, lấy 10 gần nhất, so với tìm chính xác (`IndexFlatL2`, 2,10 mili giây một truy vấn). Chỉ mục chia ô (IVF, 1.024 ô) với `nprobe` = 1 chạy nhanh hơn tìm chính xác hơn 100 lần nhưng chỉ thấy 94,3% kết quả đúng; `nprobe` = 8 thấy đủ 100% và vẫn nhanh hơn khoảng 30 đến 40 lần. Chỉ mục đồ thị (HNSW) với `efSearch` = 32 thấy 99,8%, nhanh hơn khoảng 40 đến 60 lần. Độ phủ giống hệt qua các lần chạy lại, còn tỉ lệ tốc độ dao động theo lần chạy và theo máy, nên bài chỉ nêu khoảng. Vậy là nhanh hơn nhiều chục lần mà gần như không sót, trên dữ liệu này.
4. **Nhưng độ phủ phụ thuộc dữ liệu.** Cùng các cấu hình trên, nếu dữ liệu không có cấu trúc (vector ngẫu nhiên cùng phân phối, không có cụm), IVF với `nprobe` = 1 chỉ thấy 3,6% kết quả đúng, `nprobe` = 8 thấy 15,3%, `nprobe` = 32 thấy 35,1%; HNSW với `efSearch` = 32 thấy 50,9% và `efSearch` = 128 thấy 81,7% (khi đó nhanh hơn tìm chính xác chỉ vài lần). Cả hai bộ dữ liệu đều là dữ liệu giả; vector nhúng thật nằm đâu đó giữa hai thái cực. Không thể suy độ phủ từ tên chỉ mục, phải đo trên dữ liệu của bạn.
5. **Kho nhỏ thì có thể chưa cần chỉ mục xấp xỉ.** Tìm chính xác trên 200.000 vector 64 chiều chỉ mất khoảng 2 mili giây mỗi truy vấn với một luồng. Với kho cỡ này, một bảng có cột vector hay một mảng trong bộ nhớ có thể đủ, và bạn tránh được việc phải chỉnh tham số chỉ mục. Con số này không áp dụng cho vector nhiều chiều hơn hay kho lớn hơn nhiều.

## Giới hạn cần nhớ

Phần giấy phép chỉ nói cái tệp giấy phép viết, không phải tư vấn pháp lý; điều khoản có thể đổi giữa các phiên bản và các thư mục. Phần đo dùng dữ liệu tổng hợp, một cấu hình phần cứng, một thư viện và phiên bản Faiss 1.15.1; thời gian và độ phủ trên dữ liệu thật của bạn sẽ khác. Bài không so sánh Milvus, Weaviate hay pgvector với nhau, không thử một mô hình nhúng thật và không đo chất lượng câu trả lời cuối của một hệ RAG.

## Nhìn hình trả lời

Bạn có 50.000 đoạn văn đã chuyển thành vector và đang cân nhắc dựng một cơ sở dữ liệu vector riêng. Theo hình, bạn nên làm gì trước?

<details>
<summary>Xem đáp án</summary>

Thử tìm chính xác (so sánh với mọi vector) trên dữ liệu thật và đo thời gian một truy vấn; với 200.000 vector 64 chiều trên máy thử, chỉ mất khoảng 2 mili giây. Nếu đủ nhanh cho tải của bạn, chưa cần chỉ mục xấp xỉ. Nếu cần chỉ mục xấp xỉ, đo độ phủ so với kết quả chính xác trên chính dữ liệu của bạn, vì độ phủ của cùng một cấu hình khác nhau rất nhiều giữa dữ liệu có cụm rõ và dữ liệu không có cấu trúc. Rồi đọc giấy phép của công cụ bạn chọn, kể cả phần nào của kho có giấy phép khác.

</details>

<details>
<summary>Xem sâu hơn: cách tự đo, và điều bài đã bỏ so với nguồn</summary>

Đoạn mã đo độ phủ (cần `pip install numpy faiss-cpu`; các con số trong bài chạy với `numpy` 2.5.4 và `faiss-cpu` 1.15.1):

```python
import time, numpy as np, faiss
faiss.omp_set_num_threads(1)
rng = np.random.default_rng(7)
n, d, nq, k = 200_000, 64, 1000, 10
xb = rng.normal(size=(n, d)).astype("float32")   # dữ liệu không có cấu trúc
xq = rng.normal(size=(nq, d)).astype("float32")
flat = faiss.IndexFlatL2(d); flat.add(xb)
_, truth = flat.search(xq, k)
ivf = faiss.IndexIVFFlat(faiss.IndexFlatL2(d), d, 1024)
ivf.train(xb); ivf.add(xb); ivf.nprobe = 8
_, found = ivf.search(xq, k)
print(np.mean([len(set(found[i]) & set(truth[i])) / k for i in range(nq)]))
```

Đoạn mã in ra khoảng 0,15 (lần thử cho 0,1536; con số dao động nhẹ theo hạt giống ngẫu nhiên và phiên bản).

Với dữ liệu có cấu trúc, bộ thử dùng 1.000 tâm cụm ngẫu nhiên và mỗi vector là một tâm cộng nhiễu chuẩn; xây chỉ mục IVF mất khoảng 12 giây và HNSW khoảng 21 giây trên dữ liệu có cụm (khoảng 44 giây trên dữ liệu không cấu trúc). Số đo là một lần chạy trên một máy, thời gian một truy vấn là trung bình trên 1.000 truy vấn.

Bài nguồn còn nêu Vercel, Nomic, JinaAI, "Cognito", LLMWare, Hugging Face, Langchain, và nhận định rằng các công cụ tốt nhất đều là mã nguồn mở. Những mục đó chưa được đối chiếu trong đợt này, còn câu "tốt nhất" cần điều kiện so sánh. Danh sách trong bài chỉ là ví dụ để hình dung từng tầng (giao diện, backend và gọi mô hình, embedding và RAG, lưu trữ và truy xuất, mô hình), không phải khuyến nghị chọn công cụ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-open-source-ai-stack.md): năm tầng và các ví dụ công cụ.
- Tệp giấy phép của các kho, đọc ngày 2026-10-16: [Streamlit](https://github.com/streamlit/streamlit/blob/develop/LICENSE), [FastAPI](https://github.com/fastapi/fastapi/blob/master/LICENSE), [Metaflow](https://github.com/Netflix/metaflow/blob/master/LICENSE), [Ollama](https://github.com/ollama/ollama/blob/main/LICENSE), [pgvector](https://github.com/pgvector/pgvector/blob/master/LICENSE), [Faiss](https://github.com/facebookresearch/faiss/blob/main/LICENSE), [Milvus](https://github.com/milvus-io/milvus/blob/master/LICENSE), [Weaviate](https://github.com/weaviate/weaviate/blob/main/LICENSE), [Next.js](https://github.com/vercel/next.js/blob/canary/license.md).
- [Giấy phép cộng đồng Llama 3.3](https://github.com/meta-llama/llama-models/blob/main/models/llama3_3/LICENSE): điều khoản người dùng hoạt động hàng tháng, ghi nguồn, đặt tên và chính sách sử dụng.
- [OSI — giấy phép Llama không phải mã nguồn mở](https://opensource.org/blog/metas-llama-2-license-is-not-open-source) và định nghĩa Open Source AI 1.0 (10/2024): đối chiếu qua trích đoạn tìm kiếm; trang OSI không mở được. Trang này nói về Llama 2; bài không đọc phiên bản mới.

Các phép đo Faiss chạy trên máy biên soạn ngày 2026-10-16. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

# Dòng thời gian dẫn tới ChatGPT

**ChatGPT không xuất hiện từ hư không.** Nó là chỗ gặp nhau của ba thứ: kiến trúc Transformer,
tiền huấn luyện ở quy mô lớn và việc dạy mô hình làm theo chỉ dẫn bằng phản hồi của con người.

![Tám thẻ nối nhau theo chiều dọc: thập niên 1950 hệ luật viết tay; thập niên 1980 học máy trên dữ liệu nhỏ; 1990 đến 2010 mạng nơ-ron CNN và RNN; 2014 GAN; 2017 Transformer; 2018 đến 2020 GPT, GPT-3 có 175 tỷ tham số; tháng 3 năm 2022 InstructGPT; ngày 30 tháng 11 năm 2022 ChatGPT ra mắt bản xem thử. Ghi chú: các mốc đầu là xu hướng, không phải ranh giới chính xác.](../../diagrams/sd-03-003-main.svg)

## Từ viết tắt

- **CNN** (Convolutional Neural Network) — mạng nơ-ron tích chập: loại mạng nơ-ron đặc biệt mạnh với ảnh.
- **RNN** (Recurrent Neural Network) — mạng nơ-ron hồi quy: loại mạng nơ-ron xử lý dữ liệu theo chuỗi, như văn bản.
- **GAN** (Generative Adversarial Network) — mạng đối sinh: hai mạng nơ-ron đối kháng nhau, một mạng sinh mẫu và một mạng phân biệt thật giả.
- **GPT** (Generative Pretrained Transformer) — tên một dòng mô hình ngôn ngữ được huấn luyện sẵn trên lượng văn bản rất lớn rồi mới dùng cho việc cụ thể.

## Đọc hình

**Trước 2017.** Hệ luật viết tay nhường chỗ cho học máy từ dữ liệu, rồi tới mạng nơ-ron: CNN mạnh với ảnh,
RNN xử lý chuỗi như văn bản. **GAN (2014)** cho hai mạng đối kháng nhau: một mạng sinh mẫu, một mạng
phân biệt mẫu thật với mẫu sinh ra.

**2017 — Transformer.** Bài “Attention Is All You Need” bỏ phép lặp theo chuỗi và chỉ dùng cơ chế attention.
Các tác giả báo cáo mô hình dễ chạy song song hơn nên huấn luyện nhanh hơn.

**2018–2020 — tiền huấn luyện lớn.** Dòng GPT huấn luyện mô hình ngôn ngữ trên lượng văn bản rất lớn.
GPT-3 (2020) có 175 tỷ tham số và làm tác vụ theo mô tả trong prompt, không cập nhật trọng số.

**2022 — dạy làm theo chỉ dẫn.** InstructGPT (3/2022) tinh chỉnh mô hình bằng câu trả lời mẫu và xếp hạng của người,
rồi học tăng cường từ phản hồi đó. ChatGPT (30/11/2022) dùng phương pháp gần như vậy, mở dưới dạng bản xem thử miễn phí
để thu phản hồi.

## Giới hạn cần nhớ

Dòng thời gian là một lát cắt do người biên tập chọn: các thời kỳ chồng lên nhau, và mỗi mốc gồm nhiều công trình.
Đừng đọc “2017” như thể một bài báo đã tạo ra ChatGPT; nó là một mắt xích trong chuỗi.

## Nhìn hình trả lời

Điều gì phân biệt InstructGPT với một mô hình chỉ tiền huấn luyện như GPT-3?

<details>
<summary>Xem đáp án</summary>

InstructGPT được tinh chỉnh thêm bằng câu trả lời mẫu và phản hồi của con người để làm theo chỉ dẫn.
Bài báo GPT-3 mô tả việc dùng mô hình qua prompt, không tinh chỉnh.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn xếp GAN vào giai đoạn 1990–2000; bài báo GAN được công bố năm 2014 nên hình đặt nó ở 2014.

Bài nguồn dừng ở “2018 đến nay”. Hình tách ra ba mốc có thể đối chiếu: GPT-3, InstructGPT và ngày ra mắt
bản xem thử của ChatGPT. Các mốc đầu (1950, 1980, 1990–2010) là mô tả xu hướng chung, chưa gắn với một công trình cụ thể.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/chatgpt-timeline.md): các giai đoạn.
- [Vaswani và cộng sự — Attention Is All You Need (2017)](https://research.google/pubs/attention-is-all-you-need/): Transformer chỉ dùng attention, dễ song song hơn.
- [Goodfellow và cộng sự — Generative Adversarial Nets (NIPS 2014)](https://proceedings.neurips.cc/paper/5423-generative-adversarial-nets): bộ sinh và bộ phân biệt.
- [Brown và cộng sự — Language Models are Few-Shot Learners (2020)](https://arxiv.org/abs/2005.14165): GPT-3, 175 tỷ tham số, dùng qua prompt.
- [Ouyang và cộng sự — InstructGPT (arXiv 2203.02155)](https://arxiv.org/abs/2203.02155): tinh chỉnh bằng minh họa, xếp hạng và học tăng cường từ phản hồi.
- [OpenAI — Introducing ChatGPT](https://openai.com/blog/chatgpt): bản xem thử, cùng phương pháp với InstructGPT.

Đã đọc nguồn ngày 2026-10-13. arxiv.org, openai.com và các trang bài báo không mở được trong môi trường biên soạn;
nội dung đối chiếu qua trích đoạn tìm kiếm. Ngày 30/11/2022 lấy từ bài viết của bên thứ ba, chưa từ trang OpenAI.
Bài viết và hình được thiết kế độc lập.

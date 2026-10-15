# ChatGPT hoạt động thế nào?

**Hai việc khác nhau xảy ra ở hai thời điểm.** Trước khi bạn dùng, mô hình được huấn luyện qua nhiều giai đoạn.
Khi bạn gửi prompt, mô hình sinh câu trả lời từng token một.

![Hai nhóm xếp dọc. A, huấn luyện: bước 1 tiền huấn luyện dự đoán token kế tiếp trên lượng văn bản rất lớn; bước 2 tinh chỉnh có giám sát từ câu trả lời mẫu do người viết; bước 3 mô hình thưởng học từ xếp hạng của người, rồi mô hình được tối ưu theo điểm thưởng bằng học tăng cường. B, khi bạn gửi prompt: bước 4 chia văn bản thành token; bước 5 sinh từng token một, lặp tới khi xong; bước 6 hiển thị câu trả lời. Thẻ cuối nhắc chi tiết kiểm duyệt và hạ tầng của ChatGPT chưa được công bố đầy đủ.](../../diagrams/sd-03-008-main.svg)

## Từ viết tắt

- **RL** (Reinforcement Learning) — học tăng cường: mô hình thử nhiều cách, được thưởng khi làm tốt và dần chọn cách tốt hơn.
- **PPO** (Proximal Policy Optimization) — một thuật toán học tăng cường, dùng để tinh chỉnh mô hình theo điểm thưởng.
- **GPT** (Generative Pretrained Transformer) — tên một dòng mô hình ngôn ngữ được huấn luyện sẵn trên lượng văn bản rất lớn rồi mới dùng cho việc cụ thể.
- **AI** (Artificial Intelligence) — trí tuệ nhân tạo: các hệ thống máy tính làm những việc thường cần trí thông minh của con người, như hiểu ngôn ngữ hay nhận ra hình ảnh.

## Đọc hình

**A · Huấn luyện.** Mô tả công khai đầy đủ nhất là của InstructGPT, họ hàng gần của ChatGPT.

1. **Tiền huấn luyện.** Mô hình học dự đoán token kế tiếp trên lượng văn bản rất lớn. Sau bước này nó viết tiếp văn bản
   khá tốt, nhưng chưa chắc làm theo yêu cầu.
2. **Tinh chỉnh có giám sát.** Người viết câu trả lời mẫu cho các yêu cầu; mô hình học bắt chước chúng.
3. **Mô hình thưởng và RL.** Người xếp hạng nhiều câu trả lời của mô hình. Từ đó huấn luyện một mô hình thưởng, rồi dùng
   học tăng cường để mô hình cho ra câu trả lời được điểm cao hơn.

**B · Trả lời một prompt.** Văn bản của bạn được chia thành token. Mô hình sinh từng token: mỗi bước chọn token
kế tiếp dựa trên prompt và các token đã sinh, lặp lại tới khi xong, rồi ghép thành câu trả lời.

## Giới hạn cần nhớ

Mô hình sinh văn bản có vẻ hợp lý theo những gì đã học; nó không tự kiểm từng câu với một nguồn sự thật,
nên có thể nói sai mà vẫn tự tin. Bước kiểm duyệt đầu vào và đầu ra mà nhiều sơ đồ vẽ quanh ChatGPT cũng không được
OpenAI mô tả đầy đủ, nên hình này không vẽ nó như một cơ chế đã xác nhận.

## Nhìn hình trả lời

Sau bước tiền huấn luyện, mô hình chưa làm theo yêu cầu tốt. Hai bước nào của hình A khắc phục điều đó?

<details>
<summary>Xem đáp án</summary>

Bước 2 (tinh chỉnh có giám sát bằng câu trả lời mẫu) và bước 3 (học từ xếp hạng của người, rồi tối ưu bằng học tăng cường).

</details>

<details>
<summary>Xem sâu hơn: từ InstructGPT tới ChatGPT</summary>

Bài báo InstructGPT mô tả ba bước: tinh chỉnh bằng minh họa của người, thu xếp hạng các đầu ra để huấn luyện mô hình thưởng,
rồi tối ưu bằng học tăng cường với thuật toán PPO. Các tác giả báo cáo người đánh giá ưa đầu ra của mô hình 1,3 tỷ tham số
được tinh chỉnh theo cách này hơn đầu ra của GPT-3 175 tỷ tham số.

OpenAI nói ChatGPT dùng phương pháp tương tự InstructGPT, với khác biệt nhỏ ở cách thu dữ liệu, và bắt đầu từ một mô hình
thuộc dòng GPT-3.5. Họ không công bố đầy đủ chi tiết về các phiên bản sau, nên đừng suy từ bài này ra kiến trúc hiện tại
của sản phẩm.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-chatgpt-work.md): các giai đoạn huấn luyện và luồng kiểm duyệt do bài nguồn phỏng đoán.
- [Ouyang và cộng sự — InstructGPT (arXiv 2203.02155)](https://arxiv.org/abs/2203.02155): ba bước huấn luyện. Trang không mở được; nội dung đối chiếu qua trích đoạn tìm kiếm, riêng tên PPO qua một bản tóm tắt thứ cấp.
- [OpenAI — Introducing ChatGPT](https://openai.com/blog/chatgpt): ChatGPT dùng phương pháp tương tự InstructGPT. Đối chiếu qua trích đoạn tìm kiếm.

Đã đọc nguồn ngày 2026-10-13. Bài viết và hình được thiết kế độc lập. Bài nguồn tự ghi rằng một số phần của sơ đồ có thể không chính xác
vì OpenAI chưa công bố đủ chi tiết; luồng “kiểm duyệt đầu vào → mô hình → kiểm duyệt đầu ra → câu trả lời mẫu” của nó
vì thế không được đưa vào hình chính.

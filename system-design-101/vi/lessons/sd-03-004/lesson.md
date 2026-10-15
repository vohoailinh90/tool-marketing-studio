# DeepSeek trong một trang

**Một con số chi phí chỉ có nghĩa khi biết nó đo cái gì.** Quanh DeepSeek lưu hành nhiều số liệu,
và không ít số trộn lẫn hai mô hình khác nhau: V3 và R1.

![Ba nhóm xếp dọc. Mô hình nền V3-Base: kiến trúc MoE 671 tỷ tham số tổng, 37 tỷ kích hoạt mỗi token, 14,8 nghìn tỷ token; con số khoảng 5,6 triệu USD là của V3, tính từ 2,788 triệu giờ GPU H800 nhân 2 USD giả định thuê, chỉ lần huấn luyện chính thức. Hai cách dạy suy luận: R1-Zero dùng học tăng cường trực tiếp trên mô hình nền; R1 cũng từ V3-Base, thêm vài nghìn mẫu khởi động và nhiều giai đoạn, RL dùng GRPO. Nhóm cuối đánh dấu hai con số của bài nguồn chưa đủ căn cứ.](../../diagrams/sd-03-004-main.svg)

## Từ viết tắt

- **USD** (United States Dollar) — đô la Mỹ: đơn vị tiền dùng trong con số chi phí huấn luyện của bài.
- **GPU** (Graphics Processing Unit) — bộ xử lý đồ họa: chip tính toán song song, thường dùng để huấn luyện mô hình học máy.
- **MoE** (Mixture of Experts) — hỗn hợp chuyên gia: kiến trúc chia mô hình thành nhiều khối chuyên gia, mỗi token chỉ kích hoạt một phần trong số đó.
- **RL** (Reinforcement Learning) — học tăng cường: mô hình thử nhiều cách, được thưởng khi làm tốt và dần chọn cách tốt hơn.
- **GRPO** (Group Relative Policy Optimization) — một thuật toán học tăng cường; R1 dùng nó ở bước học tăng cường, chi tiết cách tính nằm trong bài.
- **SFT** (Supervised Fine-Tuning) — tinh chỉnh có giám sát: dạy mô hình bằng các mẫu đã có đáp án cho sẵn.
- **GPT** (Generative Pretrained Transformer) — tên một dòng mô hình ngôn ngữ được huấn luyện sẵn trên lượng văn bản rất lớn rồi mới dùng cho việc cụ thể.
- **MIT** (Massachusetts Institute of Technology) — giấy phép MIT: giấy phép phần mềm ngắn và thoáng, cho phép dùng, sửa và phân phối lại; tên gọi theo viện MIT.

## Đọc hình

**Mô hình nền V3.** DeepSeek-V3 dùng kiến trúc Mixture-of-Experts (MoE): 671 tỷ tham số tổng cộng,
nhưng mỗi token chỉ kích hoạt 37 tỷ. Tiền huấn luyện dùng 14,8 nghìn tỷ token.

**Khoảng 5,6 triệu USD.** Đây là 2,788 triệu giờ GPU H800 nhân với giá thuê giả định 2 USD mỗi giờ,
của quá trình huấn luyện V3. Nó là ước tính chi phí thuê cho lần huấn luyện chính thức,
không phải tổng chi phí nghiên cứu, và không phải chi phí của R1.

**R1-Zero và R1.** Cả hai bắt đầu từ V3-Base. R1-Zero áp dụng học tăng cường (RL) thẳng lên mô hình nền,
không có bước tinh chỉnh có giám sát (SFT) mở đầu. R1 thêm vài nghìn mẫu “khởi động” và quy trình nhiều giai đoạn,
vì R1-Zero khó đọc và hay trộn ngôn ngữ. Thuật toán RL là **GRPO**: thay mô hình đánh giá riêng bằng điểm
của cả nhóm câu trả lời được lấy mẫu cho cùng một câu hỏi.

## Giới hạn cần nhớ

“Rẻ” chỉ so sánh được khi cùng cách tính. Hai số trong bài nguồn — “2.000 GPU so với 25.000 GPU của GPT-4”
và “rẻ hơn 85–90%” — không kèm nguồn đo được hay điều kiện so sánh, nên bài này không dùng chúng.

## Nhìn hình trả lời

Con số khoảng 5,6 triệu USD thuộc mô hình nào, và nó gồm những gì?

<details>
<summary>Xem đáp án</summary>

Thuộc DeepSeek-V3, không phải R1. Nó là số giờ GPU của lần huấn luyện chính thức nhân với giá thuê giả định,
không gồm toàn bộ nghiên cứu trước đó.

</details>

<details>
<summary>Xem sâu hơn: giấy phép và chi phí của R1</summary>

Mã và trọng số của R1 được phát hành theo giấy phép MIT; các bản chưng cất nhỏ hơn kế thừa giấy phép của mô hình gốc
(Qwen hoặc Llama). Mã của V3 theo MIT, còn trọng số V3 theo một Model License riêng cho phép dùng thương mại.

Bài báo R1 đăng trên Nature (9/2025) được các hãng tin dẫn là nêu khoảng 294.000 USD cho phần huấn luyện R1,
tách khỏi chi phí mô hình nền. Con số này chỉ có qua trích dẫn của báo chí trong đợt biên soạn này; chưa mở được bài báo.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/deepseek-1-pager.md): các số liệu được đối chiếu ở trên.
- [DeepSeek-V3 — README](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788e4a3a731f7567338ed15d3ec549ce03b/README.md): 671B/37B, 14,8T token, 2,788M giờ GPU H800, giấy phép.
- [DeepSeek-V3 — báo cáo kỹ thuật](https://arxiv.org/abs/2412.19437): bảng chi phí 2 USD mỗi giờ GPU. Trang không mở được; nội dung đối chiếu qua trích đoạn tìm kiếm.
- [DeepSeek-R1 — README](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561f1d51c84a21b2190626b21116d5c68bb/README.md): R1 huấn luyện từ V3-Base, giấy phép MIT.
- [DeepSeek-R1 — báo cáo kỹ thuật (PDF trong repo)](https://github.com/deepseek-ai/DeepSeek-R1/blob/0cf78561f1d51c84a21b2190626b21116d5c68bb/DeepSeek_R1.pdf): R1-Zero không SFT, mẫu khởi động, nhiều giai đoạn, GRPO.

Đã đọc nguồn ngày 2026-10-13. Bài viết và hình được thiết kế độc lập. Không giữ các tuyên bố của bài nguồn về
52 ngôn ngữ, số GPU của GPT-4, mức rẻ hơn 85–90% và “ứng dụng miễn phí số 1” vì chưa có nguồn kiểm chứng;
bài nguồn cũng gán chi phí 6 triệu USD cho R1 trong khi con số đó thuộc lần huấn luyện V3.

# Làm tốt phỏng vấn thiết kế hệ thống: bảy bước

**Phỏng vấn thiết kế hệ thống là một cuộc trò chuyện về đánh đổi, không phải bài thi có đáp án.** Một khung các bước giúp bạn
không bỏ sót điều quan trọng và luôn biết mình đang ở đâu.

![Bảy thẻ nối nhau từ trên xuống, mỗi thẻ là một câu hỏi. 1 Yêu cầu: hệ thống phải làm gì, tốt đến mức nào. 2 Quy mô: bao nhiêu người dùng, dữ liệu, lưu lượng. 3 Thiết kế cấp cao: các thành phần nối nhau thế nào. 4 Dữ liệu: lưu gì, bằng loại cơ sở dữ liệu nào. 5 Giao diện: API hay sự kiện giữa các phần. 6 Mở rộng và hiệu năng: cache, chỉ mục, chia nhỏ, sao chép. 7 Độ tin cậy: điểm lỗi đơn nằm ở đâu. Ghi chú: bản đồ, không phải kịch bản, thứ tự có thể đổi.](../../diagrams/sd-05-004-main.svg)

## Đọc hình

**1 · Yêu cầu.** Hỏi hệ thống phải làm những gì (chức năng) và phải tốt đến đâu (phi chức năng: độ sẵn sàng, độ trễ, khối lượng dữ liệu).

**2 · Quy mô.** Ước lượng số người dùng, lưu lượng, dung lượng lưu trữ, nhu cầu tính toán và mạng. Con số chỉ cần đủ để chọn hướng.

**3 · Thiết kế cấp cao.** Vẽ khối đơn giản: máy khách, máy chủ, bộ cân bằng tải, cơ sở dữ liệu… và dòng dữ liệu giữa chúng.

**4 · Dữ liệu.** Mô hình hóa dữ liệu, chọn loại cơ sở dữ liệu, rồi tới lược đồ.

**5 · Giao diện.** Các API hoặc sự kiện giữa các thành phần; chọn cách giao tiếp như REST, GraphQL, gRPC hay hướng sự kiện.

**6 · Mở rộng và hiệu năng.** Nêu kỹ thuật cho tải lớn và độ trễ thấp: mở rộng dọc/ngang, cache, chỉ mục, chia dữ liệu, sao chép, CDN.

**7 · Độ tin cậy.** Tìm điểm lỗi đơn và giảm tác động của chúng.

## Giới hạn cần nhớ

Bảy bước là bản đồ, không phải kịch bản. Người phỏng vấn có thể muốn đào sâu một bước, hoặc nhảy sang bước khác trước. Các con số ở bước 2
là giả định do bạn đặt ra: hãy nói to chúng và sẵn sàng đổi khi người phỏng vấn sửa.

## Nhìn hình trả lời

Bạn đã vẽ xong sơ đồ khối nhưng chưa biết hệ thống có bao nhiêu người dùng và cần nhanh đến mức nào. Bạn bỏ sót bước nào?

<details>
<summary>Xem đáp án</summary>

Bước 1 (làm rõ yêu cầu) và bước 2 (ước lượng quy mô). Không có chúng, bạn chưa có căn cứ để chọn cơ sở dữ liệu, cache hay cách chia nhỏ.

</details>

<details>
<summary>Xem sâu hơn: một khung khác</summary>

System Design Primer, một kho tài liệu ôn tập trên GitHub, đề xuất bốn bước: nêu ca sử dụng, ràng buộc và giả định; vẽ thiết kế cấp cao;
thiết kế các thành phần cốt lõi; mở rộng thiết kế. Hai cách chia khác nhau nhưng cùng trình tự: làm rõ, phác thảo, đào sâu, rồi mở rộng.

Hãy chọn một khung và luyện tới khi quen, thay vì thuộc lòng nhiều khung.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-ace-system-design-interviews-like-a-boss.md): bảy bước.
- [System Design Primer — How to approach a system design interview question](https://github.com/donnemartin/system-design-primer): khung bốn bước. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Đây là các khung kinh nghiệm chứ không phải tiêu chuẩn kỹ thuật, nên không có chuẩn nào để đối chiếu từng bước.
Bài viết và hình được thiết kế độc lập.

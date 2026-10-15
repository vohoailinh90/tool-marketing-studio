# Làm tốt phỏng vấn thiết kế hệ thống: bảy bước

**Phỏng vấn thiết kế hệ thống là một cuộc trò chuyện về đánh đổi, không phải bài thi có đáp án.** Một khung các bước giúp bạn
không bỏ sót điều quan trọng và luôn biết mình đang ở đâu.

![Bảy thẻ nối nhau từ trên xuống, mỗi thẻ là một câu hỏi. 1 Yêu cầu: hệ thống phải làm gì, tốt đến mức nào. 2 Quy mô: bao nhiêu người dùng, dữ liệu, lưu lượng. 3 Thiết kế cấp cao: các thành phần nối nhau thế nào. 4 Dữ liệu: lưu gì, bằng loại cơ sở dữ liệu nào. 5 Giao diện: API hay sự kiện giữa các phần. 6 Mở rộng và hiệu năng: chỗ nghẽn đầu tiên khi tải tăng. 7 Độ tin cậy: nếu một khối hỏng thì sao. Ghi chú: bản đồ, không phải kịch bản, thứ tự có thể đổi.](../../diagrams/sd-05-004-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: tập quy ước để các phần của hệ thống gọi chức năng của nhau.
- **CSDL** (cơ sở dữ liệu) — viết tắt tiếng Việt của "cơ sở dữ liệu" (database): nơi lưu dữ liệu có tổ chức để về sau tìm và cập nhật.

## Đọc hình

Ví dụ xuyên suốt: một dịch vụ rút gọn đường dẫn. Mỗi bước dưới đây nói bạn nên nói ra điều gì.

**1 · Yêu cầu.** “Người dùng dán một đường dẫn dài và nhận đường dẫn ngắn; đường dẫn ngắn phải mở nhanh và không được hỏng.”
Tách điều hệ thống làm được khỏi mức chất lượng nó phải đạt.

**2 · Quy mô.** Đặt giả định rõ ràng, như số đường dẫn tạo mỗi ngày và tỷ lệ lượt mở so với lượt tạo, rồi suy ra dữ liệu cần giữ và lưu lượng.
Con số chỉ cần đủ để chọn hướng.

**3 · Thiết kế cấp cao.** Vẽ vài khối đủ để kể một yêu cầu đi từ người dùng tới dữ liệu rồi quay về. Chưa cần chi tiết.

**4 · Dữ liệu.** Nêu thực thể (đường dẫn ngắn trỏ tới đường dẫn dài) và truy vấn chính (tra theo đường dẫn ngắn). Từ đó mới chọn nơi lưu.

**5 · Giao diện.** Mô tả hai thao tác “tạo” và “mở” trao đổi gì giữa các thành phần, và dạng giao tiếp hợp với từng cặp.

**6 · Mở rộng và hiệu năng.** Hỏi “khi tải tăng, chỗ nào nghẽn trước?” và nêu cách gỡ cho từng chỗ, kèm cái giá phải trả.

**7 · Độ tin cậy.** Chỉ vào từng khối và hỏi “nếu nó hỏng thì sao?”. Chỗ nào làm cả hệ thống ngừng thì cần phương án thay thế.

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

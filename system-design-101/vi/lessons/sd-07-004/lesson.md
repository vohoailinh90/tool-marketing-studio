# Web 1.0, 2.0 và 3.0: ai giữ dữ liệu, ai kiếm tiền

**Ba "phiên bản" của web khác nhau ở chỗ người dùng làm được gì với nội dung: chỉ đọc, đọc và viết, hay thêm cả sở hữu. Chỗ sở hữu quyết định ai giữ dữ liệu, và nhờ đó ai kiếm tiền từ nó.**

![Ba chặng nối nhau. Web 1.0, từ 1991 đến 2004, chỉ đọc: một danh mục trang tĩnh, nhảy từ liên kết này sang liên kết khác. Web 2.0, từ 2004 đến nay, đọc và viết: công cụ tìm kiếm, mạng xã hội, ứng dụng đề xuất; dữ liệu người dùng được các công ty lớn dùng cho quảng cáo. Web 3.0, đọc, viết và sở hữu: nội dung lưu ở IPFS và thuộc về người dùng; ứng dụng muốn dùng dữ liệu phải được cho phép và trả tiền.](../../diagrams/sd-07-004-main.svg)

## Từ viết tắt

- **IPFS** (InterPlanetary File System) — hệ thống tệp liên hành tinh: mạng lưu trữ tệp phân tán, nơi tệp được tìm theo nội dung của nó chứ không theo vị trí của một máy chủ. Nguồn chỉ nói nội dung nằm trên IPFS và thuộc về người dùng; câu giải nghĩa này là kiến thức chung của người biên soạn.

## Đọc hình

**Web 1.0, chỉ đọc (1991 đến 2004).** Internet giống một danh mục các trang tĩnh. Bạn duyệt nội dung bằng cách nhảy từ liên kết này sang liên kết khác, và không có tương tác nào với nội dung.

**Web 2.0, đọc và viết (2004 đến nay).** Internet có công cụ tìm kiếm, ứng dụng mạng xã hội và các ứng dụng chạy bằng thuật toán đề xuất. Khi người dùng tương tác, ứng dụng số hóa hành vi của họ và lưu dữ liệu lại.
Các công ty lớn dùng dữ liệu đó cho quảng cáo, và đó trở thành một trong những mô hình kinh doanh chính của Web 2.0. Vì thế người ta hay nói ứng dụng hiểu bạn hơn cả bạn bè, người thân, thậm chí chính bạn.

**Web 3.0, đọc, viết và sở hữu.** Ý tưởng này được bàn nhiều gần đây nhờ blockchain và các ứng dụng phi tập trung. Nội dung của người sáng tạo được lưu trên IPFS và *thuộc về người dùng*. Ứng dụng muốn dùng dữ liệu phải xin phép người dùng và trả tiền.
Nguồn nói rằng thay đổi về quyền sở hữu có thể dẫn tới những đổi mới lớn.

**Vì sao "ít quảng cáo"?** Tiêu đề nguồn hỏi câu này nhưng phần thân không trả lời trực tiếp. Từ chính các câu của nguồn có thể suy ra: quảng cáo ở Web 2.0 sống nhờ dữ liệu mà ứng dụng giữ; nếu dữ liệu thuộc về người dùng và ứng dụng phải xin phép, phải trả tiền, thì cách làm đó không còn nền tảng cũ. Đó là suy luận của người biên soạn.

## Giới hạn cần nhớ

Nguồn nói đây là ý tưởng *được bàn nhiều*, không phải một hệ thống đã hoàn thiện. Vì vậy "Web 3.0 không có quảng cáo" là kỳ vọng suy ra từ ý tưởng, không phải điều đã xảy ra hay đã được chứng minh. Các mốc năm của Web 1.0 và 2.0 cũng chỉ là cách chia của nguồn.
Bài không đánh giá công nghệ cụ thể nào, không so sánh với web hiện nay về tốc độ hay chi phí, và chưa đối chiếu với tài liệu của một dự án Web 3.0 hay của IPFS.

## Nhìn hình trả lời

Một ứng dụng mạng xã hội kiếm tiền bằng quảng cáo nhắm theo hành vi người dùng. Theo ý tưởng của Web 3.0, điều gì phải đổi để mô hình đó chạy khác đi?

<details>
<summary>Xem đáp án</summary>

Quyền đối với dữ liệu: nội dung và hành vi của người dùng không còn nằm trong kho của ứng dụng mà thuộc về chính họ. Ứng dụng muốn dùng dữ liệu phải được người dùng cho phép và trả tiền, nên lợi ích từ dữ liệu có thể chuyển một phần về người dùng.
Điều này vẫn là ý tưởng: bài chưa kiểm tra xem ứng dụng nào đã làm được thế, hay mô hình trả tiền cho dữ liệu sẽ vận hành ra sao.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn là một sơ đồ ba chặng kèm vài đoạn mô tả. Bài này giữ cả ba chặng và các mốc năm, thêm khung "Vì sao ít quảng cáo?" để trả lời tiêu đề, và nhấn rằng đây là ý tưởng đang bàn. Phần giải nghĩa IPFS và phần suy luận về quảng cáo là của người biên soạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-web-3.md): ba chặng của web, mô hình quảng cáo ở Web 2.0, quyền sở hữu và việc xin phép, trả tiền ở Web 3.0. Phần giải nghĩa IPFS và suy luận về quảng cáo là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

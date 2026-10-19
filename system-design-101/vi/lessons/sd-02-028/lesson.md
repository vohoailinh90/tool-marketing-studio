# API của Netflix qua bốn giai đoạn

**Theo bài nguồn, cách ứng dụng Netflix gọi phía sau đã qua bốn giai đoạn: khối nguyên, máy khách gọi thẳng microservice, lớp cổng gộp, rồi cổng liên hợp bằng GraphQL.**
Bài này đọc bốn giai đoạn đó theo một câu hỏi: mỗi bước sửa điều gì của bước trước, và để lại vấn đề gì cho bước sau.

![Bốn bước nối nhau. Khối nguyên: cả ứng dụng đóng gói và triển khai thành một khối, như một tệp Java WAR hay một ứng dụng Rails. Gọi thẳng: ứng dụng máy khách gửi yêu cầu thẳng tới từng microservice. Lớp cổng gộp: một lớp gom dữ liệu từ nhiều dịch vụ, ví dụ phim, sản xuất và diễn viên, để dựng một màn hình. Cổng liên hợp: một cổng GraphQL duy nhất lấy dữ liệu từ mọi API khác. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-028-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách ứng dụng gọi chức năng và lấy dữ liệu từ một dịch vụ.
- **WAR** (Web Application Resource) — một tệp đóng gói cả ứng dụng web Java để triển khai một lần.
- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, cho biết đây là cách để ứng dụng mô tả dữ liệu mình muốn lấy.

## Đọc hình

1. **Khối nguyên.** Ứng dụng được đóng gói và triển khai thành một khối, chẳng hạn một tệp Java WAR hay một ứng dụng Rails. Theo nguồn, phần lớn công ty khởi nghiệp bắt đầu như vậy.
2. **Gọi thẳng.** Ứng dụng máy khách gửi yêu cầu thẳng tới các microservice. Khi có hàng trăm, thậm chí hàng nghìn microservice, để máy khách thấy hết chúng là không hay.
3. **Lớp cổng gộp.** Một số việc cần dữ liệu từ nhiều dịch vụ. Ví dụ của nguồn: ứng dụng Netflix cần ba API (phim, sản xuất, diễn viên) để dựng giao diện; lớp cổng gộp lấy cả ba và trả về một lần.
4. **Cổng liên hợp.** Số lập trình viên tăng và nghiệp vụ phức tạp hơn, nên phát triển lớp gộp ngày càng khó. GraphQL Federation cho Netflix dựng một cổng GraphQL duy nhất, lấy dữ liệu từ mọi API khác.

Mỗi bước giữ lại phần đúng của bước trước: máy khách vẫn chỉ gọi một chỗ, nhưng chỗ đó do nhiều đội cùng làm thay vì một đội ôm hết.

## Giới hạn cần nhớ

Bài nguồn chỉ có một đoạn ngắn cho mỗi giai đoạn. Nó không nói mỗi giai đoạn diễn ra năm nào, không giải thích cổng liên hợp chia việc giữa các đội ra sao, và không nói vì sao gọi thẳng microservice "không hay". Lời giải thích ở phần dưới là của người biên soạn.

## Nhìn hình thử trả lời

Màn hình trang phim cần tên phim, hãng sản xuất và danh sách diễn viên, mỗi thứ do một dịch vụ giữ. Ở giai đoạn gọi thẳng và giai đoạn có cổng gộp, ứng dụng trên điện thoại phải gửi bao nhiêu yêu cầu?

<details>
<summary>Xem đáp án</summary>

Ở giai đoạn gọi thẳng, ứng dụng tự gọi ba dịch vụ, nên gửi ba yêu cầu và phải biết cả ba dịch vụ. Có cổng gộp, ứng dụng gửi một yêu cầu tới cổng; cổng gọi ba dịch vụ phía sau rồi trả về một kết quả.

</details>

<details>
<summary>Xem sâu hơn: vì sao không để máy khách gọi thẳng</summary>

- Mỗi yêu cầu đi qua mạng di động tốn thời gian; một màn hình cần nhiều yêu cầu thì chậm hơn.
- Máy khách biết tên từng dịch vụ thì đổi hay tách dịch vụ phía sau sẽ làm hỏng ứng dụng cũ đã cài.
- Cổng liên hợp để mỗi đội giữ phần dữ liệu của mình, rồi ghép lại thành một chỗ cho máy khách gọi.

Đây là kiến thức chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/evolution-of-the-netflix-api-architecture.md): bốn giai đoạn của kiến trúc API Netflix.

Đã đọc nguồn ngày 2026-10-19. Tài liệu kỹ thuật của Netflix chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

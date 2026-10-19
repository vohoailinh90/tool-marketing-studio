# Lỗi khi gọi web: khi nào thử lại, và thử lại sao cho không làm tệ thêm

**Gặp lỗi, phản xạ tự nhiên là gửi lại. Phản xạ đó đúng với một số lỗi và sai với số khác; và dù đúng, nếu mọi máy khách cùng gửi lại cùng lúc thì chính các lần gửi lại có thể giữ máy chủ ngã.** Bài này tách hai câu hỏi: lỗi nào đáng thử lại, và thử lại thế nào.

![Hai khung và một khung ghi chú. Khung một, phía trình duyệt, bốn bước: đọc mã lỗi, chờ rồi mới thử lại với thời gian chờ tăng dần, thêm ngẫu nhiên vào thời gian chờ, dừng sau vài lần. Khung hai, phía máy chủ, ba thành phần nối nhau: bộ giới hạn tốc độ, cầu dao, dịch vụ phía sau. Khung ba, thử mô phỏng 1000 máy khách thử lại: chờ cố định hoặc tăng dần không ngẫu nhiên thì 100 máy bỏ cuộc, có ngẫu nhiên thì không máy nào bỏ cuộc và số yêu cầu giảm gần một nửa.](../../diagrams/sd-11-019-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: giao thức trình duyệt dùng để nói chuyện với máy chủ web; mã lỗi trong bài (4xx, 5xx) là mã trạng thái của giao thức này.

## Đọc hình

**Phía trình duyệt.** Bước đầu là đọc mã trạng thái. Nhóm 4xx nghĩa là yêu cầu có vấn đề từ phía người gửi (sai cú pháp, thiếu quyền, không tìm thấy...), nên gửi lại y nguyên thường cho kết quả y nguyên. Nhóm 5xx nghĩa là máy chủ không làm được một yêu cầu có vẻ hợp lệ, nên gửi lại sau có thể thành công. Hai ngoại lệ đáng nhớ nằm trong nhóm 4xx: 408 (máy chủ chờ yêu cầu quá lâu) và 429 (gửi quá nhiều), nơi máy chủ chính là bảo "thử lại sau"; 429 và 503 có thể kèm tiêu đề `Retry-After` nói nên chờ bao lâu, và khi có thì tôn trọng nó. Ngoài ra, gửi lại một thao tác làm thay đổi dữ liệu (như tạo đơn) chỉ an toàn khi thao tác đó chịu được việc lặp, thường nhờ một khóa chống trùng; phương thức GET, PUT, DELETE được định nghĩa là lặp lại không đổi tác dụng dự kiến lên máy chủ (gửi một lần hay nhiều lần, máy chủ ở cùng trạng thái cuối; phản hồi thì có thể khác, ví dụ DELETE lần đầu báo thành công, lần thử lại báo không tìm thấy), còn POST thì không.

Khi thử lại, hai điều chỉnh làm thành khác biệt: **chờ tăng dần** (ví dụ 1, 2, 4, 8 giây, có trần) để máy chủ có thời gian thở, và **thêm ngẫu nhiên** để các máy khách không đồng bộ với nhau. Cuối cùng là **giới hạn số lần**, vì thử mãi là một cách tự gây quá tải.

**Phía máy chủ.** Máy chủ không thể tin mọi trình duyệt đều lịch sự, nên đặt một lớp chắn phía trước. **Bộ giới hạn tốc độ** từ chối bớt yêu cầu vượt mức; hai kiểu phổ biến là xô thẻ (token bucket: thẻ được thêm với tốc độ cố định, mỗi yêu cầu lấy một thẻ, xô đầy cho phép bùng nổ ngắn) và xô rò (leaky bucket: yêu cầu xếp hàng và chảy ra với tốc độ đều). **Cầu dao** (circuit breaker) có ba trạng thái: đóng (cho qua, đếm lỗi), mở (từ chối ngay khi lỗi vượt ngưỡng trong một khoảng thời gian), và nửa mở (sau một lúc cho một ít yêu cầu qua thử; thành công thì đóng lại, thất bại thì mở lại). Trạng thái nửa mở là chỗ giúp dịch vụ đang hồi phục không bị dội ngay một cơn lũ.

## Thử: 1000 máy khách cùng thất bại

Ngày 2026-10-19, một chương trình mô phỏng nhỏ (không có mạng thật): 1000 máy khách gửi yêu cầu cùng lúc ở nhịp 0; mỗi nhịp máy chủ xử lý được tối đa 100 yêu cầu, phần dư bị từ chối và máy khách thử lại, tối đa 8 lần thử lại. Ba cách chờ:

| Cách chờ giữa các lần thử | Máy khách thành công | Bỏ cuộc | Tổng yêu cầu tới máy chủ | Nhịp xong |
|---|---|---|---|---|
| Cố định 1 nhịp | 900 | 100 | 5400 | 8 |
| Tăng gấp đôi (2, 4, ... trần 64), không ngẫu nhiên | 900 | 100 | 5400 | 254 |
| Tăng gấp đôi, cộng ngẫu nhiên từ 0 tới mức đó | 1000 | 0 | 2747 | 21 |

Kết quả giải thích vì sao "tăng dần" chưa đủ: nếu mọi máy bắt đầu cùng nhịp, chúng cùng chờ rồi cùng quay lại thành những đợt đồng bộ, mỗi đợt vẫn lớn hơn sức máy chủ, nên chỉ thêm thời gian chờ chứ không bớt đợt. Ngẫu nhiên rải các lần thử ra theo thời gian, nên mỗi nhịp máy chủ nhận ít hơn mức nó chịu được.

## Giới hạn cần nhớ

Mô phỏng chỉ có một cơn sóng ban đầu, máy chủ không sập thật mà chỉ từ chối phần dư, và không có thời gian xử lý hay hàng đợi. Các con số 900, 5400, 2747 là của kịch bản đó (hạt giống ngẫu nhiên cố định), không phải mức bạn sẽ thấy ở hệ thống thật. Điều mô phỏng cho thấy là hình dạng: thử lại đồng bộ giữ nguyên áp lực, thử lại có ngẫu nhiên làm áp lực loãng ra.

## Nhìn hình trả lời

Một trang bán hàng nhận 429 kèm `Retry-After: 30` khi người dùng bấm "đặt đơn". Trình duyệt nên tự chờ 30 giây rồi gửi lại ngay không?

<details>
<summary>Xem đáp án</summary>

Chờ ít nhất 30 giây là đúng, vì máy chủ đã nói rõ. Nhưng gửi lại ngay sau đó chỉ an toàn nếu việc "đặt đơn" chịu được lặp; nếu không có khóa chống trùng, tốt hơn là báo người dùng và để họ quyết định, hoặc kiểm tra xem đơn đã tạo chưa.
Đây là suy luận của người biên soạn từ định nghĩa các phương thức và mã trạng thái.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn nêu quy tắc "4xx không thử lại, 5xx thử lại cẩn thận", rồi chuyển sang chờ tăng dần ở trình duyệt và cổng điều tiết ở máy chủ. Bài này giữ khung đó nhưng bổ sung hai ngoại lệ của nhóm 4xx (408, 429), lưu ý về tính lặp được của thao tác, và đo ngẫu nhiên bằng mô phỏng riêng. Mô tả cầu dao đối chiếu với tài liệu kiến trúc của Microsoft đã đọc; phần còn lại là kiến thức chung.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-handle-web-request-error.md): khung phía trình duyệt, phía máy chủ. Bảng mô phỏng, hai ngoại lệ của 4xx và đáp án là của người biên soạn.
- [Microsoft — Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker): ba trạng thái đóng, mở, nửa mở. Đã đọc bản trên kho GitHub MicrosoftDocs/architecture-center.
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html): các lớp mã 4xx và 5xx, phương thức lặp được, tiêu đề `Retry-After`. Kiến thức chung, chưa mở lại trong phiên viết.
- [RFC 6585 — Additional HTTP Status Codes](https://www.rfc-editor.org/rfc/rfc6585.html): mã 429. Kiến thức chung, chưa mở lại trong phiên viết.
- [Amazon Builders' Library — Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/): thử lại, chờ tăng dần và ngẫu nhiên. Chỉ đọc được đoạn trích từ tìm kiếm, chưa đọc toàn bài.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

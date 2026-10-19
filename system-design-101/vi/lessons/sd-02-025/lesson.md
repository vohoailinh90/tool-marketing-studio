# Hành trình của một tin nhắn Slack

**Theo bài nguồn, một tin nhắn Slack đi qua năm loại máy chủ: WebApp nhận tin, Admin Server tìm đúng Channel Server, Channel Server giữ lịch sử kênh, rồi Gateway Server và Envoy đẩy tin tới người nhận đang giữ kết nối WebSocket.**
Bài này đi theo một tin nhắn từ người gửi tới người nhận, và hỏi ở mỗi chặng: máy chủ này biết điều gì mà chặng trước không biết.

![Năm chặng nối nhau. Người gửi gửi tin tới WebApp, nơi định nghĩa API cho ứng dụng Slack. WebApp chuyển tới Admin Server, nơi dùng mã kênh để tìm đúng Channel Server. Channel Server giữ lịch sử kênh; hàng triệu kênh được chia cho nhiều Channel Server bằng băm nhất quán. Channel Server đẩy tin qua Gateway Server, đặt ở từng vùng địa lý và giữ các đăng ký kênh qua WebSocket, rồi qua Envoy, một proxy dịch vụ. Người nhận dùng WebSocket nên nhận tin ngay. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-025-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách ứng dụng Slack gọi chức năng của máy chủ.
- **AS** (Admin Server) — máy chủ quản trị: biết kênh nào nằm trên Channel Server nào.
- **CS** (Channel Server) — máy chủ kênh: giữ lịch sử tin nhắn của các kênh được giao cho nó.
- **GS** (Gateway Server) — máy chủ cổng: đặt ở từng vùng địa lý, giữ kết nối với người dùng trong vùng.
- **ID** (IDentifier) — mã định danh; ở đây là mã kênh.

## Đọc hình

Theo nguồn, năm loại máy chủ là:
- **WebApp:** định nghĩa API mà ứng dụng Slack dùng.
- **Admin Server (AS):** dùng ID kênh để tìm đúng Channel Server.
- **Channel Server (CS):** giữ lịch sử của kênh tin nhắn.
- **Gateway Server (GS):** đặt ở mỗi vùng địa lý, giữ các đăng ký kênh qua WebSocket.
- **Envoy:** proxy dịch vụ cho ứng dụng chạy trên đám mây.

Đường đi của một tin:
1. Vì có quá nhiều kênh, CS dùng băm nhất quán (consistent hashing) để chia hàng triệu kênh cho nhiều Channel Server.
2. Tin nhắn đi qua WebApp và AS tới đúng CS.
3. Qua GS và Envoy, CS đẩy tin tới người nhận.
4. Người nhận dùng WebSocket, một kết nối hai chiều, nên nhận được cập nhật ngay.

Mỗi chặng biết thêm một điều: WebApp biết API, AS biết kênh ở CS nào, CS biết lịch sử kênh, GS biết người dùng nào trong vùng đang theo dõi kênh nào.

## Giới hạn cần nhớ

Bài nguồn là bản tóm tắt ngắn một bài kỹ thuật của Slack. Nó không nói tin được lưu bền ở đâu ngoài CS, không nói chuyện gì xảy ra khi một CS hỏng, và không nói người nhận đang ngoại tuyến thì nhận tin thế nào. Câu "mỗi chặng biết thêm một điều" là cách đọc của người biên soạn.

## Nhìn hình thử trả lời

Hai người ở hai châu lục khác nhau cùng trong một kênh. Theo hình, tin của người thứ nhất tới máy chủ nào giữ lịch sử kênh, và đi qua đâu để tới người thứ hai?

<details>
<summary>Xem đáp án</summary>

Tin đi qua WebApp và AS tới đúng một CS, nơi giữ lịch sử của kênh đó (AS tìm CS bằng ID kênh). Từ CS, tin được đẩy qua GS ở vùng của người thứ hai và Envoy, rồi tới máy người thứ hai qua kết nối WebSocket.

</details>

<details>
<summary>Xem sâu hơn: vì sao dùng băm nhất quán</summary>

- Băm thông thường (lấy mã kênh chia lấy dư cho số máy) làm gần như mọi kênh đổi chỗ khi thêm hay bớt một máy.
- Băm nhất quán chỉ dời một phần nhỏ kênh khi số máy thay đổi.
- Nhờ vậy có thể thêm Channel Server khi số kênh tăng mà không xáo trộn cả hệ thống.

Đây là kiến thức chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-the-journey-of-a-slack-message.md): năm loại máy chủ và đường đi của một tin nhắn.

Đã đọc nguồn ngày 2026-10-19. Bài kỹ thuật gốc của Slack chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

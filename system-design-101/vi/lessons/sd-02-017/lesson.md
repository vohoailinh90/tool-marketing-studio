# Netflix gửi thông báo đẩy: sự kiện, ưu tiên, rồi từng loại thiết bị

**Theo bài nguồn, một thông báo đẩy của Netflix đi qua bảy bước: sự kiện được tạo, đưa vào bộ quản lý sự kiện, xếp vào hàng đợi theo ưu tiên, được xử lý thành dữ liệu thông báo, lưu vào Cassandra, rồi gửi ra qua dịch vụ hợp với từng loại thiết bị.**
Hệ thống phải phục vụ 220 triệu người dùng gần như tức thời, trên nhiều loại máy khác nhau. Bài này chia bảy bước thành hai nửa: quyết định gửi gì, và gửi tới đâu.

![Hai khung bước và một khung ghi nhớ. Khung một, quyết định gửi gì: sự kiện được tạo bởi đồng hồ, hành động của người dùng hoặc hệ thống; bộ quản lý sự kiện nghe các sự kiện và chuyển chúng vào hàng đợi theo luật ưu tiên; cụm xử lý theo ưu tiên tạo dữ liệu thông báo cho từng thiết bị và lưu vào Cassandra. Khung hai, gửi tới đâu: thông báo đi tới hệ thống nhắn tin ra ngoài; Android qua FCM; thiết bị Apple qua APNs; web, tivi và thiết bị phát khác qua Zuul Push do Netflix tự làm. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-017-main.svg)

## Từ viết tắt

- **FCM** (Firebase Cloud Messaging) — dịch vụ nhắn tin đám mây của Google: đường để gửi thông báo đẩy tới điện thoại Android.
- **APN** (Apple Push Notification) — dịch vụ thông báo đẩy của Apple; bài nguồn viết APNs (APN service): đường để gửi thông báo tới thiết bị Apple.
- **TV** (TeleVision) — tivi: trong bài là tivi thông minh, một loại máy khách Netflix phải gửi thông báo tới.

## Đọc hình

**Yêu cầu.** Khoảng 220 triệu người dùng; gần như tức thời; các hệ thống phía sau cần gửi thông báo tới nhiều loại máy khách: iOS, Android, smart TV, Roku, Amazon FireStick, trình duyệt web.

**Quyết định gửi gì.**
1. Sự kiện thông báo đẩy được tạo bởi đồng hồ (theo lịch), hành động của người dùng, hoặc hệ thống.
2. Sự kiện được gửi tới bộ quản lý sự kiện.
3. Bộ quản lý sự kiện nghe những sự kiện cụ thể và chuyển chúng vào các hàng đợi khác nhau, theo luật chuyển tiếp dựa trên ưu tiên.
4. Cụm xử lý theo ưu tiên xử lý sự kiện và tạo dữ liệu thông báo cho các thiết bị.
5. Dữ liệu thông báo được lưu vào cơ sở dữ liệu Cassandra.

**Gửi tới đâu.**

6. Thông báo được gửi tới các hệ thống nhắn tin ra ngoài.
7. Android dùng FCM; thiết bị Apple dùng APNs; web, TV và các thiết bị phát khác dùng giải pháp Netflix tự làm tên Zuul Push.

## Giới hạn cần nhớ

Bài nguồn dựa trên một bài blog kỹ thuật của Netflix và tự ghi là "theo hiểu biết của tôi". Nó không nói luật ưu tiên trông thế nào, không nói vì sao lưu dữ liệu vào Cassandra trước khi gửi, và không nói chuyện gì xảy ra khi một thiết bị đang tắt. Phần giải thích vì sao tách theo ưu tiên ở dưới là của người biên soạn.

## Nhìn hình thử trả lời

Một thông báo cần tới một chiếc iPhone và một chiếc tivi thông minh. Theo hình, hai thông báo đó rời Netflix qua hai đường nào?

<details>
<summary>Xem đáp án</summary>

iPhone là thiết bị Apple nên đi qua APNs. Tivi thông minh thuộc nhóm "web, tivi và thiết bị phát khác" nên đi qua Zuul Push, giải pháp Netflix tự làm. Cả hai đều xuất phát từ cùng dữ liệu thông báo ở bước 4–5.

</details>

<details>
<summary>Xem sâu hơn: vì sao tách hàng đợi theo ưu tiên</summary>

- Một thông báo gấp (chẳng hạn liên quan tới tài khoản) không phải xếp sau hàng triệu thông báo gợi ý phim.
- Mỗi hàng đợi có thể được cấp máy xử lý riêng theo mức quan trọng.
- Khi hệ thống quá tải, có thể để thông báo ít quan trọng chờ lâu hơn.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-netflix-scale-push-messaging-for-millions-of-devices.md): yêu cầu, quy mô và bảy bước của một thông báo đẩy ở Netflix.

Đã đọc nguồn ngày 2026-10-19. Bài blog kỹ thuật của Netflix mà nguồn dựa vào chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

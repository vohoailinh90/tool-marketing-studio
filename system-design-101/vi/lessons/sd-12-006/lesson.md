# Ứng dụng chat đơn giản với Redis: kênh phát tin và tập có thứ tự

**Chat bằng Redis dùng hai món cho hai việc khác nhau: kênh phát tin (`PUBLISH` và `SUBSCRIBE`) giao tin ngay cho người đang mở ứng dụng, còn tập có thứ tự (sorted set) giữ lịch sử cho người vào sau.**
Nhầm hai món này là lỗi dễ gặp nhất: kênh phát tin không nhớ gì, còn tập có thứ tự không tự đẩy tin tới ai.

![Hai khung. Khung một, đường đi của một tin nhắn: Bob gửi tin tới máy chủ chat qua WebSocket; máy chủ lưu tin vào Redis bằng zadd; máy chủ phát tin lên kênh bằng publish; Redis chuyển tin cho các kết nối đang lắng nghe kênh. Khung hai, hai việc khác nhau: zadd giữ tin để đọc sau, publish chỉ giao cho người đang nghe tại lúc phát.](../../diagrams/sd-12-006-main.svg)

## Đọc hình

**Khởi tạo kết nối (Connection Initialization).** Bob mở ứng dụng; máy khách và máy chủ thiết lập một WebSocket, tức một kết nối hai chiều giữ mở nên máy chủ đẩy tin xuống được mà không cần máy khách hỏi. Máy chủ chat mở nhiều kết nối tới Redis: một kết nối để ghi dữ liệu và phát tin, những kết nối còn lại để lắng nghe kênh. Lý do tách ra: một kết nối đã `SUBSCRIBE` chỉ được chạy một vài lệnh, phần thử nghiệm bên dưới cho thấy lệnh `GET` bị từ chối. Máy chủ lấy từ Redis danh sách thành viên và lịch sử tin rồi gửi cho Bob. Vì Bob là thành viên mới, một thông báo được phát lên kênh `member_add` để những người khác thấy Bob.

**Gửi tin (Message Handling).** Khi Bob nhắn cho Alice, máy chủ thêm tin vào tập có thứ tự bằng `ZADD`, điểm là thời gian nhận nên tập luôn xếp theo thứ tự đến. Sau đó máy chủ `PUBLISH` tin lên kênh `messages`; kết nối đang lắng nghe của Alice nhận được và đẩy xuống ứng dụng của cô.

## Thử nghiệm với Redis thật

Ngày 2026-10-19, người biên soạn chạy Redis 7.0.15 trên máy (`redis-server` và `redis-cli`) và thử các điều trên.

| Thử | Kết quả |
|---|---|
| Người nghe vào trước, 3 tin được phát | nhận cả 3 tin |
| Người nghe vào sau tin thứ hai, rồi tin thứ ba được phát | chỉ nhận tin thứ ba |
| `ZRANGE` lịch sử sau 3 tin | trả đủ 3 tin, đúng thứ tự |
| `PUBLISH` lên kênh không ai nghe | trả về 0, tin biến mất |
| `GET` trên kết nối đã `SUBSCRIBE` | lỗi: chỉ các lệnh như `SUBSCRIBE`, `UNSUBSCRIBE`, `PING`, `QUIT`, `RESET` được phép |
| `ZADD` hai lần cùng chuỗi "Bob: hi" với điểm 1 rồi 2 | chỉ còn một phần tử, điểm 2: tin thứ nhất bị ghi đè |
| `ZADD` hai chuỗi khác nhau, "Bob\|1\|hi" và "Bob\|2\|hi" | giữ cả hai |

Ba điều rút ra. Một: kênh phát tin không lưu; người vào muộn phải đọc lịch sử từ tập có thứ tự. Hai: phần tử của tập có thứ tự là duy nhất, nên hai tin trùng nội dung gửi bằng cùng một chuỗi sẽ thành một; cần kèm mã tin hay số thứ tự vào chuỗi. Ba: hai phần tử cùng điểm được xếp theo thứ tự chữ cái của chuỗi, không theo thứ tự thêm vào (thử với `b` rồi `a` cùng điểm 5, kết quả `a`, `b`).

## Giới hạn cần nhớ

Bài nguồn chỉ vẽ luồng của một máy chủ chat. Nó không bàn nhiều máy chủ chat dùng chung Redis, xác thực, việc giới hạn độ dài lịch sử hay chuyện Redis khởi động lại. Thử nghiệm trên chạy Redis một máy, không có mạng thật hay nhiều người dùng. Việc giải thích vì sao kênh phát tin không lưu tin là kết luận từ thử nghiệm; bài chưa đối chiếu với tài liệu Redis vì chưa mở được trang của nó.

## Nhìn hình trả lời

Alice mở lại ứng dụng sau khi Bob đã gửi ba tin lúc cô không mở máy. Cô lấy lại ba tin đó bằng cách nào, và kênh phát tin có làm được việc ấy không?

<details>
<summary>Xem đáp án</summary>

Máy chủ đọc tập có thứ tự (như `ZRANGE`) và gửi lịch sử cho Alice lúc cô khởi tạo kết nối, đúng như bước lấy lịch sử của Bob. Kênh phát tin không làm được: tin phát lúc không có ai nghe thì mất, như ở dòng thử nghiệm trả về 0 và người nghe muộn.
Đây là kết luận từ thử nghiệm với Redis 7.0.15 trên một máy.

</details>

<details>
<summary>Xem sâu hơn: điều đã bổ sung so với bài nguồn</summary>

Bài nguồn có hai giai đoạn, tám bước khởi tạo và ba bước gửi tin. Bài này giữ hai giai đoạn, bỏ việc đánh số bước, rồi thêm bảng thử nghiệm: người nghe muộn, tin trùng, thứ tự cùng điểm và giới hạn của kết nối đang lắng nghe.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/build-a-simple-chat-application.md): hai giai đoạn khởi tạo kết nối và xử lý tin, các kênh `member_add` và `messages`, `ZADD`.
- Thử nghiệm của người biên soạn với Redis 7.0.15 chạy cục bộ (ngày 2026-10-19): các hành vi trong bảng.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

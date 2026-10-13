# Xây ứng dụng chat đơn giản với Redis

**Chat cần hai việc khác nhau:** đẩy tin mới tới những người đang trực tuyến ngay lập tức, và nhớ lịch sử để người mới vào hay người vừa mất mạng vẫn đọc được. Redis đảm nhiệm cả hai bằng hai tính năng khác nhau.

![Bảy thẻ dọc: Bob mở ứng dụng và nối WebSocket tới máy chủ chat; máy chủ tải danh sách thành viên và lịch sử từ Redis; máy chủ publish thông báo có người vào lên kênh member_add; Bob gửi tin cho Alice; máy chủ lưu tin vào sorted set bằng ZADD với điểm là thời gian; máy chủ publish tin lên kênh messages; máy chủ của Alice đã subscribe nên đẩy tin tới Alice qua WebSocket. Chú thích: pub/sub lo tin đang bay, sorted set lo tin đã qua.](../../diagrams/sd-12-006-main.svg)

## Đọc hình

**Vào phòng (1–3).** Ứng dụng nối WebSocket tới máy chủ chat. Máy chủ lấy từ Redis danh sách thành viên và lịch sử rồi gửi cho Bob, đồng thời **publish** lên kênh `member_add` để người khác thấy Bob vào.

**Gửi tin (4–7).** Tin của Bob được ghi vào một **sorted set** bằng `ZADD`, điểm là thời gian nhận, để sau này đọc lại theo thứ tự. Cùng lúc nó được publish lên kênh `messages`; các máy chủ đã **subscribe** nhận được và đẩy tin tới Alice qua WebSocket.

## Giới hạn cần nhớ

Pub/sub của Redis chỉ chuyển tin cho những ai đang nghe lúc tin được phát; ai chưa kết nối hoặc đang mất mạng sẽ không nhận lại. Vì thế lịch sử phải nằm ở chỗ bền hơn (ở đây là sorted set) và máy khách cần tải lại phần bị lỡ khi nối lại. Redis chỉ bền theo cấu hình lưu trữ và bộ nhớ có hạn, nên lịch sử cũ cần được cắt bớt.

## Nhìn hình trả lời

Alice mất mạng 10 giây trong lúc Bob gửi tin. Khi nối lại, tin của Bob có tự tới qua kênh pub/sub không? Alice lấy lại bằng cách nào?

<details>
<summary>Xem đáp án</summary>

Không tự tới, vì pub/sub không phát lại. Alice tải lịch sử từ sorted set. Mốc phải an toàn khi nhiều tin cùng điểm: lấy từ điểm của tin cuối cô đã có trở đi (gồm cả điểm đó) rồi bỏ những tin đã nhận theo mã tin nhắn. Nếu chỉ lấy điểm lớn hơn tin cuối thì tin thứ hai cùng điểm sẽ bị bỏ sót vĩnh viễn. Gọn hơn là gán mỗi tin một mã tăng dần và lấy các tin có mã lớn hơn.

</details>

<details>
<summary>Xem sâu hơn: nhiều máy chủ, thứ tự tin và Redis Streams</summary>

- **Nhiều máy chủ chat:** mỗi máy chủ cùng subscribe một kênh, nên tin Bob gửi vào máy chủ A vẫn tới Alice đang nối vào máy chủ B. Đó là lý do cần pub/sub chứ không chỉ gọi hàm trong một tiến trình.
- **Điểm là thời gian:** hai tin cùng mili giây có cùng điểm, và Redis xếp các phần tử cùng điểm theo thứ tự từ điển của phần tử chứ không theo giờ đến. Vì vậy cần một mã tin nhắn tăng dần (hoặc dùng Redis Streams) làm mốc đọc lại, và đồng hồ nhiều máy lệch nhau thì thứ tự theo giờ không còn đáng tin.
- **Redis Streams** là lựa chọn khác: lưu tin theo thứ tự có ID và cho đọc lại từ một điểm, hợp khi không được lỡ tin.
- Ví dụ này cố ý đơn giản; hệ chat thật còn cần xác thực, phân quyền kênh, xác nhận đã nhận và chống gửi trùng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/build-a-simple-chat-application.md): ứng dụng chat dùng pub/sub và sorted set của Redis.
- [Redis — Pub/Sub](https://redis.io/docs/latest/develop/interact/pubsub/): ngữ nghĩa chuyển tin, không lưu lại.
- [Redis — Sorted sets](https://redis.io/docs/latest/develop/data-types/sorted-sets/): ZADD và sắp theo điểm.
- [Redis — Streams](https://redis.io/docs/latest/develop/data-types/streams/): luồng tin có ID, đọc lại được.
- [Redis — Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/): RDB/AOF và độ bền.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-006.json).

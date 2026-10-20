# AirTag: tìm đồ nhờ điện thoại của người lạ đi ngang

**AirTag không có mạng di động hay GPS để tự báo vị trí; nó chỉ phát một tín hiệu Bluetooth ngắn, còn điện thoại hay máy tính bảng của người khác đi ngang qua sẽ báo hộ.**
Biết ba chặng của tín hiệu đó, bạn hiểu vì sao AirTag tìm được đồ ở nơi đông người mà lại kém ở nơi vắng.

![Hai khung. Khung một, đường đi của một lần định vị: AirTag phát tín hiệu Bluetooth kèm một mã công khai; thiết bị Apple đi ngang nhận tín hiệu rồi gửi vị trí của mình, đã mã hóa, lên máy chủ Apple; chủ đồ mở ứng dụng Find My và giải mã để xem vị trí trên bản đồ. Khung hai, ba điều nên nhớ: bên đi ngang không biết đồ của ai, Apple không đọc được vị trí, và nơi ít thiết bị Apple thì vị trí cũ hoặc thiếu.](../../diagrams/sd-12-001-main.svg)

## Từ viết tắt

- **GPS** (Global Positioning System) — hệ thống định vị toàn cầu: cách điện thoại biết vị trí nhờ vệ tinh; AirTag không có bộ phận này.
- **BLE** (Bluetooth Low Energy) — Bluetooth năng lượng thấp: kiểu Bluetooth tốn rất ít pin, phù hợp với thẻ nhỏ chạy bằng pin cúc áo như AirTag.

## Đọc hình

**Chặng 1: AirTag phát tín hiệu.** Cứ vài giây thẻ lại phát một gói tin BLE ngắn trong phạm vi vài chục mét. Gói đó không ghi tên chủ mà mang một mã công khai, và mã này đổi theo thời gian, nên người đứng cạnh không theo dõi được một thẻ chỉ bằng cách ghi lại mã.

**Chặng 2: người đi ngang báo hộ.** Một thiết bị Apple nằm trong mạng Find My thấy gói tin sẽ lấy vị trí của chính nó, mã hóa vị trí bằng mã công khai trong gói, rồi gửi lên máy chủ của Apple (iCloud). Thiết bị này không biết thẻ là của ai và chủ của nó không phải làm gì.

**Chặng 3: chủ đồ lấy báo cáo.** Chỉ thiết bị của chủ giữ khóa riêng ghép với mã công khai nên chỉ họ giải mã được. Ứng dụng Find My tải các báo cáo về, giải mã và vẽ vị trí gần nhất lên bản đồ.

Vì vị trí là *vị trí của người đi ngang* lúc họ nghe thấy thẻ, nên độ chính xác chỉ cỡ tầm Bluetooth, tức là "quanh đây", không phải đúng chiếc ghế hay ngăn kéo.

## Giới hạn cần nhớ

Cả cách làm này sống nhờ có thiết bị Apple đi ngang. Ở nơi ít người dùng, thẻ có thể không được ai nghe thấy trong nhiều giờ, và bản đồ sẽ hiện vị trí cũ. Đây cũng là điều bài nguồn nhắc: vị trí cập nhật ít hơn và kém chính xác hơn ở vùng vắng thiết bị Apple.
Phần mô tả mã đổi theo thời gian và mã hóa bằng khóa công khai là kiến thức chung của người biên soạn về thiết kế Find My, chưa đối chiếu với tài liệu bảo mật của Apple; bài không nêu khoảng thời gian đổi mã cụ thể vì chưa kiểm chứng.

## Nhìn hình trả lời

Bạn để quên ba lô có AirTag ở một ga tàu đông người. Hai tiếng sau bản đồ vẫn hiện vị trí của hai tiếng trước. Theo hình, những lý do nào có thể giải thích điều này?

<details>
<summary>Xem đáp án</summary>

Bản đồ chỉ cập nhật khi có một thiết bị Apple nghe thấy thẻ và gửi báo cáo lên, nên nếu thẻ nằm trong túi ở góc không ai đi qua, hoặc những người đi qua dùng thiết bị không thuộc mạng Find My, sẽ không có báo cáo mới. Một lý do khác là thẻ đã được mang đi rồi để lại ở chỗ vắng: vị trí cuối cùng vẫn là chỗ từng có người nghe thấy nó.
Đây là suy luận từ ba chặng của hình; nguồn chỉ nói rằng nơi ít thiết bị Apple thì cập nhật ít và kém chính xác hơn.

</details>

<details>
<summary>Xem sâu hơn: điều đã bổ sung so với bài nguồn</summary>

Bài nguồn có ba ý ngắn (tín hiệu Bluetooth, mạng Find My, xem trên bản đồ) và một đoạn giới hạn. Bài này giữ cả bốn ý, rồi tách mã công khai khỏi chủ thẻ để thấy vì sao người đi ngang không biết gì về chủ đồ và vì sao Apple cũng không đọc được vị trí.
Hai điều này, cùng chuyện mã đổi theo thời gian, là mô tả chung của người biên soạn về thiết kế Find My; chưa đối chiếu với tài liệu của Apple. Chuyện thẻ bị dùng để theo dõi người khác (và các cảnh báo chống theo dõi) bài này không bàn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-airtags-work.md): ba ý chính về Bluetooth, mạng Find My, xem vị trí, và đoạn giới hạn.
- Apple Platform Security Guide, mục Find My (kiến thức chung của người biên soạn; chưa mở được trang trong phiên viết bài nên chưa đối chiếu): mã công khai đổi theo thời gian, báo cáo vị trí được mã hóa.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

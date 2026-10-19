# Chat một-một: vì sao tin nhắn cần mã thứ tự và đường đi cho người ngoại tuyến

**Trong một ứng dụng chat một-một, tin của Alice đi qua dịch vụ chat, được cấp một mã thứ tự và lưu lại, rồi được chuyển tới Bob bằng một trong hai đường tùy Bob đang trực tuyến hay không.**
Bài này giữ hai luồng của bài nguồn (đăng nhập và nhắn tin), rồi thử trên máy hai chuyện hay bị bỏ qua: tin đến lộn xộn hoặc trùng thì xử lý thế nào, và vì sao không dùng đồng hồ của máy chủ để sắp thứ tự.

![Hai khung. Khung một, đăng nhập: người dùng mở kết nối WebSocket, dịch vụ hiện diện cập nhật trạng thái và báo cho bạn bè. Khung hai, gửi tin: tin đi qua dịch vụ chat, dịch vụ cấp mã thứ tự và lưu vào kho tin nhắn, rồi hàng đợi đồng bộ kiểm tra người nhận; nếu đang trực tuyến thì đẩy qua WebSocket, nếu ngoại tuyến thì gửi thông báo đẩy.](../../diagrams/sd-12-013-main.svg)

## Đọc hình

**Đăng nhập.** Alice mở ứng dụng và thiết lập một kết nối WebSocket (kết nối hai chiều, giữ mở) với phía máy chủ. Dịch vụ hiện diện nhận thông báo, cập nhật trạng thái "đang trực tuyến" của Alice rồi báo cho bạn bè của cô.

**Nhắn tin.** Tin của Alice tới dịch vụ chat A. Từ đó nó đi tới dịch vụ cấp mã thứ tự, nơi sinh ra một mã duy nhất cho tin, và được lưu vào kho tin nhắn. Rồi tin vào hàng đợi đồng bộ tin nhắn. Trước khi chuyển, dịch vụ đồng bộ kiểm tra hiện diện của Bob:

- Bob trực tuyến: tin được chuyển tới dịch vụ chat B (nơi Bob đang kết nối) và đẩy xuống Bob qua WebSocket.
- Bob ngoại tuyến: tin được gửi tới máy chủ thông báo đẩy và đẩy tới thiết bị của Bob.

## Thử nghiệm

Ngày 2026-10-19, người biên soạn viết một chương trình Python nhỏ để thử hai điều mà sơ đồ không nói.

**Tin đến lộn xộn hoặc trùng.** Mạng chuyển tin ít khi hoàn hảo: một tin có thể được giao hai lần (khi hệ thống thử lại để chắc chắn không mất), và hai tin liền nhau có thể đến đảo ngược. Chương trình mô phỏng Alice gửi 5 tin, mỗi tin có 20% khả năng bị giao hai lần, mỗi cặp tin liền nhau có 30% khả năng đổi chỗ. Lặp 1.000 lần:

| Cách hiển thị ở máy Bob | Số lần ra sai thứ tự hoặc có tin trùng |
|---|---|
| Theo thứ tự tin đến | 918 trên 1.000 |
| Bỏ tin trùng theo mã, sắp theo mã thứ tự | 0 trên 1.000 |

Tin đến theo thứ tự "đúng" là chuyện may. Mã thứ tự do dịch vụ cấp đóng hai vai: bỏ tin trùng (đã thấy mã này rồi) và sắp thứ tự (mã nhỏ trước).

**Vì sao không dùng đồng hồ.** Giả sử Bob trả lời 5 mili giây sau khi nhận tin, nhưng đồng hồ của hai máy chủ lệch nhau ngẫu nhiên tới 50 mili giây. Trong 10.000 lần thử, 4.435 lần (khoảng 44%) lời đáp bị đóng dấu thời gian sớm hơn tin gốc của nó. Dùng thời gian của máy chủ để sắp thứ tự thì gần nửa số lần lời đáp hiện lên trước câu hỏi. Một bộ đếm tăng dần cho mỗi cuộc trò chuyện (hoặc mã sinh từ một nguồn duy nhất) không bị chuyện này.

## Giới hạn cần nhớ

Đây là mô phỏng trên một máy, không có mạng thật, không có đồng hồ thật và không có nhiều máy chủ cạnh tranh nhau. Chương trình không mô phỏng bộ đếm phân tán, và bài nguồn không nói dịch vụ cấp mã thứ tự được viết thế nào; vì vậy kết luận "mã sinh từ một nguồn duy nhất" là suy luận của người biên soạn từ thử nghiệm, không phải lời của bài nguồn. Bài cũng không bàn nhóm chat, mã hóa đầu cuối hay lưu lịch sử lâu dài.

## Nhìn hình trả lời

Bob đang ngoại tuyến. Alice gửi ba tin liên tiếp, và máy chủ thông báo đẩy gửi chúng tới điện thoại Bob không theo thứ tự. Khi Bob mở ứng dụng, tin hiện đúng thứ tự không, và nhờ đâu?

<details>
<summary>Xem đáp án</summary>

Hiện đúng nếu ứng dụng sắp theo mã thứ tự do dịch vụ cấp khi tin được lưu, chứ không theo thứ tự thông báo đẩy tới. Thông báo đẩy chỉ báo "có tin mới"; thứ tự và việc tin có đủ hay không là do kho tin nhắn và mã thứ tự quyết định. Đây là suy luận từ thử nghiệm, bài nguồn không nói chi tiết này.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn mô tả hai luồng (đăng nhập và nhắn tin) với tám bước. Bài này giữ hai luồng và thêm hai thử nghiệm: xử lý tin trùng và đảo thứ tự, và lệch đồng hồ. Phần giải thích vì sao cần mã thứ tự là của người biên soạn, không phải của bài nguồn; tỷ lệ 20% và 30% là tham số của mô phỏng, không phải số đo từ hệ thống thật.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (chỉ dùng thư viện chuẩn) đã in mọi con số của phần thử nghiệm; hạt giống ngẫu nhiên được đặt cố định trong chương trình nên chạy lại ra đúng các số đó.

```python
import random, itertools
rnd=random.Random(3)
# Alice sends 20 messages to Bob via two chat servers; delivery is at-least-once with reordering
msgs=[(i,f"m{i}") for i in range(1,6)]
def network(msgs,dup=0.2,swap=0.3):
    out=[]
    for m in msgs:
        out.append(m)
        if rnd.random()<dup: out.append(m)
    for i in range(len(out)-1):
        if rnd.random()<swap: out[i],out[i+1]=out[i+1],out[i]
    return out
trials=1000;bad_naive=bad_fixed=0;dups=0
for _ in range(trials):
    net=network(msgs)
    # naive: display in arrival order
    naive=[m[1] for m in net]
    if naive!=[m[1] for m in msgs]: bad_naive+=1
    # fixed: dedupe by id, sort by sequence id
    seen=set();fixed=[]
    for i,t in net:
        if i not in seen: seen.add(i);fixed.append((i,t))
    fixed.sort()
    if [t for _,t in fixed]!=[m[1] for m in msgs]: bad_fixed+=1
print('naive wrong',bad_naive,'of',trials,'fixed wrong',bad_fixed)
# sequencing: per-conversation counter vs timestamps from two servers with skewed clocks
cnt=0
for _ in range(10000):
    # Alice msg then Bob reply 5ms later, but server clocks differ by up to 50ms
    skew=rnd.uniform(-0.05,0.05)
    t_a=0.0; t_b=0.005+skew
    if t_b<t_a: cnt+=1
print('reply stamped earlier than message by clock skew', cnt,'of 10000')
# offline: push queue; presence flips
online=False; delivered=0; pushed=0
for i in range(1,11):
    if i in (4,5,6): online=False
    else: online=True
    if online: delivered+=1
    else: pushed+=1
print('online path',delivered,'push path',pushed)
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-design-a-chat-application-like-whatsapp-facebook-messenger-or-discord.md): luồng đăng nhập và luồng nhắn tin một-một.
- Thử nghiệm của người biên soạn bằng Python 3 (ngày 2026-10-19): giao trùng, đảo thứ tự và lệch đồng hồ.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

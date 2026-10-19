# Thông báo đẩy tới điện thoại: thẻ đăng ký, hàng đợi và việc dọn thẻ cũ

**Muốn đẩy thông báo tới điện thoại, ứng dụng không tự giữ kết nối riêng: máy chủ ứng dụng nhờ một dịch vụ nhắn tin (như FCM của Firebase) chuyển tin tới thiết bị, bằng một "thẻ đăng ký" gắn với từng bản cài đặt ứng dụng.**
Bài này đi theo đường đi của một thông báo, rồi mô phỏng hai việc mà bài nguồn chỉ nhắc: thẻ cũ tích tụ ra sao nếu không dọn, và tin gửi cho máy đang ngoại tuyến có kịp tới nơi không.

![Hai khung. Khung một, đường đi của thông báo qua dịch vụ nhắn tin của Firebase: ứng dụng khách đăng ký và nhận thẻ đăng ký, gửi thẻ cho máy chủ ứng dụng lưu lại; máy chủ ứng dụng gửi tin tới Firebase; Firebase xếp hàng nếu máy ngoại tuyến, rồi chuyển qua lớp vận chuyển của nền tảng tới thiết bị. Khung hai, ba điều rút ra từ thử nghiệm: thẻ chết tích tụ nếu không dọn, tin ngoại tuyến cần hạn sống, và tin cùng loại có thể gộp lại.](../../diagrams/sd-12-015-main.svg)

## Từ viết tắt

- **FCM** (Firebase Cloud Messaging) — dịch vụ nhắn tin đám mây của Firebase: nhận tin từ máy chủ ứng dụng, xếp hàng và chuyển tới các thiết bị.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách để chương trình này gọi chương trình khác; ở đây là cách máy chủ ứng dụng gửi tin cho FCM.
- **TTL** (Time To Live) — thời gian sống: khoảng thời gian một tin còn hiệu lực trong hàng đợi; hết hạn mà chưa giao thì bỏ.

## Đọc hình

Bài nguồn mô tả bảy bước, có thể gom thành ba chặng.

**Đăng ký.** Lần đầu mở, ứng dụng gửi thông tin định danh (mã người gửi, khóa, mã ứng dụng) cho FCM, và FCM trả về một thẻ đăng ký cho bản cài đặt đó (còn gọi là mã thể hiện). Mọi thông báo sau này phải kèm thẻ này. Ứng dụng gửi thẻ tới máy chủ ứng dụng, và máy chủ lưu lại để dùng về sau. Vì số thẻ tăng theo thời gian, cách làm được khuyên là lưu thẻ kèm mốc thời gian và định kỳ xóa thẻ cũ.

**Gửi tin.** Có hai cách soạn và gửi: nhập tay trên bảng điều khiển, hoặc gửi từ máy chủ ứng dụng bằng bộ công cụ quản trị Firebase hay bằng giao thức web. FCM nhận tin và, nếu thiết bị đang ngoại tuyến, xếp tin vào hàng đợi lưu trữ.

**Chuyển tới thiết bị.** FCM chuyển tin cho lớp vận chuyển riêng của từng nền tảng (xử lý cấu hình đặc thù của nền tảng đó), rồi tin được định tuyến tới đúng thiết bị, nơi thông báo hiện theo cấu hình máy chủ ứng dụng đã gửi.

## Thử nghiệm

Ngày 2026-10-19, người biên soạn viết một mô phỏng bằng Python. Các con số là tham số tự chọn của mô phỏng, không phải số đo của FCM.

**Thẻ chết tích tụ.** Hệ thống có 100.000 người dùng, mỗi người một thẻ. Mỗi tháng, 3% bản cài đặt được cài lại (thẻ cũ chết, thẻ mới sinh ra) và 2% bị gỡ (thẻ chết, không có thẻ mới); các bản còn lại làm mới mốc thời gian. Sau 12 tháng:

| Cách quản lý thẻ | Số thẻ đang lưu | Thẻ chết | Tỷ lệ thẻ chết |
|---|---|---|---|
| Không dọn | 132.002 | 53.455 | 40,5% |
| Xóa thẻ chết sau 60 ngày im lặng | 82.314 | 4.014 | 4,9% |

Nếu không dọn, cứ 5 lần gửi thì gần 2 lần gửi vào thẻ không còn ai nhận (tốn băng thông, và một số dịch vụ còn trả lỗi cho mỗi lần). Số thẻ còn sống trong hai cách gần như nhau (78.547 và 78.300), nên việc dọn không làm mất người nhận nào.

**Tin ngoại tuyến.** Một tin được gửi vào một thời điểm ngẫu nhiên trong ngày đầu, và máy trở lại mạng sau 1, 6, 24 hoặc 72 giờ. Với thời gian sống 4 giờ, tỷ lệ tin còn hiệu lực khi máy trở lại là 100%, 92,5%, 16,5% và 0%; với thời gian sống 28 ngày thì cả bốn mức đều 100%. Thời gian sống ngắn hợp với tin hết giá trị nhanh (mã xác thực một lần), dài hợp với tin quan trọng không hết hạn. Nếu mười lần cập nhật cùng một mục (ví dụ tỷ số trận đấu) xếp hàng khi máy ngoại tuyến, chỉ lần cuối cùng đáng giao: gộp theo khóa, mười tin còn một.

## Giới hạn cần nhớ

Đây là mô phỏng với tham số tự chọn, không đo hành vi thật của FCM, của hệ điều hành hay của hãng điện thoại (nhiều máy có chế độ tiết kiệm pin chặn thông báo). Việc FCM có giới hạn thời gian sống mặc định, có gộp tin và định dạng cấu hình thế nào không được đối chiếu vì không đọc được tài liệu Firebase trong phiên làm bài; các hành vi đó nên được kiểm lại với tài liệu chính thức trước khi dựa vào.

## Nhìn hình trả lời

Máy chủ ứng dụng của bạn gửi một thông báo khuyến mãi tới 2 triệu thẻ, và 30% trong số đó là thẻ của người đã gỡ ứng dụng từ lâu. Bạn nhận ra điều đó bằng cách nào, và thay đổi gì giúp lần sau không lặp lại?

<details>
<summary>Xem đáp án</summary>

Phần lớn dịch vụ nhắn tin trả về kết quả theo từng thẻ, nên tỷ lệ lỗi "thẻ không còn hợp lệ" cao là dấu hiệu; kiểm tra phản hồi của dịch vụ để xác nhận. Cách khắc phục theo bài nguồn và thử nghiệm: lưu thẻ kèm mốc thời gian (lần cuối thấy ứng dụng hoạt động), xóa thẻ không hoạt động quá một ngưỡng, và xóa ngay thẻ mà dịch vụ báo là không hợp lệ. Đây là suy luận của người biên soạn, chưa đối chiếu với tài liệu của FCM.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn mô tả bảy bước của FCM và khuyên lưu thẻ kèm mốc thời gian để xóa thẻ cũ. Bài này giữ các bước, gom lại thành ba chặng, và thêm hai mô phỏng: thẻ chết tích tụ khi không dọn và thời gian sống của tin ngoại tuyến. Mọi con số là của mô phỏng với tham số tự chọn.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (chỉ dùng thư viện chuẩn) đã in mọi con số của phần thử nghiệm; hạt giống ngẫu nhiên được đặt cố định trong chương trình nên chạy lại ra đúng các số đó.

```python
import random
rnd = random.Random(9)
USERS = 100000

def simulate(cleanup):
    # mỗi người một thẻ; mỗi tháng 3% cài lại (thẻ cũ chết, thẻ mới sinh ra), 2% gỡ ứng dụng (thẻ chết)
    tokens, dead, next_id = {}, set(), [0]
    def new_token():
        next_id[0] += 1
        return next_id[0]
    for user in range(USERS):
        tokens[new_token()] = (user, 0)            # thẻ -> (người dùng, lần cuối thấy hoạt động, tính bằng ngày)
    for month in range(1, 13):
        day = 30 * month
        for t, (user, last_seen) in list(tokens.items()):
            if t in dead:
                continue
            r = rnd.random()
            if r < 0.03:
                dead.add(t); tokens[new_token()] = (user, day)
            elif r < 0.05:
                dead.add(t)
            else:
                tokens[t] = (user, day)            # máy còn sống làm mới mốc thời gian
        if cleanup:                                # xóa thẻ chết đã im lặng từ 60 ngày
            for t, (user, last_seen) in list(tokens.items()):
                if t in dead and day - last_seen >= 60:
                    del tokens[t]
    return len(tokens), sum(1 for t in tokens if t in dead)

for cleanup in (False, True):
    total, dead_count = simulate(cleanup)
    print("dọn" if cleanup else "không dọn", "| thẻ đang lưu", total, "| thẻ chết", dead_count, "| %.1f%%" % (100 * dead_count / total))

def still_valid(offline_hours, ttl_hours, n=1000):
    ok = 0
    for _ in range(n):
        sent = rnd.uniform(0, 24)                  # tin gửi vào một thời điểm ngẫu nhiên của ngày đầu
        if offline_hours - sent <= ttl_hours:      # máy trở lại sau offline_hours giờ
            ok += 1
    return ok / n

for off in (1, 6, 24, 72):
    print("máy trở lại sau", off, "giờ | hạn 4 giờ:", still_valid(off, 4), "| hạn 28 ngày:", still_valid(off, 28 * 24))
queue = {}
for i in range(10):
    queue["score"] = "v%d" % i                     # gộp theo khóa: chỉ giữ tin mới nhất
print("gộp:", queue)
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-are-notifications-pushed-to-our-phones-or-pcs.md): đường đi của thông báo qua FCM, lưu thẻ kèm mốc thời gian.
- Mô phỏng của người biên soạn bằng Python 3 (ngày 2026-10-19): thẻ chết tích tụ và thời gian sống của tin. Tài liệu chính thức của Firebase chưa được đối chiếu.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

# Tám chiến lược đẩy khóa ra, và Redis thật sự có những gì

**Sách liệt kê tám chiến lược: LRU, MRU, SLRU, LFU, FIFO, TTL, bộ đệm hai tầng và thay thế ngẫu nhiên. Khi cấu hình một bộ nhớ đệm thật, câu hỏi thực tế hơn là: phần mềm mình dùng cho chọn những gì, và chọn sai thì chuyện gì xảy ra.**
Bài này đặt tám cái tên cạnh tùy chọn `maxmemory-policy` của Redis 7.0.15 rồi thử từng tùy chọn trên một máy chủ thật.

![Ba khung. Khung một: LRU, LFU và ngẫu nhiên có sẵn dưới dạng allkeys-lru, allkeys-lfu, allkeys-random, bản volatile chỉ chọn khóa có hạn sống; TTL tương ứng với volatile-ttl, bỏ khóa sắp hết hạn trước; FIFO, MRU và SLRU không có trong Redis, memcached thì dùng LRU chia ba vùng nóng, ấm, lạnh; hai tầng là bộ đệm trong tiến trình đứng trước Redis. Khung hai, thử trên Redis với 4 MB: truy cập lệch thì LFU trúng 81, LRU 79, ngẫu nhiên 77 phần trăm; khóa nóng lẫn khóa dùng một lần thì LFU 67, LRU 55; lặp vòng thì LFU 31, ngẫu nhiên 20, LRU 17. Khung ba, bẫy cấu hình: noeviction làm lệnh ghi báo lỗi khi đầy; volatile-lru mà không khóa nào có hạn sống thì y như noeviction.](../../diagrams/sd-06-014-main.svg)

## Từ viết tắt

- **LRU** (Least Recently Used) — ít được dùng gần đây nhất: bỏ khóa đã lâu nhất không ai đụng tới.
- **MRU** (Most Recently Used) — vừa được dùng gần đây nhất: bỏ chính khóa vừa được dùng.
- **SLRU** (Segmented Least Recently Used) — LRU chia vùng: khóa mới vào vùng thử, được dùng lại thì lên vùng được bảo vệ.
- **LFU** (Least Frequently Used) — ít được dùng nhất: bỏ khóa có số lần dùng thấp nhất.
- **FIFO** (First In, First Out) — vào trước ra trước: bỏ khóa được nạp vào sớm nhất.
- **TTL** (Time To Live) — thời gian sống: hạn của một khóa, hết hạn thì khóa tự mất.
- **MB** (MegaByte) — megabyte: đơn vị dung lượng cỡ một triệu byte; ở đây là giới hạn bộ nhớ đặt cho Redis.
- **OOM** (Out Of Memory) — hết bộ nhớ: lỗi Redis trả về khi đã chạm giới hạn mà không được phép xóa bớt khóa.

## Tám cái tên và Redis

Tài liệu eviction của Redis liệt kê các giá trị của `maxmemory-policy`. Đặt cạnh tám cái tên:

| Tên trong sách | Trong Redis |
|---|---|
| LRU | `allkeys-lru`, hoặc `volatile-lru` (chỉ chọn trong các khóa có hạn sống); là bản xấp xỉ, lấy mẫu vài khóa rồi bỏ khóa cũ nhất trong mẫu |
| LFU | `allkeys-lfu`, `volatile-lfu`; cũng xấp xỉ, với bộ đếm giảm dần theo thời gian |
| Thay thế ngẫu nhiên | `allkeys-random`, `volatile-random` |
| TTL | `volatile-ttl`: bỏ khóa còn ít thời gian sống nhất; ngoài ra mọi khóa có hạn đều tự mất khi hết hạn |
| FIFO, MRU, SLRU | không có trong danh sách của Redis |
| Hai tầng | không phải một tùy chọn: ứng dụng tự giữ một bộ đệm nhỏ trong bộ nhớ của tiến trình, đứng trước Redis |

SLRU không có trong Redis nhưng có trong memcached: tài liệu của memcached chia LRU thành các vùng nóng, ấm, lạnh để bảo vệ khóa đang dùng khỏi bị quét lướt đẩy ra. Còn `noeviction` là lựa chọn không đẩy gì ra cả.

## Thử trên Redis

Ngày 2026-10-18, trên một máy, Redis 7.0.15 với `maxmemory 4mb` (chứa khoảng 2.950 khóa 1.000 byte), 60.000 lượt đọc kiểu cache-aside:

| Kiểu truy cập | `allkeys-lru` | `allkeys-lfu` | `allkeys-random` |
|---|---|---|---|
| Lệch (10.000 khóa, Zipf) | 78,8% | 81,2% | 77,4% |
| 70% vào 1.500 khóa nóng, 30% khóa dùng một lần | 55,1% | 67,3% | 51,0% |
| Lặp vòng 6.000 khóa | 16,8% | 31,2% | 19,7% |

LFU thắng ở cả ba kiểu trong phép thử này. LRU của Redis không về 0% khi lặp vòng như LRU chính xác, vì nó chỉ lấy mẫu; tăng `maxmemory-samples` từ 5 lên 10 không đổi kết quả ở kiểu truy cập lệch (78,8%).

**Hai bẫy cấu hình**, đúng như tài liệu cảnh báo:

- `noeviction`: khi đầy, 8.981 lệnh ghi bị từ chối với lỗi OOM. Tỷ lệ trúng vẫn trông ổn (80,1%), nên chỉ nhìn tỷ lệ trúng sẽ không thấy lỗi.
- `volatile-lru` khi không khóa nào có hạn sống: cho đúng kết quả của `noeviction`, cùng 8.981 lỗi. Các chính sách `volatile` chỉ chọn trong khóa có hạn; không có khóa nào như vậy thì chúng không bỏ được gì.

Đặt hạn 600 giây cho mọi khóa rồi dùng `volatile-ttl` thì Redis đẩy ra 11.172 khóa và trúng 76,7%.

## Giới hạn cần nhớ

Kết quả là của một tập dữ liệu giả lập trên một máy, một phiên bản Redis. Bộ đệm hai tầng nhanh nhất nhưng mỗi tiến trình giữ một bản riêng, nên các bản có thể lệch nhau và lệch với Redis; cần hạn sống ngắn cho tầng trong tiến trình. Chọn chính sách theo kiểu truy cập thật và kiểm lại bằng `INFO` (tỷ lệ trúng, `evicted_keys`, lệnh bị từ chối).

## Nhìn hình trả lời

Một máy Redis vừa giữ phiên đăng nhập (có hạn sống) vừa giữ danh mục sản phẩm (không hạn sống), cấu hình `volatile-lru`. Khi đầy, điều gì xảy ra với hai loại dữ liệu này?

<details>
<summary>Xem đáp án</summary>

`volatile-lru` chỉ chọn trong các khóa có hạn sống, nên chỉ phiên đăng nhập bị đẩy ra, kể cả phiên đang dùng, còn danh mục sản phẩm không bao giờ bị đụng tới. Khi hết phiên để bỏ mà vẫn thiếu chỗ, Redis từ chối lệnh ghi như `noeviction` (thử nghiệm: 8.981 lỗi OOM khi không có khóa nào có hạn).
Tài liệu của Redis gợi ý tách thành hai máy Redis khi vừa dùng làm bộ nhớ đệm vừa giữ khóa cần giữ lâu.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn mô tả tám chiến lược như những thuật toán trừu tượng. Bài này nối từng cái tên với tùy chọn của Redis (và memcached cho SLRU), rồi thử trên máy chủ thật, gồm cả hai cấu hình làm lệnh ghi bị từ chối.
Bản Redis mới hơn có thêm vài chính sách (tài liệu hiện hành liệt kê thêm một họ chính sách mới); bài chỉ thử những gì có trong 7.0.15.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-8-cache-eviction-strategies.md): tám chiến lược đẩy khóa ra.
- [Redis — tài liệu eviction, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/reference/eviction/index.md): các giá trị của `maxmemory-policy`; các chính sách `volatile` hành xử như `noeviction` khi không khóa nào có hạn; LRU và LFU xấp xỉ, `maxmemory-samples`; gợi ý tách hai máy.
- [memcached — tài liệu LRU mới, tại bản 1.6.24](https://github.com/memcached/memcached/blob/1b3b8555734f9b7b8d979924c7f8d6cf82194ba8/doc/new_lru.txt): LRU chia vùng nóng, ấm, lạnh.
- [Microsoft — hướng dẫn về bộ nhớ đệm, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/best-practices/caching.md): bộ đệm riêng trong tiến trình và bộ đệm dùng chung; các bản riêng có thể lệch nhau.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày với Redis 7.0.15 và memcached 1.6.24. Bài viết và hình được thiết kế độc lập.

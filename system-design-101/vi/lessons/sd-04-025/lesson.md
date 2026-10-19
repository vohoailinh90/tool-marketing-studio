# Bốn cách chia dữ liệu vào shard: thêm một shard thì bao nhiêu khóa phải dời?

**Chọn cách chia shard là chọn trước cái giá phải trả lúc thêm máy.** Chia theo dải, băm chia dư, băm nhất quán và ô ảo đều trả lời cùng một câu hỏi: khóa này nằm ở shard nào. Chúng khác nhau rõ nhất khi có thêm một shard: bao nhiêu dữ liệu phải chuyển đi, và sau đó các shard có còn đều nhau không. Bài này đếm điều đó trên 100.000 khóa.

![Ba khung dọc. Khung một, bốn cách chọn shard cho một khóa: chia theo dải, mỗi shard giữ một dải id liền nhau; băm chia dư, băm id rồi chia lấy dư cho số shard; băm nhất quán, khóa về shard kế tiếp trên vòng băm; ô ảo, khóa được băm vào 1.024 ô và một bảng tra ghi ô nào thuộc shard nào. Khung hai, số khóa phải dời khi thêm shard thứ năm: theo dải 12.500 nhưng các shard lệch nhau; băm chia dư 79.651, gần 80 phần trăm; băm nhất quán với 100 điểm mỗi shard 20.670; ô ảo 204 ô, 19.993 khóa. Khung ba, hai cái bẫy: id tăng dần dồn mọi id mới vào shard cuối khi chia theo dải; vòng băm chỉ một điểm mỗi shard thì shard lớn gấp hơn ba lần shard nhỏ.](../../diagrams/sd-04-025-main.svg)

## Từ viết tắt

- **SHA** (Secure Hash Algorithm) — thuật toán băm an toàn: phép thử dùng SHA-256 để biến mỗi id thành một con số trông như ngẫu nhiên, rồi dựa vào số đó mà chọn shard.

## Đọc hình

Phép thử: 100.000 khóa là các id từ 1 đến 100.000, chia cho 4 shard, rồi thêm shard thứ năm và đếm khóa nào có shard mới khác shard cũ. Mã ở phần "Xem sâu hơn", chạy bằng Python 3.13 ngày 2026-10-18; số đếm là của bộ khóa này, không phải của một hệ thật.

1. **Chia theo dải.** Mỗi shard giữ một dải id liền nhau: 1 đến 25.000, 25.001 đến 50.000, và cứ thế. Thêm shard bằng cách tách đôi dải cuối: chỉ 12.500 khóa (12,5%) phải dời, nhưng sau đó hai shard giữ 12.500 khóa còn ba shard giữ 25.000. Tệ hơn, id thường được cấp tăng dần, nên 10.000 id mới tiếp theo đều rơi vào shard cuối: một shard gánh mọi lần ghi mới. Bù lại, câu hỏi theo khoảng ("id từ 30.000 đến 31.000") chỉ chạm một shard.
2. **Băm chia dư.** Shard bằng giá trị băm của id chia lấy dư cho số shard. Bốn shard chia rất đều. Nhưng đổi từ chia dư cho 4 sang chia dư cho 5 làm 79.651 khóa (gần 80%) đổi chỗ: gần như cả kho phải chuyển. Một khóa chỉ ở yên khi hai phép chia dư cho cùng kết quả, chuyện xảy ra với khoảng 1 trong 5 khóa.
3. **Băm nhất quán.** Shard và khóa cùng được băm lên một vòng số; khóa thuộc shard đứng kế tiếp nó theo chiều đi của vòng. Shard mới chỉ chen vào vài chỗ trên vòng, nên chỉ khóa ở những chỗ đó dời: 20.670 khóa (21%) khi mỗi shard có 100 điểm trên vòng. Với 1 điểm mỗi shard, các cung rất chênh: bốn shard giữ từ 13.057 đến 43.504 khóa, và shard mới chỉ nhận 2.906. Cassandra gọi các điểm này là token; tệp cấu hình mẫu của nó đặt 16 token cho mỗi máy.
4. **Ô ảo.** Khóa được băm vào 1.024 ô cố định, và một bảng nhỏ ghi ô nào thuộc shard nào. Thêm shard là trao 204 ô từ bốn shard cũ cho shard mới: 19.993 khóa (20%) dời, và năm shard giữ từ 19.922 đến 20.200 khóa. Số ô không đổi, nên chia lại chỉ là sửa bảng tra. Redis Cluster làm theo cách này với 16.384 ô, chọn ô bằng hàm `crc16` của khóa.

## Giới hạn cần nhớ

Phép thử đếm khóa chứ không đo thời gian chuyển dữ liệu thật, và khóa ở đây rải đều. Một khóa "nóng" (một tài khoản có lượng đọc khổng lồ) vẫn làm quá tải shard của nó dù chia theo cách nào. Băm làm mất thứ tự: câu hỏi theo khoảng id phải hỏi mọi shard. Còn chuyện "đụng độ băm" (hai khóa cùng một giá trị băm) không đáng lo ở đây: cách chia nào cũng xếp hàng chục nghìn khóa vào cùng một shard; điều cần là hàm băm rải đều.

## Nhìn hình thử trả lời

Hệ của bạn có 8 shard, chia bằng băm id chia lấy dư cho 8, và sắp thêm shard thứ 9. Khoảng bao nhiêu phần dữ liệu phải chuyển? Nếu đổi sang băm nhất quán hoặc ô ảo thì sao?

<details>
<summary>Xem đáp án</summary>

Một khóa chỉ ở yên khi chia dư cho 8 và cho 9 cùng kết quả, tức khoảng 1 trong 9 khóa. Gần 8 phần 9 dữ liệu (khoảng 89%) phải chuyển; chạy cùng đoạn mã với 8 và 9 shard đếm được 88.874 trên 100.000 khóa.
Với băm nhất quán (đủ nhiều điểm mỗi shard) hoặc ô ảo, chỉ phần mà shard mới cần giữ phải dời, khoảng 1 phần 9 (11%).

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

```python
import bisect, hashlib
from collections import Counter

keys = range(1, 100_001)                       # id 1..100000, cấp tăng dần
h = lambda x: int.from_bytes(hashlib.sha256(str(x).encode()).digest()[:8], "big")
def report(name, old, new, n):
    moved = sum(old(k) != new(k) for k in keys)
    load = Counter(new(k) for k in keys)
    print(f"{name}: dời {moved}, shard ít nhất {min(load.get(s, 0) for s in range(n))}, nhiều nhất {max(load.values())}")

# 1. Theo dải: tách đôi dải cuối thành shard thứ năm
limits4, limits5 = [25_000, 50_000, 75_000, 100_000], [25_000, 50_000, 75_000, 87_500, 100_000]
report("dải", lambda k: bisect.bisect_left(limits4, k), lambda k: bisect.bisect_left(limits5, k), 5)
print("10.000 id mới rơi vào shard", set(min(bisect.bisect_left(limits5, k), 4) for k in range(100_001, 110_001)))

# 2. Băm chia dư
report("mod", lambda k: h(k) % 4, lambda k: h(k) % 5, 5)
report("mod 8 -> 9", lambda k: h(k) % 8, lambda k: h(k) % 9, 9)

# 3. Băm nhất quán: mỗi shard có v điểm trên vòng
def ring(n, v):
    points = sorted((h(f"shard{s}#{i}"), s) for s in range(n) for i in range(v))
    marks = [p for p, _ in points]
    return lambda k: points[bisect.bisect(marks, h(k)) % len(points)][1]
for v in (1, 100):
    r4, r5 = ring(4, v), ring(5, v)
    print(f"vòng v={v}, 4 shard:", sorted(Counter(r4(k) for k in keys).values()))
    report(f"vòng v={v}", r4, r5, 5)

# 4. Ô ảo: 1.024 ô; shard mới nhận 51 ô từ mỗi shard cũ
table4 = {b: b % 4 for b in range(1024)}
table5 = dict(table4)
for s in range(4):
    for b in [b for b in range(1024) if table4[b] == s][:51]:
        table5[b] = 4
print("ô chuyển:", sum(table4[b] != table5[b] for b in range(1024)))
report("ô ảo", lambda k: table4[h(k) % 1024], lambda k: table5[h(k) % 1024], 5)
```

Kết quả chạy: dải dời 12.500; 10.000 id mới đều vào shard số 4 (shard thứ năm); chia dư dời 79.651 (và 88.874 khi từ 8 lên 9 shard); vòng 1 điểm giữ 13.057, 15.365, 28.074 và 43.504 khóa trên bốn shard, dời 2.906; vòng 100 điểm dời 20.670; ô ảo chuyển 204 ô, dời 19.993.

Vòng với 1 điểm mỗi shard lệch vì bốn điểm ngẫu nhiên hiếm khi chia vòng thành bốn cung bằng nhau; nhiều điểm hơn thì các cung nhỏ cộng lại gần bằng nhau. Ô ảo giữ được cả hai điều tốt: số ô cố định nên khóa không bao giờ đổi ô, chỉ có ô đổi chủ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-4-data-sharding-algorithms-explained.md): bốn thuật toán chia shard.
- [Redis — `src/cluster.h`](https://github.com/redis/redis/blob/5e332cabd547d272783cf233a34c81dcb9ea44b3/src/cluster.h) và [`src/cluster.c`](https://github.com/redis/redis/blob/5e332cabd547d272783cf233a34c81dcb9ea44b3/src/cluster.c), tại commit cố định: 16.384 ô, ô của khóa là `crc16` của khóa giữ lại 14 bit thấp. Đọc từ bản clone của kho.
- [Apache Cassandra — `conf/cassandra.yaml`](https://github.com/apache/cassandra/blob/95b178a141824a0414c4add9b5ab87eaa1ca13bf/conf/cassandra.yaml), tại commit cố định: `num_tokens: 16`, số token ngẫu nhiên gán cho mỗi máy trên vòng. Đọc từ bản clone của kho.

Phép thử chạy bằng Python 3.13.16 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

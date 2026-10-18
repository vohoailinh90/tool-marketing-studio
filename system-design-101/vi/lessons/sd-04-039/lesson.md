# Băm nhất quán: vì sao mỗi máy cần nhiều điểm trên vòng

**Băm nhất quán giữ hầu hết khóa ở yên khi số máy thay đổi; nhưng bản đơn giản nhất, mỗi máy một điểm trên vòng, vừa chia rất lệch vừa đổ toàn bộ khóa của máy hỏng lên đúng một máy.** Nguồn giải thích vì sao băm chia dư (máy = băm(khóa) chia dư cho số máy) gây "bão" dời dữ liệu khi thêm hay bớt máy, cách băm nhất quán đặt máy và khóa lên một vòng, và kể vài nơi dùng nó. Bài [Bốn cách chia dữ liệu vào shard](../sd-04-025/lesson.md) đã đếm số khóa phải dời khi thêm máy; bài này đo hai điều còn lại: số điểm mỗi máy làm độ đều thay đổi ra sao, và khi một máy hỏng thì khóa của nó đi đâu.

![Ba khung dọc. Khung một, ba bước tìm máy cho một khóa: băm mỗi máy thành một hoặc nhiều điểm trên vòng số; băm khóa bằng cùng hàm băm; đi theo chiều vòng, khóa thuộc điểm máy gặp đầu tiên. Khung hai, mười máy và 200.000 khóa: một điểm mỗi máy thì máy nhiều nhất giữ 44.980 khóa còn máy ít nhất 1.959; 100 điểm mỗi máy thì từ 18.397 đến 22.186; 1.000 điểm thì từ 18.883 đến 21.128. Khung ba, máy s3 hỏng thì khóa của nó đi đâu: một điểm mỗi máy thì cả 6.889 khóa đổ lên đúng một máy; 100 điểm thì chia cho chín máy, máy nhận nhiều nhất thêm 4.085; còn chia dư từ mười xuống chín máy thì 180.046 khóa đổi chỗ, 90 phần trăm.](../../diagrams/sd-04-039-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt gần người dùng để giữ bản sao của trang web và tệp; nguồn kể Akamai là một ví dụ dùng băm nhất quán.

## Đọc hình

Phép thử chạy bằng Python 3.13.16 ngày 2026-10-18: 10 máy, 200.000 khóa dạng `user:<số>`, hàm băm `sha256` (8 byte đầu). Mã ở phần "Xem sâu hơn"; số đếm là của bộ khóa này.

1. **Ba bước.** Băm mỗi máy (theo tên) thành một hoặc nhiều điểm trên vòng số. Băm khóa bằng cùng hàm. Từ vị trí của khóa đi theo chiều của vòng, điểm máy gặp đầu tiên là máy giữ khóa.
2. **Độ lệch.** Mỗi máy 1 điểm: mười điểm ngẫu nhiên hiếm khi chia vòng thành mười cung đều nhau, nên máy nhiều nhất giữ 44.980 khóa, máy ít nhất chỉ 1.959 (trung bình là 20.000). 10 điểm mỗi máy: từ 8.977 đến 28.645. 100 điểm: từ 18.397 đến 22.186. 1.000 điểm: từ 18.883 đến 21.128. Nhiều cung nhỏ cộng lại thì gần bằng nhau.
3. **Một máy hỏng.** Bỏ máy `s3` khỏi vòng. Với 1 điểm mỗi máy, cả 6.889 khóa của `s3` đổ lên đúng một máy, máy đứng sau nó trên vòng. Với 100 điểm, các khóa đó chia cho cả 9 máy còn lại, máy nhận nhiều nhất thêm 4.085. Để so: với băm chia dư, từ 10 xuống 9 máy làm 180.046 khóa (90%) đổi máy, gần như cả kho.

Cassandra gọi các điểm này là token. Tệp cấu hình mẫu của nó đặt 16 token cho mỗi máy, kèm một thuật toán chọn vị trí token để cân tải thay vì chọn ngẫu nhiên: chọn khéo thì không cần tới hàng trăm điểm.

## Giới hạn cần nhớ

Nhiều điểm hơn không miễn phí: mỗi máy phải biết cả vòng, vòng to thì bảng tra to, và thêm hay bớt một máy chạm tới nhiều máy khác (mỗi máy nhường một ít). Băm nhất quán cân số khóa, không cân lượng truy cập: một khóa rất "nóng" vẫn đè lên một máy. Phép thử chỉ đếm khóa, không chuyển dữ liệu thật. Danh sách nơi dùng (Amazon DynamoDB, Cassandra, Discord, Akamai, bộ cân bằng tải của Google) là theo nguồn; bài chỉ kiểm phần cấu hình của Cassandra.

## Nhìn hình thử trả lời

Một bộ đệm gồm 4 máy dùng băm nhất quán, mỗi máy 1 điểm trên vòng. Một máy hỏng giữa giờ cao điểm, và một máy khác lập tức quá tải rồi hỏng theo. Vì sao, và đổi gì để chuyện này bớt xảy ra?

<details>
<summary>Xem đáp án</summary>

Với 1 điểm mỗi máy, toàn bộ khóa của máy hỏng đổ lên đúng máy đứng sau nó trên vòng, như 6.889 khóa của `s3` trong phép thử. Máy đó gánh gấp đôi (hoặc hơn, nếu cung của máy hỏng vốn lớn), nên dễ hỏng theo, và tải của nó lại đổ tiếp sang máy kế: một chuỗi đổ dây chuyền.
Cho mỗi máy nhiều điểm (với 100 điểm, khóa của máy hỏng chia đều cho mọi máy còn lại), hoặc chọn vị trí điểm có tính toán như cách Cassandra làm; và để mỗi máy chừa dư sức cho phần tải đó.

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

```python
import bisect, hashlib, statistics
from collections import Counter

h = lambda x: int.from_bytes(hashlib.sha256(str(x).encode()).digest()[:8], "big")
keys = [f"user:{i}" for i in range(200_000)]
key_hash = {k: h(k) for k in keys}
servers = [f"s{i}" for i in range(10)]

def ring(names, v):
    points = sorted((h(f"{s}#{i}"), s) for s in names for i in range(v))
    marks = [p for p, _ in points]
    return lambda k: points[bisect.bisect(marks, key_hash[k]) % len(points)][1]

for v in (1, 10, 100, 1000):
    owner = ring(servers, v)
    before = {k: owner(k) for k in keys}
    load = Counter(before.values())
    after_owner = ring([s for s in servers if s != "s3"], v)          # máy s3 hỏng
    moved = Counter(after_owner(k) for k in keys if before[k] == "s3")
    print(f"v={v:4}: máy ít nhất {min(load.values()):6}, nhiều nhất {max(load.values()):6}, "
          f"lệch chuẩn/trung bình {statistics.pstdev(load.values()) / statistics.mean(load.values()):.2f} | "
          f"s3 giữ {load['s3']}, khi hỏng chia cho {len(moved)} máy, máy nhận nhiều nhất thêm {max(moved.values())}")

mod_before = {k: key_hash[k] % 10 for k in keys}
mod_after = {k: key_hash[k] % 9 for k in keys}
print("chia dư 10 -> 9 máy: dời", sum(mod_before[k] != mod_after[k] for k in keys), "trên", len(keys))
```

Tỉ số độ lệch chuẩn trên trung bình (càng nhỏ càng đều) là 0,75 với 1 điểm, 0,31 với 10, 0,06 với 100 và 0,04 với 1.000 điểm mỗi máy.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/consistent-hashing.md): vấn đề của băm chia dư, cách đặt máy và khóa lên vòng, ví dụ thêm một máy, các nơi dùng băm nhất quán.
- [Apache Cassandra — `conf/cassandra.yaml`](https://github.com/apache/cassandra/blob/95b178a141824a0414c4add9b5ab87eaa1ca13bf/conf/cassandra.yaml), tại commit cố định: `num_tokens: 16` và thuật toán tự chọn token để cân tải. Đọc từ bản clone của kho.

Phép thử chạy bằng Python 3.13.16 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

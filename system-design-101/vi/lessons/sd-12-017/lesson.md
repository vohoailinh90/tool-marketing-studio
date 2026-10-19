# Tìm quán gần bạn bằng geohash: chia ô, so tiền tố, và chỗ nó sót

**Geohash đổi một cặp tọa độ thành một chuỗi ký tự sao cho các điểm gần nhau thường có chuỗi bắt đầu giống nhau, nên tìm quán gần bạn chỉ còn là tìm những dòng có cùng tiền tố thay vì tính khoảng cách tới từng quán.**
Bài này giữ cách tạo geohash của bài nguồn, rồi tự chạy thử trên máy để thấy ba điều bài nguồn chỉ nhắc nhẹ: cỡ ô phải hợp với bán kính tìm, ranh giới giữa hai ô làm sót quán, và nơi đông quán làm ô quá tải.

![Hai khung. Khung một, cách tạo geohash: chia Trái Đất thành bốn ô theo đường xích đạo và kinh tuyến gốc, chia mỗi ô thành bốn ô nhỏ hơn, ghép bit kinh độ xen bit vĩ độ thành một mã, rồi tìm quán bằng cách so tiền tố mã. Khung hai, ba điều rút ra từ thử nghiệm: ô phải không nhỏ hơn bán kính tìm, chỉ xét một ô thì sót quán gần ranh giới, và ô ở nơi đông quán chứa rất nhiều quán.](../../diagrams/sd-12-017-main.svg)

## Từ viết tắt

- **LBS** (Location-Based Service) — dịch vụ dựa trên vị trí: dịch vụ trả lời "cho vị trí và bán kính này, quán nào nằm trong đó".
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để hỏi cơ sở dữ liệu, ví dụ lấy mọi dòng có mã bắt đầu bằng một tiền tố.

## Đọc hình

Bài nguồn tách hệ thống thành hai dịch vụ. **Dịch vụ quán** thêm, xóa, sửa thông tin quán và cho khách xem chi tiết. **Dịch vụ dựa trên vị trí** (LBS) nhận một vị trí và một bán kính, trả về danh sách quán gần đó.

Lưu vĩ độ, kinh độ của từng quán rồi tính khoảng cách từ bạn tới mọi quán thì rất chậm. Geohash chia nhỏ việc này:

1. Chia hành tinh thành bốn ô theo xích đạo và kinh tuyến gốc. Mỗi nửa vĩ độ và mỗi nửa kinh độ được ghi bằng một bit (0 cho nửa dưới, 1 cho nửa trên).
2. Chia mỗi ô thành bốn ô nhỏ hơn, thêm bit mới. Các bit được xen kẽ: một bit kinh độ rồi một bit vĩ độ.
3. Dãy bit dài ra theo mỗi lần chia; thành mã càng dài thì ô càng nhỏ. Để gọn, cứ 5 bit đổi thành một ký tự.
4. Tìm quán trong một ô là lấy mọi dòng có mã bắt đầu bằng mã của ô: ví dụ `SELECT * FROM geohash_index WHERE geohash LIKE '01%'`.

Bài nguồn nói rõ một điểm yếu: một ô ở trung tâm thành phố lớn có thể chứa rất nhiều quán, một ô ngoài biển thì không có quán nào, nên còn có những thuật toán phức tạp hơn.

## Thử nghiệm

Ngày 2026-10-19, người biên soạn viết một chương trình Python tự cài geohash (chia bit như trên, bắt đầu bằng bit kinh độ) và chạy thử.

**Cỡ ô theo độ dài mã (ở vĩ độ khoảng 21°).** Tọa độ trung tâm Hà Nội (21,0285 bắc, 105,8542 đông) cho mã sáu ký tự `w7er8u`.

| Độ dài mã | Ô rộng khoảng | Ô cao khoảng |
|---|---|---|
| 4 | 36,5 km | 19,6 km |
| 5 | 4,57 km | 4,89 km |
| 6 | 1,14 km | 0,61 km |
| 7 | 0,14 km | 0,15 km |

**Tìm quán trong 1 km.** 21.500 quán giả lập: 20.000 quán rải đều trong vùng khoảng 20 × 20 km quanh Hà Nội, và một cụm dày 1.500 quán trong 1 × 1 km. 300 vị trí người tìm ngẫu nhiên; kết quả đúng là mọi quán cách người tìm không quá 1 km (tổng cộng 55.139 lượt quán). So hai độ dài mã và hai cách xét ô:

| Độ dài mã | Cách xét | Quán bị sót | Quán phải xét mỗi lượt |
|---|---|---|---|
| 5 (ô khoảng 4,6 × 4,9 km) | chỉ ô chứa người tìm | 15,7% | 1.261 |
| 5 | ô chứa người tìm và tám ô kề | 0% | 9.244 |
| 6 (ô khoảng 1,14 × 0,61 km) | chỉ ô chứa người tìm | 79,1% | 40 |
| 6 | ô chứa người tìm và tám ô kề | 6,5% | 380 |
| (không dùng chỉ mục) | duyệt mọi quán | 0% | 21.500 |

Ba điều rút ra. Một: chỉ xét một ô luôn sót quán, vì người tìm đứng gần ranh giới thì những quán ở bên kia ranh giới nằm ở ô khác, dù rất gần. Hai: xét thêm tám ô kề sửa được chuyện đó khi ô lớn hơn bán kính (mã 5: 0% sót), nhưng chưa đủ khi ô nhỏ hơn bán kính (mã 6 có ô cao 0,61 km, nhỏ hơn 1 km, nên vẫn sót 6,5%). Ba: ô càng lớn thì càng ít sót nhưng phải xét càng nhiều quán; chọn độ dài mã là cân giữa hai điều đó. Với mã 5, ô đông nhất chứa 2.588 quán vì cụm dày nằm gọn trong một ô.

## Giới hạn cần nhớ

Dữ liệu giả lập, phẳng, ở một vùng nhỏ; chương trình tính ô kề bằng cách dịch tọa độ chứ không phải bằng bảng tra của thư viện geohash, và không xử lý vùng sát cực hay sát kinh tuyến 180. Bài không bàn chỉ mục chia theo mật độ như quadtree (bài về quadtree trong cùng nhóm nói chuyện đó) và không đo tốc độ truy vấn thật. Công thức chia bit là kiến thức chung của người biên soạn, đã được thử trên một ví dụ quen thuộc (mã `u4pruydqqvj` cho 57,64911 bắc, 10,40744 đông) nhưng chưa đối chiếu với tài liệu chuẩn vì không đọc được tài liệu đó trong phiên viết bài.

## Nhìn hình trả lời

Ứng dụng của bạn tìm quán trong bán kính 2 km nhưng chỉ lập chỉ mục bằng mã dài 6 ký tự (ô khoảng 1,14 × 0,61 km). Chỉ xét ô chứa người tìm và tám ô kề, bạn có tìm đủ quán không? Nên làm gì?

<details>
<summary>Xem đáp án</summary>

Không đủ: tám ô kề chỉ phủ cỡ 3,4 × 1,8 km quanh người tìm, nhỏ hơn vòng 2 km, nên quán ở xa hơn một ô kề vẫn bị sót (thử nghiệm với bán kính 1 km đã sót 6,5% ở cỡ ô này). Có hai hướng: dùng mã ngắn hơn cho ô lớn hơn bán kính (rồi lọc lại theo khoảng cách thật), hoặc xét thêm nhiều ô xung quanh. Đây là suy luận từ thử nghiệm.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn nêu hai dịch vụ, cách chia bit của geohash, câu truy vấn so tiền tố và điểm yếu về mật độ. Bài này giữ nguyên các ý đó và thêm thử nghiệm đo cỡ ô, phần quán bị sót khi chỉ xét một ô, và hiệu quả của việc xét thêm tám ô kề. Mọi con số là của người biên soạn với dữ liệu giả lập có hạt giống cố định.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (chỉ dùng thư viện chuẩn) đã in mọi con số của phần thử nghiệm; hạt giống ngẫu nhiên được đặt cố định trong chương trình. Phần đo 300 lượt tìm mất khoảng một phút.

```python
import math, random

B32 = "0123456789bcdefghjkmnpqrstuvwxyz"

def encode_bits(lat, lon, nbits):
    """Xen kẽ bit kinh độ và vĩ độ, bắt đầu bằng kinh độ; bit 0 = nửa dưới, bit 1 = nửa trên."""
    lat_lo, lat_hi, lon_lo, lon_hi = -90.0, 90.0, -180.0, 180.0
    bits = []
    for i in range(nbits):
        if i % 2 == 0:
            mid = (lon_lo + lon_hi) / 2
            if lon >= mid: bits.append(1); lon_lo = mid
            else: bits.append(0); lon_hi = mid
        else:
            mid = (lat_lo + lat_hi) / 2
            if lat >= mid: bits.append(1); lat_lo = mid
            else: bits.append(0); lat_hi = mid
    return bits

def geohash(lat, lon, chars):
    bits = encode_bits(lat, lon, chars * 5)
    return "".join(B32[int("".join(map(str, bits[i:i+5])), 2)] for i in range(0, len(bits), 5))

def cell_size_km(chars, lat=21.0):
    nbits = chars * 5
    lon_bits, lat_bits = (nbits + 1) // 2, nbits // 2
    h = 180 / 2**lat_bits * 111.32
    w = 360 / 2**lon_bits * 111.32 * math.cos(math.radians(lat))
    return w, h

def dist_km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 6371 * 2 * math.asin(math.sqrt(d))

def neighbours(lat, lon, chars):
    w, h = cell_size_km(chars, lat)
    dlat, dlon = h / 111.32, w / (111.32 * math.cos(math.radians(lat)))
    return {geohash(lat + i*dlat, lon + j*dlon, chars) for i in (-1, 0, 1) for j in (-1, 0, 1)}

print("Hà Nội 21.0285, 105.8542 ->", geohash(21.0285, 105.8542, 6))
for c in range(3, 9):
    w, h = cell_size_km(c); print(f"độ dài {c}: ô rộng khoảng {w:.2f} km, cao khoảng {h:.2f} km")

rnd = random.Random(4)
# 20.000 quán rải đều trong hình chữ nhật khoảng 20 x 20 km quanh Hà Nội, cộng một cụm dày 1.500 quán trong 1 x 1 km
pts = [(21.0 + rnd.uniform(-0.09, 0.09), 105.85 + rnd.uniform(-0.096, 0.096)) for _ in range(20000)]
pts += [(21.03 + rnd.uniform(-0.0045, 0.0045), 105.85 + rnd.uniform(-0.0048, 0.0048)) for _ in range(1500)]
R = 1.0   # bán kính tìm: 1 km
queries = [(21.0 + rnd.uniform(-0.07, 0.07), 105.85 + rnd.uniform(-0.07, 0.07)) for _ in range(300)]
truths = []
for q in queries:
    truths.append({p for p in pts if abs(p[0]-q[0]) < 0.0125 and abs(p[1]-q[1]) < 0.0125 and dist_km(p, q) <= R})
total_truth = sum(len(t) for t in truths)
print(f"{len(pts)} quán, {len(queries)} lượt tìm trong {R} km, tổng quán đúng {total_truth}")
for CH in (5, 6):
    index = {}
    for p in pts: index.setdefault(geohash(p[0], p[1], CH), []).append(p)
    w, h = cell_size_km(CH)
    print(f"mã dài {CH}: ô khoảng {w:.2f} x {h:.2f} km, {len(index)} ô có quán, ô đông nhất {max(map(len, index.values()))} quán")
    for name, cells in (("ô chứa người tìm", lambda q: {geohash(q[0], q[1], CH)}), ("ô chứa người tìm và tám ô kề", lambda q: neighbours(q[0], q[1], CH))):
        miss = scanned = 0
        for q, truth in zip(queries, truths):
            cand = [p for g in cells(q) for p in index.get(g, [])]
            got = {p for p in cand if dist_km(p, q) <= R}
            miss += len(truth - got); scanned += len(cand)
        print(f"  {name}: sót {miss} quán ({100*miss/total_truth:.1f}%), xét trung bình {scanned/len(queries):.0f} quán mỗi lượt")
print(f"duyệt toàn bộ: {len(pts)} quán mỗi lượt")
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/proximity-service.md): hai dịch vụ, cách chia bit của geohash, truy vấn so tiền tố, điểm yếu về mật độ.
- Thử nghiệm của người biên soạn bằng Python 3 (ngày 2026-10-19): cỡ ô, quán bị sót, xét tám ô kề. Tài liệu chuẩn của geohash chưa được đối chiếu.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

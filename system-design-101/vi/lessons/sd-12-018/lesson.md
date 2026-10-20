# Công cụ tìm kiếm hoạt động thế nào: thu thập, lập chỉ mục và phục vụ kết quả

**Một công cụ tìm kiếm làm ba việc nối nhau: chương trình bò web thu thập trang, hệ thống lập chỉ mục xếp nội dung đã thu thập thành một cấu trúc tra nhanh, và khi có câu hỏi thì dịch vụ phục vụ phân tích câu hỏi, lấy các trang khớp từ chỉ mục rồi xếp hạng.**
Bài này giữ ba việc của bài nguồn, rồi dựng một "web" giả trên máy để đo ba chuyện: thu thập từ vài trang hạt giống tới được bao nhiêu trang, chỉ mục nhanh hơn việc đọc từng trang bao nhiêu, và vì sao khớp từ chưa đủ.

![Hai khung. Khung một, ba việc nối nhau: thu thập, trong đó chương trình bò web đi từ vài trang hạt giống theo liên kết để tải trang; lập chỉ mục, trong đó nội dung trang được phân tích và xếp thành chỉ mục tra từ ra trang; phục vụ kết quả, gồm phân tích truy vấn, truy xuất trang khớp từ chỉ mục, rồi xếp hạng. Khung hai, ba điều rút ra từ thử nghiệm: từ vài hạt giống theo liên kết tới được phần lớn nhưng không phải mọi trang, chỉ mục trả lời nhanh hơn nhiều so với quét từng trang, và xếp hạng cần thứ gì đó hơn việc khớp từ.](../../diagrams/sd-12-018-main.svg)

## Đọc hình

**Thu thập.** Chương trình bò web (crawler) bắt đầu từ một danh sách trang đã biết gọi là hạt giống, tải về từng trang, lấy các liên kết trong đó và đi tiếp theo liên kết để tìm trang mới. Cứ vậy, nó dệt ra một mạng lưới các trang nối với nhau.

**Lập chỉ mục.** Thông tin thu về được phân tích và xếp vào một cơ sở dữ liệu khổng lồ gọi là chỉ mục. Quá trình này trích ra các yếu tố chính như từ khóa, loại nội dung, độ mới, ngôn ngữ và các tín hiệu phân loại khác để hiểu một trang nói về điều gì và hợp với những truy vấn nào.

**Phục vụ kết quả.** Khi người dùng gõ câu hỏi, thuật toán của công cụ lọc chỉ mục để tìm những trang hữu ích nhất, qua ba bước:

- **Phân tích truy vấn:** hiểu nghĩa và ý định của câu hỏi, gồm tìm từ khóa, nhận ra từ đồng nghĩa và đọc ngữ cảnh.
- **Truy xuất:** lấy từ chỉ mục các trang khớp với câu hỏi, bằng cách so từ trong câu hỏi với nội dung đã lập chỉ mục.
- **Xếp hạng:** xếp các trang vừa lấy theo độ liên quan và các yếu tố khác.

## Thử nghiệm: một web giả

Ngày 2026-10-19, người biên soạn viết một chương trình Python dựng một web giả gồm 20.000 trang, mỗi trang có 100 từ lấy từ một bộ từ vựng 2.000 từ theo phân bố kiểu Zipf (từ nhỏ số xuất hiện nhiều hơn) và 2 đến 8 liên kết (70% trỏ tới trang đã được nhiều trang trỏ tới, 30% trỏ tới trang bất kỳ). Dữ liệu là giả, nên các con số chỉ minh họa hình dạng của vấn đề.

**Thu thập từ 3 trang hạt giống.** Đi theo liên kết theo từng lớp (mỗi lớp là các trang cách hạt giống thêm một liên kết), số trang mới tìm thấy ở các lớp 0 đến 11 là 3, 15, 76, 360, 1.658, 5.552, 7.446, 2.888, 481, 54, 5 và 1. Tổng cộng tìm thấy 18.539 trên 20.000 trang; 1.461 trang (7,3%) không tới được từ ba hạt giống vì không có đường liên kết nào dẫn tới chúng từ phía đó. Số trang tìm thấy tăng gần như nhân 5 qua mỗi lớp lúc đầu, rồi chậm lại khi trang mới đã bị tìm thấy gần hết.

**Chỉ mục so với đọc từng trang.** Chỉ mục ở đây là một bảng từ → danh sách trang chứa từ đó (kèm số lần xuất hiện). Tìm trang chứa cả hai từ của câu hỏi bằng hai cách: đọc từng trang (quét), hoặc giao hai danh sách trong chỉ mục.

| Câu hỏi (hai từ) | Trang khớp | Quét từng trang | Tra chỉ mục |
|---|---|---|---|
| `w3` và `w7` (hai từ rất phổ biến) | 13.906 | 54,2 ms | 11,5 ms |
| `w40` và `w200` | 280 | 69,0 ms | 1,1 ms |
| `w300` và `w800` (hai từ hiếm hơn) | 18 | 66,4 ms | 0,2 ms |

Quét tốn thời gian gần như không đổi vì luôn đọc cả 20.000 trang; tra chỉ mục nhanh hơn nhiều khi câu hỏi chọn lọc và chậm lại khi hai từ khớp hầu hết trang. Thời gian đo trên máy của phiên viết bài, nên chỉ dùng để so hai cột với nhau.

**Xếp hạng.** Với câu hỏi `w3` và `w7`, có 13.906 trang khớp: không ai đọc hết chừng đó. Chương trình chấm điểm mỗi trang bằng tần suất của từ trong trang nhân với độ hiếm của từ trong cả web (từ càng hiếm càng có giá trị phân biệt), rồi chỉ giữ vài trang điểm cao nhất. Đây là một cách chấm rất đơn giản; công cụ thật dùng nhiều tín hiệu hơn và bài này không mô tả chúng.

## Giới hạn cần nhớ

Web thật không có cấu trúc như web giả này; các con số về độ phủ (92,7%) và tốc độ chỉ nói về dữ liệu giả với hạt giống ngẫu nhiên cố định. Chương trình không tải trang qua mạng, không tuân theo quy tắc lịch sự của bò web (giới hạn tốc độ, tệp hướng dẫn của trang), không xử lý trang trùng nhau hay trang thay đổi, và không có phân tích truy vấn như nhận ra từ đồng nghĩa. Cách chấm điểm trong thử nghiệm không phải cách của công cụ thật nào. Mô tả ba việc là của bài nguồn; ba thử nghiệm là của người biên soạn.

## Nhìn hình trả lời

Một trang mới ra hôm qua và chưa trang nào trỏ tới nó. Vì sao nó có thể không xuất hiện khi tìm kiếm, và người chủ trang có thể làm gì?

<details>
<summary>Xem đáp án</summary>

Bò web theo liên kết từ các trang đã biết, nên một trang chưa ai trỏ tới thì chưa có đường để tới (giống 1.461 trang không tới được trong thử nghiệm), và nếu chưa thu thập thì chưa vào chỉ mục. Người chủ có thể làm cho có trang đã được biết trỏ tới nó (hoặc báo cho công cụ tìm kiếm địa chỉ của trang, điều người biên soạn biết chung và chưa đối chiếu với tài liệu của công cụ nào).

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn mô tả ba việc, ba bước phục vụ và các tín hiệu mà chỉ mục trích ra, không có con số. Bài này giữ nguyên mô tả đó và thêm ba thử nghiệm trên web giả: độ phủ của thu thập từ hạt giống, chỉ mục so với quét, và một cách chấm điểm xếp hạng đơn giản. Mọi con số là của người biên soạn với dữ liệu giả lập có hạt giống cố định.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (chỉ dùng thư viện chuẩn) đã in mọi con số của phần thử nghiệm, trừ thời gian đo thay đổi theo máy; hạt giống ngẫu nhiên được đặt cố định. Chạy mất khoảng một phút.

```python
import math, random, time
from collections import deque, defaultdict

rnd = random.Random(8)
VOCAB = [f"w{i}" for i in range(2000)]                 # từ vựng giả: w0 ... w1999, từ nhỏ số xuất hiện nhiều hơn
weights = [1 / (i + 1) for i in range(len(VOCAB))]     # phân bố kiểu Zipf
N = 20000                                              # số trang của "web" giả
# mỗi trang có 100 từ và 2 đến 8 liên kết; 70% liên kết tới trang "nổi tiếng" (xác suất tỷ lệ với số trang đã trỏ tới nó), 30% tới trang bất kỳ
pages = {}; indeg = [1] * N
for u in range(N):
    words = rnd.choices(VOCAB, weights, k=100)
    links = set()
    for _ in range(rnd.randint(2, 8)):
        v = rnd.choices(range(N), indeg)[0] if rnd.random() < 0.7 else rnd.randrange(N)
        if v != u: links.add(v)
    for v in links: indeg[v] += 1
    pages[u] = (words, sorted(links))
# ---------- 1. THU THẬP: bắt đầu từ vài trang hạt giống, theo liên kết ----------
seeds = [0, 1, 2]
seen = {s: 0 for s in seeds}; queue = deque(seeds); by_depth = defaultdict(int)
while queue:
    u = queue.popleft(); by_depth[seen[u]] += 1
    for v in pages[u][1]:
        if v not in seen: seen[v] = seen[u] + 1; queue.append(v)
print("trang tìm thấy sau mỗi bước theo liên kết:", dict(sorted(by_depth.items())), "| tổng", len(seen), "trên", N)
unreachable = N - len(seen)
print("trang không tới được từ các hạt giống:", unreachable)
# ---------- 2. LẬP CHỈ MỤC: từ -> danh sách (trang, số lần xuất hiện) ----------
index = defaultdict(dict)
for u in seen:
    for w in pages[u][0]: index[w][u] = index[w].get(u, 0) + 1
print("số từ trong chỉ mục:", len(index))
# ---------- 3. PHỤC VỤ: tìm hai từ ----------
def scan(q):                                          # không có chỉ mục: đọc từng trang
    return [u for u in seen if all(w in pages[u][0] for w in q)]
def lookup(q):                                        # có chỉ mục: giao các danh sách
    lists = sorted((index[w] for w in q), key=len)
    return [u for u in lists[0] if all(u in l for l in lists[1:])]
def rank(q, docs):
    score = {}
    for u in docs:
        score[u] = sum(index[w][u] / 100 * math.log(len(seen) / len(index[w])) for w in q)   # tần suất * độ hiếm của từ
    return sorted(docs, key=lambda u: -score[u])
for q in (["w3", "w7"], ["w40", "w200"], ["w300", "w800"]):
    t = time.perf_counter(); a = scan(q); t1 = time.perf_counter() - t
    t = time.perf_counter(); b = lookup(q); t2 = time.perf_counter() - t
    assert sorted(a) == sorted(b)
    r = rank(q, b)[:3]
    print(f"truy vấn {q}: {len(b)} trang khớp | quét {t1*1000:.2f} ms, tra chỉ mục {t2*1000:.3f} ms | top 3: {r}")
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-search-engines-work.md): ba việc thu thập, lập chỉ mục, phục vụ kết quả; ba bước phân tích truy vấn, truy xuất, xếp hạng.
- Thử nghiệm của người biên soạn bằng Python 3 (ngày 2026-10-19): web giả, thu thập, chỉ mục và xếp hạng. Tài liệu của công cụ tìm kiếm cụ thể chưa được đối chiếu.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

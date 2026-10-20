# Quadtree: chia bản đồ thành bốn ô để tìm quán gần bạn

**Quadtree chia một bản đồ thành bốn ô, ô nào còn quá đông thì chia tiếp thành bốn ô nhỏ hơn, và dừng khi mỗi ô chỉ còn tối đa 100 điểm (ngưỡng dùng trong bài này).**
Tìm quán gần bạn khi đó là đi từ gốc xuống ô chứa bạn thay vì xét hàng triệu quán.

![Hai khung. Khung một, xây quadtree: cả bản đồ là gốc, ô nào có hơn 100 quán thì chia thành bốn ô con, lặp lại cho tới khi không ô nào hơn 100 quán. Khung hai, tìm quán gần bạn: đi từ gốc xuống ô lá chứa vị trí của bạn, nếu ô đủ 100 quán thì trả về, nếu thiếu thì lấy thêm quán từ các ô bên cạnh.](../../diagrams/sd-12-005-main.svg)

## Từ viết tắt

- **LBS** (Location-Based Service) — dịch vụ dựa trên vị trí: máy chủ trả lời câu hỏi kiểu "quán nào gần tôi"; quadtree của bài nằm trong bộ nhớ của từng máy chủ này.

## Đọc hình

**Xây cây.** Gốc là cả bản đồ. Nếu một ô chứa hơn 100 quán (con số ngưỡng của bài nguồn), nó được chia bằng hai đường kẻ giữa thành bốn ô con: trên trái, trên phải, dưới trái, dưới phải. Mỗi ô con lại được kiểm tra như vậy. Kết quả: nơi quán dày (trung tâm thành phố) cây chia sâu thành nhiều ô nhỏ, nơi quán thưa (đồng ruộng) cây dừng sớm với một ô to.

**Tìm quán gần.** Từ gốc, ở mỗi nút chọn ô con chứa vị trí của bạn, đi xuống tới ô lá. Ô lá giữ danh sách quán của nó. Nếu chưa đủ số cần, lấy thêm từ các ô lá kề bên.

**Quadtree nằm trong bộ nhớ, không phải một cơ sở dữ liệu.** Mỗi máy chủ LBS tự dựng cây khi khởi động. Nên khi phát hành bản mới, máy chủ phải dựng lại cây trước khi nhận việc, và bài nguồn khuyên đưa bản mới lên từng nhóm nhỏ máy chủ một để không làm cả cụm ngừng phục vụ cùng lúc.

## Thử nghiệm: ô lá thường chứa bao nhiêu quán?

Ngày 2026-10-19, người biên soạn viết một chương trình Python dựng quadtree (chia khi một ô có hơn 100 điểm), trên các điểm ngẫu nhiên trong một hình vuông. Hai kiểu dữ liệu: **đều** (điểm rải đều) và **cụm** (20 "thành phố", điểm tụ quanh mỗi nơi theo phân bố chuẩn). Sau đó chọn ngẫu nhiên 2.000 trong số chính các điểm đó (tức vị trí của các quán) làm vị trí tìm kiếm, và đếm những lần ô lá chứa vị trí ấy có ít hơn 100 điểm.

| Dữ liệu | Số điểm | Số ô lá | Độ sâu lớn nhất | Số điểm trung bình mỗi lá | Vị trí quán nằm trong lá dưới 100 điểm |
|---|---|---|---|---|---|
| Đều | 100.000 | 2.221 | 6 | 45,0 | 95,8% |
| Đều | 1.000.000 | 16.384 | 7 | 61,0 | 100% |
| Cụm | 100.000 | 2.668 | 11 | 37,5 | 99,2% |
| Cụm | 1.000.000 | 21.583 | 13 | 46,3 | 99,3% |

Ba điều rút ra. Một: vì một ô chỉ bị chia khi vượt 100 điểm, hầu hết ô lá có *ít hơn* 100 điểm, nên bước "lấy thêm từ ô bên cạnh" gần như là trường hợp thường chứ không phải ngoại lệ, ít nhất với người tìm đứng ở những nơi có quán. Hai: dữ liệu càng tụ thì cây càng sâu (độ sâu lớn nhất 13 với dữ liệu cụm so với 7 với dữ liệu đều ở cùng một triệu điểm), nhưng vẫn rất nông so với số điểm. Ba: dựng cây cho một triệu điểm mất khoảng 3,5 giây (đều) và 4,8 giây (cụm) bằng Python thuần trên máy của phiên viết bài; con số này chỉ là thời gian đo được trên máy của phiên viết bài, không so được với máy chủ thật và không dùng để suy ra thời gian cho 200 triệu quán.

## Giới hạn cần nhớ

Quadtree của bài là loại chia theo ngưỡng số điểm (người ta gọi là quadtree chứa theo "xô"); khái niệm quadtree thì rộng hơn, và bài báo gốc về cây bốn nhánh cho dữ liệu nhiều chiều là của Finkel và Bentley năm 1974. Bài nguồn nói dựng cây với 200 triệu quán mất "vài phút"; bài này không kiểm chứng con số đó. Thử nghiệm trên chỉ đo hình dạng của cây, chưa đo tốc độ tìm kiếm, chưa xử lý trường hợp vị trí nằm sát đường biên giữa hai ô, và dữ liệu cụm là dữ liệu giả, không phải bản đồ quán thật. Chương trình còn một ngoại lệ so với ngưỡng 100: nếu hơn 100 điểm trùng đúng một tọa độ, hoặc cây đã chia 40 lần mà các điểm vẫn chưa tách nhau, ô lá giữ nguyên số điểm đó và vượt 100. Dữ liệu ngẫu nhiên của thử nghiệm không rơi vào trường hợp này (độ sâu lớn nhất chỉ 13), nhưng dữ liệu thật có nhiều quán cùng một tòa nhà thì có thể. Vị trí tìm kiếm lấy từ chính vị trí các quán, nên lá đông quán được chọn nhiều hơn và lá trống không bao giờ được chọn; tỷ lệ trong bảng vì vậy là tỷ lệ theo vị trí quán, chưa phải theo vị trí người tìm, vốn có thể ở nơi khác.

## Nhìn hình trả lời

Bạn cần đúng 100 quán gần nhất nhưng ô lá chứa bạn chỉ có 40. Chỉ lấy thêm toàn bộ quán của các ô kề bên có đủ để bảo đảm 100 quán *gần nhất* không?

<details>
<summary>Xem đáp án</summary>

Không đủ để bảo đảm. Ô kề bên có thể chứa quán gần hơn một quán trong ô của bạn (khi bạn đứng sát biên), và quán gần hơn có thể nằm ở một ô không kề. Cách làm trong bài cho 100 quán *ở gần*, đủ tốt cho việc "quán quanh đây"; muốn đúng tuyệt đối cần sắp xếp theo khoảng cách thật và có thể phải xét thêm ô.
Đây là suy luận của người biên soạn; nguồn mô tả cách làm đơn giản và không nói về độ chính xác của nó.

</details>

<details>
<summary>Xem sâu hơn: điều đã bổ sung so với bài nguồn</summary>

Bài nguồn có hai hình, định nghĩa quadtree, ba bước tìm quán gần và đoạn cập nhật máy chủ. Bài này giữ các ý đó và thêm một thử nghiệm để thấy một ô lá thực tế chứa bao nhiêu điểm và cây sâu tới đâu với hai kiểu dữ liệu.
Toàn bộ chương trình của thử nghiệm nằm trong phần "Xem chương trình thử nghiệm" bên dưới; bảng ở trên chạy với hạt giống ngẫu nhiên cố định 7.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (chỉ dùng thư viện chuẩn) đã tạo ra mọi con số trong bảng thử nghiệm. Điểm đều là 1 triệu điểm ngẫu nhiên trong ô vuông đơn vị; điểm tụ là 20 cụm phân phối chuẩn có độ lệch 0,002, 0,005 hoặc 0,01; ô tách khi có hơn 100 điểm; bộ sinh số ngẫu nhiên dùng hạt giống 7. Lưu thành một tệp rồi chạy bằng `python3` sẽ in lại các dòng, trừ thời gian dựng vì thời gian đó thay đổi theo máy.

```python
import random, time, sys
CAP=100
class Node:
    __slots__=("x0","y0","x1","y1","pts","kids","d")
    def __init__(s,x0,y0,x1,y1,d): s.x0,s.y0,s.x1,s.y1,s.d=x0,y0,x1,y1,d; s.pts=[]; s.kids=None
def build(pts,x0,y0,x1,y1,d=0):
    n=Node(x0,y0,x1,y1,d)
    if len(pts)<=CAP or d>=40: n.pts=pts; return n
    mx,my=(x0+x1)/2,(y0+y1)/2
    q=[[],[],[],[]]
    for p in pts: q[(p[0]>=mx)+2*(p[1]>=my)].append(p)
    n.kids=[build(q[0],x0,y0,mx,my,d+1),build(q[1],mx,y0,x1,my,d+1),build(q[2],x0,my,mx,y1,d+1),build(q[3],mx,my,x1,y1,d+1)]
    return n
def stats(n,acc):
    if n.kids is None: acc.append((n.d,len(n.pts)))
    else:
        for k in n.kids: stats(k,acc)
def leaf(n,x,y):
    while n.kids:
        mx,my=(n.x0+n.x1)/2,(n.y0+n.y1)/2
        n=n.kids[(x>=mx)+2*(y>=my)]
    return n
def gen(kind,N,rnd):
    if kind=="uniform": return [(rnd.random(),rnd.random()) for _ in range(N)]
    # clustered: 20 "cities" gaussian, tight
    cs=[(rnd.random(),rnd.random(),rnd.choice([0.002,0.005,0.01])) for _ in range(20)]
    out=[]
    while len(out)<N:
        cx,cy,s=rnd.choice(cs); x,y=rnd.gauss(cx,s),rnd.gauss(cy,s)
        if 0<=x<1 and 0<=y<1: out.append((x,y))
    return out
rnd=random.Random(7)
for kind in ("uniform","clustered"):
  for N in (10000,100000,1000000):
    pts=gen(kind,N,rnd); t=time.time(); root=build(pts,0,0,1,1); bt=time.time()-t
    acc=[]; stats(root,acc)
    depths=[d for d,_ in acc]; sizes=[c for _,c in acc]
    # queries at random data points: how many leaves hold <CAP (need neighbours)
    qs=rnd.sample(pts,2000); small=sum(1 for x,y in qs if len(leaf(root,x,y).pts)<CAP)
    print(f"{kind:9} N={N:8} build={bt:6.2f}s leaves={len(acc):6} maxdepth={max(depths):2} meandepth={sum(depths)/len(depths):4.1f} empty_leaves={sum(1 for s in sizes if s==0)} meanleaf={sum(sizes)/len(sizes):5.1f} queries_in_leaf_lt100={small/20:.1f}%")
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/quadtree.md): định nghĩa quadtree, ngưỡng 100 quán, cách tìm quán gần và chuyện cập nhật máy chủ.
- R. A. Finkel và J. L. Bentley, "Quad trees: a data structure for retrieval on composite keys", Acta Informatica, 1974: bài báo gốc của cấu trúc này (nhớ lại tên; chưa mở được trang trong phiên này).

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

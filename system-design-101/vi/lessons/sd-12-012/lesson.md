# Bản đồ trực tuyến đơn giản hóa: ô bản đồ, vị trí và dẫn đường

**Một ứng dụng bản đồ trực tuyến gồm ba thành phần: dịch vụ vị trí ghi nhận người dùng đang ở đâu, hiển thị bản đồ phát các ô ảnh đã làm sẵn, và dịch vụ dẫn đường tìm tuyến đi.**
Bài này giữ ba thành phần của bài nguồn, rồi tự tính hai việc để thấy vì sao thiết kế như vậy: số ô bản đồ tăng nhanh ra sao theo mức thu phóng, và vì sao tuyến ngắn nhất chưa chắc là tuyến nhanh nhất.

![Hai khung. Khung một, ba thành phần: dịch vụ vị trí ghi lại vị trí người dùng gửi lên, hiển thị bản đồ chia thế giới thành các ô ảnh tĩnh phát từ CDN theo mức thu phóng, dẫn đường tìm vài tuyến ngắn nhất rồi xếp theo thời gian dự đoán. Khung hai, ba điều rút ra từ thử nghiệm: số ô tăng gấp bốn mỗi mức thu phóng, tuyến ngắn nhất chưa chắc nhanh nhất khi có kẹt xe, và việc xếp hạng phải làm sau khi có dự đoán thời gian.](../../diagrams/sd-12-012-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: các máy chủ đặt gần người dùng, giữ bản sao của tệp tĩnh như ô ảnh bản đồ để tải nhanh.

## Đọc hình

**Dịch vụ vị trí.** Ứng dụng trên điện thoại gửi vị trí của người dùng lên máy chủ mỗi vài giây. Dữ liệu này được dùng để phát hiện đường mới hoặc đường vừa đóng, để bản đồ chính xác dần theo thời gian, và làm đầu vào cho dữ liệu giao thông trực tiếp.

**Hiển thị bản đồ.** Cả thế giới được chiếu thành một ảnh phẳng khổng lồ rồi cắt thành các ô nhỏ. Các ô ít đổi nên có thể làm sẵn, lưu ở kho lưu trữ đám mây và phát qua CDN từ nơi gần người dùng. Khi người dùng thu phóng, ứng dụng tải bộ ô của mức thu phóng mới; mỗi mức được tính sẵn từ trước.

**Dẫn đường.** Đây là bước tìm tuyến từ điểm A tới điểm B. Địa chỉ gõ vào trước hết được đổi thành cặp vĩ độ, kinh độ. Rồi dịch vụ lập tuyến làm ba việc theo thứ tự: tìm vài tuyến ngắn nhất, ước tính thời gian cho từng tuyến từ giao thông hiện tại và lịch sử, rồi xếp hạng theo thời gian dự đoán và các lựa chọn của người dùng, chẳng hạn tránh đường thu phí.

## Thử nghiệm

Ngày 2026-10-19, người biên soạn tự tính hai việc bằng Python.

**Số ô bản đồ.** Với cách chia ô phổ biến của các bản đồ trên web (mỗi mức thu phóng chia mỗi ô của mức trước thành bốn), mức 0 có 1 ô, mức 5 có 1.024 ô, mức 10 có 1.048.576 ô, mức 15 có hơn 1,07 tỷ ô, mức 18 có hơn 68,7 tỷ ô. Cộng dồn từ mức 0 tới mức 15 thì được khoảng 1,43 tỷ ô; nếu mỗi ô nặng chừng 15 nghìn byte (một giả định để tính cho dễ, không đo từ hệ thống thật) thì kho ô cho riêng tới mức 15 cỡ 21 terabyte. Vì vậy ô được làm sẵn và phát từ CDN: tính lại mỗi lần người dùng kéo bản đồ sẽ không kham nổi. Ví dụ, tọa độ trung tâm Hà Nội (21,0285 vĩ bắc, 105,8542 kinh đông) rơi vào ô (813, 450) ở mức 10 và ô (26.019, 14.425) ở mức 15: mỗi mức thu phóng thì ô chứa điểm đó thay đổi.

**Tuyến ngắn nhất và tuyến nhanh nhất.** Người biên soạn dựng một lưới đường 40 × 40 nút với độ dài đoạn ngẫu nhiên (hạt giống cố định), tìm ba tuyến ngắn nhất giữa hai nút ở hai góc (thuật toán Dijkstra, rồi Yen cho các tuyến kế tiếp), và được ba tuyến dài 61,65; 61,67 và 61,68. Rồi giả định một đoạn kẹt xe làm chậm gấp ba đúng một đoạn của tuyến ngắn nhất. Thời gian ba tuyến trở thành 101,23; 101,25 và 97,57: tuyến thứ ba, ban đầu dài nhất, trở thành nhanh nhất. Thứ tự theo khoảng cách và thứ tự theo thời gian khác nhau, nên ba bước (tìm tuyến, ước tính thời gian, xếp hạng) phải chạy theo đúng thứ tự đó.

## Giới hạn cần nhớ

Đây chỉ là tính toán trên dữ liệu giả lập. Bản đồ thật dùng đồ thị đường khổng lồ và thuật toán nhanh hơn Dijkstra thuần; bài không bàn chúng, cũng không bàn cách ước tính thời gian từ dữ liệu giao thông. Quy ước chia ô và công thức đổi tọa độ là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn của bản đồ web vì không đọc được tài liệu đó; con số về dung lượng dựa trên giả định 15 nghìn byte mỗi ô.

## Nhìn hình trả lời

Hai tuyến từ A tới B: tuyến một dài 10 km, tuyến hai dài 12 km. Hôm nay tuyến một có một đoạn kẹt xe làm chậm cả tuyến. Dịch vụ lập tuyến chỉ xếp hạng theo độ dài thì người dùng bị gì? Cần thêm gì?

<details>
<summary>Xem đáp án</summary>

Người dùng được gợi ý tuyến một dù tuyến hai có thể nhanh hơn. Cần thêm bước ước tính thời gian cho từng tuyến từ giao thông hiện tại (và lịch sử, cho giờ cao điểm lặp lại), rồi mới xếp hạng. Đây cũng là lý do bài nguồn đặt ước tính thời gian giữa bước tìm tuyến và bước xếp hạng.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn mô tả ba thành phần và các bước của dịch vụ lập tuyến, không có con số nào. Bài này giữ cấu trúc đó, thêm phép tính số ô theo mức thu phóng (kèm giả định dung lượng) và một thử nghiệm tìm tuyến trên lưới đường giả lập để cho thấy thứ tự theo độ dài khác thứ tự theo thời gian. Số liệu về số người dùng của bài nguồn (một tỷ người dùng mỗi ngày, phủ 99% thế giới) không được lặp lại vì không kiểm chứng được.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (chỉ dùng thư viện chuẩn) đã in mọi con số của phần thử nghiệm; hạt giống ngẫu nhiên được đặt cố định trong chương trình nên chạy lại ra đúng các số đó. Con số dung lượng ô (`15KB`) là giả định đã nêu trong bài.

```python
import math, heapq, random
# tiles: standard web mercator slippy tiles
def tile(lat,lon,z):
    n=2**z; x=int((lon+180)/360*n)
    lr=math.radians(lat); y=int((1-math.asinh(math.tan(lr))/math.pi)/2*n); return x,y
print('tiles per zoom', {z:4**z for z in (0,5,10,15,18)})
for z in (0,5,10,15,18): print(z, tile(21.0285,105.8542,z))   # Hanoi
# ground resolution at equator for 256px tiles
for z in (0,10,18): print('m/px at equator z',z, 40075016.686/256/2**z)
# storage estimate if every tile 15 KB: total tiles to z=15
tot=sum(4**z for z in range(16)); print('tiles to z15',tot, 'at 15KB =',tot*15/1e9,'TB')
# route planning: grid graph 40x40, random edge length; k shortest simple paths via Yen's (k=3)
rnd=random.Random(5); W=40
def node(x,y): return y*W+x
adj={}
dist_edge={}
for y in range(W):
    for x in range(W):
        for dx,dy in((1,0),(0,1)):
            nx,ny=x+dx,y+dy
            if nx<W and ny<W:
                d=rnd.uniform(0.8,1.2)
                a,b=node(x,y),node(nx,ny)
                adj.setdefault(a,[]).append((b,d)); adj.setdefault(b,[]).append((a,d)); dist_edge[(a,b)]=dist_edge[(b,a)]=d
def dijkstra(src,dst,banned_nodes=set(),banned_edges=set(),w=None):
    w=w or (lambda a,b:dist_edge[(a,b)])
    D={src:0};P={};h=[(0,src)]
    while h:
        d,u=heapq.heappop(h)
        if u==dst: break
        if d>D[u]: continue
        for v,_ in adj[u]:
            if v in banned_nodes or (u,v) in banned_edges: continue
            nd=d+w(u,v)
            if nd<D.get(v,1e18): D[v]=nd;P[v]=u;heapq.heappush(h,(nd,v))
    if dst not in D: return None
    p=[dst]
    while p[-1]!=src: p.append(P[p[-1]])
    return D[dst],p[::-1]
def yen(src,dst,K):
    A=[dijkstra(src,dst)];B=[]
    for k in range(1,K):
        prev=A[-1][1]
        for i in range(len(prev)-1):
            spur=prev[i];root=prev[:i+1]
            be=set();bn=set(root[:-1])
            for c,p in A:
                if p[:i+1]==root: be.add((p[i],p[i+1]))
            r=dijkstra(spur,dst,bn,be)
            if r:
                total=sum(dist_edge[(root[j],root[j+1])] for j in range(i))+r[0]
                path=root[:-1]+r[1]
                if all(path!=b[1] for b in B) and all(path!=a[1] for a in A): B.append((total,path))
        if not B: break
        B.sort(); A.append(B.pop(0))
    return A
src,dst=node(2,2),node(37,35)
ks=yen(src,dst,3)
print('top3 dist',[round(d,2) for d,_ in ks],'hops',[len(p)-1 for _,p in ks])
# traffic: slow down edges of the best route by 3x ; recompute time
best=set(zip(ks[0][1],ks[0][1][1:]))|set(zip(ks[0][1][1:],ks[0][1]))
def tm(path,jam):
    t=0
    for a,b in zip(path,path[1:]):
        t+=dist_edge[(a,b)]*(3 if (a,b) in jam else 1)
    return t
# jam only the middle third of best route
bp=ks[0][1]; mid=bp[len(bp)//3:2*len(bp)//3]
jam=set(zip(mid,mid[1:]))|set(zip(mid[1:],mid))
print('time under jam',[round(tm(p,jam),2) for _,p in ks])
order=sorted(range(3),key=lambda i:tm(ks[i][1],jam)); print('rank by time',order)
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/design-google-maps.md): ba thành phần dịch vụ vị trí, hiển thị bản đồ, dẫn đường.
- Tính toán và thử nghiệm của người biên soạn bằng Python 3 (ngày 2026-10-19): số ô theo mức thu phóng, ba tuyến ngắn nhất trên lưới giả lập. Quy ước chia ô của bản đồ web chưa được đối chiếu với tài liệu chuẩn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

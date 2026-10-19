# Một lệnh đi qua sàn chứng khoán: đường găng và khớp lệnh lặp lại được

**Khi khách đặt một lệnh mua hoặc bán cổ phiếu, lệnh đi qua một chuỗi bước trên "luồng giao dịch", và chuỗi này phải nhanh vì nó nằm trên đường găng; bộ khớp lệnh ở cuối chuỗi phải cho cùng kết quả mỗi khi phát lại cùng dãy lệnh.**
Bài này đi theo đường đi của một lệnh, rồi thử trên máy xem vì sao việc đánh số thứ tự lệnh lại quan trọng đến vậy.

![Hai khung. Khung một, đường đi của một lệnh: khách đặt lệnh qua công ty môi giới, công ty gửi lệnh tới sàn, cổng khách hàng kiểm tra đầu vào, giới hạn tốc độ và xác thực, người quản lý lệnh kiểm tra rủi ro và số dư, bộ khớp lệnh khớp mua với bán và phát hai bản thực hiện, kết quả trả về cho khách. Khung hai, vì sao thứ tự quan trọng: lệnh và kết quả đều được đánh số thứ tự để phát lại ra đúng kết quả cũ.](../../diagrams/sd-12-014-main.svg)

## Đọc hình

Theo bài nguồn, đường đi của một lệnh qua luồng giao dịch gồm mười bốn bước, gom lại thành năm chặng:

1. **Khách đặt lệnh** qua ứng dụng web hoặc điện thoại của công ty môi giới, và công ty gửi lệnh tới sàn.
2. **Cổng khách hàng** là cửa vào của sàn: kiểm tra dữ liệu nhập, giới hạn tốc độ, xác thực, chuẩn hóa định dạng, rồi chuyển lệnh cho bộ quản lý lệnh.
3. **Quản lý lệnh** kiểm tra rủi ro theo các quy tắc do bộ quản lý rủi ro đặt ra, rồi kiểm tra ví của khách có đủ tiền không.
4. **Khớp lệnh.** Lệnh được gửi tới bộ khớp lệnh. Khi tìm được lệnh đối ứng, bộ khớp lệnh phát ra hai bản thực hiện, một cho bên mua và một cho bên bán. Để kết quả khớp lệnh luôn lặp lại được khi phát lại, cả lệnh lẫn bản thực hiện đều được đánh số thứ tự.
5. **Trả kết quả:** các bản thực hiện quay về khách.

Bài nguồn nhấn mạnh luồng giao dịch (từ bước 1 đến 14) nằm trên đường găng, còn luồng dữ liệu thị trường và luồng báo cáo thì không, nên ba luồng có yêu cầu độ trễ khác nhau.

## Thử nghiệm

Ngày 2026-10-19, người biên soạn viết một sổ lệnh nhỏ bằng Python (ưu tiên giá, rồi tới lệnh vào trước) và chạy thử trên 2.000 lệnh ngẫu nhiên, mỗi lệnh có phía mua hoặc bán, giá từ 95 đến 105 và số lượng từ 1 đến 10.

**Ví dụ nhỏ.** Hai lệnh bán, mỗi lệnh 5 cổ phiếu ở giá 100, vào lần lượt. Rồi một lệnh mua 7 cổ phiếu ở giá 100 đến. Bộ khớp lệnh khớp 5 cổ phiếu với lệnh bán đến trước và 2 cổ phiếu với lệnh bán đến sau.

**Phát lại.** Với dãy 2.000 lệnh, bộ khớp lệnh tạo ra 1.442 lần khớp với tổng khối lượng 4.373. Chạy lại đúng dãy đó thì kết quả giống hệt: cùng thứ tự, cùng giá, cùng khối lượng.

**Đổi thứ tự.** Lấy dãy đó, đổi chỗ hai lệnh liền nhau ở một vị trí ngẫu nhiên rồi chạy lại. Trong 200 lần thử, 51 lần (khoảng 25%) kết quả khớp lệnh thay đổi: có khi người này được khớp thay vì người kia, có khi giá khớp khác đi. Vì vậy bộ khớp lệnh cần một thứ tự đã chốt trước khi bắt đầu: nếu thứ tự lệnh có thể khác nhau giữa hai lần chạy, thì cùng một dãy lệnh đến sàn có thể cho hai kết quả khác nhau, và không ai chứng minh được lần nào đúng.

## Giới hạn cần nhớ

Sổ lệnh trong thử nghiệm đơn giản: chỉ có lệnh giới hạn, không có hủy lệnh, lệnh thị trường, nhiều mã chứng khoán hay nhiều bộ khớp lệnh, và chạy trên một máy, nên không đo độ trễ. Hệ thống thật còn có kiểm tra rủi ro phức tạp, thanh toán bù trừ và quy định riêng của từng sàn; bài không bàn các phần đó. Việc tại sao cần đánh số thứ tự được lấy từ bài nguồn và minh họa bằng thử nghiệm; các con số 1.442, 4.373 và 51 trên 200 là kết quả của dữ liệu ngẫu nhiên này.

## Nhìn hình trả lời

Sàn có hai bộ khớp lệnh chạy song song để dự phòng. Cả hai nhận cùng 10.000 lệnh nhưng một bộ nhận vài cặp lệnh liền nhau theo thứ tự khác. Khi bộ chính hỏng và bộ dự phòng tiếp quản, điều gì có thể xảy ra, và cách phòng tránh là gì?

<details>
<summary>Xem đáp án</summary>

Hai bộ có thể đã khớp khác nhau ở một số lệnh, nên khi chuyển sang bộ dự phòng, kết quả khách đã nhận có thể mâu thuẫn với trạng thái của bộ mới. Cách phòng tránh là cho mọi bộ khớp lệnh nhận cùng một dãy lệnh đã đánh số thứ tự từ một nguồn duy nhất, nên cả hai ra cùng kết quả. Đây là suy luận từ thử nghiệm; bài nguồn chỉ nói rằng lệnh và bản thực hiện được đánh số để kết quả lặp lại được khi phát lại.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn liệt kê các bước theo thứ tự và nêu lý do đánh số thứ tự. Bài này giữ các bước, gom lại thành năm chặng, và thêm một sổ lệnh nhỏ để cho thấy việc đổi chỗ hai lệnh làm thay đổi kết quả khớp trong khoảng một phần tư số lần thử. Quy tắc ưu tiên giá rồi tới thời gian là kiến thức chung của người biên soạn về sổ lệnh, chưa đối chiếu với tài liệu của một sàn cụ thể.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (chỉ dùng thư viện chuẩn) đã in mọi con số của phần thử nghiệm; hạt giống ngẫu nhiên được đặt cố định trong chương trình nên chạy lại ra đúng các số đó.

```python
import heapq, random, itertools
class Book:
    def __init__(s): s.bids=[];s.asks=[];s.n=0
    def submit(s,oid,side,price,qty,seq):
        ex=[]
        if side=='B':
            while qty and s.asks and s.asks[0][0]<=price:
                p,sq,aid,aq=s.asks[0]; m=min(qty,aq); ex.append((oid,aid,p,m)); qty-=m
                if m==aq: heapq.heappop(s.asks)
                else: s.asks[0]=(p,sq,aid,aq-m); heapq.heapify(s.asks)
            if qty: heapq.heappush(s.bids,(-price,seq,oid,qty))
        else:
            while qty and s.bids and -s.bids[0][0]>=price:
                p,sq,bid,bq=s.bids[0]; p=-p; m=min(qty,bq); ex.append((bid,oid,p,m)); qty-=m
                if m==bq: heapq.heappop(s.bids)
                else: s.bids[0]=(s.bids[0][0],sq,bid,bq-m); heapq.heapify(s.bids)
            if qty: heapq.heappush(s.asks,(price,seq,oid,qty))
        return ex
def run(orders):
    b=Book(); ex=[]
    for seq,(oid,side,price,qty) in enumerate(orders):
        ex+=b.submit(oid,side,price,qty,seq)
    return ex
rnd=random.Random(2)
orders=[]
for i in range(2000):
    orders.append((f"o{i}",rnd.choice('BS'),rnd.randint(95,105),rnd.randint(1,10)))
base=run(orders)
print('executions',len(base),'volume',sum(e[3] for e in base))
print('replay same sequence identical:',run(orders)==base)
diff=0
for t in range(200):
    o=orders[:]; 
    i=rnd.randrange(len(o)-1); o[i],o[i+1]=o[i+1],o[i]   # one adjacent swap
    if run(o)!=base: diff+=1
print('one adjacent swap changes executions in',diff,'of 200 trials')
# price-time priority example
b=Book(); print(b.submit('s1','S',100,5,0),b.submit('s2','S',100,5,1),b.submit('b1','B',100,7,2))
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/design-stock-exchange.md): đường đi của một lệnh, đường găng, đánh số thứ tự để lặp lại được.
- Thử nghiệm của người biên soạn bằng Python 3 (ngày 2026-10-19): sổ lệnh đơn giản, phát lại và đổi chỗ hai lệnh. Quy tắc ưu tiên giá rồi thời gian chưa được đối chiếu với tài liệu của một sàn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

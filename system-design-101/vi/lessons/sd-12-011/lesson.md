# Nền tảng thử nghiệm A/B: chia nhóm, ghi nhận, phân tích và ba chỗ dễ sai

**Nền tảng thử nghiệm A/B cho phép đưa hai phiên bản của cùng một tính năng tới hai nhóm người dùng, rồi so kết quả để biết phiên bản nào tốt hơn; nó gồm bốn phần, và phần dễ sai nhất là chia nhóm và đọc kết quả.**
Bài này giải thích bốn phần, rồi chạy thử trên máy ba điều hay làm hỏng thử nghiệm: chia nhóm lệch, hai thử nghiệm chồng lên nhau, và nhìn kết quả giữa chừng.

![Hai khung. Khung một, bốn phần của nền tảng thử nghiệm: định nghĩa và quản lý thử nghiệm, triển khai và chia nhóm, ghi nhận sự kiện, phân tích kết quả. Khung hai, ba chỗ dễ sai: chia nhóm phải ổn định và không tương quan giữa các thử nghiệm, số người mỗi nhóm phải đúng tỷ lệ đã định, và không nhìn kết quả giữa chừng để dừng sớm.](../../diagrams/sd-12-011-main.svg)

## Từ viết tắt

- **UI** (User Interface) — giao diện người dùng: màn hình mà người quản lý thử nghiệm dùng để tạo và sửa thử nghiệm.
- **SRM** (Sample Ratio Mismatch) — lệch tỷ lệ mẫu: số người trong hai nhóm không đúng tỷ lệ đã định, một dấu hiệu cho thấy việc chia nhóm hoặc việc ghi nhận đã có lỗi.

## Đọc hình

Bốn phần của nền tảng, theo thứ tự một thử nghiệm đi qua:

1. **Định nghĩa và quản lý.** Người làm sản phẩm tạo thử nghiệm trên giao diện: tên, các phiên bản (nhóm), tỷ lệ người vào mỗi nhóm, tham số của từng phiên bản. Tất cả được lưu thành cấu hình của hệ thống thử nghiệm.
2. **Triển khai.** Khi người dùng mở ứng dụng, hệ thống quyết định người đó thuộc nhóm nào (chia nhóm) và gửi tham số tương ứng cho cả máy chủ lẫn ứng dụng phía người dùng.
3. **Ghi nhận.** Ứng dụng ghi lại những gì người dùng làm (bấm, mua, thoát), kèm nhóm người đó thuộc về.
4. **Phân tích.** Sau một thời gian, so số liệu của hai nhóm và cho biết khác biệt có đáng tin hay chỉ do may rủi.

## Thử nghiệm: ba chỗ dễ sai

Ngày 2026-10-19, người biên soạn viết một chương trình Python nhỏ (chỉ dùng thư viện chuẩn) và chạy ba thí nghiệm.

**Một. Chia nhóm bằng băm.** Cách chia phổ biến là băm chuỗi `tên thử nghiệm + mã người dùng` rồi lấy phần dư, để cùng một người luôn vào cùng một nhóm mà không cần lưu gì. Với 100.000 người, hàm băm `sha256` chia thành 50.190 người nhóm A và 49.810 người nhóm B: gần 50/50, và người nào cũng ra cùng kết quả ở lần hỏi lại. Nếu hai thử nghiệm dùng chung một chuỗi băm thì hai thử nghiệm giống hệt nhau (ai ở A của thử nghiệm này cũng ở A của thử nghiệm kia). Khi mỗi thử nghiệm có tên riêng trong chuỗi băm, bốn tổ hợp A/B của hai thử nghiệm đều gần 25%, nên việc chia nhóm của hai thử nghiệm gần như không tương quan với nhau. Điều này chưa chứng minh hai tính năng không tác động lên nhau: chuyện đó cần phân tích riêng, hoặc xếp các thử nghiệm dễ tác động chéo vào những lớp loại trừ nhau, mỗi người chỉ ở một lớp.

**Hai. Lệch tỷ lệ.** Nếu thiết kế là 50/50 mà quan sát được 50.400 và 49.600 trên 100.000 người, kiểm định chi bình phương cho p khoảng 0,011, đáng ngờ; với 50.000 và 48.500 thì p cỡ 0,000002, gần như chắc chắn có lỗi (ví dụ ứng dụng ở một nhóm hay bị sập trước khi ghi sự kiện). Kết quả của thử nghiệm đó không nên tin cho tới khi tìm ra lỗi. Ở mức 50.190 và 49.810 của thí nghiệm một, p khoảng 0,23, bình thường.

**Ba. Nhìn giữa chừng.** Giả sử cả hai nhóm có tỷ lệ chuyển đổi đúng bằng nhau (10%), tức là không có gì để phát hiện:

| Cách đọc kết quả | Tỷ lệ báo "có khác biệt" sai |
|---|---|
| Đọc một lần, đúng lúc kết thúc, ngưỡng p < 0,05 | 48 trên 1.000 lần (khoảng 5%) |
| Nhìn mười lần giữa chừng, dừng ngay khi p < 0,05 | 83 trên 500 lần (khoảng 17%) |

Nhìn nhiều lần rồi dừng khi thấy "đẹp" làm tỷ lệ báo sai tăng gấp ba. Muốn nhìn giữa chừng phải dùng phương pháp thống kê dành riêng cho việc đó, hoặc chốt trước thời gian chạy.

Thêm một phép thử về độ nhạy: nếu phiên bản B thật sự tốt hơn (10% lên 11%), thử nghiệm 2.000 người mỗi nhóm chỉ phát hiện ra trong 47 trên 300 lần, còn 20.000 người mỗi nhóm phát hiện ra trong 269 trên 300 lần. Thử nghiệm quá nhỏ không bằng chứng minh là không có khác biệt.

## Giới hạn cần nhớ

Đây là mô phỏng với dữ liệu sinh ngẫu nhiên và chỉ hai nhóm. Nền tảng thật còn phải xử lý người dùng đổi thiết bị, thử nghiệm chạy dài, nhiều chỉ số cùng lúc và cách đo ảnh hưởng chéo giữa người dùng; bài không bàn các phần đó. Nội dung về cấu trúc bốn phần là của bài nguồn, còn ba thí nghiệm là của người biên soạn.

## Nhìn hình trả lời

Một thử nghiệm 50/50 chạy hai tuần, ghi nhận 50.000 người ở nhóm A và 47.000 người ở nhóm B, và nhóm B có tỷ lệ mua cao hơn 8%. Có nên tung phiên bản B ngay không? Bạn kiểm tra gì trước?

<details>
<summary>Xem đáp án</summary>

Chưa nên. 50.000 so với 47.000 là lệch tỷ lệ rõ rệt, nên phải tìm lỗi chia nhóm hoặc ghi nhận (ví dụ phiên bản B làm một phần người dùng bị lỗi và không ghi được sự kiện) trước khi đọc đến con số 8%. Nếu những người "mất" ở nhóm B chủ yếu là người ít mua, tỷ lệ mua của nhóm B cao hơn chỉ vì nhóm đã bị lọc, chứ không vì phiên bản tốt hơn.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn chỉ liệt kê bốn thành phần của nền tảng, trích từ sách "Trustworthy Online Controlled Experiments". Bài này giữ bốn thành phần đó và thêm ba thí nghiệm riêng về chia nhóm, lệch tỷ lệ và nhìn giữa chừng. Cách dùng băm để chia nhóm, kiểm tra lệch tỷ lệ và cảnh báo về nhìn giữa chừng là kiến thức chung của người biên soạn về thử nghiệm trực tuyến, chưa đối chiếu với cuốn sách vì không đọc được bản sách; con số trong bảng là kết quả chạy chương trình, với bộ sinh số ngẫu nhiên cố định.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (chỉ dùng thư viện chuẩn) đã in mọi con số của phần thử nghiệm; hạt giống ngẫu nhiên được đặt cố định trong chương trình nên chạy lại ra đúng các số đó.

```python
import hashlib, math, random
def bucket(user, exp, n=1000):
    h=hashlib.sha256(f"{exp}:{user}".encode()).digest()
    return int.from_bytes(h[:8],'big')%n
def variant(user, exp, split=0.5):
    return 'B' if bucket(user,exp) < split*1000 else 'A'
N=100000
users=[f"u{i}" for i in range(N)]
# 1 balance
cnt={'A':0,'B':0}
for u in users: cnt[variant(u,'checkout-v2')]+=1
print('balance',cnt)
# stability: same user same variant on repeat
print('stable', all(variant(u,'checkout-v2')==variant(u,'checkout-v2') for u in users[:1000]))
# 2 independence across experiments: cross-tab
ct={}
for u in users:
    k=(variant(u,'checkout-v2'),variant(u,'search-v3')); ct[k]=ct.get(k,0)+1
print('cross salted',sorted(ct.items()))
ct={}
for u in users:
    k=(variant(u,'x'),variant(u,'x')); ct[k]=ct.get(k,0)+1
print('cross same salt',sorted(ct.items()))
# 3 A/A test false-positive rate: z-test two proportions
def ztest(a_conv,a_n,b_conv,b_n):
    p=(a_conv+b_conv)/(a_n+b_n); se=math.sqrt(p*(1-p)*(1/a_n+1/b_n))
    z=(b_conv/b_n-a_conv/a_n)/se
    pv=math.erfc(abs(z)/math.sqrt(2)); return z,pv
rnd=random.Random(11)
def run(n,pa,pb):
    a=sum(rnd.random()<pa for _ in range(n)); b=sum(rnd.random()<pb for _ in range(n)); return ztest(a,n,b,n)
R=1000
fp=sum(run(2000,0.10,0.10)[1]<0.05 for _ in range(R))
print('A/A false positives',fp,'of',R)
# 4 power: true lift 10% -> 11% at n=2000 and 20000
for n in (2000,20000):
    pw=sum(run(n,0.10,0.11)[1]<0.05 for _ in range(300))
    print('power n',n,pw,'of 300')
# 5 peeking: A/A, check every 500 users per arm up to 5000, stop at first p<0.05
def peek():
    a=b=0
    for i in range(1,5001):
        a+=rnd.random()<0.10; b+=rnd.random()<0.10
        if i%500==0 and ztest(a,i,b,i)[1]<0.05: return True
    return False
pk=sum(peek() for _ in range(500))
print('peeking false positives',pk,'of 500')
# 6 sample ratio mismatch: 50/50 expected, observed 50.4/49.6 on 100k
def srm(a,b):
    e=(a+b)/2; chi=((a-e)**2+(b-e)**2)/e; return chi, math.erfc(math.sqrt(chi/2))
print('srm ok',srm(cnt['A'],cnt['B']))
print('srm bad',srm(50400,49600))
print('srm bad2 (lost 3% of B)',srm(50000,48500))
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/possible-experiment-platform-architecture.md): bốn thành phần của nền tảng thử nghiệm.
- Thử nghiệm của người biên soạn bằng Python 3 (ngày 2026-10-19): chia nhóm bằng băm, kiểm tra lệch tỷ lệ, nhìn giữa chừng. Cuốn sách mà bài nguồn trích chưa được đối chiếu.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

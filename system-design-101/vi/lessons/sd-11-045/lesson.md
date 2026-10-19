# Tính sẵn sàng cao: ba kiểu hai nút, và phép tính khi nút hỏng cùng lúc

**"Chạy hai nút thay vì một" là cách quen thuộc để tăng tính sẵn sàng, nhưng nó chỉ đúng với hai điều kiện ngầm: hai nút hỏng độc lập với nhau, và việc chuyển sang nút còn lại diễn ra đủ nhanh. Bài xem ba kiểu hai nút của bài nguồn, rồi chạy một mô phỏng để thấy mỗi điều kiện đáng giá bao nhiêu.**
Phép tính trong bài chỉ dùng số học đơn giản và một chương trình nhỏ của người biên soạn.

![Ba khung. Khung một, ba kiểu hai nút: primary-backup có nút dự phòng chờ và chuyển bằng tay; primary-secondary cho nút phụ nhận thêm lượt đọc nhưng đọc có thể cũ; primary-primary cho cả hai nhận ghi nhưng có thể xung đột. Khung hai, phép tính: mục tiêu 99,99 phần trăm chỉ cho phép khoảng 52,6 phút ngừng mỗi năm; hai nút độc lập mỗi nút 90 phần trăm cho 99 phần trăm. Khung ba, mô phỏng mười năm: một nút 90,0 phần trăm; hai nút cùng chạy 99,0; có một phần năm lần hỏng chung thì 98,2; chuyển bằng tay mất 5, 30, 120 phút thì 98,4, 95,2, 90,9 phần trăm.](../../diagrams/sd-11-045-main.svg)

## Từ viết tắt

- **CAP** (Consistency, Availability, Partition) — nhất quán, sẵn sàng, phân mảnh mạng: ba tính chất mà định lý CAP nói một kho dữ liệu phân tán không thể cùng lúc bảo đảm đầy đủ khi mạng đứt. Bài này chỉ dùng chữ A, sẵn sàng.

## Đọc hình

**Sẵn sàng nghĩa là gì.** Bài nguồn dùng nghĩa của định lý CAP: mọi nút còn chạy đều trả lời được yêu cầu trong một thời gian hợp lý, không lỗi, không hết thời gian chờ. Nguồn nhấn mạnh sẵn sàng chỉ bảo đảm có câu trả lời, không bảo đảm đó là dữ liệu mới nhất. Đây là hai tính chất khác nhau: "sẵn sàng" theo CAP là mọi yêu cầu đều nhận được câu trả lời khi mạng bị chia cắt, còn "bốn chín" đo tỷ lệ thời gian hệ thống chạy trong một khoảng thời gian; các phép tính và mô phỏng bên dưới chỉ đo cái sau, không đo sẵn sàng theo CAP. Mục tiêu "bốn chín" là chạy 99,99% thời gian; theo nguồn, đó là chỉ được ngừng khoảng 52,5 phút mỗi năm. Tính lại: một năm 365 ngày có 525.600 phút, 0,01% của số đó là 52,56 phút, nên nguồn đã làm tròn xuống một chút.

**Ba kiểu hai nút.** Nguồn đi từ một nút "Product Inventory" (kho hàng) lên hai nút:

- **Primary-Backup (chính và dự phòng).** Nút dự phòng chỉ chờ, dữ liệu sao từ nút chính sang. Khi nút chính hỏng phải chuyển sang nút dự phòng bằng tay. Nguồn lưu ý nút dự phòng có thể là phần cứng bỏ không.
- **Primary-Secondary (chính và phụ).** Giống kiểu trên, nhưng nút phụ nhận được cả lượt đọc để chia tải. Vì sao chép có độ trễ, dữ liệu đọc từ nút phụ có thể lệch so với nút chính.
- **Primary-Primary (hai nút chính).** Cả hai nút đọc và ghi, dữ liệu sao qua lại giữa hai nút. Thông lượng tăng, nhưng nguồn cảnh báo: nếu cả hai cùng cập nhật một sản phẩm, trạng thái cuối khó đoán, nên dùng thận trọng.

Nguồn kết thêm một ví dụ: nếu mỗi nút triển khai trên `EC2` với tính sẵn sàng 90%, kiến trúc hai nút nâng tính sẵn sàng từ 90% lên 99%.

## Thử: hai điều kiện ngầm đáng giá bao nhiêu

**Phép tính của nguồn.** Hai nút, mỗi nút chạy 90% thời gian, chỉ hỏng cùng lúc khi cả hai cùng hỏng: 0,1 × 0,1 = 0,01, nên còn 99%. Phép nhân này chỉ đúng nếu hai nút hỏng độc lập nhau và việc chuyển nút tức thì. Con số 90% là ví dụ của nguồn; bài này không kiểm nó với cam kết dịch vụ thật của Amazon.

**Một ví dụ cho kiểu hai nút chính.** Kho còn 10 sản phẩm. Trong lúc hai nút chưa kịp sao cho nhau, nút A bán một và ghi "còn 9", nút B cũng bán một và ghi "còn 9". Khi sao chép giá trị qua lại, cả hai cùng báo 9, nhưng thực tế đã bán hai: đáng ra còn 8. Đây là phép tính của người biên soạn, chỉ để minh họa lời cảnh báo của nguồn.

**Mô phỏng mười năm.** Ngày 2026-10-19, người biên soạn viết một chương trình với thời gian ảo, mỗi bước một phút, 5.256.000 phút (mười năm), hạt giống ngẫu nhiên cố định. Mỗi phút, nút đang chạy hỏng với xác suất 1/540 và nút hỏng được sửa xong với xác suất 1/60, tức trung bình chạy 9 giờ rồi sửa 1 giờ, nên một nút chạy khoảng 90% thời gian. Kết quả:

| Cấu hình | Tỷ lệ thời gian có phục vụ |
|---|---|
| Một nút | 90,0% |
| Hai nút cùng chạy, chuyển tức thì, hỏng độc lập | 99,0% |
| Như trên, nhưng 20% khả năng hỏng của mỗi nút đến từ một sự cố chung làm cả hai nút hỏng cùng lúc | 98,2% |
| Chính và dự phòng, chuyển bằng tay mất 5 phút | 98,4% |
| Chính và dự phòng, chuyển bằng tay mất 30 phút | 95,2% |
| Chính và dự phòng, chuyển bằng tay mất 120 phút | 90,9% |

Hai điều rút ra, đều chỉ đúng trong mô hình này. Một: tốc độ chuyển nút quan trọng ngang việc có nút thứ hai; chuyển mất hai giờ gần như xóa hết lợi ích của nút dự phòng. Hai: khi một phần số lần hỏng là chung (cùng nguồn điện, cùng cấu hình), tỷ lệ tụt từ 99,0% xuống 98,2%, nghĩa là ngừng nhiều hơn khoảng 1,8 lần so với phép tính 99%. Với mục tiêu bốn chín (52,56 phút mỗi năm), một lần chuyển bằng tay mất 30 phút đã dùng hơn một nửa quỹ thời gian, nên chỉ chịu được chưa đến hai lần như vậy.

<details>
<summary>Xem chương trình mô phỏng và kết quả</summary>

Chạy `python3 ha.py`; mã nằm trọn ở đây vì bài không thêm tệp mã vào kho. Hạt giống cố định nên kết quả lặp lại.

```python
# Virtual-time availability experiment, 1 step = 1 minute, 10 years, fixed seed.
import random
MIN=10*525600
PF=1/540; PR=1/60   # per-minute failure and repair probability -> single-node availability 0.9
def run(mode, cc=0.0, delay=30, seed=7):
    r=random.Random(seed)
    up=[True,True]; up_minutes=0
    active=0; wait=0
    for t in range(MIN):
        # failures / repairs
        common = r.random() < PF*cc
        for k in (0,1):
            if up[k]:
                if r.random()<PF*(1-cc) or common: up[k]=False
            else:
                if r.random()<PR: up[k]=True
        if mode=='single':
            ok=up[0]
        elif mode=='active-active':
            ok=up[0] or up[1]
        elif mode=='primary-backup':
            if up[active]:
                wait=0; ok=True
            else:
                ok=False
                if up[1-active]:
                    wait+=1
                    if wait>=delay: active=1-active; wait=0; ok=True
        up_minutes+= 1 if ok else 0
    return up_minutes/MIN
for mode in ('single','active-active','primary-backup'):
    print(mode, 'independent', round(run(mode),4), 'with 20% common-cause', round(run(mode,cc=0.2),4))
print('analytic indep two nodes', 1-0.1**2, '4 nines minutes/year', 525600*0.0001)
for d in (5,30,120):
    print('backup delay',d, round(run('primary-backup',delay=d),4))
```

Kết quả chương trình in ra:

```text
single independent 0.9003 with 20% common-cause 0.8995
active-active independent 0.9903 with 20% common-cause 0.982
primary-backup independent 0.9521 with 20% common-cause 0.9478
analytic indep two nodes 0.99 4 nines minutes/year 52.56
backup delay 5 0.9838
backup delay 30 0.9521
backup delay 120 0.9093
```

</details>

## Giới hạn cần nhớ

Mô phỏng chỉ có hai nút, hỏng và sửa theo xác suất cố định mỗi phút, một mức "hỏng chung" cố định do người biên soạn chọn (20% khả năng hỏng của mỗi nút đến từ sự cố chung, nên mỗi nút vẫn chạy khoảng 90%; đây không phải 20% số sự cố của cả hệ thống); hệ thống thật có nhiều tầng, sửa chữa không đều, và có những lỗi (cấu hình sai, quá tải) không theo mô hình ấy. Kiểu chính và phụ (primary-secondary) không được mô phỏng: lượt ghi vẫn chỉ đi qua nút chính nên tính sẵn sàng ghi giống kiểu chính và dự phòng, còn nút phụ chỉ thêm khả năng đọc. Ví dụ 52,56 phút dùng năm 365 ngày; năm 365,25 ngày cho 52,60 phút, nên con số của nguồn đúng với độ chính xác của một phép làm tròn.

## Nhìn hình trả lời

Một đội chọn kiểu chính và dự phòng, chuyển nút bằng tay, mỗi lần mất khoảng 30 phút, và đặt mục tiêu 99,99%. Theo phép tính trong bài, một năm họ chịu được tối đa bao nhiêu lần chuyển nút, nếu không có lý do ngừng nào khác? Điều đó nói gì về việc chuyển bằng tay?

<details>
<summary>Xem đáp án</summary>

Quỹ ngừng một năm là 52,56 phút; chia cho 30 phút mỗi lần được chưa đến 1,8 lần, tức tối đa một lần chuyển, và lần thứ hai đã làm vỡ mục tiêu. Nghĩa là chuyển bằng tay hiếm khi hợp với mục tiêu bốn chín; thường cần chuyển tự động trong vài giây hoặc hai nút cùng phục vụ. Đây là suy luận số học của người biên soạn, nguồn chỉ nói chuyển bằng tay là một đặc điểm của kiểu này.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình, một định nghĩa sẵn sàng theo CAP, con số bốn chín và ba kiểu hai nút kèm một ví dụ 90% lên 99%. Bài này giữ cả ba kiểu và ví dụ, thêm phép tính lại 52,56 phút, ví dụ tồn kho cho kiểu hai nút chính, và mô phỏng mười năm cho hai điều kiện ngầm của phép nhân 0,1 × 0,1.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-design-for-high-availability.md): định nghĩa sẵn sàng theo CAP, mục tiêu bốn chín và 52,5 phút, ba kiểu hai nút, ví dụ `EC2` 90% lên 99%. Phép tính lại, ví dụ tồn kho và mô phỏng là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Con số 90% của `EC2` chưa đối chiếu với cam kết dịch vụ của Amazon (kiến thức chung của người biên soạn, chưa đối chiếu). Mô phỏng là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

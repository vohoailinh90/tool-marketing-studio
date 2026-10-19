# So sánh ba đám mây qua một điểm chung: đếm hai bài so sánh của Microsoft

**Bài nguồn là một tờ "cheat sheet" so sánh dịch vụ của các đám mây (bản 2023), gần như chỉ có ảnh và một dòng giới thiệu; bài này không đọc nội dung ảnh. Thay vào đó, bài lấy hai trang so sánh công khai của Microsoft, một cho người đến từ AWS và một cho người đến từ Google Cloud, và đếm xem Azure đóng vai điểm chung cho bao nhiêu dịch vụ.**
Kết quả là một cách đọc bảng so sánh: dùng nó để tìm điểm xuất phát, không phải để kết luận hai dịch vụ giống nhau.

![Ba khung. Khung một, bài nguồn: một ảnh so sánh dịch vụ bản 2023 và một dòng giới thiệu, ảnh không được đọc. Khung hai, hai trang so sánh của Microsoft: trang cho người dùng AWS có 194 dòng ghép dịch vụ và 203 tên dịch vụ Azure khác nhau; trang cho người dùng Google Cloud có 140 dòng và 146 tên. Khung ba, Azure làm điểm chung: 58 dịch vụ Azure xuất hiện ở cả hai trang; ví dụ Azure Event Hubs ghép với Kinesis Data Streams và với Cloud Pub/Sub, nhưng mỗi cặp chỉ gần tương đương.](../../diagrams/sd-11-047-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon.
- **GCP** (Google Cloud Platform) — tên cũ của Google Cloud; trang Microsoft nhắc tên này trong chú thích.

## Đọc hình

**Bài nguồn có gì.** Phần chữ của bài nguồn chỉ nói đây là "một cheat sheet đẹp về các dịch vụ đám mây khác nhau (bản 2023)" và ghi một bài đăng của khách mời. Mọi so sánh nằm trong ảnh, mà bài này không đọc, nên bài không bàn tới từng dịch vụ trong ảnh.

**Hai trang của Microsoft.** Trang "Azure for AWS professionals" có một trang giới thiệu và mười một trang theo mảng việc (tài khoản, phân tích, tính toán, trí tuệ nhân tạo, cơ sở dữ liệu, nhắn tin, mạng, vùng và khu, quản lý tài nguyên, danh tính, lưu trữ). Trang "Google Cloud to Azure services comparison" là một trang dài với mười sáu mục lớn (chợ ứng dụng, nền tảng dữ liệu, phân tích, trí tuệ nhân tạo, tính toán, mạng, bảo mật, lưu trữ, nhắn tin, công cụ di chuyển...). Cả hai trang đều tự nói là chỉ ghép những dịch vụ gần tương đương, không liệt kê hết, và không bảo đảm khớp từng tính năng. Cả hai trang đều ghi ngày cập nhật trong năm 2026, nên chúng nói về hiện nay, không phải bản 2023 của tờ cheat sheet.

## Thử: đếm Azure làm điểm chung

Ngày 2026-10-19, người biên soạn viết một chương trình đọc các bảng Markdown trong hai trang (kho `MicrosoftDocs/architecture-center`, commit `8e2c239`). Với mỗi dòng có cả cột dịch vụ của nhà cung cấp kia lẫn cột "Azure service", chương trình đếm một dòng và gom tên dịch vụ Azure từ các liên kết trong cột Azure (không phân biệt hoa thường).

| | Trang cho người dùng AWS | Trang cho người dùng Google Cloud |
|---|---|---|
| Dòng ghép dịch vụ | 194 (12 tệp) | 140 (1 tệp) |
| Tên dịch vụ Azure khác nhau | 203 | 146 |

Số tên lớn hơn số dòng vì một ô có thể nêu nhiều dịch vụ Azure. Hai danh sách tên **giao nhau ở 58 dịch vụ Azure**: gần 29% danh sách của trang AWS và gần 40% danh sách của trang Google Cloud. Nhóm chung này gồm các dịch vụ nền như máy ảo, hàm, lưu trữ tệp, tường lửa, phân giải tên miền, quản lý khóa, danh tính và giám sát, cùng `Azure Service Bus`, `Azure Event Hubs` và `Azure Event Grid` ở mảng nhắn tin.

Ví dụ cụ thể: trang AWS ghép `Amazon Kinesis Data Streams` với `Azure Event Hubs`, và `Amazon MQ` với `Azure Service Bus`; trang Google Cloud ghép `Cloud Pub/Sub` với cả `Azure Service Bus` lẫn `Azure Event Hubs`. Đi qua Azure, ta được gợi ý "Kinesis Data Streams và Pub/Sub cùng được Microsoft đặt gần Event Hubs", nhưng đó là hai phép ghép riêng lẻ qua một bên thứ ba, không phải Microsoft nói hai dịch vụ kia tương đương nhau.

<details>
<summary>Xem chương trình đếm</summary>

Chạy `python3 azcount.py` sau khi sửa hằng `BASE` trỏ tới thư mục `docs/` của bản clone commit `8e2c239`; mã nằm trọn ở đây vì bài không thêm tệp mã vào kho. Kết quả in ra: `aws pairs 194 distinct azure 203`, `gcp pairs 140 distinct azure 146`, `both 58`.

```python
import re,glob,collections,sys,os
BASE='/tmp/claude-0/ac/repo/docs/'
def azure_names(path, provider_hdr):
    L=open(path,encoding='utf-8').read().split('\n')
    names=collections.Counter(); pairs=0; i=0
    while i<len(L):
        if L[i].startswith('|') and i+1<len(L) and re.match(r'^\|[\s:\-|]+\|?$',L[i+1]):
            head=[c.strip().lower() for c in L[i].strip().strip('|').split('|')]
            ai=[k for k,h in enumerate(head) if h.startswith('azure service')]
            pi=[k for k,h in enumerate(head) if h.startswith(provider_hdr)]
            j=i+2
            while j<len(L) and L[j].startswith('|'):
                if ai and pi:
                    cells=[c.strip() for c in L[j].strip().strip('|').split('|')]
                    if len(cells)>max(ai[0],pi[0]) and cells[pi[0]]:
                        pairs+=1
                        for txt in re.findall(r'\[([^\]]+)\]\([^)]*\)',cells[ai[0]]): names[txt.strip().lower()]+=1
                j+=1
            i=j; continue
        i+=1
    return names,pairs
aws=collections.Counter(); ap=0
for f in sorted(glob.glob(BASE+'aws-professional/*.md')):
    n,p=azure_names(f,'aws'); aws.update(n); ap+=p
gcp,gp=azure_names(BASE+'gcp-professional/services.md','google cloud')
print('aws pairs',ap,'distinct azure',len(aws)); print('gcp pairs',gp,'distinct azure',len(gcp))
both=sorted(set(aws)&set(gcp)); print('both',len(both)); print(both[:80])
```

</details>

## Giới hạn cần nhớ

Chương trình bỏ các bảng không có cột "Azure service" hoặc không có cột của nhà cung cấp kia (bảng chỉ có hai cột, bảng kiến trúc), nên các con số là phép đếm theo cách đọc này chứ không phải con số chính thức của Microsoft. Ghép dịch vụ do Microsoft viết, từ góc nhìn của Microsoft; AWS và Google Cloud có thể mô tả khác. Việc hai dịch vụ cùng ghép với một dịch vụ Azure không làm chúng tương đương nhau. Nội dung ảnh của bài nguồn không được đối chiếu.

## Nhìn hình trả lời

Bạn dùng `Amazon MQ` và cần tìm thứ gần nhất bên Google Cloud. Theo hai trang trên, bạn đi qua điểm chung nào, và vì sao kết quả chỉ nên coi là nơi bắt đầu đọc?

<details>
<summary>Xem đáp án</summary>

Trang AWS ghép `Amazon MQ` với `Azure Service Bus`, và trang Google Cloud ghép `Cloud Pub/Sub` với `Azure Service Bus`; vậy `Cloud Pub/Sub` là ứng viên đầu tiên để đọc tài liệu. Nhưng đó là hai phép ghép riêng qua Azure, không phải một phép ghép trực tiếp; trang Google Cloud còn ghép `Cloud Pub/Sub` với `Azure Event Hubs`, nên một dịch vụ có thể có nhiều ứng viên, và cả hai trang đều nói không bảo đảm khớp từng tính năng. Đây là suy luận của người biên soạn từ các bảng.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một ảnh so sánh và một dòng giới thiệu. Bài này không dùng ảnh; thay vào đó đọc hai trang so sánh của Microsoft và đếm các dịch vụ Azure xuất hiện ở cả hai.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-comparison-cheat-sheet.md): chỉ có phần chữ ngắn; ảnh không được đọc.
- [Microsoft — Azure for AWS professionals](https://github.com/MicrosoftDocs/architecture-center/tree/8e2c239344ee753a88856800b4210a3e27ac1036/docs/aws-professional) và [Google Cloud to Azure services comparison](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/gcp-professional/services.md): các bảng ghép dịch vụ, tại commit `8e2c239`. Phép đếm là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Phép đếm là của người biên soạn; nội dung ảnh của bài nguồn chưa đối chiếu.
Bài viết và hình được thiết kế độc lập.

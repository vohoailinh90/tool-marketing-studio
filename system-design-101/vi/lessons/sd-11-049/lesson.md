# Bản đồ dịch vụ AWS: chín trang theo cách Microsoft chia, và trang giới thiệu chứa gần một phần ba số dòng ghép dịch vụ ở hai mục Other services và Miscellaneous

**Bài nguồn giới thiệu một tờ hướng dẫn bằng hình để tìm đường trong rất nhiều dịch vụ AWS; nội dung nằm trong ảnh và bài này không đọc ảnh. Thay vào đó, bài hỏi một câu đếm được: khi Microsoft phải xếp các dịch vụ AWS vào những trang để người đến từ AWS tìm lại, họ chia thế nào? Trong 194 dòng ghép dịch vụ, 63 dòng nằm ở trang giới thiệu, trong hai mục `Other services` (53 dòng) và `Miscellaneous` (10 dòng): gần một phần ba.**
Đó là cách Microsoft chia, không phải cách AWS chia, và phép đếm không đo số dịch vụ của AWS.

![Ba khung. Khung một, bài nguồn: một ảnh hướng dẫn các dịch vụ AWS, ảnh không được đọc. Khung hai, chín trang của Microsoft chứa 194 dòng ghép dịch vụ: trang giới thiệu gom 63 dòng, tính toán 27, mạng 24, phân tích 23, lưu trữ 17, cơ sở dữ liệu 13, danh tính 13, trí tuệ nhân tạo và học máy 9, nhắn tin 5. Khung ba, điều cần nhớ: có 183 tên dịch vụ AWS khác nhau, 17 tên nằm ở hai trang, và đây là cách chia của Microsoft chứ không phải của AWS.](../../diagrams/sd-11-049-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon.

## Đọc hình

**Bài nguồn có gì.** Phần chữ của bài nguồn kể rằng AWS đi từ một dự án nội bộ thành nhà dẫn đầu thị trường dịch vụ đám mây, có nhiều dịch vụ đến mức người trong nghề cũng thấy choáng, và giới thiệu tờ hướng dẫn bằng hình như một công cụ giúp chọn đúng dịch vụ. Bài này không kiểm nhận định về thị trường, và không đọc nội dung ảnh.

**Chín trang của Microsoft.** Loạt bài "Azure for AWS professionals" có một trang giới thiệu và mười một trang theo mảng việc. Ba trang (tài khoản, vùng và khu, quản lý tài nguyên) kể về khái niệm, không có bảng ghép dịch vụ. Tám trang còn lại cộng với trang giới thiệu là chín trang có bảng, và chỉ chín trang này đóng góp dòng cho phép đếm.

**Trang giới thiệu cũng là một "kho chứa".** Chính trang này viết "Not every AWS service or Azure service is listed", rồi ở mục sau: "The preceding list doesn't include all services." Trang này có thêm các bảng dưới tiêu đề `Other services` (53 dòng, mười mục) và mục `Miscellaneous` (10 dòng); một số dịch vụ trong đó cũng xuất hiện ở trang theo mảng.

## Thử: đếm dòng theo trang

Ngày 2026-10-19, người biên soạn viết một chương trình đọc các bảng Markdown trong thư mục `docs/aws-professional` (kho `MicrosoftDocs/architecture-center`, commit `8e2c239`). Chương trình chỉ nhận bảng có cả cột "AWS service" và cột "Azure service", và đếm mỗi dòng bảng một lần.

| Trang | Số dòng | Tỷ lệ |
|---|---|---|
| Giới thiệu (hai mục Other services và Miscellaneous) | 63 | 32,5% |
| Tính toán | 27 | 13,9% |
| Mạng | 24 | 12,4% |
| Phân tích | 23 | 11,9% |
| Lưu trữ | 17 | 8,8% |
| Cơ sở dữ liệu | 13 | 6,7% |
| Danh tính | 13 | 6,7% |
| Trí tuệ nhân tạo và học máy | 9 | 4,6% |
| Nhắn tin | 5 | 2,6% |
| Tổng | 194 | 100% |

Bên trong 63 dòng của trang giới thiệu, mục lớn nhất là `Management and governance` (quản lý và quản trị) với 16 dòng, nhiều hơn cả trang cơ sở dữ liệu (13 dòng). Sau đó là `Miscellaneous` (10), `Web applications` (7), rồi ba mục 6 dòng: `DevOps and application monitoring`, `Internet of Things (IoT)` và `Authentication and authorization`. Bảo mật cũng bị rải ra: trang danh tính có 13 dòng, và bốn mục bảo mật của trang giới thiệu (`Authentication and authorization`, `Encryption`, `Firewalls`, `Security`) thêm 16 dòng.

Về tên dịch vụ: lấy chữ của các liên kết trong cột AWS (không phân biệt hoa thường), có 214 lượt nhắc nhưng chỉ 183 tên khác nhau: 17 tên xuất hiện ở hai trang, và vài tên lặp lại ngay trong một trang. Ví dụ `Amazon Lightsail` nằm ở trang tính toán và trong mục ứng dụng web của trang giới thiệu; `Amazon Kinesis Data Streams` nằm ở trang phân tích và trang nhắn tin. Mười bốn trong 17 trường hợp trùng có một trang là trang giới thiệu.

Tự thử: chọn ba dịch vụ bạn biết, đoán trang nào sẽ chứa chúng, rồi tìm. `AWS CloudFormation` nằm ở trang giới thiệu, mục `DevOps and application monitoring`; `AWS Step Functions` nằm ở cả trang tính toán lẫn trang giới thiệu; `Amazon Lightsail` như trên.

<details>
<summary>Xem chương trình đếm và kết quả</summary>

Lưu mã dưới đây vào một tệp tên `count.py`, rồi chạy `python3 count.py <thư mục docs/aws-professional>` trên bản clone commit `8e2c239`; mã nằm trọn ở đây vì bài không thêm tệp mã vào kho.

```python
import re, glob, collections, sys
root = sys.argv[1]  # .../docs/aws-professional
rows = collections.Counter(); where = collections.defaultdict(set)
mult = 0; mentions = 0; idx = collections.Counter()
for f in sorted(glob.glob(root + "/*.md")):
    page = f.split("/")[-1]; L = open(f, encoding="utf-8").read().split("\n"); sec = ""; i = 0
    while i < len(L):
        m = re.match(r"^(##+) (.*)", L[i])
        if m: sec = m.group(2).strip()
        if L[i].startswith("|") and i + 1 < len(L) and re.match(r"^\|[\s:\-|]+\|?$", L[i + 1]):
            head = [c.strip().lower() for c in L[i].strip().strip("|").split("|")]
            ai = [k for k, h in enumerate(head) if h.startswith("azure service")]
            pi = [k for k, h in enumerate(head) if h.startswith("aws")]
            j = i + 2
            while j < len(L) and L[j].startswith("|"):
                c = [x.strip() for x in L[j].strip().strip("|").split("|")]
                if ai and pi and len(c) > max(ai[0], pi[0]) and c[pi[0]]:
                    rows[page] += 1
                    if page == "index.md": idx[sec] += 1
                    names = [t.strip().lower() for t in re.findall(r"\[([^\]]+)\]\([^)]*\)", c[pi[0]])]
                    mult += len(names) > 1; mentions += len(names)
                    for t in names: where[t].add(page)
                j += 1
            i = j; continue
        i += 1
print("rows", sum(rows.values()), dict(rows))
print("index sections", dict(idx))
print("mentions", mentions, "distinct", len(where), "on two pages", sum(len(v) > 1 for v in where.values()),
      "with index", sum(len(v) > 1 and "index.md" in v for v in where.values()), "multi-name rows", mult)
```

Kết quả: `rows 194`, `mentions 214 distinct 183 on two pages 17 with index 14 multi-name rows 15`, cùng số dòng theo trang và theo mục ở bảng trên.

</details>

## Giới hạn cần nhớ

Số dòng không phải số dịch vụ: một ô có thể nêu nhiều dịch vụ AWS (15 dòng làm vậy), và một dịch vụ có thể có hai dòng ở hai trang. 183 cũng không phải số dịch vụ của AWS, vì Microsoft tự nói không liệt kê hết, và ô không có liên kết không được đếm tên. Cách chia chín trang là của Microsoft, viết cho người học Azure; cách chia của chính AWS không được đọc ở đây. Các trang ghi ngày cập nhật năm 2026, nên bản sau có thể khác. Ảnh của bài nguồn không được đối chiếu, nên bài không nói gì về cách tờ hướng dẫn chia nhóm.

## Nhìn hình trả lời

Bạn dựng bản đồ dịch vụ AWS cho đồng đội và chia thành chín nhóm như các trang của Microsoft. Vì sao nên để sẵn một nhóm "khác", và nên làm gì với nhóm đó?

<details>
<summary>Xem đáp án</summary>

Vì trong cách chia của Microsoft, 63 trên 194 dòng (32,5%) nằm ở hai mục `Other services` và `Miscellaneous` của trang giới thiệu (con số đo các dòng ở đó, không chứng minh dịch vụ nào thiếu trang theo mảng, vì 14 tên còn xuất hiện ở cả hai nơi), nên một bản đồ chỉ có chín chủ đề thiếu chỗ cho một phần đáng kể các dòng (tối đa 63 trên 194; số dịch vụ chỉ có ở đó thấp hơn, và bài không đếm số này). Nhóm "khác" cần được chia mục nhỏ, như Microsoft chia trang giới thiệu thành mười một mục. Cũng cho phép một dịch vụ có hai nhà, vì 17 trong 183 tên xuất hiện ở hai trang. Đây là suy luận của người biên soạn từ một cách chia, không phải quy tắc chung.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một ảnh hướng dẫn và vài đoạn chữ. Bài này không dựng lại ảnh; thay vào đó, đọc các trang của Microsoft và đếm dòng theo trang để thấy một bản đồ dịch vụ phải chia nhóm thế nào và nhóm "khác" lớn đến đâu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/aws-services-cheat-sheet.md): chỉ có phần chữ ngắn; ảnh không được đọc.
- [Microsoft — Azure for AWS professionals](https://github.com/MicrosoftDocs/architecture-center/tree/8e2c239344ee753a88856800b4210a3e27ac1036/docs/aws-professional): các bảng ghép dịch vụ tại commit `8e2c239`; trang `index.md` là trang giới thiệu.

Đã đọc nguồn ngày 2026-10-19. Phép đếm là của người biên soạn; nội dung ảnh của bài nguồn chưa đối chiếu.
Bài viết và hình được thiết kế độc lập.

# Tải một tệp lên kho đối tượng kiểu `S3`: dữ liệu và siêu dữ liệu ở hai nơi

**Trong một kho đối tượng kiểu `S3`, nội dung tệp và thông tin mô tả nó được lưu ở hai nơi khác nhau; thứ tự ghi hai nơi đó quyết định một sự cố giữa chừng để lại thứ gì.**
Bài này giữ cách chia xô, đối tượng và hai kho của bài nguồn, rồi thử trên máy hai thứ tự ghi để xem mỗi thứ tự hỏng theo kiểu nào.

![Hai khung. Khung một, sau khi khách gọi PUT: dịch vụ API kiểm tra quyền, gửi dữ liệu cho kho dữ liệu và nhận lại mã UUID của đối tượng, rồi ghi một dòng siêu dữ liệu vào kho siêu dữ liệu và báo thành công cho khách. Khung hai, ba điều rút ra: dữ liệu được lưu trước, siêu dữ liệu ghi sau; sự cố giữa hai bước để lại dữ liệu mồ côi mà không ai trỏ tới; dữ liệu mồ côi được dọn bằng cách quét định kỳ.](../../diagrams/sd-12-016-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cổng để chương trình khác gọi vào; ở đây là dịch vụ nhận yêu cầu tải lên.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách khách gửi yêu cầu `PUT` để tạo xô hoặc đối tượng.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để hỏi và ghi cơ sở dữ liệu; SQLite là một cơ sở dữ liệu nhỏ chạy trong chương trình dùng ngôn ngữ này.
- **IAM** (Identity and Access Management) — quản lý danh tính và quyền truy cập: dịch vụ trả lời "người này là ai và có được ghi vào xô này không".
- **UUID** (Universally Unique IDentifier) — mã định danh duy nhất toàn cầu: chuỗi đủ dài và ngẫu nhiên để hai đối tượng hầu như không bao giờ trùng mã.

## Đọc hình

`S3` là tên dịch vụ lưu trữ đối tượng của Amazon; bài nguồn lấy nó làm hình mẫu cho thiết kế.

**Hai khái niệm.** Xô (bucket) là một thùng chứa có tên duy nhất trên toàn hệ thống; muốn tải gì lên, trước hết phải tạo xô. Đối tượng (object) là một mẩu dữ liệu nằm trong xô, gồm hai phần: **siêu dữ liệu**, có thể sửa, chứa mã đối tượng, tên xô, tên đối tượng; và **dữ liệu**, bất biến, là chính dãy byte của tệp. Đường dẫn trông như `/bucket-to-share/script.txt`. Xô chỉ có siêu dữ liệu, còn đối tượng có cả siêu dữ liệu lẫn dữ liệu.

**Tải tệp lên.** Sau khi xô đã được tạo (qua một yêu cầu HTTP `PUT` khác), khách gửi `PUT` để tạo đối tượng `script.txt`:

1. Dịch vụ API kiểm tra danh tính và quyền ghi vào xô, nhờ IAM.
2. Kiểm tra xong, dịch vụ API gửi dữ liệu của tệp cho kho dữ liệu. Kho dữ liệu lưu lại và trả về mã UUID của đối tượng.
3. Dịch vụ API gọi kho siêu dữ liệu để tạo một dòng mới: mã đối tượng (UUID), mã của xô chứa nó, tên đối tượng và các thông tin khác.

Hai kho tách riêng vì hai việc khác nhau: tra cứu theo tên và quyền (siêu dữ liệu, nhỏ, cần truy vấn) và lưu khối byte lớn (dữ liệu, to, ít khi đọc theo cách khác ngoài "đưa mã, trả về nội dung").

## Thử nghiệm: thứ tự ghi hai kho

Ngày 2026-10-19, người biên soạn viết một chương trình Python nhỏ (SQLite làm kho siêu dữ liệu, một bảng băm trong bộ nhớ làm kho dữ liệu) và mô phỏng 1.000 lượt tải lên, mỗi lượt có 5% khả năng gặp sự cố đúng giữa hai bước ghi. Hai cách chạy dùng cùng hạt giống nên gặp đúng cùng 45 sự cố.

| Thứ tự ghi | Sự cố | Siêu dữ liệu trỏ vào chỗ trống | Dữ liệu mồ côi |
|---|---|---|---|
| Dữ liệu trước, siêu dữ liệu sau (như bài nguồn) | 45 | 0 | 45 |
| Siêu dữ liệu trước, dữ liệu sau | 45 | 45 | 0 |

Hai thứ tự hỏng khác nhau. Nếu ghi siêu dữ liệu trước, 45 đối tượng "tồn tại" trong danh sách nhưng đọc ra thì không có gì: lỗi người dùng nhìn thấy ngay. Nếu ghi dữ liệu trước, 45 khối dữ liệu nằm đó mà không dòng siêu dữ liệu nào trỏ tới: người dùng không thấy gì, chỉ tốn chỗ. Loại sau dọn được bằng một lượt quét: lấy mọi mã trong kho dữ liệu, xóa mã nào không có trong siêu dữ liệu. Trong thử nghiệm, quét như vậy xóa đúng 45 khối mồ côi và để lại 955 đối tượng đều có siêu dữ liệu.

Một điều nữa từ tính chất "dữ liệu bất biến": ghi đè một tệp cùng tên không sửa khối cũ mà tạo khối mới rồi trỏ lại. Ghi đè ba lần cùng một tên thì kho giữ ba khối nhưng chỉ một khối được trỏ tới, hai khối còn lại là rác chờ lượt quét.

## Giới hạn cần nhớ

Đây là mô phỏng trên một máy, không có mạng, không có nhiều bản sao, không có yêu cầu đồng thời. Bài nguồn mô tả một thiết kế đơn giản hóa lấy `S3` làm hình mẫu, không nói đây là cách Amazon vận hành thật; bài này cũng không nói vậy. Các điều về việc xóa, phiên bản đối tượng, tải lên nhiều phần và sao lưu nhiều bản không được bàn. Kết luận "dữ liệu trước là thứ tự an toàn hơn" là của người biên soạn rút ra từ thử nghiệm, không phải lời của bài nguồn.

## Nhìn hình trả lời

Người dùng bấm xóa một tệp. Dịch vụ cần xóa cả dòng siêu dữ liệu lẫn khối dữ liệu. Nên xóa cái nào trước, và vì sao?

<details>
<summary>Xem đáp án</summary>

Nên xóa dòng siêu dữ liệu trước, khối dữ liệu sau. Nếu sự cố xảy ra giữa hai bước, thứ còn lại là một khối dữ liệu mồ côi, và lượt quét sẽ dọn nó, giống tình huống tải lên theo thứ tự dữ liệu trước. Nếu xóa dữ liệu trước rồi sự cố, danh sách vẫn thấy tệp nhưng đọc ra thì lỗi, giống thứ tự tải lên "siêu dữ liệu trước" trong bảng. Đây là suy luận từ thử nghiệm; bài nguồn không nói về việc xóa.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn định nghĩa xô và đối tượng, rồi kể bảy bước tạo xô và tải một tệp lên. Bài này giữ các khái niệm và bước tải lên (gom bảy bước thành ba chặng), và thêm thử nghiệm so hai thứ tự ghi, lượt quét dọn rác và chuyện ghi đè. Mọi con số của thử nghiệm là của người biên soạn với dữ liệu ngẫu nhiên có hạt giống cố định.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (chỉ dùng thư viện chuẩn, SQLite trong bộ nhớ) đã in mọi con số của phần thử nghiệm; hạt giống ngẫu nhiên được đặt cố định trong chương trình.

```python
import random, sqlite3, uuid

N = 1000          # số lượt tải lên
FAULT = 0.05      # xác suất sự cố ngay giữa hai bước ghi

def run(order):
    rnd = random.Random(21)                          # cùng hạt giống nên hai cách gặp đúng cùng các sự cố
    data_store = {}                                  # object_id -> payload (kho dữ liệu)
    db = sqlite3.connect(":memory:")                 # kho siêu dữ liệu
    db.execute("create table object(bucket text, name text, object_id text, size integer, primary key(bucket, name))")
    faults = 0
    for i in range(N):
        name = f"file{i}.txt"
        payload = bytes([i % 256]) * rnd.randint(10, 100)
        oid = str(uuid.UUID(int=rnd.getrandbits(128), version=4))
        crash = rnd.random() < FAULT                 # sự cố xảy ra giữa bước ghi thứ nhất và bước thứ hai
        if order == "data-first":                    # như bài nguồn: lưu dữ liệu trước, ghi siêu dữ liệu sau
            data_store[oid] = payload
            if crash:
                faults += 1
                continue
            db.execute("insert into object values(?,?,?,?)", ("b", name, oid, len(payload)))
        else:                                        # đảo ngược: ghi siêu dữ liệu trước, lưu dữ liệu sau
            db.execute("insert into object values(?,?,?,?)", ("b", name, oid, len(payload)))
            if crash:
                faults += 1
                continue
            data_store[oid] = payload
    refs = {r[0] for r in db.execute("select object_id from object")}
    dangling = sum(1 for o in refs if o not in data_store)        # siêu dữ liệu trỏ vào dữ liệu không có
    orphans = [o for o in data_store if o not in refs]            # dữ liệu không ai trỏ tới
    return faults, dangling, len(orphans), data_store, orphans

for order in ("data-first", "metadata-first"):
    f, d, o, store, orph = run(order)
    print(f"{order:15} sự cố {f} | siêu dữ liệu trỏ vào chỗ trống {d} | dữ liệu mồ côi {o}")
f, d, o, store, orph = run("data-first")
for oid in orph: del store[oid]                       # dọn rác: xóa dữ liệu không được trỏ tới
print("data-first sau khi dọn rác: đã xóa", len(orph), "dữ liệu mồ côi, còn lại", len(store), "đối tượng đều có siêu dữ liệu")
# ghi đè cùng tên: dữ liệu là bất biến nên ghi đè = dữ liệu mới + trỏ lại, dữ liệu cũ thành rác
db = sqlite3.connect(":memory:"); db.execute("create table object(name text primary key, object_id text)")
store = {}
for version in range(3):
    oid = f"v{version}"; store[oid] = b"x"
    db.execute("insert or replace into object values('a.txt', ?)", (oid,))
refs = {r[0] for r in db.execute("select object_id from object")}
print("ghi đè 3 lần cùng tên: dữ liệu đang lưu", len(store), "| còn được trỏ tới", len(refs), "| rác", len(store) - len(refs))
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-happens-when-you-upload-a-file-to-amazon-s3.md): xô, đối tượng, luồng tải lên với dịch vụ API, IAM, kho siêu dữ liệu và kho dữ liệu.
- Thử nghiệm của người biên soạn bằng Python 3 và SQLite (ngày 2026-10-19): hai thứ tự ghi, quét dọn rác, ghi đè. Tài liệu chính thức của Amazon `S3` chưa được đối chiếu.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

# Quốc tế hóa một website bán hàng: năm mảng, và những chỗ máy làm giúp

**Quốc tế hóa không phải dịch giao diện: nó tách mọi thứ phụ thuộc vào nước và ngôn ngữ ra khỏi mã nguồn, ở năm mảng là ngôn ngữ, bố cục, múi giờ, tiền tệ, và pháp nhân cùng kế toán.**
Bài thử trên dữ liệu địa phương hóa có sẵn để thấy chỗ nào dễ sai: dấu phân cách số, thứ tự từ, dạng số nhiều và đồng hồ mùa hè.

![Hai khung. Khung một, ba mảng giao diện: ngôn ngữ (văn bản tách khỏi mã, không ghép chuỗi), bố cục (chừa chỗ cho chữ dài, định dạng số và ngày theo nơi), múi giờ (lưu giờ UTC, hiển thị giờ địa phương). Khung hai, hai mảng nghiệp vụ: tiền tệ (tiền hiển thị, tiền quyết toán, dịch vụ quy đổi) và pháp nhân cùng kế toán (mỗi nước một pháp nhân, chuẩn kế toán khác nhau).](../../diagrams/sd-12-008-main.svg)

## Từ viết tắt

- **UTC** (Coordinated Universal Time) — giờ phối hợp quốc tế: mốc giờ chung toàn cầu, không đổi theo mùa; dùng để lưu thời điểm.
- **CLDR** (Common Locale Data Repository) — kho dữ liệu địa phương chung: bộ quy tắc về cách mỗi vùng viết số, ngày, tiền và dạng số nhiều; thư viện Babel của Python lấy dữ liệu từ đó.

## Đọc hình

**Ngôn ngữ.** Giữ mọi chữ hiển thị trong một hệ thống riêng, không để trong mã, không ghép chuỗi từ nhiều mảnh, và không để chữ trong hình ảnh. Dùng câu đầy đủ có chỗ trống thay vì dán các từ rời, và hiển thị dữ liệu nghiệp vụ như tiền theo ngôn ngữ người xem.

**Bố cục.** Chừa chỗ cho chữ dài ngắn khác nhau, tính trước việc xuống dòng và cắt chữ, giữ nhãn nút ngắn, và đổi cách hiển thị số, ngày, giờ, địa chỉ theo từng nơi.

**Múi giờ.** Lưu thời điểm tách riêng khỏi cách hiển thị: lưu bằng giờ UTC ở cơ sở dữ liệu và dịch vụ phía sau, đổi sang giờ địa phương ở phía giao diện.

**Tiền tệ.** Quyết định tiền nào được hiển thị, tiền nào dùng để quyết toán, và cần một dịch vụ quy đổi ngoại tệ để báo giá.

**Pháp nhân và kế toán.** Mỗi nước thường có pháp nhân riêng theo quy định và chuẩn kế toán riêng, nên hệ thống phải hỗ trợ nhiều cách ghi sổ, và thường cần quản lý quỹ ở cấp công ty.

## Thử nghiệm với dữ liệu địa phương

Ngày 2026-10-19, người biên soạn dùng Python 3 với thư viện Babel 2.18.0 (dữ liệu CLDR) và `zoneinfo` để thử bốn điều.

**Số, tiền, ngày.** Cùng số 1234567,891 hiển thị là `1,234,567.891` (Anh-Mỹ), `1.234.567,891` (Việt Nam và Đức). Cùng ngày 8 tháng 3 năm 2026 ở dạng ngắn là `3/8/26` (Anh-Mỹ), `8/3/26` (Việt Nam), `2026/03/08` (Nhật), `08.03.26` (Đức): dạng `3/8` đọc thành tháng 3 hay tháng 8 tùy người. Số tiền 1234,5 đồng hiển thị là `1.234 ₫` ở Việt Nam: tiền đồng không có phần lẻ nên giá trị bị làm tròn.

**Dạng số nhiều.** Ngoài dạng chung "khác", tiếng Anh có thêm 1 dạng (một), tiếng Việt và tiếng Nhật không có dạng nào thêm, tiếng Nga có thêm 3 dạng (một, vài, nhiều), tiếng Ả Rập có thêm 5. Câu kiểu "3 mặt hàng" không thể ghép bằng cách gắn "s" vào cuối chữ.

**Thứ tự từ.** Mẫu "3 mặt hàng trong giỏ" ghép từ mảnh không dùng lại được khi thứ tự từ khác: tiếng Nhật đặt "giỏ" đầu câu, như "giỏに3個の商品". Vì vậy cả câu có chỗ trống phải là một mục dịch, không phải ba mảnh.

**Múi giờ.** Cùng một thời điểm 06:30 UTC ngày 2026-03-08 là 13:30 ở Hà Nội (+07:00), 15:30 ở Tokyo (+09:00) và 01:30 ở New York (-05:00). Ở New York, ngày đó đồng hồ nhảy từ 01:59 (-05:00) sang 03:01 (-04:00) trong khi chỉ hai phút trôi qua; còn Hà Nội luôn +07:00 vào tháng 1 lẫn tháng 7. Vì giờ địa phương có chỗ nhảy, lưu giờ địa phương thì tính khoảng cách thời gian sẽ sai.

## Giới hạn cần nhớ

Bài nguồn là một danh sách các việc cần chú ý, không nói cách làm cụ thể. Thử nghiệm trên chỉ chạm tới ngôn ngữ, bố cục, múi giờ và tiền ở mức định dạng; mảng pháp nhân và kế toán, dịch vụ quy đổi ngoại tệ và chuyện giá trị làm tròn của tiền thật không được thử. Dữ liệu CLDR thay đổi theo phiên bản nên kết quả của phiên bản khác có thể khác. Phần nói đúng-sai về cách mỗi nước làm kế toán là của người biên soạn không đối chiếu.

## Nhìn hình trả lời

Ứng dụng của bạn lưu thời điểm đặt hàng bằng giờ địa phương của máy chủ ở New York. Đơn đặt lúc 01:59 và đơn đặt hai phút sau, lúc 03:01, ngày chuyển giờ mùa hè. Cách lưu này gây ra lỗi gì khi tính "hai đơn cách nhau bao lâu"?

<details>
<summary>Xem đáp án</summary>

Hiệu hai giờ địa phương là 62 phút trong khi thực tế chỉ trôi qua 2 phút, vì đồng hồ nhảy tiến một giờ. Lưu UTC thì hiệu là 2 phút đúng, và mỗi nơi tự đổi sang giờ địa phương khi hiển thị.
Hai con số 62 và 2 là kết quả của thử nghiệm ở trên.

</details>

<details>
<summary>Xem sâu hơn: điều đã bổ sung so với bài nguồn</summary>

Bài nguồn có một hình và năm mảng, mỗi mảng vài dòng. Bài này giữ năm mảng và tên mảng, rồi thêm thử nghiệm để thấy các lỗi cụ thể: dấu phân cách số, ngày đọc nhầm, dạng số nhiều và đồng hồ mùa hè.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Chương trình Python 3 (cần thêm gói `Babel`, bản 2.18.0 khi viết bài) đã in mọi con số về định dạng, dạng số nhiều và múi giờ trong bài.

```python
from babel import Locale
from babel.numbers import format_decimal, format_currency
from babel.dates import format_datetime, format_date
from babel.plural import PluralRule
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
n=1234567.891
for loc in ("en_US","vi_VN","ja_JP","de_DE"):
    print(loc, "|", format_decimal(n,locale=loc), "|", format_currency(1234.5,"USD",locale=loc), "|", format_currency(1234.5,"VND",locale=loc), "|", format_currency(1234.5,"JPY",locale=loc))
d=datetime(2026,3,8,15,30,tzinfo=timezone.utc)
for loc in ("en_US","vi_VN","ja_JP","de_DE"):
    print(loc, "date|", format_date(d,format="short",locale=loc), "|", format_date(d,format="long",locale=loc))
# plural categories
for loc in ("en","vi","ja","ru","ar"):
    print(loc, Locale(loc).plural_form.tags)
# concatenation vs whole sentence: word order
# Same instant in 3 zones, around a DST change
inst=datetime(2026,3,8,6,30,tzinfo=timezone.utc)  # US DST starts 2026-03-08 07:00 UTC for New_York (2am local)
for z in ("UTC","Asia/Ho_Chi_Minh","America/New_York","Asia/Tokyo"):
    print(z, inst.astimezone(ZoneInfo(z)).isoformat())
a=datetime(2026,3,8,6,59,tzinfo=timezone.utc).astimezone(ZoneInfo("America/New_York"))
b=datetime(2026,3,8,7,1,tzinfo=timezone.utc).astimezone(ZoneInfo("America/New_York"))
print("NY before/after", a.isoformat(), b.isoformat(), "gap minutes UTC=2, local diff:", (b.replace(tzinfo=None)-a.replace(tzinfo=None)).total_seconds()/60)
# Hanoi has no DST
print([datetime(2026,m,1,12,tzinfo=timezone.utc).astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).utcoffset() for m in (1,7)])
print([datetime(2026,m,1,12,tzinfo=timezone.utc).astimezone(ZoneInfo("America/New_York")).utcoffset() for m in (1,7)])
# Naive concatenation example
for loc,tpl in (("en","{n} items in {c}"),("ja","{c}に{n}個の商品")):
    print(loc, tpl.format(n=3,c="giỏ"))
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-design-a-system-for-internationalization.md): năm mảng Language, Layout, Time zone, Currency, Company entity and accounting.
- Thử nghiệm của người biên soạn với Python 3, Babel 2.18.0 và `zoneinfo` (ngày 2026-10-19): số, ngày, tiền, dạng số nhiều, múi giờ.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

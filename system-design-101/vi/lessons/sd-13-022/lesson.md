# Sáu lệnh phân tích nhật ký trên dòng lệnh

grep, cut, sed, awk, sort và uniq làm việc tốt khi ghép bằng dấu `|`: mỗi lệnh làm một việc nhỏ và chuyển kết quả cho lệnh sau.

![Sáu lệnh nối bằng đường ống: grep lọc dòng, cut hoặc awk lấy cột, sed sửa chuỗi, sort sắp xếp, uniq -c đếm các dòng liền kề giống nhau.](../../diagrams/sd-13-022-main.svg)

## Nhìn hình thử trả lời

Vì sao phải `sort` trước `uniq -c` khi đếm?

<details>
<summary>Xem đáp án</summary>

`uniq` chỉ gộp các dòng giống nhau nằm liền kề. Không sắp xếp trước thì cùng một giá trị xuất hiện rải rác sẽ bị đếm thành nhiều nhóm.

</details>

## Giới hạn cần nhớ

Các lệnh này đọc văn bản theo dòng và cột. Nhật ký dạng JSON hoặc dòng nhiều tầng nên dùng công cụ hiểu cấu trúc (ví dụ `jq`). Cũng nên thử trước trên một tệp nhỏ.

<details>
<summary>Xem sâu hơn</summary>

Giả sử mỗi dòng nhật ký có dạng `ngày giờ MỨC dịch_vụ nội_dung`, ví dụ `2026-10-13 10:15:02 ERROR PaymentService Exception timeout`. Đếm số ngoại lệ theo dịch vụ:

```bash
grep Exception app.log | awk '{print $4}' | sort | uniq -c | sort -rn
```

- `grep Exception` giữ các dòng chứa chữ đó.
- `awk '{print $4}'` lấy cột thứ tư (dịch vụ).
- `sort | uniq -c` đếm số dòng của từng dịch vụ; `sort -rn` xếp giảm dần theo số đếm.

`cut -d' ' -f2` cũng lấy cột nhưng coi mỗi dấu cách là một ngăn cách, nên khi có nhiều dấu cách liên tiếp thì `awk` ổn định hơn.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/log-parsing-cheat-sheet.md).
- GNU: [grep](https://www.gnu.org/software/grep/manual/grep.html), [uniq](https://www.gnu.org/software/coreutils/manual/html_node/uniq-invocation.html), [sort](https://www.gnu.org/software/coreutils/manual/html_node/sort-invocation.html), [gawk](https://www.gnu.org/software/gawk/manual/gawk.html).

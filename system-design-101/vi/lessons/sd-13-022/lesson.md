# Phân tích nhật ký trên dòng lệnh theo từng việc

Nhớ tên lệnh ít có ích bằng nhớ việc cần làm: lọc, lấy trường, đếm, xếp hạng, che dữ liệu. Mỗi việc ứng với một cụm lệnh.

![Năm việc và lệnh tương ứng: giữ dòng lỗi bằng grep, lấy tên dịch vụ bằng awk, đếm mỗi dịch vụ bằng sort và uniq -c, xếp hạng bằng sort -rn, che dữ liệu nhạy cảm bằng sed.](../../diagrams/sd-13-022-main.svg)

**Đọc hình:** ghép các thẻ đầu bằng dấu `|` theo thứ tự lọc, lấy trường, đếm, xếp hạng là ra bảng thống kê lỗi.

## Nhìn hình thử trả lời

Vì sao phải `sort` trước `uniq -c` khi đếm?

<details>
<summary>Xem đáp án</summary>

`uniq` chỉ gộp các dòng giống nhau nằm liền kề. Không sắp xếp trước thì cùng một giá trị xuất hiện rải rác sẽ bị đếm thành nhiều nhóm.

</details>

## Giới hạn cần nhớ

Các lệnh này đọc văn bản theo dòng và cột. Nhật ký dạng JSON hoặc nhiều dòng nên dùng công cụ hiểu cấu trúc (ví dụ `jq`). Thử trước trên tệp nhỏ, nhất là với `sed`, vì mẫu sai có thể che hoặc sửa nhầm.

<details>
<summary>Xem sâu hơn</summary>

```bash
grep ERROR app.log | awk '{print $4}' | sort | uniq -c | sort -rn
```

Với dòng `2026-10-13 10:15:02 ERROR PaymentService timeout`, lệnh trên cho số dòng lỗi của mỗi dịch vụ, nhiều nhất trước.

- `cut -d' ' -f4` cũng lấy cột nhưng coi mỗi dấu cách là một ngăn, nên khi có nhiều dấu cách liên tiếp thì `awk` ổn định hơn.
- `sed` sửa từng dòng theo mẫu; dùng khi cần chuẩn hóa hoặc che dữ liệu trước khi chia sẻ nhật ký.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/log-parsing-cheat-sheet.md).
- GNU: [grep](https://www.gnu.org/software/grep/manual/grep.html), [uniq](https://www.gnu.org/software/coreutils/manual/html_node/uniq-invocation.html), [sort](https://www.gnu.org/software/coreutils/manual/html_node/sort-invocation.html), [gawk](https://www.gnu.org/software/gawk/manual/gawk.html), [sed](https://www.gnu.org/software/sed/manual/sed.html).

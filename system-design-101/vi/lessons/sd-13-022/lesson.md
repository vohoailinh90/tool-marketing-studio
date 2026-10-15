# Tìm nguyên nhân từ nhật ký bằng dòng lệnh

Khi tìm nguyên nhân sự cố trong nhật ký, đặc điểm của tệp quyết định công cụ: có cần ngữ cảnh quanh dòng lỗi không, nhật ký đã nén hay đang ghi, dạng văn bản hay JSON (JavaScript Object Notation — định dạng dữ liệu văn bản dạng khóa và giá trị), hay cần một con số.

![Năm tình huống và lệnh: xem ngữ cảnh quanh dòng lỗi bằng grep -C, tìm trong nhật ký đã nén bằng zgrep, theo dõi nhật ký đang ghi bằng tail -f nối grep, thêm --line-buffered khi đầu ra của grep còn chuyển tiếp sang lệnh khác, lọc nhật ký JSON (JavaScript Object Notation — định dạng dữ liệu văn bản dạng khóa và giá trị) bằng jq, và tính trung bình một cột số bằng awk.](../../diagrams/sd-13-022-main.svg)

**Đọc hình:** mỗi thẻ là một tình huống riêng và lệnh gợi ý; các lệnh có thể ghép bằng dấu `|` khi cần.

## Từ viết tắt

- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản biểu diễn dữ liệu bằng các cặp tên và giá trị, dễ đọc với cả người và máy.

## Nhìn hình thử trả lời

Khi nào cần thêm `--line-buffered` cho `grep` trong một đường ống với `tail -f`?

<details>
<summary>Xem đáp án</summary>

Khi đầu ra của grep không đi thẳng ra terminal, ví dụ còn nối tiếp sang lệnh khác như `tee` hoặc ghi ra tệp. Lúc đó grep đệm theo khối nên dòng khớp tới chậm, và `--line-buffered` ép nó xả từng dòng. Nếu grep in thẳng ra terminal thì nó đã xả từng dòng, và cờ này không cần.

</details>

## Giới hạn cần nhớ

Các lệnh này đọc văn bản theo dòng. Với nhật ký dạng JSON hãy dùng công cụ hiểu cấu trúc như `jq` thay vì cắt chuỗi. Nhật ký nhiều dòng (stack trace) cần `-A` hoặc `-C` để lấy đủ ngữ cảnh. Thử trước trên tệp nhỏ rồi mới chạy trên tệp lớn.

<details>
<summary>Xem sâu hơn</summary>

```bash
# ngữ cảnh: 3 dòng trước và sau mỗi dòng khớp, kèm số dòng
grep -n -C 3 "timeout" app.log

# nhật ký đã nén
zgrep "ERROR" app.log.*.gz

# theo dõi trực tiếp; --line-buffered cần vì đầu ra của grep còn đi tiếp qua ống
tail -f app.log | grep --line-buffered "ERROR" | tee errors.log

# JSON, mỗi dòng một đối tượng: {"level":"error","message":"..."}
jq -r 'select(.level=="error") | .message' app.json

# trung bình cột thứ năm (ví dụ độ trễ)
awk '{s += $5; n++} END {if (n) print s/n}' latency.log
```

- **grep -C:** in thêm dòng ngữ cảnh quanh dòng khớp; `-A` chỉ dòng sau, `-B` chỉ dòng trước.
- **zgrep:** tìm trong tệp nén gzip mà không giải nén ra đĩa.
- **jq:** đọc từng đối tượng JSON, lọc và chọn trường.
- **awk:** xử lý theo cột; `END` chạy sau khi đọc hết tệp. Điều kiện `if (n)` chặn phép chia cho 0 khi tệp rỗng, vì gawk dừng với lỗi nghiêm trọng khi chia cho 0.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/log-parsing-cheat-sheet.md).
- GNU (GNU is Not Unix — viết tắt đệ quy, tên một dự án phần mềm tự do): [grep](https://www.gnu.org/software/grep/manual/grep.html), [gzip và zgrep](https://www.gnu.org/software/gzip/manual/gzip.html), [gawk](https://www.gnu.org/software/gawk/manual/gawk.html). [jq manual](https://jqlang.github.io/jq/manual/).

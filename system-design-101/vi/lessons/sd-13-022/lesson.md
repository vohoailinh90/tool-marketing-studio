# Tìm nguyên nhân từ nhật ký bằng dòng lệnh

Khi tìm nguyên nhân sự cố trong nhật ký, đặc điểm của tệp quyết định công cụ: có cần ngữ cảnh quanh dòng lỗi không, nhật ký đã nén hay đang ghi, dạng văn bản hay JSON, hay cần một con số.

![Năm tình huống và lệnh: xem ngữ cảnh quanh dòng lỗi bằng grep -C, tìm trong nhật ký đã nén bằng zgrep, theo dõi nhật ký đang ghi bằng tail -f nối grep --line-buffered, lọc nhật ký JSON bằng jq, và tính trung bình một cột số bằng awk.](../../diagrams/sd-13-022-main.svg)

**Đọc hình:** mỗi thẻ là một tình huống riêng và lệnh gợi ý; các lệnh có thể ghép bằng dấu `|` khi cần.

## Nhìn hình thử trả lời

Vì sao khi nối `tail -f` với `grep` lại nên thêm `--line-buffered`?

<details>
<summary>Xem đáp án</summary>

Khi đầu ra của grep không phải terminal (ví dụ đang chuyển tiếp qua ống), grep đệm theo khối nên dòng khớp có thể hiện rất chậm. `--line-buffered` ép nó xả từng dòng.

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

# theo dõi trực tiếp
tail -f app.log | grep --line-buffered "ERROR"

# JSON, mỗi dòng một đối tượng: {"level":"error","message":"..."}
jq -r 'select(.level=="error") | .message' app.json

# trung bình cột thứ năm (ví dụ độ trễ)
awk '{s += $5; n++} END {if (n) print s/n}' latency.log
```

- **grep -C:** in thêm dòng ngữ cảnh quanh dòng khớp; `-A` chỉ dòng sau, `-B` chỉ dòng trước.
- **zgrep:** tìm trong tệp nén gzip mà không giải nén ra đĩa.
- **jq:** đọc từng đối tượng JSON, lọc và chọn trường.
- **awk:** xử lý theo cột; `END` chạy sau khi đọc hết tệp.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/log-parsing-cheat-sheet.md).
- GNU: [grep](https://www.gnu.org/software/grep/manual/grep.html), [gzip và zgrep](https://www.gnu.org/software/gzip/manual/gzip.html), [gawk](https://www.gnu.org/software/gawk/manual/gawk.html). [jq manual](https://jqlang.github.io/jq/manual/).

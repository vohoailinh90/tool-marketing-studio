# Thiết kế bộ sinh ID kiểu Snowflake

Một hệ thống tin nhắn cần tạo ID ở nhiều node mà không gọi DB cho từng tin. Có thể ghép ba trường: thời gian từ một mốc, mã node và số thứ tự trong cùng đơn vị thời gian.

![64 bit minh họa: 0 | thời gian 41 bit: node 10 bit | sequence 12 bit; Mỗi node: Node ID riêng, sequence riêng: Xử lý hết sequence; Tình huống lỗi: Đồng hồ quay lùi • restart: Giữ điều kiện không lặp.](../../diagrams/sd-11-022-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

Trong một bố cục minh họa 64 bit, giữ bit cao bằng 0 rồi dành 41 bit cho thời gian, 10 bit cho node và 12 bit cho sequence. Khi các node có mã khác nhau và mỗi node không lặp sequence trong cùng timestamp, ID được tách theo những trường này. Nếu hết sequence, phải chờ hoặc có cách xử lý được thiết kế trước.

ID gần theo thời gian hữu ích cho index và phân trang, nhưng không chứng minh thứ tự nhân quả giữa các máy. Cần quản lý cấp node ID và tình huống đồng hồ quay lùi. Bố cục bit là một lựa chọn triển khai, không là tiêu chuẩn duy nhất.

## Từ viết tắt

- **DB** (DataBase) — cơ sở dữ liệu: nơi lưu dữ liệu có tổ chức để ghi và tìm lại; một hệ thống tin nhắn cần tạo ID ở nhiều node mà không gọi DB cho từng tin.
- **ID** (IDentifier) — mã định danh: chuỗi hoặc số dùng để phân biệt một đối tượng với các đối tượng khác; bài thiết kế bộ sinh ID ghép thời gian từ một mốc, mã node và số thứ tự.

## Nhìn hình thử trả lời

Hai node có cùng timestamp và sequence nhưng node ID khác nhau có trùng ID không?

<details>
<summary>Xem đáp án</summary>

Không trong bố cục ghép trường đúng. Nếu node ID bị trùng, bảo đảm này mất.

</details>

## Giới hạn cần nhớ

Không gán cùng node ID cho hai tiến trình đang hoạt động. Đồng hồ quay lùi hoặc tái dùng state sai sau restart có thể gây trùng ID.

<details>
<summary>Xem sâu hơn</summary>

Kiểm tra thời hạn của trường thời gian, tốc độ tối đa mỗi node và khả năng biểu diễn số ở client. JavaScript Number không biểu diễn chính xác mọi số nguyên 64 bit; có thể truyền chuỗi.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/unique-id-generator.md).
- [github.com — snowflake](https://github.com/twitter-archive/snowflake).
- [Number.MAX_SAFE_INTEGER - JavaScript | MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.

# Đọc JSON lồng nhau bằng sơ đồ

Một phản hồi API có nhiều cấp khiến bạn khó biết giá trị nằm ở đâu. JSON Crack là một lựa chọn để xem cấu trúc bằng đồ thị. Trước hết cần hiểu quan hệ giữa object, array và giá trị; hình đẹp không thay thế kiểm tra dữ liệu.

![Object: đơn hàng: order; Thuộc tính là array: items; Phần tử đầu tiên: items[0]; Giá trị số: qty = 2.](../../diagrams/sd-09-003-main.svg)

**Đọc hình:** Các thẻ là các bước hoặc góc nhìn của ví dụ; đọc từ trên xuống. Mũi tên chỉ thứ tự đọc, không biểu diễn luồng mạng hoặc sự phụ thuộc bắt buộc.

Với dữ liệu `{"order":{"items":[{"qty":2}]}}`, đường tới số lượng là `order.items[0].qty`. Object dùng tên khóa; array dùng vị trí, bắt đầu từ 0. Một nhánh mở rộng trên đồ thị giúp lần theo đúng cấp khi dữ liệu dài.

Bạn có thể thử công cụ bằng dữ liệu giả, tìm một trường rồi đối chiếu đường dẫn với JSON gốc. Khi thiếu trường, cần phân biệt khóa không tồn tại, giá trị `null` và array rỗng. Ba trường hợp này thường dẫn đến cách xử lý khác nhau trong chương trình.

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách để một chương trình yêu cầu dữ liệu hoặc chức năng của chương trình khác; bài lấy phản hồi của một API làm dữ liệu cần đọc.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản biểu diễn dữ liệu bằng object, array và giá trị; bài đọc dữ liệu lồng nhau theo dạng này.

## Nhìn hình thử trả lời

Trong ví dụ, items là object hay array? qty nằm ở cấp nào?

<details>
<summary>Xem đáp án</summary>

items là array. qty nằm trong object ở phần tử số 0 của array này.

</details>

## Giới hạn cần nhớ

Sơ đồ cấu trúc không chứng minh dữ liệu đáp ứng schema hoặc quy tắc nghiệp vụ. Chưa kiểm chứng chế độ lưu trữ/xử lý dữ liệu của dịch vụ hiện hành; chỉ dùng dữ liệu giả khi thực hành.

<details>
<summary>Xem sâu hơn</summary>

JSON không có comment theo chuẩn và tên khóa object phải là chuỗi. Cú pháp hợp lệ vẫn có thể chứa kiểu không mong đợi, chẳng hạn qty là chuỗi "2" thay vì số 2.

</details>

## Nguồn đối chiếu

- [Chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/json-files.md). Bài viết và hình này được thiết kế độc lập; không dịch thân bài hoặc sử dụng ảnh nguồn.
- [Chuẩn JSON, RFC 8259](https://www.rfc-editor.org/rfc/rfc8259).
- [JSON Crack: mã nguồn](https://github.com/AykutSarac/jsoncrack.com).

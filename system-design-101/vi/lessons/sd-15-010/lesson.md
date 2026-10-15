# Hình dung một câu lệnh SQL

**Bạn viết `SELECT` đầu tiên, nhưng cơ sở dữ liệu không đọc theo thứ tự đó.** Hiểu thứ tự *logic* giải thích vì sao một số câu lệnh báo lỗi và cách đọc kết quả.

![Ba khung dọc: thứ tự viết SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT; hệ thống chạy câu lệnh qua ba bước phân tích, tối ưu, chạy, và bộ tối ưu có thể chọn cách chạy khác miễn kết quả không đổi; ý nghĩa của câu lệnh được mô tả bằng thứ tự logic FROM và JOIN, WHERE, GROUP BY, HAVING, SELECT cùng alias, DISTINCT, ORDER BY, LIMIT, là một mô hình chứ không phải giai đoạn chạy thêm. Alias ở SELECT chưa có khi WHERE chạy.](../../diagrams/sd-15-010-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ.

## Đọc hình

```sql
SELECT customer, SUM(amount) AS total
FROM orders
WHERE amount > 0
GROUP BY customer
HAVING SUM(amount) > 100
ORDER BY total DESC
LIMIT 3;
```

Khi chạy, hệ thống *phân tích* câu lệnh (cú pháp, tên bảng và cột), *tối ưu* để chọn kế hoạch (dùng chỉ mục nào, nối bảng ra sao), rồi *chạy* kế hoạch và trả kết quả.

**Thứ tự logic** dưới đây không phải một giai đoạn chạy thêm: nó là mô hình ý nghĩa của câu lệnh, kết quả phải giống như thể các mệnh đề được tính theo thứ tự này. Lấy bảng `orders` (FROM) → giữ các dòng có `amount > 0` (WHERE) → gom theo `customer` (GROUP BY) → giữ nhóm có tổng trên 100 (HAVING) → tính cột kết quả và đặt tên `total` (SELECT) → loại dòng trùng nếu có DISTINCT → sắp xếp (ORDER BY) → lấy 3 dòng đầu (LIMIT).

## Giới hạn cần nhớ

Thứ tự logic chỉ bảo đảm *ý nghĩa*, không phải cách chạy thật. Bộ tối ưu có thể đẩy điều kiện xuống trước hoặc đổi thứ tự nối bảng miễn kết quả không đổi. Chi tiết như alias có dùng được ở GROUP BY hay HAVING hay không khác nhau giữa các hệ quản trị.

## Nhìn hình thử trả lời

`SELECT customer, SUM(amount) AS total FROM orders WHERE total > 100 GROUP BY customer;` báo lỗi. Vì sao, và nên sửa thế nào?

<details>
<summary>Xem đáp án</summary>

WHERE chạy trước SELECT nên alias `total` chưa tồn tại, và WHERE cũng không dùng được hàm gộp. Điều kiện trên tổng của từng khách phải đặt ở HAVING (sau GROUP BY): `SELECT customer, SUM(amount) AS total FROM orders GROUP BY customer HAVING SUM(amount) > 100;`.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Hàm cửa sổ:** được tính sau HAVING, cùng giai đoạn với danh sách SELECT, nên không dùng trực tiếp trong WHERE.
- **ORDER BY** được dùng alias của SELECT vì chạy sau đó.
- **Xem kế hoạch thật:** các hệ quản trị có lệnh như `EXPLAIN` để xem cách chạy thực tế.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/visualizing-a-sql-query.md).
- [PostgreSQL — SELECT](https://www.postgresql.org/docs/current/sql-select.html): thứ tự xử lý các mệnh đề và alias trong WHERE, ORDER BY.
- [PostgreSQL — Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html) và [EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html).

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

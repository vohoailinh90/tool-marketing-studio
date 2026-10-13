# Hình dung một câu lệnh SQL

**Bạn viết `SELECT` đầu tiên, nhưng cơ sở dữ liệu không đọc theo thứ tự đó.** Hiểu thứ tự *logic* giải thích vì sao một số câu lệnh báo lỗi và cách đọc kết quả.

![Ba khung dọc: thứ tự viết SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT; thứ tự logic là FROM và JOIN, WHERE, GROUP BY, HAVING, SELECT cùng alias, DISTINCT, ORDER BY, LIMIT; sau đó hệ thống phân tích, tối ưu và chạy, và có thể chọn cách chạy khác miễn kết quả không đổi.](../../diagrams/sd-15-010-main.svg)

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

Về mặt logic: lấy bảng `orders` (FROM) → giữ các dòng có `amount > 0` (WHERE) → gom theo `customer` (GROUP BY) → giữ nhóm có tổng trên 100 (HAVING) → tính cột kết quả và đặt tên `total` (SELECT) → loại dòng trùng nếu có DISTINCT → sắp xếp (ORDER BY) → lấy 3 dòng đầu (LIMIT).

Sau đó mới tới các bước kỹ thuật: *phân tích* câu lệnh, *tối ưu* để chọn kế hoạch (dùng chỉ mục nào, nối bảng ra sao), rồi *chạy*.

## Giới hạn cần nhớ

Thứ tự logic chỉ bảo đảm *ý nghĩa*, không phải cách chạy thật. Bộ tối ưu có thể đẩy điều kiện xuống trước hoặc đổi thứ tự nối bảng miễn kết quả không đổi. Chi tiết như alias có dùng được ở GROUP BY hay HAVING hay không khác nhau giữa các hệ quản trị.

## Nhìn hình thử trả lời

`SELECT SUM(amount) AS total FROM orders WHERE total > 100;` báo lỗi. Vì sao, và nên sửa thế nào?

<details>
<summary>Xem đáp án</summary>

WHERE chạy trước SELECT nên alias `total` chưa tồn tại, và WHERE cũng không dùng được hàm gộp. Điều kiện trên tổng phải đặt ở HAVING (sau GROUP BY), ví dụ: `SELECT customer, SUM(amount) AS total FROM orders GROUP BY customer HAVING SUM(amount) > 100;`.

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

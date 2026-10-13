# Các kiểu SQL JOIN hoạt động thế nào?

**JOIN ghép các dòng của hai bảng theo một điều kiện.** Bốn kiểu thường gặp khác nhau ở chỗ:
dòng nào không có cặp thì vẫn được giữ lại, dòng nào bị bỏ.

![Hình dọc dùng hai bảng ví dụ: khach gồm An, Binh, Chi; don gồm đơn 10 (100) và đơn 11 (50) của An và đơn 12 (70) không có khách. INNER JOIN chỉ giữ cặp khớp: An–10, An–11. LEFT JOIN giữ mọi khách, thêm Binh và Chi với phần đơn trống. RIGHT JOIN giữ mọi đơn, thêm đơn 12 với phần khách trống. FULL OUTER JOIN giữ cả hai phía, tổng cộng năm dòng. Thẻ cuối cảnh báo: LEFT JOIN rồi lọc bằng điều kiện WHERE loại NULL trên cột bảng phải, như tien > 60, làm mất dòng không khớp, hãy đưa điều kiện vào ON.](../../diagrams/sd-05-001-main.svg)

## Đọc hình

Điều kiện ghép ở đây là `don.ma_khach = khach.ma`. Số tiền của các đơn: đơn 10 là 100, đơn 11 là 50, đơn 12 là 70.

**INNER JOIN.** Chỉ giữ các cặp khớp: An–10 và An–11. Binh, Chi và đơn 12 đều biến mất.

**LEFT JOIN.** Giữ mọi dòng bảng bên trái (khách). Khách chưa có đơn vẫn xuất hiện, với phần đơn là trống (`NULL`).

**RIGHT JOIN.** Giống LEFT JOIN nhưng giữ mọi dòng bảng bên phải: đơn 12 xuất hiện với phần khách trống.

**FULL OUTER JOIN.** Giữ cả hai phía: hai cặp khớp, cộng Binh, Chi và đơn 12, tổng cộng năm dòng.

## Giới hạn cần nhớ

Cạm bẫy hay gặp: viết `LEFT JOIN`, rồi lọc bằng một điều kiện `WHERE` loại `NULL` trên cột của bảng bên phải, như `don.tien > 60`.
Dòng không khớp có cột đó là `NULL`, nên bị loại ngay, và kết quả giống `INNER JOIN`. Nếu điều kiện thuộc về việc ghép, hãy đặt nó trong `ON`.
Ngược lại, `WHERE don.id IS NULL` là cách cố ý để chỉ giữ các dòng không khớp.

## Nhìn hình trả lời

Bạn muốn liệt kê mọi khách, kể cả khách chưa có đơn, nhưng chỉ ghép những đơn trên 60 (trong ví dụ: đơn 10 và đơn 12, còn đơn 11 thì không). Điều kiện `don.tien > 60` đặt ở đâu?

<details>
<summary>Xem đáp án</summary>

Trong `ON`: `... LEFT JOIN don ON don.ma_khach = khach.ma AND don.tien > 60`. Kết quả: An–10, Binh–trống, Chi–trống.
Đặt cùng điều kiện trong `WHERE` thì Binh và Chi bị loại, chỉ còn An–10.

</details>

<details>
<summary>Xem sâu hơn: số dòng có thể tăng</summary>

Nếu một khóa ở bảng này khớp nhiều dòng ở bảng kia, kết quả có nhiều dòng cho khóa đó. Ví dụ An có hai đơn nên xuất hiện hai lần.
Vì vậy sau khi JOIN, hãy so số dòng với điều bạn mong đợi.

`LEFT JOIN ... WHERE don.id IS NULL` cho Binh và Chi, khác với INNER JOIN.

Các kết quả trên được chạy lại trên SQLite 3.45.1, bản hỗ trợ cả RIGHT JOIN và FULL OUTER JOIN.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-sql-joins-work.md): bốn kiểu JOIN.
- [SQLite — SELECT và JOIN](https://www.sqlite.org/lang_select.html): kiểu JOIN và điều kiện ON. Trang này không mở được trong môi trường biên soạn; hành vi được kiểm bằng cách chạy SQLite 3.45.1.

Đã đọc nguồn ngày 2026-10-13. Mọi kết quả trong bài được chạy lại bằng câu lệnh SQL thật trên SQLite 3.45.1. Bài viết và hình được thiết kế độc lập.
Bài nguồn mô tả FULL OUTER JOIN là “các dòng có khớp ở một trong hai bảng”; bài này nói rõ các dòng không khớp được giữ với phần trống.

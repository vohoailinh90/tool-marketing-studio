# Deadlock là gì?

**Deadlock là khi hai bên giữ thứ của nhau và cùng chờ.** Không bên nào chịu nhả, không bên nào tiến lên. Nó xảy ra với tiến trình lẫn giao dịch cơ sở dữ liệu.

![Ba khung dọc: giao dịch T1 giữ khóa A và xin B, T2 giữ khóa B và xin A nên chờ vòng tròn; bốn điều kiện cần cùng lúc là loại trừ lẫn nhau, giữ và chờ, không bị cưỡng đoạt, chờ vòng tròn; cách xử lý là khóa theo thứ tự cố định, hoặc phát hiện và hủy một giao dịch rồi thử lại.](../../diagrams/sd-15-007-main.svg)

## Đọc hình

Hai giao dịch chuyển tiền giữa tài khoản A và B, mỗi giao dịch cần khóa cả hai dòng. T1 khóa A rồi xin B; cùng lúc T2 khóa B rồi xin A. T1 chờ T2, T2 chờ T1: một vòng chờ.

Deadlock chỉ xảy ra khi *cả bốn* điều kiện cùng đúng (Coffman, 1971): tài nguyên dùng độc quyền; giữ cái đang có trong lúc chờ cái khác; không thể cưỡng đoạt tài nguyên; và tồn tại vòng chờ. Phá một điều kiện là hết deadlock.

**Phòng ngừa phổ biến:** mọi nơi khóa theo cùng thứ tự (ví dụ luôn khóa tài khoản có id nhỏ trước). Khi đó không tạo được vòng chờ.

**Phát hiện và phục hồi:** cơ sở dữ liệu thường phát hiện vòng chờ, chọn một giao dịch làm "nạn nhân", hủy nó và nhả khóa; ứng dụng nhận lỗi và thử lại.

## Giới hạn cần nhớ

Khóa theo thứ tự cố định chỉ có tác dụng khi *mọi* đường code tuân theo. Đặt timeout cho việc chờ khóa giúp không treo mãi nhưng cũng làm hủy cả giao dịch không deadlock thật. Giao dịch bị chọn hủy cần được thử lại an toàn, tức thao tác phải có thể chạy lại mà không gây tác dụng phụ trùng.

## Nhìn hình thử trả lời

T1 khóa A rồi B; T2 cũng khóa A rồi B. Có deadlock giữa hai giao dịch này không?

<details>
<summary>Xem đáp án</summary>

Không. Cả hai xin theo cùng thứ tự, nên một bên chờ bên kia xong rồi mới đi tiếp; không có vòng chờ.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Đồ thị chờ:** mỗi giao dịch là một nút, mỗi lần chờ khóa là một cạnh; có chu trình là có deadlock.
- **Tránh (avoidance) khác phòng ngừa (prevention):** phòng ngừa phá một điều kiện từ đầu, như khóa theo thứ tự; thuật toán nhà băng (banker's) chỉ cấp tài nguyên khi trạng thái còn "an toàn", nhưng cần biết trước nhu cầu tối đa nên ít dùng trong hệ thống thông thường.
- **Cơ sở dữ liệu:** PostgreSQL và MySQL InnoDB tự phát hiện deadlock và hủy một giao dịch; cấu hình và thông báo lỗi khác nhau theo sản phẩm.
- **Khác với livelock và starvation:** ở đó các bên vẫn chạy nhưng không tiến, hoặc một bên bị bỏ đói.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-a-deadlock.md).
- [Coffman và cộng sự (1971) — System Deadlocks](https://doi.org/10.1145/356586.356588): bốn điều kiện.
- [OSTEP — Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf): deadlock, thứ tự khóa.
- [PostgreSQL — Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html) và [MySQL — InnoDB Deadlocks](https://dev.mysql.com/doc/refman/8.0/en/innodb-deadlocks.html).

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

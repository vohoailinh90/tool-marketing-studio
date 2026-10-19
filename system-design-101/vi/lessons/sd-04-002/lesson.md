# Khóa bi quan và khóa lạc quan: hai người cùng mua vé cuối

**Hai người cùng đọc "còn 1 vé" rồi cùng ghi "còn 0": cơ sở dữ liệu nhận cả hai lệnh ghi, và một vé được bán hai lần.**
Khóa bi quan chặn người thứ hai ngay từ lúc đọc; khóa lạc quan để cả hai đọc tự do rồi bắt xung đột lúc ghi.

![Bốn khung. Khung một, không khóa: A và B cùng đọc thấy còn 1 vé, cùng ghi còn 0, nên một vé bán cho hai người. Khung hai, khóa bi quan: A khóa hàng khi đọc và giữ khóa tới lúc commit; lệnh khóa của B phải chờ 1 giây; sau đó B đọc thấy còn 0 và từ chối bán. Khung ba, khóa lạc quan: cả hai đọc được còn 1 vé, phiên bản 1; mỗi người ghi kèm điều kiện phiên bản vẫn là 1; người ghi trước sửa được 1 dòng, người ghi sau sửa 0 dòng nên biết có xung đột, đọc lại rồi thử lại. Khung bốn: khi nào chọn cách nào.](../../diagrams/sd-04-002-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để đọc và ghi dữ liệu trong cơ sở dữ liệu quan hệ; các câu lệnh trong bài viết bằng SQL, và nó nằm trong tên PostgreSQL.

## Đọc hình

**Khung 1 · Không khóa.** Cả hai đọc số vé, tự trừ đi một trong ứng dụng, rồi ghi con số mới. Lệnh ghi thứ hai đè lên lệnh ghi thứ nhất mà không biết nó tồn tại; kiểu lỗi này thường gọi là mất cập nhật (lost update).

**Khung 2 · Khóa bi quan.** "Bi quan" vì giả định xung đột sẽ xảy ra, nên khóa trước khi quyết định. Trong PostgreSQL, `SELECT ... FOR UPDATE` khóa các hàng đọc được; giao dịch khác muốn sửa, xóa hay khóa chính hàng đó phải chờ tới khi giao dịch giữ khóa kết thúc.

**Khung 3 · Khóa lạc quan.** "Lạc quan" vì giả định xung đột hiếm, nên không khóa lúc đọc. Bảng có thêm cột `version`; lệnh ghi chỉ có hiệu lực nếu phiên bản chưa đổi:

```sql
UPDATE tickets SET left_count = 0, version = version + 1
WHERE id = 1 AND version = 1;
```

Cơ sở dữ liệu báo số dòng đã sửa. Ra 0 dòng nghĩa là ai đó đã ghi trước: ứng dụng đọc lại và quyết định lại, không được coi là thành công.

## Thử nghiệm: ba cách, cùng một vé

Một bảng `tickets` có một hàng: còn 1 vé, phiên bản 1. Hai luồng A và B chạy song song trên PostgreSQL 16.15, mỗi cách chạy lại từ đầu.

| Cách | Điều đo được | Kho còn |
|---|---|---|
| Không khóa | A bán, B cũng bán (cả hai đã đọc thấy 1) | 0 vé, nhưng hai vé đã bán |
| `SELECT ... FOR UPDATE` | người khóa trước bán; người kia chờ 1,0 giây, đọc thấy 0 và từ chối | 0 vé, một vé đã bán |
| Cột `version` | một lệnh `UPDATE` sửa 1 dòng, lệnh kia sửa 0 dòng | 0 vé, phiên bản 2 |

Thêm hai phép thử: với `FOR UPDATE NOWAIT`, người đến sau không chờ mà nhận lỗi ngay "could not obtain lock on row in relation"; ở mức cô lập `REPEATABLE READ`, chính PostgreSQL từ chối người ghi sau với lỗi "could not serialize access due to concurrent update".

## Giới hạn cần nhớ

- Khóa bi quan làm người khác **chờ**: giữ khóa càng lâu (gọi dịch vụ ngoài, chờ người dùng bấm nút trong lúc giữ khóa) thì hàng đợi càng dài. Khóa nhiều hàng theo thứ tự khác nhau còn có thể gây deadlock; PostgreSQL tự phát hiện và hủy một giao dịch, nên cách phòng tốt nhất là mọi nơi khóa theo cùng một thứ tự.
- Khóa lạc quan làm người thua **làm lại**: nếu xung đột xảy ra liên tục, vòng thử lại tốn hơn cả việc chờ. Quên kiểm số dòng đã sửa thì cột `version` không bảo vệ được gì.

## Nhìn hình trả lời

Một trang wiki cho nhiều người sửa cùng một bài; mỗi lần sửa mất vài phút gõ phím. Nên chọn cách nào, và người bấm lưu sau sẽ thấy gì?

<details>
<summary>Xem đáp án</summary>

Khóa lạc quan. Khóa bi quan sẽ giữ khóa suốt mấy phút gõ phím, ai mở bài cũng phải chờ.
Với cột phiên bản, người lưu sau nhận "0 dòng được sửa": ứng dụng báo bài đã đổi trong lúc họ gõ, cho họ xem bản mới rồi gộp lại, thay vì âm thầm đè lên bản của người kia.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn nói khóa lạc quan "rollback" thao tác khi thấy xung đột. Trong thử nghiệm ở đây, lệnh ghi theo phiên bản không báo lỗi gì cả, nó chỉ sửa 0 dòng; chính ứng dụng phải nhìn con số đó để biết mình thua.
Bài nguồn cũng xếp khóa bi quan là "tốt hơn cho toàn vẹn dữ liệu". Thử nghiệm cho thấy cả hai cách làm đúng đều chỉ bán một vé; khác nhau ở chỗ người thua phải chờ hay phải làm lại.

Mức cô lập giao dịch cũng là một cách chặn mất cập nhật, như dòng cuối của thử nghiệm.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/pessimistic-vs-optimistic-locking.md): định nghĩa hai kiểu khóa và năm lời khuyên.
- [PostgreSQL 16 — lệnh SELECT, mục The Locking Clause, tại commit cố định](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/ref/select.sgml): `FOR UPDATE`, `NOWAIT`, `SKIP LOCKED`. Đọc từ bản clone của kho, nhánh `REL_16_STABLE`.
- [PostgreSQL 16 — chương Concurrency Control, tại commit cố định](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/mvcc.sgml): khóa hàng của `FOR UPDATE`, lỗi "could not serialize access due to concurrent update" ở `REPEATABLE READ` và lời khuyên thử lại cả giao dịch, deadlock và cách phòng.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên PostgreSQL 16.15, hai kết nối trên cùng máy. Mẫu cột `version` là cách làm phổ biến, không phải tính năng riêng của PostgreSQL.
Bài viết và hình được thiết kế độc lập.

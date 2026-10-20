# Bản sao đọc: vì sao vừa ghi xong lại đọc không thấy

**Mô hình bản sao đọc (read replica) dồn mọi lệnh ghi vào một máy cơ sở dữ liệu chính và chia lệnh đọc cho các bản sao.**
Bản chính đỡ tải đọc, nhưng bản sao luôn đi sau bản chính một khoảng: đọc ở bản sao ngay sau khi ghi có thể chưa thấy dữ liệu vừa ghi.

![Ba khung. Khung một: ứng dụng gửi mọi lệnh ghi tới bản chính; bản chính chuyển nhật ký WAL cho bản sao; ứng dụng đọc từ bản sao. Khung hai, theo thử nghiệm trên PostgreSQL 16 với bản sao cố ý trễ 3 giây: ứng dụng ghi đơn hàng và lấy vị trí WAL sau commit; đọc ngay ở bản sao được 0 dòng; chờ tới khi bản sao phát lại tới vị trí đó, khoảng 2,9 giây, thì đọc được 1 dòng. Khung ba: ba cách để đọc thấy dữ liệu mình vừa ghi: đọc từ bản chính, chờ bản sao đuổi kịp vị trí WAL, hoặc cho commit chờ bản sao đồng bộ phát lại xong.](../../diagrams/sd-04-001-main.svg)

## Từ viết tắt

- **WAL** (Write-Ahead Log) — nhật ký ghi trước: PostgreSQL ghi mọi thay đổi vào nhật ký này trước khi sửa dữ liệu; bản sao nhận nhật ký đó và phát lại để có cùng dữ liệu.
- **LSN** (Log Sequence Number) — số thứ tự trong nhật ký: vị trí của một bản ghi trong WAL, chỉ tăng dần, nên so hai LSN là biết bản sao đã phát lại tới đâu.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để đọc và ghi dữ liệu trong cơ sở dữ liệu quan hệ; nằm trong tên PostgreSQL.

## Đọc hình

**Khung 1 · Đường đi.** Bản chính nhận mọi lệnh ghi, ghi thay đổi vào WAL rồi gửi WAL cho bản sao; bản sao phát lại WAL theo đúng thứ tự.
Ở PostgreSQL, bản sao chạy chế độ hot standby chỉ nhận truy vấn đọc: trong thử nghiệm dưới đây, lệnh `INSERT` gửi tới bản sao bị từ chối với lỗi "cannot execute INSERT in a read-only transaction".

**Khung 2 · Đọc ngay sau khi ghi.** Sao chép mặc định là bất đồng bộ: bản chính báo commit xong mà không chờ bản sao.
Lệnh đọc đến bản sao trước khi nó phát lại tới chỗ đó thì trả về dữ liệu cũ, ở đây là 0 dòng.

**Khung 3 · Ba cách sửa.** Cả ba đều đổi một thứ lấy một thứ khác; mục “Giới hạn cần nhớ” nói giá của từng cách.

## Thử nghiệm: thấy khoảng trễ bằng mắt

Dựng một bản chính và một bản sao PostgreSQL 16.15 trên cùng máy, sao chép luồng bất đồng bộ.
Hai máy cùng một chỗ thì gần như không trễ, nên bản sao được đặt `recovery_min_apply_delay = '3s'`: tham số này bắt bản sao chỉ phát lại một commit khi đồng hồ của nó đã qua thời điểm commit ít nhất 3 giây.
Ngoài đời, độ trễ đến từ mạng chậm hay máy quá tải, dài ngắn không đều; con số 3 giây ở đây là cố ý đặt để nhìn thấy.

| Bước | Kết quả đo |
|---|---|
| Ghi một đơn hàng ở bản chính, lấy `pg_current_wal_insert_lsn()` | `0/3027DD0` |
| Đọc ngay ở bản sao | phát lại mới tới `0/3027DA8`, đếm được 0 dòng |
| Hỏi lại tới khi `pg_last_wal_replay_lsn()` của bản sao không nhỏ hơn vị trí trên | mất 2,9 giây, đếm được 1 dòng |

Lần thứ hai, bản sao được khai là bản sao đồng bộ (`synchronous_standby_names`).
Với `synchronous_commit = on`, commit trả về ngay (0,0 giây) nhưng bản sao vẫn đọc ra 0 dòng: mức này chỉ chờ bản sao ghi WAL xuống đĩa, chưa chờ nó phát lại.
Với `synchronous_commit = remote_apply`, commit mất 3,0 giây và bản sao đọc thấy dòng mới ngay sau đó.

## Giới hạn cần nhớ

- **Đọc ở bản chính:** chỉ nên dành cho lệnh đọc ngay sau lệnh ghi của chính người đó. Dồn quá nhiều lệnh đọc về bản chính thì mất luôn lý do dùng bản sao.
- **Chờ bản sao đuổi kịp LSN:** ứng dụng phải mang LSN theo phiên của người dùng. Bản PostgreSQL 16 không có lệnh chờ sẵn, nên phải hỏi lại như trong thử nghiệm; tài liệu PostgreSQL 19 thêm lệnh `WAIT FOR LSN` chạy trên bản sao để chờ việc đó.
- **`remote_apply`:** commit nào dùng mức này phải chờ các bản sao đồng bộ phát lại xong, và chỉ các bản sao đồng bộ đó mới chắc chắn đã thấy thay đổi; bản sao bất đồng bộ khác vẫn có thể đi sau. Tham số đặt được cho từng giao dịch (`SET LOCAL synchronous_commit`), nên có thể chỉ dùng cho lệnh ghi cần đọc ngay; đặt cho cả hệ thống thì mọi lệnh ghi chậm theo bản sao đồng bộ phải chờ. Tài liệu PostgreSQL còn cảnh báo commit có thể không bao giờ xong nếu một bản sao đồng bộ bị sập, trừ khi khai thêm bản sao dự phòng.

## Nhìn hình trả lời

Một người đổi ảnh đại diện rồi tải lại trang thì vẫn thấy ảnh cũ. Hệ thống ghi vào bản chính và đọc từ bản sao.
Chỗ nào trong hình gây ra chuyện này, và cách nào sửa được mà không làm chậm mọi lệnh ghi của mọi người?

<details>
<summary>Xem đáp án</summary>

Lệnh đọc khi tải lại trang đến bản sao trước khi bản sao phát lại tới thay đổi vừa ghi (khung 2).
Hai cách đầu ở khung 3 chỉ tác động tới người vừa ghi: gửi lệnh đọc của người đó về bản chính trong một lúc, hoặc nhớ LSN sau commit và chỉ đọc bản sao đã phát lại tới đó.
Cách thứ ba (`remote_apply`) chỉ thỏa điều kiện nếu đặt riêng cho giao dịch đổi ảnh (`SET LOCAL synchronous_commit = remote_apply`) và trang được đọc từ một bản sao đồng bộ; đặt cho cả hệ thống thì mọi lệnh ghi của mọi người đều phải chờ.

</details>

<details>
<summary>Xem sâu hơn: hai bản sao, hai tốc độ</summary>

Mỗi bản sao phát lại WAL theo tốc độ riêng. Nếu hai lệnh đọc liên tiếp của cùng một người rơi vào hai bản sao khác nhau, lần đầu vào bản sao đã phát lại xa hơn, lần sau vào bản sao chậm hơn, thì dữ liệu người đó vừa thấy có thể biến mất ở lần đọc sau.
Đây là suy luận của người biên soạn từ cách phát lại WAL, không phải thử nghiệm trong bài; cách quen thuộc là cho mỗi phiên bám vào một bản sao, hoặc dùng cùng phép so LSN ở trên cho cả hai lần đọc.

Tài liệu PostgreSQL gợi ý cách theo dõi độ trễ: chênh lệch giữa `pg_current_wal_lsn()` ở bản chính và cột `sent_lsn` của `pg_stat_replication` cho thấy bản chính gửi chậm, còn chênh lệch giữa `pg_last_wal_receive_lsn()` và `pg_last_wal_replay_lsn()` ở bản sao cho thấy bản sao nhận nhanh hơn phát lại.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/read-replica-pattern.md): ghi vào bản chính, đọc ở bản sao, độ trễ sao chép và ba hướng giảm nhẹ.
- [PostgreSQL 16 — tham số cấu hình, tại commit cố định](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/config.sgml): `recovery_min_apply_delay`, các mức của `synchronous_commit` (`on` chờ bản sao ghi xuống đĩa, `remote_apply` chờ bản sao phát lại). Đọc từ bản clone của kho, nhánh `REL_16_STABLE`.
- [PostgreSQL 16 — tính sẵn sàng cao và sao chép, tại commit cố định](https://github.com/postgres/postgres/blob/8e928803020e5b5694cde58e4851fce64ef9d520/doc/src/sgml/high-availability.sgml): hot standby chỉ cho đọc, commit có thể không xong khi bản sao đồng bộ sập, cách theo dõi độ trễ bằng LSN.
- [PostgreSQL 19 — mục Read-Your-Writes Consistency, tại commit cố định](https://github.com/postgres/postgres/blob/10a0dcfc25fba51b2e0d3bbcb11584ecfb70f848/doc/src/sgml/high-availability.sgml): lấy LSN sau commit ở bản chính, dùng `WAIT FOR LSN` ở bản sao. Đọc từ bản clone, nhánh `REL_19_STABLE`.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên PostgreSQL 16.15, một máy, hai cụm cơ sở dữ liệu; con số chỉ đúng cho lần chạy đó.
Bài viết và hình được thiết kế độc lập.

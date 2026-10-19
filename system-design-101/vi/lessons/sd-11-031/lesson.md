# Khóa phân tán: sáu nơi dùng, và cái bẫy khi khóa hết hạn

**Khóa phân tán bảo đảm rằng tại một thời điểm chỉ một bên trong hệ thống nhiều máy được làm một việc.** Bài nguồn kể sáu nơi dùng. Bài này giữ sáu tên đó, rồi tập trung vào một cái bẫy mà cả sáu đều có chung: khóa thường có hạn dùng, và một bên chậm có thể vẫn tin mình còn giữ khóa khi đã hết hạn.

![Ba khung. Hai khung đầu, mỗi khung ba trong sáu tình huống dùng khóa phân tán: bầu người dẫn đầu, lập lịch tác vụ, cấp phát tài nguyên, điều phối vi dịch vụ, quản lý tồn kho, quản lý phiên. Khung ba, thử nghiệm: máy A giữ khóa hết hạn sau 10 bước rồi tạm dừng tới bước 15, máy B lấy khóa ở bước 12 và ghi; khi A tỉnh dậy ghi đè, kho nhận cả hai; nếu kho kiểm tra số thứ tự khóa thì lần ghi của A bị từ chối.](../../diagrams/sd-11-031-main.svg)

## Từ viết tắt

- **TTL** (Time To Live) — thời gian sống: khoảng thời gian một khóa còn hiệu lực trước khi tự hết hạn, để khóa không giữ mãi nếu bên giữ nó sập.

## Đọc hình

**Bầu người dẫn đầu (Leader Election).** Khóa bảo đảm mỗi lúc chỉ một nút làm người dẫn đầu. Nút nào lấy được khóa là người dẫn đầu; các nút còn lại chờ hoặc thử lại.

**Lập lịch tác vụ (Task Scheduling).** Trong một bộ lập lịch phân tán, khóa bảo đảm một tác vụ đến giờ chỉ do một máy làm việc chạy, nhờ vậy không chạy trùng.

**Cấp phát tài nguyên (Resource Allocation).** Với tài nguyên dùng chung như hệ thống tệp, cổng mạng hay thiết bị, khóa bảo đảm một lúc chỉ một tiến trình dùng nó.

**Điều phối vi dịch vụ (Microservices Coordination).** Khi nhiều vi dịch vụ cùng làm một việc, như cập nhật dữ liệu liên quan nằm ở nhiều cơ sở dữ liệu, khóa giúp các thao tác đó diễn ra có kiểm soát và có thứ tự.

**Quản lý tồn kho (Inventory Management).** Ở cửa hàng trực tuyến, nhiều người mua cùng một món cùng lúc; khóa giữ số lượng tồn chính xác.

**Quản lý phiên (Session Management).** Phiên của một người dùng chỉ nên bị sửa bởi một máy chủ mỗi lúc, để tránh sai lệch.

## Cái bẫy chung: khóa có hạn

Khóa mà không có hạn thì nếu bên giữ nó sập, mọi người chờ mãi. Vì thế khóa thường có TTL. Nhưng như vậy khóa có thể hết hạn khi bên giữ chưa xong. Thử nghiệm dưới đây tái hiện điều đó.

Ngày 2026-10-19, một chương trình Python nhỏ, thời gian tính bằng bước, không có mạng thật. Máy A lấy khóa ở bước 0 với TTL 10. Rồi A tạm dừng (ví dụ vì một lần dọn rác bộ nhớ dài) tới bước 15. Ở bước 12 khóa đã hết hạn nên máy B lấy được và ghi vào kho. Ở bước 15 A tỉnh dậy, vẫn tin mình giữ khóa và ghi.

| Kho kiểm tra gì | Kết quả |
|---|---|
| Không kiểm tra | Cả hai lần ghi được nhận, giá trị cuối là của A (ghi sau cùng, dựa vào một khóa đã hết hạn) |
| Kiểm tra số thứ tự của khóa (mỗi lần cấp khóa tăng một số; kho từ chối số nhỏ hơn số đã thấy) | Lần ghi của B được nhận (số 2), lần ghi của A bị từ chối (số 1) |

Bài học: một khóa tự nó không đủ khi bên giữ có thể chậm; kho phải cùng tham gia, ví dụ bằng số thứ tự đi kèm khóa. Đây là ý tưởng "fencing token" trong tài liệu về khóa phân tán nói chung.

## Giới hạn cần nhớ

Mô phỏng chỉ có một khóa, hai máy và thời gian rời rạc; nó không dùng một dịch vụ khóa thật (như ZooKeeper, etcd hay Redis), nên không nói gì về từng sản phẩm. Nó cũng giả định kho đủ thông minh để kiểm tra số thứ tự, điều không phải kho nào làm được. Nên dùng khóa đúng chỗ cũng là một câu hỏi: nhiều tình huống trong sáu tình huống trên có thể giải bằng cách khác (ví dụ ghi có điều kiện vào cơ sở dữ liệu), việc này nằm ngoài bài.

## Nhìn hình trả lời

Hai máy cùng đến giờ chạy một báo cáo hằng ngày. Một máy lấy khóa và chạy, chạy lâu hơn TTL của khóa. Điều gì có thể xảy ra, và cách sửa đơn giản nhất là gì?

<details>
<summary>Xem đáp án</summary>

Khóa hết hạn khi báo cáo còn đang chạy nên máy kia lấy được khóa và chạy trùng, làm đúng điều khóa sinh ra để tránh. Cách đơn giản nhất: đặt TTL dài hơn thời gian chạy xấu nhất, hoặc để máy đang chạy gia hạn khóa định kỳ, hoặc làm cho kết quả của báo cáo ghi lại được hai lần mà không đổi (chạy trùng vô hại).
Đây là suy luận của người biên soạn từ thử nghiệm.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một câu định nghĩa và sáu tình huống, mỗi tình huống một hoặc hai câu. Bài này giữ định nghĩa và sáu tình huống với tên đó, thêm thử nghiệm khóa hết hạn và nhận xét về giới hạn. Phần sáu tình huống chưa được đối chiếu với tài liệu bên ngoài.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/why-do-we-need-to-use-a-distributed-lock.md): sáu tình huống dùng khóa phân tán. Thử nghiệm và đáp án là của người biên soạn.
- [Martin Kleppmann — How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html): bàn về khóa có hạn và số thứ tự của khóa (fencing token). Chưa mở lại trong phiên viết (không mở được trang từ môi trường); kiến thức chung của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

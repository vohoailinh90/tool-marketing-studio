# Dữ liệu đi từ ứng dụng này sang ứng dụng khác

**Một tin nhắn chat đi qua nhân hệ điều hành của máy gửi, qua mạng, rồi qua nhân của máy nhận trước khi tới ứng dụng; mỗi chặng thêm hoặc bóc một lớp.**
Bài nguồn kể đường đi của một tin nhắn từ máy chủ này sang máy chủ khác; bài này giữ đúng các tên chặng của nguồn, chia thành hai chuỗi bốn bước, máy gửi và máy nhận, rồi giải thích từng bước bằng tài liệu và mã nguồn của nhân Linux.

![Hai nhóm bước và một khung ghi nhớ. Máy gửi, bốn bước: ứng dụng gửi tin chat từ không gian người dùng; tin sang không gian nhân và vào bộ đệm gửi; ngăn xếp mạng bọc tiêu đề TCP, IP, MAC rồi qdisc xếp hàng cho tin ra; card mạng NIC lấy tin từ bộ đệm vòng rồi đưa lên Internet. Máy nhận, bốn bước: NIC nhận gói vào bộ đệm vòng và báo CPU bằng ngắt; phần việc nhận chạy ở ngắt mềm hoặc ksoftirqd; nhân mở từng lớp liên kết dữ liệu, mạng, giao vận; dữ liệu được chép sang không gian người dùng tới ứng dụng. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-009-main.svg)

## Từ viết tắt

- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: quy ước để hai máy truyền dữ liệu tin cậy; tin chat được bọc thêm một tiêu đề TCP.
- **IP** (Internet Protocol) — giao thức Internet: dán nhãn địa chỉ để dữ liệu tìm đúng máy; tin chat được bọc thêm một tiêu đề IP.
- **MAC** (Media Access Control) — điều khiển truy cập môi trường: lớp chuyển dữ liệu giữa các thiết bị nối liền nhau; tin chat được bọc thêm một tiêu đề MAC.
- **NIC** (Network Interface Card) — card giao tiếp mạng: phần cứng nối máy với mạng, nơi dữ liệu rời máy gửi và vào máy nhận.
- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần cứng chạy chương trình; ở đây nó nhận ngắt từ card mạng.
- **FIFO** (First In, First Out) — vào trước ra trước: hàng đợi lấy ra theo đúng thứ tự đã đưa vào; một loại qdisc của Linux xếp gói theo kiểu này.

## Đọc hình

Tên các chặng là của bài nguồn. Lời giải thích dưới đây là của người biên soạn, dựa vào chú thích trong mã và tài liệu của nhân Linux (tên hàm và tên tệp ghi trong mục nguồn); bài nguồn không nói nó mô tả hệ điều hành nào, nên bài này đọc nó như một bức tranh về Linux.

**Máy gửi.** Ứng dụng chat chạy ở không gian người dùng (user space) và nhờ nhân gửi tin đi; tin sang không gian nhân (kernel space) và nằm trong bộ đệm gửi (send buffer). Ngăn xếp mạng (network stack) dựng gói và bọc tiêu đề TCP, IP rồi MAC (kiến thức chung của người biên soạn). Chú thích của hàm `__dev_queue_xmit` trong nhân Linux nói hàm này xếp một bộ đệm vào hàng đợi để truyền ra thiết bị mạng, và người gọi phải dựng xong bộ đệm trước khi gọi. Hàng đợi đó do qdisc (Queueing Disciplines, "kỷ luật xếp hàng") quản: mã `sch_generic.c` có sẵn nhiều loại, trong đó có `pfifo_fast`, hàng FIFO ba băng, và chú thích ghi rõ tại một thời điểm chỉ một CPU xử lý một qdisc. Cuối chặng, NIC lấy gói ra khỏi bộ đệm vòng (ring buffer), hàng đợi các ô mô tả gói giữa nhân và card; tài liệu `scaling` của Linux gọi mỗi hàng đợi nhận của card là một `RX ring`.

**Trên đường.** NIC đưa dữ liệu lên Internet. Qua nhiều router và switch, dữ liệu tới NIC của máy nhận (kiến thức chung của người biên soạn).

**Máy nhận.** Tài liệu `scaling` của Linux nói mỗi hàng đợi nhận của card có một ngắt riêng, và card kích hoạt ngắt đó để báo một CPU rằng có gói mới. Tài liệu `NAPI` mô tả bước tiếp theo: bên điều khiển card lên lịch cho một đợt xử lý, và đợt xử lý thường chạy trong ngữ cảnh ngắt mềm (soft interrupt) dù có thể chuyển sang luồng nhân riêng; mỗi đợt chỉ nhận tối đa một số gói gọi là `budget`, và trong lúc đợt đó chưa xong thì ngắt của card được giữ ở trạng thái che. Mã `softirq.c` cho thấy ksoftirqd là một tác vụ nhân riêng của từng CPU: nếu ngắt mềm được báo ngoài ngữ cảnh ngắt thì ksoftirqd được đánh thức để chạy nó, còn trong ngữ cảnh ngắt thì ngắt mềm chạy khi thoát ngắt. Sau đó gói được đưa lên ngăn xếp, mở lần lượt qua lớp liên kết dữ liệu, lớp mạng và lớp giao vận, rồi chép sang không gian người dùng tới ứng dụng chat bên nhận (hai điều này là kiến thức chung của người biên soạn).

## Giới hạn cần nhớ

Bài nguồn tả một đường đi điển hình và dừng ở đó: không nói bắt tay TCP, gói bị mất hay chia nhỏ dữ liệu, và cũng không nói hệ điều hành nào. Bài này không bổ sung những điều đó.
Chuyện "ngắt mềm để ksoftirqd lấy dữ liệu" của nguồn là bức tranh đơn giản: theo mã Linux, ksoftirqd chạy ngắt mềm khi nó được báo ngoài ngữ cảnh ngắt, còn bình thường ngắt mềm chạy ngay khi thoát ngắt. Hệ điều hành khác có thể đặt tên và chia chặng khác; bài này không nói tới chúng.

## Nhìn hình trả lời

Tin nhắn vừa tới card mạng của máy nhận. Ai báo cho CPU, bằng cách nào, và dữ liệu phải đi qua những lớp nào trước khi tới ứng dụng?

<details>
<summary>Xem đáp án</summary>

Card mạng báo CPU bằng một ngắt. Phần việc nhận gói sau đó chạy ở ngắt mềm, do ksoftirqd nếu ngắt mềm được báo ngoài ngữ cảnh ngắt.
Gói được mở lần lượt qua lớp liên kết dữ liệu, lớp mạng và lớp giao vận, rồi chép sang không gian người dùng để tới ứng dụng chat.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là ba đoạn văn liền, mỗi đoạn kể một chặng, kèm một ảnh minh họa. Bài này chỉ giữ tên các chặng và các bước; không dịch hay diễn đạt lại các câu của nguồn mà giải thích từng bước từ chú thích và tài liệu của nhân Linux (`__dev_queue_xmit`, `sch_generic.c`, `softirq.c`, `scaling` và `NAPI`, tại commit cố định ở mục nguồn), còn phần bọc tiêu đề, đường đi giữa hai máy và các lớp mạng là kiến thức chung của người biên soạn.
Hình tách thành hai chuỗi bốn bước và không dùng ảnh nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-is-data-transmitted-between-applications.md): tên các chặng giữa hai máy.
- [Linux — net/core/dev.c](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/net/core/dev.c) và [net/sched/sch_generic.c](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/net/sched/sch_generic.c): hàm xếp bộ đệm vào hàng đợi truyền, qdisc và `pfifo_fast`. Đọc từ kho mã.
- [Linux — kernel/softirq.c](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/kernel/softirq.c), [Documentation/networking/napi.rst](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/Documentation/networking/napi.rst) và [Documentation/networking/scaling.rst](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/Documentation/networking/scaling.rst): ksoftirqd theo từng CPU, đợt xử lý nhận gói, ngắt của hàng đợi nhận. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Phần bọc tiêu đề, đường đi giữa hai máy, các lớp mạng và các câu giải nghĩa viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

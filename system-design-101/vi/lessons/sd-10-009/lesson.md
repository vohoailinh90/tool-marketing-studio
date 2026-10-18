# Dữ liệu đi từ ứng dụng này sang ứng dụng khác

**Một tin nhắn chat đi qua nhân hệ điều hành của máy gửi, qua mạng, rồi qua nhân của máy nhận trước khi tới ứng dụng; mỗi chặng thêm hoặc bóc một lớp.**
Bài nguồn kể đường đi của một tin nhắn từ máy chủ này sang máy chủ khác; bài này chia thành hai chặng, máy gửi và máy nhận, mỗi chặng bốn bước.

![Hai nhóm bước và một khung ghi nhớ. Máy gửi, bốn bước: ứng dụng gửi tin chat từ không gian người dùng; tin vào bộ đệm gửi ở không gian nhân; ngăn xếp mạng bọc thêm tiêu đề TCP, IP và MAC, qdisc kiểm soát luồng; card mạng NIC nhận qua bộ đệm vòng rồi gửi lên Internet. Máy nhận, bốn bước: NIC nhận tin, đặt vào bộ đệm vòng và báo CPU bằng ngắt cứng; CPU báo ngắt mềm để ksoftirqd lấy dữ liệu; dữ liệu được mở qua lớp liên kết dữ liệu, lớp mạng, lớp giao vận; dữ liệu được chép sang không gian người dùng tới ứng dụng. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-009-main.svg)

## Từ viết tắt

- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: quy ước để hai máy truyền dữ liệu tin cậy; tin chat được bọc thêm một tiêu đề TCP.
- **IP** (Internet Protocol) — giao thức Internet: dán nhãn địa chỉ để dữ liệu tìm đúng máy; tin chat được bọc thêm một tiêu đề IP.
- **MAC** (Media Access Control) — điều khiển truy cập môi trường: lớp chuyển dữ liệu giữa các thiết bị nối liền nhau; tin chat được bọc thêm một tiêu đề MAC.
- **NIC** (Network Interface Card) — card giao tiếp mạng: phần cứng nối máy với mạng, nơi dữ liệu rời máy gửi và vào máy nhận.
- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần cứng chạy chương trình; ở đây nó nhận ngắt từ card mạng.

## Đọc hình

**Máy gửi.** Ứng dụng chat chạy ở không gian người dùng (user space) gửi tin đi. Tin vào bộ đệm gửi (send buffer) ở không gian nhân (kernel space). Ngăn xếp mạng (network stack) bọc dữ liệu bằng tiêu đề TCP, tiêu đề IP rồi tiêu đề MAC; dữ liệu cũng đi qua qdisc (Queueing Disciplines) để kiểm soát luồng. Sau đó nó tới NIC qua một bộ đệm vòng (ring buffer).

**Trên đường.** NIC đưa dữ liệu lên Internet. Qua nhiều chặng giữa các router và switch, dữ liệu tới NIC của máy nhận.

**Máy nhận.** NIC đặt dữ liệu vào bộ đệm vòng và gửi một ngắt cứng (hard interrupt) cho CPU. CPU gửi ngắt mềm (soft interrupt) để ksoftirqd nhận dữ liệu từ bộ đệm vòng. Dữ liệu được mở lần lượt qua lớp liên kết dữ liệu, lớp mạng và lớp giao vận. Cuối cùng nó được chép sang không gian người dùng và tới ứng dụng chat bên nhận.

## Giới hạn cần nhớ

Bài nguồn nói về một đường đi điển hình và dừng ở đó: không nói bắt tay TCP, gói bị mất hay chia nhỏ dữ liệu, và cũng không nói hệ điều hành nào.
Tên qdisc và ksoftirqd là của nhân Linux: mã nguồn nhân Linux tại commit cố định có tệp xử lý qdisc và một tác vụ ksoftirqd riêng cho mỗi CPU. Hệ điều hành khác có thể đặt tên và chia chặng khác; bài này không nói tới chúng.

## Nhìn hình trả lời

Tin nhắn vừa tới card mạng của máy nhận. Ai báo cho CPU, bằng cách nào, và dữ liệu phải đi qua những lớp nào trước khi tới ứng dụng?

<details>
<summary>Xem đáp án</summary>

NIC đặt dữ liệu vào bộ đệm vòng rồi báo CPU bằng ngắt cứng. CPU gửi ngắt mềm để ksoftirqd lấy dữ liệu từ bộ đệm vòng.
Dữ liệu được mở lần lượt qua lớp liên kết dữ liệu, lớp mạng và lớp giao vận, rồi chép sang không gian người dùng để tới ứng dụng chat.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn viết ba đoạn văn liền: máy gửi, đường đi, máy nhận, và có một ảnh minh họa. Hình ở đây tách thành hai chuỗi bốn bước và không dùng ảnh nguồn.
Hai câu về Linux (qdisc và ksoftirqd có trong nhân; tài liệu `NAPI` của Linux nói việc nhận gói thường chạy trong ngữ cảnh ngắt mềm) lấy từ mã nguồn và tài liệu của nhân Linux tại commit cố định, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-is-data-transmitted-between-applications.md): đường đi của một tin nhắn giữa hai máy.
- [Linux — kernel/softirq.c](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/kernel/softirq.c), [net/sched/sch_generic.c](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/net/sched/sch_generic.c) và [Documentation/networking/napi.rst](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/Documentation/networking/napi.rst): ksoftirqd theo từng CPU, qdisc, xử lý nhận gói trong ngữ cảnh ngắt mềm. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa TCP, IP, MAC, NIC, CPU trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

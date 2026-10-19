# Linux khởi động chậm ở đâu? Đo và đọc bằng systemd-analyze và journalctl

**Máy Linux khởi động mất gần bảy mươi giây: thời gian đó nằm ở nhân, ở initrd hay ở không gian người dùng, và trong đó là đơn vị nào? Bốn lệnh có sẵn của systemd trả lời lần lượt từng câu hỏi, và ví dụ trong chính tài liệu của chúng cho thấy cách đọc để khỏi sửa nhầm chỗ.**
Bài này không kể lại tám bước khởi động (bài "Khởi động Linux: tám bước của nguồn…" của kho này đã làm việc đó, nên bài này không lặp lại) mà dạy cách đo và đọc kết quả: phần số liệu lấy từ ví dụ trong trang man của `systemd-analyze`, phần tính là của bài, và những gì chạy được trên máy viết bài được ghi riêng.

![Bốn bước và một khung ghi nhớ. Bước một, systemd-analyze time: chia thời gian khởi động, ví dụ 2,584 giây nhân, 19,176 giây initrd, 47,847 giây không gian người dùng, tổng 1 phút 9,608 giây. Bước hai, systemd-analyze blame: xếp các đơn vị theo thời gian khởi tạo, pmlogger đứng đầu với 32,875 giây. Bước ba, systemd-analyze critical-chain: chuỗi chặn multi-user target, trong đó wait-online tốn 20,905 giây và pmlogger không có mặt. Bước bốn, journalctl -b: nhật ký lần khởi động này, thêm -p err hoặc -k để lọc. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-026-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần cứng chạy chương trình; bài chỉ nhắc nó khi nói thời gian nhân và dịch vụ chiếm.

## Đọc hình

**Bước một: `systemd-analyze time`.** Tài liệu nói lệnh này in thời gian ở nhân trước khi vào không gian người dùng, thời gian ở initrd trước khi vào hệ thống thường, và thời gian không gian người dùng khởi tạo. Ví dụ trong tài liệu: `Startup finished in 2.584s (kernel) + 19.176s (initrd) + 47.847s (userspace) = 1min 9.608s`. Phần không gian người dùng chiếm 47,847 trên 69,608 giây; con số này chưa nói bên trong đó là việc gì, nên bước tiếp theo là xem đơn vị nào trong phần ấy chậm. Tài liệu lưu ý các số này đo đến lúc mọi dịch vụ đã được bật lên, không phải lúc chúng khởi tạo xong hay ổ đĩa rảnh.

**Bước hai: `systemd-analyze blame`.** In các đơn vị theo thời gian khởi tạo, lâu nhất trước. Ví dụ của tài liệu: `pmlogger.service` 32,875 giây, `systemd-networkd-wait-online.service` 20,905 giây, `dev-vda1.device` 13,299 giây. Tài liệu cảnh báo bốn điều: kết quả có thể gây hiểu lầm vì một dịch vụ chậm có thể chỉ đang chờ dịch vụ khác; dịch vụ `Type=simple` không hiện vì systemd coi chúng bật tức thì; lệnh chỉ đo thời gian ở trạng thái `activating`, không đo thời gian xếp hàng; và nó phản ánh mã chương trình hơn là độ trễ do chờ phần cứng.

**Bước ba: `systemd-analyze critical-chain`.** In cây các đơn vị mà `multi-user.target` phải chờ. Sau dấu `@` là thời điểm đơn vị lên, sau dấu `+` là thời gian nó khởi tạo. Tài liệu có ví dụ bảy đơn vị có số `+`, chuỗi kết thúc ở `multi-user.target @47.820s`. Bài cộng các số `+` đó: 29,247 giây, tức 61,2% của 47,820 giây; phần còn lại, khoảng 18,6 giây, chưa được các số `+` giải thích: có thể là việc chưa được báo cáo hoặc thời gian xếp hàng, nên không gọi nó là chờ. Riêng `systemd-networkd-wait-online.service +20.905s` là 71,5% công việc trên chuỗi và 43,7% tổng 47,820 giây. Cũng ví dụ ấy, `pmlogger.service`, đứng đầu `blame`, không có mặt trên chuỗi: theo cách chuỗi được định nghĩa, rút ngắn nó không đưa `multi-user.target` lên sớm hơn, còn rút ngắn `wait-online` thì có. Đây là chỗ hai lệnh bổ sung nhau. Tài liệu cũng nhắc chuỗi có thể gây hiểu lầm do kích hoạt theo ổ cắm và do chạy song song.

**Bước bốn: `journalctl -b`.** Hai lệnh trên cho biết cái gì chậm, nhật ký cho biết vì sao. Theo trang man của `journalctl`: `-b` hiện thông điệp của lần khởi động hiện tại, `-b -1` của lần trước nữa, `--list-boots` liệt kê các lần khởi động, `-p err` chỉ giữ thông điệp từ mức lỗi trở lên (theo thang syslog, mức nhỏ hơn quan trọng hơn) và `-k` chỉ giữ thông điệp của nhân. Ví dụ để tìm nguyên nhân `wait-online`: đọc `journalctl -b -u systemd-networkd-wait-online.service`. Nếu máy khởi động chậm bất thường chỉ hôm nay, so `-b` với `-b -1`.

## Giới hạn cần nhớ

Các con số là ví dụ nằm trong tài liệu systemd, không phải số đo của bài; bài chỉ tính phép chia và cộng trên chúng. Bài không có số đo thật về khởi động: máy viết bài chạy trong container, nơi `systemd-analyze blame` trả `System has not been booted with systemd as init system (PID 1). Can't operate.` và `journalctl -b` báo không có tệp nhật ký. Cái chạy được ngoài máy khởi động thật là `systemd-analyze timespan` (đổi `1min 9.608s` ra 69.608.000 micro giây) và `systemd-analyze verify` cho một tệp đơn vị; bài chưa dùng chúng để kết luận gì về tốc độ khởi động. Bài cũng không bàn firmware, bộ nạp khởi động và initrd ngoài việc chúng là các phần của bước một, và không nói máy nào "khởi động chậm" là bao lâu.

## Nhìn hình trả lời

Trong ví dụ của tài liệu, `blame` xếp `pmlogger.service` đầu với 32,875 giây. Bạn có nên làm nó nhanh hơn trước tiên để `multi-user.target` tới sớm hơn không? Và đơn vị nào nên xem trước?

<details>
<summary>Xem đáp án</summary>

Chưa: `pmlogger.service` không nằm trên chuỗi tới `multi-user.target` trong ví dụ, nên theo chuỗi ấy rút ngắn nó chưa chắc làm mục tiêu tới sớm hơn (tài liệu cũng dặn kết quả có thể gây hiểu lầm).
Nên xem `systemd-networkd-wait-online.service` trước: `+20.905s` ngay trên chuỗi, chiếm 71,5% công việc của chuỗi. Rồi dùng `journalctl -b -u systemd-networkd-wait-online.service` để biết nó chờ gì.

</details>

<details>
<summary>Xem sâu hơn: cách tính ở bước ba</summary>

Bài chép chuỗi ví dụ của tài liệu vào một đoạn Python nhỏ, tách các số sau `@` và `+` (đổi `ms` sang giây), rồi tính: tổng các `+` là 0,548 + 2,247 + 20,905 + 1,690 + 1,904 + 1,776 + 0,177 = 29,247 giây; 29,247 chia 47,820 ra 61,2%; 20,905 chia 29,247 ra 71,5%; 20,905 chia 47,820 ra 43,7%. Công cụ `systemd-analyze timespan` cho cùng các số ở dạng micro giây (47.820.000 và 20.905.000) khi đổi tay.

Một điều dễ nhầm: tổng thời gian khởi tạo trên chuỗi không bằng thời gian tới đích, vì phần còn lại không có số `+` nào giải thích. Về một khoảng giữa hai đơn vị liền nhau, trong ví dụ, `networkd` lên ở 11,109 giây và `wait-online` lên ở 12,804 giây: `networkd` mất 1,690 giây để khởi tạo nên xong khoảng 12,799 giây, và `wait-online` bắt đầu ngay sau đó (chỉ chừng 5 mili giây sau); phần dài 1,690 giây ấy đã nằm trong số `+` của `networkd`, không phải thời gian chờ thêm.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/linux-boot-process-explained.md): chỉ lấy chủ đề khởi động Linux; góc nhìn đo thời gian, ví dụ và phép tính là của bài này. Cùng nguồn với một bài khác của kho kể tám bước khởi động; bài này không chép lại nội dung đó (liên kết nằm ở trường related của metadata).
- [systemd — systemd-analyze(1)](https://github.com/systemd/systemd/blob/8be8cffd7579208ad6d4191d08bdb731132dcc4f/man/systemd-analyze.xml): `time`, `blame`, `critical-chain` và các ví dụ của chúng. Đọc từ kho mã.
- [systemd — journalctl(1)](https://github.com/systemd/systemd/blob/8be8cffd7579208ad6d4191d08bdb731132dcc4f/man/journalctl.xml): `-b`, `--list-boots`, `-p`, `-k`. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Các lệnh `systemd-analyze timespan` và `verify` và thông báo lỗi trong container được chạy ngày 2026-10-19 với systemd 255.4; các câu giải nghĩa trong mục từ viết tắt là kiến thức chung của người biên soạn.
Bài viết và hình được thiết kế độc lập.

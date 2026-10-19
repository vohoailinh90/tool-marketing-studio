# Khởi động Linux: tám bước của nguồn, điều tài liệu thêm vào, và một lần đọc tĩnh các tệp đơn vị systemd

**Bài nguồn kể tám bước từ lúc bật nguồn tới màn hình đăng nhập. Bài này giữ đủ tám bước, đặt từng bước cạnh trang `boot(7)` của Linux và trang `bootup(7)` của systemd để xem bước nào được xác nhận, bước nào thiếu (đáng kể nhất là `initramfs`), và đọc các tệp đơn vị systemd của một máy thật bằng một chương trình nhỏ để thấy `default.target` thực sự kéo theo bao nhiêu thứ và chúng xếp thứ tự ra sao.**

![Ba khung. Khung một, tám bước khởi động Linux của nguồn: bật nguồn và chạy POST, phát hiện thiết bị, chọn thiết bị khởi động, bộ nạp khởi động GRUB, nhân và systemd là tiến trình đầu tiên, đạt mục tiêu mặc định, chạy tập lệnh khởi động, màn hình đăng nhập. Khung hai, điều tài liệu độc lập thêm hoặc sửa: phần sụn chỉ khởi tạo tối thiểu rồi giao cho bộ nạp, hoặc nạp nhân trực tiếp; giữa bộ nạp và systemd có thể có initramfs; mục tiêu mặc định thường là bí danh của graphical target hoặc multi-user target. Khung ba, đọc tĩnh các tệp đơn vị systemd của máy đo: mục tiêu mặc định kéo 78 đơn vị, chuỗi thứ tự dài nhất 15 đơn vị, 41 đơn vị không phải chờ ai.](../../diagrams/sd-08-020-main.svg)

## Từ viết tắt

- **BIOS** (Basic Input/Output System) — hệ thống vào ra cơ bản: phần mềm nằm sẵn trên bo mạch, chạy đầu tiên khi bật máy để kiểm phần cứng và tìm thiết bị khởi động.
- **UEFI** (Unified Extensible Firmware Interface) — giao diện phần sụn mở rộng thống nhất: loại phần sụn mới hơn BIOS trên bo mạch, làm việc tương tự là khởi tạo phần cứng rồi giao cho bộ nạp khởi động.
- **POST** (Power On Self Test) — tự kiểm tra khi bật nguồn: bước phần sụn kiểm nhanh phần cứng trước khi đi tiếp.
- **GRUB** (GRand Unified Bootloader) — bộ nạp khởi động hợp nhất: chương trình hiện menu chọn hệ điều hành hoặc nhân rồi nạp nhân Linux vào bộ nhớ.
- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần cứng chạy từng lệnh của chương trình; ở bước 2 của nguồn nó là một trong các thiết bị được phát hiện.
- **RAM** (Random Access Memory) — bộ nhớ truy cập ngẫu nhiên: bộ nhớ chính của máy, mất nội dung khi tắt nguồn; nguồn kể nó cùng CPU và ổ lưu trữ trong các thiết bị được phát hiện.
- **EFI** (Extensible Firmware Interface) — giao diện phần sụn mở rộng: tên đời trước của UEFI, còn xuất hiện trong tài liệu systemd khi nói phần sụn nạp thẳng nhân.
- **OS** (Operating System) — hệ điều hành: phần mềm nền quản lý máy; ở đây là Linux.
- **PID** (Process IDentifier) — số nhận dạng tiến trình: số mà nhân đặt cho mỗi tiến trình đang chạy; tiến trình đầu tiên của người dùng có số 1.

## Đọc hình

| Bước của nguồn | Nguồn nói | Điều tài liệu độc lập nói |
|---|---|---|
| 1. Bật nguồn | Phần sụn BIOS hoặc UEFI được nạp từ bộ nhớ không mất điện và chạy POST | `boot(7)`: chương trình trong bộ nhớ chỉ đọc, thường gọi là BIOS, tự kiểm cơ bản rồi đọc tham số từ bộ nhớ không mất điện. `bootup(7)`: phần sụn chỉ khởi tạo phần cứng tối thiểu |
| 2. Phát hiện thiết bị | BIOS hoặc UEFI phát hiện CPU, RAM, ổ lưu trữ | Tài liệu đọc được không mô tả bước này riêng; chỉ nói phần sụn khởi tạo tối thiểu. Phần còn lại (dò nốt phần cứng) do hệ thống quản lý dịch vụ làm sau |
| 3. Chọn thiết bị khởi động | Ổ cứng, máy chủ mạng hoặc đĩa quang | `boot(7)`: danh sách thiết bị khởi động nằm trong bộ nhớ không mất điện; thiết bị nạp có thể ở qua mạng |
| 4. Bộ nạp khởi động | Phần sụn chạy GRUB, hiện menu chọn hệ điều hành hoặc nhân | `bootup(7)`: phần sụn giao quyền cho bộ nạp khởi động (như systemd-boot hoặc GRUB) trên ổ lưu trữ, bộ nạp gọi nhân; với phần sụn kiểu EFI, phần sụn cũng có thể nạp nhân trực tiếp. `boot(7)`: bộ nạp cho phép chọn nhân khác và truyền tham số cho nhân |
| (không có trong nguồn) | | `bootup(7)`: nhân có thể gắn một hệ thống tệp trong bộ nhớ (initramfs) để tìm hệ thống tệp gốc, rồi mới trao quyền cho hệ thống quản lý dịch vụ |
| 5. Nhân và tiến trình đầu tiên | Nhân sẵn sàng, systemd là tiến trình đầu tiên, dò nốt phần cứng, gắn hệ thống tệp, chạy môi trường đồ hoạ | `boot(7)`: nhân khởi tạo các thành phần, gắn hệ thống tệp gốc, rồi tạo tiến trình số 1, truyền thống chạy `/sbin/init`. `bootup(7)`: hệ thống quản lý dịch vụ (như systemd) nằm trên hệ thống tệp gốc chịu trách nhiệm dò nốt phần cứng, gắn các hệ thống tệp và chạy các dịch vụ |
| 6. default.target | systemd kích hoạt đơn vị mục tiêu mặc định | `bootup(7)`: systemd kích hoạt mọi đơn vị mà `default.target` phụ thuộc; thường nó là bí danh của `graphical.target` hoặc `multi-user.target`; việc khởi động chạy song song nên thứ tự đạt các mục tiêu không xác định |
| 7. Tập lệnh khởi động | Chạy một bộ tập lệnh khởi động, cấu hình môi trường | Với systemd, "tập lệnh" là các đơn vị dịch vụ; cách tập lệnh trong `/etc/init.d` là cách của Unix System V (`boot(7)`) |
| 8. Đăng nhập | Hiện cửa sổ đăng nhập | `bootup(7)`: `graphical.target` kéo thêm dịch vụ quản lý màn hình khi hệ thống cấu hình giao diện đồ hoạ |

## Thử: đọc tĩnh các tệp đơn vị systemd của một máy thật

Máy dùng để viết bài có systemd 255 cài sẵn, nhưng tiến trình số 1 của nó là chương trình khởi tạo riêng của máy ảo chứ không phải systemd (dù `/sbin/init` là một liên kết tới systemd), nên không thể đo thời gian khởi động thật. Cái làm được là đọc các tệp đơn vị trên đĩa: một chương trình Python nhỏ (khoảng sáu mươi dòng) theo các khai báo `Requires`, `Wants`, `BindsTo`, `Requisite` và các thư mục `.wants` và `.requires` từ `default.target` để đếm các đơn vị mà nó kéo theo, rồi đọc các khai báo `After` và `Before` để tính thứ tự.

| Phép tính trên máy này | Kết quả |
|---|---|
| `default.target` là | liên kết tới `graphical.target` |
| Số đơn vị `default.target` kéo theo (cả bắc cầu) | 78: 35 dịch vụ, 18 mục tiêu, 8 bộ hẹn giờ, 7 ổ cắm, 6 điểm gắn, 2 đường dẫn, 1 điểm gắn tự động, 1 lát |
| Số đơn vị tên được nhắc nhưng không có tệp | 11 |
| Số cạnh thứ tự (`After`, `Before`) trong tập đó | 94 |
| Chuỗi thứ tự dài nhất | 15 đơn vị |
| Số đơn vị không phải đợi đơn vị nào trong tập | 41 trên 78 |
| Số đơn vị `sysinit.target` kéo theo | 41 |

Chuỗi dài nhất đi qua `local-fs-pre.target`, `local-fs.target`, `systemd-tmpfiles-setup.service`, `sysinit.target`, `basic.target`, `multi-user.target`, `graphical.target`, và dừng ở `systemd-update-utmp-runlevel.service`. Hai điều đọc được. Một, `bootup(7)` nói quá trình khởi động chạy song song, và con số đồng ý: 78 đơn vị mà chuỗi tuần tự dài nhất chỉ 15, hơn nửa số đơn vị (41) không phải đợi gì. Hai, những gì nguồn gom thành "chạy các tập lệnh khởi động" thực ra là một đồ thị của vài chục đơn vị với hàng chục ràng buộc thứ tự, không phải một danh sách chạy lần lượt.

## Giới hạn cần nhớ

Phép đọc chỉ là đọc tệp khai báo: chương trình bỏ qua các điều kiện (`ConditionXxx`) và các đơn vị mẫu (`foo@.service`), nên một số đơn vị sẽ không chạy ở lần khởi động thật; ảnh máy đo cũng có thêm dịch vụ cài riêng (cơ sở dữ liệu, bộ nhớ đệm, bộ chứa), nên con số 78 là của ảnh này, không phải của Linux nói chung. Không có phép đo thời gian khởi động, vì tiến trình số 1 của máy đo không phải systemd và không có phần sụn thật để chạy POST hay bộ nạp khởi động. Đối chiếu bước 1 đến 4 chỉ ở mức mô tả của tài liệu; không đọc được trang chính thức của GRUB hay UEFI từ máy viết bài. Cách khởi động kiểu Unix System V (`/etc/inittab`, `/etc/init.d`) được `boot(7)` mô tả nhưng không được đo.

## Nhìn hình trả lời

Một người bạn nói "Linux bật lên thì BIOS chạy GRUB, GRUB chạy systemd". Trong hai bước ở giữa, chi tiết nào bị bỏ qua, và nếu máy không lên được vì không tìm thấy hệ thống tệp gốc thì lỗi nằm ở đoạn nào?

<details>
<summary>Xem đáp án</summary>

Bị bỏ qua là nhân và, thường là, `initramfs`: bộ nạp nạp nhân và hình ảnh initramfs vào bộ nhớ, nhân giải nó thành một hệ thống tệp trong bộ nhớ, và chính nó có nhiệm vụ tìm và gắn hệ thống tệp gốc rồi mới trao quyền cho systemd (`bootup(7)`). Nếu không tìm thấy hệ thống tệp gốc thì lỗi nằm ở đoạn giữa bộ nạp và systemd, tức là trong nhân và initramfs, trước khi tiến trình số 1 của hệ thống thật chạy; không phải ở bước chạy dịch vụ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và tám bước ngắn. Bài này giữ tám bước theo đúng thứ tự, thêm dòng `initramfs` mà nguồn thiếu, đối chiếu từng bước với tài liệu của Linux và systemd, và thêm một lần đọc tĩnh các tệp đơn vị của một máy thật.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/linux-boot-process-explained.md): tám bước.
- [Linux man-pages — boot(7)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man7/boot.7): phần cứng, bộ nạp, nhân, tiến trình số 1 và tập lệnh khởi động. Đọc từ bản sao cục bộ.
- [systemd — bootup(7)](https://github.com/systemd/systemd/blob/cb070c87eb12f3cf1f85873db38ff756a111460e/man/bootup.xml): phần sụn, bộ nạp, initramfs, hệ thống quản lý dịch vụ, `default.target`, khởi động song song. Đọc từ tệp tải về ngày 2026-10-19.
- [systemd — systemd.special(7)](https://github.com/systemd/systemd/blob/cb070c87eb12f3cf1f85873db38ff756a111460e/man/systemd.special.xml): các đơn vị mục tiêu quen thuộc. Đọc từ tệp tải về ngày 2026-10-19.

Đã đọc nguồn ngày 2026-10-19. Phép đọc tệp đơn vị là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

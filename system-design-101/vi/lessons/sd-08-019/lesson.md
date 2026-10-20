# Chương trình chạy thế nào: tám bước của nguồn và những gì xem được trên Linux

**Bài nguồn kể tám bước từ lúc người dùng nhấp đúp một chương trình tới lúc nó thoát. Bài này giữ đủ tám bước, đối chiếu với trang hướng dẫn của Linux (`execve`, `ld.so`, `_exit`) và dùng `strace` cùng vài chương trình C nhỏ để xem từng bước diễn ra thật thế nào trên một máy Linux; những chỗ nguồn nói theo kiểu Windows (DLL, `.NET`) thì ghi rõ là không đo.**

![Ba khung. Khung một, tám bước của nguồn từ lúc nhấp đúp tới lúc thoát: nhấp đúp, nạp tệp chạy, nạp thư viện chung, cấp bộ nhớ, khởi tạo môi trường chạy, vào hàm main, CPU chạy lệnh nằm trong bộ nhớ, dọn dẹp khi thoát. Khung hai, đo trên Linux: một chương trình C nhỏ gọi hệ thống 35 lần với thư viện động và 17 lần khi nối tĩnh; khởi động mất 1,0 đến 1,4 mili giây, còn Python 16,7 đến 21,4 và Java 41 đến 45; ánh xạ 1 GiB bộ nhớ chỉ thêm 380 KiB bộ nhớ thật cho đến khi đọc tới; mã của một hàm đọc được như dữ liệu; thoát không đóng tệp thì nhân đóng hộ. Khung ba, chưa đo: Windows, DLL và môi trường chạy của Microsoft.](../../diagrams/sd-08-019-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần cứng chạy từng lệnh của chương trình; nguồn nói nó chạy lệnh nằm trong bộ nhớ.
- **GUI** (Graphical User Interface) — giao diện đồ hoạ: cửa sổ và biểu tượng mà người dùng nhấp vào; ở bài này không đo, vì phép thử chạy từ dòng lệnh.
- **OS** (Operating System) — hệ điều hành: phần mềm nền quản lý tệp, bộ nhớ và các chương trình đang chạy; ở bài này là Linux.
- **DLL** (Dynamic-Link Library) — thư viện liên kết động: tên Windows của tệp thư viện chung nạp lúc chạy; trên Linux tệp tương ứng có đuôi `.so`.
- **JVM** (Java Virtual Machine) — máy ảo Java: môi trường chạy mà nguồn lấy làm ví dụ; trong bài này chỉ đo thời gian khởi động.
- **ELF** (Executable and Linkable Format) — định dạng tệp chạy và tệp liên kết: cách tệp chương trình trên Linux ghi mã, dữ liệu và các thư viện cần nạp.
- **KiB** (Kibibyte) — kibibyte: 1.024 byte, đơn vị mà các trang thông tin bộ nhớ của Linux dùng.
- **GiB** (Gibibyte) — gibibyte: 1.024 x 1.024 x 1.024 byte, tức hơn một tỷ byte.

## Đọc hình

| Bước của nguồn | Nguồn nói | Điều xem được trên Linux |
|---|---|---|
| Nhấp đúp | Người dùng bảo hệ điều hành mở chương trình qua giao diện đồ hoạ | Phép thử chạy từ dòng lệnh; chưa đo giao diện đồ hoạ |
| Nạp tệp chạy | Hệ điều hành lấy tệp qua hệ thống tệp, nạp vào bộ nhớ | `execve` thay chương trình đang chạy bằng chương trình mới, với ngăn xếp, vùng nhớ động và vùng dữ liệu mới |
| Nạp thư viện chung | Ứng dụng hiện đại dùng nhiều thư viện chung như DLL | Trên Linux, `ld.so` tìm và nạp các tệp `.so` cần thiết; `strace` thấy mở `/etc/ld.so.cache` và `libc.so.6` rồi ánh xạ chúng vào bộ nhớ |
| Cấp bộ nhớ | Hệ điều hành cấp vùng nhớ | Cấp theo lời gọi `brk` và `mmap`; vùng nhớ chỉ thành bộ nhớ thật khi được chạm tới |
| Khởi tạo môi trường chạy | JVM hoặc `.NET` khởi tạo tài nguyên | Đo thời gian khởi động của C, Python, Node và Java |
| Gọi hệ thống và vào main | Hàm `main` được gọi để chạy mã của lập trình viên | `strace` thấy hàng chục lời gọi hệ thống trước khi tới lời gọi `write` đầu tiên của chương trình |
| Kiến trúc Von Neumann | CPU chạy lệnh lưu trong bộ nhớ | Mã nằm trong vùng bộ nhớ `r-xp` mà chương trình đọc được như dữ liệu |
| Thoát | Dọn dẹp: đóng tệp, giải phóng tài nguyên mạng, trả bộ nhớ | `exit_group` kết thúc tiến trình; nhân đóng mọi tệp còn mở |

## Thử: xem từng bước bằng `strace` và vài chương trình nhỏ

Ngày 2026-10-19, Linux trên máy 4 lõi ảo, gcc 13.3, Python 3.13.16, Node 22, Java của máy; các phép đo lặp ba lần, và mọi con số nằm trong khoảng giữa các lần chạy.

**Nạp tệp chạy và thư viện.** Chương trình C chỉ in "hello", biên dịch hai kiểu. Kiểu động (mặc định) dùng thư viện chung `libc.so.6`; kiểu tĩnh (`-static`) chép thư viện vào trong tệp.

| Phép đo | Nối động | Nối tĩnh |
|---|---|---|
| Số lời gọi hệ thống (`strace -c`) | 35 | 17 |
| Lỗi trang nhẹ (minor page fault) | 61 đến 62 | 31 đến 33 |
| Khởi động tới khi thoát, đo từ tiến trình cha | 1,10 đến 1,40 ms | 1,03 đến 1,16 ms |

Trong 35 lời gọi của kiểu động có phần việc của trình nạp: mở `/etc/ld.so.cache`, mở `libc.so.6`, ánh xạ nó nhiều lần với quyền khác nhau (chỉ đọc, đọc và chạy, đọc và ghi), rồi thiết lập vùng nhớ cục bộ của luồng, đổi quyền vài vùng. Kiểu tĩnh không có phần này và chỉ còn việc khởi tạo của chính nó. Chênh lệch khởi động nhỏ (chừng 0,1 đến 0,3 ms), vì thư viện chung đã nằm sẵn trong bộ nhớ của hệ điều hành và chỉ cần ánh xạ.

**Bộ nhớ cấp theo kiểu lười.** Một chương trình ánh xạ tệp 1 GiB vào bộ nhớ rồi đọc dần (`VmSize` là phần địa chỉ đã cấp, `VmRSS` là phần đang nằm thật trong bộ nhớ):

| Thời điểm | `VmSize` | `VmRSS` |
|---|---|---|
| trước khi ánh xạ | 2.700 KiB | 1.416 KiB |
| sau khi ánh xạ 1 GiB | 1.051.276 KiB | 1.796 KiB |
| sau khi đọc một byte | không đổi | 1.856 KiB |
| sau khi đọc một byte mỗi 4 KiB, nửa đầu tệp | không đổi | 526.084 KiB |

Cấp một gibibyte địa chỉ chỉ làm bộ nhớ thật tăng 380 KiB; bộ nhớ thật chỉ được nạp quanh vùng chương trình chạm tới, theo nhu cầu (đọc một byte kéo thêm khoảng 60 KiB, vì nhân đọc trước và nạp luôn các trang lân cận, nên không đúng từng trang một). Đây là điều phía sau câu "hệ điều hành cấp bộ nhớ" của nguồn: cấp địa chỉ rẻ, cấp bộ nhớ thật dần theo vùng được dùng.

**Môi trường chạy.** Thời gian từ lúc tiến trình cha khởi động tới lúc con thoát, với chương trình không làm gì:

| Chương trình | Trung vị | Lỗi trang nhẹ |
|---|---|---|
| C (nối động) | 1,1 đến 1,4 ms | 61 đến 62 |
| Python (`-c pass`) | 16,7 đến 21,4 ms | 838 đến 840 |
| Python bỏ qua mô-đun `site` và biến môi trường (`-S -E`) | 10,2 đến 12,5 ms | không đo |
| Node 22 (`-e 0`) | 25,1 đến 27,5 ms | không đo |
| Java (một lớp in "hello") | 41,4 đến 45,0 ms | không đo |

Bước "khởi tạo môi trường chạy" của nguồn có cái giá đo được: một chương trình trống mất cỡ 10 đến 40 lần thời gian của chương trình C, vì trình thông dịch hoặc máy ảo phải nạp và khởi tạo trước khi chạy mã của bạn.

**Mã cũng là dữ liệu trong bộ nhớ.** Một chương trình C đọc 8 byte đầu của hàm `add` như đọc mảng và in `f3 0f 1e fa 55 48 89 e5`: đó là các lệnh máy của hàm, nằm trong một vùng ánh xạ có quyền đọc và chạy (`r-xp`) trong `/proc/self/maps`, cạnh vùng dữ liệu `rw-p`, vùng nhớ động `[heap]` và `[stack]`. Cùng bộ nhớ chứa cả lệnh lẫn dữ liệu, như mô tả Von Neumann của nguồn; điều bổ sung là hệ điều hành đặt quyền riêng cho từng vùng.

**Thoát và dọn dẹp.** Một chương trình mở 500 lần tệp `/etc/hostname` rồi thoát mà không đóng: `strace -c` đếm 502 lời gọi `openat` và chỉ 2 lời gọi `close` (của trình nạp), và sau khi chạy 200 lần, con số tệp mở của cả hệ thống (`/proc/sys/fs/file-nr`) vẫn là 127 như trước. Trang hướng dẫn `_exit` nói đúng điều này: mọi tệp còn mở của tiến trình đều được đóng. Một việc dọn dẹp khác thuộc về thư viện chứ không phải nhân: chương trình in "buffered text" không xuống dòng rồi gọi `_exit(0)` thì không in ra gì khi đầu ra là một đường ống, còn gọi `exit(0)` thì in đủ, vì `exit` xả các bộ đệm của thư viện chuẩn trước khi thoát.

## Giới hạn cần nhớ

Mọi phép đo chạy trên một máy Linux, một thư viện C và một vài trình thông dịch; bài nguồn nói theo Windows (DLL, `.NET`) nên phần đó chỉ được đối chiếu ở mức tương ứng, không đo. `strace` làm chậm tiến trình, nên số lời gọi hệ thống là số đếm chứ không phải thời gian; thời gian khởi động đo từ tiến trình cha, gồm cả việc tạo tiến trình con (cỡ một mili giây), nên con số của chương trình C là cận trên của việc khởi động thật. Việc nhấp đúp bằng giao diện đồ hoạ, việc dọn tài nguyên mạng khi thoát và việc hệ điều hành nạp tệp qua hệ thống tệp ở mức đĩa không được đo. Số lần ánh xạ và thứ tự lời gọi phụ thuộc phiên bản `libc` và trình nạp.

## Nhìn hình trả lời

Một chương trình C chỉ in một dòng, nhưng `strace` cho thấy 35 lời gọi hệ thống, và bản biên dịch nối tĩnh chỉ có 17. Chênh lệch này nằm ở bước nào của nguồn, và vì sao bản nối động vẫn là mặc định?

<details>
<summary>Xem đáp án</summary>

Nằm ở bước "nạp thư viện chung": với bản động, trình nạp phải mở danh sách thư viện, mở `libc.so.6`, ánh xạ nó vào bộ nhớ và đổi quyền các vùng, trước khi tới `main`. Bản tĩnh đã chứa sẵn thư viện nên bỏ qua. Bản động vẫn là mặc định vì thư viện chung chỉ nằm một bản trên đĩa, được cập nhật riêng, và các trang chỉ đọc của nó (như mã) có thể dùng chung trong bộ nhớ giữa các tiến trình (phần ghi được, phần sửa lúc nạp và trạng thái của trình nạp vẫn riêng cho từng tiến trình); cái giá mỗi lần khởi động chỉ cỡ 0,1 đến 0,3 ms trong phép đo ở đây.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và tám đoạn ngắn theo kiểu chung chung. Bài này giữ tám bước theo đúng thứ tự, thêm cột "điều xem được trên Linux" và biến phần lớn các bước thành phép đo hoặc phép quan sát có thể lặp lại; phần Windows ghi rõ là không đo.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-computer-programs-run.md): tám bước.
- [Linux man-pages — execve(2)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man2/execve.2): thay chương trình đang chạy bằng chương trình mới, với ngăn xếp, vùng nhớ động và vùng dữ liệu mới. Đọc từ bản sao cục bộ.
- [Linux man-pages — ld.so(8)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man8/ld.so.8): trình nạp tìm và nạp các thư viện chung; mặc định trì hoãn việc phân giải hàm tới lần dùng đầu tiên. Đọc từ bản sao cục bộ.
- [Linux man-pages — _exit(2)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man2/_exit.2): mọi tệp còn mở của tiến trình được đóng khi thoát. Đọc từ bản sao cục bộ.
- [Linux man-pages — exit(3)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man3/exit.3): xả và đóng các luồng của thư viện chuẩn khi thoát. Đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

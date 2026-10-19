# Giao tiếp giữa các tiến trình trên Linux

**Hai tiến trình trên cùng một máy muốn trao đổi dữ liệu thì phải nhờ nhân hệ điều hành mở đường, và Linux có năm đường quen thuộc: ống dẫn, hàng đợi thông điệp, tín hiệu, semaphore và bộ nhớ chia sẻ.**
Bài này nói mỗi đường dùng để làm gì, rồi đo thử: cái khiến một lần trao đổi chậm thường không phải là cách chọn mà là việc đánh thức tiến trình đang ngủ.

![Hai khung. Khung một, năm cách: ống dẫn là dòng byte một chiều; hàng đợi thông điệp giữ từng thông điệp có độ ưu tiên; tín hiệu chỉ báo một sự kiện, không mang dữ liệu; semaphore là một con số để chờ và báo; bộ nhớ chia sẻ là vùng nhớ cả hai cùng thấy. Khung hai, thử 100.000 vòng đi về một byte giữa hai tiến trình: hai tiến trình ở hai lõi mất khoảng 23 đến 33 micro giây mỗi vòng với ống dẫn, socket, hàng đợi, semaphore và tín hiệu; bộ nhớ chia sẻ mà bên kia liên tục nhìn vào một cờ chỉ mất 0,4 micro giây. Khi hai tiến trình chung một lõi thì mọi cách chỉ mất 1,5 đến 5,6 micro giây.](../../diagrams/sd-08-001-main.svg)

## Từ viết tắt

- **IPC** (Inter-Process Communication) — giao tiếp giữa các tiến trình: mọi cách để hai chương trình đang chạy riêng rẽ trao đổi dữ liệu hoặc báo hiệu cho nhau.
- **POSIX** (Portable Operating System Interface X) — chuẩn giao diện cho hệ điều hành kiểu Unix (chữ X gợi nhớ Unix): bộ quy ước chung cho hệ điều hành kiểu Unix, trong đó có hàng đợi thông điệp, semaphore và bộ nhớ chia sẻ mà bài nhắc tới.
- **FIFO** (First In, First Out) — vào trước ra trước: ở bài này là ống dẫn có tên, đứng trong hệ tệp để các tiến trình không cùng họ cũng mở được.
- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: bài gọi mỗi đơn vị xử lý độc lập của nó là một lõi.
- **SIGINT** (SIGnal INTerrupt) — tín hiệu ngắt: tín hiệu nhân gửi cho tiến trình khi người dùng bấm Ctrl+C.

## Đọc hình

**1 · Ống dẫn (pipe).** Một dòng byte một chiều: một đầu ghi, một đầu đọc, byte vào trước thì ra trước. Đọc ống rỗng thì chờ; ghi vào ống đầy thì chờ. Từ Linux 2.6.11 ống chứa được 16 trang bộ nhớ, tức 65.536 byte với trang 4.096 byte. Một lần ghi không quá `PIPE_BUF` byte (4.096 trên Linux) được bảo đảm liền khối, không bị trộn với dữ liệu của tiến trình khác; ghi lớn hơn thì có thể bị trộn. Ghi vào ống không còn ai đọc thì nhận `SIGPIPE`, tín hiệu báo ống đã hỏng. Ống thường nối các tiến trình có họ hàng (cha và con); muốn nối hai tiến trình xa lạ thì dùng ống có tên (FIFO), cùng cách hoạt động nhưng có tên trong hệ tệp.

**2 · Hàng đợi thông điệp (POSIX message queue).** Khác ống, nó giữ từng thông điệp có ranh giới rõ ràng chứ không phải dòng byte, và mỗi thông điệp có độ ưu tiên: thông điệp ưu tiên cao luôn được giao trước. Hàng có giới hạn số thông điệp và cỡ thông điệp (trên máy thử: 10 thông điệp, mỗi thông điệp tối đa 8.192 byte).

**3 · Tín hiệu (signal).** Cách cổ nhất: nhân hoặc một tiến trình khác gõ cửa để báo một sự kiện. Bấm Ctrl+C là nhân gửi `SIGINT`, và hành động mặc định là kết thúc tiến trình. Tín hiệu chuẩn chỉ cho biết "sự kiện này đã xảy ra", không chở dữ liệu của ứng dụng, và **không xếp hàng**: nếu nhiều lần cùng một tín hiệu đến lúc nó đang bị chặn thì khi gỡ chặn chỉ giao một lần.

**4 · Semaphore.** Một con số nguyên không bao giờ xuống dưới 0, với hai thao tác: tăng một (`sem_post`) và giảm một (`sem_wait`); nếu số đang là 0 thì `sem_wait` chờ cho tới khi có ai tăng. Nó không chở dữ liệu, chỉ để phối hợp ("tôi xong rồi", "tới lượt bạn"), nên thường đi cùng bộ nhớ chia sẻ.

**5 · Bộ nhớ chia sẻ (shared memory).** Một vùng nhớ mà cả hai tiến trình cùng thấy trong không gian địa chỉ của mình: tạo bằng `shm_open`, đặt cỡ bằng `ftruncate`, gắn vào tiến trình bằng `mmap`. Sau khi gắn xong, đọc và ghi là truy cập bộ nhớ bình thường, không phải gọi vào nhân cho từng lần. Đổi lại, nhân không giữ trật tự hộ: hai bên tự phải thống nhất ai được ghi lúc nào.

## Thử: đo một vòng đi về

Ngày 2026-10-19, trên một máy ảo 4 lõi Intel Xeon 2,1 GHz, nhân Linux 6.18.44. Một chương trình C nhỏ cho tiến trình cha gửi một byte (hoặc một thông điệp một byte, hoặc một tín hiệu) sang tiến trình con, con trả lại ngay, và lặp 100.000 vòng; số liệu là thời gian trung bình của một vòng đi về. Mỗi cách được đo 3 lần khi hai tiến trình ghim ở hai lõi khác nhau và 4 lần khi ghim cùng một lõi. Ống dẫn cần hai ống (mỗi chiều một ống); semaphore đi cùng một vùng nhớ chia sẻ và hai semaphore; dòng cuối không dùng nhân để chờ: hai bên liên tục nhìn vào một cờ trong bộ nhớ chia sẻ.

| Cách | Hai lõi (µs mỗi vòng) | Cùng một lõi (µs mỗi vòng) |
|---|---|---|
| Ống dẫn | 24 đến 27 | 2,7 đến 3,2 |
| Socket Unix | 26 đến 33 | 4,7 đến 5,6 |
| Hàng đợi thông điệp | 24 đến 27 | 2,7 đến 3,2 |
| Bộ nhớ chia sẻ và semaphore | 23 đến 24 | 2,3 đến 2,9 |
| Tín hiệu | 25 đến 26 | 2,9 đến 3,9 |
| Bộ nhớ chia sẻ, nhìn cờ liên tục | 0,4 | 1,5 đến 2,0 |

Hai điều đọc được. Một, khi hai tiến trình ở hai lõi khác nhau, bốn cách chờ bằng cách ngủ (ống, hàng đợi, semaphore, tín hiệu) đều mất cỡ 25 µs, gần như bằng nhau: thứ chiếm thời gian là việc đánh thức một tiến trình đang ngủ trên lõi khác, không phải cấu trúc dữ liệu của từng cách. Hai, khi hai tiến trình chung một lõi thì cả bốn rẻ hơn khoảng tám lần (không còn phải đánh thức một lõi khác). Cách duy nhất rẻ hơn hẳn là không ngủ: nhìn cờ liên tục chỉ mất 0,4 µs, nhưng cái giá là hai lõi chạy hết công suất để chờ nhau. Tương tự, thử gửi 5 lần `SIGUSR1` khi tín hiệu đang bị chặn thì sau khi gỡ chặn bộ xử lý tín hiệu chạy 1 lần, còn 5 lần ghi một byte vào ống thì đọc lại được đủ 5 byte.

## Giới hạn cần nhớ

Cả năm cách chỉ nối các tiến trình trên cùng một máy; qua mạng phải dùng cách khác. Ống dẫn một chiều, nên trao đổi hai chiều cần hai ống (như phép thử) hoặc một cách hai chiều khác. Tín hiệu không xếp hàng và không chở dữ liệu, nên không dùng để đếm sự kiện hay gửi nội dung. Semaphore và bộ nhớ chia sẻ không tự bảo vệ dữ liệu: bộ nhớ chia sẻ mà không có cách phối hợp (như semaphore) thì hai bên ghi chồng lên nhau được. Phép thử chỉ đo thông điệp một byte trên một máy ảo, tức đo độ trễ của một lần đánh thức, không đo thông lượng khi chuyển khối dữ liệu lớn và cũng không đo các semaphore System V hay hàng đợi System V; con số trên máy thật sẽ khác, nên đừng dùng chúng làm bảng giá mà chỉ dùng để thấy cái gì chiếm thời gian.

## Nhìn hình trả lời

Tiến trình A cần gửi cho tiến trình B hàng nghìn bản ghi nhật ký mỗi giây, mỗi bản khoảng 100 byte, và B phải nhận đủ theo đúng thứ tự gửi. Chọn cách nào trong năm cách, và vì sao không chọn tín hiệu?

<details>
<summary>Xem đáp án</summary>

Ống dẫn (hoặc ống có tên nếu A và B không cùng họ): byte vào trước ra trước nên thứ tự được giữ, và nếu B chậm thì ống đầy khiến A phải chờ thay vì mất dữ liệu. Nếu mỗi bản ghi cần ranh giới rõ hoặc độ ưu tiên thì hàng đợi thông điệp hợp hơn. Tín hiệu không hợp vì nó không chở dữ liệu và không xếp hàng: gửi nhiều tín hiệu liên tiếp khi B chưa kịp nhận có thể gộp thành một, nên B không đếm được đã có bao nhiêu bản ghi.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê năm cách và mô tả mỗi cách bằng một hai câu. Bài này giữ năm cách đó, thêm chi tiết lấy từ trang hướng dẫn của Linux (dung lượng ống, `PIPE_BUF`, độ ưu tiên của hàng đợi, tín hiệu không xếp hàng), và thêm phép đo để thấy chi phí nằm ở đâu. Bài nguồn gọi semaphore là một vị trí trong bộ nhớ có thể kiểm tra và đặt bởi nhiều tiến trình; bài này theo trang hướng dẫn POSIX, mô tả nó là một số nguyên không âm với hai thao tác tăng và giảm.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-processes-talk-to-each-other-on-linux.md): năm cách giao tiếp giữa các tiến trình.
- [Linux man-pages — pipe(7)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man7/pipe.7): ống và ống có tên, dung lượng, `PIPE_BUF`. Đọc từ bản clone của kho (phiên bản 5.14).
- [Linux man-pages — mq_overview(7)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man7/mq_overview.7): hàng đợi thông điệp POSIX, độ ưu tiên, các giới hạn trong `/proc/sys/fs/mqueue`.
- [Linux man-pages — signal(7)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man7/signal.7): `SIGINT`, `SIGPIPE`, tín hiệu chuẩn không xếp hàng.
- [Linux man-pages — sem_overview(7)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man7/sem_overview.7): semaphore POSIX.
- [Linux man-pages — shm_overview(7)](https://github.com/mkerrisk/man-pages/blob/ae6b221882ce71ba82fcdbe02419a225111502f0/man7/shm_overview.7): bộ nhớ chia sẻ POSIX: `shm_open`, `ftruncate`, `mmap`.

Đã đọc nguồn ngày 2026-10-19. Phép đo là của người biên soạn, chạy trên một máy ảo, chưa lặp lại trên máy thật.
Bài viết và hình được thiết kế độc lập.

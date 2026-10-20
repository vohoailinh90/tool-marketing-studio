# Các tầng bộ nhớ, đo trên một máy: thanh ghi, bộ đệm, bộ nhớ chính, đĩa, mạng

**Bảng "các loại bộ nhớ" nào cũng nói tầng dưới chậm hơn tầng trên. Điều đáng nhớ là chậm hơn bao nhiêu lần, và con số đó chỉ có được khi đo.**
Bài này đo một lần đọc ở từng tầng trên chính máy dùng để biên soạn, từ một phép cộng trong bộ xử lý tới một yêu cầu qua mạng.

![Ba khung, số đo trên máy biên soạn. Khung một, trong bộ xử lý và bộ nhớ: một phép cộng trên thanh ghi 0,4 ns; đọc ngẫu nhiên trong 16 KiB, vừa bộ đệm L1, 1,5 ns; trong 256 KiB, vừa bộ đệm L2, 4,4 ns; từ 4 MiB trở lên khoảng 150 ns, gần bằng bộ nhớ chính; trong 1 GiB 326 ns. Khung hai, ra ngoài: đọc ngẫu nhiên 4 KiB từ ổ đĩa ảo trung bình 72 µs; một yêu cầu HTTPS tới GitHub khoảng 60 ms, chưa kể việc mở kết nối. Khung ba, đọc con số: một lần đọc đĩa bằng khoảng 200 lần đọc bộ nhớ chính; một yêu cầu qua mạng bằng hơn 100.000 lần; máy báo bộ đệm L3 33 MiB nhưng từ 4 MiB đã mất khoảng 150 ns; dùng trang lớn 2 MiB, đọc trong 1 GiB còn 225 ns.](../../diagrams/sd-04-023-main.svg)

## Từ viết tắt

- **KiB** (Kibibyte) — kibibyte: 1.024 byte.
- **MiB** (Mebibyte) — mebibyte: 1.048.576 byte.
- **GiB** (Gibibyte) — gibibyte: 1.073.741.824 byte.
- **RAM** (Random Access Memory) — bộ nhớ truy cập ngẫu nhiên: bộ nhớ chính của máy, nơi chương trình đang chạy để dữ liệu; mất nội dung khi tắt máy.
- **SSD** (Solid-State Drive) — ổ thể rắn: ổ lưu trữ dùng chip nhớ, không có bộ phận quay.
- **HDD** (Hard Disk Drive) — ổ đĩa cứng: ổ lưu trữ có đĩa từ quay và đầu đọc di chuyển.
- **TLB** (Translation Lookaside Buffer) — bộ đệm dịch địa chỉ: nơi bộ xử lý nhớ sẵn các cặp địa chỉ ảo và địa chỉ thật vừa dùng, để khỏi tra bảng trang mỗi lần đọc.
- **HTTPS** (HyperText Transfer Protocol Secure) — giao thức truyền siêu văn bản có mã hóa, dùng cho yêu cầu tới GitHub trong thử nghiệm.

## Đọc hình

**Khung 1 · Trong bộ xử lý và bộ nhớ.** Nhân Linux cho biết cỡ các bộ đệm qua các tệp trong thư mục `cache` của từng nhân, dưới `/sys`: trên máy này, bộ đệm dữ liệu L1 là 32 KiB, L2 là 1 MiB, L3 là 33 MiB, mỗi dòng bộ đệm 64 byte.

Để đo thời gian của một lần đọc, chương trình C dựng một chuỗi con trỏ đi qua mọi dòng 64 byte của một vùng nhớ theo thứ tự ngẫu nhiên, rồi đi theo chuỗi đó. Mỗi lần đọc phải chờ lần đọc trước trả về địa chỉ kế tiếp, nên tổng thời gian chia cho số bước là thời gian của một lần đọc, không phải băng thông. Vùng nhớ càng lớn thì càng ít phần nằm vừa trong bộ đệm.

| Vùng nhớ đi qua | Một lần đọc |
|---|---|
| 16 KiB (vừa L1) | 1,5 đến 1,7 ns |
| 256 KiB (vừa L2) | 4,4 đến 5,0 ns |
| 1 MiB | 15 đến 17 ns |
| 4 MiB | 145 đến 152 ns |
| 64 MiB | 165 đến 180 ns |
| 1 GiB | 326 đến 409 ns |

Một phép cộng mà phép sau phải chờ kết quả phép trước mất 0,4 ns: đó là tốc độ của dữ liệu đã nằm sẵn trong thanh ghi.

**Khung 2 · Ra ngoài: đĩa và mạng.**

- **Ổ đĩa ảo.** 3.000 lần đọc 4 KiB ở vị trí ngẫu nhiên trong một tệp 2 GiB, mở với `O_DIRECT` để đi thẳng xuống ổ, không qua bộ nhớ đệm của hệ điều hành: trung bình 72 µs một lần, lần chậm nhất 2,1 ms. Nhân báo ổ này là loại quay (tệp `queue/rotational` bằng 1), nhưng đây là ổ ảo của máy ảo; từ bên trong, không biết được ổ thật bên dưới là SSD hay HDD.
- **Qua mạng.** Mười yêu cầu HTTPS tới GitHub qua proxy của môi trường: sau khi bắt tay mã hóa xong, chờ byte đầu tiên mất khoảng 60 ms (trung vị); tính cả việc mở kết nối thì mỗi yêu cầu mất trung vị 0,27 s.

**Khung 3 · Đọc con số.**

- Một lần đọc đĩa ngẫu nhiên (72 µs) bằng khoảng 200 lần đọc bộ nhớ chính (326 đến 409 ns). Một yêu cầu qua mạng (60 ms) bằng hơn 100.000 lần.
- Máy báo có L3 33 MiB, nhưng từ 4 MiB trở lên mỗi lần đọc đã mất khoảng 150 ns, gần bằng đọc bộ nhớ chính. Thử nghiệm không thấy bậc L3; máy ảo dùng chung bộ xử lý với máy khác, và bài không xác định được nguyên nhân chắc chắn.
- Đi qua 1 GiB tốn hơn đi qua 64 MiB một phần vì dịch địa chỉ. Tài liệu của nhân Linux về trang lớn trong suốt giải thích: dùng trang 2 MiB thì mỗi mục TLB phủ được nhiều bộ nhớ hơn nên ít lần trượt TLB hơn, và mỗi lần trượt cũng xử lý nhanh hơn, nhất là trên máy ảo. Trong một cặp lần chạy liền nhau, xin trang lớn cho vùng 1 GiB làm một lần đọc còn 225 ns thay vì 326 ns.

## Giới hạn cần nhớ

- Một máy ảo, bốn nhân, dùng chung phần cứng; chạy lại thì số đo lệch khoảng một phần mười. Con số đúng cho máy này, không phải hằng số của "bộ nhớ chính" hay "ổ đĩa".
- Thanh ghi không đo trực tiếp được bằng cách này; 0,4 ns là thời gian một phép cộng nối tiếp.
- Ổ đĩa ở đây là ổ ảo; mạng đi qua proxy. Không đo được SSD hay HDD thật, cũng không đo kho lưu trữ từ xa dùng để sao lưu.

## Nhìn hình trả lời

Một đoạn mã lấy 1.000 đơn hàng bằng cách gọi cơ sở dữ liệu ở máy khác 1.000 lần, mỗi lần một đơn. Nhìn khung 2 và khung 3: thời gian chờ mạng khoảng bao nhiêu, và đổi cách gọi thế nào?

<details>
<summary>Xem đáp án</summary>

Nếu mỗi lần gọi tốn khoảng một lượt hỏi đáp qua mạng như trong thử nghiệm (60 ms), 1.000 lần là khoảng 60 giây chỉ để chờ mạng, trong khi xử lý 1.000 dòng trong bộ nhớ chỉ tốn cỡ micro giây. Gom thành một truy vấn lấy cả 1.000 đơn thì chỉ chờ một lượt.
Con số 60 ms là của môi trường biên soạn, qua proxy tới GitHub; giữa hai máy trong cùng một mạng nội bộ nó sẽ khác, nên hãy đo trên hệ thống của bạn trước khi tính.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn kể sáu loại: thanh ghi, bộ đệm, RAM, SSD, HDD và kho lưu trữ từ xa, mỗi loại một câu mô tả. Bài này đo thay vì mô tả, nên gộp SSD và HDD thành "ổ đĩa" (máy ảo không cho biết ổ thật) và lấy một yêu cầu HTTPS làm đại diện cho "qua mạng".
Thử nghiệm thêm hai điều bài nguồn không có: bộ đệm báo trên giấy có thể không hiện ra trong số đo, và thời gian đọc bộ nhớ chính còn phụ thuộc vào việc dịch địa chỉ.
Bài về các loại bộ nhớ và lưu trữ trong cùng nhóm đo theo cùng cách trên một máy ảo khác và giải nghĩa tên các loại bộ nhớ, ổ lưu trữ mà nguồn của nó nêu; bài này thêm tầng thanh ghi, tầng mạng và ảnh hưởng của việc dịch địa chỉ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/types-of-memory.md): sáu loại bộ nhớ.
- Tài liệu của nhân Linux, bản v6.18, đọc từ bản clone của kho: [thuộc tính bộ đệm trong sysfs](https://github.com/torvalds/linux/blob/7d0a66e4bb9081d75c82ec4957c50034cb0ea449/Documentation/ABI/testing/sysfs-devices-system-cpu), [tệp `queue/rotational` của thiết bị khối](https://github.com/torvalds/linux/blob/7d0a66e4bb9081d75c82ec4957c50034cb0ea449/Documentation/ABI/stable/sysfs-block), [trang lớn trong suốt và TLB](https://github.com/torvalds/linux/blob/7d0a66e4bb9081d75c82ec4957c50034cb0ea449/Documentation/admin-guide/mm/transhuge.rst).

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 trên một máy ảo bốn nhân (Intel Xeon 2,8 GHz, nhân Linux 6.18), chương trình C biên dịch bằng gcc 13.3 với `-O2`, và `curl` cho yêu cầu mạng.
Bài viết và hình được thiết kế độc lập.

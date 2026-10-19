# Mã xóa: chịu mất khối mà không phải nhân ba dữ liệu

**Muốn dữ liệu sống sót khi hai ổ đĩa hỏng cùng lúc, cách đơn giản là giữ ba bản, tốn gấp ba chỗ.**
Mã xóa (erasure coding) cắt dữ liệu thành k khối, tính thêm m khối mã, và chỉ cần k khối bất kỳ trong k + m khối là dựng lại được. Với 4 + 2, vẫn chịu mất hai khối mà chỉ tốn gấp 1,5 lần.

![Ba khung. Khung một là bốn bước của mã xóa 4+2: cắt đối tượng 4 MiB thành 4 khối dữ liệu 1 MiB; tính thêm 2 khối mã và đặt 6 khối ở 6 nơi khác nhau; mất 2 khối bất kỳ vẫn dựng lại đủ, đúng ở cả 15 cách mất 2 trong 6 khối; mất 3 khối thì chỉ còn 3, không đủ để dựng lại. Khung hai so ba cách giữ an toàn cho 4 MiB: nhân bản 3 bản lưu 12 MiB và chịu mất 2 bản; mã xóa 4+2 lưu 6 MiB và chịu mất 2 khối; một khối chẵn lẻ 4+1 lưu 5 MiB và chỉ chịu mất 1 khối. Khung ba là cái giá: phục hồi phải đọc các khối còn lại, dựng lại rồi ghi khối mới; Ceph khuyên không dùng một khối mã cho dữ liệu thật; các khối phải nằm ở những nơi hỏng độc lập với nhau.](../../diagrams/sd-04-013-main.svg)

## Từ viết tắt

- **MiB** (Mebibyte) — mebibyte: đơn vị dung lượng bằng 1.048.576 byte; đối tượng thử có cỡ 4 MiB.
- **RAID** (Redundant Array of Independent Disks) — dãy ổ đĩa dư thừa: cách ghép nhiều ổ đĩa; RAID-5 dùng một khối chẵn lẻ để chịu mất một ổ.

## Đọc hình

**Khung 1 · Mã xóa 4 + 2.** Tài liệu Ceph gọi k khối đầu là khối dữ liệu, m khối sau là khối mã, và m chính là số nơi lưu có thể mất cùng lúc mà không mất dữ liệu. Sáu khối phải nằm ở sáu nơi hỏng độc lập (sáu ổ, sáu máy hay sáu giá máy), không thì một sự cố lấy đi nhiều khối một lúc.

**Khung 2 · So ba cách.** Tài liệu Ceph tính hệ số chiếm chỗ của mã xóa là (k + m) / k: 1,5 với 4 + 2, so với 3,0 khi giữ ba bản. Một khối chẵn lẻ (như RAID-5) rẻ hơn nữa nhưng chỉ chịu mất một khối: lấy phép hoặc loại trừ (`xor`) từng bit của mọi khối dữ liệu, hai bit khác nhau cho 1, giống nhau cho 0.

## Thử nghiệm: mất khối nào cũng dựng lại được

Thư viện zfec cài một mã xóa (README của nó so với RAID-5 nhưng cho chọn trước số khối được phép mất). Một đối tượng 4 MiB ngẫu nhiên, k = 4, m = 2:

| Phép thử | Kết quả |
|---|---|
| Mã hóa | 6 khối 1 MiB; 4 khối đầu chính là 4 khối dữ liệu gốc |
| Bỏ đi lần lượt cả 15 cặp khối có thể có | dựng lại đúng từng byte 15/15 lần |
| Chỉ còn 3 khối | thư viện từ chối: cần đủ 4 khối |
| Một khối chẵn lẻ (4 + 1): bỏ khối dữ liệu thứ ba | dựng lại đúng từ ba khối còn lại và khối chẵn lẻ |

Bốn khối đầu giống hệt dữ liệu gốc nên khi không mất gì thì đọc thẳng được, không phải giải mã.

## Giới hạn cần nhớ

Tài liệu Ceph dặn đừng coi mã xóa là bữa trưa miễn phí: hiệu năng giảm rõ, nhất là với ổ cứng quay và khi cụm đang phục hồi. Phục hồi một khối phải đọc các khối còn lại, dựng lại rồi ghi khối mới. Khi chưa chắc chọn bộ nào, Ceph khuyên 4 + 2 hoặc 6 + 3 (bộ mặc định của Ceph là 2 + 2), và rất không nên dùng m = 1 cho dữ liệu thật vì khi đang bảo trì một nơi thì không còn gì dự phòng.

## Nhìn hình trả lời

Một cụm có 5 máy chủ lưu trữ. Đội vận hành muốn dùng mã xóa 4 + 2 và đặt mỗi khối trên một máy khác nhau. Điều gì không ổn?

<details>
<summary>Xem đáp án</summary>

4 + 2 cần 6 khối ở 6 nơi hỏng độc lập, mà cụm chỉ có 5 máy: ít nhất một máy phải giữ hai khối, nên máy đó hỏng là mất hai khối một lúc và hết dự phòng. Tài liệu Ceph còn nói có lợi về vận hành nếu cụm có ít nhất k + m + 1 nơi như vậy.
Với 5 máy, chọn một bộ k + m nhỏ hơn (như 2 + 2, hay 3 + 2 nếu chấp nhận không còn nơi dự phòng) hoặc thêm máy.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn minh họa cách tính khối mã bằng hai công thức cộng trừ "rút gọn"; mã xóa thật như của zfec làm phép tính trên trường hữu hạn chứ không phải số học thường, nên bài này không lặp lại công thức đó.
Bài nguồn dẫn tính toán của Backblaze rằng mã xóa đạt độ bền "11 số 9" so với "6 số 9" của ba bản sao, với tỉ lệ hỏng nút 0,81% mỗi năm. Bài này không đọc được tính toán gốc nên không dùng các con số đó.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/erasure-coding.md): mã xóa 4 + 2, chi phí chỗ so với ba bản sao.
- [Ceph — Erasure code, tại commit cố định](https://github.com/ceph/ceph/blob/c0b32d47115c516baef9eb0111b4dc1c21c91ff4/doc/rados/operations/erasure-code.rst): khối dữ liệu và khối mã, hệ số (k + m) / k, 1,5 so với 3,0, cái giá về hiệu năng, khuyên 4 + 2 hoặc 6 + 3 khi chưa chắc, bộ mặc định 2 + 2, tránh m = 1, cần k + m nơi hỏng độc lập, từ bản Octopus phục hồi khi còn ít nhất k khối. Đọc từ bản clone của kho.
- [zfec — README, tại commit cố định](https://github.com/tahoe-lafs/zfec/blob/1fede6c166592c98da7f102539f94daf99db4756/README.rst): thư viện mã xóa dựa trên thư viện fec của Luigi Rizzo, giải mã cần k khối. Đọc từ bản clone của kho.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 bằng zfec 1.6.0.0 trên Python 3.13; không đo tốc độ.
Bài viết và hình được thiết kế độc lập.

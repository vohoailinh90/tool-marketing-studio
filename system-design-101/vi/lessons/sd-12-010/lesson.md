# Ví, sổ cái và tệp quyết toán: ba nơi giữ số tiền phải khớp nhau

**Một khoản thanh toán thành công để lại số tiền ở ba nơi: ví của người bán, sổ cái, và tệp quyết toán của nhà cung cấp thanh toán gửi mỗi đêm; hệ thống đúng khi ba nơi này khớp nhau.**
Bài này không kể lại cả đường đi của đồng tiền mà thử xem điều gì làm ví và sổ cái lệch nhau, và cách đối soát với tệp quyết toán tìm ra chỗ lệch.

![Hai khung. Khung một, đường đi của một khoản thanh toán: dịch vụ thanh toán nhận lệnh, gọi nhà cung cấp thanh toán, cập nhật ví người bán, rồi ghi một dòng vào sổ cái. Khung hai, ba chỗ phải khớp: ví khớp với sổ cái, sổ cái khớp với tệp quyết toán mỗi đêm, và việc cập nhật ví cùng ghi sổ nên làm trong một giao dịch.](../../diagrams/sd-12-010-main.svg)

## Từ viết tắt

- **PSP** (Payment Service Provider) — nhà cung cấp dịch vụ thanh toán: bên ngoài mà hệ thống gọi để hoàn tất thanh toán bằng thẻ, và gửi tệp quyết toán mỗi đêm.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để hỏi và ghi cơ sở dữ liệu; SQLite là một cơ sở dữ liệu nhỏ chạy trong chương trình dùng ngôn ngữ này.

## Đọc hình

**Đường đi.** Khi khách bấm Mua, dịch vụ thanh toán nhận một sự kiện thanh toán và lưu nó. Một sự kiện có thể gồm nhiều lệnh thanh toán, chẳng hạn khách mua của nhiều người bán trong một lần thanh toán; mỗi lệnh được một bộ thực thi lưu rồi gọi PSP. Khi bộ thực thi báo thành công, dịch vụ thanh toán cập nhật ví để ghi số tiền người bán có, rồi gọi sổ cái để thêm một dòng mới. Mỗi bước đều ghi vào cơ sở dữ liệu.

**Quyết toán.** Mỗi đêm, PSP hoặc ngân hàng gửi tệp quyết toán: số dư tài khoản ngân hàng kèm mọi giao dịch trong ngày. Đó là bản ghi của một bên thứ ba để so với bản ghi của mình.

## Thử nghiệm: ví lệch sổ cái, và đối soát

Ngày 2026-10-19, người biên soạn viết một chương trình Python dùng SQLite trong bộ nhớ (hai bảng, `wallet` giữ số dư của ba người bán và `ledger` chỉ thêm dòng) và chạy 1.000 khoản thanh toán có số tiền ngẫu nhiên (hạt giống cố định). Chương trình cho "sự cố" xảy ra ở một số khoản ngay sau khi cập nhật ví và trước khi ghi sổ (xác suất 5% mỗi khoản, rơi vào 42 khoản).

| Cách làm | Người bán lệch | Ví nhiều hơn sổ cái |
|---|---|---|
| Hai thao tác riêng, không giao dịch | cả 3 người bán | 193.216 đơn vị tiền nhỏ nhất |
| Cả hai thao tác trong một giao dịch, sự cố thì hủy cả hai | 0 | 0 |

Rồi tạo "tệp quyết toán" từ chính danh sách đó: bỏ đi 3 khoản, sửa số tiền của 2 khoản (cộng hoặc trừ 100), thêm 1 khoản lạ. So hai bên theo mã khoản thanh toán thì được: 3 khoản chỉ có ở mình, 1 khoản chỉ có ở PSP, 2 khoản khác số tiền, tổng chênh lệch -25.000 đơn vị nhỏ nhất. Ba loại chênh lệch đó đủ để một người xử lý từng nhóm.

## Giới hạn cần nhớ

Thử nghiệm dùng một cơ sở dữ liệu trong bộ nhớ trên một máy; hệ thống thật gọi dịch vụ ví và dịch vụ sổ cái riêng qua mạng, nơi một giao dịch cơ sở dữ liệu không bao trùm được cả hai, và cần cách khác (như thử lại có kiểm soát) mà thử nghiệm không đề cập. Bài nguồn không nói gì về việc ví và sổ cái có phải nằm trong một giao dịch, nên điều đó là kết luận từ thử nghiệm, không phải lời của nguồn. Chênh lệch ở tệp quyết toán là dữ liệu sinh ngẫu nhiên, không phản ánh tỷ lệ thật. Bài cũng chưa bàn việc thử lại và khóa chống trùng, mà bài về thử lại thanh toán trong nhóm này đã nói.

## Nhìn hình trả lời

Sáng nay đối soát thấy một khoản có trong sổ cái nhưng không có trong tệp quyết toán của PSP. Có những cách giải thích nào, và bạn nên kiểm tra gì trước?

<details>
<summary>Xem đáp án</summary>

Có thể PSP chưa tính khoản đó vào ngày quyết toán này (khoản rơi sát giờ chốt), có thể gọi PSP thất bại nhưng hệ thống vẫn ghi sổ, hoặc khoản bị hoàn trả. Nên kiểm tra trước trạng thái lệnh thanh toán của khoản đó với PSP và thời điểm của nó so với giờ chốt, rồi mới sửa sổ.
Đây là suy luận của người biên soạn từ ba loại chênh lệch trong thử nghiệm; nguồn không bàn trường hợp này.

</details>

<details>
<summary>Xem sâu hơn: điều đã đổi so với bài nguồn</summary>

Bài nguồn và bài về hệ thống thanh toán trong nhóm Thanh toán cùng một nguồn: đường đi từ nút Mua tới sổ cái, và tệp quyết toán mỗi đêm. Bài này không lặp lại việc kể đường đi mà chỉ dùng nó làm nền, rồi thử hai điều: giao dịch chung cho ví và sổ cái, và đối soát với tệp quyết toán.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/payment-system.md): đường đi một khoản thanh toán và tệp quyết toán mỗi đêm. Hai thử nghiệm là của người biên soạn.
- Thử nghiệm của người biên soạn bằng Python 3 và SQLite (ngày 2026-10-19): ví và sổ cái, và đối soát.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

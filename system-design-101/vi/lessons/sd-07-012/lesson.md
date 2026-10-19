# Hệ thống thanh toán: từ nút Mua tới sổ cái

**Khi bạn bấm nút Mua trên một trang bán hàng, một sự kiện thanh toán đi qua một chuỗi dịch vụ: gọi bên thanh toán thẻ, cập nhật ví của người bán, rồi ghi thêm một dòng vào sổ cái. Mỗi bước đều lưu vào cơ sở dữ liệu.**

![Ba khung. Khung một, từ nút Mua tới PSP: khi khách bấm Mua, dịch vụ thanh toán nhận sự kiện thanh toán, gọi bộ thực thi thanh toán cho từng lệnh, và bộ thực thi gọi PSP bên ngoài để hoàn tất thanh toán bằng thẻ. Khung hai, ghi sổ: dịch vụ thanh toán cập nhật ví để ghi số tiền của người bán, rồi gọi sổ cái ghi thêm một dòng. Khung ba, điều cần nhớ: mỗi bước đều lưu vào cơ sở dữ liệu, một lần mua nhiều người bán thành nhiều lệnh, và mỗi đêm PSP hoặc ngân hàng gửi tệp quyết toán.](../../diagrams/sd-07-012-main.svg)

## Từ viết tắt

- **PSP** (Payment Service Provider) — nhà cung cấp dịch vụ thanh toán: bên ngoài mà bộ thực thi gọi để hoàn tất thanh toán bằng thẻ tín dụng.

## Đọc hình

**1. Từ nút Mua tới PSP.** Khi khách bấm Mua, một sự kiện thanh toán được tạo ra và gửi tới *dịch vụ thanh toán*, nơi lưu sự kiện vào cơ sở dữ liệu. Đôi khi một sự kiện chứa nhiều *lệnh thanh toán*: chẳng hạn khách chọn sản phẩm của nhiều người bán trong một lần thanh toán. Khi đó dịch vụ thanh toán gọi *bộ thực thi thanh toán* cho từng lệnh. Bộ thực thi lưu lệnh vào cơ sở dữ liệu rồi gọi một PSP bên ngoài để hoàn tất thanh toán bằng thẻ tín dụng.

**2. Ghi sổ.** Sau khi bộ thực thi thực hiện thanh toán thành công, dịch vụ thanh toán cập nhật *ví* để ghi lại một người bán có bao nhiêu tiền. Máy chủ ví lưu số dư mới vào cơ sở dữ liệu. Sau khi ví cập nhật xong, dịch vụ thanh toán gọi *sổ cái*; dịch vụ sổ cái thêm (append) thông tin mới vào cơ sở dữ liệu.

**Tệp quyết toán.** Mỗi đêm, PSP hoặc ngân hàng gửi cho khách hàng của họ các tệp quyết toán. Một tệp chứa số dư của tài khoản ngân hàng cùng mọi giao dịch đã diễn ra trên tài khoản đó trong ngày.

## Giới hạn cần nhớ

Nguồn chỉ liệt kê luồng, không nói gì về lỗi: nếu PSP lỗi, nếu ví cập nhật thất bại, hay nếu một lệnh trong nhiều lệnh bị từ chối thì sao, bài này không bổ sung.
Người biên soạn hiểu rằng việc sổ cái chỉ *thêm* dòng mới (không sửa dòng cũ) giúp lưu vết, và tệp quyết toán hằng đêm là thứ để đối soát với bản ghi của chính mình; cả hai là suy luận từ cách nguồn viết, chưa đối chiếu với tài liệu của một hệ thống cụ thể.

## Nhìn hình trả lời

Một khách chọn hàng của ba người bán và bấm Mua một lần. Dịch vụ thanh toán gọi bộ thực thi mấy lần, và vì sao ví cần được cập nhật *sau* khi bộ thực thi hoàn tất?

<details>
<summary>Xem đáp án</summary>

Ba lần: nguồn nói dịch vụ thanh toán gọi bộ thực thi cho từng lệnh thanh toán, và một sự kiện có thể chứa nhiều lệnh, ví dụ mỗi người bán một lệnh.
Ví cập nhật sau vì nguồn kể rõ thứ tự: chỉ sau khi bộ thực thi thực hiện thanh toán thành công, dịch vụ thanh toán mới ghi số tiền của người bán vào ví; rồi sổ cái mới được cập nhật sau khi ví xong. Vì sao cần đúng thứ tự thì nguồn không giải thích; đó là điều người biên soạn suy ra (không ghi cho người bán khoản tiền chưa thu được).

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là hình kèm mười gạch đầu dòng. Bài này nhóm chúng thành hai lược đồ ba bên và một khung ghi nhớ, đồng thời để việc lưu vào cơ sở dữ liệu thành một điều cần nhớ thay vì vẽ thêm một bên ở mỗi bước. Phản hồi của PSP trong hình là cách vẽ kết quả thành công mà nguồn nhắc ở bước sau.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/payment-system.md): luồng thanh toán từ nút Mua tới sổ cái và tệp quyết toán hằng đêm. Phần giới hạn và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

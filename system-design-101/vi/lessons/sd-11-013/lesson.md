# Từ một máy chủ tới hàng triệu người dùng: sáu bước mở rộng một trang web

**Một trang web thương mại điện tử lớn dần theo từng nút thắt: mỗi bước gỡ một nút thắt và để lộ nút thắt kế tiếp.**
Đọc theo thứ tự này, bạn biết vì sao ai cũng thêm bộ chia tải trước khi chia nhỏ cơ sở dữ liệu, và vì sao bộ nhớ đệm hay đứng sau cùng.

![Hai khung. Khung một, ba bước đầu: tách máy ứng dụng khỏi máy cơ sở dữ liệu, chạy nhiều máy ứng dụng, đặt bộ chia tải phía trước. Khung hai, ba bước sau: tách đọc và ghi bằng bản sao chỉ đọc, chia nhỏ hoặc đệm dữ liệu, rồi tách thành các dịch vụ riêng.](../../diagrams/sd-11-013-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần của máy làm các phép tính.
- **RAM** (Random Access Memory) — bộ nhớ truy cập ngẫu nhiên: bộ nhớ làm việc nhanh của máy, mất khi tắt máy.

## Đọc hình

Sáu bước giữ theo thứ tự của bài nguồn; ví dụ phụ và phép tính là của người biên soạn. Cửa hàng có hai dịch vụ: kho hàng (mô tả sản phẩm, tồn kho) và người dùng (đăng ký, đăng nhập).

**Bước 1. Tách máy ứng dụng khỏi máy cơ sở dữ liệu.** Một máy làm tất cả thì ứng dụng và cơ sở dữ liệu tranh nhau CPU và RAM. Tách ra hai máy cho mỗi bên tài nguyên riêng.

**Bước 2. Chạy một cụm máy ứng dụng.** Một máy ứng dụng không còn đủ thì chạy nhiều bản của nó. Cách này dễ khi ứng dụng không giữ trạng thái người dùng trong bộ nhớ của riêng một máy.

**Bước 3. Đặt bộ chia tải.** Có nhiều máy thì phải quyết định yêu cầu nào đi máy nào. Bộ chia tải nhận mọi yêu cầu và chia đều cho các máy.

**Bước 4. Tách đọc và ghi.** Khi cơ sở dữ liệu thành nút thắt, những truy vấn đọc thường xuyên được chuyển sang các bản sao chỉ đọc; chỉ ghi mới vào bản chính. Nhờ đó khả năng đọc tăng nhiều. Lưu ý: bản sao có thể chậm hơn bản chính một chút.

**Bước 5. Ba lựa chọn khi một cơ sở dữ liệu không đủ cho cả bảng sản phẩm lẫn bảng người dùng.** *Tăng cấu hình một máy (vertical scaling, thêm CPU, RAM)* có giới hạn cứng; bài nguồn gọi cách này là "vertical partition", nhưng thuật ngữ thường dùng cho việc này là vertical scaling. *Chia dữ liệu theo chiều ngang (horizontal partition)* là thêm máy cơ sở dữ liệu, mỗi máy giữ một phần dữ liệu. *Thêm tầng bộ nhớ đệm* để giảm lượt đọc.

**Ví dụ tính về bộ nhớ đệm.** Giả sử 1 000 lượt đọc mỗi giây và bộ đệm trả lời được 90% (tỷ lệ trúng 90%). Cơ sở dữ liệu chỉ nhận 100 lượt mỗi giây, ít hơn mười lần. Nếu tỷ lệ trúng lên 95% thì chỉ còn 50 lượt, ít hơn hai mươi lần. Tăng vài điểm phần trăm tỷ lệ trúng có thể giảm tải cho cơ sở dữ liệu rất nhiều, nhưng chỉ cho việc đọc.

**Bước 6. Tách thành các dịch vụ.** Khi các chức năng lớn đủ, tách chúng thành từng dịch vụ (kho hàng, người dùng) để mỗi dịch vụ phát triển và mở rộng riêng. Đó là kiến trúc hướng dịch vụ hay vi dịch vụ.

## Giới hạn cần nhớ

Bài nguồn gọi việc tăng cấu hình máy ở bước 5 là "vertical partition"; bài này dùng tên vertical scaling cho nó, vì "chia theo chiều dọc" ở các bài khác của bộ này nghĩa là cắt cột của bảng. Không phải trang nào cũng đi đủ sáu bước theo đúng thứ tự: nhiều trang dùng bộ nhớ đệm sớm hơn, và nhiều trang nhỏ không bao giờ cần vi dịch vụ, thứ mang thêm chi phí vận hành. Bài chưa đối chiếu được tài liệu chính thức nào trong phiên viết, và các con số trong ví dụ là số học thuần túy, không phải đo thật.

## Nhìn hình trả lời

Trang của bạn có 95% lượt truy cập là đọc, cơ sở dữ liệu quá tải, bạn chưa tách gì cả. Hai bước rẻ nhất đáng thử trước là gì, và bước nào không giúp được lượt ghi?

<details>
<summary>Xem đáp án</summary>

Thêm bộ nhớ đệm cho các truy vấn đọc lặp lại và đưa lượt đọc sang bản sao chỉ đọc. Cả hai chỉ giúp phần đọc: lượt ghi vẫn dồn vào một bản chính, nên nếu ghi mới là nút thắt thì phải chia nhỏ dữ liệu hoặc tăng cấu hình bản chính. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn kể sáu bước. Bài này giữ thứ tự, gom thành hai nhóm ba bước trong hình, và thêm một ví dụ tính về tỷ lệ trúng bộ nhớ đệm cùng lưu ý về độ trễ của bản sao chỉ đọc.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-scale-a-website-to-support-millions-of-users.md): sáu bước và ví dụ cửa hàng hai dịch vụ. Ví dụ tính, lưu ý và phần giải thích là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức; ví dụ tính là số học thuần túy.

# TikTok và kho mã frontend 200 nghìn tệp

**Một kho mã chung cho nhiều dự án có ích, nhưng càng lớn thì Git càng chậm; theo bài nguồn, TikTok gặp đúng điều này với kho mã frontend 200 nghìn tệp và làm ra công cụ Sparo để Git nhanh lại.**
Bài này trả lời ba câu: monorepo được gì, vì sao nó làm Git chậm, và Sparo đã rút ngắn những thao tác nào.

![Ba khung. Khung một: monorepo được gì, gồm chia sẻ mã dễ hơn, quản lý phụ thuộc đơn giản hơn, một cái nhìn chung về toàn bộ mã. Khung hai: cái giá, kho càng lớn thì thao tác Git càng chậm; kho frontend TypeScript của TikTok có 200 nghìn tệp; TikTok làm công cụ Sparo. Khung ba: kết quả theo nguồn, clone từ 40 phút còn 2 phút, checkout từ 1,5 phút còn 30 giây, status từ 7 giây còn 1 giây, commit từ 15 giây còn 11 giây.](../../diagrams/sd-02-020-main.svg)

## Đọc hình

**Monorepo là gì.** Theo nguồn, monorepo (kho mã nguyên khối) là cách tổ chức trong đó một kho chứa nhiều dự án, thư viện và dịch vụ. Điểm được:
- Chia sẻ mã dễ hơn.
- Quản lý phụ thuộc đơn giản hơn.
- Có một cái nhìn chung về toàn bộ mã.

**Cái giá.** Kho càng lớn thì các thao tác Git càng chậm. TikTok gặp điều này với kho mã frontend viết bằng TypeScript có 200 nghìn tệp.

**Sparo.** TikTok làm công cụ Sparo để tối ưu thao tác Git cho các kho frontend lớn. Số liệu theo nguồn, với bốn lệnh Git: `clone` lấy kho về máy, `checkout` chuyển sang một nhánh hay phiên bản, `status` xem tệp nào đã đổi, `commit` ghi lại một thay đổi.

| Thao tác | Trước | Sau |
|---|---|---|
| `clone` | 40 phút | 2 phút |
| `checkout` | 1,5 phút | 30 giây |
| `status` | 7 giây | 1 giây |
| `commit` | 15 giây | 11 giây |

Thao tác lấy cả kho về (`clone`) được lợi nhiều nhất; `commit` chỉ nhanh hơn khoảng một phần tư.

## Giới hạn cần nhớ

Bài nguồn không nói Sparo làm thế nào để nhanh hơn, số liệu đo trên máy nào, hay lúc nào. Các con số là của bài nguồn, không kiểm chứng ở đây. Phép so "nhiều nhất, một phần tư" là người biên soạn tính từ bảng.

## Nhìn hình thử trả lời

Một kỹ sư chỉ sửa một thư viện nhỏ trong kho 200 nghìn tệp. Thao tác nào trong bảng làm họ mất thời gian nhất khi mới vào dự án, và thao tác nào họ chạy nhiều lần nhất mỗi ngày?

<details>
<summary>Xem đáp án</summary>

Khi mới vào, `clone` tốn nhất (40 phút trước Sparo). Hằng ngày, họ chạy `status` và `commit` nhiều lần nhất, nên dù mỗi lần chỉ vài giây, tổng thời gian vẫn đáng kể; Sparo đưa `status` từ 7 giây xuống 1 giây.

</details>

<details>
<summary>Xem sâu hơn: vì sao kho lớn làm Git chậm</summary>

- `clone` phải tải toàn bộ lịch sử và mọi tệp, dù người dùng chỉ cần một phần.
- `status` phải kiểm tra từng tệp trong thư mục làm việc xem có đổi không; càng nhiều tệp thì càng lâu.
- Cách giảm phổ biến là chỉ lấy về phần thư mục mình cần (sparse checkout) và không tải toàn bộ lịch sử. Tên Sparo gợi ý hướng này, nhưng bài nguồn không xác nhận.

Đây là kiến thức chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-tiktok-manages-a-200k-file-frontend-monorepo.md): định nghĩa monorepo, điểm được, cái giá và số liệu của Sparo.

Đã đọc nguồn ngày 2026-10-19. Tài liệu của Sparo chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

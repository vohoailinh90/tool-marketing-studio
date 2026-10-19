# Soạn thảo chung theo thời gian thực: vì sao cần biến đổi thao tác

**Khi hai người cùng gõ vào một tài liệu, thách thức lớn nhất không phải chuyển dữ liệu nhanh mà là hợp nhất hai thao tác diễn ra cùng lúc sao cho mọi máy đều ra cùng một văn bản.**
Một thử nghiệm nhỏ cho thấy nếu chỉ áp từng thao tác theo thứ tự đến thì hai máy luôn lệch nhau, và một phép biến đổi thao tác sửa được điều đó.

![Hai khung. Khung một, năm thành phần xử lý thao tác soạn thảo: máy chủ WebSocket nhận thao tác từ máy khách, hàng đợi thông điệp lưu các thao tác, máy chủ thao tác tệp lấy thao tác ra và biến đổi, kho lưu trữ giữ siêu dữ liệu, nội dung và thao tác. Khung hai, ba thuật toán hợp nhất: OT biến đổi thao tác, DS đồng bộ chênh lệch, CRDT dùng kiểu dữ liệu tự hợp nhất.](../../diagrams/sd-12-009-main.svg)

## Từ viết tắt

- **OT** (Operational Transformation) — biến đổi thao tác: cách điều chỉnh một thao tác theo những thao tác đồng thời khác để mọi máy hội tụ về cùng kết quả.
- **DS** (Differential Synchronization) — đồng bộ chênh lệch: cách giữ hai bản sao khớp nhau bằng cách liên tục so sánh và gửi phần khác biệt.
- **CRDT** (Conflict-free Replicated Data Type) — kiểu dữ liệu nhân bản không xung đột: cấu trúc dữ liệu được thiết kế để các bản sao tự hợp nhất mà không cần phép biến đổi.

## Đọc hình

**Năm thành phần.** Máy khách gửi thao tác soạn thảo (chèn chữ, xóa chữ) tới máy chủ WebSocket, nơi lo phần giao tiếp thời gian thực. Các thao tác được ghi vào hàng đợi thông điệp. Máy chủ thao tác tệp lấy thao tác do các máy khách tạo ra và dùng thuật toán cộng tác để sinh ra thao tác đã biến đổi. Ba loại dữ liệu được lưu: siêu dữ liệu của tệp, nội dung tệp và các thao tác.

**Ba hướng hợp nhất.** Bài nguồn kể OT, DS và CRDT. Nó nói Google Docs dùng OT theo trang Wikipedia, còn CRDT vẫn là mảng đang nghiên cứu cho soạn thảo đồng thời thời gian thực.

## Thử nghiệm: hai người cùng chèn chữ

Ngày 2026-10-19, người biên soạn viết một chương trình Python nhỏ cho thao tác chèn chữ. Văn bản gốc là `ABC`. Alice chèn `X` vào vị trí 1, Bob chèn `Y` vào vị trí 2, cùng lúc, mỗi người đều tính vị trí trên bản gốc.

| Cách xử lý | Máy Alice | Máy Bob | Kết quả |
|---|---|---|---|
| Chỉ áp thao tác kia như nhận được | `AXYBC` | `AXBYC` | lệch nhau |
| Có biến đổi: dịch vị trí của thao tác kia nếu thao tác của mình chèn trước nó | `AXBYC` | `AXBYC` | giống nhau |

Phép biến đổi dùng ở đây chỉ có một luật: nếu thao tác của máy kia chèn ở vị trí trước, hoặc cùng vị trí nhưng người đó có mã nhỏ hơn, thì dịch vị trí của thao tác đang xét sang phải bấy nhiêu ký tự. Chạy 10.000 cặp thao tác chèn ngẫu nhiên (văn bản dài 0 đến 6 ký tự, vị trí ngẫu nhiên): cách chỉ áp theo thứ tự đến lệch 10.000 lần, cách có biến đổi lệch 0 lần. Khi hai người chèn đúng cùng một vị trí, mã người dùng quyết định thứ tự để hai máy cho cùng kết quả (`AXYBC`).

## Giới hạn cần nhớ

Thử nghiệm chỉ có hai máy và thao tác chèn một chuỗi; chưa có xóa, định dạng, nhiều hơn hai người, mất mạng hay thứ tự do máy chủ quyết định, là những chỗ khiến OT thật phức tạp hơn nhiều. Kết quả lệch 10.000/10.000 của cách đơn giản không có gì lạ vì hai chuỗi chèn luôn khác nhau; nó chỉ cho thấy cách đó không hội tụ, không đo mức độ. Việc Google Docs dùng OT là điều bài nguồn dẫn từ Wikipedia; bài này không đối chiếu với tài liệu của Google và không so OT với DS hay CRDT.

## Nhìn hình trả lời

Ba người cùng chèn chữ vào vị trí 0 của văn bản trống trong một mili giây. Nếu mỗi người tự áp thao tác của hai người kia theo thứ tự nhận được, điều gì xảy ra với văn bản trên ba máy?

<details>
<summary>Xem đáp án</summary>

Ba máy có thể cho ba văn bản khác nhau, vì thứ tự nhận thao tác trên mỗi máy khác nhau; đây là trường hợp "lệch nhau" của thử nghiệm với hai người, mở rộng ra ba. Một thứ tự thống nhất (mã người dùng, như trong phép biến đổi trên) hay một máy chủ chọn thứ tự là cách để cả ba hội tụ.
Đây là suy luận từ thử nghiệm hai người; chưa chạy cho ba người.

</details>

<details>
<summary>Xem sâu hơn: điều đã bổ sung so với bài nguồn</summary>

Bài nguồn liệt kê năm bước xử lý thao tác và gọi tên ba thuật toán. Bài này giữ cả hai, rồi thêm thử nghiệm để thấy vì sao riêng việc "áp theo thứ tự đến" không đủ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-design-google-docs.md): năm thành phần, ba thuật toán OT, DS, CRDT, và nhận định về Google Docs.
- Thử nghiệm của người biên soạn bằng Python 3 (ngày 2026-10-19): hai thao tác chèn đồng thời.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

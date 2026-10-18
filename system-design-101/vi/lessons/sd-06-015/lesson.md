# Bộ nhớ đệm hỏng theo những kiểu nào

**Bộ nhớ đệm đứng trước cơ sở dữ liệu để che tải cho nó. Có bốn kiểu hỏng quen thuộc, và kiểu nào cũng kết thúc giống nhau: tải dồn thẳng về cơ sở dữ liệu.** Ba kiểu do thời điểm (nhiều khóa cùng hết hạn, một khóa nóng hết hạn, bộ nhớ đệm sập), một kiểu do dữ liệu không tồn tại.
Bài này thử hai cách chống dồn tải: một khóa phân tán để chỉ một yêu cầu đi nạp lại, và hạn sống lệch nhau.

![Ba khung. Khung một, bốn kiểu hỏng: nhiều khóa hết hạn cùng lúc làm yêu cầu dồn về cơ sở dữ liệu; khóa không tồn tại thì lần nào cũng xuyên qua; một khóa nóng hết hạn làm hàng loạt yêu cầu cùng nạp lại; bộ đệm sập thì mọi yêu cầu đổ về cơ sở dữ liệu. Khung hai, thử khóa nóng hết hạn với 50 yêu cầu cùng lúc: không bảo vệ thì 50 lần hỏi cơ sở dữ liệu; giành khóa trong Redis thì 1 hoặc 2 lần; giành khóa rồi đọc lại bộ đệm thì 1 lần trong cả 10 lần thử. Khung ba, hạn sống lệch nhau: 10 nghìn khóa cùng hạn sống hết hạn trong cùng một phút; cộng thêm 0 đến 10 phút ngẫu nhiên thì rải ra 11 phút, phút đông nhất 1.042 khóa.](../../diagrams/sd-06-015-main.svg)

## Từ viết tắt

- **TTL** (Time To Live) — thời gian sống: hạn của một khóa trong bộ nhớ đệm, hết hạn thì khóa tự mất.
- **CDN** (Content Delivery Network) — mạng phân phối nội dung: các máy chủ đặt gần người dùng, giữ bản sao nội dung; ở đây là một loại bộ nhớ đệm dùng chung.
- **MDN** (Mozilla Developer Network) — bộ tài liệu web do Mozilla và cộng đồng viết; bài dùng mục "request collapse" trong hướng dẫn về bộ nhớ đệm của nó.

## Đọc hình

1. **Nhiều khóa hết hạn cùng lúc.** Nếu nạp hàng loạt khóa cùng lúc với cùng hạn sống (TTL), chúng cũng hết hạn cùng lúc, và mọi lượt đọc của chúng dồn về cơ sở dữ liệu trong một khoảnh khắc. Cách chữa: cộng thêm một khoảng ngẫu nhiên vào hạn sống.
2. **Khóa không tồn tại.** Yêu cầu xin dữ liệu không có thì không có gì để cất, nên lần nào cũng đi xuyên tới cơ sở dữ liệu. Nhóm này có một bài riêng về hiện tượng này, với cất giá trị rỗng và bộ lọc Bloom.
3. **Một khóa nóng hết hạn.** Một khóa được rất nhiều yêu cầu đọc cùng lúc vừa hết hạn: tất cả cùng thấy thiếu và cùng đi nạp lại. Cách chữa: chỉ cho một yêu cầu đi nạp, các yêu cầu khác chờ kết quả. MDN gọi việc này ở bộ nhớ đệm dùng chung (như CDN) là *request collapse*: nhiều yêu cầu giống nhau đến cùng lúc thì bộ nhớ đệm chỉ gửi một yêu cầu về máy chủ gốc rồi dùng kết quả cho tất cả.
4. **Bộ nhớ đệm sập.** Mọi yêu cầu đổ về cơ sở dữ liệu. Cách chữa: chạy bộ nhớ đệm thành cụm để một máy hỏng không mất hết, và dùng *circuit breaker*: mẫu thiết kế của Microsoft mô tả việc tạm chặn lời gọi tới một dịch vụ khi lỗi vượt ngưỡng, thay vì cứ thử lại, để dịch vụ kịp hồi phục và không kéo theo phần còn lại.

## Thử: khóa nóng hết hạn

Ngày 2026-10-18, trên một máy, với Redis 7.0.15. "Cơ sở dữ liệu" là một hàm chờ 200 ms. Khóa nóng vừa hết hạn thì 50 luồng cùng đọc nó một lúc; mỗi cách chạy 10 lần.

| Cách làm | Số lần hỏi cơ sở dữ liệu mỗi lần thử | Thời gian chờ lâu nhất |
|---|---|---|
| Không bảo vệ (cache-aside thường) | 50 ở cả 10 lần | 205–210 ms |
| Giành khóa bằng `SET lock:hot <mã ngẫu nhiên> NX PX 2000`; ai giành được thì nạp | 1 ở 6 lần, 2 ở 4 lần | 211–403 ms |
| Như trên, nhưng giành được khóa thì đọc lại bộ nhớ đệm trước khi nạp | 1 ở cả 10 lần | 213–216 ms |

Cách thứ hai đôi khi nạp hai lần: một yêu cầu thấy thiếu ngay trước khi giá trị được cất, rồi giành được khóa ngay sau khi người nạp đầu tiên đã nhả nó. Đọc lại bộ nhớ đệm sau khi giành khóa chặn được trường hợp đó. Tài liệu lệnh `SET` của Redis mô tả đúng mẫu khóa này (`NX` để chỉ đặt khi chưa có, kèm hạn để khóa tự nhả), khuyên đặt một mã ngẫu nhiên làm giá trị và chỉ xóa khóa khi giá trị còn khớp, và nói thuật toán Redlock cho bảo đảm tốt hơn khi cần. Việc so rồi xóa phải là **một thao tác nguyên tử**: tài liệu đưa một đoạn script Lua chạy cả hai bước trong Redis. Nếu đọc khóa bằng `GET` rồi mới gửi `DEL`, khóa có thể vừa hết hạn và một yêu cầu khác đã giành được nó giữa hai lệnh, và ta xóa mất khóa của người đó. Chương trình thử ở trên dùng `GET` rồi `DEL` cho đơn giản; đừng làm vậy trong mã thật.

## Thử: hạn sống lệch nhau

Đặt 10.000 khóa với cùng hạn 3.600 giây: đọc lại hạn còn lại, cả 10.000 khóa sẽ hết hạn trong cùng một phút. Đặt 10.000 khóa khác với hạn 3.600 giây cộng một số ngẫu nhiên từ 0 đến 599 giây: chúng rải ra 11 phút, phút đông nhất có 1.042 khóa.

## Giới hạn cần nhớ

Khóa phân tán làm các yêu cầu khác phải chờ (hoặc nhận bản cũ); nếu người nạp chết giữa chừng, hạn của khóa quyết định mọi người chờ bao lâu. Thử nghiệm chỉ có một máy Redis và 50 luồng trên một máy; với nhiều máy Redis và mạng thật, xem thêm Redlock. Bài nguồn còn gợi ý bỏ hạn sống cho khóa nóng; cách đó tránh được việc hết hạn nhưng phải có cách khác để cập nhật khi dữ liệu đổi.

## Nhìn hình trả lời

Mỗi đêm lúc 0 giờ, một tác vụ nạp lại 50.000 khóa giá sản phẩm với hạn 24 giờ. Cứ đúng 0 giờ đêm sau, cơ sở dữ liệu lại quá tải trong vài phút. Vì sao, và sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Cả 50.000 khóa được nạp gần như cùng lúc với cùng hạn, nên cũng hết hạn gần như cùng lúc (kiểu hỏng thứ nhất, giống phép thử 10.000 khóa cùng hạn rơi vào một phút). Các lượt đọc lúc đó đều trượt và dồn về cơ sở dữ liệu, chồng thêm lên chính tác vụ nạp lại.
Sửa: cộng một khoảng ngẫu nhiên vào hạn của từng khóa để chúng hết hạn rải ra; với vài khóa rất nóng, thêm khóa phân tán để chỉ một yêu cầu đi nạp.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm và sửa so với bài nguồn</summary>

Bài nguồn mô tả bốn kiểu hỏng và cách chữa. Bài này thử hai cách chữa, phát hiện một chỗ hở của cách giành khóa đơn giản (nạp hai lần) và cách bịt nó.
Bài nguồn nói khóa nóng chiếm 80% lượt truy vấn; bài bỏ con số này vì không có nguồn. Bài nguồn mô tả circuit breaker như việc "không cho dịch vụ truy cập cả bộ nhớ đệm lẫn cơ sở dữ liệu"; bài này dùng định nghĩa trong mẫu thiết kế của Microsoft (tạm chặn lời gọi tới dịch vụ đang lỗi). Các cách chữa kiểu hỏng thứ hai nằm ở bài riêng của nhóm.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-can-cache-systems-go-wrong.md): bốn kiểu bộ nhớ đệm hỏng và cách chữa.
- [MDN — hướng dẫn HTTP caching, tại commit cố định](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/caching/index.md): mục "Request collapse".
- [Redis — tài liệu lệnh SET, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/commands/set.md): tùy chọn `NX` và `PX`; mẫu khóa bằng `SET ... NX EX`, mã ngẫu nhiên và chỉ xóa khi khớp; Redlock cho bảo đảm tốt hơn.
- [Microsoft — mẫu Circuit Breaker, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/circuit-breaker.md): tạm chặn lời gọi tới dịch vụ khi lỗi vượt ngưỡng để nó kịp hồi phục.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày với Redis 7.0.15. Bài viết và hình được thiết kế độc lập.

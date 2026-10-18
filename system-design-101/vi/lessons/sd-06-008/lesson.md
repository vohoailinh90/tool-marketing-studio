# Năm chiến lược giữ bộ nhớ đệm khớp với cơ sở dữ liệu

**Có bộ nhớ đệm là có hai bản của cùng một dữ liệu: bản trong bộ nhớ đệm và bản trong cơ sở dữ liệu. Năm chiến lược quen thuộc (hai cho chiều đọc, ba cho chiều ghi) là năm cách giữ hai bản ấy khớp nhau, và mỗi cách lệch theo một kiểu riêng.**

![Ba khung. Khung một, hai cách đọc: cache-aside, ứng dụng hỏi bộ nhớ đệm, thiếu thì đọc cơ sở dữ liệu rồi tự cất vào; read-through, bộ nhớ đệm tự đi lấy khi thiếu. Khung hai, ba cách ghi: write-through ghi cả hai trong cùng một thao tác; write-around chỉ ghi cơ sở dữ liệu rồi xóa bản trong bộ nhớ đệm; write-back chỉ ghi bộ nhớ đệm, chép xuống cơ sở dữ liệu sau. Khung ba, kết quả thử với Redis và SQLite: sửa cơ sở dữ liệu mà không xóa bản đệm thì đọc ra giá cũ cho tới khi hết hạn; một lượt đọc chậm có thể cất lại giá cũ ngay sau lượt xóa; write-back mất lần ghi chưa chép khi bộ nhớ đệm sập.](../../diagrams/sd-06-008-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; SQLite là một cơ sở dữ liệu nhỏ dùng nó, chạy ngay trong chương trình.
- **TTL** (Time To Live) — thời gian sống: số giây một khóa trong bộ nhớ đệm còn được giữ trước khi tự hết hạn.

## Đọc hình

**Hai cách đọc.** Với *cache-aside*, ứng dụng tự làm hết: hỏi bộ nhớ đệm trước, thiếu (cache miss) thì đọc cơ sở dữ liệu, cất vào bộ nhớ đệm rồi trả. Với *read-through*, bộ nhớ đệm tự đi lấy khi thiếu, ứng dụng chỉ nói chuyện với bộ nhớ đệm. Mẫu thiết kế Cache-Aside của Microsoft ghi rằng nhiều hệ thống bộ nhớ đệm có sẵn read-through, và cache-aside là cách giả lập nó khi hệ thống không có.

**Ba cách ghi.**

- *Write-through*: ghi cơ sở dữ liệu và bộ nhớ đệm trong cùng một thao tác, chỉ báo xong khi cả hai đều xong. Đọc ngay sau khi ghi là thấy giá mới; đổi lại, mỗi lần ghi chậm hơn.
- *Write-around*: chỉ ghi cơ sở dữ liệu, rồi xóa bản trong bộ nhớ đệm (Microsoft gọi là "invalidate on write"); lần đọc sau sẽ nạp lại. Hay đi cặp với cache-aside.
- *Write-back* (còn gọi write-behind): chỉ ghi bộ nhớ đệm, rồi chép xuống cơ sở dữ liệu sau. Ghi rất nhanh, nhưng trong lúc chưa chép, dữ liệu chỉ nằm ở bộ nhớ đệm.

## Thử với Redis và SQLite

Ngày 2026-10-18, bài viết một chương trình nhỏ bằng Python: giá sản phẩm nằm trong SQLite, bản đệm nằm trong Redis 7.0.15 (không bật lưu xuống đĩa), mỗi bản đệm sống 60 giây.

1. **Cache-aside chạy đúng.** Lần đọc đầu lấy 100 từ cơ sở dữ liệu và cất vào Redis; lần sau lấy 100 từ Redis.
2. **Quên xóa bản đệm.** Sửa giá trong cơ sở dữ liệu thành 120 mà không đụng tới Redis: lần đọc sau vẫn ra 100, và bản cũ còn sống 60 giây nữa.
3. **Xóa khi ghi.** Xóa khóa trong Redis sau khi sửa: lần đọc sau lấy 120 từ cơ sở dữ liệu.
4. **Lượt đọc chậm chen vào.** Bài cố tình xếp thứ tự: một lượt đọc thấy thiếu và đọc được 120 từ cơ sở dữ liệu; ngay lúc đó một lượt ghi đổi giá thành 150 và xóa bản đệm; rồi lượt đọc kia mới cất 120 vào Redis. Kết quả: cơ sở dữ liệu là 150, bộ nhớ đệm là 120, và sẽ sai suốt 60 giây.
5. **Write-through.** Ghi 170 vào cả hai trong cùng một hàm: cả hai đều là 170.
6. **Write-back mất dữ liệu.** Ghi 200 vào Redis rồi chép xuống: cơ sở dữ liệu là 200. Ghi tiếp 210 vào Redis, rồi tắt Redis trước khi chép: cơ sở dữ liệu vẫn là 200, lần ghi 210 mất hẳn.

## Giới hạn cần nhớ

Không chiến lược nào giữ hai bản khớp tuyệt đối. Mẫu Cache-Aside của Microsoft ghi rõ nó không bảo đảm nhất quán: một tiến trình khác sửa cơ sở dữ liệu thì bộ nhớ đệm không biết, và ngay sau khi ghi, người đọc có thể gặp bản cũ trong chốc lát. Hướng dẫn của Microsoft cũng khuyên coi bộ nhớ đệm là kho tạm có thể mất bất cứ lúc nào, đừng để dữ liệu quý chỉ nằm ở đó, đúng điều bước 6 cho thấy với write-back.
Hạn sống (TTL) là lưới an toàn cuối cùng: bản đệm sai đến đâu cũng chỉ sai tối đa tới khi hết hạn.

## Nhìn hình trả lời

Trang sản phẩm dùng cache-aside với TTL 1 giờ. Đội vận hành sửa giá trực tiếp trong cơ sở dữ liệu bằng một câu lệnh, không qua ứng dụng. Khách hàng sẽ thấy giá mới khi nào? Nên sửa quy trình thế nào?

<details>
<summary>Xem đáp án</summary>

Có thể tới 1 giờ sau: bản đệm cũ vẫn còn hạn, ứng dụng không biết cơ sở dữ liệu đã đổi (giống bước 2 của thử nghiệm).
Nên đổi giá qua ứng dụng để nó xóa bản đệm sau khi ghi (bước 3), hoặc xóa khóa trong bộ nhớ đệm ngay sau câu lệnh sửa. Với dữ liệu nhạy cảm về giá, cân nhắc TTL ngắn hơn để giới hạn thời gian sai, và nhớ rằng lượt đọc chậm chen vào (bước 4) vẫn có thể làm sai thêm một hạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn liệt kê năm chiến lược và nói chúng thường được dùng kết hợp, như write-around với cache-aside. Bài này thêm định nghĩa từ tài liệu kiến trúc của Microsoft và một thử nghiệm cho thấy mỗi cách lệch thế nào.
Bước 4 xếp thứ tự bằng tay để thấy chắc chắn; trong hệ thống thật nó chỉ xảy ra khi hai yêu cầu chen nhau đúng lúc. Bài không thử read-through với một sản phẩm cụ thể; write-back trong thử nghiệm là một vòng chép tự viết, không phải tính năng của Redis.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-5-caching-strategies.md): hai chiến lược đọc, ba chiến lược ghi, thường dùng kết hợp.
- [Microsoft — mẫu thiết kế Cache-Aside, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/cache-aside-content.md): ba bước của cache-aside, xóa khi ghi, không bảo đảm nhất quán, có thể thấy bản cũ ngay sau khi ghi; read-through, write-through và write-behind có sẵn trong nhiều hệ thống.
- [Microsoft — hướng dẫn về bộ nhớ đệm, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/best-practices/caching.md): write-through và xóa khi ghi; coi bộ nhớ đệm là kho tạm có thể mất.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của kho; thử nghiệm chạy cùng ngày với Redis 7.0.15 và SQLite trong Python 3.13. Bài viết và hình được thiết kế độc lập.

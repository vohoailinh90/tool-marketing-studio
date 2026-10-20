# Năm chiến lược bộ đệm: ai đọc, ai ghi, và mất gì

**Mỗi chiến lược bộ đệm trả lời hai câu: khi đọc mà bộ đệm không có, ai đi lấy từ cơ sở dữ liệu; và khi ghi, dữ liệu đi vào bộ đệm, cơ sở dữ liệu, hay cả hai, theo thứ tự nào. Câu trả lời quyết định bạn đánh đổi tốc độ lấy gì: dữ liệu cũ, thời gian chờ, hay nguy cơ mất dữ liệu.**
Phần thử nghiệm dùng Redis làm bộ đệm và SQLite làm cơ sở dữ liệu gốc.

![Ba phần. Phần một, đọc: cache-aside, ứng dụng hỏi bộ đệm, hụt thì tự đọc cơ sở dữ liệu rồi ghi vào bộ đệm; read-through, bộ đệm có bộ nạp, hụt thì chính nó đọc cơ sở dữ liệu. Phần hai, ghi: write-through ghi cơ sở dữ liệu và bộ đệm cùng lúc, người gọi chờ cả hai; write-behind ghi bộ đệm rồi xếp hàng ghi cơ sở dữ liệu sau, nhanh nhưng có thể mất; write-around chỉ ghi cơ sở dữ liệu rồi xóa khóa cũ, quên xóa thì bộ đệm giữ bản cũ tới khi hết hạn. Phần ba, kết quả thử với Redis và SQLite: 100 lần đọc theo cache-aside chỉ đọc cơ sở dữ liệu 1 lần; người đọc chậm ghi bản cũ vào bộ đệm sau khi đã xóa, bộ đệm 100 trong khi cơ sở dữ liệu 120; write-through chờ 1,8 ms mỗi lần ghi vì phải ép xuống đĩa, write-behind 0,4 ms; bộ đệm không lưu đĩa sập trước khi đẩy thì write-behind mất cả 100 lần ghi.](../../diagrams/sd-06-026-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc dùng với cơ sở dữ liệu quan hệ; SQLite là một cơ sở dữ liệu SQL nằm gọn trong một tệp, dùng làm cơ sở dữ liệu gốc trong thử nghiệm.

## Đọc hình

**Đọc.** Với *cache-aside*, chính mã ứng dụng hỏi bộ đệm trước; không có thì đọc cơ sở dữ liệu, ghi kết quả vào bộ đệm rồi trả về. Với *read-through*, bộ đệm được cấu hình kèm một bộ nạp biết cách đọc cơ sở dữ liệu, nên ứng dụng chỉ nói chuyện với bộ đệm. Kết quả giống nhau; khác ở chỗ phần mã đọc cơ sở dữ liệu nằm ở đâu.

**Ghi.** *Write-through*: bộ đệm (hoặc mã ứng dụng) ghi vào cơ sở dữ liệu và cập nhật bộ đệm trong cùng một thao tác, người gọi chờ cả hai xong. *Write-behind* (còn gọi là write-back): ghi vào bộ đệm, còn việc ghi cơ sở dữ liệu được xếp hàng làm sau, nên người gọi đi tiếp sớm hơn nhưng cơ sở dữ liệu cập nhật trễ. *Write-around*: chỉ ghi cơ sở dữ liệu, không ghi vào bộ đệm, rồi *xóa* khóa đó trong bộ đệm nếu nó đang có (tài liệu Microsoft gọi là "invalidate on write"); lần đọc sau nạp lại bản mới. Đây cũng là cách ghi hay đi cặp với cache-aside. Quên bước xóa thì bộ đệm giữ bản cũ tới khi hết hạn, như thử nghiệm dưới đây cho thấy.

**Kết hợp.** Tài liệu Ehcache gọi read-through cùng write-through hoặc write-behind là dùng bộ đệm như thể nó là nơi lưu chính: mã ứng dụng gọn hơn, và bộ đệm có thể chặn cảnh nhiều yêu cầu cùng lúc đổ vào cơ sở dữ liệu cho một khóa vừa hết hạn. Bài [Năm chiến lược giữ bộ nhớ đệm khớp với cơ sở dữ liệu](../sd-06-008/lesson.md) nhìn cùng câu hỏi từ phía giữ bộ đệm và cơ sở dữ liệu khớp nhau.

**Thử nghiệm.**

- Cache-aside: 100 lần đọc giá một sản phẩm, cơ sở dữ liệu chỉ bị đọc 1 lần.
- Một thứ tự xấu của cache-aside, chạy từng bước bằng tay: người đọc hụt bộ đệm và đọc giá cũ 100; người ghi sửa giá thành 120 rồi xóa khóa; người đọc lúc này mới ghi 100 vào bộ đệm. Kết quả: cơ sở dữ liệu 120, bộ đệm 100, và giữ nguyên cho tới khi hết hạn sau 300 giây.
- Write-around mà quên xóa khóa: sửa giá trong cơ sở dữ liệu thành 130 mà không đụng bộ đệm; bộ đệm vẫn trả 120.
- Thời gian người gọi phải chờ (trung vị 200 lần): write-through (commit SQLite với `synchronous=FULL` cộng một lệnh Redis) khoảng 1 776 µs; write-behind (một lệnh ghi Redis cộng một lệnh xếp hàng) khoảng 382 µs.
- Write-behind: xếp 100 lần ghi vào hàng đợi trong Redis (không bật lưu xuống đĩa), rồi giết Redis bằng `SIGKILL` trước khi đẩy xuống cơ sở dữ liệu. Sau khi khởi động lại: hàng đợi rỗng, bộ đệm trống, cơ sở dữ liệu vẫn là giá trước đó. Cả 100 lần ghi đã mất.

## Giới hạn cần nhớ

Không chiến lược nào giữ bộ đệm và cơ sở dữ liệu luôn khớp. Tài liệu kiến trúc của Microsoft nói rõ cache-aside không bảo đảm nhất quán: giữa lúc ghi và lần đọc sau, người đọc có thể thấy dữ liệu cũ, và một tiến trình khác sửa thẳng cơ sở dữ liệu thì bộ đệm không biết. Thời gian hết hạn là lưới an toàn cuối cùng. Write-behind nhanh nhất cho người ghi nhưng đặt dữ liệu chưa ghi vào tay bộ đệm: nếu hàng đợi chỉ nằm trong bộ nhớ của bộ đệm (như trong thử nghiệm, Redis không bật lưu xuống đĩa), bộ đệm sập là mất.

## Nhìn hình trả lời

Một trang thương mại điện tử dùng bộ đệm cho trang chi tiết sản phẩm. Họ muốn: (a) giá hiển thị không được cũ quá vài giây sau khi đổi giá; (b) không được mất đơn hàng nào. Theo hình, chọn chiến lược nào cho giá, và có nên dùng write-behind cho đơn hàng không?

<details>
<summary>Xem đáp án</summary>

Giá: cache-aside, khi đổi giá thì ghi cơ sở dữ liệu rồi xóa khóa. Thời gian hết hạn ngắn chỉ giới hạn tuổi của từng bản đệm, chưa đủ để bảo đảm "không cũ quá vài giây": người đọc chậm như trong thử nghiệm có thể cất lại giá cũ sau khi khóa vừa bị xóa, và bản cũ đó bắt đầu một hạn mới. Muốn có giới hạn chắc chắn thì lượt nạp phải phối hợp với lượt ghi, chẳng hạn gắn số phiên bản cho giá và chỉ cất vào bộ đệm khi phiên bản đọc được vẫn là mới nhất (bài [Năm chiến lược giữ bộ nhớ đệm khớp với cơ sở dữ liệu](../sd-06-008/lesson.md) bàn kỹ chuyện này). Write-through giúp người đọc thấy giá mới ngay sau lần ghi khi cả hai lần ghi đều thành công.
Đơn hàng: không nên dùng write-behind với một bộ đệm có thể mất dữ liệu; thử nghiệm cho thấy bộ đệm không lưu xuống đĩa mà sập là mất cả hàng đợi. Đơn hàng phải được ghi bền vào cơ sở dữ liệu (hoặc một hàng đợi có lưu bền) trước khi báo cho khách là đã đặt xong.

</details>

<details>
<summary>Xem sâu hơn: các cách giảm thứ tự xấu của cache-aside</summary>

- Thời gian hết hạn giới hạn tuổi của từng bản đệm, không giới hạn tổng thời gian dữ liệu sai: một lượt nạp chậm có thể cất lại bản cũ với một hạn mới. Tài liệu Microsoft khuyên chọn thời gian hết hạn hợp với cách dữ liệu được dùng, không quá ngắn để khỏi đọc cơ sở dữ liệu liên tục.
- Muốn chặn hẳn việc cất lại bản cũ thì lượt nạp phải kiểm xem dữ liệu đã đổi chưa trước khi cất, chẳng hạn bằng số phiên bản; tài liệu Microsoft gọi cách kiểm trước khi cập nhật là cách lạc quan (optimistic).
- Write-through cập nhật bộ đệm ngay trong lần ghi, nên khi cả hai lần ghi đều thành công, người đọc sau lần ghi thấy bản mới; cái giá là mỗi lần ghi phải chờ cả hai nơi (1,8 ms so với 0,4 ms trong thử nghiệm).
- Bài nguồn nói một số chiến lược dùng chung được với nhau; theo Ehcache, cách ghép phổ biến là read-through với write-through hoặc write-behind.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-top-caching-strategies.md): năm chiến lược, hai cho đọc và ba cho ghi.
- [Ehcache 3 — Cache Usage Patterns, tại commit cố định](https://github.com/ehcache/ehcache3/blob/efea774551dcfdcfe54ec105dcfbfd70a42d8b6b/docs/src/docs/asciidoc/user/caching-patterns.adoc): cache-aside, read-through, write-through, write-behind, và cách dùng bộ đệm như nơi lưu chính.
- [Microsoft Azure Architecture Center — Cache-Aside pattern, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/patterns/cache-aside-content.md): ghi cơ sở dữ liệu rồi xóa khóa, thời gian hết hạn, không bảo đảm nhất quán, dữ liệu cũ sau khi ghi.
- [Microsoft Azure Architecture Center — Caching guidance, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/best-practices/caching.md): xóa khóa khi ghi (invalidate on write), write-through, kiểm dữ liệu đã đổi chưa trước khi cập nhật (cách lạc quan).

Thử nghiệm chạy ngày 2026-10-18 với Redis 7.0.15 (gói Ubuntu, thư viện redis-py 8.1.0) và SQLite 3.45.1 trên một máy; thứ tự xấu của cache-aside được chạy tuần tự từng bước để thấy kết quả, không phải bắt được trong lúc chạy song song. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

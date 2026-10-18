# Những điều cần cân nhắc khi dùng bộ nhớ đệm

**Bộ nhớ đệm làm hệ thống nhanh hơn khi dữ liệu được đọc lại nhiều lần và được phép cũ một lúc. Trước khi thêm, hãy hỏi: dữ liệu có hợp không, đo bằng gì, và thêm bộ nhớ thì được thêm bao nhiêu.**
Câu hỏi cuối thường bị bỏ qua: một phép thử nhỏ trên Redis cho thấy tới một mức nào đó, thêm bộ nhớ không mua thêm được gì.

![Ba khung. Khung một, khi nào đáng dùng: dữ liệu được đọc nhiều hơn ghi; dữ liệu ít đổi hoặc được phép cũ một lúc; mất bộ nhớ đệm thì vẫn nạp lại được từ kho chính. Khung hai, đo gì: tỷ lệ trúng; số khóa bị đẩy ra; bộ nhớ đã dùng so với giới hạn; lệnh ghi bị từ chối khi đầy. Khung ba, thử trên Redis với truy cập lệch: 2 MB trúng 63 phần trăm, 4 MB trúng 79 phần trăm, 8 MB trúng 88 phần trăm, 16 MB vẫn 88 phần trăm vì phần trượt còn lại là lần nạp đầu tiên; truy cập đều, 4 MB chỉ trúng 29 phần trăm.](../../diagrams/sd-06-009-main.svg)

## Từ viết tắt

- **MB** (MegaByte) — megabyte: đơn vị dung lượng cỡ một triệu byte; ở đây là giới hạn bộ nhớ đặt cho Redis.
- **TTL** (Time To Live) — thời gian sống: số giây một khóa được giữ trước khi tự hết hạn.
- **OOM** (Out Of Memory) — hết bộ nhớ: lỗi Redis trả về khi đã chạm giới hạn mà không được phép xóa bớt khóa.

## Đọc hình

**Khi nào đáng dùng.** Hướng dẫn về bộ nhớ đệm của Microsoft nói bộ nhớ đệm hợp nhất với dữ liệu được đọc thường xuyên mà ít thay đổi; dữ liệu đổi liên tục thì bản đệm cũ nhanh, hoặc công giữ nó khớp với kho chính ăn hết lợi ích. Cùng hướng dẫn đó khuyên coi bộ nhớ đệm là kho tạm có thể biến mất bất cứ lúc nào: dữ liệu quý phải nằm ở kho chính.

**Đo gì.** Tài liệu eviction của Redis chỉ ra các số đo có sẵn trong lệnh `INFO`: `keyspace_hits` và `keyspace_misses` (tỷ lệ trúng là hits chia cho hits cộng misses), `evicted_keys` (số khóa bị đẩy ra vì đầy), bộ nhớ đã dùng, và số lệnh bị từ chối vì giới hạn bộ nhớ. Tỷ lệ trúng thấp hơn dự đoán thì xem tiếp số khóa bị đẩy ra và số khóa hết hạn để biết vì sao.

**Hạn sống và khởi động nguội.** Hạn sống (TTL) quá ngắn làm khóa biến mất trước khi kịp được dùng lại; quá dài thì dữ liệu cũ lâu. Khi bộ nhớ đệm vừa khởi động, mọi lượt đọc đều trượt và dồn về kho chính; hướng dẫn của Microsoft gợi ý nạp sẵn (seed) bộ nhớ đệm để giảm tải cho kho chính lúc cao điểm.

## Thử: thêm bộ nhớ, trúng thêm bao nhiêu

Ngày 2026-10-18, trên một máy, bài chạy Redis 7.0.15 với chính sách `allkeys-lru` và đọc 60.000 lần theo kiểu cache-aside (trượt thì ghi giá trị 1.000 byte vào). Có 10.000 khóa, truy cập lệch: vài khóa rất hay được hỏi, phần lớn ít khi được hỏi (phân bố Zipf). Đổi giới hạn `maxmemory`:

| Giới hạn | Tỷ lệ trúng | Khóa bị đẩy ra | Khóa còn trong Redis |
|---|---|---|---|
| 2 MB | 63% | 21.024 | 1.032 |
| 4 MB | 79% | 9.620 | 2.951 |
| 8 MB | 88% | 549 | 6.805 |
| 16 MB | 88% | 0 | 7.298 |

Từ 8 MB lên 16 MB không trúng thêm: không còn khóa nào bị đẩy ra, phần trượt còn lại là lần đầu tiên mỗi khóa được hỏi, và không bộ nhớ đệm nào tránh được lượt đó. Với truy cập **đều** trên 10.000 khóa, 4 MB chỉ trúng 29%: bộ nhớ đệm giúp nhiều khi truy cập lệch, ít khi truy cập rải đều.

Thử thêm chính sách `noeviction` ở 4 MB: tỷ lệ trúng trông vẫn tốt (80%), nhưng 8.981 lệnh ghi bị từ chối với lỗi OOM. Nhìn mỗi tỷ lệ trúng thì không thấy lỗi này; phải đo cả lệnh bị từ chối.

## Giới hạn cần nhớ

Tỷ lệ trúng phụ thuộc kiểu truy cập của chính hệ thống bạn; con số ở trên là của một tập dữ liệu thử. Đo trên lưu lượng thật trước khi chọn kích thước, và nhớ rằng bộ nhớ đệm thêm một nơi dữ liệu có thể cũ và một hệ thống nữa phải vận hành.

## Nhìn hình trả lời

Bộ nhớ đệm của bạn trúng 70%. Đồng nghiệp đề nghị gấp đôi bộ nhớ. Bạn nên xem những gì trong cấu hình và trong `INFO` trước khi đồng ý?

<details>
<summary>Xem đáp án</summary>

Trước hết xem chính sách (`maxmemory-policy`) và bộ nhớ đã dùng so với giới hạn. Với `noeviction`, hoặc một chính sách `volatile` khi không khóa nào có hạn, `evicted_keys` luôn bằng 0 dù bộ nhớ đã đầy; khi đó hãy xem số lệnh bị từ chối (phần `commandstats`), như 8.981 lệnh bị từ chối trong thử nghiệm ở trên: thêm bộ nhớ có thể giúp.
Với chính sách có đẩy khóa ra, xem `evicted_keys` *tăng* bao nhiêu trong một khoảng thời gian tiêu biểu (số này cộng dồn từ lúc khởi động, nên con số lớn có thể chỉ là chuyện cũ). Nếu nó tăng nhanh, khóa đang bị đẩy ra trước khi kịp dùng lại, nên thêm bộ nhớ có thể giúp, như từ 2 MB lên 8 MB trong thử nghiệm. Nếu nó gần như không tăng, thêm bộ nhớ gần như không giúp (như từ 8 MB lên 16 MB): phần trượt đến từ lần nạp đầu hoặc từ khóa hết hạn; khi đó xem `expired_keys` và hạn sống của khóa.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn liệt kê năm nhóm điều cần cân nhắc: tình huống phù hợp, các kỹ thuật đọc ghi, các thuật toán đẩy khóa ra, các số đo và vài vấn đề khác. Bài này giữ ba câu hỏi chính và thêm một thử nghiệm về điều bài nguồn không nói: tới một mức, thêm bộ nhớ không thêm lượt trúng.
Các kỹ thuật đọc ghi và thuật toán đẩy khóa ra có bài riêng trong nhóm này nên không nhắc lại ở đây. Phép thử dùng một tập khóa giả lập với phân bố Zipf mũ 1; kết quả là của một máy.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/things-to-consider-when-using-cache.md): năm nhóm điều cần cân nhắc khi dùng bộ nhớ đệm.
- [Microsoft — hướng dẫn về bộ nhớ đệm, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/best-practices/caching.md): dữ liệu nào hợp để đệm; coi bộ nhớ đệm là kho tạm; nạp sẵn để giảm tải lúc cao điểm.
- [Redis — tài liệu eviction, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/reference/eviction/index.md): `maxmemory`, các chính sách, và cách dùng `INFO` (`keyspace_hits`, `keyspace_misses`, `evicted_keys`, `expired_keys`) để đánh giá bộ nhớ đệm.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày với Redis 7.0.15. Bài viết và hình được thiết kế độc lập.

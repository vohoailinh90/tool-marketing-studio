# Các chính sách đẩy khóa ra khỏi bộ nhớ đệm

**Bộ nhớ đệm đầy thì phải bỏ bớt một khóa để chỗ cho khóa mới. Chính sách đẩy khóa ra (eviction) quyết định bỏ khóa nào, và không có chính sách nào thắng ở mọi kiểu truy cập.**
Bài này mô phỏng năm chính sách trên ba kiểu truy cập, để thấy mỗi chính sách hợp và hỏng ở đâu.

![Bốn khung. Khung một, năm chính sách: TTL bỏ khóa hết hạn bất kể có dùng không; LRU bỏ khóa lâu nhất chưa dùng; LFU bỏ khóa ít được dùng nhất; MRU bỏ khóa vừa dùng xong; SLRU cho khóa mới vào vùng thử, dùng lại mới lên vùng được bảo vệ. Khung hai, mô phỏng truy cập lệch: LFU và SLRU trúng 65,5 phần trăm, LRU 57,9, FIFO và ngẫu nhiên khoảng 52, MRU 12,6. Khung ba, lặp vòng 120 khóa: LRU, LFU, FIFO và SLRU trúng 0, MRU 83, ngẫu nhiên 69. Khung bốn, nhóm khóa nóng lẫn khóa chỉ dùng một lần: LFU và SLRU 70 phần trăm, đúng mức tối đa; LRU 64; MRU gần 1.](../../diagrams/sd-06-010-main.svg)

## Từ viết tắt

- **TTL** (Time To Live) — thời gian sống: mỗi khóa có một hạn, hết hạn thì bị bỏ.
- **LRU** (Least Recently Used) — ít được dùng gần đây nhất: bỏ khóa đã lâu nhất không ai đụng tới.
- **LFU** (Least Frequently Used) — ít được dùng nhất: bỏ khóa có số lần dùng thấp nhất.
- **MRU** (Most Recently Used) — vừa được dùng gần đây nhất: bỏ chính khóa vừa được dùng.
- **SLRU** (Segmented Least Recently Used) — LRU chia vùng: khóa mới vào vùng thử, được dùng lại thì lên vùng bảo vệ, mỗi vùng tự bỏ theo LRU.
- **FIFO** (First In, First Out) — vào trước ra trước: bỏ khóa được nạp vào sớm nhất, bất kể có được dùng hay không.

## Đọc hình

**TTL** không thật sự là một cách chọn khóa khi đầy: khóa hết hạn thì đi, kể cả khóa đang được dùng nhiều. Bốn chính sách còn lại chọn khóa để bỏ khi đầy, mỗi cái đặt cược vào một điều khác nhau:

- **LRU** cược rằng khóa vừa dùng sẽ sớm được dùng lại.
- **LFU** cược rằng khóa hay được dùng sẽ còn hay được dùng. Nó phải đếm số lần dùng của từng khóa.
- **MRU** cược ngược lại: khóa vừa dùng xong sẽ lâu nữa mới cần lại, như khi đọc lần lượt một tệp lớn.
- **SLRU** muốn giữ khóa đã chứng tỏ được dùng lại khỏi bị khóa chỉ dùng một lần đẩy ra. memcached dùng đúng ý này: tài liệu của nó chia LRU thành các vùng nóng, ấm, lạnh, với mục tiêu chính là bảo vệ các khóa đang dùng khỏi việc quét lướt qua.

## Mô phỏng

Ngày 2026-10-18, bài viết một chương trình Python mô phỏng bộ đệm chứa 100 khóa, cho 100.000 lượt truy cập theo ba kiểu, và đếm tỷ lệ trúng. FIFO và chọn ngẫu nhiên được thêm vào để so sánh; SLRU dành 80% chỗ cho vùng bảo vệ.

Ba cột là ba kiểu truy cập: **lệch** (1.000 khóa, phân bố Zipf), **lặp vòng** 120 khóa, và **nóng lẫn một lần** (70% lượt vào 50 khóa nóng, 30% vào khóa chỉ dùng một lần).

| Chính sách | Lệch | Lặp vòng | Nóng lẫn một lần |
|---|---|---|---|
| LRU | 57,9% | 0% | 64,4% |
| LFU | 65,5% | 0% | 70,0% |
| FIFO | 52,4% | 0% | 52,3% |
| Ngẫu nhiên | 52,3% | 68,5% | 52,6% |
| MRU | 12,6% | 83,1% | 1,3% |
| SLRU | 65,5% | 0% | 70,0% |

Ba điều rút ra:

1. **Truy cập lệch** (vài khóa rất nóng): LFU và SLRU giữ được khóa nóng tốt nhất; MRU tệ nhất vì bỏ đúng khóa nóng.
2. **Lặp vòng lớn hơn bộ đệm**: LRU luôn bỏ đúng khóa sắp được hỏi lại, nên không trúng lần nào. MRU và chọn ngẫu nhiên lại tốt. Tài liệu eviction của Redis cũng khuyên dùng chọn ngẫu nhiên khi mọi khóa được truy cập gần như đều nhau, như khi đọc dữ liệu theo vòng lặp.
3. **Khóa dùng một lần lẫn vào**: chúng đẩy khóa nóng ra khỏi LRU (64,4%), còn LFU và SLRU chạm mức tối đa 70% (chỉ 70% lượt hỏi là khóa nóng, có thể trúng).

## Giới hạn cần nhớ

Đây là mô phỏng chính xác từng thuật toán trên dữ liệu giả lập. Hệ thống thật như Redis dùng bản xấp xỉ của LRU và LFU để tiết kiệm bộ nhớ, và LFU thật có cơ chế giảm dần số đếm để thích nghi khi kiểu truy cập đổi; LFU thuần trong mô phỏng không có cơ chế đó. Hãy chọn chính sách theo kiểu truy cập thật của hệ thống, và đo tỷ lệ trúng sau khi đổi.

## Nhìn hình trả lời

Một tác vụ đêm đọc lần lượt toàn bộ 1 triệu sản phẩm một lần để xuất báo cáo, trong khi ban ngày người dùng chủ yếu xem 2.000 sản phẩm bán chạy. Bộ đệm dùng LRU. Sáng hôm sau người dùng thấy trang chậm hẳn. Vì sao, và chính sách nào trong bảng hợp hơn?

<details>
<summary>Xem đáp án</summary>

Tác vụ đêm nạp 1 triệu khóa chỉ dùng một lần; với LRU, mỗi khóa mới là khóa "vừa dùng", nên chúng đẩy hết 2.000 khóa bán chạy ra (giống dòng cuối của bảng, nhưng nặng hơn).
SLRU hoặc LFU hợp hơn: khóa bán chạy đã được dùng nhiều lần nằm ở vùng bảo vệ hoặc có số đếm cao, khóa của tác vụ đêm chỉ dùng một lần và bị bỏ trước. Cách khác là cho tác vụ đêm đọc thẳng cơ sở dữ liệu, không qua bộ đệm.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn, và cách mô phỏng</summary>

Bài nguồn mô tả năm chính sách và nói lựa chọn tùy bối cảnh. Bài này thêm một mô phỏng cho thấy bối cảnh đó trông như thế nào bằng con số, và đối chiếu hai kết luận của mô phỏng với tài liệu của Redis (chọn ngẫu nhiên cho truy cập theo vòng) và memcached (LRU chia vùng chống quét lướt).
Cách mô phỏng: mỗi chính sách là một hàm nhận chuỗi khóa và sức chứa, đếm lượt trúng. LFU phá hòa bằng khóa vào trước; chọn ngẫu nhiên dùng một bộ sinh số cố định để chạy lại cho cùng kết quả. Phân bố Zipf có mũ 1 trên 1.000 khóa.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/most-popular-cache-eviction.md): năm chính sách TTL, LRU, LFU, MRU, SLRU.
- [Redis — tài liệu eviction, tại commit cố định](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/reference/eviction/index.md): chọn ngẫu nhiên khi truy cập đều hoặc theo vòng; LRU và LFU của Redis là bản xấp xỉ; LFU có cơ chế giảm dần số đếm.
- [memcached — tài liệu LRU mới, tại bản 1.6.24](https://github.com/memcached/memcached/blob/1b3b8555734f9b7b8d979924c7f8d6cf82194ba8/doc/new_lru.txt): LRU chia vùng nóng, ấm, lạnh để bảo vệ khóa đang dùng khỏi việc quét lướt.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; mô phỏng chạy cùng ngày bằng Python 3.13. Bài viết và hình được thiết kế độc lập.

# Quadtree: chia bản đồ thành bốn ô để tìm quán gần bạn

**Quadtree chia một bản đồ thành bốn ô, ô nào còn quá đông thì chia tiếp thành bốn ô nhỏ hơn, và dừng khi mỗi ô chỉ còn vài trăm điểm.**
Tìm quán gần bạn khi đó là đi từ gốc xuống ô chứa bạn thay vì xét hàng triệu quán.

![Hai khung. Khung một, xây quadtree: cả bản đồ là gốc, ô nào có hơn 100 quán thì chia thành bốn ô con, lặp lại cho tới khi không ô nào hơn 100 quán. Khung hai, tìm quán gần bạn: đi từ gốc xuống ô lá chứa vị trí của bạn, nếu ô đủ 100 quán thì trả về, nếu thiếu thì lấy thêm quán từ các ô bên cạnh.](../../diagrams/sd-12-005-main.svg)

## Từ viết tắt

- **LBS** (Location-Based Service) — dịch vụ dựa trên vị trí: máy chủ trả lời câu hỏi kiểu "quán nào gần tôi"; quadtree của bài nằm trong bộ nhớ của từng máy chủ này.

## Đọc hình

**Xây cây.** Gốc là cả bản đồ. Nếu một ô chứa hơn 100 quán (con số ngưỡng của bài nguồn), nó được chia bằng hai đường kẻ giữa thành bốn ô con: trên trái, trên phải, dưới trái, dưới phải. Mỗi ô con lại được kiểm tra như vậy. Kết quả: nơi quán dày (trung tâm thành phố) cây chia sâu thành nhiều ô nhỏ, nơi quán thưa (đồng ruộng) cây dừng sớm với một ô to.

**Tìm quán gần.** Từ gốc, ở mỗi nút chọn ô con chứa vị trí của bạn, đi xuống tới ô lá. Ô lá giữ danh sách quán của nó. Nếu chưa đủ số cần, lấy thêm từ các ô lá kề bên.

**Quadtree nằm trong bộ nhớ, không phải một cơ sở dữ liệu.** Mỗi máy chủ LBS tự dựng cây khi khởi động. Nên khi phát hành bản mới, máy chủ phải dựng lại cây trước khi nhận việc, và bài nguồn khuyên đưa bản mới lên từng nhóm nhỏ máy chủ một để không làm cả cụm ngừng phục vụ cùng lúc.

## Thử nghiệm: ô lá thường chứa bao nhiêu quán?

Ngày 2026-10-19, người biên soạn viết một chương trình Python dựng quadtree (chia khi một ô có hơn 100 điểm), trên các điểm ngẫu nhiên trong một hình vuông. Hai kiểu dữ liệu: **đều** (điểm rải đều) và **cụm** (20 "thành phố", điểm tụ quanh mỗi nơi theo phân bố chuẩn). Sau đó chọn 2.000 điểm ngẫu nhiên làm vị trí tìm kiếm, và đếm những lần ô lá chứa nó có ít hơn 100 điểm.

| Dữ liệu | Số điểm | Số ô lá | Độ sâu lớn nhất | Số điểm trung bình mỗi lá | Lần tìm rơi vào lá dưới 100 điểm |
|---|---|---|---|---|---|
| Đều | 100.000 | 2.221 | 6 | 45,0 | 95,8% |
| Đều | 1.000.000 | 16.384 | 7 | 61,0 | 100% |
| Cụm | 100.000 | 2.668 | 11 | 37,5 | 99,2% |
| Cụm | 1.000.000 | 21.583 | 13 | 46,3 | 99,3% |

Ba điều rút ra. Một: vì một ô chỉ bị chia khi vượt 100 điểm, hầu hết ô lá có *ít hơn* 100 điểm, nên bước "lấy thêm từ ô bên cạnh" gần như là trường hợp thường chứ không phải ngoại lệ. Hai: dữ liệu càng tụ thì cây càng sâu (độ sâu lớn nhất 13 với dữ liệu cụm so với 7 với dữ liệu đều ở cùng một triệu điểm), nhưng vẫn rất nông so với số điểm. Ba: dựng cây cho một triệu điểm mất khoảng 3,5 giây (đều) và 4,8 giây (cụm) bằng Python thuần trên máy của phiên viết bài; con số này chỉ cho thấy việc dựng là một lần duyệt qua mọi điểm, không so được với máy chủ thật và không dùng để suy ra thời gian cho 200 triệu quán.

## Giới hạn cần nhớ

Quadtree của bài là loại chia theo ngưỡng số điểm (người ta gọi là quadtree chứa theo "xô"); khái niệm quadtree thì rộng hơn, và bài báo gốc về cây bốn nhánh cho dữ liệu nhiều chiều là của Finkel và Bentley năm 1974. Bài nguồn nói dựng cây với 200 triệu quán mất "vài phút"; bài này không kiểm chứng con số đó. Thử nghiệm trên chỉ đo hình dạng của cây, chưa đo tốc độ tìm kiếm, chưa xử lý trường hợp vị trí nằm sát đường biên giữa hai ô, và dữ liệu cụm là dữ liệu giả, không phải bản đồ quán thật.

## Nhìn hình trả lời

Bạn cần đúng 100 quán gần nhất nhưng ô lá chứa bạn chỉ có 40. Chỉ lấy thêm toàn bộ quán của các ô kề bên có đủ để bảo đảm 100 quán *gần nhất* không?

<details>
<summary>Xem đáp án</summary>

Không đủ để bảo đảm. Ô kề bên có thể chứa quán gần hơn một quán trong ô của bạn (khi bạn đứng sát biên), và quán gần hơn có thể nằm ở một ô không kề. Cách làm trong bài cho 100 quán *ở gần*, đủ tốt cho việc "quán quanh đây"; muốn đúng tuyệt đối cần sắp xếp theo khoảng cách thật và có thể phải xét thêm ô.
Đây là suy luận của người biên soạn; nguồn mô tả cách làm đơn giản và không nói về độ chính xác của nó.

</details>

<details>
<summary>Xem sâu hơn: điều đã bổ sung so với bài nguồn</summary>

Bài nguồn có hai hình, định nghĩa quadtree, ba bước tìm quán gần và đoạn cập nhật máy chủ. Bài này giữ các ý đó và thêm một thử nghiệm để thấy một ô lá thực tế chứa bao nhiêu điểm và cây sâu tới đâu với hai kiểu dữ liệu.
Mã nguồn của thử nghiệm không nằm trong kho; bảng ở trên chạy với hạt giống ngẫu nhiên cố định 7.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/quadtree.md): định nghĩa quadtree, ngưỡng 100 quán, cách tìm quán gần và chuyện cập nhật máy chủ.
- R. A. Finkel và J. L. Bentley, "Quad trees: a data structure for retrieval on composite keys", Acta Informatica, 1974: bài báo gốc của cấu trúc này (nhớ lại tên; chưa mở được trang trong phiên này).

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

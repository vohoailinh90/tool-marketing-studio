# Chia theo cột và chia theo hàng: hai cách cắt dữ liệu khác hẳn nhau

**Chia theo chiều dọc cắt bảng thành các nhóm cột; chia theo chiều ngang (sharding) cắt bảng thành các nhóm hàng. Hai cách giải hai bài toán khác nhau.**
Biết mình đang cắt theo chiều nào, bạn biết khi nào dữ liệu vẫn nằm cùng chỗ và khi nào một truy vấn phải đi nhiều nơi.

![Hai khung. Khung một, hai cách cắt một bảng: chiều dọc giữ mỗi nhóm cột ở một nơi, chiều ngang giữ mỗi nhóm hàng ở một nơi. Khung hai, chọn nơi cho một hàng: theo khoảng giá trị khóa hoặc theo băm khóa, với điều mỗi cách làm tốt và làm kém.](../../diagrams/sd-11-005-main.svg)

## Đọc hình

Tên các mục giữ theo bài nguồn; lời giải thích và thử nghiệm là của người biên soạn.

**Vertical partitioning (chia theo chiều dọc).** Tách các cột của một bảng ra các bảng hoặc máy khác nhau, ví dụ cột hay đọc (tên, giá) ở một nơi và cột nặng ít đọc (mô tả dài, ảnh) ở nơi khác. Mỗi hàng vẫn xuất hiện ở cả hai nơi, nối với nhau bằng khóa. Lợi: truy vấn hay dùng chỉ chạm phần nhỏ. Giá: lấy đủ một hàng thì phải ghép lại từ nhiều nơi.

**Horizontal partitioning, hay sharding (chia theo chiều ngang).** Mỗi mảnh giữ trọn vẹn một số hàng, mọi cột. Lợi: dữ liệu và lượt ghi được chia đều cho nhiều máy. Giá: truy vấn cần nhiều hàng ở nhiều mảnh phải hỏi nhiều nơi rồi gộp.

**Routing algorithm (thuật toán định tuyến).** Muốn tìm một hàng, hệ thống phải biết mảnh nào giữ nó, bằng một quy tắc tính từ khóa.

**Range-based sharding (chia theo khoảng).** Mỗi mảnh giữ một dải khóa liền nhau (A tới F, G tới M...). Lợi: truy vấn theo dải chỉ đi vài mảnh. Giá: khóa tăng dần, như thời gian, dồn ghi mới vào một mảnh duy nhất ("điểm nóng").

**Hash-based sharding (chia theo băm).** Mảnh được chọn bằng cách băm khóa rồi lấy phần dư khi chia cho số mảnh. Lợi: dữ liệu rải đều. Giá: truy vấn theo dải phải hỏi mọi mảnh, và đổi số mảnh làm nhiều khóa đổi nơi.

**Thử nghiệm: đổi số mảnh làm bao nhiêu khóa phải chuyển?** Lấy 100 000 khóa số nguyên từ 0 đến 99 999, băm mỗi khóa bằng hàm `md5`, rồi so mảnh khi tính `băm mod 4` với `băm mod 5`. Kết quả tính được: 80,0% khóa đổi mảnh. Cùng bộ khóa, từ 4 lên 8 mảnh có 49,9% đổi, từ 10 lên 11 mảnh có 90,9% đổi. Với vòng băm nhất quán (mỗi mảnh giữ 200 điểm trên vòng), thêm mảnh thứ năm vào bốn mảnh chỉ làm khoảng 22% khóa đổi chỗ (20 000 khóa đầu, con số lý thuyết là một phần năm). Bài này không lưu mã của thử nghiệm; nếu muốn lặp lại, các bước trên đủ để viết lại.

## Giới hạn cần nhớ

"Chia theo chiều dọc" còn dùng với nghĩa khác: tăng cấu hình một máy (thêm bộ nhớ, bộ xử lý). Trong bài này nó chỉ nghĩa cắt cột. Con số trong thử nghiệm phụ thuộc vào hàm băm và bộ khóa đã nêu; chúng cho thấy cỡ lớn, không phải mọi hệ thống sẽ ra đúng 80%. Bài không so sánh với tài liệu của một cơ sở dữ liệu cụ thể (mỗi sản phẩm có cách định tuyến riêng) và không đối chiếu được tài liệu chính thức nào trong phiên viết.

## Nhìn hình trả lời

Bảng đơn hàng có cột ghi chú rất dài, ít ai đọc, làm truy vấn danh sách chậm. Cắt theo chiều nào là hợp, và nếu cần khóa theo thời gian để tra theo ngày thì chia theo khoảng có vấn đề gì?

<details>
<summary>Xem đáp án</summary>

Cắt theo chiều dọc: tách cột ghi chú sang nơi khác, để truy vấn danh sách chỉ đọc các cột nhỏ. Nếu sau này chia theo chiều ngang bằng khoảng thời gian thì tra theo ngày rất nhanh (chỉ đi một mảnh), nhưng đơn mới luôn rơi vào mảnh của ngày hiện tại, nên mảnh đó nhận gần như toàn bộ lượt ghi. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê hai kiểu chia, thuật toán định tuyến, hai cách chia theo khoảng và theo băm, rồi lợi và hại. Bài này giữ tên các mục, nhưng thay phần liệt kê lợi hại bằng cặp "lợi, giá" ở từng mục và thêm một thử nghiệm đo tác động của việc đổi số mảnh.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/vertical-partitioning-vs-horizontal-partitioning.md): chỉ lấy tên các mục. Lời giải thích và thử nghiệm là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức.

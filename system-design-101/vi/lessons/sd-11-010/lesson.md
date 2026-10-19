# Giây nhuận: vì sao nhiều công ty lớn muốn thoát khỏi nó

**Giây nhuận làm một phút có 61 giây. Với con người đó là chuyện nhỏ; với phần mềm giả định "một phút luôn có 60 giây" thì đó là mầm lỗi.**
Hiểu giây nhuận đến từ đâu và các hệ thống xử lý nó ra sao, bạn hiểu vì sao có người muốn bỏ hẳn.

![Hai khung. Khung một, vì sao có giây nhuận và nó gây lỗi gì: Trái Đất quay không đều so với đồng hồ nguyên tử, người ta chèn thêm một giây, phần mềm thấy giây thứ sáu mươi, các mốc thời gian có thể lặp hoặc lùi. Khung hai, ba cách đối phó: chèn đúng giây nhuận, làm mịn thành những lát nhỏ, hoặc bỏ giây nhuận.](../../diagrams/sd-11-010-main.svg)

## Đọc hình

Chủ đề giữ theo bài nguồn; phần giải thích là của người biên soạn.

**Vì sao có giây nhuận.** Đồng hồ nguyên tử chạy đều, còn Trái Đất quay hơi không đều. Để giờ dân sự không lệch dần khỏi vị trí Mặt Trời, thỉnh thoảng người ta chèn thêm một giây. Khi đó giây kế tiếp sau 23:59:59 là 23:59:60, không phải 00:00:00.

**Vì sao nó gây lỗi.** Phần mềm hay giả định mỗi phút có đúng 60 giây và thời gian không bao giờ lùi. Gặp giây thứ 61, mã có thể từ chối giá trị, hai sự kiện cách nhau một giây thật có thể mang cùng một mốc, hoặc một phép trừ thời gian cho ra số âm.

**Cách nhìn thời gian quyết định có phải lo hay không.** Giờ nguyên tử quốc tế và giờ của vệ tinh định vị chạy liên tục, không bao giờ chèn giây nhuận; thước có chèn là giờ dân sự quốc tế, nơi mới có 23:59:60, nên chênh lệch giữa giờ dân sự và hai thước kia đổi đi một giây mỗi lần chèn. Còn Unix timestamp phớt lờ giây nhuận, vì nó coi mỗi ngày dài đúng 86 400 giây. Với Unix timestamp, giây nhuận không có số riêng, nên hoặc một giây bị lặp, hoặc hệ thống phải làm điều gì đó để che.

**Ba cách đối phó.**

- *Chèn đúng giây nhuận.* Đúng chuẩn nhưng đụng toàn bộ phần mềm giả định phút 60 giây.
- *Làm mịn (smear).* Không có giây thứ 61; giây thừa được chia thành những lát rất nhỏ rải trong một khoảng dài, nên đồng hồ chạy chậm hơn chút ít rồi đuổi kịp. Đồng hồ ổn định, nhưng trong khoảng đó nó lệch nhẹ so với nguồn chuẩn.
- *Bỏ giây nhuận.* Không còn giây thừa để xử lý; đổi lại giờ dân sự dần lệch khỏi Mặt Trời, tới khi có người quyết định điều chỉnh bằng cách khác.

## Giới hạn cần nhớ

Bài này không nêu số liệu cụ thể (số giây nhuận đã chèn, thời hạn bỏ, độ dài khoảng làm mịn của từng công ty) vì chưa đối chiếu được với tài liệu của các tổ chức hay công ty đó trong phiên viết (không truy cập được ngoài GitHub). Việc bài nguồn đặt tên ba công ty lớn là thông tin từ bài nguồn, chưa được kiểm ở đây. Cách làm mịn cũng không thống nhất giữa các nơi.

## Nhìn hình trả lời

Hệ thống ghi sự kiện bằng Unix timestamp. Đúng lúc có giây nhuận, hai sự kiện cách nhau một giây thật lại mang cùng một mốc. Làm sao vẫn sắp đúng thứ tự?

<details>
<summary>Xem đáp án</summary>

Đừng dựa vào giờ tường để sắp thứ tự: gắn thêm một số thứ tự tăng dần do chính hệ thống cấp (hoặc đồng hồ logic) và dùng đồng hồ chỉ tiến, không bao giờ lùi, để đo khoảng thời gian. Giờ tường chỉ để con người đọc. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn kể về giây nhuận và liệt kê các cách biểu diễn thời gian. Bài này giữ chủ đề đó, tách thành hai phần (vì sao có và gây lỗi gì, ba cách đối phó) và thêm một câu hỏi về thứ tự sự kiện.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/do-you-know-why-meta-google-and-amazon-all-stop-using-leap-seconds.md): chủ đề giây nhuận và các cách biểu diễn thời gian. Phần giải thích là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập; phần giải thích là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chính thức.

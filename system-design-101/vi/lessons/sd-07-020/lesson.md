# Visa kiếm tiền thế nào: các khoản phí của một lần quẹt thẻ

**Thẻ tín dụng được gọi là sản phẩm sinh lời nhất của ngân hàng. Một lần quẹt thẻ 100 đô la kéo theo ba loại phí: người bán trả cho ngân hàng thu, ngân hàng thu chuyển một phần cho ngân hàng phát hành, và mỗi ngân hàng trả hằng tháng cho mạng thẻ như Visa.**

![Ba khung. Khung một, ba loại phí: phí chiết khấu người bán do ngân hàng thu đặt với người bán; phí liên ngân hàng do mạng thẻ đặt, trả cho ngân hàng phát hành; phí và đánh giá của mạng thẻ, mỗi ngân hàng trả hằng tháng. Khung hai, năm bước với ví dụ 100 đô la: chủ thẻ trả người bán 100 đô la; ngân hàng thu đặt phí chiết khấu; ngân hàng thu giữ 0,25 đô la và trả 1,75 đô la cho ngân hàng phát hành; mạng thẻ thu phí, ví dụ Visa thu 0,11 phần trăm cộng 0,0195 đô la mỗi lần quẹt; chủ thẻ trả ngân hàng phát hành. Khung ba, vì sao ngân hàng phát hành được trả: trả người bán dù chủ thẻ không trả, trả trước khi chủ thẻ trả, và có chi phí vận hành.](../../diagrams/sd-07-020-main.svg)

## Đọc hình

**Ba loại phí.**

- *Phí chiết khấu người bán* (merchant discount fee): do ngân hàng thu đặt với người bán. Người bán được lợi vì dùng thẻ làm doanh số cao hơn, nên phải bù cho ngân hàng phát hành và mạng thẻ vì dịch vụ thanh toán.
- *Phí liên ngân hàng* (interchange fee): khoản ngân hàng thu trả cho ngân hàng phát hành. Do mạng thẻ đặt, vì để từng ngân hàng phát hành đàm phán với từng người bán thì kém hiệu quả hơn nhiều. Phí chiết khấu người bán phải đủ bù khoản này.
- *Phí và đánh giá của mạng thẻ* (network assessments and fees): mạng thẻ thỏa thuận với từng ngân hàng và ngân hàng trả hằng tháng. Ví dụ của nguồn: Visa thu 0,11% phí đánh giá cộng 0,0195 đô la phí sử dụng cho mỗi lần quẹt.

**Năm bước với ví dụ 100 đô la.**
1. Chủ thẻ trả người bán 100 đô la để mua một món hàng.
2. Ngân hàng thu đặt phí chiết khấu với người bán.
3. và 4. Ngân hàng thu giữ 0,25 đô la, gọi là phụ phí của ngân hàng thu (acquiring markup), và 1,75 đô la được trả cho ngân hàng phát hành làm phí liên ngân hàng.
5. Mạng thẻ thu phí và đánh giá của các ngân hàng, như ví dụ Visa ở trên.
6. Chủ thẻ trả cho ngân hàng phát hành tiền dịch vụ của ngân hàng đó.

**Vì sao ngân hàng phát hành phải được trả.** Ngân hàng phát hành chuyển tiền cho phía người bán (qua mạng thẻ và ngân hàng thu, nơi ghi có cho người bán) ngay cả khi chủ thẻ không trả, và chuyển trước khi chủ thẻ trả nó; nguồn viết gọn là "trả người bán". Và nó có các chi phí vận hành khác: quản lý tài khoản khách hàng, in sao kê, phát hiện gian lận, quản lý rủi ro, bù trừ và quyết toán, v.v.

## Giới hạn cần nhớ

Nguồn đưa các con số như ví dụ, không nói đó là mức phí chung. Con số 0,25 đô la, 1,75 đô la, 0,11% và 0,0195 đô la là của nguồn, tại thời điểm nguồn viết; bài chưa kiểm tra chúng. Nguồn nêu hai phần (0,25 và 1,75) chứ không nêu tổng phí chiết khấu người bán; người biên soạn cộng lại ra 2 đô la, đó là phép tính của bài chứ không phải một số của nguồn, và việc người bán nhận về bao nhiêu thì nguồn không nói.
Nguồn kết bằng một câu hỏi mở: mạng thẻ có tính cùng mức phí liên ngân hàng cho người bán lớn và người bán nhỏ không? Nguồn không trả lời, bài này cũng không.

## Nhìn hình trả lời

Vì sao phí liên ngân hàng do mạng thẻ đặt, không để từng ngân hàng phát hành đàm phán với từng người bán? Và vì sao ngân hàng phát hành vẫn được trả dù chủ thẻ chưa trả?

<details>
<summary>Xem đáp án</summary>

Theo nguồn, để từng ngân hàng phát hành đàm phán phí với từng người bán thì kém hiệu quả hơn; nên mạng thẻ đặt mức phí liên ngân hàng chung.
Ngân hàng phát hành được trả vì nó chuyển tiền cho phía người bán (qua mạng thẻ và ngân hàng thu) ngay cả khi chủ thẻ không trả, chuyển trước khi chủ thẻ trả, và có chi phí vận hành như quản lý tài khoản, sao kê, chống gian lận, quản lý rủi ro, bù trừ và quyết toán.
Câu hỏi mở của nguồn (phí có như nhau cho người bán lớn và nhỏ?) nguồn không trả lời.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là hình kèm sáu bước và một danh sách ba lý do. Bài này đặt ba loại phí lên đầu để người đọc có từ ngữ trước khi đọc bước, gộp bước 3 và 4 làm một thẻ, và viết tên hãng là "Visa" thay cho chữ in hoa của nguồn. Phép cộng 0,25 và 1,75 chỉ có ở phần giới hạn, ghi rõ là của người biên soạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-visa-make-money.md): ba loại phí, ví dụ 100 đô la và các lý do ngân hàng phát hành được trả. Phần giới hạn và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

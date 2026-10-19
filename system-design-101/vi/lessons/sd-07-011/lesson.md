# Dòng tiền sau một đơn hàng: bù trừ và quyết toán

**Khi bạn mua hàng bằng PayPal hay thẻ ngân hàng, thông tin về khoản tiền chạy trước, còn tiền thật chỉ di chuyển sau, giữa các ngân hàng, ở ngân hàng quyết toán. Hai việc đó được tách ra.**
Hiểu hai từ "bù trừ" và "quyết toán" là hiểu được vì sao.

![Bốn khung. Khung một, Bob trả Amazon: Bob mua sách trên Amazon và chọn trả bằng PayPal, Amazon gửi PayPal yêu cầu chuyển tiền, PayPal chuyển tiền thay Bob vào tài khoản của Amazon ở ngân hàng A. Khung hai, bù trừ rồi quyết toán: ngân hàng A và B gửi sao kê cho tổ chức bù trừ, chỉ tính chênh lệch ròng, rồi tiền thật đi giữa hai quỹ dự trữ ở ngân hàng quyết toán. Khung ba, Amazon trả người bán: Amazon báo người bán, hai ngân hàng ghi sổ, rồi cũng bù trừ và quyết toán. Khung bốn, ba lớp: giao dịch, thanh toán và bù trừ, quyết toán; hai lớp đầu là dòng thông tin, lớp cuối là dòng tiền.](../../diagrams/sd-07-011-main.svg)

## Đọc hình

Hai từ cần phân biệt. **Bù trừ** (clearing) là việc tính ai phải trả ai và bao nhiêu. **Quyết toán** (settlement) là việc tiền thật di chuyển giữa các quỹ dự trữ đặt ở ngân hàng quyết toán. Ví dụ của nguồn: Bob muốn mua một cuốn sách của Claire, bán trên Amazon.

**1. Bob trả Amazon (luồng thu).** Bob mua sách trên Amazon và chọn trả bằng PayPal. Amazon gửi PayPal một yêu cầu chuyển tiền. Vì mã đại diện cho thẻ của Bob (payment token) được lưu ở PayPal, PayPal chuyển tiền thay Bob vào tài khoản của Amazon ở ngân hàng A.

**2. Bù trừ rồi quyết toán.** Ngân hàng A và ngân hàng B gửi sao kê giao dịch cho tổ chức bù trừ. Việc này làm giảm số giao dịch phải quyết toán: nếu cuối ngày A nợ B 100 đô la và B nợ A 500 đô la thì kết quả ròng là B trả A 400 đô la. Tổ chức bù trừ gửi thông tin bù trừ và quyết toán cho ngân hàng quyết toán. Cả A và B đã gửi trước một khoản tiền vào đó làm quỹ dự trữ, nên tiền thật chỉ di chuyển giữa hai tài khoản quỹ dự trữ ở ngân hàng quyết toán.

**3. Amazon trả người bán (luồng chi).** Amazon báo cho Claire biết cô sắp được trả, rồi gửi yêu cầu chuyển tiền từ ngân hàng của mình (A) sang ngân hàng của người bán (C). Hai ngân hàng ghi nhận giao dịch, nhưng chưa có tiền thật nào di chuyển. Rồi lại như trên: A và C gửi sao kê cho tổ chức bù trừ, tổ chức này gửi thông tin cho ngân hàng quyết toán, và tiền đi từ quỹ của A sang quỹ của C.

**Ba lớp, hai dòng.** Lớp giao dịch là nơi việc mua hàng diễn ra. Lớp thanh toán và bù trừ là nơi lệnh thanh toán được gửi đi và các giao dịch được tính bù trừ. Lớp quyết toán là nơi tiền thật di chuyển. Hai lớp đầu gọi là *dòng thông tin* (information flow), lớp cuối gọi là *dòng tiền* (fund flow). Trên dòng thông tin, tiền có vẻ đã trừ ở tài khoản này và cộng vào tài khoản kia, nhưng tiền thật chỉ di chuyển ở ngân hàng quyết toán vào cuối ngày.

Vì hai dòng chạy không đồng bộ, đối soát rất quan trọng để dữ liệu của các hệ thống dọc đường khớp nhau; nguồn nhắc ngay điều này ở cuối bài.

## Giới hạn cần nhớ

Nguồn kể một ví dụ gồm ba ngân hàng, một tổ chức bù trừ và một ngân hàng quyết toán; nó không nói mọi hệ thống thanh toán đều đi đúng như vậy, không nói bù trừ và quyết toán diễn ra bao lâu một lần, và không nói gì về phí. Cụm "cuối ngày" là của nguồn; bài không bổ sung giờ cụ thể.
Nguồn cũng chỉ nhắc tới trường hợp người mua trả đô la còn người bán chỉ nhận được một đồng tiền khác như một chuyện "thú vị hơn"; chi tiết ở bài về ngoại hối.

## Nhìn hình trả lời

Cuối ngày, ngân hàng A nợ ngân hàng B 100 đô la và ngân hàng B nợ ngân hàng A 500 đô la. Có cần chuyển 600 đô la thật qua lại không? Và tiền thật đó nằm ở đâu khi di chuyển?

<details>
<summary>Xem đáp án</summary>

Không. Sau bù trừ, chỉ còn một chênh lệch ròng: ngân hàng B trả ngân hàng A 400 đô la. Tiền thật đó di chuyển giữa hai tài khoản quỹ dự trữ mà A và B đã gửi sẵn ở ngân hàng quyết toán, chứ không đi trực tiếp giữa hai ngân hàng.
Nguồn dùng đúng số này làm ví dụ; còn việc bù trừ luôn cho ra một con số ròng cho mọi hệ thống thì nguồn không khẳng định.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một bức hình kèm hai danh sách bước (luồng thu và luồng chi) và lời giải thích ba lớp. Bài này vẽ luồng thu thành một lược đồ, gộp các bước sao kê, bù trừ và quyết toán của cả hai luồng thành hai khung thẻ, và để ba lớp ở cuối làm điểm tựa. Ví dụ cuốn sách đổi tên thành "một cuốn sách".

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/money-movement.md): hai luồng thu và chi, bù trừ, quyết toán, ba lớp, dòng thông tin và dòng tiền. Phần giới hạn và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

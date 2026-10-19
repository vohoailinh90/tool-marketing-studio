# Thanh toán ngoại tệ: 100 đô la thành 88 euro

**Khi người mua trả bằng đô la mà người bán ở châu Âu chỉ nhận euro, một bên trung gian phải đổi tiền: PayPal nhờ một ngân hàng ngoại hối, ngân hàng đó lấy euro từ quỹ tiền của mình, và quỹ này lại đi tìm euro ở một thị trường ba tầng.**
Quá trình này gọi là ngoại hối (foreign exchange).

![Ba khung. Khung một và hai, sáu bước: Bob gửi 100 đô la qua PayPal từ ngân hàng B; PayPal gửi 100 đô la tới tài khoản đô la của nó ở ngân hàng E, nơi đổi tiền; 100 đô la được bán vào quỹ tiền của ngân hàng E; quỹ trả 88 euro vào tài khoản euro của PayPal ở ngân hàng E; 88 euro về tài khoản euro của PayPal ở ngân hàng P2; PayPal trả 88 euro vào tài khoản euro của Alice ở ngân hàng A. Khung ba, thị trường ngoại hối có ba tầng: tầng bán lẻ, tầng bán buôn và các bên ở tầng trên cùng; khi quỹ cần thêm euro thì đi lên tầng trên.](../../diagrams/sd-07-015-main.svg)

## Đọc hình

Ví dụ của nguồn: Bob (người mua) cần trả 100 đô la cho Alice (người bán), mà Alice chỉ nhận được euro. Các ngân hàng được đặt tên bằng chữ cái để dễ đối chiếu: B là ngân hàng của Bob, P1 và P2 là hai ngân hàng nơi PayPal có tài khoản, E là ngân hàng ngoại hối, A là ngân hàng của Alice.

**Sáu bước.**
1. Bob gửi 100 đô la qua một bên thanh toán thứ ba; trong ví dụ là PayPal. Tiền đi từ tài khoản của Bob (ngân hàng B) tới tài khoản của PayPal ở ngân hàng P1.
2. PayPal cần đổi đô la sang euro nên dùng một nhà cung cấp ngoại hối là ngân hàng E. PayPal gửi 100 đô la tới tài khoản đô la của mình ở ngân hàng E.
3. 100 đô la được bán vào *quỹ tiền* (funding pool) của ngân hàng E.
4. Quỹ tiền của ngân hàng E trả 88 euro để đổi lấy 100 đô la. Số euro đó vào tài khoản euro của PayPal ở ngân hàng E.
5. Tài khoản euro của PayPal ở ngân hàng P2 nhận 88 euro.
6. 88 euro được trả vào tài khoản euro của Alice ở ngân hàng A.

**Thị trường ngoại hối có ba tầng.** *Tầng bán lẻ*: quỹ tiền là một phần của tầng này; để hiệu quả hơn, PayPal thường mua trước một lượng ngoại tệ nhất định. *Tầng bán buôn*: gồm ngân hàng đầu tư, ngân hàng thương mại và các nhà cung cấp ngoại hối, thường xử lý các lệnh đã gom lại từ tầng bán lẻ. *Tầng trên cùng*: các ngân hàng thương mại đa quốc gia, giữ rất nhiều tiền của nhiều nước.

Khi quỹ tiền của ngân hàng E cần thêm euro, nó đi lên tầng bán buôn để bán đô la và mua euro. Khi tầng bán buôn gom đủ lệnh, nó đi tiếp lên các bên ở tầng trên cùng.

## Giới hạn cần nhớ

Con số 88 euro cho 100 đô la là ví dụ của nguồn; nguồn không nêu tỷ giá, không nói phí đổi tiền và không nói quỹ tiền quyết định số euro trả ra bằng cách nào. Phép chia 88 cho 100 chỉ là phép tính của người biên soạn trên ví dụ này, không phải tỷ giá thật.
Nguồn cũng không nói PayPal chọn ngân hàng E ra sao, hay các ngân hàng P1, P2 khác nhau ở chỗ nào.

## Nhìn hình trả lời

Vì sao PayPal "thường mua trước một lượng ngoại tệ" thay vì chỉ đổi khi có khách trả? Và quỹ tiền cần thêm euro thì đi đâu?

<details>
<summary>Xem đáp án</summary>

Nguồn nói PayPal mua trước để hiệu quả hơn (to improve efficiency). Vì sao hiệu quả thì nguồn không giải thích; người biên soạn hiểu rằng có sẵn tiền thì khách trả là đổi được ngay, thay vì chờ một lượt mua riêng cho từng khách; đây là suy luận, chưa đối chiếu với tài liệu của một nhà cung cấp ngoại hối.
Khi quỹ cần thêm euro, nó đi lên tầng bán buôn để bán đô la và mua euro; khi tầng bán buôn gom đủ lệnh thì đi tiếp lên các bên ở tầng trên cùng.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là hình kèm danh sách sáu bước và đoạn mô tả ba tầng, với các bước phụ 3.1 đến 3.3 và 4.1 đến 4.3 chỉ có trên hình. Bài này giữ sáu bước nguyên văn thứ tự, vẽ ba tầng như một dãy đi lên, và đổi ký hiệu tiền tệ thành chữ "đô la", "euro".

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/foreign-exchange-payments.md): sáu bước đổi 100 đô la ra 88 euro và thị trường ngoại hối ba tầng. Phần giới hạn và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

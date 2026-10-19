# Quẹt thẻ tín dụng: Visa đứng ở đâu

**Khi bạn quẹt thẻ tín dụng ở cửa hàng, hai việc xảy ra ở hai thời điểm: ngay lúc quẹt, giao dịch được xin phép duyệt; cuối ngày, cửa hàng chốt và tiền mới được quyết toán. Mạng thẻ như Visa đứng giữa các ngân hàng để họ khỏi phải quyết toán từng cặp với nhau.**

![Bốn khung. Khung một, xin phép (bước 1 đến 3): máy POS gửi giao dịch cho ngân hàng thu, ngân hàng thu gửi cho mạng thẻ. Khung hai, xin phép (bước 4): mạng thẻ gửi cho ngân hàng phát hành để duyệt; ngân hàng phát hành giữ một phần hạn mức của thẻ nếu duyệt, rồi báo duyệt hoặc từ chối về ngân hàng thu và máy POS. Khung ba, cuối ngày: cửa hàng bấm chốt, lô giao dịch đi tới ngân hàng thu rồi mạng thẻ, mạng thẻ bù trừ và gửi tệp cho ngân hàng phát hành, ngân hàng phát hành xác nhận và chuyển tiền cho ngân hàng thu, ngân hàng thu chuyển cho ngân hàng của cửa hàng. Khung bốn, vai của mạng thẻ.](../../diagrams/sd-07-018-main.svg)

## Từ viết tắt

- **POS** (Point Of Sale) — điểm bán hàng: máy ở cửa hàng, nơi bạn quẹt thẻ.

## Đọc hình

Visa, Mastercard và American Express là các *mạng thẻ* (card network, còn gọi là card scheme) làm việc bù trừ và quyết toán tiền. Ngân hàng thu (acquiring bank, bên cung cấp máy POS cho cửa hàng) và ngân hàng phát hành (issuing bank, bên phát hành thẻ cho khách) có thể, và thường, là hai ngân hàng khác nhau. Nếu không có bên trung gian, mỗi ngân hàng phải quyết toán với mọi ngân hàng khác, rất kém hiệu quả.

**Luồng xin phép (authorization).** Xảy ra khi khách quẹt thẻ. Bước 0: ngân hàng phát hành cấp thẻ cho khách. Bước 1: khách muốn mua hàng và quẹt thẻ ở máy POS trong cửa hàng. Bước 2: máy POS gửi giao dịch tới ngân hàng thu. Bước 3 và 4: ngân hàng thu gửi giao dịch cho mạng thẻ, và mạng thẻ gửi cho ngân hàng phát hành để duyệt. Bước 4.1 đến 4.3: nếu duyệt, ngân hàng phát hành giữ chỗ số tiền đó trong hạn mức của thẻ (authorization hold); kết quả duyệt hoặc từ chối được gửi lại cho ngân hàng thu và cho máy POS.

**Luồng chốt và quyết toán (capture and settlement).** Cuối ngày, cửa hàng bấm "chốt" (capture) trên máy POS để lấy tiền. Các giao dịch được gửi cho ngân hàng thu theo lô, và ngân hàng thu gửi tệp lô cho mạng thẻ. Mạng thẻ bù trừ các giao dịch thu từ nhiều ngân hàng thu và gửi tệp bù trừ cho các ngân hàng phát hành. Các ngân hàng phát hành xác nhận tệp bù trừ đúng, rồi chuyển tiền cho các ngân hàng thu liên quan. Ngân hàng thu chuyển tiền cho ngân hàng của cửa hàng. Đây là cách nguồn vẽ; giản lược: trong thực tế mạng thẻ điều phối khâu quyết toán, tức là ghi có cho ngân hàng thu và ghi nợ tài khoản của ngân hàng phát hành qua hệ thống của mạng, nên tiền không đi thẳng từ ngân hàng phát hành sang ngân hàng thu.

**Bù trừ là gì.** Là quá trình các giao dịch bù qua lại cho nhau được cộng trừ với nhau (netting), nên các khoản phải chuyển giữa các ngân hàng thu gọn thành số dư ròng. Mỗi giao dịch vẫn phải được xử lý và bù trừ; cái giảm đi là số khoản quyết toán thật sự phải chuyển. Mạng thẻ nhận gánh nặng làm việc với từng ngân hàng và nhận phí dịch vụ để đổi lại.

## Giới hạn cần nhớ

Trong phần chốt và quyết toán, nguồn ghi "Bước 4" hai lần (một lần cho việc ngân hàng phát hành xác nhận và chuyển tiền, một lần cho lời giải thích về bù trừ ở dòng cuối). Bài này đọc theo thứ tự của chữ và xếp lời giải thích bù trừ vào khung riêng.
Nguồn không nói mức phí, không nói khoản giữ hạn mức kéo dài bao lâu, không nói ngày chuyển tiền thật sự có trùng ngày chốt hay không (người biên soạn lưu ý: ngày quyết toán thường là một ngày sau ngày chốt), và không nói chuyện gì xảy ra khi giao dịch bị từ chối sau khi đã chốt.

## Nhìn hình trả lời

Khi quẹt thẻ, tiền đã chuyển từ ngân hàng của khách sang cửa hàng chưa? Và vì sao mạng thẻ cần ở giữa thay vì để các ngân hàng quyết toán trực tiếp với nhau?

<details>
<summary>Xem đáp án</summary>

Chưa. Lúc quẹt chỉ có xin phép: ngân hàng phát hành chỉ giữ chỗ số tiền trong hạn mức của thẻ nếu duyệt, chưa chuyển tiền. Tiền chỉ được chuyển ở luồng chốt và quyết toán, bắt đầu từ lúc cửa hàng chốt cuối ngày (việc chuyển tiền có thể hoàn tất ở một ngày quyết toán sau đó), khi ngân hàng phát hành chuyển cho ngân hàng thu và ngân hàng thu chuyển cho ngân hàng của cửa hàng.
Mạng thẻ ở giữa vì nếu không, mỗi ngân hàng phải quyết toán với mọi ngân hàng khác; mạng thẻ gom, bù trừ rồi gửi tệp, nên các khoản phải chuyển giữa các ngân hàng thu gọn thành số dư ròng (từng giao dịch vẫn được xử lý), và nó nhận phí dịch vụ vì gánh việc đó.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn gồm hai danh sách bước (xin phép và chốt, quyết toán) và một đoạn giải thích bù trừ. Bài này vẽ luồng xin phép thành hai lược đồ ba bên, luồng cuối ngày thành bốn thẻ, và đưa lời giải thích về mạng thẻ thành khung cuối. Tên hãng viết hoa toàn bộ của nguồn được viết thành "Visa".

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-visa-work-when-we-swipe-a-credit-card-at-a-merchant's-shop.md): luồng xin phép, luồng chốt và quyết toán, vai của mạng thẻ. Phần giới hạn và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

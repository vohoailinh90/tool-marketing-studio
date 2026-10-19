# Ví số ở ngân hàng và ví trên blockchain

**Ví ở ngân hàng là một tài khoản trong sổ riêng của từng ngân hàng, còn ví trên blockchain là một địa chỉ trên một sổ cái chung. Khác nhau ở chỗ ai giữ sổ, tiền thật sự chuyển khi nào, và bạn phải mở ví bao nhiêu lần.**

![Ba khung. Khung một, ở ngân hàng: gửi tiền mở tài khoản riêng ở từng ngân hàng; chuyển khoản trừ và cộng ngay trong sổ nhưng tiền thật chuyển sau, khi hai ngân hàng đối chiếu cuối ngày; rút tiền trừ tài khoản và nhận tiền mặt. Khung hai, trên blockchain: tạo địa chỉ và giữ khóa riêng trong ví; chuyển bằng cách nhập địa chỉ người nhận và ký bằng khóa riêng; khi giao dịch được xác nhận, số dư hai địa chỉ đổi theo. Khung ba, điểm khác: một sổ cái chung thay cho nhiều sổ riêng, một địa chỉ thay cho nhiều tài khoản, xác nhận gần thời gian thực.](../../diagrams/sd-07-002-main.svg)

## Đọc hình

**Ở ngân hàng.** Bob đến Bank of America, mở tài khoản và gửi 100 đô la. Hệ thống ví của ngân hàng tạo tài khoản B1234 cho anh, tiền mặt vào kho của ngân hàng và ví của anh có 100 đô la. Nếu muốn dùng dịch vụ của Citibank, anh phải làm lại từ đầu.
Khi Bob dùng ứng dụng chuyển 50 đô la cho Alice, người có tài khoản C512 ở Citibank, sổ trừ 50 ở B1234 và cộng 50 vào C512 ngay. Nhưng tiền thật chưa di chuyển: nó chỉ di chuyển khi hai ngân hàng đối chiếu và thanh toán bù trừ mọi giao dịch vào cuối ngày. Cuối cùng Bob rút 50 còn lại: trừ B1234, anh nhận tiền mặt.

**Trên blockchain.** Không có tiền mặt, chỉ có tiền mã hóa. Bob tạo một địa chỉ làm nơi nhận và cất khóa riêng trong ví tiền mã hóa như Metamask. Để chuyển, anh nhập địa chỉ của Alice, gửi 2 ether và ký giao dịch bằng khóa riêng để cho phép chuyển.
Khi giao dịch được xác nhận trên blockchain, địa chỉ của Bob còn 8 ether và của Alice có 101 ether. Nguồn không nói số dư lúc đầu; con số 10 và 99 suy ra từ hai số cuối và số tiền chuyển.

**Điểm khác.** Blockchain là sổ cái phân tán, đưa ra một giao diện chung cho các thao tác thường làm với ví. Thay vì mở nhiều tài khoản ở nhiều ngân hàng, bạn chỉ cần một địa chỉ. Giao dịch được xác nhận gần như theo thời gian thực, khỏi chờ đối chiếu cuối ngày.
Từ đó nguồn cho rằng có thể gộp dịch vụ ví của nhiều ngân hàng thành một dịch vụ toàn cầu. Đó là nhận định của nguồn, không phải điều đã xảy ra.

## Giới hạn cần nhớ

Bài nguồn so sánh ở mức ý tưởng và không nhắc ba điều sau, vốn là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu của một blockchain cụ thể: giao dịch trên blockchain thường phải trả phí và vẫn cần thời gian để được xác nhận ("gần thời gian thực" không phải "tức thì"); khóa riêng do bạn tự giữ, nên mất khóa là mất quyền dùng địa chỉ đó; và con số của ví dụ (8 và 101 ether) không kể đến phí.
Ngân hàng cũng có điều blockchain không có: ngân hàng biết tài khoản thuộc về ai và chịu trách nhiệm với khách của mình. Bài không so hơn thua, chỉ chỉ ra hai thiết kế đặt trách nhiệm ở hai nơi khác nhau.

## Nhìn hình trả lời

Trong cả hai cách, ai là bên nhìn thấy "bạn có bao nhiêu tiền"? Và vì sao chuyển khoản giữa hai ngân hàng có lúc sổ đã đổi mà tiền thật chưa đổi?

<details>
<summary>Xem đáp án</summary>

Ở ngân hàng, mỗi ngân hàng giữ sổ của mình và chỉ ngân hàng đó biết số dư của bạn ở đó. Khi chuyển sang ngân hàng khác, mỗi bên sửa sổ riêng của mình ngay, còn tiền thật di chuyển sau, lúc hai ngân hàng đối chiếu và thanh toán bù trừ cuối ngày. Vì vậy có một khoảng thời gian sổ đã đổi mà tiền thật chưa đổi.
Trên blockchain, mọi người dùng chung một sổ cái và số dư của một địa chỉ nằm ngay trong sổ cái đó; chuyển xong và được xác nhận là sổ đã đổi, nên không có khoảng chờ đối chiếu cuối ngày.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn là một so sánh ngắn kèm một sơ đồ; bài này giữ các số của ví dụ (100, 50, 2 ether, 8 và 101 ether) và đặt hai quy trình cạnh nhau theo ba bước. Phần giới hạn và đáp án là của người biên soạn.
Bài không nói về chuyện Visa hay PayPal đầu tư vào blockchain, câu hỏi mở đầu của nguồn, vì nguồn không trả lời nó.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/digital-wallet-in-traditional-banks-vs-wallet-in-blockchain.md): ví ngân hàng, ví blockchain, ví dụ số và nhận định về sổ cái phân tán. Mọi điều trong phần giới hạn là kiến thức chung của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

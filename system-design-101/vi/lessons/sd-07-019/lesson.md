# ACH: trả lương theo lô, tới sáng hôm sau

**Ở Hoa Kỳ, các công ty công nghệ thường trả lương qua ACH, một hệ thống thanh toán xử lý theo lô chứ không theo thời gian thực: trong ví dụ của nguồn, tệp gửi trước 19 giờ thì tiền tới tài khoản người nhận vào sáng hôm sau; giờ chốt và ngày hiệu lực thật do từng ngân hàng gốc và loại lệnh quyết định.**
Nguồn kể quy trình qua ví dụ một công ty trả lương 100 đô la cho một nhân viên.

![Ba khung. Khung một, từ công ty tới ngân hàng gốc: công ty trả lương gửi các giao dịch lương cho bên xử lý thứ ba, bên này tạo tệp ACH và tải lên máy chủ SFTP của ngân hàng gốc ODFI trước giờ chốt 19 giờ. Khung hai, qua đêm: sau giờ làm việc, ODFI chuyển tệp cho nhà vận hành ACH để bù trừ và quyết toán, tệp được xử lý khoảng nửa đêm và có mặt ở ngân hàng nhận RDFI. Khung ba, sáng hôm sau: lúc 6 giờ sáng RDFI cập nhật tài khoản người nhận, ví dụ cộng 100 đô la. ACH xử lý theo lô, không theo thời gian thực; từ 2018 có tùy chọn ACH trong ngày.](../../diagrams/sd-07-019-main.svg)

## Từ viết tắt

- **ACH** (Automated Clearing House) — nhà bù trừ tự động: hệ thống xử lý các giao dịch bán lẻ của Hoa Kỳ, theo lô.
- **ODFI** (Originating Depository Financial Institution) — tổ chức tài chính nhận tiền gửi khởi tạo: ngân hàng của bên khởi tạo, bên duy nhất được phép khởi tạo giao dịch ACH trực tiếp.
- **RDFI** (Receiving Depository Financial Institution) — tổ chức tài chính nhận tiền gửi tiếp nhận: ngân hàng của người nhận, nơi tiền cuối cùng được cộng vào tài khoản.
- **SFTP** (Secure File Transfer Protocol) — giao thức truyền tệp an toàn: kênh để tải tệp lên một máy chủ; ở đây là máy chủ do ODFI lập.
- **EPN** (Electronic Payments Network) — mạng thanh toán điện tử: một trong hai nhà vận hành ACH, do một công ty tư nhân vận hành.

## Đọc hình

**Chuẩn bị (bước 0).** Bên khởi tạo (originator, ở đây là công ty trả lương) phải có quan hệ với một tổ chức nhận tiền gửi đủ điều kiện (ngân hàng, hợp tác xã tín dụng...), vì chỉ tổ chức như vậy mới được đưa giao dịch vào mạng ACH; tổ chức đó là ODFI, và nó khác với bên khởi tạo không phải ngân hàng. Người nhận phải cho phép bên khởi tạo thực hiện một số loại giao dịch nhất định.

**1. Công ty tới ngân hàng gốc (bước 1 và 2).** Công ty tạo ra các giao dịch trả lương và gửi cho một bên xử lý thứ ba như Gusto, bên này hỗ trợ các dịch vụ liên quan tới ACH, chẳng hạn tạo tệp ACH. Bên xử lý thứ ba thay mặt công ty tạo tệp ACH rồi tải lên một máy chủ SFTP do ODFI lập. Việc này phải xong trước giờ chốt 19 giờ mà ngân hàng ODFI quy định.

**2. Qua đêm (bước 3 và 4).** Sau giờ làm việc buổi tối, ODFI chuyển các tệp ACH cho nhà vận hành ACH để bù trừ và quyết toán. Có hai nhà vận hành: Cục Dự trữ Liên bang, và EPN do một công ty tư nhân vận hành. Các tệp được xử lý quanh nửa đêm và được chuyển cho ngân hàng nhận, RDFI.

**3. Sáng hôm sau (bước 5).** RDFI thao tác trên tài khoản của người nhận theo chỉ dẫn trong tệp. Trong ví dụ, người nhận nhận 100 đô la từ bên khởi tạo. Việc này xảy ra khi RDFI mở cửa làm việc lúc 6 giờ sáng ngày hôm sau.

ACH là hệ thống quyết toán ngày hôm sau: giao dịch gửi đi trước 19 giờ thì tới vào sáng hôm sau. Sau đó ACH trong ngày (Same Day ACH) được triển khai theo từng giai đoạn từ 2016 (nguồn nêu mốc 2018, là một giai đoạn sau) để tiền được chuyển ngay trong ngày làm việc.

## Giới hạn cần nhớ

Nguồn mô tả hệ thống của Hoa Kỳ qua một ví dụ trả lương; các giờ 19 giờ, nửa đêm và 6 giờ sáng là của ví dụ và của quy định ngân hàng ODFI, không phải con số chung cho mọi hệ thống. Nguồn không nói phí, không nói chuyện gì xảy ra khi tệp lỗi hay khi giao dịch bị trả lại, và không nói ACH trong ngày khác ACH thường ở giờ chốt nào.
Bài không bổ sung các loại giao dịch khác của ACH ngoài trả lương.

## Nhìn hình trả lời

Công ty gửi tệp lúc 20 giờ tối thứ Ba, sau giờ chốt 19 giờ của ODFI. Theo nguồn, bình thường tiền sẽ tới khi nào? Và việc nhờ bên xử lý thứ ba làm gì cho công ty?

<details>
<summary>Xem đáp án</summary>

Nguồn nói giao dịch gửi trước 19 giờ thì tới sáng hôm sau; nó không nói rõ chuyện gì xảy ra với tệp gửi sau giờ chốt. Người biên soạn suy ra tệp muộn sẽ không đi cùng đợt đêm đó và tiền tới chậm hơn, nhưng đó là suy luận, nguồn không khẳng định.
Bên xử lý thứ ba tạo tệp ACH thay mặt công ty rồi tải lên máy chủ SFTP của ODFI, và hỗ trợ các dịch vụ liên quan tới ACH.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một danh sách sáu bước (0 đến 5) kèm lời giải thích ACH và ACH trong ngày. Bài này vẽ các bước 1 đến 4 thành hai lược đồ ba bên và bước 5 thành một khung hai thẻ, giữ bước 0 trong phần chữ, và viết tên nước, giờ trong ngày và tên nhà vận hành bằng tiếng Việt để khỏi dùng thêm chữ viết tắt.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-ach-payment-work.md): các bước 0 đến 5 của ACH trả lương, giờ chốt 19 giờ, quyết toán ngày hôm sau và ACH trong ngày. Phần giới hạn và đáp án là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

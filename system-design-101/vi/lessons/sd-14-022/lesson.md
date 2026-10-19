# An ninh mạng nhập môn: bộ ba CIA và phòng thủ cơ bản

**An ninh thông tin xoay quanh ba điều cần giữ: bí mật (chỉ người được phép đọc), toàn vẹn (bị sửa thì phát hiện được) và sẵn sàng (người được phép dùng được khi cần). Mỗi biện pháp phòng thủ thường chỉ giữ một hoặc hai điều trong ba, nên hệ thống thật phải xếp nhiều lớp.**
Bài này là bản đồ cho người mới: mỗi điều có định nghĩa bằng lời thường, một ví dụ, biện pháp tương ứng và bài dạy biện pháp đó, kèm hai thí nghiệm nhỏ. Bài nguồn có năm tiêu đề nhưng bốn mục không có chữ (kể cả mục khung chuẩn), nên bài này không liệt kê khung chuẩn nào ngoài những gì đã đọc được.

![Hai khung xếp dọc. Khung một: ba điều cần giữ của bộ ba CIA, mỗi điều kèm ví dụ khi hỏng. Bí mật: bảng lương lọt ra ngoài. Toàn vẹn: 100 USD thành 900 USD mà không ai hay. Sẵn sàng: trang thanh toán không mở được. Khung hai: biện pháp giữ từng điều. Bí mật: mã hóa, phân quyền đọc, lưu mật khẩu dạng băm. Toàn vẹn: mã xác thực, chữ ký số, phân quyền ghi. Sẵn sàng: giới hạn tốc độ, thời gian chờ, dự phòng. Thêm tường lửa bớt đường vào, và nhắc xếp nhiều lớp.](../../diagrams/sd-14-022-main.svg)

## Từ viết tắt

- **CIA** (Confidentiality, Integrity, Availability) — bí mật, toàn vẹn, sẵn sàng: bộ ba điều cần giữ; không liên quan tới cơ quan có cùng chữ viết tắt.
- **USD** (United States Dollar) — đô la Mỹ: đơn vị tiền trong ví dụ “Pay Bob 100 USD”.
- **DoS** (Denial of Service) — từ chối dịch vụ: kiểu tấn công làm cạn tài nguyên máy chủ, thường bằng cách dồn dập gửi yêu cầu, để người dùng thật không dùng được; trong bài là cách MDN gọi kẻ nhắm vào điều “sẵn sàng”.
- **HMAC** (Hash-based Message Authentication Code) — mã xác thực thông điệp dùng hàm băm và một khóa bí mật: ai không có khóa thì không tính lại được thẻ đúng sau khi sửa tin.
- **AES** (Advanced Encryption Standard) — chuẩn mã hóa tiên tiến: thuật toán mã hóa một khóa chung, dùng trong thí nghiệm.
- **CTR** (CounTeR) — chế độ đếm: cách dùng AES để mã hóa tin dài; giữ bí mật nhưng không tự kiểm tin có bị sửa.
- **GCM** (Galois/Counter Mode) — chế độ Galois/đếm: cách dùng AES vừa mã hóa vừa gắn thẻ kiểm, tin bị sửa thì giải mã báo lỗi.
- **SHA** (Secure Hash Algorithm) — họ thuật toán băm: biến dữ liệu bất kỳ thành một chuỗi cố định; SHA-256 là một loại trong họ này.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.
- **ASVS** (Application Security Verification Standard) — tiêu chuẩn kiểm chứng an ninh ứng dụng: bộ yêu cầu an ninh của OWASP cho ứng dụng web.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, tài liệu tra cứu công nghệ web của Mozilla và cộng đồng; bài dùng nó để đối chiếu.
- **STRIDE** (Spoofing, Tampering, Repudiation, Information, Denial, Elevation) — mẹo nhớ sáu loại mối đe dọa về an ninh, mỗi chữ cái là chữ đầu của một loại: giả mạo (Spoofing), sửa đổi trái phép (Tampering), chối bỏ hành vi (Repudiation), lộ thông tin (Information disclosure), từ chối dịch vụ (Denial of service), nâng quyền (Elevation of privilege); OWASP và MDN dùng nó để gọi tên các loại mối đe dọa.
- **LINDDUN** (Linking, Identifying, Non, Detecting, Data, Unawareness, Non) — mẹo nhớ bảy loại mối đe dọa về quyền riêng tư mà MDN nêu cùng STRIDE, mỗi chữ cái là chữ đầu của một loại: liên kết (Linking), nhận dạng (Identifying), không thể chối bỏ (Non-repudiation), phát hiện (Detecting), lộ dữ liệu (Data disclosure), thiếu nhận biết (Unawareness), không tuân thủ (Non-compliance).

## Đọc hình

MDN mô tả CIA là mô hình định hướng chính sách an ninh thông tin của một tổ chức. Định nghĩa, ví dụ và cách ghép biện pháp dưới đây là của người biên soạn; chỗ có đối chiếu thì nói rõ nguồn.

**Khung 1 · Ba điều cần giữ.**

**Bí mật (confidentiality).** Chỉ người được phép đọc được dữ liệu. Ví dụ: bảng lương của công ty lọt ra ngoài. Mã hóa giữ bí mật: OWASP ghi đó là mục đích của nó ([bài sd-14-002](../sd-14-002/lesson.md)). Phân quyền quyết định ai được đọc ([bài sd-14-004](../sd-14-004/lesson.md)). Mật khẩu lưu dạng băm để kẻ lấy được cơ sở dữ liệu không dùng bản băm mà đăng nhập thay người dùng ([bài sd-14-003](../sd-14-003/lesson.md)).

**Toàn vẹn (integrity).** Dữ liệu bị sửa thì phải phát hiện được. Ví dụ: lệnh `Pay Bob 100 USD` bị sửa thành `900 USD` trên đường đi. Biện pháp: mã xác thực HMAC, chữ ký số ([bài sd-14-015](../sd-14-015/lesson.md)), phân quyền ghi. Giữ bí mật chưa chắc giữ toàn vẹn: trong thí nghiệm, tin mã hóa bằng AES-CTR bị lật một bit vẫn giải mã không lỗi và ra `900 USD`; AES-GCM từ chối.

**Sẵn sàng (availability).** Người được phép dùng được khi cần. Ví dụ: trang thanh toán không mở được. Kẻ nhắm vào điều này làm tấn công từ chối dịch vụ (Denial of Service, DoS): theo MDN, nó làm cạn tài nguyên máy chủ, thường bằng cách dồn dập gửi yêu cầu. OWASP nêu giới hạn tốc độ, thời gian chờ cho kết nối và thành phần dự phòng. Tường lửa lọc lưu lượng theo luật (MDN) nên bớt được đường vào ([bài sd-14-007](../sd-14-007/lesson.md), [bài sd-14-013](../sd-14-013/lesson.md)), nhưng OWASP nhắc chính thiết bị trung gian như tường lửa cũng có thể bị làm cạn tài nguyên.

**Khung 2 · Biện pháp nào giữ điều nào.** Mỗi dòng chỉ là chỗ biện pháp mạnh nhất; MDN nói quan hệ tấn công và phòng thủ là nhiều-nhiều. Xác thực ([bài sd-14-014](../sd-14-014/lesson.md)) nằm dưới cả ba, vì OWASP ghi phân quyền diễn ra sau xác thực.

**Mối đe dọa.** OWASP dùng `STRIDE` (mẹo nhớ sáu loại mối đe dọa) và ghi mỗi loại vi phạm thuộc tính nào: sửa đổi trái phép vi phạm toàn vẹn, lộ thông tin vi phạm bí mật, từ chối dịch vụ vi phạm sẵn sàng; ba loại còn lại (giả mạo, chối bỏ hành vi, nâng quyền) ứng với xác thực, nhật ký ghi vết và phân quyền. Lừa đảo (phishing) nhắm vào người dùng chứ không vào lỗi phần mềm; biện pháp MDN gọi là thật sự hiệu quả duy nhất là passkey ([bài sd-14-006](../sd-14-006/lesson.md)).

**Phần mềm diệt virus** là chương trình tìm phần mềm độc hại. OWASP khuyên cho tệp tải lên đi qua nó (hoặc môi trường cô lập), nhưng nói giải pháp chống mã độc không thể hiệu quả 100% và chỉ nên là lớp bổ sung. Bài không đo tỉ lệ bắt được của loại nào.

**Khung chuẩn.** Mục này của bài nguồn để trống. MDN nêu hai khung phân tích mối đe dọa, `STRIDE` (an ninh) và `LINDDUN` (riêng tư); OWASP ASVS tự mô tả là bộ yêu cầu an ninh cho ứng dụng web. Bài không đọc được tài liệu của các tổ chức tiêu chuẩn nên không kể khung nào khác. Đưa kiểm tra bảo mật vào từng chặng phát triển: [bài sd-14-001](../sd-14-001/lesson.md).

## Giới hạn cần nhớ

Ba điều không độc lập: bảo vệ điều này có thể làm hại điều kia. OWASP nêu khóa tài khoản sau nhiều lần đăng nhập sai là biện pháp phổ biến nhất chống đoán mật khẩu, nhưng kẻ tấn công cũng có thể cố ý đăng nhập sai để khóa người dùng thật, tức là hạ sẵn sàng. Vì thế không biện pháp nào đủ một mình: OWASP dặn không dựa vào một biện pháp duy nhất để thực thi phân quyền, và nói các biện pháp chống đoán mật khẩu thường không bảo vệ trọn vẹn nhưng xếp nhiều lớp thì đạt mức hợp lý.

## Nhìn hình trả lời

Một cửa hàng mã hóa mọi dữ liệu khách hàng, nhưng đến ngày khuyến mãi trang web chậm đến mức khách không thanh toán được. Theo hình, mã hóa đã giữ điều nào, điều nào đang hỏng, và nên tìm biện pháp ở đâu?

<details>
<summary>Xem đáp án</summary>

Mã hóa giữ bí mật (nếu làm đúng); điều đang hỏng là sẵn sàng, và mã hóa không giúp trang chịu tải. Biện pháp nằm ở dòng sẵn sàng của khung hai: giới hạn tốc độ, thời gian chờ, dự phòng, cùng tường lửa để chặn bớt lưu lượng không cần.
Chậm chưa chắc do kẻ tấn công: OWASP nêu điểm hỏng có thể đến từ lỗi lập trình hay cạn tài nguyên, nên cần biết nguyên nhân trước khi chọn biện pháp.

</details>

<details>
<summary>Xem sâu hơn: hai thí nghiệm và điều đã chỉnh so với bài nguồn</summary>

Mọi số là một lần đo trên máy biên soạn (Python 3.13.16, `cryptography` 50.0.1, khóa tạm, chỉ `127.0.0.1`); thí nghiệm 2 chạy hai lần và cho cùng kết quả.

**Thí nghiệm 1: toàn vẹn khác bí mật.** Tin là `Pay Bob 100 USD`; kẻ tấn công đổi một ký tự thành `900`.

- Băm và thẻ: SHA-256 không khóa đặt cạnh tin không cản được kẻ tấn công thay cả tin lẫn bản băm (kiểm vẫn qua). HMAC với SHA-256 thì tin giả đi kèm thẻ cũ, hay thẻ tính bằng khóa đoán, đều bị từ chối; nhưng tin vẫn đọc được, vì HMAC không giữ bí mật.
- AES-256 chế độ CTR: bản mã không chứa `Bob`. Lật một bit ở vị trí 8 (`1` thành `9`; kẻ tấn công cần biết bố cục tin, không cần khóa) thì giải mã không lỗi và ra `Pay Bob 900 USD`.
- AES-256 chế độ GCM: bản mã không chứa `Bob`; lật cùng bit thì thư viện báo `InvalidTag` và không trả gì. Khớp với OWASP: chế độ có xác thực như GCM bảo đảm cả toàn vẹn lẫn bí mật, còn CTR cần thêm bước xác thực riêng.

**Thí nghiệm 2: sẵn sàng, đếm được.** Ba máy chủ nhỏ đọc một dòng rồi trả lời. A và B xử lý từng kết nối một (tài liệu `socketserver` của Python: các lớp này xử lý yêu cầu đồng bộ); A chờ vô hạn, B bỏ cuộc sau 1,0 giây; C dùng một luồng cho mỗi kết nối. Ba “máy khách treo” kết nối rồi im lặng; sau đó năm máy khách bình thường cùng tới, mỗi máy chờ tối đa 5 giây.

| Máy chủ | Không có máy khách treo | Ba máy khách treo |
|---|---|---|
| A: từng kết nối một, chờ vô hạn | 5/5, dưới 0,01 giây | 0/5 trong 5 giây |
| B: từng kết nối một, bỏ cuộc sau 1,0 giây | 5/5, dưới 0,01 giây | 5/5, sau 2,70 giây |
| C: mỗi kết nối một luồng | 5/5, dưới 0,01 giây | 5/5, dưới 0,01 giây |

A bị một kết nối treo giữ mãi nên không phục vụ ai. B hồi phục nhờ thời gian chờ nhưng máy khách vẫn đợi gần ba giây (phù hợp với 3 × 1,0 giây trừ 0,3 giây chờ trước khi họ tới). C phục vụ ngay. Đây là mô hình đồ chơi của một nguyên nhân, không đo tấn công dồn dập thật, và số luồng của C cũng hữu hạn (OWASP: kiểu tấn công gửi yêu cầu rất chậm làm máy chủ chạm trần số kết nối đồng thời).

**Điều đã chỉnh so với bài nguồn.**

- Bốn trong năm mục của bài nguồn không có chữ; bài này điền bằng tài liệu đã đọc và nói rõ chỗ là của người biên soạn.
- Bài nguồn gọi tường lửa là thiết bị mạng (MDN: có thể chỉ là phần mềm), nói mã hóa chặn truy cập trái phép (bài này thêm: mã hóa tự nó không phát hiện sửa đổi) và không nêu giới hạn của phần mềm diệt virus (OWASP: lớp bổ sung, không hiệu quả 100%).
- Ba biện pháp của bài nguồn không có biện pháp nào chủ yếu cho toàn vẹn hay sẵn sàng; bài này thêm chúng ở khung hai. Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cybersecurity-101-in-one-picture.md): năm tiêu đề, chỉ mục biện pháp phòng thủ có chữ.
- MDN: [CIA](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/cia/index.md), [Firewall](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/firewall/index.md), [Denial of Service](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/denial_of_service/index.md), [Web Security](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/index.md), [Phishing](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/attacks/phishing/index.md), [Threat modeling frameworks](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/threat_modeling/frameworks/index.md). Đọc từ bản clone của kho.
- OWASP Cheat Sheet Series: [Security Terminology](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Security_Terminology_Cheat_Sheet.md), [Threat Modeling](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Threat_Modeling_Cheat_Sheet.md), [Denial of Service](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Denial_of_Service_Cheat_Sheet.md), [Authentication](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Authentication_Cheat_Sheet.md), [Password Storage](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Password_Storage_Cheat_Sheet.md), [Authorization](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Authorization_Cheat_Sheet.md), [Cryptographic Storage](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Cryptographic_Storage_Cheat_Sheet.md), [File Upload](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/File_Upload_Cheat_Sheet.md), [Transaction Authorization](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Transaction_Authorization_Cheat_Sheet.md), [Attack Surface Analysis](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Attack_Surface_Analysis_Cheat_Sheet.md). Đọc từ bản clone của kho.
- [OWASP ASVS — README](https://github.com/OWASP/ASVS/blob/2b47a9dd16760ee484a6672d197f1f7e25d9c632/README.md): ASVS tự mô tả.
- pyca/cryptography: [HMAC](https://github.com/pyca/cryptography/blob/6179e1c39ed0019cf27168420eff6b3ab1840ef9/docs/hazmat/primitives/mac/hmac.rst), [Authenticated encryption](https://github.com/pyca/cryptography/blob/6179e1c39ed0019cf27168420eff6b3ab1840ef9/docs/hazmat/primitives/aead.rst), [chế độ CTR](https://github.com/pyca/cryptography/blob/6179e1c39ed0019cf27168420eff6b3ab1840ef9/docs/hazmat/primitives/symmetric-encryption.rst). Các lần thử chạy với `cryptography` 50.0.1.
- [CPython — socketserver](https://github.com/python/cpython/blob/cdf010b10c673e1ec4faaf3f8f9be39237986880/Doc/library/socketserver.rst): máy chủ xử lý yêu cầu đồng bộ, và cách dùng luồng.

Đã đọc nguồn ngày 2026-10-18. Các trang của viện tiêu chuẩn và của tổ chức soạn đặc tả Internet không truy cập được nên không được trích dẫn. Lời giải thích ba điều bằng lời thường, các ví dụ, cách ghép biện pháp với từng điều và hai thí nghiệm là của người biên soạn. Bài viết và hình được thiết kế độc lập.

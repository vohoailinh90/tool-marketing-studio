# HTTPS có an toàn không? Kẻ đứng giữa đọc được khi nào

**HTTPS giữ kín nội dung trên đường đi, nhưng chỉ khi máy khách kiểm đúng chứng chỉ của đầu bên kia. Một relay đứng giữa đọc được chữ rõ khi máy khách đã tin một tổ chức cấp chứng chỉ (CA) mà relay nắm; chưa có niềm tin đó thì máy khách từ chối ngay lúc bắt tay.**
Bài dựng một mô hình trên máy mình (127.0.0.1, khóa dùng một lần, không nối ra Internet) để thấy vì sao kho CA tin cậy của máy khách quyết định chuyện này. Theo bài nguồn và OWASP, công cụ gỡ lỗi như Fiddler (ví dụ của bài nguồn) và proxy của doanh nghiệp dựa trên cùng điều kiện này, với sự đồng ý của người dùng máy. Bài không chạy chúng và không hướng dẫn nghe lén người khác.

![Bốn phần xếp dọc. Phần một, kết nối 1 giữa máy khách và relay: máy khách bắt tay TLS với relay, nhận chứng chỉ localhost do CA của relay ký, rồi gửi yêu cầu mã hóa bằng khóa 1. Phần hai, kết nối 2 giữa relay và máy chủ thật: relay bắt tay TLS lần hai, nhận chứng chỉ do CA thật ký, rồi gửi yêu cầu mã hóa bằng khóa 2; hai kết nối có hai khóa khác nhau. Phần ba: nếu kho tin cậy của máy khách chỉ có CA thật thì kiểm chứng chỉ thất bại và relay chưa đọc được gì; nếu có thêm CA của relay thì bắt tay xong và relay đọc được yêu cầu cùng trả lời. Phần bốn: chặn được đường chưa đủ, tin một CA là tin chứng chỉ nó ký, cả cho tên lạ, nếu chứng chỉ qua các kiểm tra còn lại; chỉ cài CA bạn biết và đồng ý.](../../diagrams/sd-14-021-main.svg)

## Từ viết tắt

- **HTTPS** (HyperText Transfer Protocol Secure) — HTTP chạy trên TLS: cách gửi yêu cầu và trả lời như HTTP nhưng nội dung được mã hóa.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa giữ kín dữ liệu giữa hai đầu một kết nối và giúp xác nhận đầu bên kia là ai.
- **SSL** (Secure Sockets Layer) — lớp ổ cắm an toàn: tên cũ của TLS, nay đã lỗi thời nhưng người ta vẫn quen gọi; bài nguồn dùng tên này.
- **CA** (Certificate Authority) — tổ chức cấp chứng chỉ: bên ký xác nhận rằng một khóa công khai thuộc về một tên. Trong bài còn có "CA của relay": một CA tạo riêng cho thử nghiệm.
- **RSA** (Rivest-Shamir-Adleman) — tên một thuật toán mã hóa khóa công khai, đặt theo ba tác giả; ở đây là kiểu TLS cũ dùng khóa công khai trong chứng chỉ để mã hóa khóa phiên (bước 5 và 6 của bài nguồn).
- **RFC** (Request for Comments) — "đề nghị bình luận": loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; nhiều RFC là tiêu chuẩn. Bài nhắc tới RFC 8446, đặc tả của TLS 1.3, nhưng không đọc được nó.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

Thử nghiệm dùng Python 3.13.16 (mô-đun `ssl`, OpenSSL 3.0.13) và `cryptography` 50.0.1, với ba bên: một máy chủ "thật" có chứng chỉ cho tên `localhost` do CA thật ký; một relay viết bằng Python, có chứng chỉ cũng cho `localhost` nhưng do CA của relay ký; và một máy khách. Khóa và CA tạo mới cho lần chạy, cổng ngẫu nhiên, dữ liệu là chuỗi giả. Kết quả là một lần chạy trên máy biên soạn.

**1 · Hai kết nối, không phải một.** Với máy khách, relay là một máy chủ TLS bình thường. Với máy chủ thật, relay là một máy khách TLS bình thường. Mỗi chặng có bắt tay riêng và khóa phiên riêng; relay giữ chữ rõ ở giữa. Nhật ký khóa của Python (`keylog_filename`) cho thấy mỗi chặng có 5 dòng bí mật giống hệt ở hai đầu của nó, còn hai chặng không chung `client_random` hay bí mật nào (bài chỉ đếm, không in bí mật). Cho máy chủ thật nhận tối đa TLS 1.2 thì máy khách vẫn báo TLSv1.3 còn chặng sau là TLSv1.2: hai kết nối độc lập nên không cần giống nhau.

**2 · Kho chỉ có CA thật.** Máy khách nối tới relay và nhận lỗi `SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate`. Chứng chỉ của relay do một CA không có trong kho ký, nên không dựng được chuỗi tin cậy tới một CA đã biết. (Chứng chỉ là một khóa công khai cùng tên do CA ký: xem [bài sd-14-014](../sd-14-014/lesson.md) về chứng chỉ và [bài sd-14-015](../sd-14-015/lesson.md) về chữ ký số.) Relay nhận cảnh báo `tlsv1 alert unknown ca` và đọc được 0 yêu cầu; máy chủ thật nhận 0 kết nối (relay này chỉ nối ngược sau khi bắt tay với máy khách xong). Dẫn được lưu lượng về relay vẫn chưa đủ.

**3 · Kho có thêm CA của relay.** Bắt tay xong qua TLS 1.3, máy khách nhận trả lời 200 giống hệt khi nối thẳng và không có lỗi nào từ TLS. Relay đọc được dòng yêu cầu, một tiêu đề thử và nội dung trả lời. Trong lần chạy, máy khách so sánh thấy khác ở người ký chứng chỉ (CA của relay thay vì CA thật) và dấu vân tay chứng chỉ; khóa công khai trong chứng chỉ cũng khác (phép thử ghim khóa ở phần xem sâu hơn), và hai chặng có thể thương lượng khác nhau, như phiên bản TLS của hai chặng ở mục 1. Đây là những gì lần chạy này so sánh, không phải danh sách đầy đủ.

## Giới hạn cần nhớ

Điều kiện thật là niềm tin vào CA, không phải việc chặn được đường. Hai việc tách biệt: đưa lưu lượng tới relay (cài proxy, hoặc mạng bị can thiệp, như điểm truy cập Wi-Fi do kẻ tấn công dựng ở nơi công cộng mà MDN nêu), và khiến máy khách chấp nhận chứng chỉ của relay. Bài chỉ mô hình hóa việc thứ hai. OWASP kể hai đường: xin được chứng chỉ cho tên nạn nhân từ một CA đã được tin, hoặc đưa một CA lạ vào kho tin cậy của máy khách. Khi CA đã vào kho, niềm tin không còn gắn với một CA thật duy nhất: một chứng chỉ cho tên `demo.test` do CA của relay ký bị máy khách chỉ tin CA thật từ chối, và được máy khách tin cả hai CA chấp nhận. Tên vẫn được kiểm riêng: cũng chứng chỉ đó bị từ chối (`Hostname mismatch`) khi máy khách hỏi tên `localhost`. Vì vậy kho CA là thứ phải giữ: CA nào đã vào kho thì chứng chỉ nó ký được chấp nhận, với bất kỳ tên nào nó chịu ký, miễn các kiểm tra còn lại của chứng chỉ cũng đạt (hạn dùng, mục đích khóa, ràng buộc trên đường chứng thực: bài chỉ thử một chứng chỉ hợp lệ) và trừ khi CA bị giới hạn tên (bài không thử). Còn nếu máy khách tắt hẳn việc kiểm chứng chỉ thì mã hóa vẫn chạy nhưng không ai bảo đảm đầu bên kia là ai; bài này không thử trường hợp đó, xem [bài sd-14-014](../sd-14-014/lesson.md).

## Nhìn hình trả lời

Một hướng dẫn bảo bạn cài "chứng chỉ gốc" của một công cụ lạ để xem được lưu lượng HTTPS. Sau khi cài, công cụ làm được gì mà trước đó không làm được? Và nếu lưu lượng của bạn bị dẫn qua nó mà bạn chưa cài thì sao?

<details>
<summary>Xem đáp án</summary>

Sau khi cài, một relay do công cụ (hay người giữ khóa riêng của CA đó) điều khiển có thể đưa ra chứng chỉ cho tên bạn đang gọi, và máy bạn chấp nhận, giống mục 3: relay đọc được chữ rõ. Trước khi cài thì giống mục 2: kiểm chứng chỉ thất bại, không yêu cầu nào tới relay. Vậy khóa riêng của một CA đã được tin là thứ phải giữ kín nhất, và chỉ nên cài CA khi bạn biết ai giữ nó và để làm gì.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn và các phép thử khác</summary>

Bài nguồn nêu "root certificate của relay nằm trong trust-store" thành một dòng điều kiện rồi kể tám bước. Điều kiện đó đúng và là cả vấn đề; bài này đặt nó ở giữa và chạy thử cả hai nhánh.
Bài nguồn gọi bên giữa là "malicious" nhưng lại hỏi về công cụ như Fiddler. Cơ chế giống nhau; khác nhau ở sự đồng ý của chủ máy. OWASP gọi proxy chặn của doanh nghiệp là "good" bad actor, vì cả hai kiểu đều phá bảo mật đầu cuối và không phân biệt được với nhau.
Bài nguồn viết "SSL certificate"; MDN gọi SSL là tiền thân của TLS, nên bài này nói chứng chỉ dùng cho TLS.
Bước 5 và 6 của bài nguồn (máy khách mã hóa khóa phiên bằng khóa công khai, relay giải mã rồi mã hóa lại bằng khóa công khai của máy chủ) mô tả kiểu trao khóa bằng RSA. OWASP khuyên tắt các bộ mã `TLS_RSA_*` vì chúng không có tính bí mật chuyển tiếp (forward secrecy: sau này lộ khóa riêng của máy chủ cũng không giải mã được lưu lượng đã ghi lại). Chạy `openssl s_client` vào máy chủ thử cho thấy: ở TLS 1.3, OpenSSL báo `Server Temp Key: X25519, 253 bits` (một khóa tạm) và `Peer signature type: RSA-PSS` (máy chủ ký bằng khóa trong chứng chỉ). Ép TLS 1.2 với bộ mã `AES128-GCM-SHA256` (trao khóa kiểu RSA) thì cả hai dòng đều không có. TLS 1.2 với `ECDHE-RSA-AES128-GCM-SHA256` lại có cả hai. Việc TLS 1.3 bỏ hẳn trao khóa kiểu RSA là hiểu biết chung của người biên soạn (không đọc được RFC 8446). Hệ quả: relay không "giải mã khóa phiên rồi mã hóa lại"; nó chỉ là một đầu TLS ở mỗi bên, như mục 1.
Phép thử ghim khóa: máy khách tin cả hai CA nhưng ghim khóa công khai của máy chủ thật thì nối thẳng được, còn qua relay bị từ chối vì khóa khác. OWASP lại nói gần như không bao giờ nên ghim (rủi ro gián đoạn thường lớn hơn) và đừng ghim nếu không điều khiển cả hai đầu.
Mã thử nghiệm không nằm trong kho. Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/is-https-safe.md): câu hỏi về Fiddler và tám bước của relay.
- [MDN — Transport Layer Security](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/defenses/transport_layer_security/index.md), [Certificate authority](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/certificate_authority/index.md), [Manipulator in the Middle](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/security/attacks/mitm/index.md): xác thực máy chủ bằng chứng chỉ, kho chứng chỉ gốc của trình duyệt, ví dụ điểm truy cập Wi-Fi do kẻ tấn công dựng. Đọc từ kho tại commit này.
- [OWASP — Pinning Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Pinning_Cheat_Sheet.md) và [Transport Layer Security Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/f9a631ec47a5fd134bb83b57ce690d7946360cea/cheatsheets/Transport_Layer_Security_Cheat_Sheet.md): hai đường tấn công vào niềm tin, proxy chặn, ghim khóa, bộ mã `TLS_RSA_*`.
- [Python — mô-đun ssl](https://github.com/python/cpython/blob/cdf010b10c673e1ec4faaf3f8f9be39237986880/Doc/library/ssl.rst): `load_verify_locations`, `SSLCertVerificationError`, `keylog_filename`. Đây là bản tài liệu của nhánh phát triển; các lần chạy dùng Python 3.13.16.
- [OpenSSL — openssl s_client](https://github.com/openssl/openssl/blob/6d76833d61fad07a171219d9cb1444bc37f88b8f/doc/man1/openssl-s_client.pod.in): các tùy chọn của lệnh dùng để xem bắt tay. [pyca/cryptography — x509 tutorial](https://github.com/pyca/cryptography/blob/6179e1c39ed0019cf27168420eff6b3ab1840ef9/docs/x509/tutorial.rst): cách tạo CA và chứng chỉ thử.

Đã đọc nguồn ngày 2026-10-18. Mô hình relay, cách chia ba mục đọc hình và các phép thử là của người biên soạn. Bài viết và hình được thiết kế độc lập.

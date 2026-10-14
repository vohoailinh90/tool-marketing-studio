# Passkey có thay được mật khẩu?

**Passkey thay mật khẩu bằng một cặp khóa: khóa riêng do thiết bị của bạn giữ và không gửi cho trang, trang web chỉ giữ khóa công khai.**
Đăng nhập khi đó là chứng minh bạn giữ khóa riêng, chứ không phải gửi một bí mật cho trang.

![Bảy thẻ xếp dọc. Nhóm đăng ký: 1 thử thách, trang gửi một chuỗi ngẫu nhiên; 2 tạo cặp khóa, bạn xác nhận và thiết bị tạo khóa gắn với trang này; 3 lưu khóa công khai, trang giữ khóa công khai, không có khóa riêng, cạnh tài khoản. Nhóm đăng nhập: 4 thử thách mới, mỗi lần đăng nhập một chuỗi ngẫu nhiên khác; 5 ký, trình duyệt ghi tên miền và thử thách vào dữ liệu, khóa riêng ký dữ liệu đó; 6 kiểm tra, trang kiểm tra chữ ký bằng khóa công khai cả tên miền. Thẻ cuối: điểm yếu còn lại là mất thiết bị hoặc tài khoản đồng bộ, và khôi phục tài khoản.](../../diagrams/sd-14-006-main.svg)

## Từ viết tắt

- **PIN** (Personal Identification Number) — mã số cá nhân: dãy số ngắn người dùng nhập để xác nhận trên thiết bị.
- **ECDSA** (Elliptic Curve Digital Signature Algorithm) — thuật toán chữ ký số dùng đường cong elliptic: ký bằng khóa riêng, kiểm bằng khóa công khai.

## Đọc hình

**1 · Thử thách.** Trang tạo một chuỗi ngẫu nhiên trên máy chủ của mình. Chuỗi này chỉ dùng cho lần đăng ký đó, nên một lời đáp cũ không dùng lại được.

**2 · Tạo cặp khóa.** Bạn xác nhận ngay trên thiết bị. Thường đó là sinh trắc học (như vân tay) hoặc mã PIN; tùy cấu hình, có trường hợp chỉ cần chạm vào khóa bảo mật để chứng tỏ có người ở đó, không cần sinh trắc học hay PIN. Chính thiết bị (bộ xác thực) tạo ra cặp khóa, gắn nó với trang này, giữ khóa riêng và chỉ gửi khóa công khai đi.

**3 · Lưu khóa công khai.** Trang lưu khóa công khai cạnh tài khoản của bạn. Khóa công khai không dùng được để ký, nên lộ nó không giúp ai đăng nhập thay bạn.

**4–6 · Đăng nhập.** Trang gửi một thử thách mới. Bạn xác nhận trên thiết bị. Trình duyệt ghi thử thách cùng tên miền của nơi đang yêu cầu vào dữ liệu gửi đi, khóa riêng trên thiết bị ký dữ liệu đó, và trang kiểm tra chữ ký bằng khóa công khai đã lưu, đồng thời kiểm tra tên miền và định danh trang ghi trong đó đúng là cái nó mong đợi.
Khi chạy thử, chữ ký cũ đem so với một thử thách mới thì không hợp lệ.

## Giới hạn cần nhớ

Passkey đổi chỗ yếu chứ không xóa nó. Với khóa chỉ nằm trên một thiết bị (single-device credential), điểm yếu là mất thiết bị: đặc tả WebAuthn lưu ý loại khóa này không chịu được việc mất thiết bị, và khuyên trang nên cho đăng ký thêm thiết bị xác thực hoặc có quy trình khôi phục tài khoản.
Với passkey đồng bộ (multi-device credential), khóa được sao lưu để dùng trên nhiều thiết bị; theo suy luận của người biên soạn, rủi ro khi đó chuyển một phần sang dịch vụ đồng bộ và quy trình khôi phục của nó, điều bài này chưa kiểm.

## Nhìn hình trả lời

Kẻ lừa đảo dựng một trang giả có tên miền gần giống trang thật. Passkey cản việc này thế nào, và vì sao mật khẩu thì không?

<details>
<summary>Xem đáp án</summary>

Bộ xác thực gắn mỗi khóa với trang đã đăng ký, còn trình duyệt đưa tên miền của nơi đang yêu cầu vào dữ liệu mà bộ xác thực ký; trang kiểm tra cả hai. Nhờ đó trang giả có tên miền khác không dùng được khóa của trang thật, và chữ ký tạo cho trang giả không có giá trị với trang thật, miễn là trang thật thực sự kiểm tra tên miền và định danh trang. Đặc tả WebAuthn mô tả cơ chế này như sự phối hợp giữa trình duyệt và bộ xác thực, và yêu cầu trang thực hiện các bước kiểm tra đó.
Với mật khẩu, bạn tự gõ bí mật vào trang giả, và kẻ lừa đảo có ngay bản rõ để dùng ở trang thật. Khi chạy thử, chữ ký tạo cho tên miền giả không được trang thật chấp nhận.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn viết khóa riêng “được tạo dựa trên khóa công khai do trang web cung cấp”. Đặc tả WebAuthn mô tả ngược lại: bộ xác thực tạo cặp khóa, khóa công khai được gửi về trang trong lúc đăng ký, còn khóa riêng gắn với bộ xác thực. Bài này theo đặc tả.
Bài nguồn cũng nói “không có rủi ro lộ mật khẩu” vì trang không lưu mật khẩu. Đúng là không có mật khẩu để lộ, nhưng đó là cách nói quá: điểm yếu chuyển sang thiết bị và khôi phục, như phần trên. Bài này bỏ ý “trải nghiệm đồng nhất trên mọi nền tảng” của bài nguồn vì chưa kiểm được.
Đặc tả gọi khóa dùng được trên nhiều thiết bị là “multi-device credential”, thường gọi là passkey đồng bộ.

Ví dụ chạy thử là mô hình tối giản bằng ECDSA P-256 của thư viện `cryptography`, trong đó phần “thiết bị” tự ghép tên miền vào dữ liệu ký; trong WebAuthn thật, trình duyệt đưa tên miền vào dữ liệu, bộ xác thực giữ khóa và ký, còn trang phải kiểm tra tên miền và định danh trang.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/is-passkey-shaping-a-passwordless-future.md): hai bước tạo và dùng passkey.
- [W3C — Web Authentication (nguồn đặc tả)](https://github.com/w3c/webauthn/blob/0c50bd034f4ee86c524b652a4f96362df4a5bd80/index.bs): cặp khóa do bộ xác thực tạo và gắn với trang; khóa công khai gửi về trang khi đăng ký; tên miền nằm trong dữ liệu được ký; thử thách ngẫu nhiên từ máy chủ; khóa trên một thiết bị cần thiết bị thêm hoặc khôi phục tài khoản. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Ví dụ chạy thử bằng Python và `cryptography` 50.0.1. Đặc tả được đọc ở các đoạn về cặp khóa, phạm vi theo trang, thử thách và khóa một thiết bị; không đọc toàn bộ. Bài viết và hình được thiết kế độc lập.

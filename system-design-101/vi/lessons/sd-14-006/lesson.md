# Passkey có thay được mật khẩu?

**Passkey thay mật khẩu bằng một cặp khóa: khóa riêng do thiết bị của bạn giữ và không gửi cho trang, trang web chỉ giữ khóa công khai.**
Đăng nhập khi đó là chứng minh bạn giữ khóa riêng, chứ không phải gửi một bí mật cho trang.

![Bảy thẻ xếp dọc. Nhóm đăng ký: 1 thử thách, trang gửi một chuỗi ngẫu nhiên; 2 tạo cặp khóa, bạn xác nhận và thiết bị tạo khóa gắn với trang này; 3 lưu khóa công khai, trang giữ khóa công khai, không có khóa riêng, cạnh tài khoản. Nhóm đăng nhập: 4 thử thách mới, mỗi lần đăng nhập một chuỗi ngẫu nhiên khác; 5 ký, bạn xác nhận và khóa riêng ký thử thách cùng tên miền; 6 kiểm tra, trang dùng khóa công khai để kiểm tra chữ ký. Thẻ cuối: điểm yếu còn lại là mất thiết bị hoặc tài khoản đồng bộ, và khôi phục tài khoản.](../../diagrams/sd-14-006-main.svg)

## Đọc hình

**1 · Thử thách.** Trang tạo một chuỗi ngẫu nhiên trên máy chủ của mình. Chuỗi này chỉ dùng cho lần đăng ký đó, nên một lời đáp cũ không dùng lại được.

**2 · Tạo cặp khóa.** Bạn xác nhận ngay trên thiết bị. Thường đó là sinh trắc học (như vân tay) hoặc mã PIN; tùy cấu hình, có trường hợp chỉ cần chạm vào khóa bảo mật để chứng tỏ có người ở đó, không cần sinh trắc học hay PIN. Chính thiết bị (bộ xác thực) tạo ra cặp khóa, gắn nó với trang này, giữ khóa riêng và chỉ gửi khóa công khai đi.

**3 · Lưu khóa công khai.** Trang lưu khóa công khai cạnh tài khoản của bạn. Khóa công khai không dùng được để ký, nên lộ nó không giúp ai đăng nhập thay bạn.

**4–6 · Đăng nhập.** Trang gửi một thử thách mới. Bạn xác nhận trên thiết bị, khóa riêng ký thử thách cùng tên miền của nơi đang yêu cầu, và trang kiểm tra chữ ký bằng khóa công khai đã lưu.
Khi chạy thử, chữ ký cũ đem so với một thử thách mới thì không hợp lệ.

## Giới hạn cần nhớ

Passkey đổi chỗ yếu chứ không xóa nó. Với khóa chỉ nằm trên một thiết bị (single-device credential), điểm yếu là mất thiết bị: đặc tả WebAuthn lưu ý loại khóa này không chịu được việc mất thiết bị, và khuyên trang nên cho đăng ký thêm thiết bị xác thực hoặc có quy trình khôi phục tài khoản.
Với passkey đồng bộ (multi-device credential), khóa được sao lưu để dùng trên nhiều thiết bị; theo suy luận của người biên soạn, rủi ro khi đó chuyển một phần sang dịch vụ đồng bộ và quy trình khôi phục của nó, điều bài này chưa kiểm.

## Nhìn hình trả lời

Kẻ lừa đảo dựng một trang giả có tên miền gần giống trang thật. Passkey cản việc này thế nào, và vì sao mật khẩu thì không?

<details>
<summary>Xem đáp án</summary>

Thiết bị gắn mỗi khóa với trang đã đăng ký và đưa tên miền của nơi đang yêu cầu vào dữ liệu được ký, nên trang giả có tên miền khác không dùng được khóa của trang thật, và chữ ký tạo cho trang giả không có giá trị với trang thật. Đặc tả WebAuthn mô tả đúng cơ chế này.
Với mật khẩu, bạn tự gõ bí mật vào trang giả, và kẻ lừa đảo có ngay bản rõ để dùng ở trang thật. Khi chạy thử, chữ ký tạo cho tên miền giả không được trang thật chấp nhận.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn viết khóa riêng “được tạo dựa trên khóa công khai do trang web cung cấp”. Đặc tả WebAuthn mô tả ngược lại: bộ xác thực tạo cặp khóa, khóa công khai được gửi về trang trong lúc đăng ký, còn khóa riêng gắn với bộ xác thực. Bài này theo đặc tả.
Bài nguồn cũng nói “không có rủi ro lộ mật khẩu” vì trang không lưu mật khẩu. Đúng là không có mật khẩu để lộ, nhưng đó là cách nói quá: điểm yếu chuyển sang thiết bị và khôi phục, như phần trên. Bài này bỏ ý “trải nghiệm đồng nhất trên mọi nền tảng” của bài nguồn vì chưa kiểm được.
Đặc tả gọi khóa dùng được trên nhiều thiết bị là “multi-device credential”, thường gọi là passkey đồng bộ.

Ví dụ chạy thử là mô hình tối giản bằng ECDSA P-256 của thư viện `cryptography`, trong đó phần “thiết bị” tự ghép tên miền vào dữ liệu ký; trong WebAuthn thật, trình duyệt cung cấp tên miền và bộ xác thực mới là nơi giữ khóa.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/is-passkey-shaping-a-passwordless-future.md): hai bước tạo và dùng passkey.
- [W3C — Web Authentication (nguồn đặc tả)](https://github.com/w3c/webauthn/blob/main/index.bs): cặp khóa do bộ xác thực tạo và gắn với trang; khóa công khai gửi về trang khi đăng ký; tên miền nằm trong dữ liệu được ký; thử thách ngẫu nhiên từ máy chủ; khóa trên một thiết bị cần thiết bị thêm hoặc khôi phục tài khoản. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Ví dụ chạy thử bằng Python và `cryptography` 50.0.1. Đặc tả được đọc ở các đoạn về cặp khóa, phạm vi theo trang, thử thách và khóa một thiết bị; không đọc toàn bộ. Bài viết và hình được thiết kế độc lập.

# JWT: ba phần và hai cách ký

**Một JWT là một chuỗi chữ gồm ba phần nối bằng dấu chấm: header, payload và signature. Nó được ký chứ không được mã hóa: ai nhặt được token cũng đọc được payload, nhưng sửa một ký tự thì lúc kiểm dấu ký sẽ thất bại.**
Bài này mổ một token ra từng phần bằng các lần chạy thử với PyJWT, rồi so hai cách ký (một bí mật chung và một cặp khóa) và chỉ ra những việc bên kiểm phải tự quyết. Ý tưởng chữ ký số nằm ở [bài sd-14-015](../sd-14-015/lesson.md). Bài này không so sánh JWT với session; phần nhận ra người dùng bằng token, cookie và session xem ở [bài sd-14-010](../sd-14-010/lesson.md).

![Ba khung xếp dọc. Khung một, ba phần nối bằng dấu chấm: header ghi thuật toán ký (alg) và loại token (typ); payload chứa các claim như sub, aud, exp; signature là dấu ký tính trên header và payload. Header và payload ai cũng đọc được. Khung hai, hai cách ký: dùng một bí mật chung thì ai kiểm được cũng ký được; dùng cặp khóa thì khóa riêng ký, khóa công khai kiểm. Khung ba, bên kiểm phải tự chốt danh sách thuật toán, từ chối alg là none, kiểm tiếp exp, aud, iss, và không để bí mật trong payload.](../../diagrams/sd-14-020-main.svg)

## Từ viết tắt

- **JWT** (JSON Web Token) — mã thông báo web dạng JSON: một chuỗi chữ gồm ba phần nối bằng dấu chấm, mang các thông tin (claim) về một chủ thể và có dấu ký để bên nhận kiểm.
- **JSON** (JavaScript Object Notation) — ký pháp đối tượng JavaScript: cách ghi dữ liệu thành văn bản gồm các cặp tên và giá trị, như `{"sub":"alice"}`.
- **HMAC** (Hash-based Message Authentication Code) — mã xác thực thông điệp dựa trên hàm băm: tính ra từ thông điệp và một khóa bí mật, nên ai có cùng khóa thì tính lại và so khớp được.
- **SHA** (Secure Hash Algorithm) — họ thuật toán băm: biến dữ liệu bất kỳ thành một chuỗi cố định; SHA-256 là một loại trong họ này.
- **RSA** (Rivest-Shamir-Adleman) — tên một thuật toán mã hóa khóa công khai, đặt theo ba tác giả.
- **ECDSA** (Elliptic Curve Digital Signature Algorithm) — thuật toán chữ ký số dùng đường cong elliptic: ký bằng khóa riêng, kiểm bằng khóa công khai.
- **JWE** (JSON Web Encryption) — mã hóa web dạng JSON: dạng token khác trong họ JWT, ở đó payload được mã hóa nên người không có khóa giải mã thì không đọc được.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng chuyên về bảo mật ứng dụng, có các hướng dẫn mà bài dùng để đối chiếu.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.

## Đọc hình

Các lần thử dùng Python 3.13, PyJWT 2.14.0 và `cryptography` 50.0.1 với khóa tạm, chạy cục bộ. Token mẫu mang payload `{"sub":"alice","role":"user","iat":1700000000}`.

**Khung 1 · Ba phần nối bằng dấu chấm.** Ở dạng gọn, JWT là `header.payload.signature`. Header và payload là văn bản JSON được viết lại bằng base64url: một cách ghi dữ liệu thành chữ chỉ gồm chữ cái, chữ số, `-` và `_`, không có dấu `=` đệm ở cuối (theo MDN). Token mẫu dài 143 ký tự và không có dấu `=`.

- Header, ở token mẫu là `{"alg":"HS256","typ":"JWT"}`: `alg` là thuật toán ký, `typ` là loại token.
- Payload: các claim, tức những khẳng định về token và chủ thể của nó. Tài liệu PyJWT liệt kê các tên đã đăng ký: `iss` (bên phát hành), `sub` (chủ thể), `aud` (bên nhận), `exp` (hết hạn), `nbf` (chưa hợp lệ trước thời điểm này), `iat` (thời điểm phát hành), `jti` (mã riêng của token). Tài liệu ghi cả bảy là tùy chọn.
- Signature: dấu ký tính trên đúng chuỗi `header.payload`. OWASP nói nó bảo vệ cả header lẫn claim.

Đọc hai phần đầu không cần khóa: `jwt.get_unverified_header(token)` trả về `{'alg': 'HS256', 'typ': 'JWT'}` và `jwt.decode(token, options={"verify_signature": False})` trả về payload. Base64url chỉ là cách viết lại, không giấu gì (về khác biệt giữa encoding và encryption xem [bài sd-14-002](../sd-14-002/lesson.md)). Tài liệu PyJWT cảnh báo cách đọc này bỏ qua việc kiểm dấu ký, nên không thể tin nội dung đọc ra.

Signature thì khác. Đổi đúng một ký tự trong 143 ký tự của token (ở payload, `alice` thành `alic!`): PyJWT báo `InvalidSignatureError`, dù payload đã sửa vẫn đọc được bình thường.

**Khung 2 · Hai cách ký.** Với một bí mật chung (`HS256`, tức HMAC với SHA-256), bên phát hành và bên kiểm giữ cùng một khóa, và khóa ấy vừa tính dấu ký vừa kiểm lại. Thử: ai cầm khóa cũng tự tạo được token `role: admin` mà bên kiểm chấp nhận. Kiểm được nghĩa là ký được.

Với cặp khóa (`ES256` dùng ECDSA, `RS256` dùng RSA), khóa riêng ký, khóa công khai kiểm. Thử: token `ES256` và `RS256` đều kiểm được chỉ với khóa công khai; kiểm bằng khóa công khai của cặp khác thì báo `InvalidSignatureError`. Nhờ vậy một bên ký được cho nhiều bên kiểm, vì bên kiểm chỉ cần thông tin công khai (OWASP).

**Khung 3 · Bên kiểm phải tự quyết.** Header do người gửi viết, nên `alg` trong token chỉ là điều người gửi tuyên bố. Bên kiểm phải đưa ra danh sách thuật toán chấp nhận từ phía mình: PyJWT từ chối mọi `alg` ngoài danh sách bằng `InvalidAlgorithmError`, và tài liệu của nó dặn không tính danh sách từ `alg` của token. Thử: token `alg: none` (không có dấu ký) bị từ chối khi bên kiểm chỉ nhận `HS256`; token ký `HS256` bị từ chối khi bên kiểm chỉ nhận `RS256`.

Dấu ký đúng cũng chưa đủ. Thử: `exp` đã qua thì `ExpiredSignatureError`; `nbf` ở tương lai thì `ImmatureSignatureError`; `aud` không khớp bên nhận thì `InvalidAudienceError`. Token không có `exp` vẫn được nhận theo mặc định; muốn bắt buộc thì truyền `options={"require": ["exp"]}` (thử: `MissingRequiredClaimError`).

## Giới hạn cần nhớ

Ký không phải mã hóa. Dấu ký cho biết payload không bị sửa và (tùy cách ký) ai có thể đã tạo ra nó; nó không giấu payload. OWASP nhắc rằng ai có token cũng đọc được mọi claim, và claim lộ cả ở những chỗ ngoài đường truyền như nhật ký ứng dụng, bộ nhớ của trình duyệt hay tiêu đề referrer. Cách đơn giản nhất là đừng đưa thông tin nhạy cảm vào token. Muốn payload kín thì có JWE, một dạng khác nằm ngoài phạm vi bài này. Với bí mật chung, dấu ký hợp lệ cũng chỉ cho biết token do một người giữ bí mật ấy tạo ra, không cho biết là người nào (OWASP).

## Nhìn hình trả lời

Một dịch vụ báo giá chỉ cần kiểm token, và được giao bí mật chung `HS256` để kiểm. Ngoài kiểm, nó còn làm được gì? Muốn nó chỉ kiểm được thì đổi gì ở khung hai?

<details>
<summary>Xem đáp án</summary>

Với cùng bí mật, dịch vụ ấy tạo được token tự đặt, ví dụ `role: admin`, mà mọi bên giữ bí mật đó sẽ chấp nhận, vì kiểm và ký dùng cùng một khóa (đã thử với PyJWT).
Đổi sang cặp khóa, ví dụ `ES256`: bên phát hành giữ khóa riêng, dịch vụ chỉ nhận khóa công khai, nên kiểm được mà không ký được (đối tượng khóa công khai của `cryptography` không có hàm `sign`). Bên kiểm vẫn phải cố định danh sách thuật toán là `["ES256"]`, và khóa công khai ấy phải thật sự là của bên phát hành: xem [bài sd-14-015](../sd-14-015/lesson.md) và [bài sd-14-014](../sd-14-014/lesson.md).

</details>

<details>
<summary>Xem sâu hơn: thử nghiệm và điều đã chỉnh so với bài nguồn</summary>

Tự dựng một token `HS256` bằng `hmac`, `hashlib` và base64url, rồi so với đầu ra của PyJWT (chạy ra `True`):

```python
import base64, hashlib, hmac, json, jwt

def b64u(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

secret = b"0123456789abcdef0123456789abcdef"  # 32 byte, chỉ để thử
header = {"alg": "HS256", "typ": "JWT"}
claims = {"sub": "alice", "role": "user", "iat": 1700000000}

head = b64u(json.dumps(header, separators=(",", ":")).encode())
body = b64u(json.dumps(claims, separators=(",", ":")).encode())
sig = hmac.new(secret, f"{head}.{body}".encode(), hashlib.sha256).digest()
token = f"{head}.{body}.{b64u(sig)}"

print(token == jwt.encode(claims, secret, algorithm="HS256"))
```

Dấu ký tính trên chuỗi chữ chứ không trên ý nghĩa của JSON: viết cùng payload ấy với dấu cách (`{"sub": "alice", ...}`) rồi giữ dấu ký cũ cũng báo `InvalidSignatureError`.

Số đo, một lần trên máy biên soạn: cùng payload, dấu ký dài 32 byte với `HS256`, 64 byte với `ES256` và 256 byte với `RS256` (khóa RSA 2048 bit); token dài 143, 186 và 442 ký tự. Cặp khóa đổi lấy dấu ký dài hơn.

Về `alg: none`: OWASP nói một số thư viện từng nhận nó theo mặc định, khiến kẻ tấn công tự làm token giả; OWASP cho rằng nay thư viện đã sửa, nhưng vẫn dặn bảo đảm bên kiểm không nhận. Với PyJWT 2.14.0, token `alg: none` bị từ chối khi `algorithms=["HS256"]`, cả khi viết `None` hay `NONE`; gọi `decode` mà không truyền `algorithms` báo `DecodeError`; khi danh sách chỉ có `none` thì kiểm vẫn báo `InvalidSignatureError`.

Về nhầm lẫn thuật toán: OWASP mô tả việc kẻ tấn công ký token bằng `HS256` với khóa công khai của bên phát hành làm bí mật, hy vọng thư viện dùng khóa ấy như bí mật HMAC; biện pháp là cố định thuật toán chấp nhận và không trộn hai họ thuật toán. Thử: token `HS256` ký tay bằng văn bản `PEM` của khóa công khai bị từ chối với `algorithms=["RS256"]` (`InvalidAlgorithmError`); với danh sách trộn `["RS256", "HS256"]`, PyJWT báo `InvalidKeyError` vì không cho dùng khóa bất đối xứng làm bí mật HMAC (OWASP ghi đây là biện pháp giảm nhẹ của bản PyJWT gần đây). Thư viện khác có thể khác, nên đừng dựa vào đó.

Về khóa: OWASP yêu cầu bí mật `HS256` do bộ sinh ngẫu nhiên an toàn tạo, không phải mật khẩu, dài ít nhất 256 bit, và riêng cho từng cặp bên phát hành và bên nhận. Khóa HMAC 5 byte làm PyJWT 2.14.0 phát `InsecureKeyLengthWarning`. Bảng của OWASP xếp `ES256`, `PS256` và `EdDSA` là nên dùng, còn `RS256` là không khuyến nghị; vì thế bài lấy `ES256` làm ví dụ chính và chỉ thử `RS256` thêm.

Điều đã chỉnh so với bài nguồn:

- Bài nguồn gọi JWT là cách truyền thông tin "an toàn" và nói signature làm nó "bảo mật". Dấu ký bảo vệ tính nguyên vẹn, không giữ kín; payload chỉ được viết lại bằng base64url nên ai cũng đọc được.
- Bài nguồn tả signature tạo từ "khóa bí mật" và nói bí mật phải chia sẻ cho bên kiểm, nhưng không nói hệ quả: bên kiểm cũng ký được. Mô tả ấy chỉ khớp cách ký bằng bí mật chung; với cặp khóa là khóa riêng ký.
- Bài nguồn nói header "chỉ định thuật toán" và không nhắc việc kiểm `exp`, `aud`, `iss`. Bài này thêm: bên kiểm cố định danh sách thuật toán, từ chối `alg: none`, kiểm cả claim.
- Bài nguồn chia claim thành "registered, public, private"; bài này không kiểm được cách chia ấy (không đọc được đặc tả chính thức) và chỉ dùng các tên đã đăng ký mà PyJWT và OWASP nêu. Tiêu đề bài nguồn gắn JWT với xác thực không giữ trạng thái; bài này không đánh giá điều đó.
- Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/jwt-101-key-to-stateless-authentication.md): ba thành phần và hai kiểu chữ ký.
- [OWASP — JSON Web Token Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/3e2db6bf3f5f0c807aef8a8fc84e395acce0292c/cheatsheets/JSON_Web_Token_Cheat_Sheet.md): cấu trúc token, bí mật chung và cặp khóa, `alg: none`, nhầm lẫn thuật toán, `iss` và `aud`, JWT không giữ kín. Đọc từ bản clone của kho.
- [PyJWT — usage](https://github.com/jpadilla/pyjwt/blob/c6fe464b356ff4b1ebc9ba62172d331a40aa27df/docs/usage.rst) và [PyJWT — algorithms](https://github.com/jpadilla/pyjwt/blob/c6fe464b356ff4b1ebc9ba62172d331a40aa27df/docs/algorithms.rst), tại commit của bản 2.14.0: các claim đã đăng ký, danh sách `algorithms`, đọc không kiểm dấu ký, độ dài khóa tối thiểu. Đọc qua tệp thô của kho.
- [MDN — Base64](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/base64/index.md): biến thể base64 an toàn cho địa chỉ web. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-18. Các số đo (độ dài dấu ký và token) là một lần đo trên máy biên soạn với PyJWT 2.14.0 và `cryptography` 50.0.1. Các văn bản đặc tả chính thức của JWT không truy cập được nên không được trích dẫn. Cách chia ba khung, các lần thử và cách ghép các nguồn là của người biên soạn. Bài viết và hình được thiết kế độc lập.

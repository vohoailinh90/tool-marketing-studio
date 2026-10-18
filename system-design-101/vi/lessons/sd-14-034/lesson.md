# JWT cho người mới: chiếc hộp trong suốt có dấu niêm phong

**Một JWT “đã ký” giống chiếc hộp trong suốt có dấu niêm phong: ai cầm hộp cũng đọc được bên trong. Dấu chỉ giúp người nhận biết hộp có bị sửa sau khi niêm phong hay không.**
Bài này chỉ nói về JWT đã ký (tên kỹ thuật JWS) bằng một bí mật dùng chung, thuật toán `HS256`; “ba phần nối bằng dấu chấm” là cấu trúc của riêng loại đã ký. Bài có một thí nghiệm nhỏ bằng Python và không dạy cách dùng JWT trong sản phẩm thật.

![Ba khung dọc. Khung một, JWT đã ký gồm ba phần nối bằng dấu chấm: nhãn ghi cách niêm phong, nội dung viết bằng JSON, và dấu niêm phong tính từ nhãn, nội dung và một bí mật; nhãn và nội dung ai cũng đọc được. Khung hai, người nhận tách ba phần, tự tính lại dấu từ bí mật mình giữ rồi so hai dấu: khớp thì chưa bị sửa, lệch thì bỏ hộp. Khung ba, ba điều cần nhớ: nhãn và nội dung ai cũng đọc được; dấu chỉ cho biết hộp có bị sửa hay không; ai giữ bí mật dùng chung cũng niêm phong được hộp mới.](../../diagrams/sd-14-034-main.svg)

## Từ viết tắt

- **JWT** (JSON Web Token) — mã thông báo web dạng JSON: chuỗi chữ mang vài thông tin, ví dụ tên và cấp độ, để bên này đưa cho bên kia.
- **JWS** (JSON Web Signature) — chữ ký web dạng JSON: tên kỹ thuật của JWT loại đã ký, loại bài này nói tới.
- **JWE** (JSON Web Encryption) — mã hóa web dạng JSON: tên kỹ thuật của JWT loại mã hóa, nằm ngoài phạm vi bài.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: văn bản gồm các cặp tên và giá trị, ví dụ `{"name":"Minh"}`.
- **HMAC** (Hash-based Message Authentication Code) — mã xác thực thông điệp dựa trên hàm băm: trộn bí mật vào dữ liệu rồi băm ra một dãy ngắn; thiếu bí mật thì không tính lại được.
- **OWASP** (Open Worldwide Application Security Project) — tổ chức cộng đồng về bảo mật ứng dụng, có hướng dẫn mà bài dùng để đối chiếu.

## Đọc hình

Các lần thử dùng Python 3.13 (`hmac`, `hashlib`, `base64`) và một bí mật tạm sinh ngẫu nhiên; nội dung ví dụ là `{"name":"Minh","level":1}`.

**1 · Ba phần.** JWT đã ký là một chuỗi gồm ba phần nối bằng hai dấu chấm. Nhãn (header) ghi cách niêm phong, ví dụ `"alg":"HS256"`; nội dung (payload) là thông tin cần gửi. Cả hai là JSON đổi sang base64url, một cách viết byte thành chữ in được: đó là mã hóa ký tự, không phải mã hóa bảo mật (xem [bài sd-14-002](../sd-14-002/lesson.md)). Phần ba là dấu.

**2 · Hộp trong suốt.** Không cần khóa nào: giải base64url là đọc ra `{"alg":"HS256","typ":"JWT"}` và `{"name":"Minh","level":1}`. Nhân tiện, JWT thường bắt đầu bằng `eyJ`, tức phần mở đầu `{"` của nhãn sau khi đổi sang base64url.

**3 · Dấu niêm phong.** Dấu là HMAC (hàm băm 256 bit) của đoạn “nhãn.nội dung”, lấy bí mật làm khóa. PyJWT 2.14.0 nhận token tự làm là hợp lệ, và khi tạo token từ cùng dữ liệu với cùng bí mật thì cho ra đúng chuỗi ấy: hộp tự làm là một JWT thật.

**4 · Người nhận kiểm.** Tách ba phần, tự tính lại dấu từ hai phần đầu cùng bí mật của mình, rồi so với phần thứ ba. Đổi đúng một ký tự trong nội dung (`"level":1` thành `"level":9`), giữ nguyên dấu cũ: phép kiểm báo lệch, PyJWT báo `InvalidSignatureError`. Đổi một chữ của nhãn (`JWT` thành `JWS`) cũng lệch, vì dấu bao cả nhãn lẫn nội dung.

**5 · Ai niêm phong được hộp mới?** Dùng chính bí mật ấy niêm phong `{"name":"Minh","level":9}`: phép kiểm báo hợp lệ, và người nhận không thấy khác gì một hộp thật. Dùng một bí mật khác: lệch. Với bí mật dùng chung, dấu hợp lệ chỉ nói “một người giữ bí mật này đã niêm phong hộp”, chứ không nói người đó là ai.

## Giới hạn cần nhớ

Hình ảnh chiếc hộp dừng lại ở ba chỗ.

**Hộp không giấu gì.** OWASP nói JWT đã ký bảo đảm hộp nguyên vẹn và xác thực nhưng không giữ kín: nội dung chỉ qua base64url, ai có token cũng đọc được, kể cả khi nó nằm trong log hay bộ nhớ của trình duyệt. Đừng bỏ vào đó điều cần giấu. Đọc được cũng chưa là tin được: PyJWT ghi rõ nội dung đọc mà không kiểm dấu thì không thể tin là nguyên vẹn hay xác thực.

**Bí mật không phải “mật khẩu”.** OWASP khuyên không dùng mật khẩu làm bí mật HMAC: nên sinh bằng bộ sinh số ngẫu nhiên an toàn, dài ít nhất bằng đầu ra (256 bit cho `HS256`), và dùng riêng cho từng cặp bên cấp, bên nhận, vì chung một bí mật cho nhiều bên nhận thì một bên có thể làm giả token. Muốn chỉ người giữ khóa riêng mới niêm phong được thì dùng cặp khóa và chữ ký số, bên nhận chỉ cầm khóa công khai ([bài sd-14-015](../sd-14-015/lesson.md)).

**Bài bỏ qua gì, và vì sao.** JWT mã hóa (JWE: hộp thật sự kín, cấu trúc khác), thời hạn, việc kiểm token có dành cho mình không, chuyện bên nhận tự chọn thuật toán, thu hồi và cặp khóa. Mỗi mục đủ cho một bài, còn người mới cần nắm trước ý “trong suốt, có niêm phong”. JWT so với session: [bài sd-14-010](../sd-14-010/lesson.md); phần còn lại có trong bản cheat sheet của OWASP.

## Nhìn hình trả lời

Máy chủ gửi cho Minh hộp có `"level":1`. Minh mở hộp, sửa thành 9 và gửi lại, giữ nguyên dấu. Máy chủ sẽ làm gì? Và điều gì khác đi nếu một dịch vụ khác cũng giữ cùng bí mật?

<details>
<summary>Xem đáp án</summary>

Máy chủ tính lại dấu từ nội dung mới, thấy nó lệch với dấu cũ nên bỏ hộp; Minh không có bí mật nên không tính được dấu mới.
Dịch vụ giữ cùng bí mật thì làm được: nó niêm phong hộp `"level":9` và máy chủ coi là hợp lệ, vì dấu không ghi ai đã niêm phong (bước 5). Vì vậy bí mật dùng chung chỉ nên nằm ở những bên bạn tin hoàn toàn.

</details>

<details>
<summary>Xem sâu hơn: tự chạy thử, và điều đã chỉnh so với bài nguồn</summary>

Đây là toàn bộ thí nghiệm. Chuỗi token đổi theo mỗi bí mật tạm; bốn dòng đúng/sai lặp lại: True, False, True, False.

```python
import base64, hashlib, hmac, json, secrets

def b64(raw): return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
def unb64(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
def seal(data, key): return b64(hmac.new(key, data.encode(), hashlib.sha256).digest())
def make(payload, key):
    head = b64(b'{"alg":"HS256","typ":"JWT"}')
    body = b64(json.dumps(payload, separators=(",", ":")).encode())
    return f"{head}.{body}.{seal(head + '.' + body, key)}"
def ok(token, key):
    head, body, mark = token.split(".")
    return hmac.compare_digest(seal(head + "." + body, key), mark)

key = secrets.token_bytes(32)
token = make({"name": "Minh", "level": 1}, key)
head, body, mark = token.split(".")
print(unb64(head), unb64(body))                 # đọc không cần khóa
print(ok(token, key))                           # True
edited = b64(unb64(body).replace(b'"level":1', b'"level":9'))
print(ok(f"{head}.{edited}.{mark}", key))       # False
print(ok(make({"name": "Minh", "level": 9}, key), key))                      # True
print(ok(make({"name": "Minh", "level": 9}, secrets.token_bytes(32)), key))  # False
```

Bài nguồn dạy bằng hình ảnh chiếc hộp đặc biệt; bài này giữ hình ảnh và sửa năm chỗ.
Nguồn nói “một JWT có ba phần” mà không phân loại: điều đó chỉ đúng với loại đã ký, còn JWE có cấu trúc khác.
Nguồn gợi ý hộp che nội dung: nội dung JWT đã ký ai cũng đọc được.
Nguồn nói dấu làm từ “mã bí mật giống mật khẩu” mà chỉ người gửi tạo được: OWASP khuyên không dùng mật khẩu, và với bí mật dùng chung ai giữ nó cũng tạo được dấu.
Nguồn nói máy chủ đọc nhãn và nội dung để biết bạn là ai: chỉ nên tin sau khi kiểm dấu.
Nguồn nói người gửi biết nếu có người sửa: chính người nhận phát hiện, khi tự tính lại dấu.
Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/explaining-json-web-token-jwt-to-a-10-year-old-kid.md): hộp có nhãn, nội dung và dấu.
- [OWASP — JSON Web Token Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/1c3144a85e9aa1b50bef773683405fcc626ce6e1/cheatsheets/JSON_Web_Token_Cheat_Sheet.md): cấu trúc, HMAC so với chữ ký số, yêu cầu với bí mật, JWT đã ký không giữ kín. Đọc từ bản tải về ở commit đó.
- [PyJWT — Usage Examples](https://github.com/jpadilla/pyjwt/blob/16231abfd1d8eab4953e8779b3017b859c88565e/docs/usage.rst): ví dụ `HS256`, lưu ý về đọc nội dung không kiểm dấu. Đọc từ bản tải về ở commit đó; thí nghiệm chạy với PyJWT 2.14.0 đã cài.

Đã đọc nguồn ngày 2026-10-18. Kết quả chạy là một lần đo trên máy biên soạn (Python 3.13.16). Hình ảnh chiếc hộp trong suốt có dấu niêm phong và cách chia bài là của người biên soạn. Bài viết và hình được thiết kế độc lập.

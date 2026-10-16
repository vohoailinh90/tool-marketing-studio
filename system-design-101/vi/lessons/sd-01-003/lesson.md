# Mã HTTP lạ: máy khách đọc số, không đọc tên

**Với một mã trạng thái mà nó không biết, máy khách tin chữ số đầu tiên trước hết.** Năm mã hay được kể như chuyện vui (218, 420, 451, 530, 418) làm mẫu thử cho một câu hỏi thực dụng: khi API của bạn trả một mã lạ, phần mềm gọi API sẽ làm gì, và vì sao mã chuẩn đáng chọn hơn mã dễ nhớ?

![Bốn khung dọc. Một: chữ số đầu là lớp; 218 thuộc nhóm hai trăm nên được coi là thành công, còn 420, 418, 451 là lỗi phía bên gọi và 530 là lỗi phía máy chủ. Hai: tên không đi theo số; 218, 420 và 530 không có trong bảng tên của Python. Ba: danh sách liệt kê tường minh bỏ sót; thư viện được cấu hình thử lại 500, 502, 503 và 504 sẽ thử lại 500 nhưng không thử lại 530. Bốn: 429 kèm Retry-After khiến máy khách chờ rồi thử lại, còn 420 thì không. Kết quả đo một lần trên một máy.](../../diagrams/sd-01-003-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt hoặc chương trình gửi yêu cầu và máy chủ trả lời; mã trạng thái HTTP là số ba chữ số trong câu trả lời, cho biết kết quả.
- **IANA** (Internet Assigned Numbers Authority) — tổ chức giữ danh sách đăng ký chính thức các con số và tên dùng trên Internet, trong đó có mã trạng thái HTTP.
- **RFC** (Request for Comments) — "đề nghị bình luận": loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; nhiều RFC là tiêu chuẩn.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: tập quy ước để một chương trình dùng chức năng của chương trình khác.

## Đọc hình

1. **Chữ số đầu là lớp.** RFC 9110 (mục 15) yêu cầu máy khách hiểu *lớp* của mọi mã, theo chữ số đầu, và coi mã không nhận ra như mã tròn trăm của lớp đó: gặp 471 thì xử lý như 400. Thử với bốn công cụ ngày 2026-10-16 (cách thử ở phần "Xem sâu hơn"): mã lạ 420 cho đúng kết quả của 400, còn 530 đúng như 500. Ở `requests`, `urllib` và `curl --fail`, cả cặp đều là lỗi. Còn 218 nằm trong nhóm 2xx nên được coi là **thành công**: `urllib` trả về bình thường, `requests` báo `ok`, `curl --fail` thoát với mã 0. Đó là hệ quả thực tế nhất của một cái tên như "This Is Fine": nếu server dùng nhóm hai trăm cho một tình huống lỗi, bên gọi sẽ đọc nó là ổn.
2. **Tên không đi theo số.** Bảng tên trong thư viện chuẩn của Python (`http.HTTPStatus`) có 418, 429 và 451 nhưng không có 218, 420 hay 530. Máy khách chỉ chuyển lại phần chữ mà máy chủ gửi: máy chủ thử không gửi chữ nào cho ba mã đó nên `reason` rỗng, còn khi máy chủ gửi "This Is Fine" kèm 218 thì máy khách hiện đúng chữ ấy và vẫn xử lý theo số 218. Tên chỉ để người đọc; mã máy khách rẽ nhánh theo số.
3. **Danh sách liệt kê tường minh bỏ sót.** Quy tắc lớp nói cách *hiểu* một mã, không bắt thư viện *thử lại* theo lớp. Cấu hình thử lại của `urllib3` hoạt động theo danh sách. Khi chỉ liệt kê 500, 502, 503 và 504, máy chủ nhận 4 yêu cầu cho 500 (một lần cộng ba lần thử lại) nhưng chỉ 1 cho 530: thư viện không suy 530 thành "một dạng 500". Đọc mã nguồn bản đã thử (`retry.py` 2.8.0): ngoài danh sách bạn đưa ra, nó chỉ thử lại 413, 429 và 503, và chỉ khi phản hồi có `Retry-After`.
4. **429 khác 420.** Cùng một ý "bạn gọi quá nhiều", nhưng khi máy chủ trả 429 kèm `Retry-After: 1`, cấu hình thử lại mặc định chờ rồi gọi lại (3 yêu cầu, tổng khoảng 2 giây) vì 429 có trong danh sách trên; 420 chỉ đến một lần rồi dừng. RFC 6585 (mục 4) định nghĩa 429 cho giới hạn tần suất và cho phép kèm `Retry-After`. Nếu thiếu `Retry-After`, 429 cũng chỉ được gọi 1 lần với cấu hình mặc định.
5. **418 và 451 là mã chuẩn, nhưng khác bản chất.** 451 là mã đăng ký thật cho trường hợp bị buộc từ chối truy cập vì yêu cầu pháp lý (RFC 7725, mục 3). 418 xuất phát từ RFC đùa ngày Cá tháng Tư (RFC 2324); RFC 9110 (mục 15.5.19) ghi nó là "Unused" và giữ chỗ, tức không cấp cho ứng dụng khác nhưng cũng không phải một mã có nghĩa chính thức. Cả hai nằm trong nhóm 4xx nên máy khách xử lý như lỗi.

## Giới hạn cần nhớ

Phép thử chỉ gồm một máy, `curl` 8.5.0, Python 3.13.16, `requests` 2.34.2 và `urllib3` 2.8.0, chạy với một máy chủ giả cục bộ. Trình duyệt, proxy, bộ cân bằng tải hay cổng API có thể xử lý mã lạ khác (có cái đổi mã, có cái thay trang lỗi); bài chưa thử chúng. Việc 218, 420 và 530 chưa được IANA gán dựa vào lần đọc registry ngày 2026-10-12; trang registry không mở được trong lần kiểm tra này, nên chỉ có đối chiếu phụ với một danh sách mã khác cùng kết quả (xem mục nguồn). Nếu bạn tự thiết kế API: chọn mã trong bộ đã đăng ký, dùng nhóm đúng với bản chất lỗi, và coi cái tên là phần ghi chú cho người đọc.

## Nhìn hình thử trả lời

API của bạn trả **420** khi người dùng vượt hạn mức, và bạn mong ứng dụng khách dùng `urllib3` với cấu hình thử lại mặc định (`Retry(total=3)`) sẽ tự chờ rồi gọi lại. Thực tế nó không làm vậy. Vì sao, và bạn đổi gì ở phía máy chủ?

<details>
<summary>Xem đáp án</summary>

Với cấu hình mặc định, `urllib3` chỉ tự thử lại 429 (cùng 413 và 503) khi phản hồi có `Retry-After`. Một 420 không nằm trong danh sách nào nên chỉ được coi là lỗi 4xx thông thường: thư viện dừng sau một lần gọi, và bên gọi tự quyết tiếp (báo lỗi, hoặc tự viết vòng gọi lại). Đổi sang **429** và thêm `Retry-After` (số giây) để thư viện chuẩn chờ đúng khoảng bạn muốn. Với ứng dụng khách cũ đã viết cứng 420, giữ tương thích một thời gian rồi mới bỏ.

</details>

<details>
<summary>Xem sâu hơn: cách tự thử, và điều bài chưa kiểm chứng</summary>

Cách tự thử, chỉ dùng thư viện chuẩn của Python:

```python
import http.server, threading, urllib.request, urllib.error

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(int(self.path[1:]))
        self.send_header("Content-Length", "0")
        self.end_headers()

srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
for code in (200, 218, 400, 420, 530):
    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:{srv.server_address[1]}/{code}")
        print(code, "bình thường", r.status)
    except urllib.error.HTTPError as e:
        print(code, "HTTPError", e.code)
```

Kết quả ngày thử: 200 và 218 đi qua như thành công; 400, 420 và 530 đều ném `HTTPError`.

Những gì đã thử thêm: `http.client` chấp nhận dòng trạng thái 600 nhưng từ chối 099, 20 hay 1000 với lỗi `BadStatusLine`. Đọc mã nguồn thì thấy chỉ mã trong 100–999 được chấp nhận. RFC 9110 viết giá trị ngoài 100–599 là không hợp lệ, dù cài đặt thường dùng 600–999 để báo lỗi nội bộ của thư viện.

Điều chưa kiểm chứng: bài ByteByteGo kể Twitter từng dùng 420 để báo giới hạn tần suất và 218 gắn với meme "This Is Fine" cùng một cách xử lý trang lỗi của máy chủ. Hai câu chuyện lịch sử này chưa có nguồn thứ hai trong lần biên soạn; đừng xem chúng là hướng dẫn cho API hiện tại. Pantheon ghi 530 cho site bị đóng băng; không nên suy ra mọi 530 đều có nghĩa đó, vì một sản phẩm khác có thể dùng cùng số cho việc khác.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn, phiên bản cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/5-http-status-codes-that-should-never-have-been-created.md): năm mã được kể.
- [RFC 9110, mục 15 và 15.5.19](https://httpwg.org/specs/rfc9110.html): quy tắc lớp mã, mã ngoài 100–599, trạng thái 418. Đọc bản do nhóm HTTP của IETF lưu trên GitHub ngày 2026-10-16.
- [RFC 6585, mục 4](https://httpwg.org/specs/rfc6585.html): ý nghĩa 429 và `Retry-After`; [RFC 7725, mục 3](https://httpwg.org/specs/rfc7725.html): ý nghĩa 451.
- [urllib3 2.8.0, `retry.py`](https://github.com/urllib3/urllib3/blob/2.8.0/src/urllib3/util/retry.py): điều kiện thử lại; [requests 2.34.2, `models.py`](https://github.com/psf/requests/blob/v2.34.2/src/requests/models.py): `ok` và `raise_for_status`; [CPython 3.13, `http/client.py`](https://github.com/python/cpython/blob/v3.13.0/Lib/http/client.py): phạm vi mã được chấp nhận.
- [Registry mã trạng thái của IANA](https://www.iana.org/assignments/http-status-codes): 218, 420, 530 chưa gán (đọc ngày 2026-10-12, không mở được lại ngày 2026-10-16); đối chiếu phụ với danh sách của [jshttp/statuses](https://github.com/jshttp/statuses), một thư viện Node tổng hợp từ registry này, cũng không có ba mã đó.
- [Pantheon — Platform and Site Information](https://docs.pantheon.io/guides/platform-considerations/platform-site-info): 530 cho site bị đóng băng (đọc ngày 2026-10-12).

Các phép thử chạy trên máy biên soạn ngày 2026-10-16. Bài viết độc lập và hình thiết kế mới, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-01-003.json).

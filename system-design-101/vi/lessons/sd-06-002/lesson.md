# CDN phổ biến vì đâu, và máy chủ biên lưu những gì

**CDN đặt nhiều máy chủ biên ở gần người dùng; mỗi máy giữ bản sao nội dung để khỏi phải hỏi máy chủ gốc ở xa. Nhưng máy biên không tự quyết lưu gì: máy gốc dặn qua header của từng câu trả lời.**
Nắm được lời dặn đó, bạn biết vì sao một trang nhanh hẳn lên sau khi có CDN, và vì sao trang khác thì không.

![Hai khung. Khung một, trình tự giữa người dùng, máy chủ biên và máy chủ gốc: người dùng xin logo; máy biên chưa có bản sao nên hỏi máy gốc; máy gốc trả logo kèm lời dặn lưu 60 giây; máy biên cất bản sao rồi trả; lần sau máy biên trả ngay từ bản sao. Khung hai, bốn mảnh ghép: DNS chỉ người dùng tới máy biên ở gần; máy biên giữ bản sao, hết hạn hay thiếu thì hỏi lại gốc; máy gốc giữ bản chính và dặn được lưu bao lâu; phần điều khiển cấu hình và xóa bản sao trên các máy biên.](../../diagrams/sd-06-002-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy đặt ở nhiều nơi, lưu bản sao nội dung và phát cho người dùng từ máy gần họ.
- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" của Internet, đổi tên miền thành địa chỉ IP; với CDN, câu trả lời của nó chỉ người dùng tới một máy biên.
- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ và chuyển gói tin giữa các máy; địa chỉ IP là địa chỉ của một máy trên mạng.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời, kèm các header như `Cache-Control`.
- **MDN** (Mozilla Developer Network) — bộ tài liệu web do Mozilla và cộng đồng viết; bài dùng mục từ CDN và hướng dẫn về bộ nhớ đệm của nó.
- **RFC** (Request for Comments) — loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; RFC 9111 là tiêu chuẩn về bộ nhớ đệm của HTTP.

## Đọc hình

**Một lượt hỏi.** Người dùng xin một tệp, máy biên xem mình có bản sao còn hạn không. Có thì trả ngay. Không có thì hỏi máy gốc, cất một bản theo lời dặn rồi trả. Hết hạn thì hỏi lại. Lợi ích nằm ở hai chỗ: người dùng đi quãng đường ngắn hơn, và máy gốc chỉ phải trả lời một lần cho rất nhiều người.

**Các mảnh ghép.** DNS chỉ người dùng tới một máy biên gần. Máy gốc giữ bản chính. Phần điều khiển (control plane) cấu hình các máy biên và xóa bản sao khi cần; tài liệu MDN ghi rằng với bộ nhớ đệm do mình vận hành như CDN, bản đã lưu có thể bị xóa bất cứ lúc nào qua bảng điều khiển hay lời gọi, điều mà bản thân chuẩn HTTP không quy định.

**Lời dặn của máy gốc.** RFC 9111 gọi máy biên là *bộ nhớ đệm dùng chung*: nó lưu câu trả lời để dùng lại cho nhiều người, khác với bộ nhớ đệm *riêng* trong trình duyệt của một người. Vì dùng chung, nó phải theo vài luật riêng:

- `Cache-Control: private` nghĩa là bộ nhớ đệm dùng chung **không được** lưu câu trả lời này.
- `no-store` cấm mọi bộ nhớ đệm lưu.
- `s-maxage` là hạn dành riêng cho bộ nhớ đệm dùng chung và thắng `max-age`.

## Thử với nginx

Ngày 2026-10-18, bài dựng một máy gốc nhỏ bằng Python và đặt nginx 1.24 phía trước làm máy biên (bật `proxy_cache`, không chỉnh gì thêm), rồi gửi mỗi đường dẫn ba lần. nginx ghi lại kết quả của từng lượt: `MISS` là phải hỏi máy gốc, `HIT` là trả từ bản sao, `EXPIRED` là bản sao đã hết hạn.

| Máy gốc trả về | Ba lượt | Máy gốc phải trả lời |
|---|---|---|
| `public, max-age=60` | `MISS`, `HIT`, `HIT` | 1 lần |
| `max-age=60, s-maxage=2` | `MISS`, `HIT`, `HIT`; sau 3 giây: `EXPIRED` | 2 lần |
| `private, max-age=60` | `MISS` cả ba | 3 lần |
| `no-store` | `MISS` cả ba | 3 lần |
| `public, max-age=60` kèm `Set-Cookie` | `MISS` cả ba | 3 lần |
| Không có `Cache-Control` | `MISS` cả ba | 3 lần |

Phần RFC 9111 bắt buộc là phần *cấm*: bộ nhớ đệm dùng chung không được lưu câu trả lời `private`, không bộ nhớ đệm nào được lưu `no-store`, và nếu đã lưu thì `s-maxage` thắng `max-age`, nên dòng thứ hai hết hạn sau 2 giây. Còn việc *có lưu hay không* thì tùy bộ nhớ đệm: mục 2 của RFC 9111 ghi bộ nhớ đệm là tính năng hoàn toàn tùy chọn của HTTP, nên việc nginx lưu và trả `HIT` ở hai dòng đầu là lựa chọn của nginx, được phép chứ không bắt buộc. Hai dòng cuối cũng là hành vi đã thấy của nginx với cấu hình mặc định: nó không lưu câu trả lời có `Set-Cookie`, và không tự đặt hạn cho câu trả lời không ghi hạn (RFC 9111 cho phép bộ nhớ đệm tự ước một hạn trong vài trường hợp, nhưng không bắt buộc). Mỗi CDN có mặc định riêng; hãy đọc tài liệu của dịch vụ bạn dùng.

## Giới hạn cần nhớ

CDN chỉ giúp được phần nội dung mà máy gốc cho phép lưu. Với trang `private`, máy biên không được lưu, nên mọi yêu cầu đi tới CDN đều được chuyển về máy gốc; `private` vẫn cho trình duyệt giữ bản của chính người đó, nên không phải lần truy cập nào cũng tạo ra một yêu cầu. Với `no-store` thì không nơi nào được lưu. **Đừng trông vào cookie để chặn việc lưu**: RFC 9111 (mục 7.3) lưu ý `Set-Cookie` không ngăn bộ nhớ đệm lưu câu trả lời. nginx mặc định không lưu những câu trả lời đó, nhưng một CDN khác hoàn toàn có thể lưu, rồi trả trang riêng của người này cho người khác. Trang riêng của từng người phải tự ghi `Cache-Control: private` hoặc `no-store`. MDN còn nêu ba cái giá: thêm một bên thứ ba có thể hỏng hoặc bị chặn, thêm một chỗ có thể bị tấn công, và có lúc CDN của bên thứ ba còn làm trang chậm đi vì trình duyệt phải mở thêm kết nối tới một tên miền khác.

## Nhìn hình trả lời

Trang hồ sơ cá nhân của bạn trả `Cache-Control: private, max-age=300`. Sau khi bật CDN, máy gốc có bớt tải cho trang này không? Trình duyệt của người dùng thì sao?

<details>
<summary>Xem đáp án</summary>

CDN không giúp máy gốc bớt tải cho trang này: `private` cấm bộ nhớ đệm dùng chung như máy biên lưu câu trả lời, nên mọi yêu cầu đi tới máy biên đều được chuyển tiếp về máy gốc (thử với nginx cho thấy đúng như vậy).
Nhưng trình duyệt vẫn được lưu: `private` cho bộ nhớ đệm riêng của từng người giữ bản sao trong 300 giây, nên trong khoảng đó trình duyệt dùng lại bản của mình mà không gửi yêu cầu nào. Phần tải máy gốc được bớt là nhờ trình duyệt, không nhờ CDN.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm và bỏ so với bài nguồn</summary>

Bài nguồn liệt kê luồng hỏi, các thành phần và ba cách định tuyến (cân bằng tải theo vùng địa lý, anycast, điểm trao đổi Internet). Bài này giữ luồng hỏi và các thành phần, rồi đi sâu vào phần quyết định CDN có giúp được hay không: lời dặn `Cache-Control` theo RFC 9111, kèm một thử nghiệm.
Phần định tuyến không được giải thích ở đây vì bài chưa đọc tài liệu chuẩn về chúng. Bài nguồn có nêu một con số dự báo về quy mô thị trường CDN; bài này bỏ con số đó vì không có nguồn để đối chiếu.
Hành vi của nginx với `Set-Cookie` và với câu trả lời không ghi hạn chỉ là điều đã thấy trong thử nghiệm; bài chưa đối chiếu với tài liệu của nginx.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/why-are-content-delivery-networks-cdn-so-popular.md): luồng hỏi qua máy biên, các thành phần, cách định tuyến.
- [IETF HTTP Working Group — RFC 9111, bản XML tại commit cố định](https://github.com/httpwg/httpwg.github.io/blob/03f35d852e7b64668ab08fda1a8076d6d44d17ae/specs/rfc9111.xml): bộ nhớ đệm dùng chung và riêng (mục 1); điều kiện được lưu (mục 3); chỉ thị `no-store`, `private`, `s-maxage` (mục 5.2.2); bộ nhớ đệm là tính năng tùy chọn (mục 2); `Set-Cookie` không ngăn việc lưu (mục 7.3).
- [MDN — mục từ CDN, tại commit cố định](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/cdn/index.md): lợi ích và ba cái giá của CDN.
- [MDN — hướng dẫn HTTP caching, tại commit cố định](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/caching/index.md): bộ nhớ đệm do mình vận hành (CDN) xóa được bản đã lưu qua bảng điều khiển hay lời gọi.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày với nginx 1.24.0 trên một máy. Bài viết và hình được thiết kế độc lập.

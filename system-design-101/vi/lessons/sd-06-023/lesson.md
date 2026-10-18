# CDN là gì: bốn lợi ích, và điều kiện để có từng cái

**CDN là mạng các máy chủ đặt ở nhiều nơi (máy biên), giữ bản sao nội dung để người dùng tải từ chỗ gần mình thay vì từ máy gốc. Người ta thường kể bốn lợi ích: nhanh hơn, giảm tải máy gốc, chống tấn công làm sập dịch vụ, và vẫn phục vụ khi máy gốc gặp sự cố. Lợi ích nào cũng có điều kiện đi kèm.**
Bài thử hai lợi ích đo được trên một máy (giảm tải máy gốc, phục vụ khi máy gốc tắt) bằng nginx; hai lợi ích còn lại dựa vào tài liệu.

![Hai phần. Phần một, bốn thẻ lợi ích và điều kiện: giảm độ trễ vì máy biên ở gần, chỉ với nội dung đã có sẵn; giảm tải máy gốc vì nhiều người dùng chung một bản đã giữ; chống từ chối dịch vụ vì mạng lớn hứng lưu lượng, phải giấu máy gốc; tăng tính sẵn sàng vì máy gốc sập vẫn trả bản cũ, nếu bật sẵn. Phần hai, kết quả thử với nginx và một ảnh 200 KB: 100 lần tải thẳng máy gốc thì máy gốc gửi 20 MB; 100 lần qua máy biên thì máy gốc gửi 200 KB, một lần; máy gốc tắt và bản đã hết hạn thì máy biên trả lỗi 502; bật dùng bản cũ khi lỗi thì máy biên trả 200 với bản cũ.](../../diagrams/sd-06-023-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy chủ ở nhiều nơi giữ bản sao nội dung để phục vụ người dùng từ chỗ gần họ.
- **KB** (KiloByte) — kilobyte: một nghìn byte, đơn vị đo dung lượng.
- **MB** (MegaByte) — megabyte: một triệu byte.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền trang web; mã trạng thái như 200 (thành công) hay 502 (máy trung gian không lấy được câu trả lời từ máy phía sau) là của nó.
- **IP** (Internet Protocol) — giao thức Internet; địa chỉ IP là địa chỉ của một máy trên mạng.

## Đọc hình

**Giảm độ trễ.** Đường từ người dùng tới máy biên ngắn hơn tới máy gốc ở xa. Nhưng chỉ nội dung *đã có* trong bộ đệm của máy biên mới được trả nhanh; lần đầu một nội dung được hỏi ở một nơi, máy biên vẫn phải đi lấy từ máy gốc.

**Giảm tải máy gốc.** Nhiều người tải cùng một tệp thì máy gốc chỉ gửi một lần, máy biên gửi phần còn lại. Điều kiện: máy gốc cho phép giữ chung (ví dụ `Cache-Control: public, max-age=...`); trang riêng của từng người phải `private` và luôn đi tới máy gốc.

**Chống từ chối dịch vụ.** Một cuộc tấn công từ chối dịch vụ phân tán dồn lưu lượng từ rất nhiều máy để làm sập trang. Khi CDN đứng trước, lưu lượng đổ vào mạng của CDN, vốn có năng lực lớn và bộ lọc riêng. Tài liệu Cloudflare nhấn mạnh trang không phải lộ địa chỉ IP của máy gốc; ngược lại, nếu kẻ tấn công biết địa chỉ đó, họ đi vòng qua CDN.

**Tăng tính sẵn sàng.** Máy gốc tắt, máy biên có thể trả bản đã giữ, kể cả bản đã quá hạn, nhưng chỉ khi được cấu hình làm vậy và bản đó còn trong bộ đệm. Cloudflare có tính năng Always Online; nginx có chỉ thị `proxy_cache_use_stale`.

**Thử nghiệm.** Một máy gốc viết bằng Python trả ảnh 200 000 byte với `Cache-Control: public, max-age=5` và đếm byte đã gửi; nginx làm máy biên. 100 lần tải thẳng máy gốc: máy gốc gửi 100 lần, 20 000 000 byte. 100 lần qua máy biên: máy gốc gửi đúng 1 lần, 200 000 byte. Đợi 6 giây cho bản hết hạn rồi tắt máy gốc: máy biên cấu hình thường trả `502 Bad Gateway` (trạng thái bộ đệm `EXPIRED`); máy biên bật `proxy_cache_use_stale error timeout` trả `200` với trạng thái `STALE`.

## Giới hạn cần nhớ

Bốn lợi ích không tự đến khi bật CDN. Nội dung không được giữ (riêng tư, `no-store`, hết hạn quá nhanh) thì không nhanh hơn và không giảm tải. Phục vụ khi máy gốc sập chỉ áp dụng cho bản đã có, và tài liệu Cloudflare nói rõ nó không phục vụ được nội dung động khi máy gốc tắt. Bài không thử độ trễ theo khoảng cách hay tấn công thật.

## Nhìn hình trả lời

Một trang tin tức đặt sau CDN. Trong một đợt sự cố, máy gốc tắt 10 phút: trang chủ vẫn hiện, nhưng trang "Tài khoản của tôi" báo lỗi. Theo hình, vì sao?

<details>
<summary>Xem đáp án</summary>

Trang chủ là nội dung dùng chung, được máy biên giữ; nếu máy biên được phép trả bản cũ khi máy gốc lỗi, người đọc vẫn thấy trang chủ (có thể hơi cũ). Trang tài khoản là nội dung riêng, đúng ra phải gắn `private` nên không được giữ ở máy biên; không có bản nào để trả, máy biên chỉ có thể báo lỗi như `502` trong thử nghiệm. Muốn trang riêng chịu được sự cố thì phải làm máy gốc sẵn sàng hơn, CDN không thay được việc đó.

</details>

<details>
<summary>Xem sâu hơn: các chỉ thị điều khiển việc giữ bản</summary>

- `max-age` là thời gian sống cho mọi bộ đệm; `s-maxage` chỉ cho bộ đệm dùng chung như CDN và được ưu tiên hơn `max-age` ở đó. Trình duyệt bỏ qua `s-maxage`.
- `stale-while-revalidate` cho phép trả bản cũ trong lúc đi lấy bản mới; `stale-if-error` cho phép trả bản cũ khi máy gốc lỗi. Tài liệu Cloudflare ghi khi bật Always Online thì hai chỉ thị này bị bỏ qua.
- Trong thử nghiệm, nginx dùng `proxy_cache_use_stale` để quyết định khi nào trả bản cũ (lỗi kết nối, hết thời gian chờ, mã 502, 503, 504...), độc lập với tiêu đề của máy gốc.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-cdn-content-delivery-network.md): định nghĩa CDN và bốn lợi ích.
- Tài liệu Cloudflare, kho `cloudflare/cloudflare-docs` tại commit cố định: [How Cloudflare works](https://github.com/cloudflare/cloudflare-docs/blob/2ab084e257fef531e4e22a10c9a6feab7b3a4fce/src/content/docs/fundamentals/concepts/how-cloudflare-works.mdx) (proxy ngược, không lộ địa chỉ máy gốc, bộ đệm), [Bảo vệ khỏi tấn công từ chối dịch vụ](https://github.com/cloudflare/cloudflare-docs/blob/2ab084e257fef531e4e22a10c9a6feab7b3a4fce/src/content/docs/ddos-protection/about/index.mdx), [Always Online](https://github.com/cloudflare/cloudflare-docs/blob/2ab084e257fef531e4e22a10c9a6feab7b3a4fce/src/content/docs/cache/how-to/always-online.mdx) (trả bản cũ khi máy gốc không tới được, không phục vụ nội dung động), [Cache-Control](https://github.com/cloudflare/cloudflare-docs/blob/2ab084e257fef531e4e22a10c9a6feab7b3a4fce/src/content/docs/cache/concepts/cache-control.mdx) (`s-maxage`, `stale-while-revalidate`, `stale-if-error`).
- [nginx — `ngx_http_proxy_module`, tại commit cố định của kho tài liệu](https://github.com/nginx/nginx.org/blob/0ebe7b53ff30e8c4fbf348881b4c8bcec3cf27cb/xml/en/docs/http/ngx_http_proxy_module.xml): `proxy_cache_use_stale`.
- [MDN — HTTP caching, tại commit cố định](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/caching/index.md): bộ đệm riêng và dùng chung, `private`.

Thử nghiệm chạy ngày 2026-10-18 trên một máy với nginx 1.24.0 của Ubuntu và một máy gốc Python; không đo độ trễ và không thử tấn công. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

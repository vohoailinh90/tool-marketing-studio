# Tối ưu hiệu năng giao diện: gửi ít, gửi sau, gửi trước

**Tám mẹo tăng tốc giao diện web dễ nhớ hơn khi xếp theo ba câu hỏi: có gửi ít byte hơn được không (nén, bỏ mã chết), có để phần chưa cần lại sau được không (tách mã, nạp động, chỉ vẽ phần đang thấy), và phần cần ngay có được gửi trước, đúng thứ tự không (ưu tiên, tải trước, tìm nạp trước).**
Bài đo bốn mẹo trên mã thật: gói giao diện của chính kho này, một ví dụ đóng gói bằng esbuild, và một trang nhiều ảnh trong Chromium.

![Bốn phần. Gửi ít hơn, hai thẻ: nén, gzip và brotli nén tệp văn bản trước khi gửi; bỏ mã chết, khi đóng gói bỏ những hàm không ai gọi tới. Gửi sau, hai thẻ: tách mã và nạp động, phần chỉ cần khi bấm thì tải lúc bấm; chỉ phần nhìn thấy, vẽ và tải phần trong màn hình, phần dưới để sau. Gửi trước và đúng thứ tự, ba thẻ: ưu tiên, tài nguyên quan trọng và phần đầu màn hình đi trước; tải trước, báo sớm thứ trang này sắp cần; tìm nạp trước, lấy sẵn thứ trang sau có thể cần với mức ưu tiên thấp. Đo thử: gói giao diện của kho này 499 KB, gzip còn 156 KB, brotli còn 133 KB; bỏ hai hàm không dùng thì gói từ 189 KB còn 60 KB; tách phần soạn thảo thì tệp đầu còn 313 byte; trang 40 ảnh bật tải lười thì lúc tải trang chỉ tải 11 ảnh.](../../diagrams/sd-06-024-main.svg)

## Từ viết tắt

- **KB** (KiloByte) — kilobyte: một nghìn byte.
- **HTML** (HyperText Markup Language) — ngôn ngữ viết nội dung trang web; các gợi ý như tải trước được viết bằng thẻ HTML.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền trang web; nén được trình duyệt và máy chủ thỏa thuận qua tiêu đề HTTP.
- **CSS** (Cascading Style Sheets) — ngôn ngữ mô tả cách trình bày trang: màu, cỡ chữ, bố cục.
- **MDN** (Mozilla Developer Network) — bộ tài liệu web do Mozilla duy trì, nay gọi là MDN Web Docs.

## Đọc hình

**Gửi ít hơn.** *Nén*: máy chủ nén tệp văn bản (HTML, JavaScript, CSS) bằng gzip hay brotli, trình duyệt giải nén; MDN nói việc này thường đã có sẵn ở trình duyệt và máy chủ, chỉ cần cấu hình đúng. *Bỏ mã chết* (tree shaking): công cụ đóng gói dựa vào `import` và `export` để biết hàm nào không ai dùng và bỏ chúng ra khỏi gói.

**Gửi sau.** *Tách mã* chia gói thành nhiều phần tải độc lập; *nạp động* bằng `import()` là cách mã gọi phần đó đúng lúc cần, ví dụ khi người dùng bấm nút. *Chỉ phần nhìn thấy*: danh sách dài chỉ dựng các dòng đang ở trên màn hình (windowing), ảnh dưới màn hình chỉ tải khi sắp cuộn tới (`loading="lazy"`); MDN gọi chung là tải lười.

**Gửi trước, đúng thứ tự.** *Ưu tiên*: `fetchpriority` báo cho trình duyệt một ảnh hay script quan trọng hơn (hoặc kém hơn) nó tự đoán. *Tải trước* (`<link rel="preload">`) báo sớm tài nguyên trang này sắp cần, để trình duyệt tải với ưu tiên cao thay vì phát hiện muộn. *Tìm nạp trước* (`<link rel="prefetch">`) lấy sẵn thứ trang *sau* có thể cần, với ưu tiên thấp.

**Đo thử.**

- **Nén:** gói JavaScript đã dựng của giao diện trong kho này (`web/dist`) nặng 498 691 byte; gzip mức 9 còn 155 855 byte, brotli mức 11 còn 133 404 byte. Tệp CSS 36 954 byte còn 7 343 và 6 414 byte.
- **Bỏ mã chết:** một ứng dụng nhỏ chỉ dùng một trong ba hàm của một thư viện tự viết, hai hàm kia mỗi hàm mang một bảng dữ liệu lớn. esbuild 0.25.10 tắt tree shaking: 189 400 byte; bật: 59 822 byte.
- **Tách mã:** cùng ứng dụng, phần soạn thảo được gọi bằng `import()` khi bấm nút. Không tách: một tệp 59 822 byte. Tách (`--splitting`): tệp đầu 313 byte, phần soạn thảo nằm riêng 58 995 byte và chỉ được tải khi bấm.
- **Tải lười:** trang 40 ảnh (mỗi ảnh khoảng 50 KB) trên màn hình 375 × 800 trong Chromium. Không bật: tới sự kiện `load` đã tải đủ 40 ảnh (khoảng 2 017 KB). Bật `loading="lazy"`: chỉ 11 ảnh (khoảng 555 KB); một lần cuộn nhảy thẳng xuống cuối trang thì tổng cộng có 22 ảnh: 11 ảnh đầu cộng các ảnh quanh chỗ dừng; ảnh ở giữa bị nhảy qua nên không được tải.

## Giới hạn cần nhớ

Mỗi mẹo đổi một thứ lấy một thứ. Tải lười ảnh nằm ngay đầu màn hình làm ảnh quan trọng nhất hiện chậm hơn. Tách mã quá vụn thì thêm nhiều lượt tải nhỏ. Tải trước thứ không dùng là phí băng thông và chen ưu tiên của thứ cần thật. Nén thêm một tệp đã nén sẵn (phần lớn ảnh, video) gần như không được gì. Cách chắc nhất là đo trước và sau khi áp dụng.

## Nhìn hình trả lời

Trang chủ của một cửa hàng có ảnh lớn ở đầu màn hình, một danh sách 500 sản phẩm bên dưới, và một trình chỉnh ảnh chỉ mở khi khách bấm "Sửa ảnh". Áp mẹo nào cho từng phần?

<details>
<summary>Xem đáp án</summary>

Ảnh lớn ở đầu màn hình: không tải lười; nếu trình duyệt phát hiện nó muộn thì tải trước, hoặc đánh `fetchpriority="high"`. Danh sách 500 sản phẩm: chỉ dựng các dòng đang thấy (windowing) và tải lười ảnh sản phẩm bên dưới. Trình chỉnh ảnh: tách thành phần riêng, nạp bằng `import()` khi khách bấm. Cả trang: bật nén ở máy chủ và để công cụ đóng gói bỏ mã chết.

</details>

<details>
<summary>Xem sâu hơn: điều kiện để từng mẹo có tác dụng</summary>

- Tree shaking cần mã viết theo module `import`/`export`; trong thử nghiệm, phần bị bỏ là hai hàm chứa bảng dữ liệu, chuyện hay gặp với thư viện tiện ích dùng một phần nhỏ.
- MDN ghi `rel="preload"` chỉ tải và giữ trong bộ đệm, không chạy script; `rel="prefetch"` giữ kết quả trong bộ đệm HTTP trên đĩa, ưu tiên thấp, nên phải để ý tiêu đề bộ đệm của tài nguyên.
- Tải lười làm đường dựng trang ngắn lại vì bớt tài nguyên không cần ngay, theo MDN; ảnh nên có sẵn chiều rộng và chiều cao để trang không nhảy bố cục khi ảnh về.
- Bài nguồn tách "tách mã" và "nạp động" thành hai mẹo; ở đây gộp làm một thẻ vì nạp động là cách dùng phần đã tách.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-load-your-websites-at-lightning-speed.md): tám mẹo tối ưu giao diện.
- MDN, kho `mdn/content` tại commit cố định: [Compression in HTTP](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/compression/index.md), [Tree shaking](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/tree_shaking/index.md), [Code splitting](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/code_splitting/index.md), [`import()`](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/javascript/reference/operators/import/index.md), [Lazy loading](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/performance/guides/lazy_loading/index.md), [`rel="preload"`](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/html/reference/attributes/rel/preload/index.md), [`rel="prefetch"`](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/html/reference/attributes/rel/prefetch/index.md), [`fetchpriority`](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/html/reference/attributes/fetchpriority/index.md).
- [Gói giao diện đã dựng của kho này, tại commit cố định](https://github.com/vohoailinh90/tool-marketing-studio/tree/1c544ad683dad2445b66a05e029f90e44dc32615/web/dist/assets): tệp dùng để đo nén.

Thử nghiệm chạy ngày 2026-10-18: nén bằng thư viện `zlib` của Node.js 22, đóng gói bằng esbuild 0.25.10, trang ảnh trong Chromium 141 qua Playwright với máy chủ Python cục bộ. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

# Chín chỉ số hiệu năng web: mỗi chỉ số trả lời một câu hỏi

**Các chỉ số hiệu năng web không thay thế nhau được: mỗi chỉ số trả lời một câu hỏi khác nhau. TTFB hỏi máy chủ và mạng phản hồi nhanh không; số yêu cầu và dung lượng hỏi trang nặng cỡ nào; FCP hỏi bao giờ người dùng thấy thứ đầu tiên. Đo nhầm câu hỏi thì sửa nhầm chỗ.**
Thử nghiệm dưới đây đo hai trang giống hệt nhau trong Chromium, chỉ khác cách nạp một tệp CSS.

![Ba phần. Phần một, ba nhóm câu hỏi, mỗi nhóm một thẻ: máy chủ và mạng, gồm TTFB là thời gian chờ byte đầu tiên và RTT là một lượt đi về; trang nặng cỡ nào, gồm số yêu cầu, tổng dung lượng và số tài nguyên chặn hiển thị; người dùng thấy gì và khi nào, gồm DOMContentLoaded, FCP, phần đầu màn hình và thời gian tải. Phần hai, thử với một tệp CSS trả chậm 800 ms: chặn hiển thị thì FCP 940 ms, không chặn thì 132 ms; TTFB như nhau 104 ms vì việc chặn xảy ra sau byte đầu; DOMContentLoaded khoảng 120 ms ở cả hai, trước khi trang hiện chữ; sự kiện load khoảng 920 ms ở cả hai trang. Phần ba, Core Web Vitals hiện nay: LCP, phần tử lớn nhất hiện ra, tốt khi không quá 2,5 giây; INP, phản hồi khi bấm hay gõ, tốt khi không quá 200 ms; CLS, độ xô lệch bố cục, tốt khi không quá 0,1.](../../diagrams/sd-06-027-main.svg)

## Từ viết tắt

- **TTFB** (Time To First Byte) — thời gian tới byte đầu tiên: từ lúc trình duyệt gửi yêu cầu tới lúc nhận byte đầu của trả lời.
- **RTT** (Round Trip Time) — thời gian một lượt đi về: gói tin đi tới đích và xác nhận quay lại.
- **FCP** (First Contentful Paint) — lần vẽ nội dung đầu tiên: lúc trình duyệt vẽ chữ, ảnh hay hình đầu tiên.
- **LCP** (Largest Contentful Paint) — lúc vẽ xong phần tử nội dung lớn nhất trong khung nhìn.
- **INP** (Interaction to Next Paint) — từ lúc người dùng bấm, chạm hay gõ tới lúc trang vẽ lại để phản hồi.
- **CLS** (Cumulative Layout Shift) — tổng độ xô lệch bố cục: các phần tử nhảy chỗ bất ngờ khi trang đang tải.
- **CSS** (Cascading Style Sheets) — ngôn ngữ mô tả cách trình bày trang (màu, cỡ chữ, bố cục).
- **DOM** (Document Object Model) — cây đối tượng trình duyệt dựng từ trang; sự kiện `DOMContentLoaded` báo cây này đã dựng xong.
- **HTML** (HyperText Markup Language) — ngôn ngữ đánh dấu viết nội dung trang web.
- **DNS** (Domain Name System) — hệ thống đổi tên miền thành địa chỉ máy.
- **TCP** (Transmission Control Protocol) — giao thức mở kết nối tin cậy giữa hai máy.
- **TLS** (Transport Layer Security) — lớp mã hóa kết nối, phần "S" của HTTPS.
- **HTTPS** (HyperText Transfer Protocol Secure) — giao thức truyền trang web có mã hóa.
- **MDN** (Mozilla Developer Network) — bộ tài liệu web do Mozilla duy trì, nay gọi là MDN Web Docs; bài dùng các định nghĩa chỉ số của nó.

## Đọc hình

**Máy chủ và mạng.** TTFB tính từ lúc gửi yêu cầu tới byte đầu tiên của trả lời; theo MDN nó gồm cả tra DNS, bắt tay TCP và TLS, nên không chỉ đo máy chủ. RTT là một lượt đi về; trang cần nhiều lượt đi về (nhiều yêu cầu nối tiếp) thì RTT nhân lên.

**Trang nặng cỡ nào.** Số yêu cầu, tổng dung lượng và số tài nguyên *chặn hiển thị*: theo MDN, nguyên nhân hay gặp nhất là CSS và JavaScript nạp từ đầu, vì trình duyệt chờ chúng rồi mới vẽ.

**Người dùng thấy gì, khi nào.** `DOMContentLoaded` bắn khi HTML đã phân tích xong và các script hoãn (`defer`) đã chạy; nó không chờ CSS hay ảnh. FCP là lúc vẽ nội dung đầu tiên. "Phần đầu màn hình" là phần thấy được khi chưa cuộn. Thời gian tải là tới sự kiện `load`, khi trang và mọi tài nguyên đã về.

**Thử nghiệm** (Chromium 141 qua Playwright, máy chủ Python cục bộ trả HTML sau 100 ms và tệp CSS sau 800 ms; trung vị 5 lần):

| Chỉ số | CSS chặn hiển thị | CSS nạp không chặn |
|---|---|---|
| TTFB | 104 ms | 103 ms |
| `DOMContentLoaded` | 117 ms | 124 ms |
| FCP (cũng là LCP ở trang nhỏ này) | 940 ms | 132 ms |
| `load` | 920 ms | 924 ms |
| Số yêu cầu, dung lượng | 3, 2 160 byte | 3, 2 198 byte |

Cùng TTFB, cùng số yêu cầu, gần cùng dung lượng và cùng thời gian `load`, nhưng người dùng thấy chữ sớm hơn khoảng 0,8 giây khi CSS không chặn hiển thị. Trình duyệt cũng tự báo trạng thái của tệp CSS: `blocking` ở trang thứ nhất, `non-blocking` ở trang thứ hai.

## Giới hạn cần nhớ

Đo trong phòng thử (một máy, mạng cục bộ) khác đo từ người dùng thật với máy và mạng đủ loại; thư viện `web-vitals` của Google đo Core Web Vitals từ người dùng thật. Thời gian `load` và `DOMContentLoaded` dễ đo nhưng không nói người dùng thấy gì: trong thử nghiệm, cả hai gần như không đổi trong khi FCP chênh gấp bảy lần. Bài không đo INP vì cần thao tác thật.

## Nhìn hình trả lời

Sau một lần cập nhật, đội phát triển báo "thời gian tải trang không đổi, vẫn khoảng 1 giây", nhưng người dùng than trang trắng lâu hơn trước khi hiện chữ. Theo hình, nên xem chỉ số nào, và nghi gì trước?

<details>
<summary>Xem đáp án</summary>

Xem FCP (và LCP), vì đó là chỉ số đo lúc người dùng thấy nội dung; thời gian `load` không phản ánh điều này, như thử nghiệm cho thấy (`load` như nhau, FCP 132 ms so với 940 ms). Nghi trước một tài nguyên chặn hiển thị mới thêm vào, như một tệp CSS hay script đặt trong phần đầu trang; kiểm trạng thái `renderBlockingStatus` của từng tài nguyên, rồi nạp phần không cần cho lần vẽ đầu theo cách không chặn.

</details>

<details>
<summary>Xem sâu hơn: Core Web Vitals và ngưỡng</summary>

- Thư viện `web-vitals` liệt kê Core Web Vitals hiện tại là CLS, INP và LCP, và đo chúng trên người dùng thật theo cùng cách Chrome đo.
- Ngưỡng "tốt" trong mã của thư viện: LCP tới 2 500 ms, INP tới 200 ms, CLS tới 0,1; "kém" từ trên 4 000 ms, 500 ms và 0,25. Thư viện cũng có ngưỡng cho FCP (1 800 ms) và TTFB (800 ms), hai chỉ số dùng để chẩn đoán.
- Bài nguồn có chín chỉ số và chưa nhắc tới Core Web Vitals; bài này giữ chín chỉ số làm khung và thêm ba chỉ số đó.
- Cách nạp CSS không chặn trong thử nghiệm là đặt `media="print"` rồi đổi sang `all` khi tệp đã về; nó chỉ hợp với CSS không cần cho lần vẽ đầu, nếu không trang sẽ nhảy bố cục (tăng CLS).

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-9-website-performance-metrics-you-cannot-ignore.md): chín chỉ số.
- MDN, kho `mdn/content` tại commit cố định: [Time to First Byte](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/time_to_first_byte/index.md), [First Contentful Paint](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/first_contentful_paint/index.md), [Largest Contentful Paint](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/largest_contentful_paint/index.md), [Render-blocking](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/render_blocking/index.md), [Round Trip Time](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/round_trip_time/index.md), [`DOMContentLoaded`](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/api/document/domcontentloaded_event/index.md), [Page load time](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/page_load_time/index.md), [`renderBlockingStatus`](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/api/performanceresourcetiming/renderblockingstatus/index.md).
- Thư viện `web-vitals` tại commit cố định: [`README`](https://github.com/GoogleChrome/web-vitals/blob/e773747b90f0e8763aed02ba5a74358d628a828c/README.md) (Core Web Vitals, đo trên người dùng thật) và ngưỡng trong [`src/onLCP.ts`](https://github.com/GoogleChrome/web-vitals/blob/e773747b90f0e8763aed02ba5a74358d628a828c/src/onLCP.ts), [`src/onINP.ts`](https://github.com/GoogleChrome/web-vitals/blob/e773747b90f0e8763aed02ba5a74358d628a828c/src/onINP.ts), [`src/onCLS.ts`](https://github.com/GoogleChrome/web-vitals/blob/e773747b90f0e8763aed02ba5a74358d628a828c/src/onCLS.ts), [`src/onFCP.ts`](https://github.com/GoogleChrome/web-vitals/blob/e773747b90f0e8763aed02ba5a74358d628a828c/src/onFCP.ts), [`src/onTTFB.ts`](https://github.com/GoogleChrome/web-vitals/blob/e773747b90f0e8763aed02ba5a74358d628a828c/src/onTTFB.ts).

Thử nghiệm chạy ngày 2026-10-18 trên một máy; số liệu chỉ để so hai trang với nhau, không phải con số của một trang thật. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

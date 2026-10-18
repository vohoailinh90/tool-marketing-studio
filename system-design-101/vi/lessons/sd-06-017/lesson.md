# CDN hoạt động thế nào: tìm máy biên, rồi hỏi dần lên máy gốc

**Một CDN làm hai việc nối nhau: đưa người dùng tới một máy biên ở gần (chặng tìm địa chỉ), rồi trả nội dung từ bộ đệm của máy biên; máy biên chưa có thì đi lấy từ máy gốc, hoặc, nếu CDN bật bộ đệm nhiều tầng, hỏi một tầng trên trước để chỉ tầng trên mới phải hỏi máy gốc (chặng tìm nội dung).**
Ví dụ quen thuộc: cửa hàng đặt máy chủ ở châu Âu, khách ở châu Á tải ảnh sản phẩm từ một máy biên gần mình thay vì đi nửa vòng Trái Đất.

![Ba phần. Phần một, chặng tìm địa chỉ, bốn bước: hỏi tên miền qua bộ đệm DNS của máy rồi máy phân giải; DNS của trang trả một bí danh CNAME trỏ sang CDN; DNS của CDN trả máy biên gần máy phân giải, hoặc một địa chỉ anycast; trình duyệt kết nối tới địa chỉ vừa nhận. Phần hai, chặng tìm nội dung khi có nhiều tầng, ba thẻ nối bằng mũi tên: máy biên gần người dùng, có sẵn thì trả ngay, thiếu thì hỏi lên; máy tầng vùng, chỉ có khi bật bộ đệm nhiều tầng, nhiều máy biên hỏi chung; máy gốc, nơi nội dung thật nằm, có nhiều tầng thì chỉ tầng trên hỏi tới. Phần ba, kết quả thử với nginx gồm hai máy biên và một tầng vùng: lần đầu qua máy biên A hai tầng hụt và máy gốc nhận 1 yêu cầu; lần đầu qua máy biên B tầng vùng trúng và máy gốc không nhận thêm; trang giỏ hàng gắn private, no-store thì máy gốc nhận cả hai lần.](../../diagrams/sd-06-017-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy chủ đặt ở nhiều nơi, giữ bản sao nội dung để phục vụ người dùng từ chỗ gần họ.
- **DNS** (Domain Name System) — hệ thống tên miền: đổi tên như một trang web thành địa chỉ máy để kết nối.
- **CNAME** (Canonical NAME) — loại bản ghi DNS nói "tên này là bí danh của tên kia"; nhờ nó tên miền của trang trỏ được sang tên do CDN quản lý.
- **IP** (Internet Protocol) — giao thức Internet; địa chỉ IP là địa chỉ của một máy trên mạng.
- **EDNS** (Extended DNS) — phần mở rộng của DNS (tên đầy đủ trong chuẩn: Extension Mechanisms for DNS), cho phép gửi thêm thông tin kèm câu hỏi; EDNS Client Subnet là phần gửi kèm một đoạn địa chỉ của người dùng.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền trang web giữa trình duyệt và máy chủ; tiêu đề `Cache-Control` là một phần của nó.
- **MDN** (Mozilla Developer Network) — bộ tài liệu web do Mozilla duy trì, nay gọi là MDN Web Docs; bài dùng phần về bộ đệm HTTP của nó.

## Đọc hình

**Chặng 1: tìm địa chỉ.** Trình duyệt hỏi bộ đệm DNS của máy, chưa có thì hỏi máy phân giải (thường của nhà mạng hay một dịch vụ DNS công cộng). Máy phân giải lần theo hệ thống DNS tới máy chủ có thẩm quyền của tên miền. Khi trang dùng CDN, bản ghi ở đó là một CNAME trỏ sang tên của CDN, và phần còn lại do CDN quyết định. Có hai cách hay gặp:

- **Chọn bằng DNS:** máy chủ DNS của CDN trả địa chỉ một máy biên phù hợp. Nó chỉ thấy địa chỉ của *máy phân giải*, không thấy địa chỉ người dùng, trừ khi máy phân giải gửi kèm một phần địa chỉ đó (EDNS Client Subnet). Tài liệu của 1.1.1.1 ghi rõ máy phân giải này không gửi.
- **Anycast:** cùng một địa chỉ IP được nhiều trung tâm dữ liệu công bố; định tuyến Internet đưa mỗi yêu cầu tới một nơi ở gần. Tài liệu Cloudflare mô tả cách này: DNS trả địa chỉ anycast thay vì địa chỉ máy gốc.

**Chặng 2: tìm nội dung.** Máy biên có bản còn hạn thì trả ngay. Không có thì đi lấy từ máy gốc. Khi CDN bật bộ đệm nhiều tầng (Cloudflare gọi là Tiered Cache, một tùy chọn), máy biên hỏi một tầng trên trước, và chỉ tầng trên mới được hỏi máy gốc, nên máy gốc nhận ít yêu cầu và ít kết nối hơn. Hình và thử nghiệm dựng kiểu nhiều tầng này. Nội dung nào được giữ là do tiêu đề `Cache-Control` của máy gốc quyết định.

**Thử nghiệm.** Một máy gốc viết bằng Python đếm yêu cầu, một nginx làm tầng vùng, hai nginx làm máy biên A và B, mỗi tầng ghi trạng thái bộ đệm vào một tiêu đề. Ảnh `/logo.png` gắn `public, max-age=60`: lần 1 qua A, cả hai tầng `MISS`; lần 2 qua A, máy biên `HIT`; lần đầu qua B, máy biên `MISS` nhưng tầng vùng `HIT`. Máy gốc chỉ nhận 1 yêu cầu cho ảnh. Trang `/cart` gắn `private, no-store`: hai lần đều `MISS` ở cả hai tầng, máy gốc nhận 2.

## Giới hạn cần nhớ

CDN chỉ đỡ được phần nội dung được phép chia sẻ. Trang riêng của từng người (giỏ hàng, tài khoản) phải đi tới máy gốc, và nếu lỡ gắn nhầm là được chia sẻ, CDN có thể trả nội dung của người này cho người khác. Lần đầu một nội dung được hỏi ở một vùng vẫn phải đi tới máy gốc. Và "gần" ở cách chọn bằng DNS là gần máy phân giải, không nhất thiết gần người dùng.

## Nhìn hình trả lời

Sau khi bật CDN, máy gốc của một cửa hàng vẫn nhận gần như mọi yêu cầu tải ảnh sản phẩm. Theo hình và phần thử nghiệm, bạn kiểm điều gì trước?

<details>
<summary>Xem đáp án</summary>

Tiêu đề `Cache-Control` máy gốc gửi kèm ảnh. Nếu đó là `private` hay `no-store` (như trang giỏ hàng trong thử nghiệm), CDN không được giữ, nên lần nào cũng phải hỏi máy gốc. Ảnh dùng chung nên gắn `public` với một `max-age` hợp lý. Sau đó mới xem tới các nguyên nhân khác: thời gian sống quá ngắn, mỗi đường dẫn ảnh khác nhau ở tham số truy vấn, hay CDN chưa bật bộ đệm nhiều tầng.

</details>

<details>
<summary>Xem sâu hơn: điều thử nghiệm cho thấy và không cho thấy</summary>

- Ở lần 2 qua máy biên A, tiêu đề của tầng vùng vẫn ghi `MISS`: đó là bản phản hồi máy biên đã giữ từ lần 1, kể cả tiêu đề, chứ tầng vùng không được hỏi lại.
- MDN chia bộ đệm làm hai loại: bộ đệm riêng (trình duyệt) và bộ đệm dùng chung; CDN và proxy ngược là bộ đệm dùng chung do người làm dịch vụ đặt ra. `private` nghĩa là chỉ bộ đệm riêng được giữ.
- Thử nghiệm chạy cả bốn chương trình trên một máy, nên không đo được độ trễ theo khoảng cách; nó chỉ cho thấy đường đi của yêu cầu và số yêu cầu tới máy gốc. Chặng DNS không được dựng lại.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-cnd-work.md): các bước phân giải tên miền qua CNAME và bộ cân bằng tải của CDN, máy biên, máy vùng, máy trung tâm và máy gốc.
- Tài liệu Cloudflare, kho `cloudflare/cloudflare-docs` tại commit cố định: [How Cloudflare works](https://github.com/cloudflare/cloudflare-docs/blob/2ab084e257fef531e4e22a10c9a6feab7b3a4fce/src/content/docs/fundamentals/concepts/how-cloudflare-works.mdx) (trả địa chỉ anycast, proxy ngược, bộ đệm), [Cloudflare IP addresses](https://github.com/cloudflare/cloudflare-docs/blob/2ab084e257fef531e4e22a10c9a6feab7b3a4fce/src/content/docs/fundamentals/concepts/cloudflare-ip-addresses.mdx) (anycast: một địa chỉ công bố từ nhiều trung tâm), [Tiered Cache](https://github.com/cloudflare/cloudflare-docs/blob/2ab084e257fef531e4e22a10c9a6feab7b3a4fce/src/content/docs/cache/how-to/tiered-cache.mdx) (tầng dưới hỏi tầng trên, chỉ tầng trên hỏi máy gốc), [1.1.1.1 FAQ](https://github.com/cloudflare/cloudflare-docs/blob/2ab084e257fef531e4e22a10c9a6feab7b3a4fce/src/content/docs/1.1.1.1/faq.mdx) (không gửi EDNS Client Subnet).
- [MDN — HTTP caching, tại commit cố định](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/web/http/guides/caching/index.md): bộ đệm riêng và dùng chung, `private`, `no-store`, CDN là bộ đệm do dịch vụ quản lý.

Thử nghiệm chạy ngày 2026-10-18 trên một máy: nginx 1.24.0 của Ubuntu cho ba tầng bộ đệm, máy gốc là một chương trình Python nhỏ. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.

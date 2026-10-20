# Chọn bộ cân bằng tải trên đám mây: bốn ô và hai kiểu kết nối

**Trước khi so sánh sản phẩm, hãy trả lời hai câu: lưu lượng của bạn có phải HTTP(S) không, và bạn cân bằng trong một khu vực hay trên nhiều khu vực. Hai câu đó chia các bộ cân bằng tải của một nhà cung cấp đám mây thành bốn ô; câu thứ ba, "bộ cân bằng tải có tự kết thúc kết nối không", quyết định nó làm được gì với nội dung yêu cầu.**
Bài lấy phần phân loại trong tài liệu của Microsoft về Azure làm ví dụ, vì nó viết thành lời; sơ đồ bảng tóm tắt của bài nguồn không dùng ở đây.

![Hai khung. Khung một, bốn ô chọn: toàn cầu và HTTP(S) là Front Door; toàn cầu và không phải HTTP(S) là Traffic Manager, dùng DNS; khu vực và HTTP(S) là Application Gateway; khu vực và không phải HTTP(S) là Load Balancer. Khung hai, hai kiểu kết nối: xuyên suốt thì máy khách nối thẳng tới máy chủ được chọn; kết thúc kết nối thì máy khách nối tới bộ cân bằng tải, rồi nó mở một kết nối khác tới máy chủ.](../../diagrams/sd-11-039-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách trình duyệt và máy chủ web trao đổi yêu cầu và trả lời.
- **HTTPS** (HyperText Transfer Protocol Secure) — HTTP có mã hóa: nội dung đi giữa hai bên được giữ kín.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: tạo một kết nối tin cậy giữa hai máy, bên dưới HTTP.
- **UDP** (User Datagram Protocol) — giao thức gói dữ liệu người dùng: gửi gói tin rời, không dựng kết nối.
- **DNS** (Domain Name System) — hệ thống tên miền: đổi tên dịch vụ thành địa chỉ máy; một số bộ cân bằng tải chọn máy bằng cách trả địa chỉ khác nhau.
- **TLS** (Transport Layer Security) — bảo mật tầng truyền tải: lớp mã hóa dưới HTTPS.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình gọi một dịch vụ; một dịch vụ Azure trong bảng chỉ cân bằng tải cho API.
- **URL** (Uniform Resource Locator) — địa chỉ tài nguyên: chuỗi chỉ tới một trang hay tệp; phần đường dẫn của nó là chỗ bộ cân bằng tải kiểu kết thúc kết nối đọc để chọn máy.
- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; bài nhắc tên bốn loại bộ cân bằng tải của AWS.

## Đọc hình

Bài nguồn là một bảng tóm tắt dạng ảnh, kèm lời khuyên chung: khi chọn loại bộ cân bằng tải, hãy xét kiểu lưu lượng, nhu cầu mở rộng và an ninh. Dưới đây là cách cụ thể hóa lời khuyên đó bằng tài liệu của Microsoft (trang "Load balancing options"). Tài liệu chia các dịch vụ Azure theo hai trục: toàn cầu hay khu vực, và HTTP(S) hay không.

| Dịch vụ Azure | Toàn cầu hay khu vực | Kiểu lưu lượng hợp |
|---|---|---|
| Front Door | Toàn cầu | HTTP(S) |
| Traffic Manager | Toàn cầu | Không phải HTTP(S); dùng DNS |
| Application Gateway | Khu vực | HTTP(S), TCP và TLS |
| Load Balancer | Khu vực hoặc toàn cầu | Không phải HTTP(S): TCP và UDP |
| Application Gateway for Containers | Khu vực | HTTP(S), cho khối lượng chạy trong Kubernetes |
| API Management | Khu vực hoặc toàn cầu | Chỉ API HTTP(S); tài liệu nói đó không phải bộ cân bằng tải thông thường |

Bốn ô của hình là bốn dòng đầu (Load Balancer đặt ở ô "khu vực" vì cách dùng phổ biến, dù tài liệu nói nó cũng có bản toàn cầu). Hai dòng cuối là trường hợp riêng.

Hai kiểu kết nối, theo định nghĩa trong cùng tài liệu: bộ cân bằng tải **xuyên suốt** (passthrough) để máy khách nối trực tiếp tới máy chủ mà thuật toán phân phối đã chọn; bộ cân bằng tải **kết thúc kết nối** (terminating) là một proxy: máy khách nối tới nó, rồi nó mở kết nối riêng tới máy chủ. Chỉ kiểu thứ hai nhìn được nội dung HTTP, nên chỉ nó chọn máy theo đường dẫn URL hay giải mã TLS giùm máy chủ. Tài liệu xếp Application Gateway vào nhóm kết thúc kết nối.

Hai chi tiết đáng nhớ từ tài liệu. Traffic Manager chỉ trả lời DNS chứ không đứng giữa lưu lượng; vì DNS có bộ nhớ đệm, nó chuyển sang khu vực khác chậm hơn Front Door. Còn dùng một dịch vụ khu vực làm điểm vào cho các máy chủ ở nhiều khu vực thì thêm một điểm hỏng đơn lẻ và thêm độ trễ vì lưu lượng phải qua khu vực đó.

Với AWS, trang giới thiệu Elastic Load Balancing liệt kê bốn loại: Application, Network, Gateway và Classic Load Balancer. Việc xếp chúng vào lớp ứng dụng hay lớp vận chuyển trong bài này là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu từng loại.

## Giới hạn cần nhớ

Phần chi tiết theo từng dịch vụ lấy từ một nhà cung cấp; tên và giới hạn thay đổi theo thời gian, nên bảng chỉ để học cách phân loại, không để chọn sản phẩm. Tài liệu cũng nói chính nó chỉ là điểm xuất phát: mỗi ứng dụng có yêu cầu riêng, và một hệ thống thường dùng nhiều loại bộ cân bằng tải ở những chỗ khác nhau. Nhà cung cấp khác (Google Cloud) không được đọc trong bài này.

## Nhìn hình trả lời

Một ứng dụng web chạy ở hai khu vực, người dùng ở khắp nơi. Bạn muốn một điểm vào duy nhất và muốn nó chuyển sang khu vực còn lại thật nhanh khi một khu vực hỏng. Chọn ô nào?

<details>
<summary>Xem đáp án</summary>

Ô "toàn cầu, HTTP(S)", tức dịch vụ như Front Door. Dùng Traffic Manager cũng chọn được khu vực, nhưng vì dựa vào DNS và bộ nhớ đệm DNS nên chuyển chậm hơn. Dùng một dịch vụ khu vực làm cửa chung thì tạo điểm hỏng đơn lẻ. Đây là suy luận từ tài liệu đã đọc.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn chỉ có một đoạn mở đầu và một ảnh bảng tóm tắt; đoạn chữ khuyên xét kiểu lưu lượng, nhu cầu mở rộng và an ninh. Bài này không dùng ảnh đó, thay bằng hai trục và hai kiểu kết nối lấy từ tài liệu Azure, kèm lời nhắc về loại bộ cân bằng tải của AWS.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-load-balancer-cheat-sheet.md): lời khuyên chung; không dùng ảnh.
- [Microsoft — Load balancing options (kho architecture-center)](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/guide/technology-choices/load-balancing-overview.md): hai trục, bảng dịch vụ, kiểu kết nối. Đọc từ nhánh chính, không ghim commit.
- [AWS — giới thiệu Elastic Load Balancing (kho lưu trữ, commit 667a87a)](https://github.com/awsdocs/elb-user-guide/blob/667a87a2a539f1043d9dd1181b00633289146d48/doc_source/what-is-load-balancing.md): tên bốn loại bộ cân bằng tải.

Đã đọc nguồn ngày 2026-10-19. Bài không có phép thử riêng.
Bài viết và hình được thiết kế độc lập.

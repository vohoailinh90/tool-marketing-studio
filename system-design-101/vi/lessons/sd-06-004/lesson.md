# CDN cho người mới: máy chủ biên, điện toán biên và chơi game trên mây

**Ba thứ cùng mang chữ "biên" nhưng giải ba bài toán khác nhau: máy chủ biên mang *bản sao* tới gần người dùng, điện toán biên mang *phép tính* tới gần, còn chơi game trên mây thì không có gì để lưu sẵn: bộ nhớ đệm không giúp được, phải đo cả chuỗi từ lúc bấm nút tới lúc thấy hình.**
Phân biệt được ba thứ này, bạn biết CDN giúp được phần nào của một ứng dụng và phần nào thì không.

![Hai khung. Khung một, ba nghĩa của chữ biên. Máy chủ biên giữ bản sao nội dung ở gần người dùng; trong thử nghiệm với máy gốc chậm 200 mili giây, lượt có bản sao trả trong chưa tới 1 mili giây, lượt phải về gốc mất khoảng 200 mili giây. Điện toán biên chạy mã ở gần người dùng, cho phần không lưu sẵn được như trang riêng của từng người. Chơi game trên mây: máy chủ chạy game và gửi về từng khung hình, không có gì để lưu sẵn. Khung hai, cái giá: thêm một bên thứ ba có thể hỏng hay bị chặn; thêm một chỗ có thể bị tấn công để phát nội dung độc; trình duyệt không dùng chung bản đã tải giữa các trang web khác nhau.](../../diagrams/sd-06-004-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy chủ đặt ở nhiều nơi, lưu bản sao nội dung và phát cho người dùng từ máy gần họ.
- **MDN** (Mozilla Developer Network) — bộ tài liệu web do Mozilla và cộng đồng viết; bài dùng mục từ CDN của nó.
- **CSS** (Cascading Style Sheets) — ngôn ngữ mô tả cách trình bày trang web (màu, cỡ chữ, bố cục); tệp CSS giống nhau với mọi người xem.
- **RFC** (Request for Comments) — loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; RFC 9111 là tiêu chuẩn về bộ nhớ đệm của giao thức web.

## Đọc hình

**Máy chủ biên: mang bản sao tới gần.** MDN định nghĩa CDN là một nhóm máy chủ ở nhiều nơi, giữ bản sao dữ liệu để phục vụ người dùng từ máy gần nhất, và ghi rằng khoảng cách địa lý ảnh hưởng tới độ trễ. Bản sao chỉ có ích khi nhiều người cần *cùng một* nội dung: ảnh, tệp CSS, tệp JavaScript, video đã quay sẵn.

**Điện toán biên: mang phép tính tới gần.** Có những câu trả lời khác nhau với từng người (trang chào "Xin chào An", giỏ hàng, kết quả lọc theo vị trí). Không có bản sao chung nào để giữ. Một lựa chọn là *chạy mã* ở gần người dùng thay vì chỉ cất tệp: đó là ý tưởng của điện toán biên. Nó chỉ giúp khi đo thấy thời gian nằm ở quãng đường, và khi dữ liệu mà mã cần cũng nằm gần; nếu mã ở biên vẫn phải hỏi một cơ sở dữ liệu ở trung tâm, nó vẫn phải đi chặng đường dài đó, có khi còn thêm một chặng. Khi thời gian nằm ở truy vấn trung tâm thì sửa ở đó (chỉ mục chẳng hạn), hoặc để trình duyệt giữ bản riêng của người dùng, thường có ích hơn.

**Chơi game trên mây: không có gì để lưu.** Máy chủ chạy trò chơi, vẽ từng khung hình rồi gửi về như một luồng video; mỗi lần bấm nút phải đi lên máy chủ rồi mới nhận về khung hình mới. Mỗi khung hình chỉ dùng một lần cho một người, nên bộ nhớ đệm không giúp được. Thời gian từ lúc bấm tới lúc thấy hình không chỉ là đường mạng: còn có thời gian máy chủ chạy game và vẽ khung hình, nén khung hình thành video, rồi máy người chơi giải nén và hiện ra. Máy chủ ở gần và mạng ổn là cần, nhưng phải đo cả chuỗi đó mới biết khúc nào chậm.

## Thử nghiệm: bản sao giúp được gì, và không giúp được gì

Ngày 2026-10-18, bài dựng một máy gốc bằng Python cố tình chờ 200 ms trước mỗi câu trả lời (giả làm một máy ở xa), đặt nginx 1.24 phía trước làm máy biên, rồi gửi mỗi đường dẫn 10 lần:

- Tệp dùng chung (`Cache-Control: public, max-age=60`): lần đầu 204 ms (`MISS`, phải hỏi máy gốc); 9 lần sau trung vị 0,3 ms (`HIT`). Máy gốc chỉ nhận 1 yêu cầu.
- Trang riêng (`Cache-Control: private, max-age=60`): cả 10 lần đều về máy gốc, trung vị 202 ms. Máy gốc nhận đủ 10 yêu cầu.

Máy biên không làm trang riêng nhanh hơn chút nào. Đó chính là khoảng trống mà điện toán biên nhắm tới. Số đo là của một máy, máy gốc và máy biên chạy chung một máy; 200 ms là độ trễ giả lập, không phải số đo mạng thật.

## Giới hạn cần nhớ

MDN liệt kê ba cái giá của việc dùng CDN của bên thứ ba: trang của bạn phụ thuộc thêm một dịch vụ (nó hỏng, bị chặn ở một vùng hay ngừng hẳn thì trang hỏng theo); thêm một chỗ kẻ xấu có thể chiếm để phát nội dung độc; và có thể còn *chậm* hơn, vì trình duyệt phải tra thêm tên miền, mở thêm kết nối, và các trình duyệt hiện đại không dùng chung bản đã tải giữa các trang web khác nhau.

## Nhìn hình trả lời

Một ứng dụng có ba phần: ảnh sản phẩm, trang giỏ hàng của từng người, và một trò chơi chạy trên máy chủ rồi phát hình về. Với mỗi phần, máy chủ biên có giữ được một bản sao dùng chung không? Với phần không có bản sao, bạn cần đo gì trước khi chọn cách làm nó nhanh hơn?

<details>
<summary>Xem đáp án</summary>

Ảnh sản phẩm: máy chủ biên, vì mọi người xem cùng một tệp; thử nghiệm cho thấy lượt có bản sao không phải về máy gốc.
Giỏ hàng: khác nhau với từng người nên không có bản sao chung. Đo xem thời gian nằm ở quãng đường hay ở truy vấn ở máy gốc: nếu ở truy vấn thì sửa truy vấn trước; điện toán biên là một lựa chọn, chỉ đáng khi thời gian nằm ở quãng đường và dữ liệu giỏ hàng cũng đặt được ở gần.
Trò chơi: mỗi khung hình dùng một lần nên không có bản sao nào để giữ. Đo cả chuỗi từ lúc bấm tới lúc thấy hình: đường mạng, thời gian chạy game và vẽ, nén và giải nén hình; đặt máy chủ gần người chơi chỉ rút ngắn phần đường mạng.

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn</summary>

Bài nguồn (một bài viết khách mời) điểm qua máy chủ biên, điện toán biên và chơi game trên mây như ba công nghệ cùng làm trải nghiệm nhanh hơn. Bài này đặt ba thứ cạnh nhau để thấy chỗ khác: cái gì được mang tới gần, và vì sao bản sao không giúp được hai thứ sau. Thử nghiệm và ba cái giá lấy từ MDN là phần thêm.
Phần về điện toán biên và chơi game trên mây là lập luận của người biên soạn; bài chưa đối chiếu với tài liệu của một nền tảng điện toán biên hay dịch vụ game cụ thể nào, và không nêu con số độ trễ nào cho chúng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-beginner's-guide-to-cdn-content-delivery-network.md): máy chủ biên, điện toán biên và chơi game trên mây.
- [MDN — mục từ CDN, tại commit cố định](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/glossary/cdn/index.md): định nghĩa CDN, khoảng cách ảnh hưởng độ trễ, và các cái giá khi dùng CDN của bên thứ ba.
- [IETF HTTP Working Group — RFC 9111, bản XML tại commit cố định](https://github.com/httpwg/httpwg.github.io/blob/03f35d852e7b64668ab08fda1a8076d6d44d17ae/specs/rfc9111.xml): chỉ thị `private` cấm bộ nhớ đệm dùng chung lưu câu trả lời (mục 5.2.2.7), điều thử nghiệm dựa vào.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày với nginx 1.24.0 trên một máy. Bài viết và hình được thiết kế độc lập.

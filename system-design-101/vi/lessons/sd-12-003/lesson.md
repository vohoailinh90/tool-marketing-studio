# Alice gửi thư cho Bob: đường đi qua máy chủ Outlook và Gmail

**Một lá thư từ Outlook sang Gmail đi qua đúng bốn việc: ứng dụng đưa thư cho máy chủ của mình, máy chủ này tra DNS để tìm máy chủ của Gmail, rồi chuyển thư sang, và Bob lấy thư ra khi mở Gmail.**
Theo từng bước với hai cái tên cụ thể, bạn thấy mỗi giao thức nằm ở chặng nào và ai chịu trách nhiệm với thư ở từng lúc.

![Hai khung. Khung một, gửi thư: Alice dùng ứng dụng Outlook gửi thư tới máy chủ Outlook bằng SMTP; máy chủ Outlook chuyển thư tới máy chủ Gmail cũng bằng SMTP sau khi tra DNS; máy chủ Gmail trả lời đã nhận. Khung hai, nhận thư: Gmail lưu thư vào hộp thư của Bob, Bob đăng nhập, ứng dụng của Bob lấy thư về bằng IMAP hoặc POP3.](../../diagrams/sd-12-003-main.svg)

## Từ viết tắt

- **SMTP** (Simple Mail Transfer Protocol) — giao thức truyền thư đơn giản: ngôn ngữ để đẩy thư đi, từ ứng dụng sang máy chủ và giữa hai máy chủ.
- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" đổi tên miền thành thông tin để máy tìm nhau; ở đây nó cho biết máy chủ nào nhận thư của gmail.com.
- **IMAP** (Internet Message Access Protocol) — giao thức truy cập thư Internet: cho ứng dụng đọc thư vẫn nằm trên máy chủ.
- **POP** (Post Office Protocol) — giao thức bưu điện: bản đang dùng là POP3; cho ứng dụng tải thư về máy.
- **MX** (Mail eXchange) — bản ghi trao đổi thư: dòng trong DNS chỉ ra máy chủ nhận thư của một tên miền.
- **MUA** (Mail User Agent) — ứng dụng thư của người dùng: ở đây là Outlook của Alice và ứng dụng thư của Bob.
- **MTA** (Mail Transfer Agent) — chương trình chuyển thư: mỗi máy chủ thư trong bài đóng vai này khi nhận thư từ nơi khác và chuyển tiếp.
- **MDA** (Mail Delivery Agent) — chương trình giao thư: bỏ thư vào hộp thư trên máy chủ nhận.
- **RFC** (Request For Comments) — tài liệu xin ý kiến: loạt văn bản kỹ thuật của Internet, trong đó có chuẩn SMTP.

## Đọc hình

**Bước 1: Alice gửi.** Alice soạn thư trong ứng dụng Outlook, bấm gửi. Ứng dụng nói chuyện với máy chủ Outlook bằng SMTP. Từ lúc máy chủ nhận thư, việc đưa thư tới đích là việc của máy chủ, không còn là của ứng dụng; Alice có thể tắt máy.

**Bước 2: máy chủ Outlook tìm Gmail.** Địa chỉ của Bob kết thúc bằng gmail.com. Máy chủ Outlook hỏi DNS bản ghi MX của tên miền này, nhận về tên máy chủ nhận thư của Gmail, mở kết nối SMTP tới đó và đưa thư. Máy chủ Gmail trả lời đã nhận (mã 250 trong SMTP). Từ lúc đó trách nhiệm giữ thư chuyển sang Gmail.

**Bước 3: Gmail lưu thư.** Máy chủ Gmail đặt thư vào hộp thư của Bob và chờ.

**Bước 4: Bob lấy thư.** Khi Bob mở Gmail, ứng dụng của anh lấy thư mới về qua IMAP hoặc POP3.

Trên đường đi, mỗi máy chủ thư nhận thư theo chuẩn SMTP phải thêm một dòng `Received:` vào đầu phần thông tin của thư (RFC 5321, mục 4.4). Nhờ vậy, mở "xem thư gốc" ra bạn đọc được từng chặng thư đã qua, theo thứ tự từ dưới lên.

## Giới hạn cần nhớ

Hình chỉ có hai máy chủ nên trông như thư luôn đi hai nhảy; thực tế có thể có thêm máy chủ trung gian, và mỗi máy thêm một dòng `Received:`. Hình cũng bỏ qua lọc thư rác, kiểm tra người gửi có đúng là người gửi và chuyện thư đính kèm lớn. Cách ứng dụng web của Gmail lấy thư không nhất thiết là IMAP hay POP3: đó là ứng dụng riêng của Google và bài này không mô tả nó. Phần nói về mã 250 và dòng `Received:` là kiến thức của người biên soạn về chuẩn SMTP; trang chuẩn chưa mở được trong phiên viết bài.

## Nhìn hình trả lời

Alice gửi một thư cho cả Bob (gmail.com) và Carol, người dùng một tên miền khác. Máy chủ Outlook phải làm gì khác so với hình?

<details>
<summary>Xem đáp án</summary>

Nó phải tra DNS cho cả hai tên miền, vì mỗi tên miền có máy chủ nhận riêng, rồi mở một kết nối SMTP tới từng máy chủ. Thư tới Bob đi theo đúng bốn bước của hình; thư tới Carol đi theo bốn bước tương tự nhưng qua máy chủ khác. Nếu hai người cùng dùng một máy chủ nhận thì chuẩn SMTP cho phép gửi một lần cho cả hai người nhận.
Đây là suy luận từ cách SMTP hoạt động; nguồn không bàn trường hợp nhiều người nhận.

</details>

<details>
<summary>Xem sâu hơn: điều đã bổ sung so với bài nguồn</summary>

Bài nguồn là một hình và bốn bước đánh số (ứng dụng Outlook gửi bằng SMTP, tra DNS rồi chuyển sang Gmail, Gmail lưu thư, ứng dụng của Bob lấy thư bằng IMAP hoặc POP). Bài này giữ bốn bước và thêm hai điều: phản hồi đã nhận của máy chủ nhận quyết định ai chịu trách nhiệm với thư, và dòng `Received:` cho phép đọc lại đường đi.
Khác với bài trước trong nhóm (bốn vai MUA, MTA, MDA), bài này đi theo một lá thư cụ thể từ đầu đến cuối.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/design-gmail.md): bốn bước gửi và nhận thư giữa Outlook và Gmail.
- RFC 5321 (Simple Mail Transfer Protocol) mục 4.4 và 5.1: dòng `Received:` và tìm máy chủ nhận (nhớ lại từ chuẩn; chưa mở được trang trong phiên này).

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

# Sáu thuật toán cân bằng tải

**Bộ cân bằng tải chia yêu cầu cho nhiều bản sao của một dịch vụ; bài nguồn nêu sáu cách chia, bốn cách "tĩnh" và hai cách "động".**
Bài này đọc từng cách theo lời nguồn, rồi đối chiếu với tài liệu của nginx để thấy tên gọi ngoài đời ra sao.

![Hai nhóm thẻ và một khung ghi nhớ. Thuật toán tĩnh, bốn thẻ: round robin gửi lần lượt tới từng dịch vụ; sticky round-robin giữ một khách ở cùng một dịch vụ; weighted round-robin chia theo trọng số quản trị viên đặt; hash băm IP hoặc URL của yêu cầu. Thuật toán động, hai thẻ: least connections gửi tới dịch vụ có ít kết nối đồng thời nhất; least response time gửi tới dịch vụ phản hồi nhanh nhất. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-018-main.svg)

## Từ viết tắt

- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ; địa chỉ IP là địa chỉ của một máy trên mạng.
- **URL** (Uniform Resource Locator) — định vị tài nguyên thống nhất: địa chỉ của một trang hay tài nguyên trên web.

## Đọc hình

**Nhóm tĩnh (static).**
- Round robin: các yêu cầu của khách được gửi tới các bản sao của dịch vụ lần lượt theo thứ tự. Theo nguồn, các dịch vụ thường phải là loại không giữ trạng thái (stateless).
- Sticky round-robin: cải tiến của round robin. Nếu yêu cầu đầu tiên của Alice tới dịch vụ A thì các yêu cầu sau của Alice cũng tới A.
- Weighted round-robin: quản trị viên đặt trọng số cho từng dịch vụ; dịch vụ có trọng số cao hơn xử lý nhiều yêu cầu hơn.
- Hash: áp một hàm băm lên IP hoặc URL của yêu cầu đến; yêu cầu được chuyển tới bản sao tương ứng với kết quả của hàm băm.

**Nhóm động (dynamic).**
- Least connections: yêu cầu mới tới bản sao có ít kết nối đồng thời nhất.
- Least response time: yêu cầu mới tới bản sao có thời gian phản hồi nhanh nhất.

**Gặp lại trong nginx.** Tài liệu của nginx cho thấy các tên này dùng ngoài đời. Mặc định nginx chia yêu cầu theo kiểu weighted round-robin: trọng số của mỗi máy chủ mặc định là 1, và với ví dụ trọng số 5, 1, 1 thì cứ 7 yêu cầu sẽ có 5 yêu cầu tới máy đầu và mỗi máy còn lại nhận 1. Chỉ thị `ip_hash` chia theo địa chỉ IP của khách, nên yêu cầu của cùng một khách luôn tới cùng một máy chủ trừ khi máy đó không dùng được; chỉ thị `hash` chia theo khóa băm tùy chọn. Chỉ thị `least_conn` gửi yêu cầu tới máy có ít kết nối đang hoạt động nhất, có tính tới trọng số. Chỉ thị `sticky` bật "gắn phiên" (session affinity), tức yêu cầu của cùng một khách tới cùng một máy chủ. Phương pháp `least_time`, chọn máy có thời gian phản hồi trung bình ngắn nhất, nằm trong gói thương mại của nginx.

## Giới hạn cần nhớ

Nguồn chỉ mô tả từng thuật toán trong một hai câu, không nói thuật toán nào hợp với tình huống nào, không có số đo và không định nghĩa "tĩnh" với "động"; bài giữ hai tên đó như nguồn gọi. Cách một thuật toán đo "số kết nối" hay "thời gian phản hồi" cũng không được nguồn mô tả.
Phần nginx chỉ là một vài trường hợp đã đối chiếu, không phải danh sách đầy đủ; các bộ cân bằng tải khác đặt tên và cấu hình khác. Bài không kiểm tra câu "dịch vụ thường phải không giữ trạng thái" của nguồn.

## Nhìn hình trả lời

Ba máy chủ có trọng số 5, 1 và 1. Cứ 7 yêu cầu liên tiếp thì mỗi máy nhận bao nhiêu? Thuật toán nào giữ Alice ở cùng một dịch vụ cho mọi yêu cầu sau yêu cầu đầu tiên?

<details>
<summary>Xem đáp án</summary>

Theo ví dụ trong tài liệu nginx (weighted round-robin): máy đầu nhận 5, hai máy còn lại mỗi máy nhận 1.
Sticky round-robin giữ Alice ở dịch vụ mà yêu cầu đầu tiên của Alice tới.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và một danh sách lồng: nhóm tĩnh (bốn thuật toán), nhóm động (hai thuật toán), mỗi thuật toán một câu. Hình ở đây giữ đúng hai nhóm và thứ tự đó, chỉ trình bày thành thẻ; bài không dùng ảnh nguồn.
Mục "Gặp lại trong nginx" lấy từ tài liệu mô-đun upstream của nginx tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-load-balancing-algorithms.md): sáu thuật toán, hai nhóm.
- [nginx — tài liệu mô-đun upstream](https://github.com/nginx/nginx.org/blob/0ebe7b53ff30e8c4fbf348881b4c8bcec3cf27cb/xml/en/docs/http/ngx_http_upstream_module.xml): mặc định weighted round-robin, `ip_hash`, `hash`, `least_conn`, `sticky`, `least_time`. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa IP và URL trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

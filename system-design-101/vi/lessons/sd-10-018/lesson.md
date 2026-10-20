# Sáu thuật toán cân bằng tải

**Bộ cân bằng tải chia yêu cầu cho nhiều máy cùng làm một việc; bài nguồn nêu sáu cách chia: round robin, sticky round-robin, weighted round-robin, hash, least connections và least response time.**
Bài giữ sáu tên đó và cách chia nhóm "tĩnh" và "động" của nguồn, rồi giải thích từng cách bằng tài liệu của nginx và của `HAProxy`, hai bộ cân bằng tải đang dùng ngoài đời.

![Ba khối: hai nhóm thẻ và một khung ghi nhớ. Theo lượt và trọng số: round robin dùng từng máy lần lượt, sticky round-robin giữ một khách ở cùng một máy, weighted round-robin cho máy trọng số cao nhiều lượt hơn. Theo khóa băm hoặc theo tải: hash băm địa chỉ IP của khách hoặc URL để chọn máy, least connections chọn máy ít kết nối nhất, least response time chọn máy phản hồi trung bình nhanh nhất và ít kết nối nhất. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-018-main.svg)

## Từ viết tắt

- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ; địa chỉ IP là địa chỉ của một máy trên mạng.
- **URL** (Uniform Resource Locator) — định vị tài nguyên thống nhất: địa chỉ của một trang hay tài nguyên trên web.
- **IPv4** (Internet Protocol version 4) — giao thức Internet phiên bản 4: dạng địa chỉ IP gồm bốn nhóm số.
- **IPv6** (Internet Protocol version 6) — giao thức Internet phiên bản 6: dạng địa chỉ IP mới, dài hơn IPv4.
- **HA** (High Availability) — tính sẵn sàng cao: hệ thống vẫn chạy khi một phần hỏng; đây là phần đầu trong tên `HAProxy`.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời.

## Đọc hình

**Theo lượt và trọng số.**
- Round robin: tài liệu của `HAProxy` mô tả đây là cách dùng từng máy lần lượt, theo trọng số của chúng, và coi đó là cách trơn tru và công bằng nhất khi thời gian xử lý của các máy phân bố đều. Với nginx, đây là cách mặc định, và vì trọng số mặc định của mỗi máy là 1 nên các máy được dùng đều nhau. Bài nguồn nói thuật toán này thường đòi hỏi dịch vụ không giữ trạng thái (stateless); bài chưa kiểm tra điều đó.
- Sticky round-robin: nginx gọi điều tương ứng là "gắn phiên" (session affinity): chỉ thị `sticky` làm cho các yêu cầu của cùng một khách luôn đi tới cùng một máy trong nhóm, với ba cách nhận ra khách là cookie, tuyến (route) hoặc học theo giá trị (learn). Chỉ thị này từng chỉ có trong bản thương mại của nginx, và tài liệu ghi từ bản 1.27.3 trở đi nó không còn bị giới hạn như vậy.
- Weighted round-robin: người quản trị đặt trọng số cho từng máy, và máy trọng số cao được chọn nhiều lần hơn. Ví dụ trong tài liệu nginx có ba máy với trọng số 5, 1 và 1: cứ 7 yêu cầu thì 5 yêu cầu tới máy đầu, mỗi máy còn lại nhận 1.

**Theo khóa băm.**
- Hash: chọn máy từ kết quả băm một khóa. nginx có `ip_hash`, dùng ba nhóm số đầu của địa chỉ IPv4 (hoặc cả địa chỉ IPv6) của khách làm khóa, nên khách đó luôn tới cùng một máy trừ khi máy ấy không dùng được; chỉ thị `hash` cho chọn khóa tùy ý, như URL. `HAProxy` có `source` (băm địa chỉ IP nguồn) và `uri` (băm địa chỉ yêu cầu, hợp với bộ nhớ đệm trung gian vì tăng khả năng trúng bộ nhớ đệm). Cả hai tài liệu cùng cảnh báo: khi số máy đổi, nhiều khóa bị chuyển sang máy khác. nginx có tham số `consistent`, dùng băm nhất quán để chỉ một số ít khóa phải chuyển.

**Theo tải.**
- Least connections: nginx gửi yêu cầu tới máy có ít kết nối đang hoạt động nhất, có tính tới trọng số; nếu nhiều máy ngang nhau thì thử lần lượt theo weighted round-robin. `HAProxy` nói cách này hợp với giao thức có phiên rất dài và không hợp lắm với giao thức phiên ngắn như HTTP.
- Least response time: nginx có `least_time`, gửi yêu cầu tới máy có thời gian phản hồi trung bình ngắn nhất và ít kết nối nhất, đo tới lúc nhận phần đầu phản hồi hoặc tới lúc nhận đủ phản hồi. Phương pháp này nằm trong gói thương mại của nginx.

**"Tĩnh" và "động".** Bài nguồn gọi bốn cách đầu là tĩnh và hai cách sau là động, nhưng không định nghĩa hai từ này. Tài liệu `HAProxy` dùng chúng theo nghĩa khác: một thuật toán "động" cho phép đổi trọng số của máy ngay khi đang chạy (ví dụ để máy mới khởi động tăng tải dần), còn "tĩnh" thì đổi trọng số lúc chạy không có tác dụng; trong đó roundrobin và leastconn là động, còn hash, source và uri mặc định là tĩnh.

## Giới hạn cần nhớ

Bài nguồn chỉ nói mỗi cách trong một hai câu, không nói cách nào hợp với tình huống nào và không có số đo. Cách mỗi bộ cân bằng tải đo "số kết nối" hay "thời gian phản hồi" cũng không được nguồn mô tả; phần nginx và `HAProxy` chỉ là vài trường hợp đã đối chiếu, các bộ cân bằng tải khác đặt tên và cấu hình khác.
Hai cách dùng chữ "tĩnh" và "động" (của nguồn và của `HAProxy`) không trùng nhau; bài giữ cách chia của nguồn để theo danh sách, còn hình nhóm các cách theo cái chúng dựa vào.

## Nhìn hình trả lời

Ba máy chủ có trọng số 5, 1 và 1. Cứ 7 yêu cầu liên tiếp thì mỗi máy nhận bao nhiêu? Một nhóm máy dùng `ip_hash` rồi một máy được thêm vào nhóm: điều gì có thể xảy ra với các khách, và nginx cho tham số nào để giảm điều đó?

<details>
<summary>Xem đáp án</summary>

Theo ví dụ trong tài liệu nginx (weighted round-robin): máy đầu nhận 5, hai máy còn lại mỗi máy nhận 1.
Nhiều khách có thể bị chuyển sang máy khác vì kết quả băm thay đổi theo số máy; `ip_hash` không có tham số nào để giảm điều đó; nginx có tham số `consistent` của chỉ thị `hash`, nên phải đổi sang `hash` (ví dụ `hash $remote_addr consistent;`) thì mới chỉ một số ít khóa phải chuyển.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và một danh sách lồng: nhóm tĩnh (bốn thuật toán), nhóm động (hai thuật toán), mỗi thuật toán một hai câu. Bài này giữ sáu tên và hai nhãn "tĩnh", "động" của nguồn, nhưng giải thích từng cách bằng tài liệu mô-đun upstream của nginx và phần `balance` trong tài liệu cấu hình `HAProxy` tại commit cố định ở mục nguồn nên không lặp câu chữ của nguồn. Hình nhóm sáu cách theo cái chúng dựa vào (lượt và trọng số, khóa băm, tải) và không dùng ảnh nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-load-balancing-algorithms.md): chỉ lấy sáu tên, hai nhãn tĩnh và động, và nhận xét về dịch vụ không giữ trạng thái.
- [nginx — tài liệu mô-đun upstream](https://github.com/nginx/nginx.org/blob/0ebe7b53ff30e8c4fbf348881b4c8bcec3cf27cb/xml/en/docs/http/ngx_http_upstream_module.xml): mặc định weighted round-robin, trọng số, `ip_hash`, `hash` và `consistent`, `least_conn`, `least_time`, `sticky`. Đọc từ kho mã.
- [HAProxy — tài liệu cấu hình, phần balance](https://github.com/haproxy/haproxy/blob/612b87e75f399b928903141d9bf8ecf59d4f4f6b/doc/configuration.txt): `roundrobin`, `static-rr`, `leastconn`, `source`, `uri`, `hash` và nghĩa của "tĩnh", "động". Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Các câu giải nghĩa IP, IPv4, IPv6, HA, URL và HTTP trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

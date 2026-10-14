# Tường lửa: sáu cách viết một luật

**Một luật tường lửa thường gồm hai nửa: điều kiện mô tả gói tin, và hành động là cho qua hay chặn. Sáu loại luật trong bài nguồn khác nhau ở chỗ điều kiện nhìn vào cái gì.**
Bài này chạy thử từng cách viết trên Linux với nftables, để thấy mỗi cách nhìn được gì, mù ở đâu, và vì sao thứ tự luật cũng quan trọng như nội dung luật.

![Tám thẻ xếp dọc. Thẻ đầu: mọi luật tường lửa là một điều kiện cộng một hành động, gói tin khớp điều kiện thì cho qua hoặc chặn. Sáu thẻ là sáu cách viết điều kiện. Cổng: nhìn số cổng chứ không nhìn ứng dụng đứng sau, nên một dịch vụ không phải HTTP vẫn đi qua cổng được phép. Địa chỉ IP: cho hoặc chặn theo địa chỉ nguồn hay đích, danh sách trắng hoặc danh sách đen. Giao thức: TCP, UDP, ICMP, có thể không nêu cổng; luật chặn UDP không nêu cổng chặn cả hai cổng UDP đã thử trên địa chỉ đó. Thời gian: khớp theo đồng hồ của máy chạy tường lửa. Trạng thái: cho qua gói thuộc kết nối đã có, xem bài sd-14-007. Ứng dụng: thử được là nhận ra người dùng tạo gói tin, không thử được là nhận ra nội dung. Thẻ cuối: thứ tự luật có thể quyết định kết quả; luật cho kết nối đã mở mà xếp trước luật chặn thì kết nối cũ còn sống.](../../diagrams/sd-14-013-main.svg)

## Đọc hình

**Một luật = điều kiện + hành động.** Bài nguồn gọi chúng là “sáu trường hợp sử dụng”; nhìn gần hơn thì đó là sáu thứ có thể đặt vào phần điều kiện. Toàn bộ các lần thử dưới đây chạy trên một máy Linux, bằng nftables v1.0.9, với một bảng luật tạm thời trên địa chỉ loopback (đã xóa sau khi thử).

**Cổng.** Luật cho qua kết nối TCP (truyền tin có thiết lập kết nối) tới cổng 18091 và chặn cổng 18092, 18093: kết nối tới 18091 nhận được trả lời, kết nối tới 18092 quá hạn (không có trả lời). Sau đó đổi luật để cho phép cổng 18093 và dựng ở đó một dịch vụ không phải HTTP: nó vẫn trả lời bình thường. Luật cổng so khớp con số, không biết chương trình đứng sau cổng là gì; “chỉ cho 80 và 443” thực ra nghĩa là chỉ cho hai con số đó.

**Địa chỉ IP (địa chỉ của một máy trên mạng).** Luật chặn nguồn 127.0.0.2 làm một máy khách gắn với địa chỉ đó quá hạn, còn máy khách từ 127.0.0.1 vẫn vào. Dạng danh sách trắng (cho 127.0.0.1, chặn phần còn lại) cho đúng hai kết quả ấy. Luật theo địa chỉ chỉ chặn được thứ mà địa chỉ phân biệt được; địa chỉ có thể bị giả mạo, danh sách đen sẽ cũ đi và nhiều người có thể dùng chung một địa chỉ (đây là hiểu biết chung của người biên soạn, chưa chạy thử).

**Giao thức.** TCP và UDP (gửi từng gói, không thiết lập kết nối) là hai giao thức vận chuyển phổ biến. Luật `meta l4proto udp ip daddr 127.0.0.1 drop`, không nêu cổng nào, chặn cả hai trao đổi UDP tới hai cổng khác nhau (18094 và 18098), trong khi kết nối TCP tới cổng 18095 trên cùng địa chỉ vẫn chạy. Ví dụ trong bài nguồn là “chỉ TCP trên cổng 22”, tức là ghép giao thức với cổng; luật giao thức thuần chỉ cần tên giao thức. ICMP (giao thức của lệnh ping) không được thử vì máy không có công cụ ping.

**Thời gian.** Luật chặn cổng 18096 trong một khung giờ chặn kết nối khi khung giờ chứa đồng hồ của máy (14:22 giờ UTC, khung rộng 30 phút mỗi bên) và cho qua khi khung giờ nằm sau đó hai tiếng. Điều kiện thời gian là đồng hồ của máy chạy tường lửa; cách xử lý múi giờ không được thử.

**Trạng thái.** Luật theo trạng thái cho qua gói thuộc một kết nối đã có. Phần này đã có bài riêng với một lần chạy nftables: xem [bài sd-14-007](../sd-14-007/lesson.md). Ở đây chỉ dùng nó để trả lời câu hỏi về thứ tự luật bên dưới.

**Ứng dụng.** Bài nguồn nêu ví dụ cho phép hoặc chặn Skype, BitTorrent. Trên một máy, nftables nhận ra được người dùng cục bộ đã gửi gói: luật chặn cổng 18097 khi người gửi có uid (số định danh người dùng của hệ điều hành) 65534 làm một máy khách chạy dưới uid đó quá hạn, còn cùng chương trình chạy bằng root thì đi qua. Đó là nhận ra ai gửi, không phải nhận ra nội dung gói là của ứng dụng nào; việc nhận ra ứng dụng qua nội dung, như các tường lửa thế hệ mới thường làm (hiểu biết chung của người biên soạn), không được thử ở đây.

## Giới hạn cần nhớ

Mỗi loại luật chỉ thấy một khía cạnh của gói tin và mù với phần còn lại: luật cổng không biết chương trình nào đứng sau, luật địa chỉ không biết ai dùng địa chỉ, luật giao thức không biết cổng nào. Các thí nghiệm ở đây chạy trên loopback với một bảng luật nhỏ trên một máy; chúng cho thấy cách nftables xử lý từng điều kiện, không chứng minh một mạng thật được an toàn. Hành vi của các tường lửa khác có thể khác, và tôi không đọc được trang tài liệu nftables nào nên các kết luận dựa trên chính những lần chạy ấy.

## Nhìn hình trả lời

Một quản trị viên muốn chặn mọi kết nối mới tới cổng quản trị từ 22:00 đến 06:00. Lúc 21:55 một người đang giữ một kết nối đã mở. Kết nối đó có bị cắt khi khung giờ chặn bắt đầu không?

<details>
<summary>Xem đáp án</summary>

Chỉ biết khung giờ thì chưa trả lời được: kết quả phụ thuộc vào thứ tự luật. Khi thử, tôi mô phỏng việc khung giờ chặn bắt đầu bằng cách thêm luật chặn cổng trong lúc một kết nối TCP (không phải một phiên SSH, tức đăng nhập từ xa, thật) đang gửi một dòng mỗi 0,25 giây. Chỉ có luật chặn: kết nối nhận 7 dòng trong 1,5 giây trước khi thêm luật và chỉ 1 dòng trong 2 giây sau đó, tức là gần như dừng hẳn. Đặt trước luật chặn một luật `ct state established,related accept` (cho gói thuộc kết nối đã có): kết nối cũ vẫn nhận 7 dòng rồi 8 dòng; còn một kết nối mới tới cùng cổng thì bị chặn trong cả hai trường hợp.
Vậy muốn “chặn người mới nhưng không cắt người đang làm việc” thì luật cho kết nối đã mở phải đứng trước luật chặn. Đây là kết quả của một lần mô phỏng trên nftables; việc khung giờ thật mở ra theo đồng hồ không được chờ.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn viết mỗi loại luật bằng một hai câu và không nêu ví dụ kiểm chứng. Bài này giữ đủ sáu loại nhưng đổi cách trình bày: thay vì sáu “trường hợp sử dụng” rời nhau, mỗi loại là một thứ đặt vào phần điều kiện của luật, kèm kết quả quan sát được.
Ví dụ giao thức của bài nguồn (chỉ TCP trên cổng 22) ghép giao thức với cổng; bài này chạy một luật giao thức không có cổng để thấy rõ phần giao thức làm gì.
Bài nguồn trình bày luật theo thời gian như một lịch; bài này bổ sung rằng một kết nối đang mở có thể còn sống hay không tùy thứ tự luật, dựa trên lần mô phỏng ở trên.
Ví dụ ứng dụng của bài nguồn (Skype, BitTorrent) cần nhận ra ứng dụng qua nội dung; bài này chỉ thử được luật theo người dùng cục bộ trên một máy, và nói rõ việc nhận ra theo nội dung chưa được thử.
Mục theo dõi trạng thái được rút gọn thành liên kết tới bài sd-14-007, nơi đã có lần chạy nftables riêng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-firewall-use-cases.md): sáu loại luật (cổng, địa chỉ IP, giao thức, thời gian, trạng thái, ứng dụng).
- Hành vi của từng loại luật lấy từ lần chạy nftables v1.0.9 trên máy tác giả (loopback, bảng luật tạm đã xóa). Không có trang tài liệu nftables nào truy cập được nên bài không trích dẫn trang nào cho phần cú pháp luật. Phần theo dõi trạng thái xem [bài sd-14-007](../sd-14-007/lesson.md).

Đã đọc nguồn ngày 2026-10-14. Cách gom sáu loại luật thành “sáu thứ đặt vào phần điều kiện” và phần thứ tự luật là của người biên soạn. Bài viết và hình được thiết kế độc lập.

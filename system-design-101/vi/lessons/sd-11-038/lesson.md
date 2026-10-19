# Bảy mẫu hệ thống phân tán hay gặp: mỗi mẫu trả lời một vấn đề

**Ambassador, Circuit Breaker, CQRS, Event Sourcing, Leader Election, Publisher/Subscriber và Sharding là bảy tên gọi của bảy vấn đề lặp lại khi một hệ thống tách ra nhiều máy: ai thay ứng dụng nói chuyện với bên ngoài, khi nào nên thôi gọi một dịch vụ đang hỏng, đọc và ghi có nên chung một mô hình, và dữ liệu hay việc được chia cho ai.**
Bài đọc từng mẫu như câu trả lời cho một vấn đề, rồi chạy thử một mô phỏng nhỏ cho Circuit Breaker để thấy nó cứu được bao nhiêu thời gian chờ.

![Ba khung. Khung một, giữ dịch vụ khỏe: Ambassador là bên trung gian đặt cạnh ứng dụng để gọi ra ngoài; Circuit Breaker ngừng gọi khi lỗi vượt ngưỡng; Leader Election chọn một bản làm người điều phối. Khung hai, dữ liệu và thông điệp: CQRS tách mô hình đọc và ghi; Event Sourcing lưu chuỗi sự kiện thay vì trạng thái hiện tại; Publisher/Subscriber phát sự kiện cho nhiều bên nhận; Sharding chia kho dữ liệu thành nhiều phần. Khung ba, thử Circuit Breaker: không có thì chờ 80 giây, có thì chờ 16 giây.](../../diagrams/sd-11-038-main.svg)

## Từ viết tắt

- **CQRS** (Command Query Responsibility Segregation) — tách trách nhiệm ghi và đọc: phần nhận lệnh thay đổi dữ liệu và phần trả lời truy vấn được làm thành hai mô hình riêng, mỗi bên tối ưu theo cách của mình.

## Đọc hình

Định nghĩa dưới đây tóm từ trang mô tả mẫu thiết kế đám mây của Microsoft (kho tài liệu công khai); bài nguồn chỉ nêu bảy tên.

| Mẫu | Vấn đề nó trả lời | Cái giá |
|---|---|---|
| Ambassador | Ứng dụng cần theo dõi, định tuyến, bảo mật, chống lỗi khi gọi ra ngoài mà không sửa được mã của nó | Thêm một tiến trình chạy cạnh ứng dụng để quản |
| Circuit Breaker | Dịch vụ bị gọi đang hỏng lâu; cứ thử lại chỉ chờ vô ích và lan lỗi | Phải chọn ngưỡng lỗi và thời gian mở sao cho hợp |
| CQRS | Đọc và ghi cùng một mô hình thì khó tối ưu cả hai, dễ tranh chấp khóa | Hai mô hình, và phải đồng bộ giữa chúng |
| Event Sourcing | Chỉ giữ trạng thái hiện tại thì mất lịch sử và ghi đè nhau khi tải cao | Phức tạp: đổi cách lưu, xử lý song song, đổi lược đồ, truy vấn trạng thái |
| Leader Election | Nhiều bản cùng chạy một việc thì giẫm lên nhau hoặc tranh tài nguyên chung | Cần cách chọn và thay người điều phối khi nó chết |
| Publisher/Subscriber | Bên gửi không nên biết từng bên nhận, và mỗi bên nhận muốn một phần sự kiện | Gián tiếp hơn: khó thấy ai nhận gì |
| Sharding | Một máy hết chỗ chứa, hết sức tính, hết băng thông, hoặc dữ liệu phải ở đúng vùng | Truy vấn qua nhiều phần khó hơn; phải chọn khóa chia |

Trang của Microsoft về Event Sourcing nói thẳng rằng đây là mẫu phức tạp, tốn kém khi chuyển vào hay ra, và với phần lớn hệ thống cách quản lý dữ liệu truyền thống là đủ. Chỉ nên dùng khi lợi ích như dấu vết kiểm toán và khôi phục lịch sử đáng cho độ phức tạp đó.

Circuit Breaker có ba trạng thái. Đóng: yêu cầu đi qua và bộ đếm lỗi gần đây tăng khi có lỗi; vượt ngưỡng trong một khoảng thời gian thì chuyển sang mở. Mở: yêu cầu thất bại ngay không gọi đi; hết thời gian chờ thì sang nửa mở. Nửa mở: cho một số ít yêu cầu đi qua; thành công thì đóng lại, một lần lỗi thì mở lại và đếm thời gian chờ từ đầu. Nửa mở có mục đích riêng: để dịch vụ đang hồi phục không bị đổ ập cả luồng yêu cầu.

## Thử: mô phỏng Circuit Breaker

Ngày 2026-10-19, người biên soạn viết một mô phỏng với thời gian ảo. Một ứng dụng gọi một dịch vụ mỗi giây, 100 lần; dịch vụ hỏng từ giây 20 đến hết giây 59. Một lần gọi tới dịch vụ đang hỏng chờ hết thời hạn 2 giây rồi mới lỗi. Bộ ngắt: mở sau 5 lỗi liên tiếp, giữ mở 10 giây, rồi nửa mở với một yêu cầu thử.

- **Không có bộ ngắt.** Cả 100 lần đều đi tới dịch vụ; 40 lần lỗi, mỗi lần chờ 2 giây: tổng 80 giây chờ.
- **Có bộ ngắt.** Bộ ngắt mở ở giây 24 sau 5 lỗi đầu. Chỉ 64 lần tới dịch vụ, trong đó 8 lần lỗi (5 lần đầu và ba lần thử lại lúc nửa mở ở các giây 34, 44, 54); 36 lần thất bại tức thì. Tổng chờ: 16 giây. Giây 64 lần thử nửa mở thành công và bộ ngắt đóng lại.

Phép thử chỉ cho thấy hình dạng của lợi ích; con số phụ thuộc hoàn toàn vào các tham số ở trên (ngưỡng 5, mở 10 giây, thời hạn 2 giây) mà người biên soạn chọn. Nó cũng không mô phỏng tải đồng thời hay nhiều ứng dụng cùng gọi.

## Giới hạn cần nhớ

Bài nguồn gọi đây là "7 mẫu hay dùng nhất" nhưng không đưa số đo nào về mức phổ biến; bài này không khẳng định mẫu nào dùng nhiều hơn mẫu nào. Bảy mẫu cũng không phải toàn bộ: các trang mẫu của Microsoft liệt kê nhiều mẫu khác. Bảng "cái giá" là tóm tắt của người biên soạn từ các trang đó, không phải trích dẫn. Dùng một mẫu khi chưa có vấn đề nó giải là một cái giá nữa.

## Nhìn hình trả lời

Một trang đặt hàng gọi dịch vụ thanh toán; dịch vụ này đang chậm vì quá tải, mỗi lần gọi chờ vài giây rồi lỗi. Ứng dụng thử lại ngay khi lỗi. Mẫu nào trong bảy mẫu giúp, và vì sao thử lại liên tục lại làm tệ hơn?

<details>
<summary>Xem đáp án</summary>

Circuit Breaker. Thử lại liên tục giữ thêm nhiều yêu cầu đang chờ ở cả hai phía và thêm tải lên dịch vụ đang quá tải, nên nó khó hồi phục. Bộ ngắt thất bại tức thì khi lỗi vượt ngưỡng, giữ tải khỏi dịch vụ một lúc, rồi dùng trạng thái nửa mở để thử nhẹ trước khi mở lại hoàn toàn. Trang Microsoft nói thêm bộ ngắt hợp để xử lý lỗi kéo dài, còn lỗi thoáng qua tự hết thì dùng cách thử lại có kiểm soát.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn chỉ là một hình và danh sách bảy tên. Bài này giữ bảy tên, mô tả mỗi mẫu bằng vấn đề nó giải và cái giá của nó theo tài liệu của Microsoft, và thêm một mô phỏng cho Circuit Breaker.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-7-most-used-distributed-system-patterns.md): bảy tên mẫu. Bảng vấn đề và cái giá, và mô phỏng, là của người biên soạn.
- [Microsoft — mẫu Ambassador](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/ambassador.md), [Circuit Breaker](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/circuit-breaker.md), [CQRS](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/cqrs.md), [Event Sourcing](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/event-sourcing.md), [Leader Election](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/leader-election-content.md), [Publisher-Subscriber](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/publisher-subscriber.md) và [Sharding](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/sharding.md): vấn đề, giải pháp và ba trạng thái của Circuit Breaker. Đọc từ nhánh chính, không ghim commit.

Đã đọc nguồn ngày 2026-10-19. Mô phỏng là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

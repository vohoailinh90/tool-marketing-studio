# Bảy thuật ngữ của thiết kế hướng miền, và cái giá của một khối dữ liệu quá lớn

**Bài nguồn liệt kê bảy thuật ngữ của thiết kế hướng miền: thực thể, đối tượng giá trị, khối nhất quán, kho lưu, nhà máy, dịch vụ miền và sự kiện miền. Bài này giải nghĩa từng thuật ngữ, thử ba thuật ngữ đầu bằng mã Python và đo một điều mà các định nghĩa khó cho thấy: đặt ranh giới của khối nhất quán quá rộng thì chi phí nằm ở đâu.**

![Ba khung. Khung một, bảy thuật ngữ chia ba nhóm: cấu tạo gồm thực thể, đối tượng giá trị, khối nhất quán; vòng đời gồm kho lưu và nhà máy; hành vi gồm dịch vụ miền và sự kiện miền. Khung hai, thử trong mã: hai đối tượng giá trị cùng nội dung thì bằng nhau và không sửa được, hai thực thể cùng mã định danh thì là một dù thuộc tính khác, luật huỷ nằm trong thực thể. Khung ba, tám luồng cập nhật 2.400 lần: một khối nhất quán chung gây từ 44 đến 67 lần xung đột khi việc nhẹ và từ 8.618 đến 8.778 lần khi việc nặng, còn mỗi giao hàng một khối thì 0 lần.](../../diagrams/sd-08-009-main.svg)

## Từ viết tắt

- **DDD** (Domain-Driven Design) — thiết kế hướng miền: cách xây phần mềm bằng mô hình của chính lĩnh vực nghiệp vụ, với tên gọi lấy từ lĩnh vực đó.
- **ID** (IDentifier) — mã định danh: giá trị riêng của một đối tượng, dùng để tìm lại đúng đối tượng ấy.

## Đọc hình

Bài nguồn chia bảy thuật ngữ thành ba nhóm; bảng dưới giữ cách chia đó và ghép thêm ý của tài liệu Microsoft về DDD (đọc độc lập, xem phần nguồn).

| Nhóm | Thuật ngữ | Ý của bài nguồn | Ghi chú đối chiếu |
|---|---|---|---|
| Cấu tạo | Thực thể (Entity) | Đối tượng có mã định danh và vòng đời | Hai bản có cùng mã định danh là cùng một khái niệm dù thuộc tính khác nhau; luật nghiệp vụ nên nằm trong thực thể |
| Cấu tạo | Đối tượng giá trị (Value Object) | Đối tượng không có mã định danh, mô tả thuộc tính của thực thể | Không đổi được; muốn đổi thì tạo bản mới |
| Cấu tạo | Khối nhất quán (Aggregate) | Tập thực thể gắn với nhau bởi một thực thể gốc; là đơn vị lưu trữ | Tài liệu Microsoft nhấn vào ranh giới nhất quán: chỉ gồm dữ liệu phải đổi cùng một giao dịch, khối khác chỉ tham chiếu bằng mã định danh |
| Vòng đời | Kho lưu (Repository) | Lưu và nạp khối nhất quán | Tài liệu Microsoft nhắc tên nhưng không giải thích |
| Vòng đời | Nhà máy (Factory) | Lo việc tạo khối nhất quán | Như trên |
| Hành vi | Dịch vụ miền (Domain Service) | Điều phối nhiều khối nhất quán | Tài liệu Microsoft: đối tượng không có trạng thái, chứa luật nghiệp vụ không thuộc riêng thực thể nào; dịch vụ ứng dụng thì điều phối ca sử dụng và không chứa luật nghiệp vụ |
| Hành vi | Sự kiện miền (Domain Event) | Mô tả điều đã xảy ra với khối, được công bố để bên khác dùng | Việc ghi một dòng vào bảng không phải sự kiện miền, còn "giao hàng bị huỷ" thì có |

Hai tài liệu không hoàn toàn trùng: bài nguồn gọi khối nhất quán là "đơn vị lưu trữ", tài liệu Microsoft gọi nó là "ranh giới nhất quán". Phần đo bên dưới theo cách hiểu của tài liệu Microsoft vì chỉ cách hiểu đó cho biết cỡ của khối phải chọn thế nào.

## Thử: ba thuật ngữ đầu trong mã

Ngày 2026-10-19, Python 3.13.16. Kết quả chạy:

- **Đối tượng giá trị.** Hai địa chỉ `Address("1 Main", "Hue")` tạo riêng nhau bằng nhau (`==` cho `True`) dù là hai đối tượng khác (`is` cho `False`). Lớp khai báo bất biến: gán `city` bị từ chối (`FrozenInstanceError`); `dataclasses.replace` cho một bản mới và bản cũ vẫn là `Hue`.
- **Thực thể.** Hai đối tượng `Delivery` cùng mã `D1` nhưng điểm đến khác nhau được coi là bằng nhau, vì phép so sánh chỉ xét mã định danh.
- **Luật trong thực thể.** `Delivery.cancel()` chỉ cho huỷ khi trạng thái còn là `created`: sau `pick_up()`, huỷ bị từ chối ("cannot cancel after pickup"), và thực thể ghi lại sự kiện `DeliveryPickedUp` để bên khác nhận.

## Thử: cỡ của khối nhất quán

Một kho lưu dùng khoá lạc quan: mỗi khối có số phiên bản; nạp khối, xử lý, rồi lưu chỉ thành công khi phiên bản chưa đổi, nếu không thì phải nạp lại và làm lại (một "xung đột"). Tám luồng, mỗi luồng cập nhật 300 giao hàng, tổng 2.400 lần. Hai cách đặt ranh giới: **một khối chung** chứa mọi giao hàng, hoặc **mỗi giao hàng một khối**. Ba lần chạy mỗi mức, chỉ đổi lượng việc xử lý giữa lúc nạp và lúc lưu:

| Việc xử lý giữa nạp và lưu | Một khối chung: số xung đột | Mỗi giao hàng một khối |
|---|---|---|
| nhẹ | 44 đến 67 | 0 |
| vừa (gấp 10 lần) | 1.279 đến 1.586 | 0 |
| nặng (gấp 100 lần) | 8.618 đến 8.778 | 0 |

Không lần nào mất cập nhật: mọi lần chạy đều giữ đủ 2.400 trên 2.400 lần; giá phải trả là việc làm lại. Ở mức nặng, một khối chung chạy từ 4.057 đến 4.407 mili giây, còn mỗi giao hàng một khối chạy từ 895 đến 981 mili giây trong cùng điều kiện.

## Giới hạn cần nhớ

Phép đo dùng luồng của Python trên một máy, nên con số tuyệt đối thuộc về máy đó; điều có giá trị là xu hướng: xung đột tăng theo lượng việc xử lý giữa lúc nạp và lúc lưu. Đây cũng chỉ là một cơ chế (khoá lạc quan); với khoá bi quan hay một cơ sở dữ liệu thật, chi phí sẽ khác dạng. Phần giải nghĩa dựa trên bài nguồn và tài liệu Microsoft, chưa đối chiếu với cuốn sách của Eric Evans (không truy cập được trong lúc viết). Kho lưu và nhà máy không có phép thử ở đây. Tài liệu Microsoft cũng nói khối nên nhỏ, nhưng không nói nhỏ tới đâu: đó là phán đoán theo từng hệ thống.

## Nhìn hình trả lời

Bạn gộp tài khoản của khách và mọi đơn giao hàng của họ vào một khối nhất quán để "cho an toàn". Điều gì xảy ra khi hai nhân viên cùng sửa hai đơn khác nhau của khách đó, và nên sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Hai thay đổi cùng đụng vào một khối, nên một trong hai bị từ chối ở lần lưu và phải làm lại; càng nhiều việc giữa nạp và lưu thì càng nhiều lần làm lại (bảng đo). Cách sửa: tách mỗi đơn thành khối riêng, tài khoản chỉ giữ mã định danh của đơn, và việc cần đồng bộ giữa hai khối đi qua sự kiện miền thay vì cùng một giao dịch.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn chỉ có một danh sách bảy thuật ngữ cùng một hình. Bài này giữ cách chia nhóm của nguồn, thêm cách hiểu "ranh giới nhất quán" từ tài liệu Microsoft, thay hình bằng ba phép thử trong mã và một phép đo về cỡ khối.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/key-terms-in-domain-driven-design.md): bảy thuật ngữ và cách chia ba nhóm.
- [Microsoft — Use tactical DDD to design microservices](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/microservices/model/tactical-domain-driven-design.md): thực thể, đối tượng giá trị, khối nhất quán, dịch vụ và sự kiện miền; đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

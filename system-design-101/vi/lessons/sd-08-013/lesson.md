# Chín thành phần của một ứng dụng dịch vụ nhỏ chạy thật, và cái giá của từng thành phần

**Bài nguồn là một sơ đồ chín thành phần mà một ứng dụng dịch vụ nhỏ chạy thật thường có, mỗi thành phần kèm vài tên sản phẩm. Bài này giữ chín thành phần, không đi vào tên sản phẩm, và hỏi một câu mà sơ đồ không trả lời: mỗi thành phần thêm vào thì thêm cái giá nào? Năm thành phần được đo thử bằng chương trình nhỏ trên một máy, bốn thành phần chưa đo được thì ghi rõ.**

![Ba khung. Khung một, chín thành phần của nguồn: cổng vào, sổ đăng ký dịch vụ, tầng dịch vụ, máy chủ cấp quyền, kho dữ liệu, bộ nhớ đệm phân tán, liên lạc bất đồng bộ, đo lường và gom nhật ký. Khung hai, năm cái giá đo trên một máy: tra sổ đăng ký mỗi lần gọi làm một lời gọi tốn 507 đến 559 micro giây thay vì 179 đến 206; kiểm chữ ký tại chỗ mất 1,8 micro giây còn hỏi máy chủ cấp quyền mất 192 đến 223; một lần đọc Redis mất 39 đến 40 micro giây còn đọc cơ sở dữ liệu trong cùng tiến trình mất 1 đến 5; đẩy việc vào hàng đợi trả lời sau 36 đến 40 micro giây thay vì 5,1 mili giây; một dòng nhật ký ra tệp mất 12 đến 13 micro giây. Khung ba, bốn thành phần chưa đo.](../../diagrams/sd-08-013-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình cho chương trình khác gọi tới; "cổng API" là chỗ đứng trước các dịch vụ để nhận lời gọi của bên ngoài.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: cách quen thuộc để một chương trình gọi một dịch vụ qua mạng; ở bài này dùng ngay trên máy để đo.

## Đọc hình

| Thành phần | Việc của nó theo bài nguồn | Cái giá khi thêm vào |
|---|---|---|
| Cổng API | Một cửa vào cho các ứng dụng khách: định tuyến, lọc, cân bằng tải | thêm một bước nhảy cho mỗi lời gọi; chưa đo ở bài này |
| Sổ đăng ký dịch vụ | Giữ chi tiết mọi dịch vụ, cổng tìm dịch vụ qua đó | một lời gọi tra cứu nếu tra mỗi lần (đo bên dưới) |
| Tầng dịch vụ | Mỗi dịch vụ nhỏ lo một việc nghiệp vụ và chạy được nhiều bản | chưa đo |
| Máy chủ cấp quyền | Bảo vệ các dịch vụ, quản lý danh tính và quyền truy cập | một lời gọi hỏi nếu hỏi mỗi lần (đo bên dưới) |
| Kho dữ liệu | Lưu dữ liệu do các dịch vụ tạo ra | chưa đo |
| Bộ nhớ đệm phân tán | Tăng tốc ứng dụng | một bước nhảy mạng mỗi lần đọc (đo bên dưới) |
| Liên lạc bất đồng bộ | Hàng đợi hay luồng thông điệp giữa các dịch vụ | thêm một thành phần phải vận hành; lợi là đáp nhanh (đo bên dưới) |
| Đo lường | Dịch vụ phát số đo, công cụ vẽ biểu đồ | chi phí tăng một bộ đếm (đo bên dưới); phần vẽ chưa đo |
| Gom nhật ký | Nhật ký của các dịch vụ được gom, lưu, rồi xem | chi phí ghi một dòng (đo bên dưới); phần gom và tìm chưa đo |

Tài liệu của Microsoft về cổng API khớp với phần mô tả của nguồn: cổng là điểm vào tập trung, đóng vai trò máy chủ trung chuyển, định tuyến lời gọi tới dịch vụ phù hợp và làm các việc chung như xác thực, giới hạn tốc độ; nó cũng nhắc rằng cổng có thể gộp nhiều lời gọi của khách thành một để giảm số lần trao đổi. Cột thứ ba là suy luận của người biên soạn, không phải của nguồn.

## Thử: năm cái giá

Ngày 2026-10-19, một máy ảo 4 lõi, Python 3.13.16, Redis 7.0.15, máy chủ HTTP đơn giản viết bằng thư viện chuẩn chạy trên cùng máy, ba lần chạy.

| Điều đo | Kết quả |
|---|---|
| Gọi một dịch vụ khi đã nhớ địa chỉ so với tra sổ đăng ký trước mỗi lần gọi | 179 đến 206 micro giây so với 507 đến 559 micro giây (gấp 2,5 đến 3 lần) |
| Kiểm chữ ký của token tại chỗ so với hỏi một máy chủ cấp quyền qua HTTP mỗi lần | 1,8 micro giây so với 192 đến 223 micro giây |
| Đọc một giá trị từ Redis (một bước nhảy mạng) so với đọc cơ sở dữ liệu `sqlite3` ngay trong tiến trình | 39 đến 40 micro giây so với 1 đến 2 micro giây (bộ nhớ) và 5 micro giây (tệp) |
| Một yêu cầu làm việc 5 mili giây ngay trong lời gọi so với đẩy việc vào hàng đợi (Redis) rồi trả lời | 5.116 đến 5.127 micro giây so với 36 đến 40 micro giây |
| Tăng một bộ đếm số đo có khoá; ghi một dòng nhật ký mức `INFO` ra tệp; một dòng bị bỏ vì mức thấp | 0,23 đến 0,24 micro giây; 11,7 đến 13,1 micro giây; 0,17 đến 0,18 micro giây |

Bốn điều đọc được. Một, hai thành phần "tra cứu" (sổ đăng ký, máy chủ cấp quyền) đều đắt khi gọi mỗi lần và rẻ khi nhớ kết quả hoặc kiểm tại chỗ: cái giá không nằm ở thành phần mà ở cách dùng. Hai, bộ nhớ đệm phân tán không tự nhanh hơn: một lần đọc Redis tốn một bước nhảy mạng, nên chậm hơn đọc một cơ sở dữ liệu nằm trong cùng tiến trình; nó chỉ có lợi khi lần đọc cơ sở dữ liệu thật còn đắt hơn một bước nhảy, và phép thử này không dựng cơ sở dữ liệu từ xa. Ba, hàng đợi cho ra lợi rõ nhất về thời gian trả lời (chưa đến một phần trăm thời gian làm việc), nhưng việc vẫn phải được làm sau đó: trong mỗi lần chạy, hàng đợi còn lại 5.500 việc chưa ai làm. Bốn, đo lường và nhật ký rẻ ở mức một lần ghi, nên cái đáng tính là tổng số dòng mỗi giây nhân với 12 micro giây, không phải một dòng.

## Giới hạn cần nhớ

Mọi dịch vụ, sổ đăng ký, máy chủ cấp quyền chạy trên cùng một máy nên bước nhảy mạng rẻ hơn thật nhiều (cỡ 170 micro giây cho một lời gọi HTTP đo ở đây); trên mạng thật giữa hai máy hoặc hai vùng, mỗi bước nhảy đắt hơn nên các thời gian tuyệt đối sẽ lớn hơn. Các tỷ lệ thì không đổi cùng một hướng: khi độ trễ mạng chiếm hết, so sánh "tra sổ mỗi lần" với "nhớ địa chỉ" tiến về cỡ 2 lần (hai lời gọi so với một), thấp hơn mức 2,5 đến 3 lần đã đo, và tỷ lệ giữa làm việc ngay và đẩy vào hàng đợi cũng có thể nhỏ đi khi hàng đợi nằm trên một máy khác. Phép kiểm chữ ký dùng khoá chia sẻ; token ký bằng khoá công khai sẽ đắt hơn. Các công cụ cụ thể mà nguồn nêu tên không được thử. Bốn thành phần (cổng, tầng dịch vụ, kho dữ liệu, phần vẽ biểu đồ và tìm nhật ký) chưa đo.

## Nhìn hình trả lời

Nhóm bạn có cổng API và sổ đăng ký, và thấy mỗi lời gọi giữa hai dịch vụ chậm gấp ba. Nguyên nhân dễ nhất để kiểm tra là gì, và sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Có thể mỗi lời gọi tra sổ đăng ký trước khi gọi, nên thêm một bước nhảy (phép thử: 507 đến 559 so với 179 đến 206 micro giây). Sửa bằng cách bên gọi nhớ địa chỉ trong một khoảng thời gian ngắn, rồi tra lại khi gọi thất bại hoặc hết hạn; cái phải đổi lại là xử lý trường hợp địa chỉ đã cũ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một sơ đồ cùng một đoạn ngắn cho mỗi thành phần, kèm tên sản phẩm. Bài này giữ chín thành phần, bỏ tên sản phẩm, thêm cột cái giá và năm phép đo, và nói rõ các thành phần chưa đo.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/9-essential-components-of-a-production-microservice-application.md): chín thành phần.
- [Microsoft — API gateways](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/microservices/design/gateway-content.md): vai trò của cổng API: điểm vào tập trung, định tuyến, gộp lời gọi, làm hộ các việc chung. Đọc từ bản sao cục bộ.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.

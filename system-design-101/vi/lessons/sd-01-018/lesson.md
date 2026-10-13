# Load Balancer và API Gateway

**Cả hai đứng trước dịch vụ, nhưng một bên chia lưu lượng, còn bên kia lo các việc chung của API.** Bài này so cách chúng khác nhau, rồi nêu hai cách xếp thường gặp và lúc nào chưa cần cả hai.

![Năm khung dọc: bộ cân bằng tải tầng kết nối chia theo địa chỉ IP, cổng và kết nối mà không đọc nội dung HTTP; bộ cân bằng tải tầng HTTP đọc host, đường dẫn và header để định tuyến phong phú hơn; API gateway lo xác thực, giới hạn tốc độ và cache như một cửa chung cho nhiều API; cách A là bộ cân bằng tải tầng HTTP tới thẳng các dịch vụ, mỗi dịch vụ tự lo xác thực nên linh hoạt nhưng lặp việc; cách B là qua API gateway lo việc chung nên dịch vụ nhẹ hơn nhưng thêm một chặng và kém linh hoạt. Dịch vụ nhỏ thường chỉ cần một bộ cân bằng tải.](../../diagrams/sd-01-018-main.svg)

## Đọc hình

1. **Tầng kết nối** (tầng 4, như NLB của AWS): chọn máy theo địa chỉ IP, cổng và kết nối TCP hoặc UDP, không đọc nội dung HTTP. Việc đơn giản nên nhanh, hợp khi chỉ cần chia kết nối, hoặc khi đặt trước một lớp khác như gateway.
2. **Tầng HTTP** (tầng 7, như ALB): đọc được host, đường dẫn và header nên định tuyến phong phú hơn, ví dụ `/orders` tới nhóm máy này, `/users` tới nhóm kia.
3. **API gateway:** làm việc ở mức API chứ không ở mức chia tải: xác thực, giới hạn tốc độ theo khách hoặc theo khóa API, cache, ghi log và thống kê, đổi định dạng, rồi chuyển tới đúng dịch vụ.
4. **Cách A, bộ cân bằng tải tầng HTTP tới thẳng dịch vụ:** mỗi dịch vụ tự lo xác thực và giới hạn tốc độ. Linh hoạt vì mỗi dịch vụ chọn luật riêng, nhưng việc bị lặp lại ở mọi dịch vụ và dễ lệch giữa các nhóm.
5. **Cách B, qua API gateway:** việc chung làm một lần ở cửa nên dịch vụ nhẹ hơn và chính sách thống nhất. Đổi lại có thêm một chặng, gateway thành điểm tập trung cần được nhân bản, và kém linh hoạt khi một dịch vụ cần luật riêng.

Hai cách không loại trừ nhau. Thường gặp là một bộ cân bằng tải đứng trước các bản sao của gateway, gateway chọn dịch vụ, và mỗi dịch vụ lại có bộ cân bằng tải riêng cho các bản sao của nó.

## Giới hạn cần nhớ

Ranh giới theo từng sản phẩm: nhiều phần mềm làm được cả hai việc. Với dịch vụ nhỏ, một bộ cân bằng tải thường đủ; thêm gateway là thêm chi phí vận hành và độ trễ. Đừng nhồi logic nghiệp vụ vào gateway. Giới hạn tốc độ ở gateway cũng không thay việc dịch vụ tự bảo vệ mình bằng timeout và hàng đợi.

## Nhìn hình thử trả lời

Ba dịch vụ nội bộ của cùng một nhóm, lưu lượng vừa phải, cần chuyển `/orders` và `/users` về đúng dịch vụ và dùng chung một kiểu xác thực. Có cần thêm API gateway không? Nêu một lý do nên thêm và một lý do chưa cần.

<details>
<summary>Xem đáp án</summary>

Chưa chắc. Bộ cân bằng tải tầng HTTP đã định tuyến được theo đường dẫn, còn xác thực dùng chung có thể làm bằng thư viện chung vì chỉ một nhóm sở hữu cả ba dịch vụ. Nên thêm gateway khi có nhiều nhóm hoặc khách bên ngoài cần chính sách thống nhất: giới hạn tốc độ theo khóa API, xác thực ngay tại cửa, cache, thống kê. Chưa cần khi dịch vụ ít và một nhóm lo hết, vì gateway thêm một chặng và một thành phần phải vận hành.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Giữ nguyên mã hóa tới tận dịch vụ:** bộ cân bằng tải tầng kết nối có thể chuyển tiếp byte mà không giải mã; bộ cân bằng tải tầng HTTP phải giải mã mới đọc được header.
- **Gateway theo từng loại client:** mỗi loại client (web, di động) có một gateway riêng với đúng dữ liệu nó cần; đôi khi gọi là mẫu Backends for Frontends.
- **Nhân bản gateway:** vì mọi yêu cầu đi qua nó, gateway cần chạy nhiều bản và có kiểm tra sức khỏe, nếu không nó thành điểm đơn lỗi.
- **Nội bộ khác bên ngoài:** gateway ở rìa lo client bên ngoài; giữa các dịch vụ với nhau, việc tương tự đôi khi do proxy đi kèm từng dịch vụ làm.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-differences-between-a-load-balancer-and-an-api-gateway.md).
- [AWS — Elastic Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html) và [AWS — API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html).
- [Azure — API gateway pattern](https://learn.microsoft.com/en-us/azure/architecture/microservices/design/gateway) và [Backends for Frontends](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends).
- [NGINX — Cân bằng tải TCP và UDP](https://docs.nginx.com/nginx/admin-guide/load-balancer/tcp-udp-load-balancer/) và [HAProxy — tài liệu](https://docs.haproxy.org/).

Đã đọc bản nguồn ByteByteGo ngày 2026-10-13; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.

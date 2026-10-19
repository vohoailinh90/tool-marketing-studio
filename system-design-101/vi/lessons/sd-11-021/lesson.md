# Mạng trên AWS: VPC và các cách nối ra, nối vào

**Mạng của một hệ thống trên AWS bắt đầu từ một mạng ảo riêng (VPC) đặt trong một vùng địa lý; mọi cách nối với internet, với văn phòng hay với VPC khác đều là một thành phần bạn chọn thêm vào.** Hiểu các lớp rồi hiểu từng cách nối, bạn đọc được sơ đồ mạng AWS của hầu hết hệ thống.

![Ba khung. Khung một, bốn lớp từ ngoài vào trong: Region, vùng sẵn sàng AZ, VPC, subnet. Khung hai, bốn cách nối VPC ra ngoài: Internet gateway ra internet, Client VPN cho người làm từ xa, Virtual private gateway cho trung tâm dữ liệu công ty, NAT gateway cho máy trong mạng riêng đi ra. Khung ba, bốn cách nối giữa các VPC và dịch vụ: VPC peering, Transit gateway, endpoint dạng gateway, endpoint dạng interface hay PrivateLink.](../../diagrams/sd-11-021-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ web của Amazon: nền tảng đám mây mà bài này nói tới.
- **VPC** (Virtual Private Cloud) — đám mây riêng ảo: một mạng bạn định nghĩa, tách biệt về mặt logic với mạng của khách hàng khác.
- **AZ** (Availability Zone) — vùng sẵn sàng: một hay nhiều trung tâm dữ liệu riêng biệt, có điện và mạng riêng, nằm trong một Region.
- **VPN** (Virtual Private Network) — mạng riêng ảo: đường nối mã hóa đi qua internet, để người hay văn phòng ở xa vào được mạng riêng.
- **NAT** (Network Address Translation) — dịch địa chỉ mạng: thay địa chỉ riêng của máy bên trong bằng một địa chỉ công khai khi đi ra, để máy bên trong gọi ra được mà bên ngoài không gọi thẳng vào được.
- **IP** (Internet Protocol) — giao thức liên mạng: quy định địa chỉ của mỗi máy trong mạng; nói "địa chỉ IP riêng" là địa chỉ chỉ dùng được trong mạng nội bộ.

## Đọc hình

**Từ ngoài vào trong.** Một **Region** là một vùng địa lý, chứa nhiều **AZ**. Một **VPC** nằm trong một Region và trải qua nhiều AZ của Region đó; bạn chọn dải địa chỉ IP của nó. VPC được chia thành **subnet**, mỗi subnet nằm trong đúng một AZ. Việc đặt các bản của một dịch vụ vào subnet ở những AZ khác nhau là cách dùng dư thừa đã nói ở bài về chịu lỗi. Một **bảng định tuyến** gắn với subnet quyết định gói tin đi tiếp bằng đường nào; "subnet công khai" hay "subnet riêng" chủ yếu khác nhau ở chỗ bảng này có đường ra Internet gateway hay không.

**Nối VPC ra ngoài.**

- **Internet gateway**: cửa giữa VPC và internet, đi được cả hai chiều cho máy có địa chỉ công khai.
- **Client VPN**: dịch vụ để người làm việc từ xa nối vào tài nguyên AWS (hoặc mạng nội bộ công ty) qua một đường VPN.
- **Virtual private gateway**: đầu phía AWS của một đường VPN nối trung tâm dữ liệu của công ty với VPC.
- **NAT gateway** (không nằm trong sơ đồ nguồn, người biên soạn thêm vì nó là mảnh ghép thường gặp): để máy trong subnet riêng đi ra internet (cập nhật gói, gọi dịch vụ ngoài) mà không cho kết nối từ ngoài vào.

**Nối VPC với nhau và với dịch vụ.**

- **VPC peering**: nối hai VPC để máy trong mỗi bên gọi nhau bằng địa chỉ riêng. Đây là quan hệ một-một và **không bắc cầu**: A nối B, B nối C không có nghĩa A gọi được C. Dải địa chỉ hai bên không được chồng nhau.
- **Transit gateway**: một trạm trung chuyển, nối nhiều VPC và đường VPN vào cùng một chỗ; thêm VPC mới là thêm một kết nối vào trạm, thay vì nối với từng VPC cũ.
- **Gateway endpoint**: lối riêng từ VPC tới một số dịch vụ AWS (hiện là S3 và DynamoDB), đi qua một dòng trong bảng định tuyến, không cần Internet gateway hay NAT.
- **Interface endpoint** (dùng PrivateLink): đặt một lối vào mang địa chỉ IP riêng ngay trong subnet của bạn, trỏ tới một dịch vụ AWS, hoặc tới một dịch vụ đã được đưa ra (endpoint service, đứng sau một bộ cân bằng tải) từ một VPC khác hay từ bên thứ ba (nhà cung cấp phần mềm dạng dịch vụ), không đi qua internet. Nó nối tới một dịch vụ cụ thể, không phải định tuyến cả VPC như peering.

## Tính thử: nối bao nhiêu VPC thì peering thành gánh nặng

Muốn mọi VPC trong tập n VPC đều gọi được nhau bằng peering thì vì không bắc cầu, cần n(n−1)/2 quan hệ peering. Với 4 VPC là 6; với 10 VPC là 45. Với Transit gateway, mỗi VPC chỉ cần một kết nối vào trạm, tức n kết nối: 10 cho 10 VPC. Con số cho thấy vì sao peering hợp với vài VPC, còn Transit gateway hợp khi nhiều.

## Giới hạn cần nhớ

Bài mô tả khái niệm ở mức đủ để đọc sơ đồ; hạn mức, giá và tên dịch vụ có thể đổi, và bài chưa mở lại tài liệu AWS trong phiên viết (môi trường không mở được trang đó), nên chi tiết cụ thể như danh sách dịch vụ có gateway endpoint cần đối chiếu với tài liệu hiện hành trước khi dựa vào.

## Nhìn hình trả lời

Máy ứng dụng ở subnet riêng cần tải ảnh từ S3 nhưng công ty cấm đi qua internet. Nên dùng thành phần nào trong hình?

<details>
<summary>Xem đáp án</summary>

Một gateway endpoint cho S3: nó thêm một dòng vào bảng định tuyến để gói tin tới S3 đi thẳng bằng đường riêng của AWS, không cần Internet gateway hay NAT gateway.
Đây là suy luận của người biên soạn từ mô tả các endpoint, cần đối chiếu với tài liệu hiện hành.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn đi lần lượt qua tám kiểu kết nối đánh số. Bài này gom chúng theo hướng nối (ra ngoài, giữa các VPC và dịch vụ) thay vì theo số thứ tự, gộp mục kết nối riêng cho dịch vụ bên thứ ba vào interface endpoint, thêm NAT gateway và bảng định tuyến, và thêm phép đếm peering. Lời giải thích viết từ hiểu biết chung về AWS, chưa đối chiếu lại với tài liệu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/typical-aws-network-architecture-in-one-diagram.md): tám kiểu kết nối. Cách gom nhóm, NAT gateway, phép đếm peering và đáp án là của người biên soạn.
- [Tài liệu AWS — Amazon VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html): VPC, subnet, bảng định tuyến, Internet gateway, NAT gateway, peering, endpoint. Kiến thức chung, chưa mở lại trong phiên viết.
- [Tài liệu AWS — AWS Global Infrastructure](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/): Region và AZ. Kiến thức chung, chưa mở lại trong phiên viết.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.

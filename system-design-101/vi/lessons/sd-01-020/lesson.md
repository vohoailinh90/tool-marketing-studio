# Các cách đưa GraphQL vào hệ thống

**Theo nguồn, có bốn cách đặt GraphQL vào một hệ thống: ở phía client, cùng các lớp BFF, trong một máy chủ nguyên khối, hoặc liên hợp nhiều đồ thị thành một.** Theo cách đọc của bài, điểm khác nhau chính là việc gom dữ liệu diễn ra ở đâu và nhóm nào sở hữu lớp GraphQL.

![Năm khung dọc: điểm xuất phát là một ứng dụng client hỏi một máy chủ GraphQL; GraphQL phía client bọc các API sẵn có sau một điểm vào nên người lập trình dễ làm việc hơn nhưng client vẫn chịu chi phí gom dữ liệu; GraphQL cùng BFF, mỗi loại client có một dịch vụ BFF riêng nên hiệu năng và trải nghiệm tốt hơn nhưng phải xây và duy trì thêm; GraphQL nguyên khối, nhiều nhóm dùng chung một mã nguồn hoặc một nhóm sở hữu một API cho nhiều nhóm client; GraphQL liên hợp, nhiều đồ thị gộp thành siêu đồ thị, cổng liên hợp định tuyến yêu cầu tới các dịch vụ con và dữ liệu vẫn thuộc nhóm lĩnh vực.](../../diagrams/sd-01-020-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách để một chương trình gọi chức năng hoặc lấy dữ liệu của chương trình khác theo quy ước đã định.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu (request) và máy chủ gửi trả lời (response).
- **REST** (REpresentational State Transfer) — kiểu thiết kế dịch vụ qua HTTP: mỗi tài nguyên có một địa chỉ riêng và được lấy hay sửa qua các phương thức chuẩn.
- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, cho biết đây là cách để client mô tả dữ liệu mình muốn lấy.
- **BFF** (Backend for Frontend) — dịch vụ phía sau riêng cho từng client: một lớp trung gian mà mỗi loại client, như web hay di động, có một cái riêng để gom dữ liệu đúng theo nhu cầu của loại client đó.

## Đọc hình

1. **Điểm xuất phát.** Nguồn nói nhiều nhóm bắt đầu bằng kiến trúc đơn giản: một ứng dụng client hỏi một máy chủ GraphQL. Bốn cách dưới đây là các hướng mở rộng từ đó.
2. **GraphQL phía client.** Client bọc các API (giao diện lập trình ứng dụng) hiện có sau một điểm vào GraphQL duy nhất. Người lập trình làm việc dễ hơn, nhưng client vẫn phải chịu chi phí hiệu năng của việc gom dữ liệu.
3. **GraphQL cùng BFF.** BFF (Backend for Frontend, tạm dịch là dịch vụ phía sau riêng cho từng client) là một lớp mới: mỗi client có một dịch vụ BFF của mình, và GraphQL hợp để dựng lớp trung gian hướng về client này. Hiệu năng và trải nghiệm cho client tốt hơn, đổi lại phải xây và duy trì các BFF.
4. **GraphQL nguyên khối.** Nhiều nhóm dùng chung một mã nguồn cho một máy chủ GraphQL phục vụ nhiều client; hoặc một nhóm sở hữu một API GraphQL mà nhiều nhóm client cùng truy cập.
5. **GraphQL liên hợp (federation).** Nhiều đồ thị được gộp thành một siêu đồ thị (supergraph). Cổng liên hợp định tuyến yêu cầu tới các dịch vụ con (subgraph), mỗi dịch vụ lo một phần của lược đồ GraphQL. Dữ liệu vẫn thuộc nhóm lĩnh vực của nó và công sức không bị làm lặp.

## Giới hạn cần nhớ

Nguồn chỉ tả bốn cách trong vài câu, không có số liệu, ngưỡng hay tiêu chí chọn. Những điểm sau là suy luận của bài, không phải lời của nguồn. Bốn cách không loại trừ nhau: một tổ chức có thể dùng BFF cho ứng dụng di động và liên hợp cho phần còn lại. Mỗi cách chuyển chi phí chứ không xóa nó: gom ở client thì thiết bị gánh, BFF thêm dịch vụ phải vận hành, nguyên khối dồn việc phối hợp vào một mã nguồn chung, liên hợp thêm cổng và quy trình ghép lược đồ giữa các nhóm. Muốn chọn cho một hệ thống cụ thể, cần biết số nhóm, số dịch vụ, ai sở hữu dữ liệu và yêu cầu về độ trễ; bài không đưa ngưỡng nào.

## Nhìn hình thử trả lời

Công ty có ba nhóm backend (đơn hàng, thanh toán, kho), mỗi nhóm đã có API riêng. Ứng dụng di động cần một màn hình lấy dữ liệu từ cả ba. Bạn cân nhắc cách nào, và mỗi cách đổi lại điều gì?

<details>
<summary>Xem đáp án</summary>

Không có một đáp án duy nhất; điều cần thấy là mỗi cách đặt chi phí ở đâu. Gom ở client: không cần dịch vụ mới, nhưng điện thoại phải gọi cả ba API qua mạng di động. BFF cho ứng dụng di động: việc gom chuyển sang máy chủ, một lần gọi từ điện thoại, đổi lại có thêm một dịch vụ phải xây và vận hành. Liên hợp: mỗi nhóm giữ lược đồ và dữ liệu của mình, nhưng cần cổng liên hợp và thỏa thuận giữa các nhóm. Nguyên khối: một máy chủ GraphQL dùng chung, nhưng theo suy luận của bài, các nhóm phải phối hợp trên cùng mã nguồn hoặc phụ thuộc vào nhóm sở hữu nó.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **BFF:** mẫu "Backends for Frontends" cho mỗi loại trải nghiệm (web, di động) một backend riêng. GraphQL chỉ là một cách dựng BFF; BFF vẫn có thể viết bằng REST.
- **Siêu đồ thị và dịch vụ con:** mỗi nhóm công bố lược đồ của phần mình; công cụ liên hợp ghép các lược đồ thành một lược đồ chung, và cổng dùng nó để chia truy vấn xuống từng dịch vụ con. Theo suy luận của bài, điểm riêng của cổng liên hợp so với một API gateway thông thường không phải là chuyển tiếp HTTP (API gateway thông thường cũng xác thực, giới hạn tốc độ, cache và gom lời gọi) mà là dùng lược đồ GraphQL đã ghép để lập kế hoạch và chạy một truy vấn qua nhiều dịch vụ con.
- **Điểm chung của bốn cách (suy luận của bài):** đều có một lớp GraphQL đứng giữa client và các nguồn dữ liệu; chỗ đặt lớp đó và nhóm sở hữu nó là chỗ bốn cách khác nhau.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/graphql-adoption-patterns.md): bốn cách đưa GraphQL vào hệ thống.
- [GraphQL — Learn](https://graphql.org/learn/) và [Đặc tả GraphQL](https://spec.graphql.org/).
- [Microsoft — mẫu Backends for Frontends](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends) và [Sam Newman — Pattern: Backends For Frontends](https://samnewman.io/patterns/architectural/bff/).
- [Apollo — Federation](https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/federation).

Đã đọc body nguồn ByteByteGo ghim và đối chiếu các claim được liệt kê trong metadata ngày 2026-10-15. Phạm vi và giới hạn evidence nằm trong metadata; các đánh đổi và giả định của bài được ghi riêng. Bài viết và hình được thiết kế độc lập; chưa thử với người học.

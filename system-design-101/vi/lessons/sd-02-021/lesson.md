# Netflix dùng Java thế nào qua ba đời kiến trúc

**Theo bài nguồn, mọi ứng dụng phía sau của Netflix đều viết bằng Java, nhưng cách các ứng dụng đó phục vụ máy khách đã đổi ba lần: một cổng chung, rồi mỗi loại máy khách một lớp riêng, rồi GraphQL Federation.**
Bài này đọc ba đời đó theo một câu hỏi: mỗi lần đổi giải quyết vấn đề gì của đời trước.

![Ba bước nối nhau. Bước một, cổng API: Netflix theo kiến trúc microservice, mỗi chức năng và dữ liệu thuộc về một microservice viết bằng Java, ban đầu là Java 8. Bước hai, BFF với Groovy và RxJava: một cổng chung cho nhiều loại máy khách gặp khó vì TV, ứng dụng di động và trình duyệt khác nhau chút ít, nên mỗi loại có một lớp phía sau riêng, còn Zuul chuyển sang vai trò proxy. Bước ba, GraphQL Federation: cách Groovy và RxJava bắt người làm giao diện viết thêm script Groovy, và lập trình phản ứng thường khó. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-021-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một chương trình gọi chức năng của chương trình khác.
- **BFF** (Backend For Frontend) — lớp phía sau riêng cho từng loại giao diện: mỗi loại máy khách có một dịch vụ trung gian chuẩn bị dữ liệu đúng như nó cần.
- **TV** (TeleVision) — tivi: ở đây là ứng dụng Netflix chạy trên tivi.
- **UI** (User Interface) — giao diện người dùng: phần màn hình người xem nhìn và bấm.
- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, cho biết đây là cách để ứng dụng mô tả dữ liệu mình muốn lấy.

## Đọc hình

Theo nguồn, Netflix chủ yếu là "một cửa hàng Java": mọi ứng dụng phía sau, gồm ứng dụng nội bộ, phát video và sản xuất phim, đều là ứng dụng Java. Nhưng ngăn xếp Java đó đã qua nhiều đời:

1. **Cổng API.** Netflix theo kiến trúc microservice: mỗi chức năng và mỗi phần dữ liệu thuộc về một microservice viết bằng Java (ban đầu là Java 8). Máy khách gọi qua một cổng chung.
2. **BFF với Groovy và RxJava.** Một cổng chung cho nhiều loại máy khách là vấn đề, vì mỗi loại (TV, ứng dụng di động, trình duyệt web) khác nhau một chút. Netflix dùng mẫu BFF để xử lý, và Zuul được chuyển sang vai trò proxy (trạm chuyển tiếp yêu cầu).
3. **GraphQL Federation.** Cách làm với Groovy và RxJava bắt người làm UI viết thêm script Groovy, và lập trình phản ứng (reactive programming) nói chung là khó. Netflix chuyển sang GraphQL Federation.

Điểm chung của ba đời: dịch vụ phía sau vẫn là Java; thứ thay đổi là lớp nằm giữa máy khách và các dịch vụ.

## Giới hạn cần nhớ

Bài nguồn dừng ở lý do rời đời thứ hai; nó không giải thích GraphQL Federation hoạt động thế nào hay vì sao nó đỡ việc hơn. Bài cũng không nói mỗi đời kéo dài bao lâu. Lời giải thích về GraphQL Federation ở phần dưới là của người biên soạn.

## Nhìn hình thử trả lời

Ứng dụng trên tivi cần ảnh bìa lớn, còn ứng dụng điện thoại cần ảnh nhỏ và ít trường dữ liệu hơn. Với một cổng chung (đời một), vấn đề là gì, và đời hai giải quyết nó ra sao?

<details>
<summary>Xem đáp án</summary>

Nếu cổng chung trả cùng một dạng dữ liệu cho mọi máy khách thì hoặc tivi thiếu thứ nó cần, hoặc điện thoại phải nhận thừa dữ liệu. Cổng chung cũng có thể cho từng loại máy khách chọn trường riêng; khi đó mỗi cách xử lý riêng cho tivi hay điện thoại lại dồn vào cùng một cổng, và các đội phải cùng sửa một chỗ. Ở đời hai, mỗi loại máy khách có một BFF riêng, chuẩn bị dữ liệu đúng như máy khách đó cần.

</details>

<details>
<summary>Xem sâu hơn: GraphQL Federation đỡ việc ở đâu</summary>

- Với GraphQL, máy khách tự nói nó cần những trường nào, nên không cần viết một script riêng cho mỗi loại máy khách.
- Federation ghép phần lược đồ dữ liệu của nhiều dịch vụ thành một lược đồ chung; mỗi đội vẫn giữ phần của mình.
- Cái giá: cần một lớp ghép lược đồ và quy tắc chung để các đội không đặt trùng tên.

Đây là kiến thức chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-netflix-really-uses-java.md): Java cho mọi ứng dụng phía sau và ba đời kiến trúc.

Đã đọc nguồn ngày 2026-10-19. Tài liệu kỹ thuật của Netflix chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.

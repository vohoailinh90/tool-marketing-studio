# API của các API: nối ứng dụng bằng trigger và action

**Dịch vụ no-code như Zapier hay If This Then That cho bạn nối hai ứng dụng bằng một quy tắc "khi A xảy ra thì làm B" mà không phải viết code.** Phía sau, dịch vụ là một lớp đứng trên API của rất nhiều ứng dụng; nguồn gọi đó là "API của các API".

![Năm khung nối tiếp nhau bằng mũi tên: sự kiện xảy ra ở ứng dụng A như email mới hoặc dòng mới trong bảng tính; trigger, nền tảng biết sự kiện bằng cách hỏi định kỳ hoặc nhờ ứng dụng A gọi webhook; lọc điều kiện và ghép trường của sự kiện vào ô nhập của bước sau; action, nền tảng gọi API của ứng dụng B bằng quyền người dùng đã cấp; cái giá gồm trễ, báo trùng, lỗi giữa chừng và giới hạn số lời gọi của ứng dụng B.](../../diagrams/sd-02-002-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách để một chương trình gọi chức năng hoặc lấy dữ liệu của chương trình khác theo quy ước đã định.
- **OAuth** (Open AUTHorization) — chuẩn ủy quyền mở: cho một ứng dụng được làm một số việc thay bạn mà không phải đưa mật khẩu của bạn cho bên kia.

## Đọc hình

1. **Sự kiện ở ứng dụng A.** Phần lớn quy tắc bắt đầu từ một việc xảy ra trong một ứng dụng: có email mới, có dòng mới trong bảng tính, có đơn hàng mới (cũng có trigger theo lịch, như "mỗi sáng thứ hai").
2. **Trigger (điều kiện kích hoạt).** Nền tảng phải biết sự kiện đã xảy ra, và có hai cách phổ biến. *Polling*: nền tảng hỏi API của A theo chu kỳ "có gì mới không?"; đơn giản, nhưng trễ cỡ một chu kỳ hỏi. *Webhook*: A tự gọi tới một địa chỉ web do nền tảng cấp mỗi khi có sự kiện; thường gần như tức thì, nhưng A phải hỗ trợ.
3. **Lọc và ghép trường.** Nền tảng kiểm điều kiện ("chỉ khi tiêu đề có chữ hóa đơn"), rồi chuyển các trường của sự kiện sang ô nhập của bước sau ("người gửi" thành "tên khách").
4. **Action (hành động).** Nền tảng gọi API của ứng dụng B để làm việc thay bạn: tạo một dòng, gửi một tin, tạo một thẻ. Quyền để gọi thường do bạn cấp một lần, qua OAuth, khi nối tài khoản. Một quy tắc có thể có nhiều action nối tiếp.
5. **Cái giá.** Khung này do bài bổ sung, không có trong nguồn: trễ do polling, báo trùng khi một bước bị thử lại, lỗi giữa chừng thường không tự quay lui, và giới hạn số lời gọi của ứng dụng B.

## Giới hạn cần nhớ

Nguồn chỉ có vài câu và một lưu đồ lấy từ một bài báo khoa học so sánh hai dịch vụ; lưu đồ đó không được dùng lại ở đây. Năm khung trên là cách bài giải thích mô hình trigger-action nói chung, còn mỗi sản phẩm làm một khác: chu kỳ polling, cách thử lại khi lỗi, trigger nào gần như tức thì, giới hạn số lần chạy đều tùy sản phẩm và gói dịch vụ, nên hãy đọc tài liệu của dịch vụ mình dùng. Cũng đừng hiểu "no-code" là "không có kỹ thuật": quy tắc nối ứng dụng vẫn gặp các vấn đề của một hệ thống phân tán nhỏ (trễ, trùng, lỗi giữa chừng), chỉ là được giấu sau giao diện kéo thả.

## Nhìn hình thử trả lời

Quy tắc: "khi có email kèm tệp, lưu tệp vào kho lưu trữ rồi báo vào nhóm chat". Nền tảng kiểm email mỗi vài phút; bước báo vào nhóm chat gặp lỗi mạng nên được thử lại. Bạn có thể thấy những hiện tượng nào, và giảm chúng thế nào?

<details>
<summary>Xem đáp án</summary>

Hai hiện tượng chính. Một là trễ: tin báo có thể đến muộn cỡ một chu kỳ hỏi; nếu ứng dụng email hỗ trợ webhook thì chọn trigger kiểu đó. Hai là trùng: nếu lần gửi đầu thực ra đã tới nơi nhưng nền tảng không nhận được xác nhận, lần thử lại báo thêm một tin nữa; giảm bằng cách ghi lại "đã xử lý email này" và kiểm trước khi gửi, hoặc dùng khóa chống trùng nếu ứng dụng đích có hỗ trợ. Ngoài ra, nếu bước lưu tệp đã xong mà bước báo hỏng hẳn thì tệp vẫn nằm đó và không ai được báo, vì nền tảng thường không tự quay lui.

</details>

<details>
<summary>Xem sâu hơn</summary>

Các điểm dưới đây là kiến thức chung về mô hình này, chưa được đối chiếu với tài liệu của từng sản phẩm.

- **Tên gọi:** Zapier gọi một quy tắc là *Zap*, If This Then That gọi là *applet*; cả hai đều xoay quanh một trigger và một hoặc nhiều action.
- **Polling cần nhớ, webhook cần chịu lặp:** để không báo lại mục cũ, nền tảng phải nhớ mục đã thấy. Với webhook thì ngược lại: ứng dụng nguồn có thể gửi lại cùng một sự kiện nếu không nhận được xác nhận, nên bước đầu cần chịu được sự kiện lặp.
- **OAuth:** với OAuth, ứng dụng B không đưa mật khẩu cho nền tảng mà cấp một token có phạm vi, chỉ làm được những việc đã cho phép. Token thu hồi được hay không và hết hạn lúc nào là do nhà cung cấp quyết định: có một chuẩn riêng mô tả cách thu hồi token, nhưng việc hỗ trợ tùy nhà cung cấp, và token đã cấp có thể còn dùng được tới khi hết hạn. Nền tảng giữ token của bạn nên là một điểm cần tin cậy; hãy cấp phạm vi nhỏ nhất đủ dùng và xem nhà cung cấp có cho thu hồi quyền hay không.
- **Vòng lặp:** nếu action ở B tự nó là sự kiện kích trigger ở A, quy tắc có thể gọi lại chính mình mãi. Thêm điều kiện lọc để bỏ qua mục do chính quy tắc tạo ra.
- **Giới hạn của ứng dụng đích:** API của B thường giới hạn số lời gọi trong một khoảng thời gian; gọi dồn có thể bị từ chối, và việc thử lại sau đó là một lý do nữa dẫn tới trùng.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/api-of-apis-app-integrations.md): công cụ no-code, tự động hóa quy trình qua giao diện trực quan.
- [RFC 6749: The OAuth 2.0 Authorization Framework](https://www.rfc-editor.org/rfc/rfc6749): ủy quyền, token và phạm vi.
- [RFC 7009: OAuth 2.0 Token Revocation](https://www.rfc-editor.org/rfc/rfc7009): thu hồi token; việc hỗ trợ tùy nhà cung cấp.
- [Trung tâm trợ giúp của Zapier](https://help.zapier.com/) và [trung tâm trợ giúp của If This Then That](https://help.ifttt.com/): cách mỗi dịch vụ gọi và chạy trigger, action.
- Bài báo mà nguồn nêu làm xuất xứ lưu đồ: *IFTTT vs. Zapier: A Comparative Study of Trigger-Action Programming Frameworks* (chưa mở, lưu đồ không được dùng lại).

Đã đọc body nguồn ByteByteGo ghim ngày 2026-10-16. Các tài liệu chuẩn và tài liệu của sản phẩm nêu trên chưa được mở để đối chiếu (máy biên soạn không truy cập được các trang đó), và hành vi của Zapier hay If This Then That chưa được chạy thử. Bài viết và hình được thiết kế độc lập; chưa thử với người học.

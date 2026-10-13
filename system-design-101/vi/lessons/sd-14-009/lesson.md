# Cookie HTTP hoạt động thế nào?

**Cookie là một mẩu dữ liệu nhỏ mà máy chủ nhờ trình duyệt giữ hộ và gửi lại; các thuộc tính của nó quyết định khi nào, tới đâu và cho ai nó được gửi hay đọc.**
Hiểu từng thuộc tính là hiểu vì sao cùng một cookie lúc có mặt, lúc vắng mặt trong một yêu cầu.

![Tám thẻ xếp dọc. Thẻ đầu: máy chủ trả Set-Cookie gồm tên, giá trị và các thuộc tính; trình duyệt lưu lại. Thẻ thứ hai: mỗi yêu cầu sau, trình duyệt tự quyết cookie nào được gắn vào tiêu đề Cookie. Bốn thẻ thuộc tính: Domain và Path giới hạn địa chỉ nhận cookie; Secure chỉ gửi qua HTTPS; HttpOnly để JavaScript không đọc được cookie; SameSite quyết định có gửi cookie trong yêu cầu từ trang khác site hay không, với Strict, Lax và None. Thẻ thời hạn: Expires hoặc Max-Age, không có thì là cookie phiên. Thẻ cuối: nên khai SameSite rõ ràng vì trình duyệt có thể xử lý cookie không khai theo cách khác nhau.](../../diagrams/sd-14-009-main.svg)

## Đọc hình

**Set-Cookie.** Máy chủ gửi `Set-Cookie: tên=giá trị; thuộc tính…`. Tên và giá trị là phần dữ liệu; phần còn lại là thuộc tính điều khiển cách dùng. Trình duyệt lưu cookie và, ở mỗi yêu cầu sau, tự quyết định cookie nào được gắn vào tiêu đề `Cookie`.

**Phạm vi: Domain và Path.** Giới hạn những địa chỉ sẽ nhận cookie.

**Secure và HttpOnly.** `Secure`: chỉ gửi qua kết nối mã hóa HTTPS (có ngoại lệ cho localhost). `HttpOnly`: mã JavaScript không đọc được cookie qua `document.cookie`, dù trình duyệt vẫn gửi nó lên máy chủ. Khi chạy thử, cookie `HttpOnly` vắng mặt trong `document.cookie` nhưng máy chủ vẫn nhận được.

**SameSite.** Quyết định có gửi cookie trong yêu cầu xuất phát từ trang khác site hay không. `Strict`: không gửi. `Lax`: gửi khi người dùng bấm liên kết sang trang này, nhưng không gửi kèm các yêu cầu như form POST từ trang khác. `None`: gửi cả khi xuyên site (phải kèm `Secure`).

**Thời hạn.** `Expires` hoặc `Max-Age` đặt ngày hết hạn; không có thì là cookie phiên, bị xóa khi phiên của trình duyệt kết thúc.

## Giới hạn cần nhớ

`SameSite` chặt hơn thì bảo vệ tốt hơn khỏi yêu cầu giả từ trang khác, nhưng cũng làm hỏng những luồng cần cookie xuyên site, như nội dung nhúng. Khi chạy thử trên Chromium, cookie không khai `SameSite` vẫn được gửi kèm một form POST xuyên site ngay sau khi tạo, nhưng 130 giây sau thì không (nguyên nhân chưa kiểm nguồn); vì vậy nên khai `SameSite` rõ ràng thay vì dựa vào mặc định.

## Nhìn hình trả lời

Người dùng đang đăng nhập ngân hàng, rồi mở một trang khác site có form tự gửi POST tới ngân hàng. Cookie phiên khai `SameSite=Lax`, `SameSite=Strict` hay không khai gì thì có được gửi?

<details>
<summary>Xem đáp án</summary>

Khi chạy thử trên Chromium: cookie khai `Strict` không được gửi kèm cả lúc bấm liên kết từ trang khác site; cookie khai `Lax` được gửi khi bấm liên kết nhưng không được gửi kèm form POST từ trang khác site; cookie không khai gì thì tùy thời điểm, như phần giới hạn trên.
Vì vậy để cookie phiên không đi kèm form POST từ trang khác, nên khai `Lax` hoặc `Strict`. `SameSite` không thay thế các biện pháp khác chống giả mạo yêu cầu, và bài này không thử các trình duyệt khác.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn liệt kê “SameSite, Name, Value, Secure, Domain, HttpOnly” như một nhóm thuộc tính. Tên và giá trị không phải thuộc tính mà là dữ liệu của cookie, nên bài này tách ra, và thêm `Path`, `Expires`, `Max-Age` vì chúng cũng có trong tài liệu MDN.
MDN viết rằng cookie không khai `SameSite` được coi như `Lax`. Bài này giữ ý đó và ghi thêm điều quan sát được khi chạy thử, vì thực tế trình duyệt có thể có ngoại lệ tạm thời cho cookie mới tạo; nguyên nhân cụ thể chưa kiểm nguồn.
Bài nguồn dùng cách nói vui (“cookie là những mẩu giấy nhắn”, “người gác cổng”); bài này giữ lại ý chính là trình duyệt quyết định cookie nào được gửi tới trang nào.

Ví dụ chạy thử là một máy chủ Python và Chromium 141 (Playwright); “khác site” được dựng bằng `127.0.0.1` và `localhost`, hai tên máy khác nhau.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/http-cookies-explained-with-a-simple-diagram.md): HTTP không nhớ trạng thái, cookie và các thuộc tính chính.
- [MDN — Using HTTP cookies](https://github.com/mdn/content/blob/main/files/en-us/web/http/guides/cookies/index.md): `Set-Cookie`, thời hạn, `Secure`, `HttpOnly`, `Domain`, `Path`, `SameSite` và mặc định `Lax`. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Ví dụ chạy thử bằng Python và Chromium 141; đã không mở trang MDN trên web. Bài viết và hình được thiết kế độc lập.

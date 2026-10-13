# Cookie HTTP hoạt động thế nào?

**Cookie là một mẩu dữ liệu nhỏ mà máy chủ nhờ trình duyệt giữ hộ và gửi lại; các thuộc tính của nó quyết định khi nào, tới đâu và cho ai nó được gửi hay đọc.**
Hiểu từng thuộc tính là hiểu vì sao cùng một cookie lúc có mặt, lúc vắng mặt trong một yêu cầu.

![Tám thẻ xếp dọc. Thẻ đầu: máy chủ trả Set-Cookie gồm tên, giá trị và các thuộc tính; trình duyệt lưu lại. Thẻ thứ hai: mỗi yêu cầu sau, trình duyệt tự quyết cookie nào được gắn vào tiêu đề Cookie. Bốn thẻ thuộc tính: Domain và Path giới hạn địa chỉ nhận cookie; Secure chỉ gửi qua HTTPS; HttpOnly để JavaScript không đọc được cookie; SameSite quyết định có gửi cookie trong yêu cầu từ trang khác site hay không, với Strict, Lax và None; Lax chỉ gửi khi đó là điều hướng cấp cao nhất bằng phương thức an toàn như GET; None phải kèm Secure và trình duyệt vẫn có thể chặn cookie bên thứ ba. Thẻ thời hạn: Expires hoặc Max-Age, không có thì là cookie phiên. Thẻ cuối: nên khai SameSite rõ ràng vì trình duyệt có thể xử lý cookie không khai theo cách khác nhau.](../../diagrams/sd-14-009-main.svg)

## Đọc hình

**Set-Cookie.** Máy chủ gửi `Set-Cookie: tên=giá trị; thuộc tính…`. Tên và giá trị là phần dữ liệu; phần còn lại là thuộc tính điều khiển cách dùng. Trình duyệt lưu cookie và, ở mỗi yêu cầu sau, tự quyết định cookie nào được gắn vào tiêu đề `Cookie`.

**Phạm vi: Domain và Path.** Giới hạn những địa chỉ sẽ nhận cookie.

**Secure và HttpOnly.** `Secure`: chỉ gửi qua kết nối mã hóa HTTPS (có ngoại lệ cho localhost). `HttpOnly`: mã JavaScript không đọc được cookie qua `document.cookie`, dù trình duyệt vẫn gửi nó lên máy chủ. Khi chạy thử, cookie `HttpOnly` vắng mặt trong `document.cookie` nhưng máy chủ vẫn nhận được.

**SameSite.** Quyết định có gửi cookie trong yêu cầu xuất phát từ trang khác site hay không. `Strict`: không gửi. `Lax`: với yêu cầu xuyên site, chỉ gửi khi đó là điều hướng cấp cao nhất (địa chỉ trên thanh địa chỉ đổi, ví dụ người dùng bấm liên kết sang trang này) bằng phương thức an toàn (GET là ví dụ thường gặp); không gửi kèm form POST từ trang khác, cũng không gửi cho yêu cầu từ iframe, ảnh, script hay `fetch()` xuyên site. `None`: gửi cả khi xuyên site (phải kèm `Secure`). Đây chỉ là phần luật của `SameSite`: MDN ghi các nhà làm trình duyệt đã bắt đầu chặn cookie bên thứ ba theo mặc định (hoặc có kế hoạch như vậy), và cài đặt hay tiện ích khác cũng có thể chặn, nên `None` kèm `Secure` không bảo đảm cookie tới được máy chủ.

**Thời hạn.** `Expires` hoặc `Max-Age` đặt ngày hết hạn; không có thì là cookie phiên, thường bị xóa khi phiên hiện tại kết thúc. Lúc nào phiên kết thúc do trình duyệt quyết định, và một số trình duyệt khôi phục phiên cũ khi mở lại, khiến cookie phiên có thể tồn tại rất lâu; vì vậy đóng trình duyệt không phải cách đăng xuất đáng tin (kết luận cuối là suy luận của người biên soạn).

## Giới hạn cần nhớ

`SameSite` chặt hơn thì bảo vệ tốt hơn khỏi yêu cầu giả từ trang khác, nhưng cũng làm hỏng những luồng cần cookie xuyên site, như nội dung nhúng (và trình duyệt vẫn có thể chặn cookie bên thứ ba dù đã khai `None`). Khi chạy thử trên Chromium, cookie không khai `SameSite` vẫn được gửi kèm một form POST xuyên site ngay sau khi tạo, nhưng 130 giây sau thì không. Điều này khớp với ghi chú của MDN: khi `Lax` được áp dụng làm mặc định thì dùng bản nới lỏng, cho cả yêu cầu POST nếu cookie được đặt không quá hai phút trước yêu cầu, nên với cookie không khai `SameSite` có một cửa sổ ngắn mà form POST xuyên site vẫn mang cookie đi (kết luận về cửa sổ ngắn này là suy luận của người biên soạn); vì vậy nên khai `SameSite` rõ ràng thay vì dựa vào mặc định.

## Nhìn hình trả lời

Người dùng đang đăng nhập ngân hàng, rồi mở một trang khác site có form tự gửi POST tới ngân hàng. Cookie phiên khai `SameSite=Lax`, `SameSite=Strict` hay không khai gì thì có được gửi?

<details>
<summary>Xem đáp án</summary>

Khi chạy thử trên Chromium: cookie khai `Strict` không được gửi kèm cả lúc bấm liên kết từ trang khác site; cookie khai `Lax` được gửi khi bấm liên kết (điều hướng cấp cao nhất bằng GET) nhưng không được gửi kèm form POST từ trang khác site; cookie không khai gì thì, trên Chromium 141 đã thử, tùy thời điểm như phần giới hạn trên và khớp ghi chú hai phút của MDN.
Vì vậy để cookie phiên không đi kèm form POST từ trang khác, nên khai `Lax` hoặc `Strict`. `SameSite` không thay thế các biện pháp khác chống giả mạo yêu cầu, và bài này không thử các trình duyệt khác.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn liệt kê “SameSite, Name, Value, Secure, Domain, HttpOnly” như một nhóm thuộc tính. Tên và giá trị không phải thuộc tính mà là dữ liệu của cookie, nên bài này tách ra, và thêm `Path`, `Expires`, `Max-Age` vì chúng cũng có trong tài liệu MDN.
MDN viết rằng cookie không khai `SameSite` được coi như `Lax`. Bài này giữ ý đó và ghi thêm điều quan sát được khi chạy thử, vì quan sát này chỉ có ở Chromium 141 trong lần chạy thử. MDN ghi chú rằng khi `Lax` là mặc định thì bản nới lỏng cho cả POST trong hai phút sau khi cookie được đặt, khớp với quan sát; chưa thử trình duyệt khác nên chưa biết trình duyệt nào khác cũng làm vậy.
Bài nguồn dùng cách nói vui (“cookie là những mẩu giấy nhắn”, “người gác cổng”); bài này giữ lại ý chính là trình duyệt quyết định cookie nào được gửi tới trang nào.

Ví dụ chạy thử là một máy chủ Python và Chromium 141 (Playwright); “khác site” được dựng bằng `127.0.0.1` và `localhost`, hai tên máy khác nhau.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/http-cookies-explained-with-a-simple-diagram.md): HTTP không nhớ trạng thái, cookie và các thuộc tính chính.
- [MDN — Set-Cookie, phần SameSite (bản ghim)](https://github.com/mdn/content/blob/19370346042efad9e179fbf1f55deeeadee98c40/files/en-us/web/http/reference/headers/set-cookie/index.md): Lax chỉ gửi xuyên site cho điều hướng cấp cao nhất bằng phương thức an toàn; không gồm iframe, ảnh, script, `fetch()`; khi Lax là mặc định thì bản nới lỏng cho cả POST nếu cookie được đặt không quá hai phút trước. Đọc từ bản clone của kho.
- [MDN — Using HTTP cookies](https://github.com/mdn/content/blob/19370346042efad9e179fbf1f55deeeadee98c40/files/en-us/web/http/guides/cookies/index.md): `Set-Cookie`, thời hạn, `Secure`, `HttpOnly`, `Domain`, `Path`, `SameSite` và mặc định `Lax`. Đọc từ bản clone của kho.

Đã đọc nguồn ngày 2026-10-13. Ví dụ chạy thử bằng Python và Chromium 141; đã không mở trang MDN trên web. Bài viết và hình được thiết kế độc lập.

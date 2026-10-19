# Sáu loại máy chủ thường gặp

**Cùng gọi là "máy chủ", nhưng mỗi loại làm một việc khác: phát trang web, giữ bản gốc, đứng giữa, dịch tên, chuyển thư, chuyển tệp.**
Bài nguồn liệt kê sáu loại thường dùng trong hạ tầng hiện đại; bài này xếp chúng thành hai nhóm để thấy việc của từng loại nằm ở đâu.

![Hai nhóm thẻ xếp dọc. Nhóm đưa nội dung tới người dùng gồm ba thẻ: máy chủ web giữ trang web và gửi nội dung qua Internet; máy chủ gốc giữ nội dung gốc để lưu nhớ tạm và phát tới các máy chủ biên; máy chủ proxy đứng giữa máy khách và máy chủ khác để thêm bảo mật, tăng hiệu năng và ẩn danh. Nhóm dịch vụ nền của mạng gồm ba thẻ: máy chủ DNS dịch tên miền thành địa chỉ IP; máy chủ thư gửi, nhận và chuyển tiếp thư điện tử; máy chủ FTP truyền tệp giữa máy khách và máy chủ. Khung cuối nhắc rằng đây là sáu vai trò, không phải sáu loại máy.](../../diagrams/sd-10-001-main.svg)

## Từ viết tắt

- **DNS** (Domain Name System) — hệ thống tên miền: hệ thống tra một tên miền ra địa chỉ IP, để người dùng gõ tên dễ nhớ thay vì dãy số.
- **IP** (Internet Protocol) — giao thức Internet: địa chỉ IP là dãy số chỉ ra một máy trên mạng.
- **FTP** (File Transfer Protocol) — giao thức truyền tệp: quy ước để chuyển tệp giữa máy khách và máy chủ.

## Đọc hình

Mô tả từng loại theo bài nguồn; cách chia hai nhóm là của người biên soạn.

**Nhóm 1 · Đưa nội dung tới người dùng.**
Máy chủ web giữ trang web và gửi nội dung tới máy khách qua Internet. Máy chủ gốc (origin) giữ nguồn nội dung trung tâm; nội dung đó được lưu nhớ tạm và phân phát tới các máy chủ biên để người dùng nhận nhanh hơn.
Máy chủ proxy đứng giữa máy khách và các máy chủ khác, làm cổng trung gian: có thể thêm bảo mật, tối ưu hiệu năng và che danh tính người gọi.

**Nhóm 2 · Dịch vụ nền của mạng.**
Máy chủ DNS dịch tên miền thành địa chỉ IP, nhờ đó người dùng truy cập website bằng tên dễ nhớ.
Máy chủ thư lo việc gửi, nhận và định tuyến thư điện tử giữa các mạng. Máy chủ FTP giúp truyền tệp giữa máy khách và máy chủ qua mạng.

## Giới hạn cần nhớ

Sáu loại là sáu **vai trò**, không phải sáu loại máy khác nhau. Một máy có thể đảm nhận nhiều vai trò, và một vai trò có thể chia cho nhiều máy. Bài nguồn không nói điều này; đây là kiến thức chung của người biên soạn.
Danh sách cũng chỉ là "sáu loại thường dùng", không phải mọi loại máy chủ.

## Nhìn hình trả lời

Bạn gõ tên một website vào trình duyệt lần đầu, khi chưa có địa chỉ nào được nhớ sẵn và trình duyệt đi thẳng tới trang. Trong sáu loại ở hình, loại nào được hỏi trước, và để làm gì?

<details>
<summary>Xem đáp án</summary>

Máy chủ DNS. Trình duyệt biết tên nhưng cần địa chỉ IP để gửi yêu cầu đi, nên khi chưa có sẵn địa chỉ thì phải hỏi DNS trước. Nếu địa chỉ đã được nhớ sẵn (bộ nhớ đệm) thì không phải hỏi lại, và khi đi qua proxy thì việc dịch tên có thể do proxy làm.
Có địa chỉ rồi, yêu cầu tới máy chủ web, có thể qua một proxy đứng giữa. Nếu nội dung đã được phân phát tới máy chủ biên, người dùng nhận từ máy chủ biên thay vì từ máy chủ gốc.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê sáu loại theo thứ tự web, thư, DNS, proxy, FTP, gốc, mỗi loại một câu và không nói loại này liên hệ với loại kia thế nào.
Hình này xếp lại thành hai nhóm. Máy chủ gốc đứng cạnh máy chủ web vì cùng liên quan tới nội dung phát cho người dùng; mô tả về máy chủ biên lấy từ chính câu của nguồn về máy chủ gốc.
Bài không nhắc tới sản phẩm cụ thể nào và không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-most-commonly-used-server-types.md): sáu loại máy chủ và mô tả một câu cho mỗi loại.

Đã đọc nguồn ngày 2026-10-18. Phần nói về vai trò so với máy là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.

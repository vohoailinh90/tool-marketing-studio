# Quản lý cấu hình và hạ tầng bằng mã: hai cách nhìn một việc

**Quản lý cấu hình giữ cho những thứ đã được cấp ở đúng trạng thái; hạ tầng bằng mã (IaC) cấp chúng ra từ một bản khai báo. Hai cách này chồng lên nhau nhiều hơn tên gọi gợi ý, và việc cần nhớ là cái gì được coi là sự thật: những lệnh đã chạy, hay một tệp mô tả trạng thái mong muốn.** Bài này so hai cách rồi thử một việc cả hai đều phải làm: phát hiện và sửa khi ai đó đã đổi tay một thứ.

![Ba khung. Khung một, quản lý cấu hình truyền thống: duy trì trạng thái các mục đã cấp, công cụ như Puppet, Chef, Ansible vẫn khai báo và tự động được. Khung hai, hạ tầng bằng mã: tự động cấp phát, thường khai báo trạng thái mong muốn, tệp được quản lý phiên bản. Khung ba, bốn bước khi hạ tầng bị sửa tay: so sánh mong muốn với thực tế, liệt kê thay đổi, áp dụng, chạy lại không còn thay đổi.](../../diagrams/sd-11-025-main.svg)

## Từ viết tắt

- **IaC** (Infrastructure as Code) — hạ tầng bằng mã: viết cấu hình máy, mạng, dịch vụ thành tệp để lưu phiên bản, kiểm tra và dùng lại như mã nguồn.

## Đọc hình

**Quản lý cấu hình truyền thống.** Hướng vào việc duy trì trạng thái mong muốn của các mục cấu hình (máy chủ, thiết bị mạng, ứng dụng) sau khi chúng đã được cấp. Các công cụ như Puppet, Chef hay Ansible cũng có thể tự động, khai báo trạng thái mong muốn, chạy lặp lại không đổi kết quả và lưu trong kho mã; điểm khác nằm ở phạm vi: chúng tập trung vào cấu hình máy và phần mềm đã có, còn việc cấp máy, mạng thường nằm ngoài. Cách làm tay hoặc chuỗi lệnh từng bước là kiểu quản trị thủ công chứ không phải đặc điểm của quản lý cấu hình.

**Hạ tầng bằng mã.** Coi việc dựng và đổi hạ tầng là việc của phát triển phần mềm: một bản khai báo trong tệp, thường theo kiểu mô tả trạng thái mong muốn, nằm trong kho mã để lưu phiên bản và duyệt. Công cụ lo phần cấp phát và biến thực tế thành đúng như khai báo.

**Chỗ hai cách gặp nhau.** Cả hai đều quan tâm trạng thái mong muốn; khác nhau ở điểm xuất phát và mức tự động. Nhiều công cụ làm cả hai việc: Puppet và Chef mô tả trạng thái mong muốn của máy; Ansible chạy các tác vụ thường được viết để chạy lại không đổi kết quả. Nên nhãn "công cụ cấu hình" hay "công cụ IaC" là sự tiện lợi khi nói, không phải ranh giới cứng.

## Thử: phát hiện lệch cấu hình

Ngày 2026-10-19, một chương trình Python nhỏ so một bản khai báo hai máy web (cổng 80, bật mã hóa) với thực tế đã bị sửa tay: một máy đổi cổng sang 8080 và có một máy thứ ba không có trong khai báo.

| Bước | Kết quả |
|---|---|
| So sánh khai báo với thực tế, lập kế hoạch | 2 thay đổi: đổi lại cổng của máy 2, xóa máy 3 |
| Áp dụng kế hoạch | thực tế khớp khai báo |
| Chạy lại so sánh | 0 thay đổi |

Kế hoạch được lập trước khi áp dụng, nên người duyệt thấy trước hai việc sắp làm. Đây là lý do mô tả trạng thái mong muốn dễ kiểm soát hơn "chạy lại các lệnh cũ": các lệnh cũ không biết thực tế đã trôi đi đâu.

## Giới hạn cần nhớ

Mô hình so hai bảng nhỏ trong bộ nhớ; công cụ thật còn phải đọc trạng thái từ nhà cung cấp, xử lý phụ thuộc giữa tài nguyên, và quyết định có xóa thứ không có trong khai báo hay không (xóa tự động là hành vi nguy hiểm, nhiều công cụ bắt xác nhận). Phân biệt "quản lý cấu hình" với "IaC" ở bài nguồn cũng đơn giản hóa: nguồn xếp Chef và Puppet vào IaC, còn nhiều tài liệu xếp chúng vào quản lý cấu hình.

## Nhìn hình trả lời

Một đồng nghiệp sửa tay cấu hình trên máy chủ thật để chữa gấp một sự cố, nhưng không sửa tệp khai báo. Tuần sau công cụ chạy lại. Chuyện gì xảy ra, và nên làm gì để lần sau không mất bản chữa?

<details>
<summary>Xem đáp án</summary>

Công cụ coi sửa tay là lệch cấu hình và đưa máy về đúng như tệp, tức xóa bản chữa gấp. Muốn giữ bản chữa thì phải đưa nó vào tệp khai báo và duyệt như mọi thay đổi khác; sửa tay chỉ nên là bước tạm khẩn cấp, kèm việc cập nhật tệp ngay sau đó.
Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn so sánh hai cách bằng một sơ đồ và hai đoạn mô tả. Bài này giữ cách so sánh nhưng thêm điểm chồng lấn giữa hai cách, rồi thử việc phát hiện lệch mà cả hai đều cần. Mô tả công cụ là kiến thức chung của người biên soạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-manage-configurations-in-a-system.md): so sánh quản lý cấu hình truyền thống và IaC. Thử nghiệm và đáp án là của người biên soạn.
- [Puppet — tài liệu về ngôn ngữ khai báo](https://www.puppet.com/docs/puppet/): mô tả trạng thái mong muốn của tài nguyên. Kiến thức chung, chưa mở lại trong phiên viết.
- [Ansible — khái niệm về tác vụ chạy lại không đổi kết quả](https://docs.ansible.com/ansible/latest/reference_appendices/glossary.html): kiến thức chung, chưa mở lại trong phiên viết.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
